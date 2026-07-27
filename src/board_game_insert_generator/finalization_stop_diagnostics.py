"""Stable, user-facing diagnostics for bounded finalization outcomes."""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping


FINALIZATION_STOP_DIAGNOSTICS_SCHEMA_V1 = (
    "bgig.finalization_stop_diagnostics.v1"
)

OUTCOME_SUCCESS = "success"
OUTCOME_PREREQUISITE_MISSING = "prerequisite_missing"
OUTCOME_CERTIFICATE_REJECTED = "certificate_rejected"
OUTCOME_STRATEGY_EXHAUSTED = "strategy_exhausted"
OUTCOME_DEADLINE_REACHED = "deadline_reached"
OUTCOME_PROVEN_IMPOSSIBLE = "proven_impossible"
OUTCOME_STALE = "stale"


def build_finalization_stop_diagnostics(
    report: Mapping[str, object],
    *,
    elapsed_ms: int,
    budget_cap_ms: int,
) -> dict[str, object]:
    """Classify one stop without turning a bounded failure into impossibility."""

    stop_reason = str(
        report.get("stop_reason", "coupled_finalization_rejected")
    )
    elapsed = max(0, int(elapsed_ms))
    cap = max(0, int(budget_cap_ms))
    declared_budget_elapsed = report.get("budget_elapsed_ms")
    budget_elapsed = (
        max(0, int(declared_budget_elapsed))
        if isinstance(declared_budget_elapsed, int)
        and not isinstance(declared_budget_elapsed, bool)
        else min(elapsed, cap) if cap > 0 else elapsed
    )
    termination_elapsed = max(0, elapsed - budget_elapsed)
    deadline_reached = bool(
        report.get("deadline_reached") is True
        or "deadline" in stop_reason
        or "time_limit" in stop_reason
    )
    outcome_kind = _outcome_kind(
        stop_reason,
        status=str(report.get("status", "")),
        deadline_reached=deadline_reached,
    )
    phase = _phase(stop_reason)
    candidate_count = _first_non_negative_int(
        report,
        "candidate_attempt_count",
        "candidates_evaluated",
        "iterations",
    )
    raw_rejection_codes = report.get("rejection_codes", ())
    if not isinstance(raw_rejection_codes, (list, tuple)):
        raw_rejection_codes = ()
    rejection_codes = [
        str(value)
        for value in raw_rejection_codes
        if isinstance(value, str) and value
    ]
    raw_attempts = report.get("candidate_pool_attempts", ())
    if not isinstance(raw_attempts, (list, tuple)):
        raw_attempts = ()
    attempts = [
        value
        for value in raw_attempts
        if isinstance(value, Mapping)
    ]
    rejected_attempts = sum(
        1 for value in attempts if value.get("status") != "solution_found"
    )
    rejection_count = max(len(rejection_codes), rejected_attempts)
    title, summary = _user_copy(outcome_kind, phase)
    counters = {
        key: value
        for key in (
            "candidate_pool_count",
            "candidate_attempt_count",
            "candidates_evaluated",
            "iterations",
            "repair_attempts",
            "repairs_applied",
            "global_resolve_invocation_count",
        )
        if (
            isinstance((value := report.get(key)), int)
            and not isinstance(value, bool)
            and value >= 0
        )
    }
    return {
        "schema_version": FINALIZATION_STOP_DIAGNOSTICS_SCHEMA_V1,
        "outcome_kind": outcome_kind,
        "phase": phase,
        "stop_reason": stop_reason,
        "user_title": title,
        "user_summary": summary,
        "elapsed_ms": elapsed,
        "wall_clock_elapsed_ms": elapsed,
        "budget_elapsed_ms": budget_elapsed,
        "termination_elapsed_ms": termination_elapsed,
        "budget_cap_ms": cap,
        "wall_clock_cap_ms": cap,
        "wall_clock_cap_exceeded": bool(cap > 0 and elapsed > cap),
        "elapsed_is_search_plus_termination": True,
        "stopped_before_cap": bool(
            cap > 0 and budget_elapsed < cap and not deadline_reached
        ),
        "deadline_reached": deadline_reached,
        "proof_of_impossibility": outcome_kind == OUTCOME_PROVEN_IMPOSSIBLE,
        "candidate_count": candidate_count,
        "rejection_count": rejection_count,
        "rejection_codes": rejection_codes,
        "counters": deepcopy(counters),
    }


def attach_finalization_stop_diagnostics(
    report: Mapping[str, object],
    *,
    elapsed_ms: int,
    budget_cap_ms: int,
) -> dict[str, object]:
    """Copy one report and attach its canonical diagnostics."""

    enriched = deepcopy(dict(report))
    enriched["stop_diagnostics"] = build_finalization_stop_diagnostics(
        enriched,
        elapsed_ms=elapsed_ms,
        budget_cap_ms=budget_cap_ms,
    )
    return enriched


