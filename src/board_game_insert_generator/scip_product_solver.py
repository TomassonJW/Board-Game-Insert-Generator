"""Lane produit SCIP 3D locale, hors ligne et recertifiée par BGIG."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import importlib.util
import json
from math import ceil
import os
from pathlib import Path
import sys
import tempfile
from time import perf_counter
from types import ModuleType
from typing import Callable, Mapping, Sequence

from board_game_insert_generator.free_3d_beam_solver import VariantFree3DPlacement
from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
    _support_at,
)
from board_game_insert_generator.free_3d_plan_adapter import Free3DPreparedProblem
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_settings import solver_deadline_seconds

SCIP_PRODUCT_SCHEMA_V1 = "bgig.scip_product_lane.v1"
SCIP_PRODUCT_VERSION = "10.0.2"
SCIP_PRODUCT_PYSCIPOPT_VERSION = "6.2.1"
SCIP_PRODUCT_SOPLEX_VERSION = "8.0.2"
SCIP_PRODUCT_NUMPY_VERSION = "2.5.1"
SCIP_PRODUCT_FAMILY = "constraint_integer_programming"
SCIP_PRODUCT_MODEL = "integer_xyz_support_then_bounded_exact_top_inset_z_compensation"
SCIP_PRODUCT_ARTIFACT_DIGEST = "2c2f58bdea37efc6a9172e641f3e348997d7c76152358780b8a69bf277abac9c"
SCIP_PRODUCT_ARCHIVE_SHA256 = "0a718ea5884d6326d66777db0ab853a31fa981e6392b89f184342fde27d465c6"

STATUS_NOT_CONFIGURED = "not_configured"
STATUS_UNSUPPORTED = "unsupported"
STATUS_INVALID_RUNTIME = "invalid_runtime"
STATUS_SOLUTION_FOUND = "solution_found"
STATUS_BOUNDED_UNKNOWN = "bounded_unknown"
STATUS_EXTERNAL_ERROR = "external_error"
STATUS_CERTIFICATE_REJECTED = "certificate_rejected"
STATUS_CANCELLED = "cancelled"

_SCALE_PER_MM = 1000
_EPSILON_MM = 1e-6
_MAX_PARTICIPANT_COUNT = 128
_INPUT_SCHEMA = "bgig.real_3d_worker_input.v1"
_OUTPUT_SCHEMA = "bgig.real_3d_worker_output.v1"

_configured_runtime_root: Path | None = None
_configured_artifact_path: Path | None = None
_configured_worker_root: Path | None = None
_configured_scratch_root: Path | None = None
_validated_runtime_signature: tuple[str, str, str] | None = None
_loaded_worker: ModuleType | None = None
_dll_handles: list[object] = []


@dataclass(frozen=True)
class ScipProductLimits:
    wall_seconds: float
    memory_mebibytes: int = 1024
    threads: int = 1
    seed: int = 6408
    solution_limit: int = 1

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class _ProductOption:
    participant_id: str
    role: str
    name: str
    variant_id: str
    local_size_mm: tuple[float, float, float]
    minimum_local_size_mm: tuple[float, float, float]
    floor_thickness_mm: float
    cavities: tuple[tuple[float, float, float, float, float], ...]
    variant_digest: str
    variant_canonical: bool


@dataclass(frozen=True)
class _PreparedProductProblem:
    payload: dict[str, object]
    problem_digest: str
    options: dict[tuple[str, str], _ProductOption]
    participants: dict[str, dict[str, object]]
    box_clearance_mm: float
    xy_clearance_mm: float
    z_clearance_mm: float


@dataclass(frozen=True)
class ScipProductExecution:
    status: str
    stop_reason: str
    limits: ScipProductLimits
    problem_digest: str
    engine_status: str
    placements: tuple[Free3DPlacement, ...]
    model_digest: str
    solution_digest: str
    invocation_count: int
    total_wall_seconds: float | None = None

    def deterministic_report(self) -> dict[str, object]:
        reported_limits = self.limits.to_dict()
        reported_limits["wall_seconds"] = float(
            ceil(float(reported_limits["wall_seconds"]))
        )
        report: dict[str, object] = {
            "schema_version": SCIP_PRODUCT_SCHEMA_V1,
            "candidate": {
                "candidate_id": "scip",
                "family": SCIP_PRODUCT_FAMILY,
                "version": SCIP_PRODUCT_VERSION,
                "pyscipopt_version": SCIP_PRODUCT_PYSCIPOPT_VERSION,
                "soplex_version": SCIP_PRODUCT_SOPLEX_VERSION,
                "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
            },
            "model": {
                "kind": SCIP_PRODUCT_MODEL,
                "problem_digest": self.problem_digest,
                "model_digest": self.model_digest,
                "scale_per_mm": _SCALE_PER_MM,
            },
            "limits": reported_limits,
            "status": self.status,
            "stop_reason": self.stop_reason,
            "engine_status": self.engine_status,
            "solution_digest": self.solution_digest,
            "invocation_count": self.invocation_count,
            "invariants": {
                "bgig_certificate_required": True,
                "global_install_required": False,
                "network_invocation_count": 0,
                "native_in_process": True,
                "subprocess_isolated": False,
                "telemetry_enabled": False,
                "volatile_runtime_metrics_in_certifiable_payload": False,
                "remaining_deadline_is_ceiled_in_report": True,
                "holdout_read": False,
            },
        }
        report["report_digest"] = canonical_digest(report)
        return report


def configure_scip_product_runtime(
    runtime_root: str | Path | None,
    *,
    artifact_path: str | Path | None = None,
    worker_root: str | Path | None = None,
    scratch_root: str | Path | None = None,
) -> None:
    """Configure uniquement les ressources locales fournies par l'add-in."""

    global _configured_runtime_root
    global _configured_artifact_path
    global _configured_worker_root
    global _configured_scratch_root
    global _validated_runtime_signature
    resolved_runtime = Path(runtime_root).resolve() if runtime_root is not None else None
    resolved_artifact = Path(artifact_path).resolve() if artifact_path is not None else None
    resolved_worker = Path(worker_root).resolve() if worker_root is not None else None
    resolved_scratch = Path(scratch_root).resolve() if scratch_root is not None else None
    runtime_changed = (
        resolved_runtime != _configured_runtime_root
        or resolved_artifact != _configured_artifact_path
        or resolved_worker != _configured_worker_root
    )
    _configured_runtime_root = resolved_runtime
    _configured_artifact_path = resolved_artifact
    _configured_worker_root = resolved_worker
    _configured_scratch_root = resolved_scratch
    if runtime_changed:
        _validated_runtime_signature = None


def scip_product_runtime_configured() -> bool:
    return _configured_runtime_root is not None


