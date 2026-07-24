"""Tournoi reproductible P64-L08F sur les cas limites 3D BGIG."""

from __future__ import annotations

from copy import deepcopy
from math import ceil
from statistics import median
from typing import Mapping, Sequence

from .incremental_project_state import canonical_digest
from .real_3d_solver_adapters import (
    STATUS_BOUNDED_UNKNOWN,
    STATUS_CERTIFICATE_REJECTED,
    STATUS_EXTERNAL_ERROR,
    STATUS_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND,
    STATUS_UNSUPPORTED,
)
from .real_3d_solver_corpus import (
    FAMILIES,
    materialize_case_problem,
    validate_case_record,
)


REAL_3D_SELECTION_SCHEMA_V1 = "bgig.real_3d_tournament_selection.v1"
REAL_3D_OPEN_CAMPAIGN_SCHEMA_V1 = "bgig.real_3d_open_tournament.v1"
REAL_3D_HOLDOUT_CAMPAIGN_SCHEMA_V1 = "bgig.real_3d_holdout_tournament.v1"
REAL_3D_EVIDENCE_SCHEMA_V1 = "bgig.real_3d_tournament_evidence.v1"
REAL_3D_OPENING_RECEIPT_SCHEMA_V1 = "bgig.real_3d_holdout_opening_receipt.v1"

EXTERNAL_CANDIDATE_IDS = (
    "ortools_cp_sat",
    "scip",
    "packingsolver_box",
    "laff",
)
PRODUCT_GATE_BY_CANDIDATE = {
    "ortools_cp_sat": "product_eligible_apache_2_0",
    "scip": "benchmark_only_pending_native_notices",
    "packingsolver_box": "benchmark_only_pending_redistribution_review",
    "laff": "benchmark_only_pending_epl_edl_review",
}
_FAILURE_STATUSES = {STATUS_CERTIFICATE_REJECTED, STATUS_EXTERNAL_ERROR}


class Real3DTournamentError(ValueError):
    """Configuration, scellement ou resultat de tournoi invalide."""


def materialize_tournament_problem(
    record: Mapping[str, object],
) -> dict[str, object] | None:
    """Traduit un record ouvert/holdout sans transmettre son temoin positif."""

    accepted = validate_case_record(record)
    problem = materialize_case_problem(accepted)
    if problem.get("input_kind") == "reviewed_bgig_project_reference":
        return None
    payload = deepcopy(problem)
    payload["case_id"] = accepted["case_id"]
    payload["case_digest"] = accepted["case_digest"]
    payload["source_problem_digest"] = accepted["problem_digest"]
    if accepted["expected"] == "infeasible":
        payload = _apply_formal_negative_control(payload, accepted)
    payload.pop("expected", None)
    payload.pop("formal_negative_bound", None)
    payload["problem_digest"] = canonical_digest(payload)
    return payload


def build_result_row(
    record: Mapping[str, object],
    *,
    candidate_id: str,
    report: Mapping[str, object],
    stage: str,
    trial_id: str,
) -> dict[str, object]:
    accepted = validate_case_record(record)
    status = str(report.get("status", ""))
    expected = str(accepted["expected"])
    row = {
        "candidate_id": candidate_id,
        "case_id": accepted["case_id"],
        "case_digest": accepted["case_digest"],
        "family": accepted["family"],
        "tier": accepted["tier"],
        "expected": expected,
        "stage": stage,
        "trial_id": trial_id,
        "status": status,
        "truth_pass": truth_matches(expected, status),
        "representable": status != STATUS_UNSUPPORTED,
        "candidate_failure": status in _FAILURE_STATUSES,
        "certified": (
            isinstance(report.get("recertification"), Mapping)
            and report["recertification"].get("certified") is True
        ),
        "worker_invocation_count": int(report.get("worker_invocation_count", 0)),
        "unsupported_constraints": list(report.get("unsupported_constraints", [])),
        "quality": deepcopy(dict(report.get("quality", {}))),
        "execution": _compact_execution(report.get("execution")),
        "report_digest": report.get("report_digest"),
    }
    row["row_digest"] = canonical_digest(row)
    return row


