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

    candidates: list[dict[str, Any]] = []
    for group in _compatible_asset_groups(config.assets):
        if len(group) == 1:
            candidates.append(_candidate_from_asset(config, group[0]))
        else:
            candidates.append(_candidate_from_asset_group(config, group))
    return candidates



def _compatible_asset_groups(assets: tuple[Asset, ...]) -> list[list[Asset]]:
    groups: list[list[Asset]] = []
    grouped_indexes: set[int] = set()
    for index, asset in enumerate(assets):
        if index in grouped_indexes:
            continue
        if not _can_group_asset(asset):
            groups.append([asset])
            grouped_indexes.add(index)
            continue
        group = [asset]
        grouped_indexes.add(index)
        for other_index, other in enumerate(assets[index + 1 :], start=index + 1):
            if other_index in grouped_indexes:
                continue
            if _asset_group_key(other) == _asset_group_key(asset) and _can_group_asset(other):
                group.append(other)
                grouped_indexes.add(other_index)
        groups.append(group)
    return groups


def _can_group_asset(asset: Asset) -> bool:
    return (
        not _is_reservation_only(asset)
        and not (asset.dimension_confidence.value == "unknown_z" and asset.dimensions.z <= 0)
        and asset.reservation_ref is None
        and asset.module_hint is None
    )


def _asset_group_key(asset: Asset) -> tuple[str, str, str]:
    return (asset.kind.value, asset.containment_intent.value, asset.dimension_confidence.value)


def _candidate_from_asset_group(config: InsertConfig, assets: list[Asset]) -> dict[str, Any]:
    representative = assets[0]
    clearance_mm, clearance_source = _asset_clearance(config, representative)
    dimensions = Dimension3D(
        x=max(asset.dimensions.x for asset in assets),
        y=max(asset.dimensions.y for asset in assets),
        z=max(asset.dimensions.z for asset in assets),
    )
    suggested_module = _suggested_module_from_values(
        config=config,
        candidate_id=f"asset-group-candidate:{representative.kind.value}:{representative.containment_intent.value}:{representative.dimension_confidence.value}",
        name=f"Grouped candidate for {representative.kind.value}",
        functional_type=_functional_type(representative),
        dimensions=dimensions,
        clearance_mm=clearance_mm,
        clearance_source=clearance_source,
    )
    warnings = []
    if representative.dimension_confidence.value != "exact":
        warnings.append(
            f"Grouped assets use {representative.dimension_confidence.value} dimensions; candidate dimensions need human review."
        )
    return {
        "candidate_id": suggested_module["id"].replace("candidate-module:", "asset-group-candidate:"),
        "source_asset_ids": [asset.id for asset in assets],
        "status": "candidate_only",
        "derivation": "asset_group_dimension_padding",
        "functional_type": _functional_type(representative).value,
        "containment_intent": representative.containment_intent.value,
        "dimension_confidence": representative.dimension_confidence.value,
        "quantity": {
            "count": sum(asset.quantity.count for asset in assets),
            "grouping": "grouped_assets",
        },
        "suggested_module": suggested_module,
        "constraints": {
            "clearance_mm": clearance_mm,
            "clearance_source": clearance_source,
            "wall_thickness_mm": config.defaults.wall_thickness_mm,
            "floor_thickness_mm": config.defaults.floor_thickness_mm,
        },
        "reasons": [
            "Compatible assets share kind, containment intent and dimension confidence.",
            "Grouped candidate uses the largest source asset envelope plus profile/default padding.",
        ],
        "warnings": warnings,
    }

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
    return _suggested_module_from_values(
        config=config,
        candidate_id=f"candidate-module:{asset.id}",
        name=f"Candidate module for {asset.name}",
        functional_type=_functional_type(asset),
        dimensions=asset.dimensions,
        clearance_mm=clearance_mm,
        clearance_source=clearance_source,
    )