def scip_product_limits(effort_profile: str) -> ScipProductLimits:
    return ScipProductLimits(wall_seconds=solver_deadline_seconds(effort_profile))


def solve_scip_product_3d(
    participants: Sequence[Mapping[str, object]],
    problem: Free3DPreparedProblem,
    *,
    effort_profile: str,
    cancel_check: Callable[[], bool] | None = None,
    wall_seconds: float | None = None,
) -> ScipProductExecution:
    limits = scip_product_limits(effort_profile)
    if wall_seconds is not None:
        limits = replace(limits, wall_seconds=max(0.001, float(wall_seconds)))
    if _configured_runtime_root is None:
        return _empty_execution(
            limits,
            status=STATUS_NOT_CONFIGURED,
            stop_reason="product_runtime_not_configured",
        )
    runtime_error = _runtime_error()
    if runtime_error is not None:
        return _empty_execution(
            limits,
            status=STATUS_INVALID_RUNTIME,
            stop_reason=runtime_error,
        )
    prepared, rejection = _prepare_product_problem(participants, problem)
    if prepared is None:
        return _empty_execution(
            limits,
            status=STATUS_UNSUPPORTED,
            stop_reason=rejection,
        )
    if cancel_check is not None and cancel_check():
        return _empty_execution(
            limits,
            status=STATUS_CANCELLED,
            stop_reason="cancelled_before_native_solve",
            problem_digest=prepared.problem_digest,
        )
    started = perf_counter()
    try:
        output = _invoke_worker(prepared, limits)
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return _empty_execution(
            limits,
            status=STATUS_EXTERNAL_ERROR,
            stop_reason="scip_native_execution_failed",
            problem_digest=prepared.problem_digest,
            invocation_count=1,
        )
    elapsed = perf_counter() - started
    invocation_count = int(output.get("worker_invocation_count", 1))
    if cancel_check is not None and cancel_check():
        return _empty_execution(
            limits,
            status=STATUS_CANCELLED,
            stop_reason="cancelled_after_native_solve",
            problem_digest=prepared.problem_digest,
            invocation_count=invocation_count,
            engine_status=str(output.get("engine_status", "")),
            total_wall_seconds=elapsed,
        )
    model_digest = canonical_digest(
        {
            "artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
            "problem_digest": prepared.problem_digest,
            "limits": limits.to_dict(),
            "model": SCIP_PRODUCT_MODEL,
        }
    )
    if output.get("status") != "feasible":
        return _empty_execution(
            limits,
            status=STATUS_BOUNDED_UNKNOWN,
            stop_reason="strict_product_model_no_solution_within_budget",
            problem_digest=prepared.problem_digest,
            invocation_count=invocation_count,
            engine_status=str(output.get("engine_status", "")),
            model_digest=model_digest,
            total_wall_seconds=elapsed,
        )
    try:
        placements = _convert_placements(output.get("placements"), prepared)
    except (KeyError, TypeError, ValueError):
        return _empty_execution(
            limits,
            status=STATUS_EXTERNAL_ERROR,
            stop_reason="scip_solution_projection_failed",
            problem_digest=prepared.problem_digest,
            invocation_count=invocation_count,
            engine_status=str(output.get("engine_status", "")),
            model_digest=model_digest,
            total_wall_seconds=elapsed,
        )
    solution_digest = canonical_digest([_placement_payload(value) for value in placements])
    return ScipProductExecution(
        status=STATUS_SOLUTION_FOUND,
        stop_reason="native_solution_requires_bgig_recertification",
        limits=limits,
        problem_digest=prepared.problem_digest,
        engine_status=str(output.get("engine_status", "")),
        placements=placements,
        model_digest=model_digest,
        solution_digest=solution_digest,
        invocation_count=invocation_count,
        total_wall_seconds=elapsed,
    )


def _runtime_error() -> str | None:
    global _validated_runtime_signature
    if sys.version_info[:2] != (3, 14):
        return "python_abi_mismatch_expected_cp314"
    if os.name != "nt":
        return "windows_x86_64_runtime_required"
    if (
        _configured_runtime_root is None
        or _configured_artifact_path is None
        or _configured_worker_root is None
    ):
        return "runtime_paths_incomplete"
    try:
        manifest = _read_json(_configured_artifact_path)
    except (OSError, json.JSONDecodeError, ValueError):
        return "artifact_manifest_unreadable"
    supplied = manifest.pop("artifact_digest", None)
    if supplied != SCIP_PRODUCT_ARTIFACT_DIGEST or supplied != canonical_digest(manifest):
        return "artifact_digest_mismatch"
    archive = manifest.get("archive")
    if not isinstance(archive, dict) or archive.get("sha256") != SCIP_PRODUCT_ARCHIVE_SHA256:
        return "archive_contract_mismatch"
    signature = (
        str(_configured_runtime_root),
        str(_configured_artifact_path),
        str(_configured_worker_root),
    )
    if _validated_runtime_signature == signature:
        return _loaded_module_conflict()
    try:
        tree = _runtime_tree(_configured_runtime_root)
    except OSError:
        return "runtime_tree_unreadable"
    if tree != manifest.get("runtime_tree"):
        return "runtime_tree_digest_mismatch"
    worker_records = manifest.get("worker_files")
    if not isinstance(worker_records, list):
        return "worker_manifest_missing"
    for record in worker_records:
        if not isinstance(record, dict):
            return "worker_manifest_invalid"
        path = _configured_artifact_path.parent / str(record.get("path", ""))
        try:
            if (
                not path.is_file()
                or path.stat().st_size != int(record.get("size_bytes", -1))
                or _sha256(path) != record.get("sha256")
            ):
                return "worker_digest_mismatch"
        except (OSError, TypeError, ValueError):
            return "worker_unreadable"
    required = (
        _configured_runtime_root / "site-packages" / "pyscipopt" / "scip.cp314-win_amd64.pyd",
        _configured_runtime_root / "site-packages" / "pyscipopt" / "libscip.dll",
        _configured_runtime_root / "site-packages" / "numpy" / "__init__.py",
        _configured_worker_root / "scip_real_3d_worker.py",
        _configured_worker_root / "_real_3d_worker_common.py",
    )
    if any(not path.is_file() for path in required):
        return "runtime_required_file_missing"
    conflict = _loaded_module_conflict()
    if conflict is not None:
        return conflict
    _validated_runtime_signature = signature
    return None


def _loaded_module_conflict() -> str | None:
    if "numpy" in sys.modules:
        numpy_module = sys.modules["numpy"]
        if getattr(numpy_module, "__version__", None) != SCIP_PRODUCT_NUMPY_VERSION:
            return "numpy_runtime_conflict"
    if "pyscipopt" in sys.modules:
        module = sys.modules["pyscipopt"]
        if getattr(module, "__version__", None) != SCIP_PRODUCT_PYSCIPOPT_VERSION:
            return "pyscipopt_runtime_conflict"
        module_path = Path(str(getattr(module, "__file__", ""))).resolve()
        if _configured_runtime_root is None or _configured_runtime_root not in module_path.parents:
            return "pyscipopt_origin_conflict"
    return None


