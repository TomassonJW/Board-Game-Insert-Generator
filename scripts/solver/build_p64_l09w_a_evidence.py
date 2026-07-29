#!/usr/bin/env python3
"""Construit la preuve compacte et versionnée de P64-L09W-A."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)


SCHEMA_VERSION = "bgig.p64_l09w_a_solver_robustness_evidence.v1"


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain one JSON object.")
    return value


def _verify(path: Path, digest_key: str) -> dict[str, object]:
    value = _read(path)
    supplied = value.pop(digest_key, None)
    if not isinstance(supplied, str) or supplied != canonical_digest(value):
        raise RuntimeError(f"{path.name} has an invalid {digest_key}.")
    value[digest_key] = supplied
    return value


def _write(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def aggregate_runtime_attribution(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    executed = [value for value in rows if value.get("runs")]
    first_runs = [value["runs"][0] for value in executed]
    route_counts = Counter(
        "|".join(
            (
                str(value["route"].get("candidate_source", "not_available")),
                str(value["route"].get("lane_id", "not_available")),
                str(value["route"].get("external_status", "not_available")),
            )
        )
        for value in first_runs
    )
    counter_totals = Counter()
    internal_lane_counts = Counter()
    external_invocation_count = 0
    for value in first_runs:
        route = value.get("route", {})
        if isinstance(route, Mapping):
            lane_count = route.get("internal_lane_count")
            if isinstance(lane_count, int) and not isinstance(
                lane_count, bool
            ):
                internal_lane_counts[str(lane_count)] += 1
            invocation_count = route.get("external_invocation_count")
            if isinstance(invocation_count, int) and not isinstance(
                invocation_count, bool
            ):
                external_invocation_count += invocation_count
        counters = value.get("counters", {})
        if not isinstance(counters, Mapping):
            continue
        for key, number in counters.items():
            if isinstance(number, int) and not isinstance(number, bool):
                counter_totals[str(key)] += number
    positives = [value for value in rows if value["expected"] == "feasible"]
    negatives = [value for value in rows if value["expected"] == "impossible"]
    return {
        "scheduled_case_count": len(rows),
        "executed_case_count": len(executed),
        "not_executed_case_count": len(rows) - len(executed),
        "route_counts": dict(sorted(route_counts.items())),
        "external_invocation_count_first_run": external_invocation_count,
        "internal_lane_count_distribution_first_run": dict(
            sorted(internal_lane_counts.items())
        ),
        "solver_stop_reason_counts": dict(
            sorted(
                Counter(
                    str(value["stop_reason"]) for value in rows
                ).items()
            )
        ),
        "positive_status_counts": dict(
            sorted(
                Counter(str(value["status"]) for value in positives).items()
            )
        ),
        "negative_status_counts": dict(
            sorted(
                Counter(str(value["status"]) for value in negatives).items()
            )
        ),
        "negative_control_executed_count": sum(
            bool(value.get("runs")) for value in negatives
        ),
        "counter_totals_first_run": dict(sorted(counter_totals.items())),
        "counter_scope": (
            "first run only; top-level solver counters plus lane telemetry"
        ),
    }


def _coverage_summary(value: Mapping[str, object]) -> dict[str, object]:
    return {
        "audit_digest": value["audit_digest"],
        "direct_case_count_with_duplicates": value[
            "direct_case_count_with_duplicates"
        ],
        "unique_project_digest_count": value[
            "unique_project_digest_count"
        ],
        "source_counts": deepcopy(value["source_counts"]),
        "split_counts": deepcopy(value["split_counts"]),
        "family_counts": deepcopy(value["family_counts"]),
        "density_targets": deepcopy(value["density_targets"]),
        "layer_targets": deepcopy(value["layer_targets"]),
        "reservation_modes": deepcopy(value["reservation_modes"]),
        "execution_modes": deepcopy(value["execution_modes"]),
        "change_kinds": deepcopy(value["change_kinds"]),
        "rotation_policies": deepcopy(value["rotation_policies"]),
        "oracle_kinds": deepcopy(value["oracle_kinds"]),
        "flat_item_count_distribution": deepcopy(
            value["flat_item_count_distribution"]
        ),
        "feasible_outer_load_ratio_by_density": deepcopy(
            value["feasible_outer_load_ratio_by_density"]
        ),
        "container_count_range": deepcopy(value["container_count_range"]),
        "content_record_count_range": deepcopy(
            value["content_record_count_range"]
        ),
        "content_quantity_range": deepcopy(value["content_quantity_range"]),
        "flat_item_count_range": deepcopy(value["flat_item_count_range"]),
        "minimum_body_axis_range_mm": deepcopy(
            value["minimum_body_axis_range_mm"]
        ),
        "content_axis_range_mm": deepcopy(value["content_axis_range_mm"]),
        "box_axis_range_mm": deepcopy(value["box_axis_range_mm"]),
        "l06_generator_drift": {
            key: deepcopy(value["l06_generator_drift"][key])
            for key in (
                "case_count",
                "drifted_case_count",
                "changed_field_counts",
                "drifted_by_split",
                "drifted_by_reservation_mode",
            )
        },
        "l07_generator_drift": {
            key: deepcopy(value["l07_generator_drift"][key])
            for key in (
                "case_count",
                "drifted_case_count",
                "changed_field_counts",
                "drifted_by_split",
                "drifted_by_reservation_mode",
            )
        },
        "l08_core_only": deepcopy(value["l08_core_only"]),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--baseline-report", type=Path, required=True)
    parser.add_argument("--baseline-checkpoint", type=Path, required=True)
    parser.add_argument("--downstream-report", type=Path, required=True)
    parser.add_argument("--scip-integration", type=Path, required=True)
    parser.add_argument("--discarded-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    coverage = _verify(args.coverage, "audit_digest")
    baseline = _verify(args.baseline_report, "report_digest")
    checkpoint = _verify(
        args.baseline_checkpoint, "checkpoint_digest"
    )
    downstream = _verify(args.downstream_report, "report_digest")
    scip = _verify(args.scip_integration, "receipt_digest")
    discarded = _verify(args.discarded_report, "report_digest")
    if checkpoint["binding_digest"] != canonical_digest(
        baseline["bindings"]
    ):
        raise RuntimeError("Baseline report and checkpoint bindings differ.")
    if (
        downstream["baseline_report_digest"] != baseline["report_digest"]
        or downstream["baseline_checkpoint_digest"]
        != checkpoint["checkpoint_digest"]
    ):
        raise RuntimeError("Downstream audit is not bound to the baseline.")
    if (
        scip["runtime_artifact_digest"]
        != baseline["candidate"]["runtime_artifact_digest"]
    ):
        raise RuntimeError("SCIP integration and baseline artifacts differ.")

    product_rows = [
        deepcopy(value)
        for _key, value in sorted(
            checkpoint["product_results"].items()
        )
    ]
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-A",
        "date": "2026-07-29",
        "status": "complete",
        "candidate": deepcopy(baseline["candidate"]),
        "bindings": {
            "coverage_audit_digest": coverage["audit_digest"],
            "baseline_report_digest": baseline["report_digest"],
            "baseline_checkpoint_digest": checkpoint[
                "checkpoint_digest"
            ],
            "downstream_report_digest": downstream["report_digest"],
            "scip_integration_receipt_digest": scip["receipt_digest"],
        },
        "coverage": _coverage_summary(coverage),
        "reconstructibility": deepcopy(baseline["inventory"]),
        "execution": deepcopy(baseline["execution"]),
        "product": deepcopy(baseline["summary"]["product"]),
        "runtime_attribution": aggregate_runtime_attribution(product_rows),
        "core_only": deepcopy(baseline["summary"]["core_only"]),
        "downstream": deepcopy(downstream["summary"]),
        "scip_determinism_gate": {
            "python_version": scip["python_version"],
            "repeat_count": scip["repeat_count"],
            "runs_identical": scip["runs_identical"],
            "runtime_artifact_digest": scip["runtime_artifact_digest"],
        },
        "discarded_measurement": {
            "report_digest": discarded["report_digest"],
            "authoritative": False,
            "reasons": [
                "request identity differed between functional replays",
                "finalization did not use the product default normal profile",
            ],
        },
        "preregistered_targets": {
            "new_holdout_positive_case_count": 400,
            "global_certified_minimum": 380,
            "global_certified_rate_minimum": 0.95,
            "common_case_count": 240,
            "common_certified_minimum": 238,
            "common_certified_rate_minimum": 0.991667,
            "false_impossible_maximum": 0,
            "uncertified_solution_maximum": 0,
        },
        "invariants": {
            "r9_v_result_preserved": True,
            "historical_semantic_drift_executed": False,
            "old_holdout_used_as_new_holdout": False,
            "solver_budget_changed": False,
            "physical_value_changed": False,
            "grid_changed": False,
            "epsilon_changed": False,
            "fusion_materialization_invocation_count": 0,
            "fusion_validated": True,
            "print_validated": False,
        },
    }
    evidence["evidence_digest"] = canonical_digest(evidence)
    _write(args.output, evidence)
    print(
        "P64_L09W_A_EVIDENCE_OK "
        f"digest={evidence['evidence_digest']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
