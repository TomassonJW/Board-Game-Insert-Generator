"""User-facing P65-M004 explanations derived from an existing partition plan.

This module deliberately translates only facts already calculated by P64.  It
does not rank a plan, change a score, or infer geometry in the palette.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


PREVIEW_EXPLANATIONS_SCHEMA_V1 = "bgig.preview_explanations.v1"


class PreviewExplanationsError(ValueError):
    """Raised when a presentation would hide a malformed result contract."""


def build_preview_explanations(partition: object) -> dict[str, object]:
    """Translate a solved P64 partition without mutating it."""

    plan = _mapping(partition, "partition")
    summary = _mapping(plan.get("summary"), "partition.summary")
    placements = _mappings(plan.get("placements"), "partition.placements")
    reservations = _mappings(
        _mapping_or_empty(plan.get("top_inset_reservations")).get("reservations", []),
        "partition.top_inset_reservations.reservations",
    )
    residuals = _mapping_or_empty(plan.get("residuals"))
    suggestions = _mappings(plan.get("suggestions", []), "partition.suggestions")
    stage_support = _mapping_or_empty(plan.get("stage_support"))
    flat_support = _mapping_or_empty(plan.get("support"))
    score_breakdown = _mapping_or_empty(summary.get("score_breakdown"))
    stage_count = _integer_or_zero(summary.get("stage_count"))

    return {
        "schema_version": PREVIEW_EXPLANATIONS_SCHEMA_V1,
        "score": _score_explanation(score_breakdown),
        "stage_support": _stage_support_explanation(stage_support, stage_count),
        "flat_support": _flat_support_explanation(flat_support),
        "removal": _removal_explanation(
            _mappings(plan.get("removal_sequence", []), "partition.removal_sequence"),
            placements,
            reservations,
        ),
        "residual": _residual_explanation(residuals, suggestions),
        "invariants": {
            "derived_from_existing_plan": True,
            "does_not_change_score": True,
            "does_not_change_materializability": True,
            "does_not_create_bodies": True,
            "does_not_mutate_plan": True,
        },
    }


def _score_explanation(scores: dict[str, Any]) -> dict[str, object]:
    criteria = (
        ("simplicity", "Simplicite du plan", "Favorise un rangement moins complexe a imprimer et a comprendre."),
        ("target_fit", "Respect des tailles ciblees", "Compare les tailles obtenues aux objectifs souples demandes."),
        ("material_distribution", "Repartition de la matiere", "Compare la repartition du surplus autour des volumes minimums."),
        ("support", "Appui des etages", "Tient compte de la couverture calculee sous les elements superieurs."),
    )
    return {
        "title": "Indice de comparaison",
        "value": _number_or_none(scores.get("total")),
        "scale_label": "sur 100",
        "summary": (
            "Cet indice compare les propositions de ce projet. Il ne garantit ni la resistance "
            "du modele, ni une impression reelle."
        ),
        "criteria": [
            {
                "label": label,
                "value": _number_or_none(scores.get(key)),
                "summary": summary,
            }
            for key, label, summary in criteria
        ],
    }


def _stage_support_explanation(support: dict[str, Any], stage_count: int) -> dict[str, object]:
    status = str(support.get("status", ""))
    coverage = _number_or_none(support.get("minimum_coverage_ratio"))
    required = _number_or_none(support.get("minimum_required_ratio"))
    if stage_count <= 1:
        title = "Appui des etages"
        summary = "Un seul etage : les conteneurs reposent sur le fond de la boite."
        state = "single_stage"
    elif status == "supported":
        title = "Appui des etages"
        summary = "Chaque etage superieur atteint la couverture d appui calculee requise."
        state = "confirmed"
    else:
        title = "Appui des etages"
        summary = "Certains elements superieurs n atteignent pas la couverture d appui requise."
        state = "attention"
    return {
        "title": title,
        "summary": summary,
        "state": state,
        "coverage_label": _coverage_label(coverage, "Couverture minimale"),
        "required_label": _coverage_label(required, "Seuil requis"),
    }


def _flat_support_explanation(support: dict[str, Any]) -> dict[str, object]:
    status = str(support.get("status", ""))
    if status == "not_required":
        summary = "Aucun plateau ou livret ne demande d encastrement dans cette proposition."
        state = "not_required"
    elif status == "supported_by_requested_bodies":
        summary = "Les plateaux et livrets encastres reposent sur les conteneurs demandes."
        state = "confirmed"
    else:
        summary = "L appui des plateaux ou livrets doit etre verifie avant fabrication."
        state = "attention"
    return {
        "title": "Plateaux et livrets",
        "summary": summary,
        "state": state,
        "support_count_label": f"Zones d appui : {_integer_or_zero(support.get('top_support_count'))}",
        "coverage_label": _coverage_label(_number_or_none(support.get("coverage_ratio")), "Couverture projetee"),
    }


def _removal_explanation(
    sequence: list[dict[str, Any]],
    placements: list[dict[str, Any]],
    reservations: list[dict[str, Any]],
) -> dict[str, object]:
    placement_names = {str(item.get("id")): str(item.get("name", "Conteneur")) for item in placements}
    reservation_names = {str(item.get("id")): str(item.get("name", "Plateau ou livret")) for item in reservations}
    entries: list[dict[str, object]] = []
    for item in sorted(sequence, key=lambda value: _integer_or_zero(value.get("order"))):
        target_id = str(item.get("target_id", item.get("placement_id", "")))
        reservation_id = str(item.get("reservation_id", ""))
        if reservation_id:
            label = reservation_names.get(reservation_id, "Plateau ou livret")
            kind = "Plateau ou livret"
        else:
            label = placement_names.get(target_id, "Conteneur")
            kind = "Conteneur"
        entries.append(
            {
                "order": _integer_or_zero(item.get("order")),
                "label": label,
                "kind": kind,
                "summary": f"Retirer {label}.",
            }
        )
    return {
        "title": "Ordre de retrait",
        "summary": (
            "Retire les elements dans cet ordre, du dessus vers le fond."
            if entries
            else "Aucun ordre de retrait particulier n est calcule pour cette proposition."
        ),
        "entries": entries,
    }


def _residual_explanation(
    residuals: dict[str, Any], suggestions: list[dict[str, Any]],
) -> dict[str, object]:
    residual_volume = _number_or_none(residuals.get("residual_volume_mm3")) or 0.0
    has_residual = str(residuals.get("status", "")) == "present" or residual_volume > 0.0
    translated_suggestions = [
        {
            "label": str(item.get("name", "Suggestion optionnelle")),
            "dimensions_mm": deepcopy(item.get("dimensions_mm")),
            "summary": "Choix manuel : cette suggestion ne cree aucun corps automatiquement.",
            "requires_confirmation": bool(item.get("requires_confirmation", True)),
        }
        for item in suggestions
    ]
    return {
        "title": "Volume residuel a decider",
        "present": has_residual,
        "volume_mm3": residual_volume,
        "summary": (
            "Une partie du volume reste sans corps imprimable. Elle n est ni materialisee ni comblee automatiquement."
            if has_residual
            else "Aucun volume residuel ne demande de decision."
        ),
        "suggestions": translated_suggestions,
    }


def _coverage_label(value: float | None, label: str) -> str:
    return f"{label} : {value * 100:g} %" if value is not None else f"{label} : non calculee"


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PreviewExplanationsError(f"{field} doit etre un objet.")
    return value


def _mapping_or_empty(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _mappings(value: object, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PreviewExplanationsError(f"{field} doit etre une liste.")
    return [_mapping(item, f"{field}[{index}]") for index, item in enumerate(value)]


def _integer_or_zero(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return int(value)


def _number_or_none(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PreviewExplanationsError("Une valeur de presentation doit etre numerique ou absente.")
    return float(value)
