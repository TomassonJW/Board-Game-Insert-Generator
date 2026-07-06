from __future__ import annotations

from typing import Any

from board_game_insert_generator.models import (
    Asset,
    AssetKind,
    ContainmentIntent,
    Dimension3D,
    FunctionalType,
    InsertConfig,
)


_RESERVATION_ONLY_KINDS = {AssetKind.BOARD, AssetKind.RULEBOOK, AssetKind.TRAY}
_FUNCTIONAL_TYPE_BY_ASSET_KIND = {
    AssetKind.CARDS: FunctionalType.CARDS,
    AssetKind.SLEEVED_CARDS: FunctionalType.SLEEVED_CARDS,
    AssetKind.TOKENS: FunctionalType.TOKENS,
    AssetKind.DICE: FunctionalType.DICE,
    AssetKind.MEEPLES: FunctionalType.MEEPLES,
}


def build_module_candidates_from_assets(config: InsertConfig) -> list[dict[str, Any]]:
    """Build deterministic, report-only module candidates from loaded assets.

    Candidates are explanatory metadata. They do not mutate config.modules, do not
    create layout cells and do not authorize any Fusion generation.
    """

    return [_candidate_from_asset(config, asset) for asset in config.assets]


def _candidate_from_asset(config: InsertConfig, asset: Asset) -> dict[str, Any]:
    clearance_mm, clearance_source = _asset_clearance(config, asset)
    reasons: list[str] = []
    warnings: list[str] = []

    if asset.dimension_confidence.value != "exact":
        warnings.append(
            f"Asset dimensions are {asset.dimension_confidence.value}; candidate dimensions need human review."
        )
    if asset.module_hint is not None:
        reasons.append(f"Asset already references manual module hint '{asset.module_hint}'.")
    if asset.reservation_ref is not None:
        reasons.append(f"Asset references volumetric reservation '{asset.reservation_ref}'.")

    status = "candidate_only"
    suggested_module: dict[str, Any] | None
    if _is_reservation_only(asset):
        status = "reservation_only"
        suggested_module = None
        reasons.append("Asset kind or intent is reservation-oriented; no printable module candidate is derived.")
    elif asset.dimension_confidence.value == "unknown_z" and asset.dimensions.z <= 0:
        status = "blocked"
        suggested_module = None
        reasons.append("Asset Z dimension is unknown; candidate height cannot be derived safely.")
    else:
        suggested_module = _suggested_module(config, asset, clearance_mm, clearance_source)
        reasons.append("Candidate dimensions are derived from asset dimensions, profile clearance and geometry defaults.")

    return {
        "candidate_id": f"asset-candidate:{asset.id}",
        "source_asset_ids": [asset.id],
        "status": status,
        "derivation": "asset_dimension_padding",
        "functional_type": _functional_type(asset).value,
        "containment_intent": asset.containment_intent.value,
        "dimension_confidence": asset.dimension_confidence.value,
        "quantity": {
            "count": asset.quantity.count,
            "grouping": asset.quantity.grouping,
        },
        "suggested_module": suggested_module,
        "constraints": {
            "clearance_mm": clearance_mm,
            "clearance_source": clearance_source,
            "wall_thickness_mm": config.defaults.wall_thickness_mm,
            "floor_thickness_mm": config.defaults.floor_thickness_mm,
        },
        "reasons": reasons,
        "warnings": warnings,
    }


def _is_reservation_only(asset: Asset) -> bool:
    return asset.kind in _RESERVATION_ONLY_KINDS or asset.containment_intent == ContainmentIntent.RESERVE


def _functional_type(asset: Asset) -> FunctionalType:
    return _FUNCTIONAL_TYPE_BY_ASSET_KIND.get(asset.kind, FunctionalType.OTHER)


def _asset_clearance(config: InsertConfig, asset: Asset) -> tuple[float, str]:
    tolerances = config.tolerances
    if asset.kind == AssetKind.CARDS:
        return tolerances.card_clearance_mm, "tolerances.card_clearance_mm"
    if asset.kind == AssetKind.SLEEVED_CARDS:
        return tolerances.sleeved_card_clearance_mm, "tolerances.sleeved_card_clearance_mm"
    if asset.kind in (AssetKind.TOKENS, AssetKind.DICE):
        return tolerances.token_clearance_mm, "tolerances.token_clearance_mm"
    if asset.kind == AssetKind.MEEPLES:
        return tolerances.meeple_clearance_mm, "tolerances.meeple_clearance_mm"
    return 0.0, "none"


def _suggested_module(
    config: InsertConfig,
    asset: Asset,
    clearance_mm: float,
    clearance_source: str,
) -> dict[str, Any]:
    wall = config.defaults.wall_thickness_mm
    floor = config.defaults.floor_thickness_mm
    inner = Dimension3D(
        x=asset.dimensions.x + clearance_mm * 2.0,
        y=asset.dimensions.y + clearance_mm * 2.0,
        z=asset.dimensions.z + clearance_mm,
    )
    outer = Dimension3D(
        x=inner.x + wall * 2.0,
        y=inner.y + wall * 2.0,
        z=inner.z + floor,
    )
    return {
        "id": f"candidate-module:{asset.id}",
        "name": f"Candidate module for {asset.name}",
        "functional_type": _functional_type(asset).value,
        "min_dimensions_mm": _dimension_to_dict(outer),
        "inner_asset_envelope_mm": _dimension_to_dict(inner),
        "clearance_source": clearance_source,
        "status": "candidate_only_not_placed",
    }


def _dimension_to_dict(dimension: Dimension3D) -> dict[str, float]:
    return {"x": round(dimension.x, 4), "y": round(dimension.y, 4), "z": round(dimension.z, 4)}