def summarize_rows(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    by_candidate: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        by_candidate.setdefault(str(row["candidate_id"]), []).append(row)
    candidates = []
    for candidate_id in sorted(by_candidate):
        values = by_candidate[candidate_id]
        walls = [_wall_seconds(value) for value in values]
        statuses: dict[str, int] = {}
        for value in values:
            status = str(value["status"])
            statuses[status] = statuses.get(status, 0) + 1
        candidate = {
            "candidate_id": candidate_id,
            "case_count": len(values),
            "representable_count": sum(bool(value["representable"]) for value in values),
            "worker_invocation_count": sum(
                int(value["worker_invocation_count"]) for value in values
            ),
            "truth_pass_count": sum(bool(value["truth_pass"]) for value in values),
            "certified_solution_count": sum(bool(value["certified"]) for value in values),
            "candidate_failure_count": sum(bool(value["candidate_failure"]) for value in values),
            "statuses": dict(sorted(statuses.items())),
            "total_wall_seconds": round(sum(walls), 6),
            "p50_wall_seconds": round(median(walls), 6) if walls else 0.0,
            "p95_wall_seconds": round(_percentile(walls, 0.95), 6) if walls else 0.0,
        }
        candidate["summary_digest"] = canonical_digest(candidate)
        candidates.append(candidate)
    summary = {
        "row_count": len(rows),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    summary["summary_digest"] = canonical_digest(summary)
    return summary


def build_selection_evidence(
    *,
    open_rows: Sequence[Mapping[str, object]],
    baseline_rows: Sequence[Mapping[str, object]],
    config_digest: str,
    manifest_digest: str,
    artifact_bundle_digest: str,
    code_bundle_digest: str,
    holdout_limits: Mapping[str, object],
    maximum_complements: int = 2,
) -> dict[str, object]:
    """Scelle trials, moteur principal et routage avant le holdout."""

    external_rows = [
        dict(value) for value in open_rows if str(value["candidate_id"]) in EXTERNAL_CANDIDATE_IDS
    ]
    if {str(value["candidate_id"]) for value in external_rows} != set(EXTERNAL_CANDIDATE_IDS):
        raise Real3DTournamentError("Four external engines must be present before sealing.")
    selected_trial_by_candidate = _select_tuning_trials(external_rows)
    selected_rows = _selected_open_rows(external_rows, selected_trial_by_candidate)
    family_metrics = _family_metrics(selected_rows)
    primary = _select_primary(family_metrics)
    family_winners = {family: _select_family_winner(family_metrics, family) for family in FAMILIES}
    complements: list[str] = []
    family_routes: dict[str, str] = {}
    for family in FAMILIES:
        winner = family_winners[family]
        if (
            winner != primary
            and _family_rank(family_metrics[winner][family])
            > _family_rank(family_metrics[primary][family])
            and winner not in complements
            and len(complements) < maximum_complements
        ):
            complements.append(winner)
        family_routes[family] = winner if winner in complements else primary
    selected_ids = [primary, *complements]
    comparison = compare_result_sets(_route_rows(selected_rows, family_routes), baseline_rows)
    full_coverage = all(
        family_metrics[primary][family]["semantically_complete"] for family in FAMILIES
    )
    payload = {
        "schema_version": REAL_3D_SELECTION_SCHEMA_V1,
        "config_digest": config_digest,
        "manifest_digest": manifest_digest,
        "artifact_bundle_digest": artifact_bundle_digest,
        "code_bundle_digest": code_bundle_digest,
        "external_candidate_ids": list(EXTERNAL_CANDIDATE_IDS),
        "external_candidate_count": len(EXTERNAL_CANDIDATE_IDS),
        "external_family_count": len(EXTERNAL_CANDIDATE_IDS),
        "selected_trial_by_candidate": selected_trial_by_candidate,
        "primary_candidate_id": primary,
        "selected_candidate_ids": selected_ids,
        "complement_candidate_ids": complements,
        "family_routes": family_routes,
        "family_winners": family_winners,
        "family_metrics": family_metrics,
        "holdout_limits": deepcopy(dict(holdout_limits)),
        "open_portfolio_vs_current_bgig": comparison,
        "selection_decision": (
            "sealed_full_coverage_candidate"
            if full_coverage
            else "sealed_negative_no_full_coverage_candidate"
        ),
        "primary_full_semantic_coverage": full_coverage,
        "product_gate_by_selected_candidate": {
            candidate_id: PRODUCT_GATE_BY_CANDIDATE[candidate_id] for candidate_id in selected_ids
        },
        "post_selection_tuning_allowed": False,
        "holdout_opened": False,
    }
    payload["selection_digest"] = canonical_digest(payload)
    return payload


def validate_selection_evidence(value: Mapping[str, object]) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop("selection_digest", None)
    if (
        payload.get("schema_version") != REAL_3D_SELECTION_SCHEMA_V1
        or supplied != canonical_digest(payload)
        or payload.get("post_selection_tuning_allowed") is not False
        or payload.get("holdout_opened") is not False
        or payload.get("external_candidate_count") < 3
        or payload.get("external_family_count") < 3
    ):
        raise Real3DTournamentError("Invalid sealed real-3D selection evidence.")
    selected = payload.get("selected_candidate_ids")
    if (
        not isinstance(selected, list)
        or not selected
        or payload.get("primary_candidate_id") != selected[0]
        or any(item not in EXTERNAL_CANDIDATE_IDS for item in selected)
    ):
        raise Real3DTournamentError("Invalid selected external engine set.")
    payload["selection_digest"] = supplied
    return payload


def sanitize_oracle_leaked_baseline_rows(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Retire uniquement les vérités obtenues par lecture d'une borne de corpus."""

    sanitized = []
    for value in rows:
        row = deepcopy(dict(value))
        if (
            row.get("candidate_id") == "current_bgig"
            and row.get("expected") == "infeasible"
            and row.get("status") == STATUS_INFEASIBLE_PROVEN
        ):
            original_status = row["status"]
            row["status"] = STATUS_BOUNDED_UNKNOWN
            row["truth_pass"] = False
            row["certified"] = False
            row["recovery"] = {
                "reason": "benchmark_oracle_metadata_leak",
                "original_status": original_status,
            }
            row.pop("row_digest", None)
            row["row_digest"] = canonical_digest(row)
        sanitized.append(row)
    return sanitized


def build_holdout_decision(
    *,
    portfolio_rows: Sequence[Mapping[str, object]],
    primary_rows: Sequence[Mapping[str, object]],
    baseline_rows: Sequence[Mapping[str, object]],
    selected_candidate_ids: Sequence[str],
    primary_candidate_id: str,
) -> dict[str, object]:
    """Applique la règle préenregistrée : portefeuille sinon meilleur moteur seul."""

    portfolio_vs_primary = compare_result_sets(portfolio_rows, primary_rows)
    portfolio_beats_primary = bool(
        portfolio_vs_primary["no_functional_loss"]
        and (
            portfolio_vs_primary["functional_gain_demonstrated"]
            or portfolio_vs_primary["quality_gain_demonstrated"]
        )
    )
    if portfolio_beats_primary:
        retained_rows = [deepcopy(dict(value)) for value in portfolio_rows]
        retained_ids = list(selected_candidate_ids)
    else:
        retained_rows = [deepcopy(dict(value)) for value in primary_rows]
        retained_ids = [primary_candidate_id]
    retained_vs_baseline = compare_result_sets(retained_rows, baseline_rows)
    retained_product_ready = all(
        PRODUCT_GATE_BY_CANDIDATE[str(candidate_id)].startswith("product_eligible")
        for candidate_id in retained_ids
    )
    demonstrated_gain = bool(
        retained_vs_baseline["no_functional_loss"]
        and (
            retained_vs_baseline["functional_gain_demonstrated"]
            or retained_vs_baseline["quality_gain_demonstrated"]
        )
    )
    verdict = {
        "benchmark_winner_demonstrated": demonstrated_gain,
        "portfolio_beats_primary": portfolio_beats_primary,
        "retained_candidate_ids": retained_ids,
        "retained_product_redistribution_ready": retained_product_ready,
        "product_integration_authorized": demonstrated_gain and retained_product_ready,
        "decision": (
            "winner_ready_for_l08g"
            if demonstrated_gain and retained_product_ready
            else "negative_no_product_integrable_winner"
        ),
    }
    verdict["verdict_digest"] = canonical_digest(verdict)
    return {
        "portfolio_vs_primary": portfolio_vs_primary,
        "retained_rows": retained_rows,
        "retained_vs_current_bgig": retained_vs_baseline,
        "verdict": verdict,
    }


def compare_result_sets(
    first_rows: Sequence[Mapping[str, object]],
    second_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    first = {str(value["case_id"]): value for value in first_rows}
    second = {str(value["case_id"]): value for value in second_rows}
    common = sorted(set(first) & set(second))
    first_losses = 0
    first_gains = 0
    quality_wins = 0
    quality_losses = 0
    details = []
    for case_id in common:
        left = first[case_id]
        right = second[case_id]
        left_ok = bool(left["truth_pass"])
        right_ok = bool(right["truth_pass"])
        first_gains += int(left_ok and not right_ok)
        first_losses += int(right_ok and not left_ok)
        relation = "not_comparable"
        left_quality = quality_axes(left)
        right_quality = quality_axes(right)
        if left_quality is not None and right_quality is not None:
            if left_quality < right_quality:
                quality_wins += 1
                relation = "first_better"
            elif right_quality < left_quality:
                quality_losses += 1
                relation = "second_better"
            else:
                relation = "tie"
        details.append(
            {
                "case_id": case_id,
                "first_status": left["status"],
                "second_status": right["status"],
                "quality_relation": relation,
            }
        )
    result = {
        "common_case_count": len(common),
        "first_truth_gain_count": first_gains,
        "first_truth_loss_count": first_losses,
        "quality_win_count": quality_wins,
        "quality_loss_count": quality_losses,
        "first_total_wall_seconds": round(sum(_wall_seconds(value) for value in first.values()), 6),
        "second_total_wall_seconds": round(
            sum(_wall_seconds(value) for value in second.values()), 6
        ),
        "no_functional_loss": first_losses == 0,
        "functional_gain_demonstrated": first_gains > 0,
        "quality_gain_demonstrated": quality_wins > quality_losses,
        "details": details,
    }
    result["comparison_digest"] = canonical_digest(result)
    return result


def quality_axes(row: Mapping[str, object]) -> tuple[int, int, int, int] | None:
    quality = row.get("quality")
    if not row.get("certified") or not isinstance(quality, Mapping):
        return None
    required = (
        "max_top_mm",
        "bounding_envelope_volume_mm3",
        "max_rear_mm",
        "max_right_mm",
    )
    if any(not isinstance(quality.get(field), int) for field in required):
        return None
    return tuple(int(quality[field]) for field in required)


def truth_matches(expected: str, status: str) -> bool:
    if expected == "feasible":
        return status == STATUS_SOLUTION_FOUND
    if expected == "infeasible":
        return status == STATUS_INFEASIBLE_PROVEN
    if expected == "bounded_unknown":
        return status not in {STATUS_INFEASIBLE_PROVEN, STATUS_SOLUTION_FOUND}
    return False


def _apply_formal_negative_control(
    problem: dict[str, object], record: Mapping[str, object]
) -> dict[str, object]:
    family = str(record["family"])
    participants = problem["participants"]
    first = participants[0]
    world = problem["world_mm"]
    if family == "access":
        first_id = str(participants[0]["participant_id"])
        second_id = str(participants[1]["participant_id"])
        problem["access_precedence_edges"] = [
            [first_id, second_id],
            [second_id, first_id],
        ]
        return problem
    if family == "support":
        first["ground_allowed"] = False
        first["required_support_area_mm2"] = int(world[0]) * int(world[1]) * len(participants) + 1
        return problem
    if family == "reservations":
        size = [int(world[0]), int(world[1]), int(world[2])]
    elif family == "fragmentation":
        size = [
            int(problem["fragment_cell_mm"][0]) + 1,
            1,
            1,
        ]
    elif family == "layers":
        size = [1, 1, int(world[2]) + 1]
    else:
        size = [int(world[0]) + 1, 1, 1]
    for variant in first["variants"]:
        variant["size"] = list(size)
    return problem


def _select_tuning_trials(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, str]:
    selected = {}
    for candidate_id in EXTERNAL_CANDIDATE_IDS:
        trials = sorted(
            {
                str(value["trial_id"])
                for value in rows
                if value["candidate_id"] == candidate_id and value["stage"] == "tuning"
            }
        )
        if not trials:
            raise Real3DTournamentError(f"Missing tuning trials for {candidate_id}.")
        selected[candidate_id] = max(
            trials,
            key=lambda trial_id: _rows_rank(
                [
                    value
                    for value in rows
                    if value["candidate_id"] == candidate_id
                    and value["stage"] == "tuning"
                    and value["trial_id"] == trial_id
                ]
            ),
        )
    return selected


def _selected_open_rows(
    rows: Sequence[Mapping[str, object]],
    selected_trials: Mapping[str, str],
) -> list[dict[str, object]]:
    return [
        dict(value)
        for value in rows
        if value["stage"] == "discovery"
        or (
            value["stage"] == "tuning"
            and value["trial_id"] == selected_trials[str(value["candidate_id"])]
        )
    ]


def _family_metrics(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, dict[str, object]]]:
    result: dict[str, dict[str, dict[str, object]]] = {}
    for candidate_id in EXTERNAL_CANDIDATE_IDS:
        result[candidate_id] = {}
        for family in FAMILIES:
            values = [
                value
                for value in rows
                if value["candidate_id"] == candidate_id and value["family"] == family
            ]
            metric = {
                "case_count": len(values),
                "representable_count": sum(bool(value["representable"]) for value in values),
                "truth_pass_count": sum(bool(value["truth_pass"]) for value in values),
                "certified_solution_count": sum(bool(value["certified"]) for value in values),
                "candidate_failure_count": sum(
                    bool(value["candidate_failure"]) for value in values
                ),
                "total_wall_seconds": round(sum(_wall_seconds(value) for value in values), 6),
            }
            metric["semantically_complete"] = bool(
                len(values) == 4
                and metric["representable_count"] == len(values)
                and metric["candidate_failure_count"] == 0
            )
            metric["metric_digest"] = canonical_digest(metric)
            result[candidate_id][family] = metric
    return result


def _select_primary(
    metrics: Mapping[str, Mapping[str, Mapping[str, object]]],
) -> str:
    return max(
        EXTERNAL_CANDIDATE_IDS,
        key=lambda candidate_id: (
            sum(
                bool(metrics[candidate_id][family]["semantically_complete"]) for family in FAMILIES
            ),
            sum(int(metrics[candidate_id][family]["truth_pass_count"]) for family in FAMILIES),
            sum(
                int(metrics[candidate_id][family]["certified_solution_count"])
                for family in FAMILIES
            ),
            -sum(float(metrics[candidate_id][family]["total_wall_seconds"]) for family in FAMILIES),
            candidate_id,
        ),
    )


def _select_family_winner(
    metrics: Mapping[str, Mapping[str, Mapping[str, object]]], family: str
) -> str:
    return max(
        EXTERNAL_CANDIDATE_IDS,
        key=lambda candidate_id: (_family_rank(metrics[candidate_id][family]), candidate_id),
    )


def _family_rank(metric: Mapping[str, object]) -> tuple[object, ...]:
    return (
        bool(metric["semantically_complete"]),
        int(metric["truth_pass_count"]),
        int(metric["certified_solution_count"]),
        -int(metric["candidate_failure_count"]),
        -float(metric["total_wall_seconds"]),
    )


def _rows_rank(rows: Sequence[Mapping[str, object]]) -> tuple[object, ...]:
    return (
        sum(bool(value["truth_pass"]) for value in rows),
        sum(bool(value["certified"]) for value in rows),
        -sum(bool(value["candidate_failure"]) for value in rows),
        -sum(_wall_seconds(value) for value in rows),
    )


def _route_rows(
    rows: Sequence[Mapping[str, object]], routes: Mapping[str, str]
) -> list[dict[str, object]]:
    selected = []
    for family in FAMILIES:
        candidate_id = routes[family]
        selected.extend(
            dict(value)
            for value in rows
            if value["family"] == family and value["candidate_id"] == candidate_id
        )
    return selected


def _compact_execution(value: object) -> dict[str, object]:
    execution = dict(value) if isinstance(value, Mapping) else {}
    return {
        key: execution.get(key)
        for key in (
            "execution_status",
            "exit_code",
            "total_wall_seconds",
            "cpu_seconds",
            "peak_working_set_bytes",
            "input_digest",
        )
    }


def _wall_seconds(row: Mapping[str, object]) -> float:
    execution = row.get("execution")
    if not isinstance(execution, Mapping):
        return 0.0
    value = execution.get("total_wall_seconds")
    return float(value) if isinstance(value, (int, float)) else 0.0


def _percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, ceil(len(ordered) * quantile) - 1))]
