#!/usr/bin/env python3
"""Build the permanent open performance panels for P64-L09W.

The builder consumes only the public manifest and the completed open C
checkpoint. It has no holdout argument or private corpus access.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Callable, Mapping, Sequence, TypeVar


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
    plan_p64_l09w_d_stratified_validation as stratified,
)
from scripts.solver import (  # noqa: E402
    run_p64_l09w_c_reference_campaign as campaign,
)


SCHEMA_VERSION = "bgig.p64_l09w_performance_panels.v1"
SENTINEL_CASE_COUNT = 16
CANDIDATE_CASE_COUNT = 48
SENTINEL_REPETITIONS = 5
CANDIDATE_REPETITIONS = 2

CAUSAL_CASE_IDS = (
    "p64-l09w-discovery-001-55d8459fc2",
    "p64-l09w-tuning-240-ea12ccc81d",
)
DETERMINISM_CASE_ID = "p64-l09w-tuning-360-c8628c8c54"

SENTINEL_CASE_IDS = (
    "p64-l09w-discovery-198-8571c434f9",
    "p64-l09w-discovery-066-df4182ac57",
    "p64-l09w-discovery-191-ec4377484e",
    "p64-l09w-discovery-035-9c38dbce0f",
    "p64-l09w-discovery-201-bdfe0b1cca",
    "p64-l09w-discovery-218-71f60f5cab",
    "p64-l09w-discovery-050-0185c51bad",
    "p64-l09w-discovery-001-55d8459fc2",
    "p64-l09w-tuning-340-780412f833",
    "p64-l09w-tuning-240-ea12ccc81d",
    "p64-l09w-tuning-396-85a80285ef",
    "p64-l09w-tuning-287-6a0b59538e",
    "p64-l09w-tuning-388-a020715e35",
    "p64-l09w-tuning-360-c8628c8c54",
    "p64-l09w-tuning-384-ed4a7a7670",
    "p64-l09w-tuning-300-cf933fb090",
)

FEATURE_AXES = (
    "target_density_pct",
    "box_size",
    "execution",
    "layer_bucket",
    "flat_count",
    "fragmentation_class",
    "aspect_profile",
)

_T = TypeVar("_T")


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


def _first_run(result: Mapping[str, object]) -> Mapping[str, object]:
    runs = result.get("runs")
    if (
        not isinstance(runs, list)
        or not runs
        or not isinstance(runs[0], Mapping)
    ):
        raise RuntimeError("Reference case result has no first run.")
    return runs[0]


def _ready(result: Mapping[str, object]) -> bool:
    run = _first_run(result)
    finalization = run.get("finalization")
    cad_ir = run.get("cad_ir")
    return bool(
        isinstance(finalization, Mapping)
        and finalization.get("status") == "solution_found"
        and isinstance(cad_ir, Mapping)
        and cad_ir.get("status") == "ready_for_fusion"
    )


def _loss_details(result: Mapping[str, object]) -> tuple[str, ...]:
    losses = result.get("losses")
    if not isinstance(losses, list):
        return ()
    return tuple(
        sorted(
            str(value["detail"])
            for value in losses
            if isinstance(value, Mapping) and value.get("detail")
        )
    )


def _reference_row(
    result: Mapping[str, object],
) -> dict[str, object]:
    run = _first_run(result)
    route = run.get("route")
    functional_digests = {
        str(value.get("functional_digest"))
        for value in result.get("runs", [])
        if isinstance(value, Mapping) and value.get("functional_digest")
    }
    return {
        "status": result["status"],
        "deterministic": result.get("deterministic"),
        "ready": _ready(result),
        "placement_digest": run.get("placement_digest"),
        "candidate_source": (
            route.get("candidate_source")
            if isinstance(route, Mapping)
            else None
        ),
        "lane_id": route.get("lane_id") if isinstance(route, Mapping) else None,
        "calculation_ms": run["timings"]["calculation_ms"],
        "functional_digests": sorted(functional_digests),
        "loss_details": list(_loss_details(result)),
    }


def _evenly_spaced(
    values: Sequence[_T],
    count: int,
    *,
    key: Callable[[_T], object],
) -> list[_T]:
    ordered = sorted(values, key=key)
    if count >= len(ordered):
        return ordered
    if count == 1:
        return [ordered[len(ordered) // 2]]
    indices = {
        round(index * (len(ordered) - 1) / (count - 1))
        for index in range(count)
    }
    return [ordered[index] for index in sorted(indices)]


def _coverage_tokens(
    result: Mapping[str, object],
    *,
    timing_bucket: int,
) -> set[tuple[object, ...]]:
    features = dict(result["features"])
    tokens: set[tuple[object, ...]] = {
        ("status", result["status"]),
        ("ready", _ready(result)),
        ("lane", _reference_row(result)["lane_id"]),
        ("timing_bucket", result["stratum"], timing_bucket),
    }
    tokens.update(("loss", value) for value in _loss_details(result))
    for index, left in enumerate(FEATURE_AXES):
        tokens.add(("axis", left, features.get(left)))
        for right in FEATURE_AXES[index + 1 :]:
            tokens.add(
                (
                    "pair",
                    left,
                    features.get(left),
                    right,
                    features.get(right),
                )
            )
    return tokens


def _timing_buckets(
    results: Mapping[str, Mapping[str, object]],
) -> dict[str, int]:
    buckets: dict[str, int] = {}
    for stratum in ("common", "stress"):
        ordered = sorted(
            (
                (case_id, float(_first_run(result)["timings"]["calculation_ms"]))
                for case_id, result in results.items()
                if result["stratum"] == stratum
            ),
            key=lambda value: (value[1], value[0]),
        )
        for rank, (case_id, _elapsed) in enumerate(ordered):
            buckets[case_id] = min(4, rank * 5 // len(ordered))
    return buckets


def _select_candidate_ids(
    results: Mapping[str, Mapping[str, object]],
) -> tuple[str, ...]:
    selected = set(SENTINEL_CASE_IDS)

    for stratum, ready_count, bounded_count in (
        ("common", 5, 3),
        ("stress", 4, 3),
    ):
        available_ready = [
            (case_id, result)
            for case_id, result in results.items()
            if result["stratum"] == stratum
            and _ready(result)
            and case_id not in selected
        ]
        selected.update(
            case_id
            for case_id, _result in _evenly_spaced(
                available_ready,
                ready_count,
                key=lambda value: (
                    float(
                        _first_run(value[1])["timings"]["calculation_ms"]
                    ),
                    value[0],
                ),
            )
        )
        available_bounded = [
            (case_id, result)
            for case_id, result in results.items()
            if result["stratum"] == stratum
            and result["status"] == campaign.RESULT_BOUNDED_UNKNOWN
            and case_id not in selected
        ]
        selected.update(
            case_id
            for case_id, _result in _evenly_spaced(
                available_bounded,
                bounded_count,
                key=lambda value: (
                    float(
                        _first_run(value[1])["timings"]["calculation_ms"]
                    ),
                    value[0],
                ),
            )
        )

    buckets = _timing_buckets(results)
    covered = set()
    for case_id in selected:
        covered.update(
            _coverage_tokens(
                results[case_id],
                timing_bucket=buckets[case_id],
            )
        )

    for stratum in ("common", "stress"):
        target = CANDIDATE_CASE_COUNT // 2
        while sum(
            results[case_id]["stratum"] == stratum for case_id in selected
        ) < target:
            options = []
            for case_id, result in results.items():
                if case_id in selected or result["stratum"] != stratum:
                    continue
                tokens = _coverage_tokens(
                    result,
                    timing_bucket=buckets[case_id],
                )
                reference_ms = float(
                    _first_run(result)["timings"]["calculation_ms"]
                )
                options.append(
                    (
                        len(tokens - covered),
                        -reference_ms,
                        case_id,
                        tokens,
                    )
                )
            if not options:
                raise RuntimeError("Candidate panel selection exhausted.")
            _score, _cost, case_id, tokens = max(options)
            selected.add(case_id)
            covered.update(tokens)

    if len(selected) != CANDIDATE_CASE_COUNT:
        raise RuntimeError("Candidate panel size is not exactly 48.")
    return tuple(
        sorted(
            selected,
            key=lambda case_id: (
                results[case_id]["stratum"],
                float(
                    _first_run(results[case_id])["timings"][
                        "calculation_ms"
                    ]
                ),
                case_id,
            ),
        )
    )


def build_plan(
    manifest: Mapping[str, object],
    reference_checkpoint: Mapping[str, object],
) -> dict[str, object]:
    built = campaign.build_open_inventory(manifest)
    checkpoint = stratified._validated_checkpoint(reference_checkpoint)
    results = {
        str(case_id): stratified._validated_case_result(value)
        for case_id, value in dict(checkpoint["case_results"]).items()
        if isinstance(value, Mapping)
    }
    if len(results) != campaign.OPEN_POSITIVE_COUNT:
        raise RuntimeError("Reference checkpoint must contain 400 open cases.")
    records = {str(value["case_id"]): value for value in built["records"]}
    if set(records) != set(results):
        raise RuntimeError("Manifest and reference checkpoint cases differ.")

    candidate_ids = _select_candidate_ids(results)
    cases = []
    for case_id in candidate_ids:
        result = results[case_id]
        roles = ["candidate"]
        if case_id in SENTINEL_CASE_IDS:
            roles.append("sentinel")
        if case_id in CAUSAL_CASE_IDS:
            roles.append("causal")
        if case_id == DETERMINISM_CASE_ID:
            roles.append("determinism")
        if _ready(result):
            roles.append("ready_non_regression")
        if result["status"] == campaign.RESULT_BOUNDED_UNKNOWN:
            roles.append("bounded_control")
        if stratified.TARGET_LOSS in _loss_details(result):
            roles.append("target_loss")
        cases.append(
            {
                "case_id": case_id,
                "case_digest": records[case_id]["case_digest"],
                "stratum": result["stratum"],
                "roles": sorted(roles),
                "features": deepcopy(dict(result["features"])),
                "reference": _reference_row(result),
            }
        )

    population_axis_values = {
        axis: sorted(
            {
                result["features"][axis]
                for result in results.values()
            },
            key=lambda value: (str(type(value)), str(value)),
        )
        for axis in FEATURE_AXES
    }
    sentinel_cases = [
        value for value in cases if "sentinel" in value["roles"]
    ]
    sentinel_axis_values = {
        axis: sorted(
            {value["features"][axis] for value in sentinel_cases},
            key=lambda value: (str(type(value)), str(value)),
        )
        for axis in FEATURE_AXES
    }
    plan: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-D-P",
        "status": "planned",
        "sources": {
            "manifest_digest": built["inventory"]["manifest_digest"],
            "reference_checkpoint_digest": checkpoint["checkpoint_digest"],
            "reference_code_bundle_digest": checkpoint["binding_payload"][
                "code_bundle_digest"
            ],
        },
        "tiers": {
            "sentinel": {
                "case_count": SENTINEL_CASE_COUNT,
                "repetitions": SENTINEL_REPETITIONS,
                "estimated_reference_calculation_seconds": round(
                    sum(
                        float(value["reference"]["calculation_ms"])
                        for value in sentinel_cases
                    )
                    / 1000.0,
                    3,
                ),
                "purpose": (
                    "permanent_fast_causal_functional_and_performance_gate"
                ),
            },
            "candidate": {
                "case_count": CANDIDATE_CASE_COUNT,
                "repetitions": CANDIDATE_REPETITIONS,
                "estimated_reference_calculation_seconds": round(
                    sum(
                        float(value["reference"]["calculation_ms"])
                        for value in cases
                    )
                    / 1000.0,
                    3,
                ),
                "purpose": "promising_candidate_confirmation",
                "requires_sentinel_pass": True,
            },
            "open_frozen": {
                "case_count": campaign.OPEN_POSITIVE_COUNT,
                "purpose": "global_change_or_frozen_candidate_before_e",
                "requires_candidate_pass": True,
            },
        },
        "selection": {
            "sentinel_case_ids": list(SENTINEL_CASE_IDS),
            "candidate_case_ids": list(candidate_ids),
            "causal_case_ids": list(CAUSAL_CASE_IDS),
            "determinism_case_id": DETERMINISM_CASE_ID,
            "feature_axes": list(FEATURE_AXES),
            "population_axis_values": population_axis_values,
            "sentinel_axis_values": sentinel_axis_values,
            "sample_is_rate_estimator": False,
        },
        "early_stop_rules": [
            "false_impossible",
            "uncertified_solution",
            "selected_product_regression",
            "ready_result_regression",
            "causal_case_failure",
            "new_replay_nondeterminism",
            "checkpoint_or_binding_mismatch",
            "holdout_access_attempt",
        ],
        "cases": cases,
        "invariants": {
            "holdout_file_read": False,
            "holdout_opening_count": 0,
            "holdout_solver_invocation_count": 0,
            "solver_budget_changed": False,
            "product_grid_changed": False,
            "geometry_epsilon_changed": False,
            "physical_value_changed": False,
        },
    }
    plan["plan_digest"] = canonical_digest(plan)
    return validate_plan(plan)


def validate_plan(value: Mapping[str, object]) -> dict[str, object]:
    plan = deepcopy(dict(value))
    supplied = plan.pop("plan_digest", None)
    if (
        plan.get("schema_version") != SCHEMA_VERSION
        or plan.get("status") != "planned"
        or supplied != canonical_digest(plan)
    ):
        raise RuntimeError("Performance panel plan digest is invalid.")
    cases = plan.get("cases")
    if not isinstance(cases, list):
        raise RuntimeError("Performance panel cases are missing.")
    case_ids = [
        str(value.get("case_id"))
        for value in cases
        if isinstance(value, Mapping)
    ]
    sentinel_ids = list(plan["selection"]["sentinel_case_ids"])
    candidate_ids = list(plan["selection"]["candidate_case_ids"])
    if (
        len(case_ids) != CANDIDATE_CASE_COUNT
        or len(set(case_ids)) != CANDIDATE_CASE_COUNT
        or set(case_ids) != set(candidate_ids)
        or len(sentinel_ids) != SENTINEL_CASE_COUNT
        or not set(sentinel_ids).issubset(candidate_ids)
        or plan["selection"]["sentinel_axis_values"]
        != plan["selection"]["population_axis_values"]
        or plan["selection"]["sample_is_rate_estimator"] is not False
        or plan["invariants"]["holdout_file_read"] is not False
        or plan["invariants"]["holdout_opening_count"] != 0
        or plan["invariants"]["holdout_solver_invocation_count"] != 0
    ):
        raise RuntimeError("Performance panel plan contract is invalid.")
    by_id = {
        str(value["case_id"]): value
        for value in cases
        if isinstance(value, Mapping)
    }
    if (
        any(
            "causal" not in by_id[case_id]["roles"]
            for case_id in CAUSAL_CASE_IDS
        )
        or "determinism" not in by_id[DETERMINISM_CASE_ID]["roles"]
        or sum(
            by_id[case_id]["stratum"] == "common"
            for case_id in sentinel_ids
        )
        != SENTINEL_CASE_COUNT // 2
        or sum(
            by_id[case_id]["stratum"] == "common"
            for case_id in candidate_ids
        )
        != CANDIDATE_CASE_COUNT // 2
    ):
        raise RuntimeError("Performance panel balance is invalid.")
    plan["plan_digest"] = supplied
    return plan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--reference-checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    plan = build_plan(
        _read_json(args.manifest),
        _read_json(args.reference_checkpoint),
    )
    _write_json(args.output, plan)
    print(
        "P64_L09W_PERFORMANCE_PANELS_OK "
        f"sentinel={SENTINEL_CASE_COUNT} "
        f"candidate={CANDIDATE_CASE_COUNT} "
        f"digest={plan['plan_digest']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
