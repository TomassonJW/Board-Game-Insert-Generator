"""Adaptateurs fideles de solvage 3D externe pour P64-L08E.

Le protocole transporte le probleme complet en JSON. Aucun temoin positif du
corpus n'est transmis aux workers. Chaque sortie est recertifiee par ce module
avant de pouvoir compter comme plan BGIG.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from time import perf_counter, sleep
from typing import Mapping, Sequence

from board_game_insert_generator.external_solver_adapters import (
    ExternalSolverLimits,
    ExternalSolverRuntime,
    _process_metrics,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


REAL_3D_ADAPTER_REPORT_SCHEMA_V1 = "bgig.real_3d_adapter_report.v1"
REAL_3D_WORKER_INPUT_SCHEMA_V1 = "bgig.real_3d_worker_input.v1"
REAL_3D_WORKER_OUTPUT_SCHEMA_V1 = "bgig.real_3d_worker_output.v1"

STATUS_SOLUTION_FOUND = "solution_found"
STATUS_INFEASIBLE_PROVEN = "infeasible_proven"
STATUS_BOUNDED_UNKNOWN = "bounded_unknown"
STATUS_UNSUPPORTED = "unsupported"
STATUS_CERTIFICATE_REJECTED = "certificate_rejected"
STATUS_EXTERNAL_ERROR = "external_error"

_ALL_RULES = frozenset(
    {
        "xyz",
        "stacking",
        "heterogeneous_layers",
        "support",
        "multi_support",
        "lower_reservation",
        "upper_reservation",
        "top_down_access",
        "disjoint_regions",
        "near_saturation",
        "p45_variant_front",
        "rotations",
        "high_container_cardinality",
        "high_content_cardinality",
        "reviewed_anonymized_source",
    }
)

CANDIDATE_FIDELITY = {
    "ortools_cp_sat": {
        "family": "constraint_programming_sat_hybrid",
        "rules": _ALL_RULES,
        "model": "integer_xyz_pairwise_disjunction_and_explicit_support",
    },
    "scip": {
        "family": "constraint_integer_programming",
        "rules": _ALL_RULES,
        "model": "integer_xyz_big_m_disjunction_and_explicit_support",
    },
    "packingsolver_box": {
        "family": "specialized_3d_tree_search",
        "rules": frozenset(
            {
                "xyz",
                "stacking",
                "heterogeneous_layers",
                "rotations",
                "high_container_cardinality",
                "high_content_cardinality",
            }
        ),
        "model": "native_packingsolver_box_tree_search",
    },
    "laff": {
        "family": "specialized_level_heuristic",
        "rules": frozenset(
            {
                "xyz",
                "stacking",
                "heterogeneous_layers",
                "rotations",
                "high_container_cardinality",
                "high_content_cardinality",
            }
        ),
        "model": "native_laff_3d_levels",
    },
}


class Real3DAdapterError(ValueError):
    """Entree, sortie ou certificat 3D externe invalide."""


def build_real_3d_exact_controls() -> tuple[dict[str, object], ...]:
    """Petits controles sans temoin transmis aux moteurs."""

    controls = [
        _control(
            "stacking-feasible",
            [6, 6, 8],
            [_participant("a", [[6, 6, 3]]), _participant("b", [[6, 6, 5]])],
            ["xyz", "stacking", "heterogeneous_layers"],
            "feasible",
        ),
        _control(
            "stacking-infeasible",
            [6, 6, 8],
            [_participant("a", [[6, 6, 4]]), _participant("b", [[6, 6, 5]])],
            ["xyz", "stacking", "heterogeneous_layers"],
            "infeasible",
        ),
        _control(
            "multi-support-feasible",
            [10, 10, 8],
            [
                _participant("left", [[5, 10, 4]]),
                _participant("right", [[5, 10, 4]]),
                _participant("load", [[10, 10, 4]], minimum_support_count=2),
            ],
            ["xyz", "stacking", "support", "multi_support"],
            "feasible",
        ),
        _control(
            "reservation-feasible",
            [18, 6, 8],
            [
                _participant("a", [[6, 6, 4]]),
                _participant("b", [[6, 6, 4]]),
                _participant("c", [[6, 6, 4]]),
            ],
            ["xyz", "stacking", "support", "lower_reservation", "upper_reservation"],
            "feasible",
            reservations=[
                {
                    "reservation_id": "blocked-lower-left",
                    "zone": "lower",
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "size": [6, 6, 4],
                },
                {
                    "reservation_id": "blocked-upper-right",
                    "zone": "upper",
                    "x": 12,
                    "y": 0,
                    "z": 4,
                    "size": [6, 6, 4],
                },
            ],
        ),
        _control(
            "fragmentation-feasible",
            [26, 14, 4],
            [_participant("a", [[10, 10, 4]]), _participant("b", [[10, 10, 4]])],
            ["xyz", "disjoint_regions", "near_saturation"],
            "feasible",
            fragment_cell=[10, 10, 4],
            fragment_gap=2,
        ),
        _control(
            "variant-rotation-feasible",
            [8, 6, 4],
            [_participant("item", [[9, 7, 4], [6, 8, 4]])],
            ["xyz", "p45_variant_front", "rotations"],
            "feasible",
        ),
    ]
    return tuple(controls)


def prepare_real_3d_problem(
    problem: Mapping[str, object], candidate_id: str
) -> tuple[dict[str, object] | None, tuple[str, ...]]:
    """Valide l'entree et rend explicite toute regle non representee."""

    if candidate_id not in CANDIDATE_FIDELITY:
        return None, ("unknown_candidate",)
    payload = deepcopy(dict(problem))
    supplied_problem_digest = payload.pop("problem_digest", None)
    try:
        world = payload["world_mm"]
        participants = payload["participants"]
        active = set(payload["active_constraints"])
    except (KeyError, TypeError):
        return None, ("incomplete_real_3d_problem",)
    if (
        not isinstance(world, list)
        or len(world) != 3
        or any(not isinstance(value, int) or value <= 0 for value in world)
        or not isinstance(participants, list)
        or not participants
        or not active <= _ALL_RULES
    ):
        return None, ("invalid_real_3d_problem",)
    unsupported = sorted(active - CANDIDATE_FIDELITY[candidate_id]["rules"])
    if candidate_id in {"laff", "packingsolver_box"}:
        if payload.get("reservation_volumes"):
            unsupported.append("reservation_volumes")
        if any(len(item.get("variants", [])) != 1 for item in participants):
            unsupported.append("variant_choice")
        if any(int(item.get("minimum_support_count", 1)) > 1 for item in participants):
            unsupported.append("multi_support_count")
        if payload.get("access_policy") != "unconstrained":
            unsupported.append("access_policy")
        if payload.get("project_mode") != "cold":
            unsupported.append("incremental_replay")
    if unsupported:
        return None, tuple(sorted(set(unsupported)))
    for participant in participants:
        if not isinstance(participant, dict) or not participant.get("variants"):
            return None, ("participant_without_variant",)
    computed_problem_digest = canonical_digest(payload)
    if supplied_problem_digest is not None and supplied_problem_digest != computed_problem_digest:
        return None, ("problem_digest_mismatch",)
    payload["problem_digest"] = computed_problem_digest
    return payload, ()


