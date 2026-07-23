"""Adapters isolés et recertifiés du tournoi externe P64-L07C.

Le coeur BGIG ne charge aucun package candidat. Chaque moteur tourne dans un
processus hors ligne, reçoit le même problème rectangulaire sur un seul niveau,
puis toute sortie positive est reconstruite et certifiée par BGIG.
"""

from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from copy import deepcopy
from dataclasses import dataclass
import ctypes
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from time import perf_counter, sleep
from typing import Mapping, Sequence

from board_game_insert_generator.external_solver_artifacts import (
    external_solver_candidate_catalog,
    validate_external_solver_artifact_lock,
    validate_external_solver_artifact_receipt,
)
from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.free_3d_plan_adapter import (
    Free3DPreparedProblem,
    certify_minimal_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import (
    blank_project_v1,
    normalize_project_draft,
)
from board_game_insert_generator.solver_contract import SolverBudget, SolverStrategy


EXTERNAL_ADAPTER_RESULT_SCHEMA_V2 = "bgig.external_solver_adapter_result.v2"
EXTERNAL_FLOOR_MODEL_SCHEMA_V1 = "bgig.external_floor_problem.v1"
EXTERNAL_WORKER_INPUT_SCHEMA_V1 = "P64L07FLOOR"
EXTERNAL_WORKER_OUTPUT_SCHEMA_V1 = "P64L07RESULT"
EXTERNAL_WORKER_PROTOCOL_VERSION = "1"
EXTERNAL_ADAPTER_CONTROL_SCHEMA_V1 = "bgig.external_adapter_controls.v1"
STATUS_SOLUTION_FOUND = "solution_found"
STATUS_INFEASIBLE_PROVEN = "infeasible_proven"
STATUS_BOUNDED_UNKNOWN = "bounded_unknown"
STATUS_UNSUPPORTED = "unsupported"
STATUS_INVALID_INPUT = "invalid_input"
STATUS_CERTIFICATE_REJECTED = "certificate_rejected"
STATUS_EXTERNAL_ERROR = "external_error"
_SCALE_PER_MM = 1000
_EPSILON_MM = 0.000001
_MAX_ITEM_COUNT = 64


class ExternalSolverAdapterError(ValueError):
    """Entrée, configuration ou sortie de worker externe invalide."""


@dataclass(frozen=True)
class ExternalSolverLimits:
    """Enveloppe totale identique donnée à chaque candidat."""

    wall_seconds: float = 5.0
    memory_mebibytes: int = 1024
    threads: int = 1
    seed: int = 640_707

    def __post_init__(self) -> None:
        if (
            isinstance(self.wall_seconds, bool)
            or not isinstance(self.wall_seconds, (int, float))
            or not 0.1 <= float(self.wall_seconds) <= 3600.0
            or isinstance(self.memory_mebibytes, bool)
            or not isinstance(self.memory_mebibytes, int)
            or not 64 <= self.memory_mebibytes <= 8192
            or isinstance(self.threads, bool)
            or not isinstance(self.threads, int)
            or not 1 <= self.threads <= 2
            or isinstance(self.seed, bool)
            or not isinstance(self.seed, int)
            or self.seed < 0
        ):
            raise ValueError("External solver limits are outside P64-L07.")

    def to_dict(self) -> dict[str, object]:
        return {
            "memory_mebibytes": self.memory_mebibytes,
            "seed": self.seed,
            "threads": self.threads,
            "wall_seconds": float(self.wall_seconds),
        }


@dataclass(frozen=True)
class ExternalSolverRuntime:
    """Commande locale déjà préparée, sans chemin publié dans le rapport."""

    candidate_id: str
    command: tuple[str, ...]
    environment: tuple[tuple[str, str], ...]
    scratch_root: str
    worker_digest: str

    def __post_init__(self) -> None:
        if (
            not self.candidate_id
            or not self.command
            or any(not isinstance(value, str) or not value for value in self.command)
            or not _is_digest(self.worker_digest)
            or not self.scratch_root
            or any(
                not isinstance(key, str)
                or not key
                or not isinstance(value, str)
                for key, value in self.environment
            )
        ):
            raise ValueError("External solver runtime is invalid.")


@dataclass(frozen=True)
class ExternalFloorItem:
    participant_id: str
    role: str
    name: str
    local_size_mm: tuple[float, float, float]
    packed_width: int
    packed_height: int


@dataclass(frozen=True)
class ExternalFloorProblem:
    case_id: str
    project_digest: str
    family: str
    split: str
    prepared: Free3DPreparedProblem
    bin_width: int
    bin_height: int
    scale_per_mm: int
    box_clearance_mm: float
    between_clearance_mm: float
    rotation_allowed: bool
    complete_for_infeasibility: bool
    items: tuple[ExternalFloorItem, ...]
    constraints: tuple[str, ...]

    @property
    def problem_digest(self) -> str:
        return canonical_digest(
            {
                "schema_version": EXTERNAL_FLOOR_MODEL_SCHEMA_V1,
                "case_id": self.case_id,
                "project_digest": self.project_digest,
                "bin_width": self.bin_width,
                "bin_height": self.bin_height,
                "scale_per_mm": self.scale_per_mm,
                "rotation_allowed": self.rotation_allowed,
                "complete_for_infeasibility": self.complete_for_infeasibility,
                "items": [
                    {
                        "participant_id": item.participant_id,
                        "packed_width": item.packed_width,
                        "packed_height": item.packed_height,
                    }
                    for item in self.items
                ],
                "constraints": list(self.constraints),
            }
        )


@dataclass(frozen=True)
class ExternalFloorPreparation:
    status: str
    problem: ExternalFloorProblem | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ExternalAdapterExecution:
    report: dict[str, object]
    certified_plan: dict[str, object] | None


@dataclass(frozen=True)
class _WorkerPlacement:
    participant_id: str
    x: int
    y: int
    rotation_deg_z: int


@dataclass(frozen=True)
class _WorkerOutput:
    raw_status: str
    engine_status: str
    solve_ms: float
    placements: tuple[_WorkerPlacement, ...]
    metrics: tuple[tuple[str, str], ...]
    output_digest: str


def build_external_adapter_exact_controls() -> dict[str, object]:
    """Construit trois cas BGIG exacts propres à L07C, sans oracle caché."""

    definitions = (
        (
            "l07c-exact-feasible-floor",
            "feasible",
            (100.0, 80.0, 10.0),
            (40.0, 40.0, 10.0),
            2,
        ),
        (
            "l07c-exact-rotation-required",
            "feasible",
            (110.0, 70.0, 10.0),
            (70.0, 40.0, 10.0),
            2,
        ),
        (
            "l07c-exact-infeasible-floor",
            "infeasible",
            (100.0, 80.0, 10.0),
            (60.0, 60.0, 10.0),
            2,
        ),
    )
    cases = []
    for case_id, truth, box, item_size, item_count in definitions:
        project = _build_control_project(case_id, box, item_size, item_count)
        cases.append(
            {
                "case_id": case_id,
                "family": "l07c_small_exact_floor",
                "split": "adapter_control",
                "project": project,
                "project_digest": canonical_digest(project),
                "solver_settings": {"effort": "quick", "method": "auto"},
                "features": {
                    "execution_mode": "cold",
                    "layer_target": 1,
                    "reservation_mode": "absent",
                    "rotation_policy_target": "permitted",
                },
                "exact_truth": truth,
                "truth_basis": (
                    "constructive_witness"
                    if truth == "feasible"
                    else "two_60_by_60_rectangles_cannot_fit_100_by_80"
                ),
                "oracle_payload_supplied_to_worker": False,
            }
        )
    payload: dict[str, object] = {
        "schema_version": EXTERNAL_ADAPTER_CONTROL_SCHEMA_V1,
        "model": "axis_aligned_single_floor_rectangles_v1",
        "cases": cases,
        "case_count": len(cases),
        "invariants": {
            "holdout_case_count": 0,
            "oracle_payload_supplied_to_worker": False,
            "t0_t1_only": True,
        },
    }
    payload["controls_digest"] = canonical_digest(payload)
    return payload


def prepare_external_floor_case(case: object) -> ExternalFloorPreparation:
    """Convertit un projet BGIG sans retirer une contrainte déclarée."""

    if not isinstance(case, Mapping):
        return ExternalFloorPreparation(
            STATUS_INVALID_INPUT, None, ("case_must_be_an_object",)
        )
    value = deepcopy(dict(case))
    case_id = str(value.get("case_id", "")).strip()
    if not case_id:
        return ExternalFloorPreparation(
            STATUS_INVALID_INPUT, None, ("case_id_is_required",)
        )
    try:
        project = normalize_project_draft(value.get("project")).project
    except (TypeError, ValueError) as exc:
        return ExternalFloorPreparation(
            STATUS_INVALID_INPUT,
            None,
            (f"project_normalization_failed:{type(exc).__name__}",),
        )
    project_digest = str(value.get("project_digest", ""))
    if canonical_digest(project) != project_digest:
        return ExternalFloorPreparation(
            STATUS_INVALID_INPUT, None, ("project_digest_mismatch",)
        )
    settings = _mapping_or_empty(value.get("solver_settings"))
    if settings.get("method", "auto") != "auto":
        return ExternalFloorPreparation(
            STATUS_UNSUPPORTED, None, ("non_auto_solver_method",)
        )
    features = _mapping_or_empty(value.get("features"))
    unsupported: list[str] = []
    if str(features.get("execution_mode", "cold")) != "cold":
        unsupported.append("incremental_state_not_represented")
    layer_target = features.get("layer_target")
    if layer_target is not None and layer_target != 1:
        unsupported.append("multiple_layers_required_by_case")
    reservation_mode = features.get("reservation_mode")
    if reservation_mode not in {None, "absent"}:
        unsupported.append("benchmark_reservation_constraint_not_represented")
    rotation_policy = str(
        features.get("rotation_policy_target", "permitted")
    )
    if rotation_policy not in {"permitted", "forbidden_by_benchmark"}:
        unsupported.append("rotation_policy_is_not_explicit")
    if unsupported:
        return ExternalFloorPreparation(
            STATUS_UNSUPPORTED, None, tuple(sorted(set(unsupported)))
        )
    preparation = prepare_free_3d_problem(project)
    if preparation.problem is None:
        return ExternalFloorPreparation(
            STATUS_INVALID_INPUT, None, preparation.rejection_codes
        )
    prepared = preparation.problem
    if prepared.top_inset_zones:
        return ExternalFloorPreparation(
            STATUS_UNSUPPORTED,
            None,
            ("resolved_top_inset_reservation_not_represented",),
        )
    if not 1 <= len(prepared.participants) <= _MAX_ITEM_COUNT:
        return ExternalFloorPreparation(
            STATUS_UNSUPPORTED, None, ("participant_count_outside_adapter_cap",)
        )
    dimensions: list[tuple[dict[str, object], tuple[float, float, float]]] = []
    for participant in prepared.participants:
        minimum = _mapping_or_empty(participant.get("minimum_local_mm"))
        target = _mapping_or_empty(participant.get("target_local_mm"))
        modes = _mapping_or_empty(participant.get("dimension_modes"))
        if any(
            modes.get(axis) == "fixed"
            and target.get(axis) is not None
            and abs(float(target[axis]) - float(minimum[axis])) > _EPSILON_MM
            for axis in ("x", "y", "z")
        ):
            return ExternalFloorPreparation(
                STATUS_UNSUPPORTED,
                None,
                ("fixed_expanded_envelope_not_supported_by_minimal_certificate",),
            )
        local = tuple(float(minimum[axis]) for axis in ("x", "y", "z"))
        if any(number <= 0.0 for number in local):
            return ExternalFloorPreparation(
                STATUS_INVALID_INPUT, None, ("non_positive_participant_size",)
            )
        if local[2] > prepared.storage_height_mm + _EPSILON_MM:
            return ExternalFloorPreparation(
                STATUS_INVALID_INPUT,
                None,
                ("participant_height_exceeds_storage_height",),
            )
        dimensions.append((dict(participant), local))
    box_clearance = float(prepared.box_xy_clearance_mm)
    between_clearance = float(prepared.xy_clearance_mm)
    usable_x = prepared.box["x"] - 2.0 * box_clearance
    usable_y = prepared.box["y"] - 2.0 * box_clearance
    if usable_x <= 0.0 or usable_y <= 0.0:
        return ExternalFloorPreparation(
            STATUS_INVALID_INPUT, None, ("non_positive_floor_bounds",)
        )
    try:
        bin_width = _scaled(usable_x + between_clearance)
        bin_height = _scaled(usable_y + between_clearance)
        items = tuple(
            ExternalFloorItem(
                participant_id=str(participant["id"]),
                role=str(participant["role"]),
                name=str(participant["name"]),
                local_size_mm=local,
                packed_width=_scaled(local[0] + between_clearance),
                packed_height=_scaled(local[1] + between_clearance),
            )
            for participant, local in dimensions
        )
    except ExternalSolverAdapterError as exc:
        return ExternalFloorPreparation(
            STATUS_UNSUPPORTED, None, (str(exc),)
        )
    uniform_clearances = _uniform_clearances(
        prepared, box_clearance, between_clearance
    )
    complete = (
        layer_target == 1
        and reservation_mode == "absent"
        and uniform_clearances
    )
    problem = ExternalFloorProblem(
        case_id=case_id,
        project_digest=project_digest,
        family=str(value.get("family", "regression")),
        split=str(value.get("split", "regression")),
        prepared=prepared,
        bin_width=bin_width,
        bin_height=bin_height,
        scale_per_mm=_SCALE_PER_MM,
        box_clearance_mm=box_clearance,
        between_clearance_mm=between_clearance,
        rotation_allowed=rotation_policy == "permitted",
        complete_for_infeasibility=complete,
        items=items,
        constraints=(
            "all_requested_participants",
            "axis_aligned_rectangles",
            "box_xy_clearance",
            "container_between_xy_clearance",
            "floor_origin_z_zero",
            "single_floor_only",
            "z_rotation_only",
        ),
    )
    return ExternalFloorPreparation("ready", problem, ())


def run_external_solver_adapter(
    case: object,
    candidate_id: str,
    *,
    artifact_lock: object,
    artifact_receipt: object,
    runtime: ExternalSolverRuntime,
    limits: ExternalSolverLimits | None = None,
) -> ExternalAdapterExecution:
    """Exécute un candidat isolé puis refuse toute sortie non certifiée."""

    accepted_lock = validate_external_solver_artifact_lock(artifact_lock)
    catalog = {
        str(item["candidate_id"]): item
        for item in external_solver_candidate_catalog(accepted_lock)
    }
    if candidate_id not in catalog:
        raise ExternalSolverAdapterError(
            f"Unknown external solver candidate {candidate_id!r}."
        )
    if runtime.candidate_id != candidate_id:
        raise ExternalSolverAdapterError(
            "External solver runtime candidate mismatch."
        )
    receipt = validate_external_solver_artifact_receipt(
        artifact_receipt,
        lock=accepted_lock,
        candidate_id=candidate_id,
    )
    candidate = catalog[candidate_id]
    envelope = limits or ExternalSolverLimits()
    preparation = prepare_external_floor_case(case)
    if preparation.problem is None:
        report = _report_without_worker(
            case,
            candidate,
            receipt,
            envelope,
            status=preparation.status,
            reasons=preparation.reasons,
        )
        return ExternalAdapterExecution(report, None)
    problem = preparation.problem
    worker_run = _execute_worker(problem, runtime, envelope)
    execution_status = str(worker_run["execution_status"])
    if execution_status != "completed":
        bounded_limit = execution_status in {
            "wall_time_limit_exceeded",
            "memory_limit_exceeded",
        }
        report = _report_from_worker(
            problem,
            candidate,
            receipt,
            envelope,
            worker_run,
            worker_output=None,
            status=(
                STATUS_BOUNDED_UNKNOWN
                if bounded_limit
                else STATUS_EXTERNAL_ERROR
            ),
            stop_reason=execution_status,
            recertification=_not_attempted_certificate(),
            solution=None,
        )
        return ExternalAdapterExecution(report, None)
    try:
        output = _parse_worker_output(
            Path(str(worker_run["output_path"])), problem
        )
    except (OSError, UnicodeError, ValueError) as exc:
        report = _report_from_worker(
            problem,
            candidate,
            receipt,
            envelope,
            worker_run,
            worker_output=None,
            status=STATUS_EXTERNAL_ERROR,
            stop_reason=f"invalid_worker_output:{type(exc).__name__}",
            recertification=_not_attempted_certificate(),
            solution=None,
        )
        return ExternalAdapterExecution(report, None)
    if output.raw_status == "feasible":
        return _recertify_external_solution(
            problem,
            candidate,
            receipt,
            envelope,
            worker_run,
            output,
        )
    if (
        output.raw_status == "infeasible"
        and bool(candidate["exact_for_floor_model"])
        and problem.complete_for_infeasibility
    ):
        status = STATUS_INFEASIBLE_PROVEN
        reason = "exact_declared_floor_model_proven_infeasible"
    else:
        status = STATUS_BOUNDED_UNKNOWN
        reason = (
            "candidate_cannot_prove_infeasibility"
            if output.raw_status == "infeasible"
            else "candidate_returned_no_certifiable_solution"
        )
    report = _report_from_worker(
        problem,
        candidate,
        receipt,
        envelope,
        worker_run,
        worker_output=output,
        status=status,
        stop_reason=reason,
        recertification=_not_attempted_certificate(),
        solution=None,
    )
    return ExternalAdapterExecution(report, None)


def _recertify_external_solution(
    problem: ExternalFloorProblem,
    candidate: Mapping[str, object],
    receipt: Mapping[str, object],
    limits: ExternalSolverLimits,
    worker_run: Mapping[str, object],
    output: _WorkerOutput,
) -> ExternalAdapterExecution:
    by_id = {item.participant_id: item for item in problem.items}
    placements = []
    for proposed in output.placements:
        item = by_id[proposed.participant_id]
        rotated = proposed.rotation_deg_z == 90
        world = (
            item.local_size_mm[1] if rotated else item.local_size_mm[0],
            item.local_size_mm[0] if rotated else item.local_size_mm[1],
            item.local_size_mm[2],
        )
        placements.append(
            Free3DPlacement(
                participant_id=item.participant_id,
                role=item.role,
                name=item.name,
                origin_mm=(
                    _round_mm(
                        problem.box_clearance_mm
                        + proposed.x / problem.scale_per_mm
                    ),
                    _round_mm(
                        problem.box_clearance_mm
                        + proposed.y / problem.scale_per_mm
                    ),
                    0.0,
                ),
                world_size_mm=world,
                local_size_mm=item.local_size_mm,
                rotation_deg_z=proposed.rotation_deg_z,
                supporting_ids=(),
                support_coverage_ratio=1.0,
            )
        )
    strategy = SolverStrategy(
        str(candidate["candidate_id"]), str(candidate["version"])
    )
    budget = SolverBudget(
        str(candidate["family"]),
        "external-benchmark",
        tuple(sorted(limits.to_dict().items())),
    )
    certified, rejections = certify_minimal_free_3d_plan(
        problem.prepared,
        strategy=strategy,
        budget=budget,
        candidate_id=f"external-{candidate['candidate_id']}-{problem.case_id}",
        placements=tuple(sorted(placements, key=lambda item: item.participant_id)),
        empty_spaces=(),
        search_telemetry={
            "external_engine_status": output.engine_status,
            "external_solve_ms": output.solve_ms,
            "worker_metrics": dict(output.metrics),
        },
        search_provenance={
            "artifact_bundle_digest": receipt["bundle_digest"],
            "external_floor_problem_digest": problem.problem_digest,
            "external_worker_output_digest": output.output_digest,
            "model": EXTERNAL_FLOOR_MODEL_SCHEMA_V1,
            "stop_reason": "external_candidate_common_recertification",
        },
    )
    if certified is None:
        report = _report_from_worker(
            problem,
            candidate,
            receipt,
            limits,
            worker_run,
            worker_output=output,
            status=STATUS_CERTIFICATE_REJECTED,
            stop_reason="fresh_bgig_recertification_rejected",
            recertification={
                "attempted": True,
                "certified": False,
                "candidate_digest": None,
                "schema_version": None,
                "rejection_codes": list(rejections),
            },
            solution=None,
        )
        return ExternalAdapterExecution(report, None)
    certificate = certified.certificate
    plan = certified.plan
    solution = {
        "candidate_digest": certificate.candidate_digest,
        "certificate_schema_version": certificate.schema_version,
        "placement_count": len(placements),
        "placement_digest": certified.placement_digest,
        "plan_digest": plan.get("plan_digest"),
        "metrics": deepcopy(
            _mapping_or_empty(
                _mapping_or_empty(plan.get("minimal_layout")).get("metrics")
            )
        ),
        "rotation_count": sum(
            1 for item in placements if item.rotation_deg_z == 90
        ),
    }
    report = _report_from_worker(
        problem,
        candidate,
        receipt,
        limits,
        worker_run,
        worker_output=output,
        status=STATUS_SOLUTION_FOUND,
        stop_reason="fresh_bgig_recertification_accepted",
        recertification={
            "attempted": True,
            "certified": certificate.certified,
            "candidate_digest": certificate.candidate_digest,
            "schema_version": certificate.schema_version,
            "rejection_codes": list(certificate.rejection_codes),
        },
        solution=solution,
    )
    return ExternalAdapterExecution(report, deepcopy(plan))


def _execute_worker(
    problem: ExternalFloorProblem,
    runtime: ExternalSolverRuntime,
    limits: ExternalSolverLimits,
) -> dict[str, object]:
    scratch_root = Path(runtime.scratch_root).resolve()
    scratch_root.mkdir(parents=True, exist_ok=True)
    input_payload = _worker_input(problem, limits)
    input_digest = sha256(input_payload.encode("utf-8")).hexdigest()
    run_key = (
        f"{_safe_name(problem.case_id)}-{problem.problem_digest[:12]}-"
        f"{runtime.worker_digest[:12]}-{input_digest[:12]}"
    )
    run_dir = scratch_root / _safe_name(runtime.candidate_id) / run_key
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = run_dir / "input.tsv"
    output_path = run_dir / "output.tsv"
    metadata_path = run_dir / "run.json"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    if input_path.exists():
        if input_path.read_text(encoding="utf-8") != input_payload:
            raise ExternalSolverAdapterError(
                "Existing external worker input checkpoint differs."
            )
    else:
        input_path.write_text(input_payload, encoding="utf-8")
    if output_path.exists() or metadata_path.exists():
        if not metadata_path.is_file():
            return {
                "execution_status": "incomplete_checkpoint",
                "output_path": str(output_path),
                "checkpoint_reused": False,
            }
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        supplied_digest = metadata.pop("metadata_digest", None)
        expected_output_digest = metadata.get("output_digest")
        output_binding_valid = (
            (
                expected_output_digest is None
                and not output_path.exists()
            )
            or (
                _is_digest(expected_output_digest)
                and output_path.is_file()
                and expected_output_digest == _sha256_path(output_path)
            )
        )
        if (
            not _is_digest(supplied_digest)
            or canonical_digest(metadata) != supplied_digest
            or metadata.get("input_digest") != input_digest
            or metadata.get("worker_digest") != runtime.worker_digest
            or not output_binding_valid
        ):
            return {
                "execution_status": "invalid_checkpoint",
                "output_path": str(output_path),
                "checkpoint_reused": False,
            }
        metadata["metadata_digest"] = supplied_digest
        metadata["output_path"] = str(output_path)
        metadata["checkpoint_reused"] = True
        return metadata
    environment = dict(os.environ)
    for key in (
        "ALL_PROXY",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "all_proxy",
        "http_proxy",
        "https_proxy",
    ):
        environment.pop(key, None)
    environment.update(
        {
            "NO_PROXY": "*",
            "PIP_NO_INDEX": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    environment.update(dict(runtime.environment))
    started = perf_counter()
    peak_bytes = 0
    cpu_seconds = 0.0
    termination_reason: str | None = None
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            [*runtime.command, str(input_path), str(output_path)],
            cwd=str(run_dir),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            shell=False,
        )
        while process.poll() is None:
            elapsed = perf_counter() - started
            current_peak, current_cpu = _process_metrics(process.pid)
            peak_bytes = max(peak_bytes, current_peak or 0)
            cpu_seconds = max(cpu_seconds, current_cpu or 0.0)
            if peak_bytes > limits.memory_mebibytes * 1024 * 1024:
                termination_reason = "memory_limit_exceeded"
                process.terminate()
                break
            if elapsed > limits.wall_seconds:
                termination_reason = "wall_time_limit_exceeded"
                process.terminate()
                break
            sleep(0.02)
        if termination_reason is not None:
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
        exit_code = process.wait()
    total_wall_seconds = perf_counter() - started
    if termination_reason is not None:
        execution_status = termination_reason
    elif exit_code != 0:
        execution_status = "worker_exit_nonzero"
    elif not output_path.is_file():
        execution_status = "worker_output_missing"
    else:
        execution_status = "completed"
    output_digest = _sha256_path(output_path) if output_path.is_file() else None
    metadata: dict[str, object] = {
        "schema_version": "bgig.external_worker_run_checkpoint.v1",
        "candidate_id": runtime.candidate_id,
        "execution_status": execution_status,
        "exit_code": exit_code,
        "input_digest": input_digest,
        "output_digest": output_digest,
        "worker_digest": runtime.worker_digest,
        "total_wall_seconds": round(total_wall_seconds, 6),
        "cpu_seconds": round(cpu_seconds, 6),
        "peak_working_set_bytes": peak_bytes or None,
    }
    metadata["metadata_digest"] = canonical_digest(metadata)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    metadata["output_path"] = str(output_path)
    metadata["checkpoint_reused"] = False
    return metadata


def _parse_worker_output(
    path: Path, problem: ExternalFloorProblem
) -> _WorkerOutput:
    raw = path.read_text(encoding="utf-8")
    rows = [line.split("\t") for line in raw.splitlines() if line]
    if (
        len(rows) < 2
        or rows[0] != [
            EXTERNAL_WORKER_OUTPUT_SCHEMA_V1,
            EXTERNAL_WORKER_PROTOCOL_VERSION,
        ]
        or len(rows[1]) != 4
        or rows[1][0] != "RESULT"
        or rows[1][1] not in {"feasible", "infeasible", "unknown"}
    ):
        raise ExternalSolverAdapterError(
            "Unsupported external worker output schema or status."
        )
    raw_status = rows[1][1]
    solve_ms = float(rows[1][2])
    engine_status = _decode_id(rows[1][3])
    placements: list[_WorkerPlacement] = []
    metrics: list[tuple[str, str]] = []
    for row in rows[2:]:
        if row[0] == "PLACEMENT" and len(row) == 5:
            placements.append(
                _WorkerPlacement(
                    _decode_id(row[1]),
                    int(row[2]),
                    int(row[3]),
                    int(row[4]),
                )
            )
        elif row[0] == "METRIC" and len(row) == 3:
            metrics.append((row[1], row[2]))
        else:
            raise ExternalSolverAdapterError(
                "External worker output row is invalid."
            )
    if raw_status == "feasible":
        _validate_worker_placements(problem, placements)
    elif placements:
        raise ExternalSolverAdapterError(
            "External worker emitted placements without a feasible status."
        )
    return _WorkerOutput(
        raw_status,
        engine_status,
        solve_ms,
        tuple(placements),
        tuple(metrics),
        sha256(raw.encode("utf-8")).hexdigest(),
    )


def _validate_worker_placements(
    problem: ExternalFloorProblem,
    placements: Sequence[_WorkerPlacement],
) -> None:
    item_by_id = {item.participant_id: item for item in problem.items}
    if (
        len(placements) != len(problem.items)
        or {item.participant_id for item in placements} != set(item_by_id)
    ):
        raise ExternalSolverAdapterError(
            "External worker placement set is incomplete."
        )
    rectangles = []
    for placement in placements:
        item = item_by_id[placement.participant_id]
        if placement.rotation_deg_z not in ({0, 90} if problem.rotation_allowed else {0}):
            raise ExternalSolverAdapterError(
                "External worker rotation violates the case policy."
            )
        width, height = (
            (item.packed_height, item.packed_width)
            if placement.rotation_deg_z == 90
            else (item.packed_width, item.packed_height)
        )
        if (
            placement.x < 0
            or placement.y < 0
            or placement.x + width > problem.bin_width
            or placement.y + height > problem.bin_height
        ):
            raise ExternalSolverAdapterError(
                "External worker placement is outside the floor bounds."
            )
        rectangles.append(
            (placement.participant_id, placement.x, placement.y, width, height)
        )
    for first_index, first in enumerate(rectangles):
        for second in rectangles[first_index + 1 :]:
            separated = (
                first[1] + first[3] <= second[1]
                or second[1] + second[3] <= first[1]
                or first[2] + first[4] <= second[2]
                or second[2] + second[4] <= first[2]
            )
            if not separated:
                raise ExternalSolverAdapterError(
                    "External worker placements overlap."
                )


def _worker_input(
    problem: ExternalFloorProblem, limits: ExternalSolverLimits
) -> str:
    rows = [
        (
            EXTERNAL_WORKER_INPUT_SCHEMA_V1,
            EXTERNAL_WORKER_PROTOCOL_VERSION,
        ),
        ("BIN", str(problem.bin_width), str(problem.bin_height)),
        (
            "LIMIT",
            str(max(1, int(float(limits.wall_seconds) * 900.0))),
            str(limits.seed),
            str(limits.threads),
        ),
        ("ROTATE", "1" if problem.rotation_allowed else "0"),
    ]
    rows.extend(
        (
            "ITEM",
            _encode_id(item.participant_id),
            str(item.packed_width),
            str(item.packed_height),
        )
        for item in sorted(problem.items, key=lambda value: value.participant_id)
    )
    return "\n".join("\t".join(row) for row in rows) + "\n"


def _report_without_worker(
    case: object,
    candidate: Mapping[str, object],
    receipt: Mapping[str, object],
    limits: ExternalSolverLimits,
    *,
    status: str,
    reasons: Sequence[str],
) -> dict[str, object]:
    value = dict(case) if isinstance(case, Mapping) else {}
    report: dict[str, object] = {
        "schema_version": EXTERNAL_ADAPTER_RESULT_SCHEMA_V2,
        "candidate": _candidate_report(candidate, receipt),
        "case": {
            "case_id": str(value.get("case_id", "")),
            "family": str(value.get("family", "")),
            "project_digest": str(value.get("project_digest", "")),
            "split": str(value.get("split", "")),
        },
        "limits": limits.to_dict(),
        "model": None,
        "raw_status": None,
        "status": status,
        "stop_reason": reasons[0] if reasons else "not_reported",
        "unsupported_constraints": list(reasons) if status == STATUS_UNSUPPORTED else [],
        "errors": list(reasons) if status == STATUS_INVALID_INPUT else [],
        "timing": None,
        "resources": None,
        "recertification": _not_attempted_certificate(),
        "solution": None,
        "invariants": _report_invariants(worker_invocation_count=0),
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _report_from_worker(
    problem: ExternalFloorProblem,
    candidate: Mapping[str, object],
    receipt: Mapping[str, object],
    limits: ExternalSolverLimits,
    worker_run: Mapping[str, object],
    *,
    worker_output: _WorkerOutput | None,
    status: str,
    stop_reason: str,
    recertification: Mapping[str, object],
    solution: Mapping[str, object] | None,
) -> dict[str, object]:
    solve_seconds = (
        worker_output.solve_ms / 1000.0 if worker_output is not None else None
    )
    total_seconds = worker_run.get("total_wall_seconds")
    report: dict[str, object] = {
        "schema_version": EXTERNAL_ADAPTER_RESULT_SCHEMA_V2,
        "candidate": _candidate_report(candidate, receipt),
        "case": {
            "case_id": problem.case_id,
            "family": problem.family,
            "project_digest": problem.project_digest,
            "split": problem.split,
        },
        "limits": limits.to_dict(),
        "model": {
            "schema_version": EXTERNAL_FLOOR_MODEL_SCHEMA_V1,
            "problem_digest": problem.problem_digest,
            "scale_per_mm": problem.scale_per_mm,
            "item_count": len(problem.items),
            "constraints_applied": list(problem.constraints),
            "complete_for_infeasibility": problem.complete_for_infeasibility,
        },
        "raw_status": (
            {
                "normalized_by_worker": worker_output.raw_status,
                "engine_status": worker_output.engine_status,
                "metrics": dict(worker_output.metrics),
                "output_digest": worker_output.output_digest,
            }
            if worker_output is not None
            else None
        ),
        "status": status,
        "stop_reason": stop_reason,
        "unsupported_constraints": [],
        "errors": (
            []
            if status != STATUS_EXTERNAL_ERROR
            else [str(worker_run.get("execution_status"))]
        ),
        "timing": {
            "checkpoint_reused": bool(worker_run.get("checkpoint_reused")),
            "engine_solve_seconds": (
                round(solve_seconds, 6) if solve_seconds is not None else None
            ),
            "startup_and_adapter_seconds": (
                round(max(0.0, float(total_seconds) - solve_seconds), 6)
                if solve_seconds is not None and total_seconds is not None
                else None
            ),
            "time_to_first_certifiable_seconds": (
                float(total_seconds) if status == STATUS_SOLUTION_FOUND else None
            ),
            "total_wall_seconds": total_seconds,
        },
        "resources": {
            "cpu_seconds": worker_run.get("cpu_seconds"),
            "peak_working_set_bytes": worker_run.get("peak_working_set_bytes"),
            "threads_requested": limits.threads,
        },
        "recertification": deepcopy(dict(recertification)),
        "solution": deepcopy(dict(solution)) if solution is not None else None,
        "invariants": _report_invariants(worker_invocation_count=1),
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _candidate_report(
    candidate: Mapping[str, object],
    receipt: Mapping[str, object],
) -> dict[str, object]:
    return {
        "candidate_id": candidate["candidate_id"],
        "family": candidate["family"],
        "version": candidate["version"],
        "source_url": candidate["source_url"],
        "license": candidate["license"],
        "product_gate": candidate["product_gate"],
        "exact_for_floor_model": candidate["exact_for_floor_model"],
        "artifact_lock_digest": receipt["lock_digest"],
        "artifact_bundle_digest": receipt["bundle_digest"],
        "artifact_count": receipt["artifact_count"],
        "bundle_byte_count": receipt["bundle_byte_count"],
        "worker_protocol": (
            f"{EXTERNAL_WORKER_INPUT_SCHEMA_V1}/"
            f"{EXTERNAL_WORKER_PROTOCOL_VERSION}"
        ),
    }


def _report_invariants(*, worker_invocation_count: int) -> dict[str, object]:
    return {
        "external_worker_invocation_count": worker_invocation_count,
        "fusion_runtime_invocation_count": 0,
        "holdout_payload_consumed": False,
        "network_service_invocation_count": 0,
        "product_solver_routing_changed": False,
        "solution_requires_fresh_bgig_certificate": True,
        "t0_t1_only": True,
    }


def _not_attempted_certificate() -> dict[str, object]:
    return {
        "attempted": False,
        "candidate_digest": None,
        "certified": False,
        "rejection_codes": [],
        "schema_version": None,
    }


def _build_control_project(
    case_id: str,
    box_size_mm: tuple[float, float, float],
    item_size_mm: tuple[float, float, float],
    item_count: int,
) -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = f"P64-L07C {case_id}"
    project["box"] = {
        "inner_dimensions_mm": {
            "x": box_size_mm[0],
            "y": box_size_mm[1],
            "z": box_size_mm[2] + 2.0,
        },
        "usable_height_mm": box_size_mm[2],
        "lid_clearance_mm": 2.0,
    }
    project["layout"].update(
        {
            "layout_clearance_mm": 0.0,
            "container_z_clearance_mm": 0.0,
            "container_box_xy_clearance_mm": 0.0,
            "default_content_clearance_mm": 0.0,
        }
    )
    groups = []
    contents = []
    for index in range(item_count):
        group_id = f"control-{index + 1}"
        groups.append(
            {
                "id": group_id,
                "name": f"Control {index + 1}",
                "wall_thickness_mm": 1.0,
                "floor_thickness_mm": 1.0,
            }
        )
        contents.append(
            {
                "id": f"content-{index + 1}",
                "name": f"Content {index + 1}",
                "shape_kind": "custom",
                "dimensions_mm": {
                    "x": item_size_mm[0] - 2.0,
                    "y": item_size_mm[1] - 2.0,
                    "z": item_size_mm[2] - 1.0,
                },
                "quantity": 1,
                "container_group_id": group_id,
                "content_clearance_mm": 0.0,
                "measurement_confidence": "exact",
            }
        )
    project["container_groups"] = groups
    project["contents"] = contents
    return normalize_project_draft(project).project


def _uniform_clearances(
    problem: Free3DPreparedProblem,
    box_clearance: float,
    between_clearance: float,
) -> bool:
    for participant in problem.participants:
        policy = _mapping_or_empty(
            participant.get("external_clearance_effective_v1")
        )
        between = _mapping_or_empty(policy.get("between_mm"))
        box = _mapping_or_empty(policy.get("box_per_side_xy_mm"))
        if between and (
            abs(float(between.get("x", between_clearance)) - between_clearance)
            > _EPSILON_MM
            or abs(float(between.get("y", between_clearance)) - between_clearance)
            > _EPSILON_MM
        ):
            return False
        if box and (
            abs(float(box.get("x", box_clearance)) - box_clearance)
            > _EPSILON_MM
            or abs(float(box.get("y", box_clearance)) - box_clearance)
            > _EPSILON_MM
        ):
            return False
    return True


def _scaled(value_mm: float) -> int:
    scaled = int(round(float(value_mm) * _SCALE_PER_MM))
    if (
        scaled <= 0
        or abs(scaled / _SCALE_PER_MM - float(value_mm)) > _EPSILON_MM
    ):
        raise ExternalSolverAdapterError(
            "dimension_not_representable_on_0_001_mm_grid"
        )
    return scaled


def _process_metrics(process_id: int) -> tuple[int | None, float | None]:
    if os.name != "nt":
        return None, None
    try:
        return _windows_process_metrics(process_id)
    except (AttributeError, OSError, ValueError):
        return None, None


def _windows_process_metrics(process_id: int) -> tuple[int | None, float | None]:
    class ProcessMemoryCountersEx(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    class FileTime(ctypes.Structure):
        _fields_ = [
            ("low", ctypes.c_ulong),
            ("high", ctypes.c_ulong),
        ]

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    handle = kernel32.OpenProcess(0x1000 | 0x0400, False, process_id)
    if not handle:
        return None, None
    try:
        memory = ProcessMemoryCountersEx()
        memory.cb = ctypes.sizeof(memory)
        peak: int | None = None
        if psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(memory), ctypes.sizeof(memory)
        ):
            peak = int(memory.PeakWorkingSetSize)
        creation = FileTime()
        exit_time = FileTime()
        kernel = FileTime()
        user = FileTime()
        cpu: float | None = None
        if kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ):
            kernel_ticks = (kernel.high << 32) + kernel.low
            user_ticks = (user.high << 32) + user.low
            cpu = (kernel_ticks + user_ticks) / 10_000_000.0
        return peak, cpu
    finally:
        kernel32.CloseHandle(handle)


def _mapping_or_empty(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _safe_name(value: str) -> str:
    result = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in value
    )
    return result[:128] or "unnamed"


def _encode_id(value: str) -> str:
    return urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_id(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8")


def _sha256_path(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round_mm(value: float) -> float:
    return round(float(value), 6)


def _is_digest(value: object) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
