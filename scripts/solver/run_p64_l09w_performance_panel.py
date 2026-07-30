#!/usr/bin/env python3
"""Run a checkpointed open P64-L09W performance panel.

The runner accepts only the public manifest and a versioned open panel plan.
It has no holdout input.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
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
from scripts.solver import build_p64_l09w_performance_panels as panels  # noqa: E402
from scripts.solver import (  # noqa: E402
    plan_p64_l09w_d_stratified_validation as stratified,
)
from scripts.solver import (  # noqa: E402
    run_p64_l09w_c_reference_campaign as campaign,
)


SCHEMA_VERSION = "bgig.p64_l09w_performance_panel_report.v1"
CHECKPOINT_SCHEMA_VERSION = (
    "bgig.p64_l09w_performance_panel_checkpoint.v1"
)
MAX_BATCH_SIZE = 4


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain one JSON object.")
    return value


def _write_json_atomic(
    path: Path,
    value: Mapping[str, object],
) -> None:
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


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


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
            raise RuntimeError("Performance checkpoint binding is invalid.")
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
        raise RuntimeError("Cannot recover without a checkpoint.")
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


def _seed_case_results(
    value: Mapping[str, object],
    *,
    scheduled_ids: set[str],
    code_bundle_digest: str,
    manifest_digest: str,
    repetitions: int,
) -> tuple[dict[str, object], str]:
    seed = deepcopy(dict(value))
    supplied = seed.pop("checkpoint_digest", None)
    binding = seed.get("binding_payload")
    raw_results = seed.get("case_results")
    if (
        seed.get("schema_version") != CHECKPOINT_SCHEMA_VERSION
        or supplied != canonical_digest(seed)
        or not isinstance(binding, Mapping)
        or seed.get("binding_digest") != canonical_digest(binding)
        or binding.get("tier") != "sentinel"
        or binding.get("code_bundle_digest") != code_bundle_digest
        or binding.get("manifest_digest") != manifest_digest
        or binding.get("repetitions") != repetitions
        or not isinstance(raw_results, Mapping)
    ):
        raise RuntimeError("Seed checkpoint is incompatible.")
    imported = {}
    for case_id, result in raw_results.items():
        normalized_id = str(case_id)
        if normalized_id not in scheduled_ids:
            continue
        validated = campaign._validate_case_result(result)
        if validated["case_id"] != normalized_id:
            raise RuntimeError("Seed checkpoint case identity is invalid.")
        imported[normalized_id] = validated
    return imported, str(supplied)


def _is_ready(result: Mapping[str, object]) -> bool:
    runs = result.get("runs")
    if (
        not isinstance(runs, list)
        or not runs
        or not isinstance(runs[0], Mapping)
    ):
        return False
    finalization = runs[0].get("finalization")
    cad_ir = runs[0].get("cad_ir")
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
            isinstance(value, Mapping)
            and value.get("detail") == stratified.TARGET_LOSS
            for value in losses
        )
    )


def _assess_case(
    plan_case: Mapping[str, object],
    result: Mapping[str, object],
) -> dict[str, object]:
    reference = dict(plan_case["reference"])
    roles = {str(value) for value in plan_case["roles"]}
    runs = [
        value
        for value in result.get("runs", [])
        if isinstance(value, Mapping)
    ]
    first = runs[0] if runs else {}
    failures = []
    if result.get("status") == campaign.RESULT_PROVEN_IMPOSSIBLE:
        failures.append("false_impossible")
    if result.get("status") == campaign.RESULT_ERROR:
        failures.append("candidate_error_or_uncertified_solution")
    if (
        reference.get("status") == campaign.RESULT_CERTIFIED
        and result.get("status") != campaign.RESULT_CERTIFIED
    ):
        failures.append("certified_status_regression")
    if (
        reference.get("placement_digest")
        and first.get("placement_digest")
        != reference.get("placement_digest")
    ):
        failures.append("selected_placement_regression")
    if "ready_non_regression" in roles and not _is_ready(result):
        failures.append("ready_result_regression")
    if "causal" in roles and (
        not _is_ready(result) or _has_target_loss(result)
    ):
        failures.append("causal_case_failure")
    selected_digests = sorted(
        {
            str(value.get("selected_product_digest"))
            for value in runs
            if value.get("selected_product_digest")
        }
    )
    trace_digests = sorted(
        {
            str(value.get("execution_trace_digest"))
            for value in runs
            if value.get("execution_trace_digest")
        }
    )
    placement_digests = sorted(
        {
            str(value.get("placement_digest"))
            for value in runs
            if value.get("placement_digest")
        }
    )
    route_variants = sorted(
        {
            (
                str(dict(value.get("route", {})).get("candidate_source")),
                str(dict(value.get("route", {})).get("lane_id")),
            )
            for value in runs
        }
    )
    if result.get("status") == campaign.RESULT_CERTIFIED:
        nondeterministic_product = (
            len(selected_digests) != 1
            or len(placement_digests) != 1
        )
    else:
        nondeterministic_product = (
            len(selected_digests) > 1
            or len(placement_digests) > 1
        )
    if nondeterministic_product:
        failures.append("selected_product_nondeterminism")
    return {
        "case_id": plan_case["case_id"],
        "stratum": plan_case["stratum"],
        "roles": sorted(roles),
        "status": result.get("status"),
        "ready": _is_ready(result),
        "target_loss_present": _has_target_loss(result),
        "selected_product_digest_count": len(selected_digests),
        "selected_product_digests": selected_digests,
        "placement_digests": placement_digests,
        "execution_trace_digest_count": len(trace_digests),
        "execution_trace_digests": trace_digests,
        "execution_route_variant_count": len(route_variants),
        "execution_route_variants": [
            {"candidate_source": source, "lane_id": lane}
            for source, lane in route_variants
        ],
        "hard_gate_passed": not failures,
        "failures": failures,
    }


def _nearest_rank(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    rank = max(1, (len(ordered) * int(fraction * 100) + 99) // 100)
    return ordered[min(rank - 1, len(ordered) - 1)]


def _timing_summary(result: Mapping[str, object]) -> dict[str, object]:
    samples = [
        float(value["timings"]["calculation_ms"])
        for value in result["runs"]
        if isinstance(value, Mapping)
    ]
    center = median(samples)
    absolute_deviations = [abs(value - center) for value in samples]
    return {
        "sample_count": len(samples),
        "samples_ms": samples,
        "minimum_ms": min(samples),
        "median_ms": center,
        "p95_ms": _nearest_rank(samples, 0.95),
        "maximum_ms": max(samples),
        "range_ms": max(samples) - min(samples),
        "mad_ms": median(absolute_deviations),
    }


def _build_report(
    *,
    plan: Mapping[str, object],
    tier: str,
    checkpoint: Mapping[str, object],
) -> dict[str, object]:
    case_by_id = {
        str(value["case_id"]): value
        for value in plan["cases"]
        if isinstance(value, Mapping)
    }
    scheduled_ids = list(plan["selection"][f"{tier}_case_ids"])
    results = {
        str(case_id): campaign._validate_case_result(value)
        for case_id, value in checkpoint["case_results"].items()
        if isinstance(value, Mapping)
    }
    assessments = [
        _assess_case(case_by_id[case_id], results[case_id])
        for case_id in scheduled_ids
        if case_id in results
    ]
    timings = {
        case_id: _timing_summary(results[case_id])
        for case_id in scheduled_ids
        if case_id in results
    }
    failures = [
        {
            "case_id": value["case_id"],
            "failures": value["failures"],
        }
        for value in assessments
        if value["failures"]
    ]
    complete = len(results) == len(scheduled_ids)
    stopped = bool(checkpoint.get("stopped")) or bool(failures)
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-D-P",
        "tier": tier,
        "status": (
            "stopped"
            if stopped
            else "complete"
            if complete
            else "partial"
        ),
        "decision": (
            f"{tier}_baseline_passed"
            if complete and not stopped
            else f"{tier}_hard_gate_failed"
            if stopped
            else f"continue_{tier}_baseline"
        ),
        "bindings": {
            **deepcopy(dict(checkpoint["binding_payload"])),
            "binding_digest": checkpoint["binding_digest"],
            "checkpoint_digest": checkpoint["checkpoint_digest"],
        },
        "execution": {
            "scheduled_case_count": len(scheduled_ids),
            "completed_case_count": len(results),
            "remaining_case_count": len(scheduled_ids) - len(results),
            "repetitions_per_case": plan["tiers"][tier]["repetitions"],
            "active_case_id": checkpoint.get("active_case_id"),
            "stopped": stopped,
        },
        "functional": {
            "hard_gate_failure_count": len(failures),
            "failures": failures,
            "assessment_count": len(assessments),
            "assessments": assessments,
        },
        "performance": {
            "thresholds_defined": False,
            "timings_by_case": timings,
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
        },
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument(
        "--tier",
        choices=("sentinel", "candidate"),
        required=True,
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--worker-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--seed-checkpoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-new-cases", type=int, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--recover-interrupted-case")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError(
            "P64-L09W performance panels require Fusion CPython 3.14."
        )
    if not 1 <= args.max_new_cases <= MAX_BATCH_SIZE:
        raise ValueError(
            f"max-new-cases must stay between 1 and {MAX_BATCH_SIZE}."
        )
    plan = panels.validate_plan(_read_json(args.plan))
    built = campaign.build_open_inventory(_read_json(args.manifest))
    if (
        built["inventory"]["manifest_digest"]
        != plan["sources"]["manifest_digest"]
    ):
        raise RuntimeError("Panel plan no longer matches public manifest.")
    runtime_receipt = campaign._validate_runtime_receipt(
        _read_json(args.runtime_receipt)
    )
    repetitions = int(plan["tiers"][args.tier]["repetitions"])
    scheduled_ids = list(
        plan["selection"][f"{args.tier}_case_ids"]
    )
    seed_results: dict[str, object] = {}
    seed_digest = None
    if args.seed_checkpoint is not None:
        if args.tier != "sentinel" or args.resume:
            raise RuntimeError(
                "Seed checkpoint is allowed only for a new sentinel run."
            )
        seed_results, seed_digest = _seed_case_results(
            _read_json(args.seed_checkpoint),
            scheduled_ids=set(scheduled_ids),
            code_bundle_digest=campaign._code_bundle_digest(),
            manifest_digest=built["inventory"]["manifest_digest"],
            repetitions=repetitions,
        )
        records_by_id_for_seed = {
            str(value["case_id"]): value
            for value in built["records"]
        }
        if any(
            result["case_digest"]
            != records_by_id_for_seed[case_id]["case_digest"]
            for case_id, result in seed_results.items()
        ):
            raise RuntimeError(
                "Seed checkpoint does not match public case digests."
            )
    binding_payload = {
        "plan_digest": plan["plan_digest"],
        "tier": args.tier,
        "repetitions": repetitions,
        "runner_digest": _sha256_path(Path(__file__).resolve()),
        "manifest_digest": built["inventory"]["manifest_digest"],
        "code_bundle_digest": campaign._code_bundle_digest(),
        "runtime_artifact_digest": campaign.SCIP_PRODUCT_ARTIFACT_DIGEST,
        "runtime_receipt_digest": runtime_receipt["receipt_digest"],
        "seed_checkpoint_digest": seed_digest,
    }
    if args.validate_only:
        print(
            "P64_L09W_PERFORMANCE_PANEL_VALIDATE_OK "
            f"tier={args.tier} "
            f"cases={plan['tiers'][args.tier]['case_count']} "
            f"repetitions={repetitions} "
            f"plan={plan['plan_digest']}",
            flush=True,
        )
        return 0

    checkpoint = _checkpoint(
        args.checkpoint,
        binding_payload=binding_payload,
        resume=args.resume,
        recover_interrupted_case=args.recover_interrupted_case,
    )
    if seed_results:
        if checkpoint["case_results"]:
            raise RuntimeError("Cannot seed a non-empty checkpoint.")
        checkpoint["case_results"] = seed_results
        _save_checkpoint(args.checkpoint, checkpoint)
    if checkpoint.get("stopped"):
        raise RuntimeError("Checkpoint is stopped after a hard gate failure.")

    records_by_id = {
        str(value["case_id"]): value for value in built["records"]
    }
    cases_by_id = {
        str(value["case_id"]): value
        for value in plan["cases"]
        if isinstance(value, Mapping)
    }
    completed = dict(checkpoint["case_results"])
    pending = [
        case_id for case_id in scheduled_ids if case_id not in completed
    ][: args.max_new_cases]

    campaign.configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root,
    )
    initial_completed = len(completed)
    for case_id in pending:
        checkpoint["active_case_id"] = case_id
        _save_checkpoint(args.checkpoint, checkpoint)
        result = campaign.run_open_case(
            records_by_id[case_id],
            repeat_count=repetitions,
        )
        checkpoint["case_results"][case_id] = result
        checkpoint["active_case_id"] = None
        assessment = _assess_case(cases_by_id[case_id], result)
        if assessment["failures"]:
            checkpoint["gate_failures"].append(assessment)
            checkpoint["stopped"] = True
        _save_checkpoint(args.checkpoint, checkpoint)
        timing = _timing_summary(result)
        print(
            "P64_L09W_PERFORMANCE_PANEL_CASE "
            f"tier={args.tier} "
            f"completed={len(checkpoint['case_results'])}/"
            f"{len(scheduled_ids)} "
            f"case={case_id} "
            f"median_ms={timing['median_ms']:.3f} "
            f"mad_ms={timing['mad_ms']:.3f} "
            f"gate={str(assessment['hard_gate_passed']).lower()}",
            flush=True,
        )
        if checkpoint["stopped"]:
            break

    report = _build_report(
        plan=plan,
        tier=args.tier,
        checkpoint=checkpoint,
    )
    _write_json_atomic(args.output, report)
    print(
        "P64_L09W_PERFORMANCE_PANEL_BATCH "
        f"tier={args.tier} "
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
