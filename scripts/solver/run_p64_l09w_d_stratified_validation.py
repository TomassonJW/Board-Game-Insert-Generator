#!/usr/bin/env python3
"""Exécute la validation ouverte stratifiée P64-L09W-D.

L'exécuteur ne connaît que le manifest public, le plan stratifié et les
checkpoints ouverts C/D. Il ne possède aucune entrée permettant d'ouvrir le
holdout.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from scripts.solver import (  # noqa: E402
    plan_p64_l09w_d_stratified_validation as planner,
)
from scripts.solver import (  # noqa: E402
    run_p64_l09w_c_reference_campaign as campaign,
)


SCHEMA_VERSION = "bgig.p64_l09w_d_stratified_validation.v1"
CHECKPOINT_SCHEMA_VERSION = (
    "bgig.p64_l09w_d_stratified_validation_checkpoint.v1"
)
MAX_BATCH_SIZE = 10


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain one JSON object.")
    return value


def _write_json_atomic(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


def _validated_plan(value: Mapping[str, object]) -> dict[str, object]:
    plan = deepcopy(dict(value))
    supplied = plan.pop("plan_digest", None)
    if (
        plan.get("schema_version") != planner.SCHEMA_VERSION
        or plan.get("status") != "planned"
        or not isinstance(supplied, str)
        or supplied != canonical_digest(plan)
        or not isinstance(plan.get("schedule"), list)
        or dict(plan.get("execution", {})).get("holdout_file_read") is not False
        or dict(plan.get("execution", {})).get("holdout_opening_count") != 0
        or dict(plan.get("execution", {})).get(
            "holdout_solver_invocation_count"
        )
        != 0
    ):
        raise RuntimeError("Stratified validation plan is invalid.")
    plan["plan_digest"] = supplied
    return plan


def _checkpoint(
    path: Path,
    *,
    binding_payload: Mapping[str, object],
    resume: bool,
    recover_interrupted_case: str | None,
) -> dict[str, object]:
    binding_digest = canonical_digest(binding_payload)
    if path.exists():
        if not resume:
            raise RuntimeError("Checkpoint already exists; use --resume.")
        value = _read_json(path)
        supplied = value.pop("checkpoint_digest", None)
        if (
            value.get("schema_version") != CHECKPOINT_SCHEMA_VERSION
            or value.get("binding_digest") != binding_digest
            or value.get("binding_payload") != dict(binding_payload)
            or supplied != canonical_digest(value)
            or not isinstance(value.get("case_results"), dict)
            or not isinstance(value.get("gate_failures"), list)
        ):
            raise RuntimeError("Stratified checkpoint binding is invalid.")
        value["checkpoint_digest"] = supplied
        active = value.get("active_case_id")
        if active is not None:
            if recover_interrupted_case != active:
                raise RuntimeError(
                    "Checkpoint has an ambiguous active case; pass the exact "
                    "--recover-interrupted-case id after process verification."
                )
            value["active_case_id"] = None
            _save_checkpoint(path, value)
        elif recover_interrupted_case is not None:
            raise RuntimeError("No interrupted case exists in checkpoint.")
        return value
    if resume:
        raise RuntimeError("Cannot resume a missing checkpoint.")
    if recover_interrupted_case is not None:
        raise RuntimeError("Cannot recover without an existing checkpoint.")
    value = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "binding_digest": binding_digest,
        "binding_payload": deepcopy(dict(binding_payload)),
        "active_case_id": None,
        "case_results": {},
        "gate_failures": [],
        "stopped": False,
    }
    value["checkpoint_digest"] = canonical_digest(value)
    _write_json_atomic(path, value)
    return value


def _save_checkpoint(path: Path, value: dict[str, object]) -> None:
    value.pop("checkpoint_digest", None)
    value["checkpoint_digest"] = canonical_digest(value)
    _write_json_atomic(path, value)


def _first_run(result: Mapping[str, object]) -> Mapping[str, object]:
    runs = result.get("runs")
    if (
        not isinstance(runs, list)
        or not runs
        or not isinstance(runs[0], Mapping)
    ):
        raise RuntimeError("Case result has no first run.")
    return runs[0]


def _is_ready(result: Mapping[str, object]) -> bool:
    run = _first_run(result)
    finalization = run.get("finalization")
    cad_ir = run.get("cad_ir")
    return bool(
        isinstance(finalization, Mapping)
        and finalization.get("status") == "solution_found"
        and isinstance(cad_ir, Mapping)
        and cad_ir.get("status") == "ready_for_fusion"
    )


def _has_target_loss(result: Mapping[str, object]) -> bool:
    losses = result.get("losses")
    return bool(
        isinstance(losses, list)
        and any(
            isinstance(loss, Mapping)
            and loss.get("detail") == planner.TARGET_LOSS
            for loss in losses
        )
    )


def _functional_signature(
    result: Mapping[str, object],
) -> tuple[object, ...]:
    run = _first_run(result)
    return (
        result.get("status"),
        run.get("solver_status"),
        run.get("functional_digest"),
        run.get("placement_digest"),
    )


def _solver_signature(
    result: Mapping[str, object],
) -> tuple[object, ...]:
    run = _first_run(result)
    route = run.get("route")
    return (
        result.get("status"),
        run.get("solver_status"),
        run.get("placement_digest"),
        (
            route.get("lane_id")
            if isinstance(route, Mapping)
            else None
        ),
    )


def assess_case(
    *,
    schedule_row: Mapping[str, object],
    reference_result: Mapping[str, object],
    candidate_result: Mapping[str, object],
) -> dict[str, object]:
    case_id = str(schedule_row["case_id"])
    tiers = {str(value) for value in schedule_row.get("tiers", [])}
    failures: list[str] = []
    status = candidate_result.get("status")
    if status == campaign.RESULT_PROVEN_IMPOSSIBLE:
        failures.append("false_impossible")
    if status == campaign.RESULT_ERROR:
        failures.append("candidate_error_or_uncertified_solution")
    if (
        status != reference_result.get("status")
        and reference_result.get("status") == campaign.RESULT_CERTIFIED
    ):
        failures.append("certified_status_regression")
    if "target_stratified" in tiers:
        if (
            reference_result.get("deterministic") is True
            and candidate_result.get("deterministic") is not True
        ):
            failures.append("target_replay_nondeterminism_regression")
        if _solver_signature(candidate_result) != _solver_signature(
            reference_result
        ):
            failures.append("target_solver_signature_regression")

    ready = _is_ready(candidate_result)
    if "ready_non_regression" in tiers:
        if not ready:
            failures.append("ready_result_regression")
        if _functional_signature(candidate_result) != _functional_signature(
            reference_result
        ):
            failures.append("ready_functional_digest_regression")

    target_removed = not _has_target_loss(candidate_result)
    if "causal" in tiers and (not ready or not target_removed):
        failures.append("causal_case_failure")

    return {
        "case_id": case_id,
        "stratum": schedule_row["stratum"],
        "tiers": sorted(tiers),
        "ready": ready,
        "target_loss_removed": target_removed,
        "preexisting_nondeterminism": (
            reference_result.get("deterministic") is False
        ),
        "hard_gate_passed": not failures,
        "failures": failures,
    }


def _execution_order(
    schedule: Sequence[Mapping[str, object]],
) -> list[Mapping[str, object]]:
    def key(row: Mapping[str, object]) -> tuple[int, float, str]:
        tiers = {str(value) for value in row.get("tiers", [])}
        case_id = str(row["case_id"])
        if "causal" in tiers:
            priority = 0 if row.get("stratum") == "stress" else 1
        elif "ready_non_regression" in tiers:
            priority = 2
        else:
            priority = 3
        return (
            priority,
            float(row.get("reference_calculation_ms", 0.0)),
            case_id,
        )

    return sorted(schedule, key=key)


def _build_report(
    *,
    plan: Mapping[str, object],
    checkpoint: Mapping[str, object],
    reference_results: Mapping[str, Mapping[str, object]],
    source_candidate_results: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    executed_results = {
        str(case_id): campaign._validate_case_result(value)
        for case_id, value in dict(checkpoint["case_results"]).items()
        if isinstance(value, Mapping)
    }
    assessments = []
    scheduled_ids = []
    for row in _execution_order(plan["schedule"]):
        case_id = str(row["case_id"])
        scheduled_ids.append(case_id)
        result = (
            source_candidate_results.get(case_id)
            if row.get("already_completed") is True
            else executed_results.get(case_id)
        )
        if result is None:
            continue
        assessments.append(
            assess_case(
                schedule_row=row,
                reference_result=reference_results[case_id],
                candidate_result=result,
            )
        )
    completed_ids = {str(value["case_id"]) for value in assessments}
    failures = [
        {
            "case_id": assessment["case_id"],
            "failures": assessment["failures"],
        }
        for assessment in assessments
        if assessment["failures"]
    ]
    complete = len(completed_ids) == len(scheduled_ids)
    stopped = bool(checkpoint.get("stopped")) or bool(failures)
    status = "stopped" if stopped else "complete" if complete else "partial"
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-D",
        "status": status,
        "decision": (
            "increment_validation_passed"
            if complete and not stopped
            else "increment_validation_failed"
            if stopped
            else "continue_stratified_validation"
        ),
        "bindings": {
            **deepcopy(dict(checkpoint["binding_payload"])),
            "binding_digest": checkpoint["binding_digest"],
            "checkpoint_digest": checkpoint["checkpoint_digest"],
        },
        "execution": {
            "scheduled_case_count": len(scheduled_ids),
            "reused_case_count": sum(
                bool(row.get("already_completed"))
                for row in plan["schedule"]
            ),
            "new_completed_case_count": len(executed_results),
            "completed_case_count": len(completed_ids),
            "remaining_case_count": len(scheduled_ids) - len(completed_ids),
            "active_case_id": checkpoint.get("active_case_id"),
            "stopped": stopped,
        },
        "summary": {
            "hard_gate_failure_count": len(failures),
            "failures": failures,
            "causal_pass_count": sum(
                "causal" in assessment["tiers"]
                and assessment["hard_gate_passed"]
                for assessment in assessments
            ),
            "ready_non_regression_pass_count": sum(
                "ready_non_regression" in assessment["tiers"]
                and assessment["hard_gate_passed"]
                for assessment in assessments
            ),
            "target_sample_count": sum(
                "target_stratified" in assessment["tiers"]
                for assessment in assessments
            ),
            "target_loss_removed_count": sum(
                "target_stratified" in assessment["tiers"]
                and assessment["target_loss_removed"]
                for assessment in assessments
            ),
            "target_ready_count": sum(
                "target_stratified" in assessment["tiers"]
                and assessment["ready"]
                for assessment in assessments
            ),
            "by_stratum": dict(
                sorted(
                    Counter(
                        str(assessment["stratum"])
                        for assessment in assessments
                    ).items()
                )
            ),
            "assessments": assessments,
        },
        "invariants": {
            "sample_is_rate_estimator": False,
            "holdout_file_read": False,
            "holdout_opening_count": 0,
            "holdout_solver_invocation_count": 0,
            "solver_budget_changed": False,
            "product_grid_changed": False,
            "geometry_epsilon_changed": False,
            "physical_value_changed": False,
            "print_validated": False,
        },
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--worker-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--reference-checkpoint", type=Path, required=True)
    parser.add_argument("--candidate-checkpoint", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--max-new-cases", type=int, required=True)
    parser.add_argument("--recover-interrupted-case")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError(
            "P64-L09W-D must run with the Fusion CPython 3.14 ABI."
        )
    if not 1 <= args.max_new_cases <= MAX_BATCH_SIZE:
        raise ValueError(
            f"max-new-cases must stay between 1 and {MAX_BATCH_SIZE}."
        )
    plan = _validated_plan(_read_json(args.plan))
    reference = planner._validated_checkpoint(
        _read_json(args.reference_checkpoint)
    )
    source_candidate = planner._validated_checkpoint(
        _read_json(args.candidate_checkpoint)
    )
    if (
        plan["sources"]["reference_checkpoint_digest"]
        != reference["checkpoint_digest"]
        or plan["sources"]["candidate_checkpoint_digest"]
        != source_candidate["checkpoint_digest"]
        or plan["sources"]["current_code_bundle_digest"]
        != campaign._code_bundle_digest()
    ):
        raise RuntimeError("Plan no longer matches checkpoints or code bundle.")

    built = campaign.build_open_inventory(_read_json(args.manifest))
    inventory = dict(built["inventory"])
    if inventory["manifest_digest"] != plan["sources"]["manifest_digest"]:
        raise RuntimeError("Plan no longer matches public manifest.")
    records_by_id = {
        str(record["case_id"]): record for record in built["records"]
    }
    reference_results = {
        str(case_id): planner._validated_case_result(value)
        for case_id, value in dict(reference["case_results"]).items()
        if isinstance(value, Mapping)
    }
    source_candidate_results = {
        str(case_id): planner._validated_case_result(value)
        for case_id, value in dict(source_candidate["case_results"]).items()
        if isinstance(value, Mapping)
    }
    runtime_receipt = campaign._validate_runtime_receipt(
        _read_json(args.runtime_receipt)
    )
    binding_payload = {
        "plan_digest": plan["plan_digest"],
        "executor_digest": _sha256_path(Path(__file__).resolve()),
        "manifest_digest": inventory["manifest_digest"],
        "reference_checkpoint_digest": reference["checkpoint_digest"],
        "source_candidate_checkpoint_digest": source_candidate[
            "checkpoint_digest"
        ],
        "code_bundle_digest": campaign._code_bundle_digest(),
        "runtime_artifact_digest": campaign.SCIP_PRODUCT_ARTIFACT_DIGEST,
        "runtime_receipt_digest": runtime_receipt["receipt_digest"],
    }
    if args.validate_only:
        print(
            "P64_L09W_D_STRATIFIED_VALIDATE_OK "
            f"plan={plan['plan_digest']} "
            f"scheduled={len(plan['schedule'])} "
            f"new={plan['execution']['new_case_count']} "
            f"replays={plan['execution']['new_replay_count']}",
            flush=True,
        )
        return 0
    checkpoint = _checkpoint(
        args.checkpoint,
        binding_payload=binding_payload,
        resume=args.resume,
        recover_interrupted_case=args.recover_interrupted_case,
    )
    if checkpoint.get("stopped"):
        raise RuntimeError("Checkpoint is stopped after a hard gate failure.")

    reused_failures = []
    for row in plan["schedule"]:
        if row.get("already_completed") is not True:
            continue
        case_id = str(row["case_id"])
        assessment = assess_case(
            schedule_row=row,
            reference_result=reference_results[case_id],
            candidate_result=source_candidate_results[case_id],
        )
        if assessment["failures"]:
            reused_failures.append(assessment)
    if reused_failures:
        checkpoint["gate_failures"] = reused_failures
        checkpoint["stopped"] = True
        _save_checkpoint(args.checkpoint, checkpoint)
        report = _build_report(
            plan=plan,
            checkpoint=checkpoint,
            reference_results=reference_results,
            source_candidate_results=source_candidate_results,
        )
        _write_json_atomic(args.output, report)
        print(
            "P64_L09W_D_STRATIFIED_STOP "
            "reason=reused_case_gate_failure "
            f"report={report['report_digest']}",
            flush=True,
        )
        return 2

    campaign.configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root,
    )
    completed = dict(checkpoint["case_results"])
    pending = [
        row
        for row in _execution_order(plan["schedule"])
        if row.get("already_completed") is not True
        and str(row["case_id"]) not in completed
    ]
    selected = pending[: args.max_new_cases]
    initial_completed = len(completed)
    for row in selected:
        case_id = str(row["case_id"])
        checkpoint["active_case_id"] = case_id
        _save_checkpoint(args.checkpoint, checkpoint)
        result = campaign.run_open_case(
            records_by_id[case_id],
            repeat_count=int(row["required_repeats"]),
        )
        checkpoint["case_results"][case_id] = result
        checkpoint["active_case_id"] = None
        assessment = assess_case(
            schedule_row=row,
            reference_result=reference_results[case_id],
            candidate_result=result,
        )
        if assessment["failures"]:
            checkpoint["gate_failures"].append(assessment)
            checkpoint["stopped"] = True
        _save_checkpoint(args.checkpoint, checkpoint)
        print(
            "P64_L09W_D_STRATIFIED_CASE "
            f"completed={len(checkpoint['case_results'])}/"
            f"{plan['execution']['new_case_count']} "
            f"case={case_id} repeats={row['required_repeats']} "
            f"ready={str(assessment['ready']).lower()} "
            f"target_removed={str(assessment['target_loss_removed']).lower()} "
            f"gate={str(assessment['hard_gate_passed']).lower()}",
            flush=True,
        )
        if checkpoint["stopped"]:
            break

    report = _build_report(
        plan=plan,
        checkpoint=checkpoint,
        reference_results=reference_results,
        source_candidate_results=source_candidate_results,
    )
    _write_json_atomic(args.output, report)
    print(
        "P64_L09W_D_STRATIFIED_BATCH "
        f"status={report['status']} "
        f"new={len(checkpoint['case_results']) - initial_completed} "
        f"completed={report['execution']['completed_case_count']}/"
        f"{report['execution']['scheduled_case_count']} "
        f"checkpoint={checkpoint['checkpoint_digest']} "
        f"report={report['report_digest']}",
        flush=True,
    )
    return 2 if checkpoint["stopped"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