def run_real_3d_adapter(
    problem: Mapping[str, object],
    *,
    candidate_id: str,
    runtime: ExternalSolverRuntime,
    limits: ExternalSolverLimits,
    artifact_receipt: Mapping[str, object],
    exact_control: bool = False,
) -> dict[str, object]:
    """Execute un worker externe isole puis recertifie sa sortie en 3D."""

    prepared, unsupported = prepare_real_3d_problem(problem, candidate_id)
    if prepared is None:
        return _report(
            candidate_id,
            problem,
            limits,
            artifact_receipt,
            status=STATUS_UNSUPPORTED,
            stop_reason="unsupported_semantics",
            unsupported=unsupported,
            worker_invocation_count=0,
        )
    if runtime.candidate_id != candidate_id:
        raise Real3DAdapterError("Runtime candidate mismatch.")
    worker_input = {
        "schema_version": REAL_3D_WORKER_INPUT_SCHEMA_V1,
        "candidate_id": candidate_id,
        "problem": prepared,
        "limits": asdict(limits),
        "exact_control": exact_control,
    }
    worker_input["input_digest"] = canonical_digest(worker_input)
    execution = _execute_json_worker(worker_input, runtime, limits)
    if execution["execution_status"] != "completed":
        return _report(
            candidate_id,
            prepared,
            limits,
            artifact_receipt,
            status=STATUS_BOUNDED_UNKNOWN,
            stop_reason=str(execution["execution_status"]),
            worker_invocation_count=1,
            execution=execution,
        )
    try:
        output = json.loads(Path(execution["output_path"]).read_text(encoding="utf-8"))
        _validate_worker_output(output, worker_input["input_digest"], candidate_id)
    except (OSError, json.JSONDecodeError, Real3DAdapterError) as exc:
        return _report(
            candidate_id,
            prepared,
            limits,
            artifact_receipt,
            status=STATUS_EXTERNAL_ERROR,
            stop_reason=f"invalid_worker_output:{type(exc).__name__}",
            worker_invocation_count=1,
            execution=execution,
        )
    raw_status = output["status"]
    if raw_status == "feasible":
        placements = output.get("placements", [])
        errors = recertify_real_3d_solution(prepared, placements)
        if errors:
            return _report(
                candidate_id,
                prepared,
                limits,
                artifact_receipt,
                status=STATUS_CERTIFICATE_REJECTED,
                stop_reason="fresh_bgig_recertification_rejected",
                worker_invocation_count=1,
                execution=execution,
                engine=output,
                certification_errors=errors,
            )
        return _report(
            candidate_id,
            prepared,
            limits,
            artifact_receipt,
            status=STATUS_SOLUTION_FOUND,
            stop_reason="fresh_bgig_recertification_accepted",
            worker_invocation_count=1,
            execution=execution,
            engine=output,
            solution={"placements": deepcopy(placements)},
        )
    if raw_status == "infeasible" and exact_control and output.get("proof_status") == "complete":
        status = STATUS_INFEASIBLE_PROVEN
        reason = "complete_external_search"
    else:
        status = STATUS_BOUNDED_UNKNOWN
        reason = "no_certified_plan_within_budget"
    return _report(
        candidate_id,
        prepared,
        limits,
        artifact_receipt,
        status=status,
        stop_reason=reason,
        worker_invocation_count=1,
        execution=execution,
        engine=output,
    )