def _suggested_module_from_values(
    *,
    config: InsertConfig,
    candidate_id: str,
    name: str,
    functional_type: FunctionalType,
    dimensions: Dimension3D,
    clearance_mm: float,
    clearance_source: str,
) -> dict[str, Any]:
    wall = config.defaults.wall_thickness_mm
    floor = config.defaults.floor_thickness_mm
    inner = Dimension3D(
        x=dimensions.x + clearance_mm * 2.0,
        y=dimensions.y + clearance_mm * 2.0,
        z=dimensions.z + clearance_mm,
    )
    outer = Dimension3D(
        x=inner.x + wall * 2.0,
        y=inner.y + wall * 2.0,
        z=inner.z + floor,
    )
    return {
        "id": candidate_id,
        "name": name,
        "functional_type": functional_type.value,
        "min_dimensions_mm": _dimension_to_dict(outer),
        "inner_asset_envelope_mm": _dimension_to_dict(inner),
        "clearance_source": clearance_source,
        "status": "candidate_only_not_placed",
    }



def build_asset_candidate_variants(config: InsertConfig) -> list[dict[str, Any]]:
    candidates = build_module_candidates_from_assets(config)
    printable_candidates = [candidate for candidate in candidates if candidate["status"] == "candidate_only"]
    if not printable_candidates:
        return [
            {
                "variant_id": "asset-candidates:row_fill",
                "source": "module_candidates",
                "status": "rejected",
                "recommended": False,
                "total_score": 0.0,
                "subscores": {},
                "placements": [],
                "candidate_ids": [],
                "reasons": ["No printable asset module candidates are available."],
                "rejection_reasons": [
                    _variant_rejection_reason(
                        code="NO_CANDIDATES",
                        category="assets",
                        message="No candidate_only module candidates were produced from assets.",
                        constraint_ref="assets",
                        actionable="Add a storable asset with known dimensions or review reservation-only assets.",
                    )
                ],
            }
        ]

    variant = _row_fill_asset_candidate_variant(config, printable_candidates)
    return [variant]


def recommended_asset_candidate_variant(variants: list[dict[str, Any]]) -> dict[str, Any] | None:
    viable = [variant for variant in variants if variant["status"] != "rejected"]
    if not viable:
        return None
    return max(viable, key=lambda variant: variant["total_score"])