def _outcome_kind(
    stop_reason: str,
    *,
    status: str,
    deadline_reached: bool,
) -> str:
    if status == "solution_found" or stop_reason in {
        "global_finalization_certified",
        "candidate_finalization_certified",
    }:
        return OUTCOME_SUCCESS
    if status == "proven_impossible":
        return OUTCOME_PROVEN_IMPOSSIBLE
    if stop_reason in {
        "minimal_layout_missing_or_stale",
        "minimal_candidate_pool_empty",
        "minimal_incumbent_not_certified",
        "minimal_plan_not_certified",
        "minimal_incumbent_reconstruction_failed",
        "container_variant_frontier_reconstruction_failed",
        "input_validation_failed",
    }:
        return OUTCOME_PREREQUISITE_MISSING
    if stop_reason == "finalization_result_stale" or "stale" in stop_reason:
        return OUTCOME_STALE
    if deadline_reached:
        return OUTCOME_DEADLINE_REACHED
    if (
        "proven_impossible" in stop_reason
        or stop_reason == "printable_domain_impossible"
    ):
        return OUTCOME_PROVEN_IMPOSSIBLE
    if "certificate" in stop_reason or "contract_rejected" in stop_reason:
        return OUTCOME_CERTIFICATE_REJECTED
    return OUTCOME_STRATEGY_EXHAUSTED


def _phase(stop_reason: str) -> str:
    if stop_reason == "minimal_layout_missing_or_stale":
        return "prerequis"
    if "minimal_candidate" in stop_reason or "incumbent" in stop_reason:
        return "selection_plan_minimal"
    if (
        "preparation" in stop_reason
        or "input_validation" in stop_reason
        or "frontier_reconstruction" in stop_reason
    ):
        return "preparation"
    if "xy_composite" in stop_reason or "composite" in stop_reason:
        return "fermeture_composite"
    if "rectangular" in stop_reason or "gross_partition" in stop_reason:
        return "partition_rectangulaire"
    if "continuous" in stop_reason:
        return "fermeture_continue"
    if "certificate" in stop_reason:
        return "certificat_final"
    if "stale" in stop_reason:
        return "validation_identite"
    if "finalization_certified" in stop_reason:
        return "certificat_final"
    return "finalisation"


def _user_copy(outcome_kind: str, phase: str) -> tuple[str, str]:
    phase_label = {
        "prerequis": "les prérequis",
        "selection_plan_minimal": "la sélection du plan minimal",
        "preparation": "la préparation",
        "partition_rectangulaire": "la partition rectangulaire",
        "fermeture_continue": "la fermeture continue",
        "fermeture_composite": "la fermeture composite",
        "certificat_final": "le certificat final",
        "validation_identite": "la validation d’identité",
        "finalisation": "la finalisation",
    }.get(phase, "la finalisation")
    if outcome_kind == OUTCOME_SUCCESS:
        return (
            "Finition terminée",
            "Le plan final a été certifié et peut être matérialisé.",
        )
    if outcome_kind == OUTCOME_PREREQUISITE_MISSING:
        return (
            "Calcul requis avant la finition",
            "Le plan minimal est absent ou obsolète. Lance Calculer, puis Finaliser.",
        )
    if outcome_kind == OUTCOME_DEADLINE_REACHED:
        return (
            "Plafond de finition atteint",
            (
                f"La recherche s’est arrêtée pendant {phase_label} au plafond "
                "prévu, sans plan final certifié. Cela ne prouve pas qu’aucune "
                "finition n’existe."
            ),
        )
    if outcome_kind == OUTCOME_CERTIFICATE_REJECTED:
        return (
            "Candidat de finition rejeté",
            (
                f"Un candidat a été rejeté pendant {phase_label}. Le plan minimal "
                "reste disponible ; ce rejet ne prouve pas une impossibilité générale."
            ),
        )
    if outcome_kind == OUTCOME_PROVEN_IMPOSSIBLE:
        return (
            "Finition impossible avec ces contraintes",
            (
                f"Une preuve d’impossibilité a été établie pendant {phase_label} "
                "pour les contraintes actuelles."
            ),
        )
    if outcome_kind == OUTCOME_STALE:
        return (
            "Résultat de finition obsolète",
            (
                "Le projet a changé pendant la finition. Le résultat terminé a "
                "été rejeté et le plan minimal courant reste protégé."
            ),
        )
    return (
        "Stratégie de finition épuisée",
        (
            f"La stratégie bornée s’est arrêtée pendant {phase_label} sans plan "
            "final certifié. Le résultat reste inconnu, pas impossible."
        ),
    )


def _first_non_negative_int(
    report: Mapping[str, object],
    *keys: str,
) -> int:
    for key in keys:
        value = report.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
    return 0