def _prepare_product_problem(
    participants: Sequence[Mapping[str, object]],
    problem: Free3DPreparedProblem,
) -> tuple[_PreparedProductProblem | None, str]:
    if not 1 <= len(participants) <= _MAX_PARTICIPANT_COUNT:
        return None, "participant_count_outside_scip_product_cap"
    try:
        box_clearance = _exact_mm(problem.box_xy_clearance_mm)
        xy_clearance = _exact_mm(problem.xy_clearance_mm)
        z_clearance = _exact_mm(problem.z_clearance_mm)
        usable = (
            _exact_mm(float(problem.box["x"]) - 2.0 * box_clearance),
            _exact_mm(float(problem.box["y"]) - 2.0 * box_clearance),
            _exact_mm(problem.storage_height_mm),
        )
        if any(value <= 0.0 for value in usable):
            return None, "non_positive_scip_product_bounds"
        world = [
            _scaled_exact(usable[0] + xy_clearance),
            _scaled_exact(usable[1] + xy_clearance),
            _scaled_exact(usable[2] + z_clearance),
        ]
        xy_ticks = _scaled_exact(xy_clearance)
        z_ticks = _scaled_exact(z_clearance)
        box_origin_ticks = _scaled_exact(box_clearance)
        top_inset_zones = _worker_top_inset_zones(problem)
        layout = problem.project["layout"]
        if not isinstance(layout, Mapping):
            raise ValueError("Product layout must be a mapping.")
        default_floor = _exact_mm(float(layout["default_floor_thickness_mm"]))
        worker_participants = []
        option_records: dict[tuple[str, str], _ProductOption] = {}
        participant_records: dict[str, dict[str, object]] = {}
        for raw in sorted(participants, key=_participant_stacking_preference_key):
            participant = deepcopy(dict(raw))
            participant_id = str(participant["id"])
            if participant_id in participant_records:
                return None, "duplicate_participant_id"
            participant_records[participant_id] = participant
            options = _participant_options(
                participant,
                default_floor_mm=default_floor,
            )
            worker_variants = []
            for option in options:
                key = (participant_id, option.variant_id)
                if key in option_records:
                    return None, "duplicate_variant_id"
                option_records[key] = option
                local_ticks = tuple(_scaled_exact(value) for value in option.local_size_mm)
                padded = [
                    local_ticks[0] + xy_ticks,
                    local_ticks[1] + xy_ticks,
                    local_ticks[2] + z_ticks,
                ]
                rotations = ["xyz"]
                if local_ticks[0] != local_ticks[1]:
                    rotations.append("yxz")
                worker_variants.append(
                    {
                        "variant_id": option.variant_id,
                        "size": padded,
                        "allowed_rotations": rotations,
                        **(
                            {
                                "top_inset_support_profiles": {
                                    orientation: _top_inset_support_profile(
                                        option,
                                        orientation,
                                    )
                                    for orientation in rotations
                                }
                            }
                            if top_inset_zones
                            else {}
                        ),
                    }
                )
            dimension_modes = participant.get("dimension_modes")
            expandable_z = bool(
                top_inset_zones
                and participant.get("role") == "container"
                and isinstance(dimension_modes, Mapping)
                and str(dimension_modes.get("z")) != "fixed"
            )
            worker_participants.append(
                {
                    "participant_id": participant_id,
                    "assigned_content_count": 0,
                    "variants": worker_variants,
                    "minimum_support_count": 1,
                    "ground_allowed": True,
                    "expandable_z": expandable_z,
                }
            )
    except (KeyError, TypeError, ValueError, OverflowError):
        return None, "product_geometry_not_exactly_representable"
    active_constraints = [
        "xyz",
        "stacking",
        "support",
        "p45_variant_front",
        "rotations",
    ]
    if top_inset_zones:
        active_constraints.append("top_inset_support")
    if len(worker_participants) >= 24:
        active_constraints.append("high_container_cardinality")
    payload: dict[str, object] = {
        "case_id": "bgig-product-explicit-solve",
        "world_mm": world,
        "participants": worker_participants,
        "active_constraints": active_constraints,
        "reservation_volumes": [],
        **(
            {
                "top_inset_zones": top_inset_zones,
                "box_origin_xy": [box_origin_ticks, box_origin_ticks],
            }
            if top_inset_zones
            else {}
        ),
        "access_policy": "unconstrained",
        "access_precedence_edges": [],
        "project_mode": "cold",
        "scale_per_mm": _SCALE_PER_MM,
        "product_clearance_padding": {
            "box_xy_mm": box_clearance,
            "between_xy_mm": xy_clearance,
            "between_z_mm": z_clearance,
            "positive_axis_padding": True,
        },
        "stacking_preference": {
            "kind": "small_footprint_below_large_footprint",
            "hard_constraint": False,
            "participant_order_is_warm_start_only": True,
        },
    }
    payload["problem_digest"] = canonical_digest(payload)
    return (
        _PreparedProductProblem(
            payload=payload,
            problem_digest=str(payload["problem_digest"]),
            options=option_records,
            participants=participant_records,
            box_clearance_mm=box_clearance,
            xy_clearance_mm=xy_clearance,
            z_clearance_mm=z_clearance,
        ),
        "",
    )


def _participant_stacking_preference_key(
    participant: Mapping[str, object],
) -> tuple[float, float, float, str]:
    size = _dimension_tuple(participant["minimum_local_mm"])
    return (
        size[0] * size[1],
        min(size[0], size[1]),
        size[0] * size[1] * size[2],
        str(participant["id"]),
    )