def recertify_real_3d_solution(
    problem: Mapping[str, object], placements: object
) -> tuple[str, ...]:
    """Revalide completement un monde 3D sans confiance dans le worker."""

    if not isinstance(placements, list):
        return ("placements_not_a_list",)
    required_fields = {
        "participant_id",
        "x",
        "y",
        "z",
        "size",
        "orientation",
        "selected_variant_id",
        "assigned_content_count",
        "support_ids",
        "removal_rank",
    }
    if any(
        not isinstance(item, dict)
        or not required_fields <= set(item)
        or not isinstance(item.get("size"), list)
        or len(item["size"]) != 3
        or any(not isinstance(value, int) or value <= 0 for value in item["size"])
        for item in placements
    ):
        return ("invalid_placement_record",)
    participants = {str(item["participant_id"]): item for item in problem["participants"]}
    by_id = {str(item.get("participant_id")): item for item in placements if isinstance(item, dict)}
    errors: list[str] = []
    if set(by_id) != set(participants) or len(by_id) != len(placements):
        errors.append("participant_set_mismatch")
        return tuple(errors)
    world = problem["world_mm"]
    ordered = [by_id[key] for key in sorted(by_id)]
    for index, item in enumerate(ordered):
        participant = participants[str(item["participant_id"])]
        variant = next(
            (
                value
                for value in participant["variants"]
                if value["variant_id"] == item.get("selected_variant_id")
            ),
            None,
        )
        if variant is None or item.get("orientation") not in variant["allowed_rotations"]:
            errors.append(f"variant_or_rotation:{item['participant_id']}")
            continue
        expected_size = list(variant["size"])
        if item["orientation"] == "yxz":
            expected_size[0], expected_size[1] = expected_size[1], expected_size[0]
        if item.get("size") != expected_size:
            errors.append(f"size:{item['participant_id']}")
        for axis, size_index in (("x", 0), ("y", 1), ("z", 2)):
            value = item.get(axis)
            if (
                not isinstance(value, int)
                or value < 0
                or value + expected_size[size_index] > world[size_index]
            ):
                errors.append(f"bounds:{item['participant_id']}:{axis}")
        if item.get("assigned_content_count") != participant["assigned_content_count"]:
            errors.append(f"content_assignment:{item['participant_id']}")
        for other in ordered[index + 1 :]:
            if _overlap_3d(item, other):
                errors.append(f"collision:{item['participant_id']}:{other['participant_id']}")
    for reservation in problem.get("reservation_volumes", []):
        for item in ordered:
            if _overlap_3d(item, reservation):
                errors.append(
                    f"reservation:{item['participant_id']}:{reservation['reservation_id']}"
                )
    for item in ordered:
        support_ids = item.get("support_ids")
        if not isinstance(support_ids, list):
            errors.append(f"support_list:{item['participant_id']}")
            continue
        if item["z"] == 0:
            if support_ids:
                errors.append(f"ground_support:{item['participant_id']}")
            continue
        supports = []
        for support_id in support_ids:
            support = by_id.get(str(support_id))
            if support is None or support["z"] + support["size"][2] != item["z"]:
                errors.append(f"support_plane:{item['participant_id']}:{support_id}")
            else:
                supports.append(support)
        if len(supports) < int(participants[str(item["participant_id"])]["minimum_support_count"]):
            errors.append(f"support_count:{item['participant_id']}")
        required = item["size"][0] * item["size"][1]
        if _covered_area(item, supports) < required:
            errors.append(f"support_coverage:{item['participant_id']}")
    if "disjoint_regions" in problem.get("active_constraints", []):
        cell = problem["fragment_cell_mm"]
        stride_x = cell[0] + int(problem["fragment_gap_mm"])
        stride_y = cell[1] + int(problem["fragment_gap_mm"])
        for item in ordered:
            if item["x"] < 2 or item["y"] < 2:
                errors.append(f"fragment:{item['participant_id']}")
                continue
            cell_x = 2 + stride_x * ((item["x"] - 2) // stride_x)
            cell_y = 2 + stride_y * ((item["y"] - 2) // stride_y)
            if (
                item["x"] + item["size"][0] > cell_x + cell[0]
                or item["y"] + item["size"][1] > cell_y + cell[1]
            ):
                errors.append(f"fragment:{item['participant_id']}")
    if problem.get("access_policy") == "top_down":
        for lower in ordered:
            for upper in ordered:
                if (
                    upper["z"] >= lower["z"] + lower["size"][2]
                    and _overlap_xy(lower, upper)
                    and upper.get("removal_rank", 0) >= lower.get("removal_rank", 0)
                ):
                    errors.append(f"access:{lower['participant_id']}:{upper['participant_id']}")
    return tuple(sorted(set(errors)))


def _execute_json_worker(
    payload: Mapping[str, object],
    runtime: ExternalSolverRuntime,
    limits: ExternalSolverLimits,
) -> dict[str, object]:
    root = Path(runtime.scratch_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    input_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    input_digest = sha256(input_text.encode("utf-8")).hexdigest()
    run_key = f"{runtime.worker_digest[:12]}-{input_digest[:16]}"
    run_dir = root / runtime.candidate_id / run_key
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = run_dir / "input.json"
    output_path = run_dir / "output.json"
    input_path.write_text(input_text, encoding="utf-8")
    environment = dict(os.environ)
    for key in ("ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "http_proxy", "https_proxy"):
        environment.pop(key, None)
    environment.update({"NO_PROXY": "*", "PIP_NO_INDEX": "1", "PYTHONNOUSERSITE": "1"})
    environment.update(dict(runtime.environment))
    started = perf_counter()
    peak = 0
    cpu = 0.0
    termination = None
    process = subprocess.Popen(
        [*runtime.command, str(input_path), str(output_path)],
        cwd=str(run_dir),
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
    )
    while process.poll() is None:
        elapsed = perf_counter() - started
        current_peak, current_cpu = _process_metrics(process.pid)
        peak = max(peak, current_peak or 0)
        cpu = max(cpu, current_cpu or 0.0)
        if peak > limits.memory_mebibytes * 1024 * 1024:
            termination = "memory_limit_exceeded"
            process.terminate()
            break
        if elapsed > limits.wall_seconds:
            termination = "wall_time_limit_exceeded"
            process.terminate()
            break
        sleep(0.02)
    if termination:
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
    exit_code = process.wait()
    elapsed = perf_counter() - started
    status = termination or (
        "worker_exit_nonzero"
        if exit_code
        else "completed"
        if output_path.is_file()
        else "worker_output_missing"
    )
    return {
        "execution_status": status,
        "exit_code": exit_code,
        "total_wall_seconds": round(elapsed, 6),
        "cpu_seconds": round(cpu, 6),
        "peak_working_set_bytes": peak or None,
        "input_digest": input_digest,
        "output_path": str(output_path),
    }


def _validate_worker_output(output: object, input_digest: str, candidate_id: str) -> None:
    if not isinstance(output, dict):
        raise Real3DAdapterError("Worker output is not an object.")
    supplied = output.pop("output_digest", None)
    if (
        output.get("schema_version") != REAL_3D_WORKER_OUTPUT_SCHEMA_V1
        or output.get("candidate_id") != candidate_id
        or output.get("input_digest") != input_digest
        or output.get("status") not in {"feasible", "infeasible", "unknown"}
        or not isinstance(supplied, str)
        or supplied != canonical_digest(output)
    ):
        raise Real3DAdapterError("Worker output binding is invalid.")
    output["output_digest"] = supplied


def _report(
    candidate_id: str,
    problem: Mapping[str, object],
    limits: ExternalSolverLimits,
    receipt: Mapping[str, object],
    *,
    status: str,
    stop_reason: str,
    worker_invocation_count: int,
    unsupported: Sequence[str] = (),
    execution: Mapping[str, object] | None = None,
    engine: Mapping[str, object] | None = None,
    solution: Mapping[str, object] | None = None,
    certification_errors: Sequence[str] = (),
) -> dict[str, object]:
    report = {
        "schema_version": REAL_3D_ADAPTER_REPORT_SCHEMA_V1,
        "candidate_id": candidate_id,
        "candidate_family": CANDIDATE_FIDELITY.get(candidate_id, {}).get("family"),
        "translation_model": CANDIDATE_FIDELITY.get(candidate_id, {}).get("model"),
        "problem_digest": problem.get("problem_digest") or canonical_digest(problem),
        "artifact_bundle_digest": receipt.get("bundle_digest"),
        "status": status,
        "stop_reason": stop_reason,
        "unsupported_constraints": list(unsupported),
        "worker_invocation_count": worker_invocation_count,
        "limits": asdict(limits),
        "execution": deepcopy(dict(execution or {})),
        "engine": deepcopy(dict(engine or {})),
        "solution": deepcopy(dict(solution or {})),
        "recertification": {
            "attempted": status in {STATUS_SOLUTION_FOUND, STATUS_CERTIFICATE_REJECTED},
            "certified": status == STATUS_SOLUTION_FOUND,
            "errors": list(certification_errors),
        },
        "invariants": {
            "semantic_projection": "none",
            "coordinates": "integer_xyz_mm",
            "network_required": False,
            "global_install_count": 0,
            "fresh_bgig_recertification_required": True,
        },
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _control(
    control_id: str,
    world: list[int],
    participants: list[dict[str, object]],
    active: list[str],
    expected: str,
    *,
    reservations: list[dict[str, object]] | None = None,
    fragment_cell: list[int] | None = None,
    fragment_gap: int = 0,
) -> dict[str, object]:
    problem = {
        "control_id": control_id,
        "world_mm": world,
        "participants": participants,
        "reservation_volumes": reservations or [],
        "fragment_cell_mm": fragment_cell or [world[0], world[1], world[2]],
        "fragment_gap_mm": fragment_gap,
        "access_policy": "unconstrained",
        "active_constraints": active,
        "project_mode": "cold",
        "expected": expected,
    }
    problem["problem_digest"] = canonical_digest(problem)
    return problem


def _participant(
    participant_id: str,
    sizes: list[list[int]],
    *,
    minimum_support_count: int = 1,
) -> dict[str, object]:
    return {
        "participant_id": participant_id,
        "variants": [
            {
                "variant_id": f"v{index}",
                "size": size,
                "allowed_rotations": ["xyz", "yxz"],
                "p45_certified": True,
            }
            for index, size in enumerate(sizes)
        ],
        "assigned_content_count": 1,
        "minimum_support_count": minimum_support_count,
        "support_coverage_ratio": 1.0,
    }


def _overlap_xy(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    return (
        left["x"] < right["x"] + right["size"][0]
        and right["x"] < left["x"] + left["size"][0]
        and left["y"] < right["y"] + right["size"][1]
        and right["y"] < left["y"] + left["size"][1]
    )


def _overlap_3d(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    return (
        _overlap_xy(left, right)
        and left["z"] < right["z"] + right["size"][2]
        and right["z"] < left["z"] + left["size"][2]
    )


def _covered_area(load: Mapping[str, object], supports: Sequence[Mapping[str, object]]) -> int:
    xs = {int(load["x"]), int(load["x"] + load["size"][0])}
    ys = {int(load["y"]), int(load["y"] + load["size"][1])}
    for support in supports:
        xs.update(
            (
                max(load["x"], support["x"]),
                min(load["x"] + load["size"][0], support["x"] + support["size"][0]),
            )
        )
        ys.update(
            (
                max(load["y"], support["y"]),
                min(load["y"] + load["size"][1], support["y"] + support["size"][1]),
            )
        )
    x_values = sorted(xs)
    y_values = sorted(ys)
    area = 0
    for x0, x1 in zip(x_values, x_values[1:]):
        for y0, y1 in zip(y_values, y_values[1:]):
            if (
                x1 > x0
                and y1 > y0
                and any(
                    s["x"] <= x0
                    and s["x"] + s["size"][0] >= x1
                    and s["y"] <= y0
                    and s["y"] + s["size"][1] >= y1
                    for s in supports
                )
            ):
                area += (x1 - x0) * (y1 - y0)
    return area