def _row_fill_asset_candidate_variant(
    config: InsertConfig,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    cursor_x = 0.0
    cursor_y = 0.0
    row_depth = 0.0
    placements: list[dict[str, Any]] = []
    box = config.box.inner_dimensions

    for candidate in candidates:
        size = candidate["suggested_module"]["min_dimensions_mm"]
        oriented_size, rotated = _choose_candidate_orientation(size, box.x - cursor_x, box.x, box.y)
        if oriented_size["x"] > box.x or oriented_size["y"] > box.y:
            return _rejected_asset_candidate_variant(
                candidate,
                f"Candidate '{candidate['candidate_id']}' cannot fit inside the box in any allowed XY orientation.",
                "DIMENSIONS_INCOMPATIBLE",
                "modules[].min_dimensions_mm / box.inner_dimensions_mm",
            )
        if cursor_x > 0 and oriented_size["x"] > box.x - cursor_x:
            cursor_x = 0.0
            cursor_y += row_depth
            row_depth = 0.0
            oriented_size, rotated = _choose_candidate_orientation(size, box.x, box.x, box.y)
        if cursor_y + oriented_size["y"] > box.y:
            return _rejected_asset_candidate_variant(
                candidate,
                (
                    f"Candidate '{candidate['candidate_id']}' row_fill placement needs Y up to "
                    f"{cursor_y + oriented_size['y']:.2f} mm, box has {box.y:.2f} mm."
                ),
                "DOES_NOT_FIT",
                "box.inner_dimensions_mm / module_candidates",
            )
        placements.append(
            {
                "candidate_id": candidate["candidate_id"],
                "origin_mm": {"x": round(cursor_x, 4), "y": round(cursor_y, 4), "z": 0.0},
                "size_mm": oriented_size,
                "rotated": rotated,
            }
        )
        cursor_x += oriented_size["x"]
        row_depth = max(row_depth, oriented_size["y"])

    footprint_x = max((placement["origin_mm"]["x"] + placement["size_mm"]["x"] for placement in placements), default=0.0)
    footprint_y = max((placement["origin_mm"]["y"] + placement["size_mm"]["y"] for placement in placements), default=0.0)
    occupation = (footprint_x * footprint_y / (box.x * box.y)) * 100.0 if box.x * box.y > 0 else 0.0
    subscores = {
        "compactness": round(max(0.0, 40.0 - occupation * 0.2), 4),
        "asset_coverage": round(30.0 * (len(placements) / len(candidates)), 4),
        "measurement_confidence": _candidate_measurement_score(candidates),
        "simplicity": round(max(0.0, 20.0 - len(placements) * 2.0), 4),
    }
    total_score = round(sum(subscores.values()), 4)
    return {
        "variant_id": "asset-candidates:row_fill",
        "source": "module_candidates",
        "status": "recommended",
        "recommended": True,
        "total_score": total_score,
        "subscores": subscores,
        "placements": placements,
        "footprint_mm": {"x": round(footprint_x, 4), "y": round(footprint_y, 4), "z": 0.0},
        "occupation_percent": round(occupation, 4),
        "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
        "reasons": [
            "All printable asset module candidates fit with deterministic row_fill heuristic.",
            "Variant is report-only and does not mutate config.modules or Fusion geometry.",
        ],
        "rejection_reasons": [],
    }


def _choose_candidate_orientation(
    size: dict[str, float],
    remaining_x: float,
    max_x: float,
    max_y: float,
) -> tuple[dict[str, float], bool]:
    normal = {"x": size["x"], "y": size["y"], "z": size["z"]}
    rotated = {"x": size["y"], "y": size["x"], "z": size["z"]}
    if normal["x"] <= remaining_x and normal["y"] <= max_y:
        return normal, False
    if rotated["x"] <= remaining_x and rotated["y"] <= max_y:
        return rotated, True
    if normal["x"] <= max_x and normal["y"] <= max_y:
        return normal, False
    if rotated["x"] <= max_x and rotated["y"] <= max_y:
        return rotated, True
    return normal, False


def _candidate_measurement_score(candidates: list[dict[str, Any]]) -> float:
    if not candidates:
        return 0.0
    values = []
    for candidate in candidates:
        confidence = candidate["dimension_confidence"]
        if confidence == "exact":
            values.append(10.0)
        elif confidence == "approximate":
            values.append(6.0)
        else:
            values.append(3.0)
    return round(sum(values) / len(values), 4)


def _rejected_asset_candidate_variant(
    candidate: dict[str, Any],
    message: str,
    code: str,
    constraint_ref: str,
) -> dict[str, Any]:
    return {
        "variant_id": "asset-candidates:row_fill",
        "source": "module_candidates",
        "status": "rejected",
        "recommended": False,
        "total_score": 0.0,
        "subscores": {},
        "placements": [],
        "candidate_ids": [candidate["candidate_id"]],
        "reasons": [message],
        "rejection_reasons": [
            _variant_rejection_reason(
                code=code,
                category="fit",
                message=message,
                constraint_ref=constraint_ref,
                actionable="Review asset dimensions, split the asset group, or keep using a manual module.",
            )
        ],
    }


def _variant_rejection_reason(
    *,
    code: str,
    category: str,
    message: str,
    constraint_ref: str,
    actionable: str,
) -> dict[str, str]:
    return {
        "code": code,
        "category": category,
        "severity": "error",
        "message": message,
        "constraint_ref": constraint_ref,
        "actionable": actionable,
    }

def _dimension_to_dict(dimension: Dimension3D) -> dict[str, float]:
    return {"x": round(dimension.x, 4), "y": round(dimension.y, 4), "z": round(dimension.z, 4)}
