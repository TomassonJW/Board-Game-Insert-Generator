"""Runner reprenable et atomique de la campagne P64-L06D.

Les solveurs restent dans les adapters offline. Ce module ordonne les cas,
écrit un résultat compact après chaque exécution et reprend sans relancer un
résultat déjà validé. Le holdout reste protégé par le contrat du corpus.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Callable, Mapping, Sequence

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import (
    _solve_minimal_layout_once,
    minimal_lane_specs,
    solve_minimal_layout,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_benchmark_adapters import (
    CURRENT_BGIG_ADAPTER_ID,
    STATUS_BOUNDED_UNKNOWN,
    STATUS_CERTIFICATE_REJECTED,
    STATUS_PROVEN_IMPOSSIBLE,
    STATUS_UNSUPPORTED,
    available_benchmark_adapters,
    recertify_minimal_layout_plan,
    run_benchmark_adapter,
)
from board_game_insert_generator.solver_benchmark_corpus import (
    materialize_benchmark_split,
    validate_solver_benchmark_manifest,
)
from board_game_insert_generator.solver_outcome import SOLUTION_FOUND


CAMPAIGN_CHECKPOINT_SCHEMA_V1 = "bgig.solver_benchmark_checkpoint.v1"
CAMPAIGN_CASE_RESULT_SCHEMA_V1 = "bgig.solver_benchmark_case_result.v1"
CAMPAIGN_SUMMARY_SCHEMA_V1 = "bgig.solver_benchmark_phase_summary.v1"
_ALLOWED_ADAPTERS = {item["adapter_id"] for item in available_benchmark_adapters()}
_DIAGNOSTIC_RELAXATIONS = {
    "relax_rotation_policy",
    "remove_top_reservations",
    "relax_rotation_and_reservations",
}
_LANE_HYPOTHESES = {
    "lane_center_quick_v1": (
        "historical_legacy_corner",
        "historical_bridge_edge",
        "variant_center_footprint",
    ),
    "lane_lowest_quick_v1": (
        "historical_legacy_corner",
        "historical_bridge_edge",
        "variant_lowest_height",
    ),
    "lane_interleave_quick_v1": (
        "historical_legacy_corner",
        "variant_corner_long_side",
        "variant_edge_interleave",
    ),
}
_ALLOWED_EXPERIMENTS = {
    "canonical",
    *_DIAGNOSTIC_RELAXATIONS,
    *_LANE_HYPOTHESES,
}


class SolverBenchmarkCampaignError(ValueError):
    """Configuration, checkpoint ou résultat de campagne incohérent."""


@dataclass(frozen=True)
class CampaignPhaseConfig:
    split: str
    adapter_ids: tuple[str, ...]
    base_sha: str
    branch: str
    max_case_executions: int
    case_ids: tuple[str, ...] = ()
    experiment_id: str = "canonical"

    def __post_init__(self) -> None:
        if self.split not in {"regression", "discovery", "tuning", "holdout"}:
            raise ValueError("Unsupported campaign split.")
        if not self.adapter_ids or len(set(self.adapter_ids)) != len(self.adapter_ids):
            raise ValueError("Campaign adapters must be a non-empty unique tuple.")
        unknown = set(self.adapter_ids) - _ALLOWED_ADAPTERS
        if unknown:
            raise ValueError(f"Unknown campaign adapters: {sorted(unknown)}.")
        if not _is_digest(self.base_sha):
            raise ValueError(
                "Campaign base_sha must be a 40- or 64-character Git object id."
            )
        if not self.branch:
            raise ValueError("Campaign branch is required.")
        if (
            isinstance(self.max_case_executions, bool)
            or not isinstance(self.max_case_executions, int)
            or self.max_case_executions <= 0
        ):
            raise ValueError("Campaign execution cap must be a positive integer.")
        if len(set(self.case_ids)) != len(self.case_ids):
            raise ValueError("Campaign case_ids must be unique.")
        if self.experiment_id not in _ALLOWED_EXPERIMENTS:
            raise ValueError("Unsupported campaign experiment.")
        if (
            self.experiment_id in _DIAGNOSTIC_RELAXATIONS
            and self.split != "discovery"
        ):
            raise ValueError("Diagnostic relaxations are discovery-only.")
        if (
            self.experiment_id in _LANE_HYPOTHESES
            and self.split not in {"discovery", "tuning", "holdout"}
        ):
            raise ValueError("Lane hypotheses require discovery, tuning or holdout.")

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter_ids": list(self.adapter_ids),
            "base_sha": self.base_sha,
            "branch": self.branch,
            "case_ids": list(self.case_ids),
            "experiment_id": self.experiment_id,
            "max_case_executions": self.max_case_executions,
            "split": self.split,
        }


@dataclass(frozen=True)
class CampaignPhaseExecution:
    checkpoint: dict[str, object]
    executed_now: int
    skipped_existing: int


def run_campaign_phase(
    manifest: object,
    config: CampaignPhaseConfig,
    output_directory: Path | str,
    *,
    holdout_selection: object | None = None,
) -> CampaignPhaseExecution:
    """Exécute une phase, checkpointée après chaque couple cas/adapter."""

    validated_manifest = validate_solver_benchmark_manifest(manifest)
    cases = materialize_benchmark_split(
        validated_manifest,
        config.split,
        holdout_selection=holdout_selection,
    )
    cases = [_apply_experiment(case, config.experiment_id) for case in cases]
    if config.case_ids:
        by_id = {str(case["case_id"]): case for case in cases}
        missing = [case_id for case_id in config.case_ids if case_id not in by_id]
        if missing:
            raise SolverBenchmarkCampaignError(
                "Unknown case ids for split: " + ", ".join(missing)
            )
        cases = [by_id[case_id] for case_id in config.case_ids]
    schedule = tuple(
        (case, adapter_id)
        for case in cases
        for adapter_id in config.adapter_ids
    )
    if len(schedule) > config.max_case_executions:
        raise SolverBenchmarkCampaignError(
            "Campaign schedule exceeds the explicit execution cap."
        )
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    results_directory = output / "results"
    results_directory.mkdir(parents=True, exist_ok=True)
    identity = _run_identity(validated_manifest, config, schedule, holdout_selection)
    checkpoint_path = output / "checkpoint.json"
    checkpoint = _load_or_create_checkpoint(
        checkpoint_path,
        identity,
        validated_manifest,
        config,
        len(schedule),
    )
    completed = {
        str(item["execution_key"]): dict(item)
        for item in _mapping_list(checkpoint.get("completed"), "checkpoint.completed")
    }
    executed_now = 0
    skipped_existing = 0
    for index, (case, adapter_id) in enumerate(schedule):
        execution_key = _execution_key(str(case["case_id"]), adapter_id)
        existing = completed.get(execution_key)
        if existing is not None and _completed_result_is_valid(output, existing):
            skipped_existing += 1
            continue
        if existing is not None:
            completed.pop(execution_key, None)
            checkpoint["completed"] = [completed[key] for key in sorted(completed)]
        if len(completed) >= config.max_case_executions:
            checkpoint["stop_reason"] = "execution_cap_reached"
            checkpoint["next_action"] = execution_key
            checkpoint["child_pid"] = None
            _finalize_checkpoint(checkpoint, checkpoint_path)
            raise SolverBenchmarkCampaignError(
                "Campaign execution cap reached before the schedule completed."
            )
        checkpoint["child_pid"] = None
        checkpoint["next_action"] = execution_key
        checkpoint["stop_reason"] = "running"
        _finalize_checkpoint(checkpoint, checkpoint_path)
        try:
            result = _execute_case(case, adapter_id)
        except Exception as error:
            checkpoint["child_pid"] = None
            checkpoint["stop_reason"] = f"case_failed:{type(error).__name__}"
            checkpoint["next_action"] = execution_key
            _finalize_checkpoint(checkpoint, checkpoint_path)
            raise
        relative_path = Path("results") / (
            _safe_component(str(case["case_id"]))
            + "--"
            + _safe_component(adapter_id)
            + ".json"
        )
        result_path = output / relative_path
        _write_json_atomic(result_path, result)
        record = {
            "adapter_id": adapter_id,
            "case_id": str(case["case_id"]),
            "execution_index": index,
            "execution_key": execution_key,
            "result_digest": result["result_digest"],
            "result_path": relative_path.as_posix(),
        }
        completed[execution_key] = record
        checkpoint["completed"] = [
            completed[key] for key in sorted(completed)
        ]
        checkpoint["last_completed"] = execution_key
        checkpoint["budget"] = {
            "consumed_case_executions": len(completed),
            "maximum_case_executions": config.max_case_executions,
            "remaining_case_executions": (
                config.max_case_executions - len(completed)
            ),
            "scheduled_case_executions": len(schedule),
        }
        checkpoint["child_pid"] = None
        checkpoint["next_action"] = (
            _execution_key(str(schedule[index + 1][0]["case_id"]), schedule[index + 1][1])
            if index + 1 < len(schedule)
            else "phase_summary"
        )
        checkpoint["stop_reason"] = "case_checkpointed"
        _finalize_checkpoint(checkpoint, checkpoint_path)
        executed_now += 1

    summary = build_campaign_phase_summary(
        output,
        manifest_digest=str(validated_manifest["manifest_digest"]),
        config=config,
    )
    _write_json_atomic(output / "summary.json", summary)
    checkpoint["summary_digest"] = summary["summary_digest"]
    checkpoint["summary_path"] = "summary.json"
    checkpoint["child_pid"] = None
    checkpoint["next_action"] = "phase_complete"
    checkpoint["stop_reason"] = "phase_complete"
    _finalize_checkpoint(checkpoint, checkpoint_path)
    return CampaignPhaseExecution(deepcopy(checkpoint), executed_now, skipped_existing)


def build_campaign_phase_summary(
    output_directory: Path | str,
    *,
    manifest_digest: str,
    config: CampaignPhaseConfig,
) -> dict[str, object]:
    """Reconstruit un résumé déterministe depuis les seuls résultats validés."""

    output = Path(output_directory)
    checkpoint = _read_json(output / "checkpoint.json")
    _validate_checkpoint(checkpoint)
    if str(checkpoint.get("run_id")) != _checkpoint_digest(checkpoint, "run_id"):
        raise SolverBenchmarkCampaignError("Checkpoint run identity mismatch.")
    rows: list[dict[str, object]] = []
    for record in _mapping_list(checkpoint.get("completed"), "checkpoint.completed"):
        result_path = output / str(record["result_path"])
        result = _read_json(result_path)
        _validate_case_result(result)
        if result["result_digest"] != record["result_digest"]:
            raise SolverBenchmarkCampaignError("Checkpoint result digest mismatch.")
        adapter = _mapping(result["adapter_result"], "result.adapter_result")
        recertification = _mapping_or_empty(adapter.get("recertification"))
        solution = _mapping_or_empty(adapter.get("solution"))
        rows.append(
            {
                "adapter_id": record["adapter_id"],
                "case_id": record["case_id"],
                "certificate_attempted": bool(recertification.get("attempted")),
                "certificate_certified": bool(recertification.get("certified")),
                "comparison": result["comparison"],
                "experiment_id": _mapping_or_empty(result.get("experiment")).get(
                    "experiment_id", "canonical"
                ),
                "family": result["family"],
                "placement_count": solution.get("placement_count"),
                "project_digest": result["project_digest"],
                "result_digest": result["result_digest"],
                "solver_status": adapter["status"],
                "split": result["split"],
                "stop_reason": adapter["stop_reason"],
            }
        )
    rows.sort(key=lambda item: (str(item["case_id"]), str(item["adapter_id"])))
    by_adapter: dict[str, dict[str, int]] = {}
    by_comparison: dict[str, int] = {}
    by_family: dict[str, dict[str, int]] = {}
    for row in rows:
        adapter_counts = by_adapter.setdefault(str(row["adapter_id"]), {})
        status = str(row["solver_status"])
        adapter_counts[status] = adapter_counts.get(status, 0) + 1
        comparison = str(row["comparison"])
        by_comparison[comparison] = by_comparison.get(comparison, 0) + 1
        family_counts = by_family.setdefault(str(row["family"]), {})
        family_counts[comparison] = family_counts.get(comparison, 0) + 1
    summary: dict[str, object] = {
        "schema_version": CAMPAIGN_SUMMARY_SCHEMA_V1,
        "manifest_digest": manifest_digest,
        "config": config.to_dict(),
        "row_count": len(rows),
        "rows": rows,
        "counts": {
            "by_adapter_status": {
                adapter_id: dict(sorted(counts.items()))
                for adapter_id, counts in sorted(by_adapter.items())
            },
            "by_comparison": dict(sorted(by_comparison.items())),
            "by_family_comparison": {
                family: dict(sorted(counts.items()))
                for family, counts in sorted(by_family.items())
            },
            "fresh_certified_solution_count": sum(
                bool(row["certificate_certified"]) for row in rows
            ),
        },
        "invariants": {
            "holdout_opened": config.split == "holdout",
            "result_paths_relative": True,
            "resume_without_double_execution": True,
            "solution_requires_fresh_bgig_certificate": True,
        },
    }
    summary["summary_digest"] = canonical_digest(summary)
    return summary


def _apply_experiment(
    case: Mapping[str, object],
    experiment_id: str,
) -> dict[str, object]:
    value = deepcopy(dict(case))
    original_project_digest = str(value.get("project_digest", ""))
    relaxations: list[str] = []
    if experiment_id in {
        "relax_rotation_policy",
        "relax_rotation_and_reservations",
    }:
        features = _mapping_or_empty(value.get("features"))
        recipe = _mapping_or_empty(value.get("recipe"))
        oracle = _mapping_or_empty(value.get("oracle"))
        if str(features.get("rotation_policy_target")) == "forbidden_by_benchmark":
            features["rotation_policy_target"] = "permitted"
            features["rotation_disable_control"] = "relaxed_for_discovery_diagnostic"
            recipe["rotation_policy_target"] = "permitted"
            oracle["rotation_policy_target"] = "permitted"
            value["features"] = features
            value["recipe"] = recipe
            value["oracle"] = oracle
            value["oracle_digest"] = canonical_digest(oracle)
            relaxations.append("rotation_policy_forbidden_to_permitted")
    if experiment_id in {
        "remove_top_reservations",
        "relax_rotation_and_reservations",
    }:
        features = _mapping_or_empty(value.get("features"))
        recipe = _mapping_or_empty(value.get("recipe"))
        project = _mapping(value.get("project"), "case.project")
        if project.get("flat_items"):
            project["flat_items"] = []
            normalized = normalize_project_draft(project).project
            value["project"] = normalized
            value["project_digest"] = canonical_digest(normalized)
            previous = value.get("previous_project")
            if isinstance(previous, Mapping):
                previous_value = dict(previous)
                previous_value["flat_items"] = []
                previous_normalized = normalize_project_draft(previous_value).project
                value["previous_project"] = previous_normalized
                value["previous_project_digest"] = canonical_digest(previous_normalized)
            features["reservation_mode"] = "absent"
            recipe["reservation_mode"] = "absent"
            value["features"] = features
            value["recipe"] = recipe
            relaxations.append("top_reservations_removed")
    value["experiment"] = {
        "experiment_id": experiment_id,
        "lane_ids": list(_LANE_HYPOTHESES.get(experiment_id, ())),
        "monotone_relaxation": experiment_id in _DIAGNOSTIC_RELAXATIONS,
        "original_project_digest": original_project_digest,
        "relaxations": relaxations,
        "truth_preservation": (
            "feasible_witness_remains_feasible_and_fixed_lower_bounds_remain_valid"
            if experiment_id in _DIAGNOSTIC_RELAXATIONS
            else "canonical_case"
        ),
    }
    return value


def _lane_hypothesis_solver(
    experiment_id: str,
) -> Callable[..., dict[str, object]] | None:
    lane_ids = _LANE_HYPOTHESES.get(experiment_id)
    if lane_ids is None:
        return None
    normal_lanes = {
        lane.lane_id: lane for lane in minimal_lane_specs("normal")
    }
    lane_specs = tuple(normal_lanes[lane_id] for lane_id in lane_ids)

    def run(
        raw_project: object,
        *,
        effort_profile: str,
        initial_incumbent: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        if effort_profile != "quick":
            return solve_minimal_layout(
                raw_project,
                effort_profile=effort_profile,
                initial_incumbent=initial_incumbent,
            )
        return _solve_minimal_layout_once(
            raw_project,
            effort_profile=effort_profile,
            request_id=None,
            request_revision=None,
            cancel_check=None,
            container_frontiers=None,
            frontier_digests=(),
            lane_specs_override=lane_specs,
            initial_incumbent=initial_incumbent,
        )

    return run


def _execute_case(case: Mapping[str, object], adapter_id: str) -> dict[str, object]:
    initial_incumbent = None
    context = {
        "incremental_context_requested": False,
        "previous_plan_status": "not_applicable",
        "previous_plan_digest": None,
    }
    features = _mapping_or_empty(case.get("features"))
    if (
        adapter_id == CURRENT_BGIG_ADAPTER_ID
        and str(features.get("execution_mode")) == "incremental"
        and str(features.get("rotation_policy_target")) != "forbidden_by_benchmark"
    ):
        context["incremental_context_requested"] = True
        previous = case.get("previous_project")
        if isinstance(previous, Mapping):
            settings = _mapping(case.get("solver_settings"), "case.solver_settings")
            previous_plan = solve_minimal_layout(
                previous,
                effort_profile=str(settings["effort"]),
            )
            previous_solver = _mapping(previous_plan.get("solver"), "previous.solver")
            previous_status = str(
                _mapping(previous_solver.get("result"), "previous.solver.result").get(
                    "status", "invalid_input"
                )
            )
            context["previous_plan_status"] = previous_status
            context["previous_plan_digest"] = previous_plan.get("plan_digest")
            if previous_status == SOLUTION_FOUND:
                certificate = recertify_minimal_layout_plan(previous_plan)
                if certificate.certified:
                    initial_incumbent = previous_plan
                    context["previous_plan_status"] = "certified_solution_found"
    experiment = _mapping_or_empty(case.get("experiment"))
    execution = run_benchmark_adapter(
        case,
        adapter_id,
        initial_incumbent=initial_incumbent,
        current_solver=_lane_hypothesis_solver(
            str(experiment.get("experiment_id", "canonical"))
        ),
    )
    adapter_result = execution.report
    comparison = _compare_result(case, adapter_result)
    result: dict[str, object] = {
        "schema_version": CAMPAIGN_CASE_RESULT_SCHEMA_V1,
        "adapter_id": adapter_id,
        "adapter_result": deepcopy(adapter_result),
        "case_id": str(case["case_id"]),
        "comparison": comparison,
        "context": context,
        "experiment": deepcopy(_mapping_or_empty(case.get("experiment"))),
        "family": str(case.get("family", "regression")),
        "project_digest": str(case["project_digest"]),
        "split": str(case.get("split", "regression")),
    }
    result["result_digest"] = canonical_digest(result)
    return result


def _compare_result(
    case: Mapping[str, object],
    adapter_result: Mapping[str, object],
) -> str:
    status = str(adapter_result.get("status", "invalid_input"))
    if status == STATUS_CERTIFICATE_REJECTED:
        return "functional_regression_certificate_rejected"
    if status == STATUS_UNSUPPORTED:
        return "unsupported_constraint"
    if status == STATUS_BOUNDED_UNKNOWN:
        return "bounded_unknown"
    if str(case.get("split", "regression")) == "regression":
        expectations = _mapping_or_empty(case.get("expectations"))
        accepted = expectations.get("accepted_statuses", [])
        if isinstance(accepted, list) and status in {str(value) for value in accepted}:
            return "regression_expectation_met"
        return "functional_regression_unexpected_status"
    oracle = _mapping(case.get("oracle"), "case.oracle")
    expected = str(oracle.get("expected_truth", ""))
    if expected == "feasible":
        return (
            "feasible_found"
            if status == SOLUTION_FOUND
            else "feasible_missed_within_budget"
        )
    if expected == "impossible":
        if status == SOLUTION_FOUND:
            return "oracle_contradiction_certified_solution"
        if status == STATUS_PROVEN_IMPOSSIBLE:
            return "impossible_proven"
        return "impossible_not_overclaimed"
    return "reference_truth_missing"


def _run_identity(
    manifest: Mapping[str, object],
    config: CampaignPhaseConfig,
    schedule: Sequence[tuple[Mapping[str, object], str]],
    holdout_selection: object | None,
) -> dict[str, object]:
    identity: dict[str, object] = {
        "base_sha": config.base_sha,
        "branch": config.branch,
        "config": config.to_dict(),
        "manifest_digest": manifest["manifest_digest"],
        "producer": deepcopy(manifest["producer"]),
        "schedule": [
            {
                "adapter_id": adapter_id,
                "case_id": case["case_id"],
                "project_digest": case["project_digest"],
            }
            for case, adapter_id in schedule
        ],
        "selection_digest": (
            _mapping_or_empty(holdout_selection).get("selection_digest")
            if holdout_selection is not None
            else None
        ),
    }
    identity["run_id"] = canonical_digest(identity)
    return identity


def _load_or_create_checkpoint(
    path: Path,
    identity: Mapping[str, object],
    manifest: Mapping[str, object],
    config: CampaignPhaseConfig,
    schedule_count: int,
) -> dict[str, object]:
    if path.is_file():
        checkpoint = _read_json(path)
        _validate_checkpoint(checkpoint)
        if checkpoint.get("run_id") != identity.get("run_id"):
            raise SolverBenchmarkCampaignError(
                "Existing checkpoint belongs to another campaign run."
            )
        return checkpoint
    checkpoint: dict[str, object] = {
        "schema_version": CAMPAIGN_CHECKPOINT_SCHEMA_V1,
        "run_id": identity["run_id"],
        "identity": deepcopy(dict(identity)),
        "base_sha": config.base_sha,
        "branch": config.branch,
        "manifest_digest": manifest["manifest_digest"],
        "producer": deepcopy(manifest["producer"]),
        "phase": config.split,
        "completed": [],
        "last_completed": None,
        "budget": {
            "consumed_case_executions": 0,
            "maximum_case_executions": config.max_case_executions,
            "remaining_case_executions": config.max_case_executions,
            "scheduled_case_executions": schedule_count,
        },
        "child_pid": None,
        "next_action": "first_scheduled_case",
        "stop_reason": "initialized",
        "summary_digest": None,
        "summary_path": None,
    }
    _finalize_checkpoint(checkpoint, path)
    return checkpoint


def _finalize_checkpoint(checkpoint: dict[str, object], path: Path) -> None:
    checkpoint.pop("checkpoint_digest", None)
    checkpoint["checkpoint_digest"] = canonical_digest(checkpoint)
    _write_json_atomic(path, checkpoint)


def _validate_checkpoint(checkpoint: Mapping[str, object]) -> None:
    if checkpoint.get("schema_version") != CAMPAIGN_CHECKPOINT_SCHEMA_V1:
        raise SolverBenchmarkCampaignError("Unsupported campaign checkpoint schema.")
    supplied = checkpoint.get("checkpoint_digest")
    payload = dict(checkpoint)
    payload.pop("checkpoint_digest", None)
    if canonical_digest(payload) != supplied:
        raise SolverBenchmarkCampaignError("Campaign checkpoint digest mismatch.")
    identity = _mapping(checkpoint.get("identity"), "checkpoint.identity")
    if identity.get("run_id") != checkpoint.get("run_id"):
        raise SolverBenchmarkCampaignError("Campaign checkpoint identity mismatch.")


def _checkpoint_digest(checkpoint: Mapping[str, object], field: str) -> object:
    identity = _mapping(checkpoint.get("identity"), "checkpoint.identity")
    return identity.get(field)


def _completed_result_is_valid(
    output: Path,
    record: Mapping[str, object],
) -> bool:
    path = output / str(record.get("result_path", ""))
    if not path.is_file():
        return False
    try:
        result = _read_json(path)
        _validate_case_result(result)
    except (OSError, json.JSONDecodeError, SolverBenchmarkCampaignError):
        return False
    return (
        result.get("result_digest") == record.get("result_digest")
        and result.get("case_id") == record.get("case_id")
        and result.get("adapter_id") == record.get("adapter_id")
    )


def _validate_case_result(result: Mapping[str, object]) -> None:
    if result.get("schema_version") != CAMPAIGN_CASE_RESULT_SCHEMA_V1:
        raise SolverBenchmarkCampaignError("Unsupported campaign case-result schema.")
    supplied = result.get("result_digest")
    payload = dict(result)
    payload.pop("result_digest", None)
    if canonical_digest(payload) != supplied:
        raise SolverBenchmarkCampaignError("Campaign case-result digest mismatch.")


def _write_json_atomic(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    temporary.write_text(rendered, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise SolverBenchmarkCampaignError(f"{path.name} must contain an object.")
    return dict(value)


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise SolverBenchmarkCampaignError(f"{field} must be an object.")
    return dict(value)


def _mapping_or_empty(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _mapping_list(value: object, field: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise SolverBenchmarkCampaignError(f"{field} must be a list of objects.")
    return [dict(item) for item in value]


def _execution_key(case_id: str, adapter_id: str) -> str:
    return f"{case_id}::{adapter_id}"


def _safe_component(value: str) -> str:
    safe = "".join(character if character.isalnum() or character in "-_" else "-" for character in value)
    return safe.strip("-") or "case"


def _is_digest(value: object) -> bool:
    if not isinstance(value, str) or len(value) not in {40, 64}:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True