def _participant_options(
    participant: Mapping[str, object],
    *,
    default_floor_mm: float = 0.0,
) -> tuple[_ProductOption, ...]:
    participant_id = str(participant["id"])
    role = str(participant["role"])
    name = str(participant["name"])
    raw_variants = participant.get("container_internal_variant_options_v1")
    variants = raw_variants if role == "container" and isinstance(raw_variants, list) else []
    hint_value = participant.get("top_inset_search_hint_v1")
    hint = hint_value if isinstance(hint_value, Mapping) else {}
    floor = _exact_mm(float(hint.get("floor_thickness_mm", default_floor_mm)))
    if not variants:
        minimum_value = participant["minimum_local_mm"]
        local = _resolved_local_size(participant, minimum_value)
        minimum = _dimension_tuple(minimum_value)
        return (
            _ProductOption(
                participant_id=participant_id,
                role=role,
                name=name,
                variant_id=f"canonical:{participant_id}",
                local_size_mm=local,
                minimum_local_size_mm=minimum,
                floor_thickness_mm=floor,
                cavities=_cavity_specs(hint.get("cavities", [])),
                variant_digest="",
                variant_canonical=True,
            ),
        )
    result = []
    for value in variants:
        if not isinstance(value, Mapping):
            raise ValueError("Invalid product variant option.")
        try:
            minimum = _dimension_tuple(value["minimum_outer_envelope_mm"])
            local = _resolved_local_size(
                participant,
                value["minimum_outer_envelope_mm"],
            )
        except ValueError as exc:
            if str(exc) == "Fixed product dimension is smaller than its minimum.":
                continue
            raise
        result.append(
            _ProductOption(
                participant_id=participant_id,
                role=role,
                name=name,
                variant_id=str(value["variant_id"]),
                local_size_mm=local,
                minimum_local_size_mm=minimum,
                floor_thickness_mm=floor,
                cavities=_cavity_specs(value.get("cavities", hint.get("cavities", []))),
                variant_digest=str(value["geometry_digest"]),
                variant_canonical=bool(value.get("canonical", False)),
            )
        )
    if not result:
        raise ValueError("No product variant satisfies the fixed dimensions.")
    return tuple(result)


