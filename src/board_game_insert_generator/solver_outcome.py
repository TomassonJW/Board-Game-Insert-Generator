"""Additive, truthful result and telemetry projection for the P64 baseline.

The stage solver remains heuristic.  This module deliberately describes what it
did without changing its search order, budgets, scoring, or placement choices.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any


SOLVER_RESULT_SCHEMA_V1 = "bgig.solver_result.v1"
SOLVER_TELEMETRY_SCHEMA_V1 = "bgig.solver_telemetry.v1"

SOLUTION_FOUND = "solution_found"
NO_SOLUTION_WITHIN_BUDGET = "no_solution_within_budget"
PROVEN_IMPOSSIBLE = "proven_impossible"
INVALID_INPUT = "invalid_input"
STALE_OR_CANCELLED = "stale_or_cancelled"

_LABELS = {
    SOLUTION_FOUND: "Solution trouvée",
    NO_SOLUTION_WITHIN_BUDGET: "Aucune solution trouvée dans le budget",
    PROVEN_IMPOSSIBLE: "Impossible prouvé",
    INVALID_INPUT: "Projet à corriger",
    STALE_OR_CANCELLED: "Réponse obsolète ou annulée",
}

_INPUT_DIAGNOSTIC_CODES = {
    "NO_CONTAINER_GROUP",
    "CONTAINER_SET_INCOMPLETE",
    "CONTAINER_MINIMUM_BLOCKED",
    "EXPLICIT_COMPLEMENT_NEEDS_EXACT_SIZE",
    "NO_PARTICIPANT",
}


def result_label(status: str) -> str:
    """Return the French product label for one public solver result status."""

    return _LABELS.get(status, _LABELS[NO_SOLUTION_WITHIN_BUDGET])


def attach_solver_outcome(
    plan: dict[str, object],
    *,
    request_id: str | None,
    request_revision: int | None,
    elapsed_ms: float,
) -> dict[str, object]:
    """Attach the P64-H04 result contract without changing legacy plan fields."""

    summary = _mapping(plan.get("summary"))
    solver = _mapping(plan.get("solver"))
    diagnostics = _mappings(plan.get("diagnostics", []))
    search = _mapping(solver.get("search", {}))
    proof = _first_formal_proof(diagnostics)
    status = _classify_legacy_plan(summary, diagnostics, proof)
    stop_reason = _stop_reason(status, summary, diagnostics, search, proof)
    certified = 1 if status == SOLUTION_FOUND else 0
    telemetry = {
        "schema_version": SOLVER_TELEMETRY_SCHEMA_V1,
        "family": {
            "id": "stage_stack",
            "version": solver.get("schema_version") or "not_applicable",
        },
        "request": {
            "id": request_id or "not_applicable",
            "revision": request_revision if request_revision is not None else "not_applicable",
        },
        "elapsed_ms": _elapsed_ms(request_id, request_revision, elapsed_ms),
        "budgets": deepcopy(_mapping(solver.get("budgets", {}))),
        "counters": {
            "candidate_proposals": _first_counter(
                search, "candidate_count_across_portfolios", "candidate_count"
            ),
            "search_states": _sum_counters(
                search,
                "groupings_evaluated_across_portfolios",
                "groupings_evaluated",
                "adaptive_partitions_evaluated",
                "stack_partitions_evaluated",
            ),
            "placements_attempted": _first_counter(search, "xy_arrangements_evaluated"),
            "certified_complete_solutions": certified,
            "z_start_levels": _z_start_levels(plan) if status == SOLUTION_FOUND else "not_applicable",
        },
        "prunes": {
            "candidate_budget_truncations": 1 if bool(search.get("truncated")) else 0,
            "visible_validation_rejections": _visible_validation_rejections(diagnostics),
            "deduplicated_candidates": "not_applicable",
        },
        "diagnostic_code_counts": dict(sorted(Counter(_text(item.get("code")) for item in diagnostics).items())),
        "stop_reason": stop_reason,
    }
    result = {
        "schema_version": SOLVER_RESULT_SCHEMA_V1,
        "status": status,
        "label": result_label(status),
        "legacy_summary_status": _text(summary.get("status")),
        "proof": proof,
        "materializable": bool(summary.get("materializable")) and status == SOLUTION_FOUND,
    }
    summary["result_status"] = status
    summary["result_label"] = result["label"]
    solver["result"] = result
    solver["telemetry"] = telemetry
    return plan


def invalid_input_result(request_id: str | None, request_revision: int | None) -> dict[str, object]:
    """Return an additive result for a request rejected before any search."""

    return {
        "schema_version": SOLVER_RESULT_SCHEMA_V1,
        "status": INVALID_INPUT,
        "label": result_label(INVALID_INPUT),
        "legacy_summary_status": "not_applicable",
        "proof": None,
        "materializable": False,
        "telemetry": {
            "schema_version": SOLVER_TELEMETRY_SCHEMA_V1,
            "family": {"id": "not_applicable", "version": "not_applicable"},
            "request": {
                "id": request_id or "not_applicable",
                "revision": request_revision if request_revision is not None else "not_applicable",
            },
            "elapsed_ms": "not_applicable",
            "budgets": {},
            "counters": {
                "candidate_proposals": "not_applicable",
                "search_states": "not_applicable",
                "placements_attempted": "not_applicable",
                "certified_complete_solutions": 0,
                "z_start_levels": "not_applicable",
            },
            "prunes": {
                "candidate_budget_truncations": "not_applicable",
                "visible_validation_rejections": "not_applicable",
                "deduplicated_candidates": "not_applicable",
            },
            "diagnostic_code_counts": {},
            "stop_reason": "input_validation_failed",
        },
    }


def _classify_legacy_plan(
    summary: dict[str, Any],
    diagnostics: list[dict[str, Any]],
    proof: dict[str, object] | None,
) -> str:
    legacy_status = _text(summary.get("status"))
    if legacy_status == "constructed" and bool(summary.get("materializable")):
        return SOLUTION_FOUND
    if proof is not None:
        return PROVEN_IMPOSSIBLE
    if legacy_status == "proposal_with_residuals":
        return NO_SOLUTION_WITHIN_BUDGET
    if any(_text(item.get("code")) in _INPUT_DIAGNOSTIC_CODES for item in diagnostics):
        return INVALID_INPUT
    return NO_SOLUTION_WITHIN_BUDGET


def _stop_reason(
    status: str,
    summary: dict[str, Any],
    diagnostics: list[dict[str, Any]],
    search: dict[str, Any],
    proof: dict[str, object] | None,
) -> str:
    if status == SOLUTION_FOUND:
        return "validated_complete_proposal"
    if status == PROVEN_IMPOSSIBLE:
        return _text(proof.get("code")) if proof is not None else "formal_bound_violated"
    if status == INVALID_INPUT:
        return "input_validation_failed"
    if _text(summary.get("status")) == "proposal_with_residuals":
        return "partial_proposal_not_materializable"
    codes = {_text(item.get("code")) for item in diagnostics}
    if "NO_VALIDATED_STAGE_PROPOSAL" in codes:
        return "candidates_rejected_after_validation"
    if bool(search.get("truncated")):
        return "candidate_budget_reached"
    return "heuristic_search_exhausted"


def _first_formal_proof(diagnostics: list[dict[str, Any]]) -> dict[str, object] | None:
    for diagnostic in diagnostics:
        proof = diagnostic.get("proof")
        if isinstance(proof, dict) and isinstance(proof.get("code"), str):
            return deepcopy(proof)
    return None


def _first_counter(search: dict[str, Any], *names: str) -> int | str:
    for name in names:
        value = search.get(name)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return "not_applicable"


def _sum_counters(search: dict[str, Any], *names: str) -> int | str:
    values = [search.get(name) for name in names]
    counters = [value for value in values if isinstance(value, int) and not isinstance(value, bool)]
    return sum(counters) if counters else "not_applicable"


def _visible_validation_rejections(diagnostics: list[dict[str, Any]]) -> int:
    return sum(
        1
        for diagnostic in diagnostics
        if _text(diagnostic.get("code"))
        in {"FINAL_ENVELOPE_REJECTED", "INTERNAL_STAGE_PLAN_INVALID", "TOP_INSET_PIERCES_CAVITY_FLOOR", "TOP_INSET_PIERCES_BODY_FLOOR"}
    )


def _z_start_levels(plan: dict[str, object]) -> int:
    placements = _mappings(plan.get("placements", []))
    return len({float(_mapping(item.get("origin_mm")).get("z")) for item in placements})


def _elapsed_ms(
    request_id: str | None,
    request_revision: int | None,
    elapsed_ms: float,
) -> float | str:
    if request_id is None and request_revision is None:
        return "not_applicable"
    return round(max(0.0, float(elapsed_ms)), 3)


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Internal P64 solver outcome value must be an object.")
    return value


def _mappings(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [_mapping(item) for item in value if isinstance(item, dict)]


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""
