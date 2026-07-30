#!/usr/bin/env python3
"""Derive measured sentinel performance thresholds for P64-L09W."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from statistics import NormalDist, median
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
from scripts.solver import run_p64_l09w_performance_panel as runner  # noqa: E402


SCHEMA_VERSION = "bgig.p64_l09w_performance_thresholds.v1"
FAMILY_WISE_ALPHA = 0.01
ROBUST_SIGMA_SCALE = 1.4826


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain one JSON object.")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _validated_report(value: Mapping[str, object]) -> dict[str, object]:
    report = deepcopy(dict(value))
    supplied = report.pop("report_digest", None)
    if (
        report.get("schema_version") != runner.SCHEMA_VERSION
        or supplied != canonical_digest(report)
        or report.get("tier") != "sentinel"
        or report.get("status") != "complete"
        or report.get("decision") != "sentinel_baseline_passed"
        or report["functional"]["hard_gate_failure_count"] != 0
        or report["execution"]["completed_case_count"]
        != panels.SENTINEL_CASE_COUNT
        or report["execution"]["repetitions_per_case"]
        != panels.SENTINEL_REPETITIONS
        or report["invariants"]["holdout_file_read"] is not False
        or report["invariants"]["holdout_opening_count"] != 0
        or report["invariants"]["holdout_solver_invocation_count"] != 0
    ):
        raise RuntimeError("Sentinel baseline report is invalid.")
    report["report_digest"] = supplied
    return report


def _sample_summary(
    samples: Sequence[float],
    *,
    alpha: float,
) -> dict[str, object]:
    values = [float(value) for value in samples]
    center = median(values)
    deviations = [abs(value - center) for value in values]
    mad = median(deviations)
    robust_sigma = ROBUST_SIGMA_SCALE * mad
    z_score = NormalDist().inv_cdf(1.0 - alpha)
    observed_upper_deviation = max(values) - center
    statistical_allowance = z_score * robust_sigma
    allowance = max(
        observed_upper_deviation,
        statistical_allowance,
    )
    upper_limit = center + allowance
    return {
        "sample_count": len(values),
        "samples_ms": values,
        "minimum_ms": min(values),
        "median_ms": center,
        "maximum_ms": max(values),
        "mad_ms": mad,
        "robust_sigma_ms": robust_sigma,
        "alpha": alpha,
        "one_sided_z_score": z_score,
        "observed_upper_deviation_ms": observed_upper_deviation,
        "statistical_allowance_ms": statistical_allowance,
        "selected_allowance_ms": allowance,
        "upper_median_limit_ms": upper_limit,
        "selected_allowance_ratio": (
            allowance / center if center > 0.0 else None
        ),
    }


def _aggregate_samples(
    case_ids: Sequence[str],
    timings: Mapping[str, Mapping[str, object]],
) -> list[float]:
    sample_count = {
        len(timings[case_id]["samples_ms"])
        for case_id in case_ids
    }
    if sample_count != {panels.SENTINEL_REPETITIONS}:
        raise RuntimeError("Sentinel timing samples are incomplete.")
    return [
        sum(
            float(timings[case_id]["samples_ms"][index])
            for case_id in case_ids
        )
        for index in range(panels.SENTINEL_REPETITIONS)
    ]


def build_thresholds(
    plan_value: Mapping[str, object],
    report_value: Mapping[str, object],
) -> dict[str, object]:
    plan = panels.validate_plan(plan_value)
    report = _validated_report(report_value)
    if report["bindings"]["plan_digest"] != plan["plan_digest"]:
        raise RuntimeError("Baseline report and panel plan differ.")

    sentinel_ids = list(plan["selection"]["sentinel_case_ids"])
    plan_cases = {
        str(value["case_id"]): value
        for value in plan["cases"]
        if isinstance(value, Mapping)
    }
    timings = {
        str(case_id): value
        for case_id, value in report["performance"][
            "timings_by_case"
        ].items()
        if isinstance(value, Mapping)
    }
    assessments = {
        str(value["case_id"]): value
        for value in report["functional"]["assessments"]
        if isinstance(value, Mapping)
    }
    if set(timings) != set(sentinel_ids) or set(assessments) != set(
        sentinel_ids
    ):
        raise RuntimeError("Baseline report does not cover all sentinels.")

    case_alpha = FAMILY_WISE_ALPHA / len(sentinel_ids)
    case_thresholds = {}
    for case_id in sentinel_ids:
        assessment = assessments[case_id]
        if (
            assessment["hard_gate_passed"] is not True
            or assessment["selected_product_digest_count"] > 1
        ):
            raise RuntimeError("Sentinel functional identity is unstable.")
        case_thresholds[case_id] = {
            "stratum": plan_cases[case_id]["stratum"],
            "roles": deepcopy(list(plan_cases[case_id]["roles"])),
            "expected_status": plan_cases[case_id]["reference"]["status"],
            "expected_placement_digest": plan_cases[case_id]["reference"][
                "placement_digest"
            ],
            "selected_product_digests": deepcopy(
                list(assessment["selected_product_digests"])
            ),
            "observed_execution_route_variants": deepcopy(
                list(assessment["execution_route_variants"])
            ),
            "observed_execution_trace_digests": deepcopy(
                list(assessment["execution_trace_digests"])
            ),
            "timing": _sample_summary(
                timings[case_id]["samples_ms"],
                alpha=case_alpha,
            ),
        }

    aggregate = {}
    for name, ids in (
        ("overall", sentinel_ids),
        (
            "common",
            [
                case_id
                for case_id in sentinel_ids
                if plan_cases[case_id]["stratum"] == "common"
            ],
        ),
        (
            "stress",
            [
                case_id
                for case_id in sentinel_ids
                if plan_cases[case_id]["stratum"] == "stress"
            ],
        ),
    ):
        aggregate[name] = _sample_summary(
            _aggregate_samples(ids, timings),
            alpha=(
                FAMILY_WISE_ALPHA
                if name == "overall"
                else FAMILY_WISE_ALPHA / 2.0
            ),
        )
        aggregate[name]["case_count"] = len(ids)

    thresholds: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-D-P",
        "status": "frozen",
        "method": {
            "family_wise_alpha": FAMILY_WISE_ALPHA,
            "case_alpha": case_alpha,
            "robust_sigma_scale": ROBUST_SIGMA_SCALE,
            "case_multiplicity_correction": "bonferroni",
            "one_sided_distribution": "standard_normal",
            "allowance_rule": (
                "max_observed_upper_deviation_or_one_sided_robust_bound"
            ),
            "fixed_percentage_margin": None,
        },
        "bindings": {
            "plan_digest": plan["plan_digest"],
            "baseline_report_digest": report["report_digest"],
            "baseline_checkpoint_digest": report["bindings"][
                "checkpoint_digest"
            ],
            "code_bundle_digest": report["bindings"][
                "code_bundle_digest"
            ],
            "runtime_artifact_digest": report["bindings"][
                "runtime_artifact_digest"
            ],
            "runtime_receipt_digest": report["bindings"][
                "runtime_receipt_digest"
            ],
            "seed_checkpoint_digest": report["bindings"].get(
                "seed_checkpoint_digest"
            ),
        },
        "gates": {
            "functional_fail_fast": True,
            "all_case_medians_at_or_below_limits": True,
            "overall_total_median_at_or_below_limit": True,
            "stratum_total_medians_at_or_below_limits": True,
            "execution_route_change_is_functional_failure": False,
            "execution_trace_change_is_functional_failure": False,
            "candidate_48_requires_sentinel_pass": True,
            "candidate_48_is_rate_estimator": False,
            "open_400_requires_candidate_pass": True,
        },
        "case_thresholds": case_thresholds,
        "aggregate_thresholds": aggregate,
        "invariants": {
            "sample_is_rate_estimator": False,
            "holdout_file_read": False,
            "holdout_opening_count": 0,
            "holdout_solver_invocation_count": 0,
        },
    }
    thresholds["thresholds_digest"] = canonical_digest(thresholds)
    return validate_thresholds(thresholds)


def validate_thresholds(
    value: Mapping[str, object],
) -> dict[str, object]:
    thresholds = deepcopy(dict(value))
    supplied = thresholds.pop("thresholds_digest", None)
    if (
        thresholds.get("schema_version") != SCHEMA_VERSION
        or thresholds.get("status") != "frozen"
        or supplied != canonical_digest(thresholds)
        or thresholds["method"]["fixed_percentage_margin"] is not None
        or thresholds["invariants"]["sample_is_rate_estimator"] is not False
        or thresholds["invariants"]["holdout_file_read"] is not False
        or thresholds["invariants"]["holdout_opening_count"] != 0
        or thresholds["invariants"]["holdout_solver_invocation_count"] != 0
        or len(thresholds["case_thresholds"])
        != panels.SENTINEL_CASE_COUNT
    ):
        raise RuntimeError("Performance thresholds are invalid.")
    thresholds["thresholds_digest"] = supplied
    return thresholds


def evaluate_report(
    thresholds_value: Mapping[str, object],
    report_value: Mapping[str, object],
) -> dict[str, object]:
    thresholds = validate_thresholds(thresholds_value)
    report = _validated_report(report_value)
    failures = []
    if (
        report["bindings"]["plan_digest"]
        != thresholds["bindings"]["plan_digest"]
    ):
        failures.append("plan_digest_mismatch")
    timings = report["performance"]["timings_by_case"]
    assessments = {
        str(value["case_id"]): value
        for value in report["functional"]["assessments"]
        if isinstance(value, Mapping)
    }
    for case_id, expected in thresholds["case_thresholds"].items():
        assessment = assessments.get(case_id)
        if not isinstance(assessment, Mapping):
            failures.append(f"missing_assessment:{case_id}")
        elif list(assessment["selected_product_digests"]) != list(
            expected["selected_product_digests"]
        ):
            failures.append(f"selected_product_regression:{case_id}")
        observed = timings.get(case_id)
        if not isinstance(observed, Mapping):
            failures.append(f"missing_case:{case_id}")
            continue
        if (
            float(observed["median_ms"])
            > float(expected["timing"]["upper_median_limit_ms"])
        ):
            failures.append(f"case_median_regression:{case_id}")
    plan_case_ids = list(thresholds["case_thresholds"])
    observed_aggregate = {
        "overall": _aggregate_samples(plan_case_ids, timings)
    }
    for stratum in ("common", "stress"):
        observed_aggregate[stratum] = _aggregate_samples(
            [
                case_id
                for case_id, value in thresholds[
                    "case_thresholds"
                ].items()
                if value["stratum"] == stratum
            ],
            timings,
        )
    for name, samples in observed_aggregate.items():
        if median(samples) > float(
            thresholds["aggregate_thresholds"][name][
                "upper_median_limit_ms"
            ]
        ):
            failures.append(f"aggregate_median_regression:{name}")
    return {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "thresholds_digest": thresholds["thresholds_digest"],
        "report_digest": report["report_digest"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--baseline-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    thresholds = build_thresholds(
        _read_json(args.plan),
        _read_json(args.baseline_report),
    )
    _write_json(args.output, thresholds)
    print(
        "P64_L09W_PERFORMANCE_THRESHOLDS_OK "
        f"cases={len(thresholds['case_thresholds'])} "
        f"digest={thresholds['thresholds_digest']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
