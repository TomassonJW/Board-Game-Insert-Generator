"""Lane produit SCIP 3D locale, hors ligne et recertifiée par BGIG."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import importlib.util
import json
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
    _support_at,
)
from board_game_insert_generator.free_3d_plan_adapter import Free3DPreparedProblem
from board_game_insert_generator.incremental_project_state import canonical_digest

SCIP_PRODUCT_SCHEMA_V1 = "bgig.scip_product_lane.v1"
SCIP_PRODUCT_VERSION = "10.0.2"
SCIP_PRODUCT_PYSCIPOPT_VERSION = "6.2.1"
SCIP_PRODUCT_SOPLEX_VERSION = "8.0.2"
SCIP_PRODUCT_NUMPY_VERSION = "2.5.1"
SCIP_PRODUCT_FAMILY = "constraint_integer_programming"
SCIP_PRODUCT_MODEL = "integer_xyz_big_m_disjunction_and_explicit_support"
SCIP_PRODUCT_ARTIFACT_DIGEST = "540e2fe6b9324f2d58afbdaab827760f98b6b0e4ab9f626efdaee69d2c6d2786"
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

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class _ProductOption:
    participant_id: str
    role: str
    name: str
    variant_id: str
    local_size_mm: tuple[float, float, float]
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
            "limits": self.limits.to_dict(),
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
    if effort_profile == "quick":
        return ScipProductLimits(wall_seconds=1.0)
    if effort_profile == "normal":
        return ScipProductLimits(wall_seconds=5.0)
    if effort_profile == "deep":
        return ScipProductLimits(wall_seconds=30.0)
    raise ValueError(f"Unknown effort profile {effort_profile!r}.")


def solve_scip_product_3d(
    participants: Sequence[Mapping[str, object]],
    problem: Free3DPreparedProblem,
    *,
    effort_profile: str,
    cancel_check: Callable[[], bool] | None = None,
) -> ScipProductExecution:
    limits = scip_product_limits(effort_profile)
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
    if cancel_check is not None and cancel_check():
        return _empty_execution(
            limits,
            status=STATUS_CANCELLED,
            stop_reason="cancelled_after_native_solve",
            problem_digest=prepared.problem_digest,
            invocation_count=1,
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
            invocation_count=1,
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
            invocation_count=1,
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
        invocation_count=1,
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
    if problem.top_inset_zones:
        return None, "top_inset_reservations_not_supported"
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
        worker_participants = []
        option_records: dict[tuple[str, str], _ProductOption] = {}
        participant_records: dict[str, dict[str, object]] = {}
        for raw in participants:
            participant = deepcopy(dict(raw))
            participant_id = str(participant["id"])
            if participant_id in participant_records:
                return None, "duplicate_participant_id"
            participant_records[participant_id] = participant
            options = _participant_options(participant)
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
                    }
                )
            worker_participants.append(
                {
                    "participant_id": participant_id,
                    "assigned_content_count": 0,
                    "variants": worker_variants,
                    "minimum_support_count": 1,
                    "ground_allowed": True,
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
    if len(worker_participants) >= 24:
        active_constraints.append("high_container_cardinality")
    payload: dict[str, object] = {
        "case_id": "bgig-product-explicit-solve",
        "world_mm": world,
        "participants": worker_participants,
        "active_constraints": active_constraints,
        "reservation_volumes": [],
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


def _participant_options(participant: Mapping[str, object]) -> tuple[_ProductOption, ...]:
    participant_id = str(participant["id"])
    role = str(participant["role"])
    name = str(participant["name"])
    raw_variants = participant.get("container_internal_variant_options_v1")
    variants = raw_variants if role == "container" and isinstance(raw_variants, list) else []
    if not variants:
        local = _resolved_local_size(participant, participant["minimum_local_mm"])
        return (
            _ProductOption(
                participant_id=participant_id,
                role=role,
                name=name,
                variant_id=f"canonical:{participant_id}",
                local_size_mm=local,
                variant_digest="",
                variant_canonical=True,
            ),
        )
    result = []
    for value in variants:
        if not isinstance(value, Mapping):
            raise ValueError("Invalid product variant option.")
        try:
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
                variant_digest=str(value["geometry_digest"]),
                variant_canonical=bool(value.get("canonical", False)),
            )
        )
    if not result:
        raise ValueError("No product variant satisfies the fixed dimensions.")
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
    worker = _load_worker()
    scratch = _configured_scratch_root
    if scratch is not None:
        scratch.mkdir(parents=True, exist_ok=True)
    worker_input: dict[str, object] = {
        "schema_version": _INPUT_SCHEMA,
        "candidate_id": "scip",
        "problem": prepared.payload,
        "limits": limits.to_dict(),
        "exact_control": False,
    }
    worker_input["input_digest"] = canonical_digest(worker_input)
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
        local_size = option.local_size_mm
        world_size = (
            (local_size[1], local_size[0], local_size[2]) if orientation == "yxz" else local_size
        )
        origin = (
            _unscaled(int(raw["x"])) + prepared.box_clearance_mm,
            _unscaled(int(raw["y"])) + prepared.box_clearance_mm,
            _unscaled(int(raw["z"])),
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
        support_ids, support_ratio = _support_at(
            placement.origin_mm,
            placement.world_size_mm,
            [other for other in preliminary if other.participant_id != placement.participant_id],
            participant,
            prepared.z_clearance_mm,
        )
        resolved.append(
            replace(
                placement,
                supporting_ids=support_ids,
                support_coverage_ratio=round(support_ratio, 6),
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