def _worker_top_inset_zones(
    problem: Free3DPreparedProblem,
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    box_x = _scaled_exact(float(problem.box["x"]))
    box_y = _scaled_exact(float(problem.box["y"]))
    design_top = _scaled_exact(problem.storage_height_mm)
    for index, zone in enumerate(problem.top_inset_zones):
        if not isinstance(zone, TopInsetZone):
            raise ValueError("Invalid top-inset zone.")
        origin = [_scaled_exact(value) for value in zone.origin_xy_mm]
        size = [_scaled_exact(value) for value in zone.size_xy_mm]
        support_plane = _scaled_exact(zone.support_plane_z_mm)
        inset_depth = _scaled_exact(zone.inset_depth_mm)
        if (
            any(value < 0 for value in origin)
            or any(value <= 0 for value in size)
            or origin[0] + size[0] > box_x
            or origin[1] + size[1] > box_y
            or support_plane < 0
            or inset_depth <= 0
            or support_plane + inset_depth != design_top
        ):
            raise ValueError("Top-inset zone is outside exact product bounds.")
        result.append(
            {
                "zone_id": f"top-inset:{index}",
                "origin_xy": origin,
                "size_xy": size,
                "support_plane_z": support_plane,
                "inset_depth": inset_depth,
                "design_top_z": design_top,
            }
        )
    return result


def _top_inset_support_profile(
    option: _ProductOption,
    orientation: str,
) -> dict[str, object]:
    local_x, local_y, local_z = option.local_size_mm
    minimum_x, minimum_y, _ = option.minimum_local_size_mm
    offset_x = max(0.0, local_x - minimum_x) / 2.0
    offset_y = max(0.0, local_y - minimum_y) / 2.0
    cavities = []
    for cavity_x, cavity_y, size_x, size_y, size_z in option.cavities:
        local_cavity_x = offset_x + cavity_x
        local_cavity_y = offset_y + cavity_y
        if orientation == "yxz":
            origin_xy = (
                local_y - local_cavity_y - size_y,
                local_cavity_x,
            )
            size_xy = (size_y, size_x)
            physical_size = (local_y, local_x, local_z)
        else:
            origin_xy = (local_cavity_x, local_cavity_y)
            size_xy = (size_x, size_y)
            physical_size = (local_x, local_y, local_z)
        cavities.append(
            {
                "origin_xy": [_scaled_exact(value) for value in origin_xy],
                "size_xy": [_scaled_exact(value) for value in size_xy],
                "depth": _scaled_exact(size_z),
            }
        )
    if orientation == "yxz":
        physical_size = (local_y, local_x, local_z)
    else:
        physical_size = (local_x, local_y, local_z)
    return {
        "physical_size": [_scaled_exact(value) for value in physical_size],
        "minimum_floor": _scaled_exact(option.floor_thickness_mm),
        "cavities": cavities,
    }


def _dimension_tuple(value: object) -> tuple[float, float, float]:
    if not isinstance(value, Mapping):
        raise ValueError("Product dimensions must be a mapping.")
    return tuple(_exact_mm(float(value[axis])) for axis in ("x", "y", "z"))  # type: ignore[return-value]


def _cavity_specs(
    values: object,
) -> tuple[tuple[float, float, float, float, float], ...]:
    if not isinstance(values, list):
        raise ValueError("Product cavities must be a list.")
    result = []
    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError("Product cavity must be a mapping.")
        origin = value.get("local_origin_mm")
        size = value.get("inner_dimensions_mm")
        if not isinstance(origin, Mapping) or not isinstance(size, Mapping):
            raise ValueError("Product cavity geometry is incomplete.")
        result.append(
            (
                _exact_mm(float(origin["x"])),
                _exact_mm(float(origin["y"])),
                _exact_mm(float(size["x"])),
                _exact_mm(float(size["y"])),
                _exact_mm(float(size["z"])),
            )
        )
    return tuple(result)


def _resolved_local_size(
    participant: Mapping[str, object], minimum_value: object
) -> tuple[float, float, float]:
    if not isinstance(minimum_value, Mapping):
        raise ValueError("Participant minimum must be a mapping.")
    modes = participant.get("dimension_modes")
    targets = participant.get("target_local_mm")
    if not isinstance(modes, Mapping) or not isinstance(targets, Mapping):
        raise ValueError("Participant dimensions are incomplete.")
    values = []
    for axis in ("x", "y", "z"):
        minimum = _exact_mm(float(minimum_value[axis]))
        target = targets.get(axis)
        value = (
            _exact_mm(float(target))
            if str(modes.get(axis)) == "fixed"
            and isinstance(target, (int, float))
            and not isinstance(target, bool)
            else minimum
        )
        if value + _EPSILON_MM < minimum:
            raise ValueError("Fixed product dimension is smaller than its minimum.")
        values.append(value)
    return tuple(values)  # type: ignore[return-value]


def _invoke_worker(
    prepared: _PreparedProductProblem,
    limits: ScipProductLimits,
) -> dict[str, object]:
    if prepared.payload.get("top_inset_zones"):
        return _invoke_worker_with_top_inset_compensation(prepared, limits)
    deferred_ids = _hybrid_deferred_participant_ids(prepared)
    if not deferred_ids:
        output = _invoke_worker_once(prepared, limits)
        output["worker_invocation_count"] = 1
        return _rebind_worker_output(output, prepared, limits)
    started = perf_counter()
    anchor = _prepared_without_participants(prepared, deferred_ids)
    output = _invoke_worker_once(anchor, limits)
    if output.get("status") != "feasible":
        output["worker_invocation_count"] = 1
        return _rebind_worker_output(output, prepared, limits)
    placements = [dict(value) for value in output.get("placements", [])]
    participants = prepared.payload["participants"]
    if not isinstance(participants, list):
        raise RuntimeError("SCIP product participants must be a list.")
    by_id = {str(value["participant_id"]): value for value in participants}
    world = tuple(int(value) for value in prepared.payload["world_mm"])
    for participant_id in deferred_ids:
        placement = _place_deferred_participant(by_id[participant_id], placements, world)
        if placement is None:
            remaining = limits.wall_seconds - (perf_counter() - started)
            if remaining >= 0.1:
                fallback = _invoke_worker_once(
                    prepared,
                    replace(limits, wall_seconds=remaining),
                )
                fallback["worker_invocation_count"] = 2
                return _rebind_worker_output(fallback, prepared, limits)
            output.update(
                {
                    "status": "unknown",
                    "proof_status": "bounded",
                    "engine_status": "hybrid_fill_failed",
                    "placements": [],
                    "worker_invocation_count": 1,
                }
            )
            return _rebind_worker_output(output, prepared, limits)
        placements.append(placement)
    output.update(
        {
            "status": "feasible",
            "proof_status": "incumbent",
            "engine_status": "hybrid_anchor_and_fill",
            "placements": placements,
            "hybrid_deferred_count": len(deferred_ids),
            "worker_invocation_count": 1,
        }
    )
    return _rebind_worker_output(output, prepared, limits)


def _invoke_worker_with_top_inset_compensation(
    prepared: _PreparedProductProblem,
    limits: ScipProductLimits,
) -> dict[str, object]:
    started = perf_counter()
    base = _prepared_without_top_insets(prepared)
    output = _invoke_worker_once(base, limits)
    if output.get("status") == "feasible":
        compensated = _apply_required_top_inset_z_compensation(
            output.get("placements"),
            prepared,
        )
        if compensated is not None:
            output["placements"] = compensated
            output["engine_status"] = (
                f"{output.get('engine_status', '')}+required_z_compensation"
            )
            output["worker_invocation_count"] = 1
            return _rebind_worker_output(output, prepared, limits)
    remaining = limits.wall_seconds - (perf_counter() - started)
    if remaining < 0.1:
        output.update(
            {
                "status": "unknown",
                "proof_status": "bounded",
                "engine_status": "top_inset_compensation_budget_exhausted",
                "placements": [],
                "worker_invocation_count": 1,
            }
        )
        return _rebind_worker_output(output, prepared, limits)
    fallback = _invoke_worker_once(
        prepared,
        replace(limits, wall_seconds=remaining),
    )
    fallback["worker_invocation_count"] = 2
    return _rebind_worker_output(fallback, prepared, limits)


def _prepared_without_top_insets(
    prepared: _PreparedProductProblem,
) -> _PreparedProductProblem:
    payload = deepcopy(prepared.payload)
    payload.pop("top_inset_zones", None)
    payload.pop("box_origin_xy", None)
    payload["active_constraints"] = [
        value
        for value in payload.get("active_constraints", [])
        if value != "top_inset_support"
    ]
    for participant in payload.get("participants", []):
        participant["expandable_z"] = False
    payload.pop("problem_digest", None)
    payload["problem_digest"] = canonical_digest(payload)
    return replace(
        prepared,
        payload=payload,
        problem_digest=str(payload["problem_digest"]),
    )


def _apply_required_top_inset_z_compensation(
    raw_placements: object,
    prepared: _PreparedProductProblem,
) -> list[dict[str, object]] | None:
    if not isinstance(raw_placements, list):
        return None
    placements = [dict(value) for value in raw_placements if isinstance(value, Mapping)]
    if len(placements) != len(raw_placements):
        return None
    payload_participants = prepared.payload.get("participants")
    zones = prepared.payload.get("top_inset_zones")
    box_origin = prepared.payload.get("box_origin_xy")
    if (
        not isinstance(payload_participants, list)
        or not isinstance(zones, list)
        or not isinstance(box_origin, list)
        or len(box_origin) != 2
    ):
        return None
    participants_by_id = {
        str(value["participant_id"]): value
        for value in payload_participants
        if isinstance(value, Mapping)
    }
    for zone in zones:
        if not isinstance(zone, Mapping):
            return None
        zone_x = int(zone["origin_xy"][0]) - int(box_origin[0])
        zone_y = int(zone["origin_xy"][1]) - int(box_origin[1])
        zone_width, zone_depth = (int(value) for value in zone["size_xy"])
        design_top = int(zone["design_top_z"])
        inset_depth = int(zone["inset_depth"])
        candidates: list[tuple[int, int, str, dict[str, object], int]] = []
        already_supported = False
        for placement in placements:
            participant_id = str(placement.get("participant_id", ""))
            participant = participants_by_id.get(participant_id)
            if participant is None:
                return None
            profile = _raw_top_inset_profile(placement, participant)
            if profile is None:
                return None
            physical_width, physical_depth, minimum_physical_height = (
                int(value) for value in profile["physical_size"]
            )
            raw_size = placement.get("size")
            if not isinstance(raw_size, list) or len(raw_size) != 3:
                return None
            padding_z = int(raw_size[2]) - minimum_physical_height
            x = int(placement["x"])
            y = int(placement["y"])
            z = int(placement["z"])
            if not _raw_xy_overlaps(
                x,
                y,
                physical_width,
                physical_depth,
                zone_x,
                zone_y,
                zone_width,
                zone_depth,
            ):
                continue
            physical_top = z + int(raw_size[2]) - padding_z
            if physical_top == design_top:
                minimum_floor = int(profile["minimum_floor"])
                if (
                    int(raw_size[2]) - padding_z < minimum_floor + inset_depth
                    or not _raw_cavities_are_safe_for_top_inset(
                        profile,
                        x,
                        y,
                        zone_x,
                        zone_y,
                        zone_width,
                        zone_depth,
                        int(raw_size[2]) - padding_z,
                        inset_depth,
                    )
                ):
                    return None
                already_supported = True
                break
            if not bool(participant.get("expandable_z")):
                continue
            required_physical_height = design_top - z
            if required_physical_height < minimum_physical_height:
                continue
            minimum_floor = int(profile["minimum_floor"])
            if required_physical_height < minimum_floor + inset_depth:
                continue
            if not _raw_cavities_are_safe_for_top_inset(
                profile,
                x,
                y,
                zone_x,
                zone_y,
                zone_width,
                zone_depth,
                required_physical_height,
                inset_depth,
            ):
                continue
            required_padded_height = required_physical_height + padding_z
            if z + required_padded_height > int(prepared.payload["world_mm"][2]):
                continue
            if _raw_z_expansion_collides(
                placement,
                required_padded_height,
                placements,
            ):
                continue
            overlap_width = min(x + physical_width, zone_x + zone_width) - max(x, zone_x)
            overlap_depth = min(y + physical_depth, zone_y + zone_depth) - max(y, zone_y)
            candidates.append(
                (
                    -(z + minimum_physical_height),
                    -(overlap_width * overlap_depth),
                    participant_id,
                    placement,
                    required_padded_height,
                )
            )
        if already_supported:
            continue
        if not candidates:
            return None
        _, _, _, selected, required_height = min(candidates)
        selected["size"] = [
            int(selected["size"][0]),
            int(selected["size"][1]),
            required_height,
        ]
    return placements


def _raw_top_inset_profile(
    placement: Mapping[str, object],
    participant: Mapping[str, object],
) -> Mapping[str, object] | None:
    variant_id = str(placement.get("selected_variant_id", ""))
    orientation = str(placement.get("orientation", ""))
    variants = participant.get("variants")
    if not isinstance(variants, list):
        return None
    variant = next(
        (
            value
            for value in variants
            if isinstance(value, Mapping) and str(value.get("variant_id")) == variant_id
        ),
        None,
    )
    if variant is None:
        return None
    profiles = variant.get("top_inset_support_profiles")
    if not isinstance(profiles, Mapping):
        return None
    profile = profiles.get(orientation)
    return profile if isinstance(profile, Mapping) else None


def _raw_xy_overlaps(
    left_x: int,
    left_y: int,
    left_width: int,
    left_depth: int,
    right_x: int,
    right_y: int,
    right_width: int,
    right_depth: int,
) -> bool:
    return (
        left_x < right_x + right_width
        and right_x < left_x + left_width
        and left_y < right_y + right_depth
        and right_y < left_y + left_depth
    )


def _raw_cavities_are_safe_for_top_inset(
    profile: Mapping[str, object],
    body_x: int,
    body_y: int,
    zone_x: int,
    zone_y: int,
    zone_width: int,
    zone_depth: int,
    physical_height: int,
    inset_depth: int,
) -> bool:
    minimum_floor = int(profile["minimum_floor"])
    cavities = profile.get("cavities")
    if not isinstance(cavities, list):
        return False
    for cavity in cavities:
        if not isinstance(cavity, Mapping):
            return False
        cavity_x = body_x + int(cavity["origin_xy"][0])
        cavity_y = body_y + int(cavity["origin_xy"][1])
        cavity_width, cavity_depth = (int(value) for value in cavity["size_xy"])
        if not _raw_xy_overlaps(
            cavity_x,
            cavity_y,
            cavity_width,
            cavity_depth,
            zone_x,
            zone_y,
            zone_width,
            zone_depth,
        ):
            continue
        if physical_height < minimum_floor + int(cavity["depth"]) + inset_depth:
            return False
    return True


def _raw_z_expansion_collides(
    placement: Mapping[str, object],
    required_height: int,
    placements: Sequence[Mapping[str, object]],
) -> bool:
    x = int(placement["x"])
    y = int(placement["y"])
    z = int(placement["z"])
    width, depth = (int(value) for value in placement["size"][:2])
    participant_id = str(placement["participant_id"])
    for other in placements:
        if str(other.get("participant_id")) == participant_id:
            continue
        other_size = other.get("size")
        if not isinstance(other_size, list) or len(other_size) != 3:
            return True
        if not _raw_xy_overlaps(
            x,
            y,
            width,
            depth,
            int(other["x"]),
            int(other["y"]),
            int(other_size[0]),
            int(other_size[1]),
        ):
            continue
        other_z = int(other["z"])
        if z < other_z + int(other_size[2]) and other_z < z + required_height:
            return True
    return False

def _invoke_worker_once(
    prepared: _PreparedProductProblem,
    limits: ScipProductLimits,
) -> dict[str, object]:
    worker = _load_worker()
    scratch = _configured_scratch_root
    if scratch is not None:
        scratch.mkdir(parents=True, exist_ok=True)
    worker_input = _worker_input(prepared, limits)
    with tempfile.TemporaryDirectory(
        prefix="bgig-scip-product-",
        dir=str(scratch) if scratch is not None else None,
    ) as temporary:
        root = Path(temporary)
        input_path = root / "input.json"
        output_path = root / "output.json"
        input_path.write_text(
            json.dumps(worker_input, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        worker.main(str(input_path), str(output_path))
        output = _read_json(output_path)
    supplied_output_digest = output.pop("output_digest", None)
    if supplied_output_digest != canonical_digest(output):
        raise RuntimeError("SCIP worker output digest mismatch.")
    if (
        output.get("schema_version") != _OUTPUT_SCHEMA
        or output.get("candidate_id") != "scip"
        or output.get("input_digest") != worker_input["input_digest"]
    ):
        raise RuntimeError("SCIP worker output binding mismatch.")
    output["output_digest"] = supplied_output_digest
    return output


def _worker_input(
    prepared: _PreparedProductProblem,
    limits: ScipProductLimits,
) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": _INPUT_SCHEMA,
        "candidate_id": "scip",
        "problem": prepared.payload,
        "limits": limits.to_dict(),
        "exact_control": False,
    }
    value["input_digest"] = canonical_digest(value)
    return value


def _rebind_worker_output(
    output: dict[str, object],
    prepared: _PreparedProductProblem,
    limits: ScipProductLimits,
) -> dict[str, object]:
    rebound = dict(output)
    rebound.pop("output_digest", None)
    rebound["input_digest"] = _worker_input(prepared, limits)["input_digest"]
    rebound["output_digest"] = canonical_digest(rebound)
    return rebound


def _hybrid_deferred_participant_ids(
    prepared: _PreparedProductProblem,
) -> tuple[str, ...]:
    payload = prepared.payload
    participants = payload.get("participants")
    world = payload.get("world_mm")
    if (
        not isinstance(participants, list)
        or not isinstance(world, list)
        or payload.get("reservation_volumes")
        or payload.get("top_inset_zones")
        or payload.get("access_precedence_edges")
        or "disjoint_regions" in payload.get("active_constraints", [])
    ):
        return ()
    groups: dict[tuple[object, ...], list[str]] = {}
    for participant in participants:
        if not isinstance(participant, Mapping):
            return ()
        variants = participant.get("variants")
        if (
            not isinstance(variants, list)
            or len(variants) != 1
            or int(participant.get("minimum_support_count", 1)) != 1
            or not bool(participant.get("ground_allowed", True))
            or int(participant.get("required_support_area_mm2", 0)) != 0
        ):
            continue
        variant = variants[0]
        if not isinstance(variant, Mapping):
            continue
        size = tuple(int(value) for value in variant.get("size", []))
        rotations = tuple(str(value) for value in variant.get("allowed_rotations", ["xyz"]))
        if len(size) != 3 or not rotations:
            continue
        horizontal = (max(size[0], size[1]), max(size[0], size[1]))
        if (
            horizontal[0] * 4 > int(world[0])
            or horizontal[1] * 4 > int(world[1])
            or size[2] * 4 > int(world[2])
        ):
            continue
        key = (
            size,
            rotations,
            int(participant.get("assigned_content_count", 0)),
        )
        groups.setdefault(key, []).append(str(participant["participant_id"]))
    deferred: set[str] = set()
    for participant_ids in groups.values():
        if len(participant_ids) >= 4:
            deferred.update(participant_ids[2:])
    return tuple(
        str(value["participant_id"])
        for value in participants
        if str(value["participant_id"]) in deferred
    )


def _prepared_without_participants(
    prepared: _PreparedProductProblem,
    deferred_ids: Sequence[str],
) -> _PreparedProductProblem:
    payload = deepcopy(prepared.payload)
    deferred = set(deferred_ids)
    payload["participants"] = [
        value for value in payload["participants"] if str(value["participant_id"]) not in deferred
    ]
    payload.pop("problem_digest", None)
    payload["problem_digest"] = canonical_digest(payload)
    return replace(
        prepared,
        payload=payload,
        problem_digest=str(payload["problem_digest"]),
    )


def _place_deferred_participant(
    participant: Mapping[str, object],
    placements: Sequence[Mapping[str, object]],
    world: tuple[int, int, int],
) -> dict[str, object] | None:
    variants = participant["variants"]
    if not isinstance(variants, list):
        return None
    x_values = sorted({0, *(int(value["x"]) + int(value["size"][0]) for value in placements)})
    y_values = sorted({0, *(int(value["y"]) + int(value["size"][1]) for value in placements)})
    z_values = sorted({0, *(int(value["z"]) + int(value["size"][2]) for value in placements)})
    candidates: list[tuple[tuple[object, ...], dict[str, object]]] = []
    for variant in variants:
        if not isinstance(variant, Mapping):
            continue
        base_size = tuple(int(value) for value in variant["size"])
        for orientation in variant.get("allowed_rotations", ["xyz"]):
            size = base_size if orientation == "xyz" else (base_size[1], base_size[0], base_size[2])
            width, depth, height = size
            for z in z_values:
                for y in y_values:
                    for x in x_values:
                        if x + width > world[0] or y + depth > world[1] or z + height > world[2]:
                            continue
                        candidate = (x, y, z, width, depth, height)
                        if any(_raw_placements_overlap(candidate, value) for value in placements):
                            continue
                        supports = _raw_support_ids(x, y, z, width, depth, placements)
                        if z != 0 and not supports:
                            continue
                        record = {
                            "participant_id": participant["participant_id"],
                            "x": x,
                            "y": y,
                            "z": z,
                            "size": list(size),
                            "orientation": str(orientation),
                            "selected_variant_id": variant["variant_id"],
                            "assigned_content_count": participant.get("assigned_content_count", 0),
                            "support_ids": supports,
                            "removal_rank": world[2] - z,
                        }
                        rank = (
                            z + height,
                            z,
                            y,
                            x,
                            str(orientation),
                            str(variant["variant_id"]),
                        )
                        candidates.append((rank, record))
    return min(candidates, key=lambda value: value[0])[1] if candidates else None


def _raw_placements_overlap(
    candidate: tuple[int, int, int, int, int, int],
    placed: Mapping[str, object],
) -> bool:
    x, y, z, width, depth, height = candidate
    placed_size = placed["size"]
    return not (
        x + width <= int(placed["x"])
        or int(placed["x"]) + int(placed_size[0]) <= x
        or y + depth <= int(placed["y"])
        or int(placed["y"]) + int(placed_size[1]) <= y
        or z + height <= int(placed["z"])
        or int(placed["z"]) + int(placed_size[2]) <= z
    )


def _raw_support_ids(
    x: int,
    y: int,
    z: int,
    width: int,
    depth: int,
    placements: Sequence[Mapping[str, object]],
) -> list[str]:
    return [
        str(value["participant_id"])
        for value in placements
        if int(value["z"]) + int(value["size"][2]) == z
        and int(value["x"]) <= x
        and int(value["y"]) <= y
        and int(value["x"]) + int(value["size"][0]) >= x + width
        and int(value["y"]) + int(value["size"][1]) >= y + depth
    ]


def _load_worker() -> ModuleType:
    global _loaded_worker
    if _loaded_worker is not None:
        return _loaded_worker
    if _configured_runtime_root is None or _configured_worker_root is None:
        raise RuntimeError("SCIP runtime is not configured.")
    site_packages = _configured_runtime_root / "site-packages"
    pyscipopt_dir = site_packages / "pyscipopt"
    numpy_libs = site_packages / "numpy.libs"
    for directory in (pyscipopt_dir, numpy_libs):
        handle = os.add_dll_directory(str(directory))
        _dll_handles.append(handle)
    sys.path.insert(0, str(site_packages))
    previous_dont_write = sys.dont_write_bytecode
    previous_common = sys.modules.get("_real_3d_worker_common")
    sys.dont_write_bytecode = True
    try:
        common_path = _configured_worker_root / "_real_3d_worker_common.py"
        common_spec = importlib.util.spec_from_file_location("_real_3d_worker_common", common_path)
        if common_spec is None or common_spec.loader is None:
            raise ImportError("Cannot load the sealed SCIP common worker.")
        common = importlib.util.module_from_spec(common_spec)
        sys.modules["_real_3d_worker_common"] = common
        common_spec.loader.exec_module(common)
        worker_path = _configured_worker_root / "scip_real_3d_worker.py"
        worker_spec = importlib.util.spec_from_file_location(
            "bgig_scip_product_worker", worker_path
        )
        if worker_spec is None or worker_spec.loader is None:
            raise ImportError("Cannot load the sealed SCIP worker.")
        worker = importlib.util.module_from_spec(worker_spec)
        worker_spec.loader.exec_module(worker)
        pyscipopt_module = sys.modules.get("pyscipopt")
        if (
            pyscipopt_module is None
            or getattr(pyscipopt_module, "__version__", None) != SCIP_PRODUCT_PYSCIPOPT_VERSION
        ):
            raise ImportError("Unexpected PySCIPOpt product version.")
        numpy_module = sys.modules.get("numpy")
        if (
            numpy_module is None
            or getattr(numpy_module, "__version__", None) != SCIP_PRODUCT_NUMPY_VERSION
        ):
            raise ImportError("Unexpected NumPy product version.")
        _loaded_worker = worker
        return worker
    finally:
        sys.dont_write_bytecode = previous_dont_write
        if previous_common is None:
            sys.modules.pop("_real_3d_worker_common", None)
        else:
            sys.modules["_real_3d_worker_common"] = previous_common


def _convert_placements(
    raw_placements: object,
    prepared: _PreparedProductProblem,
) -> tuple[Free3DPlacement, ...]:
    if not isinstance(raw_placements, list):
        raise ValueError("SCIP placements must be a list.")
    preliminary: list[Free3DPlacement] = []
    seen: set[str] = set()
    for raw in raw_placements:
        if not isinstance(raw, Mapping):
            raise ValueError("Invalid SCIP placement record.")
        participant_id = str(raw["participant_id"])
        variant_id = str(raw["selected_variant_id"])
        option = prepared.options[(participant_id, variant_id)]
        if participant_id in seen:
            raise ValueError("Duplicate SCIP participant placement.")
        seen.add(participant_id)
        orientation = str(raw["orientation"])
        if orientation not in {"xyz", "yxz"}:
            raise ValueError("Unsupported SCIP orientation.")
        raw_size = raw.get("size")
        if (
            not isinstance(raw_size, list)
            or len(raw_size) != 3
            or any(not isinstance(value, int) or isinstance(value, bool) for value in raw_size)
        ):
            raise ValueError("Invalid SCIP placement size.")
        base_local_size = option.local_size_mm
        expected_world_xy = (
            (base_local_size[1], base_local_size[0])
            if orientation == "yxz"
            else (base_local_size[0], base_local_size[1])
        )
        expected_padded_xy = tuple(
            _scaled_exact(value + prepared.xy_clearance_mm)
            for value in expected_world_xy
        )
        if tuple(raw_size[:2]) != expected_padded_xy:
            raise ValueError("Unexpected SCIP XY placement size.")
        base_padded_z = _scaled_exact(base_local_size[2] + prepared.z_clearance_mm)
        if raw_size[2] < base_padded_z:
            raise ValueError("SCIP placement shrinks below its selected variant.")
        expands_z = raw_size[2] > base_padded_z
        participant = prepared.participants[participant_id]
        dimension_modes = participant.get("dimension_modes")
        allows_z_expansion = bool(
            option.role == "container"
            and prepared.payload.get("top_inset_zones")
            and isinstance(dimension_modes, Mapping)
            and str(dimension_modes.get("z")) != "fixed"
        )
        if expands_z and not allows_z_expansion:
            raise ValueError("Unexpected SCIP Z expansion.")
        raw_z = int(raw["z"])
        if raw_z + raw_size[2] > int(prepared.payload["world_mm"][2]):
            raise ValueError("SCIP placement exceeds the Z world bound.")
        local_size = (
            base_local_size[0],
            base_local_size[1],
            _unscaled(raw_size[2] - _scaled_exact(prepared.z_clearance_mm)),
        )
        world_size = (
            (local_size[1], local_size[0], local_size[2]) if orientation == "yxz" else local_size
        )
        origin = (
            _unscaled(int(raw["x"])) + prepared.box_clearance_mm,
            _unscaled(int(raw["y"])) + prepared.box_clearance_mm,
            _unscaled(raw_z),
        )
        common = {
            "participant_id": participant_id,
            "role": option.role,
            "name": option.name,
            "origin_mm": origin,
            "world_size_mm": world_size,
            "local_size_mm": local_size,
            "rotation_deg_z": 90 if orientation == "yxz" else 0,
            "supporting_ids": (),
            "support_coverage_ratio": 0.0,
        }
        if option.role == "container":
            preliminary.append(
                VariantFree3DPlacement(
                    **common,
                    container_variant_id=option.variant_id,
                    container_variant_digest=option.variant_digest,
                    container_variant_canonical=option.variant_canonical,
                )
            )
        else:
            preliminary.append(Free3DPlacement(**common))
    if seen != set(prepared.participants):
        raise ValueError("SCIP participant set is incomplete.")
    resolved = []
    for placement in preliminary:
        participant = prepared.participants[placement.participant_id]
        support = _support_at(
            placement.origin_mm,
            placement.world_size_mm,
            [other for other in preliminary if other.participant_id != placement.participant_id],
            participant,
            prepared.participants,
            prepared.xy_clearance_mm,
            prepared.z_clearance_mm,
        )
        resolved.append(
            replace(
                placement,
                supporting_ids=support.supporting_ids,
                support_coverage_ratio=round(support.coverage_ratio, 6),
            )
        )
    return tuple(sorted(resolved, key=lambda value: value.participant_id))


def _placement_payload(value: Free3DPlacement) -> dict[str, object]:
    payload = {
        "participant_id": value.participant_id,
        "origin_mm": list(value.origin_mm),
        "world_size_mm": list(value.world_size_mm),
        "local_size_mm": list(value.local_size_mm),
        "rotation_deg_z": value.rotation_deg_z,
        "supporting_ids": list(value.supporting_ids),
        "support_coverage_ratio": value.support_coverage_ratio,
    }
    if isinstance(value, VariantFree3DPlacement):
        payload["container_variant_id"] = value.container_variant_id
        payload["container_variant_digest"] = value.container_variant_digest
    return payload


def _empty_execution(
    limits: ScipProductLimits,
    *,
    status: str,
    stop_reason: str,
    problem_digest: str = "",
    invocation_count: int = 0,
    engine_status: str = "not_started",
    model_digest: str = "",
    total_wall_seconds: float | None = None,
) -> ScipProductExecution:
    return ScipProductExecution(
        status=status,
        stop_reason=stop_reason,
        limits=limits,
        problem_digest=problem_digest,
        engine_status=engine_status,
        placements=(),
        model_digest=model_digest,
        solution_digest="",
        invocation_count=invocation_count,
        total_wall_seconds=total_wall_seconds,
    )


def _runtime_tree(root: Path) -> dict[str, object]:
    records = []
    for path in sorted(
        (value for value in root.rglob("*") if value.is_file()),
        key=lambda value: value.relative_to(root).as_posix().lower(),
    ):
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return {
        "file_count": len(records),
        "size_bytes": sum(int(item["size_bytes"]) for item in records),
        "tree_digest": canonical_digest({"files": records}),
    }


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scaled_exact(value: float) -> int:
    scaled = int(round(float(value) * _SCALE_PER_MM))
    if abs(scaled / _SCALE_PER_MM - float(value)) > _EPSILON_MM:
        raise ValueError("Millimetre value is not exactly representable.")
    return scaled


def _unscaled(value: int) -> float:
    return round(value / _SCALE_PER_MM, 3)


def _exact_mm(value: float) -> float:
    return _unscaled(_scaled_exact(value))
