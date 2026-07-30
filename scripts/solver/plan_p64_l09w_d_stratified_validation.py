#!/usr/bin/env python3
"""Construit le plan ouvert et stratifié de validation P64-L09W-D.

Ce plan ne lit que les checkpoints ouverts C et D. Il ne possède aucun argument
de holdout et n'exécute aucun solveur.
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
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)


SCHEMA_VERSION = "bgig.p64_l09w_d_stratified_validation_plan.v1"
TARGET_LOSS = "xy_composite_residual_owner_not_found"
CAUSAL_CASE_IDS = (
    "p64-l09w-discovery-001-55d8459fc2",
    "p64-l09w-tuning-240-ea12ccc81d",
)
SAMPLE_AXES = (
    "target_density_pct",
    "box_size",
    "execution",
    "layer_bucket",
    "flat_count",
    "fragmentation_class",
    "aspect_profile",
)
TIMING_QUANTILES = (0.10, 0.50, 0.90)
MINIMUM_SAMPLE_SIZE_PER_STRATUM = 8
REFERENCE_RUNNER = (
    ROOT / "scripts/solver/run_p64_l09w_c_reference_campaign.py"
)


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


def _current_candidate_code_bundle_digest() -> str:
    digest = sha256()
    paths = [
        *sorted((ROOT / "src/board_game_insert_generator").glob("*.py")),
        REFERENCE_RUNNER,
    ]
    for path in paths:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _validated_checkpoint(
    value: Mapping[str, object],
) -> dict[str, object]:
    checkpoint = deepcopy(dict(value))
    supplied = checkpoint.pop("checkpoint_digest", None)
    if (
        not isinstance(supplied, str)
        or supplied != canonical_digest(checkpoint)
        or checkpoint.get("active_case_id") is not None
        or not isinstance(checkpoint.get("case_results"), dict)
        or not isinstance(checkpoint.get("binding_payload"), dict)
    ):
        raise RuntimeError("Open campaign checkpoint is invalid or active.")
    checkpoint["checkpoint_digest"] = supplied
    return checkpoint


def _validated_case_result(
    value: Mapping[str, object],
) -> dict[str, object]:
    result = deepcopy(dict(value))
    supplied = result.pop("case_result_digest", None)
    if not isinstance(supplied, str) or supplied != canonical_digest(result):
        raise RuntimeError("Open campaign case result is invalid.")
    result["case_result_digest"] = supplied
    return result


def _first_run(result: Mapping[str, object]) -> Mapping[str, object]:
    runs = result.get("runs")
    if (
        not isinstance(runs, list)
        or not runs
        or not isinstance(runs[0], Mapping)
    ):
        raise RuntimeError("Open campaign case has no first run.")
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
            and loss.get("detail") == TARGET_LOSS
            for loss in losses
        )
    )


def _calculation_ms(result: Mapping[str, object]) -> float:
    run = _first_run(result)
    timings = run.get("timings")
    if not isinstance(timings, Mapping):
        raise RuntimeError("Open campaign case has no timings.")
    value = timings.get("calculation_ms")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RuntimeError("Open campaign calculation time is invalid.")
    return float(value)


def _case_categories(
    result: Mapping[str, object],
) -> set[tuple[str, object]]:
    features = result.get("features")
    if not isinstance(features, Mapping):
        raise RuntimeError("Open campaign case has no features.")
    return {(axis, features.get(axis)) for axis in SAMPLE_AXES}


def select_stratified_target_cases(
    results: Mapping[str, Mapping[str, object]],
    *,
    stratum: str,
) -> list[str]:
    population = [
        case_id
        for case_id, result in sorted(results.items())
        if result.get("stratum") == stratum and _has_target_loss(result)
    ]
    if not population:
        raise RuntimeError(f"No target-loss case exists for {stratum}.")
    frequencies = Counter(
        category
        for case_id in population
        for category in _case_categories(results[case_id])
    )
    missing = set(frequencies)
    selected = [
        case_id for case_id in CAUSAL_CASE_IDS if case_id in population
    ]
    for case_id in selected:
        missing -= _case_categories(results[case_id])

    while missing:
        candidates = [
            case_id for case_id in population if case_id not in selected
        ]
        if not candidates:
            raise RuntimeError(f"Cannot cover every {stratum} category.")

        def score(case_id: str) -> tuple[float, int, str]:
            new_categories = _case_categories(results[case_id]) & missing
            rarity = sum(
                1.0 / frequencies[category]
                for category in new_categories
            )
            return (rarity, len(new_categories), case_id)

        candidate = max(candidates, key=score)
        selected.append(candidate)
        missing -= _case_categories(results[candidate])

    remaining = sorted(
        (case_id for case_id in population if case_id not in selected),
        key=lambda case_id: (_calculation_ms(results[case_id]), case_id),
    )
    for quantile in TIMING_QUANTILES:
        if not remaining:
            break
        index = round(quantile * (len(remaining) - 1))
        selected.append(remaining.pop(index))
    while len(selected) < MINIMUM_SAMPLE_SIZE_PER_STRATUM:
        if not remaining:
            break
        index = round(0.50 * (len(remaining) - 1))
        selected.append(remaining.pop(index))
    return selected


def build_plan(
    reference_checkpoint: Mapping[str, object],
    candidate_checkpoint: Mapping[str, object],
) -> dict[str, object]:
    reference = _validated_checkpoint(reference_checkpoint)
    candidate = _validated_checkpoint(candidate_checkpoint)
    reference_results = {
        str(case_id): _validated_case_result(value)
        for case_id, value in dict(reference["case_results"]).items()
        if isinstance(value, Mapping)
    }
    candidate_results = {
        str(case_id): _validated_case_result(value)
        for case_id, value in dict(candidate["case_results"]).items()
        if isinstance(value, Mapping)
    }
    if len(reference_results) != 400:
        raise RuntimeError("Reference checkpoint must contain 400 open cases.")
    if not set(candidate_results).issubset(reference_results):
        raise RuntimeError("Candidate checkpoint contains an unknown case.")
    if (
        reference["binding_payload"].get("manifest_digest")
        != candidate["binding_payload"].get("manifest_digest")
        or reference["binding_payload"].get("runtime_artifact_digest")
        != candidate["binding_payload"].get("runtime_artifact_digest")
        or reference["binding_payload"].get("runtime_receipt_digest")
        != candidate["binding_payload"].get("runtime_receipt_digest")
        or candidate["binding_payload"].get("repeat_count") != 2
    ):
        raise RuntimeError("Reference and candidate checkpoints are incompatible.")
    current_code_bundle_digest = _current_candidate_code_bundle_digest()
    if (
        candidate["binding_payload"].get("code_bundle_digest")
        != current_code_bundle_digest
    ):
        raise RuntimeError("Candidate code bundle no longer matches checkpoint.")

    ready_ids = sorted(
        case_id
        for case_id, result in reference_results.items()
        if _is_ready(result)
    )
    target_ids = sorted(
        case_id
        for case_id, result in reference_results.items()
        if _has_target_loss(result)
    )
    target_sample = {
        stratum: select_stratified_target_cases(
            reference_results,
            stratum=stratum,
        )
        for stratum in ("common", "stress")
    }
    sampled_ids = set().union(*target_sample.values())
    if not set(CAUSAL_CASE_IDS).issubset(sampled_ids):
        raise RuntimeError("Both causal cases must be in the target sample.")

    tiers_by_case: dict[str, set[str]] = {}
    for case_id in CAUSAL_CASE_IDS:
        tiers_by_case.setdefault(case_id, set()).add("causal")
    for case_id in ready_ids:
        tiers_by_case.setdefault(case_id, set()).add("ready_non_regression")
    for case_id in sampled_ids:
        tiers_by_case.setdefault(case_id, set()).add("target_stratified")

    schedule = []
    for case_id, tiers in sorted(tiers_by_case.items()):
        already_completed = case_id in candidate_results
        required_repeats = (
            0
            if already_completed
            else 2
            if "target_stratified" in tiers
            else 1
        )
        schedule.append(
            {
                "case_id": case_id,
                "stratum": reference_results[case_id]["stratum"],
                "tiers": sorted(tiers),
                "already_completed": already_completed,
                "required_repeats": required_repeats,
                "reference_calculation_ms": _calculation_ms(
                    reference_results[case_id]
                ),
            }
        )

    new_rows = [row for row in schedule if not row["already_completed"]]
    estimated_ms = sum(
        float(row["reference_calculation_ms"])
        * int(row["required_repeats"])
        for row in new_rows
    )
    plan: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-D",
        "status": "planned",
        "sources": {
            "reference_checkpoint_digest": reference["checkpoint_digest"],
            "candidate_checkpoint_digest": candidate["checkpoint_digest"],
            "manifest_digest": reference["binding_payload"]["manifest_digest"],
            "candidate_code_bundle_digest": candidate["binding_payload"][
                "code_bundle_digest"
            ],
            "current_code_bundle_digest": current_code_bundle_digest,
        },
        "population": {
            "open_case_count": len(reference_results),
            "candidate_completed_case_count": len(candidate_results),
            "reference_ready_case_count": len(ready_ids),
            "target_loss_case_count": len(target_ids),
            "remaining_full_replay_case_count": (
                len(reference_results) - len(candidate_results)
            ),
        },
        "selection": {
            "causal_case_ids": list(CAUSAL_CASE_IDS),
            "ready_non_regression_case_ids": ready_ids,
            "target_stratified_case_ids": target_sample,
            "sample_axes": list(SAMPLE_AXES),
            "timing_quantiles": list(TIMING_QUANTILES),
            "sample_is_rate_estimator": False,
        },
        "execution": {
            "new_case_count": len(new_rows),
            "new_replay_count": sum(
                int(row["required_repeats"]) for row in new_rows
            ),
            "estimated_reference_calculation_seconds": round(
                estimated_ms / 1000.0,
                3,
            ),
            "holdout_file_read": False,
            "holdout_opening_count": 0,
            "holdout_solver_invocation_count": 0,
        },
        "early_stop_rules": [
            "causal_case_failure",
            "ready_result_regression",
            "false_impossible",
            "uncertified_solution",
            "candidate_error",
            "target_replay_nondeterminism",
            "checkpoint_or_binding_mismatch",
            "holdout_access_attempt",
        ],
        "schedule": schedule,
    }
    plan["plan_digest"] = canonical_digest(plan)
    return plan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-checkpoint", type=Path, required=True)
    parser.add_argument("--candidate-checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    plan = build_plan(
        _read_json(args.reference_checkpoint),
        _read_json(args.candidate_checkpoint),
    )
    _write_json_atomic(args.output, plan)
    print(
        "P64_L09W_D_STRATIFIED_PLAN_OK "
        f"new_cases={plan['execution']['new_case_count']} "
        f"new_replays={plan['execution']['new_replay_count']} "
        f"plan={plan['plan_digest']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
