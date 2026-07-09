from __future__ import annotations

from math import ceil, floor
from typing import Any

from board_game_insert_generator.models import (
    Asset,
    AssetKind,
    ContainmentIntent,
    Dimension3D,
    FunctionalType,
    GridPoint3D,
    GridSize3D,
    InsertConfig,
)
from board_game_insert_generator.volumetric import (
    CELL_FORBIDDEN,
    CELL_OCCUPIED,
    CELL_RESERVED,
    build_volumetric_summary,
    span_cells,
    span_fits_grid,
)


_RESERVATION_ONLY_KINDS = {AssetKind.BOARD, AssetKind.RULEBOOK, AssetKind.TRAY}
_FUNCTIONAL_TYPE_BY_ASSET_KIND = {
    AssetKind.CARDS: FunctionalType.CARDS,
    AssetKind.SLEEVED_CARDS: FunctionalType.SLEEVED_CARDS,
    AssetKind.TOKENS: FunctionalType.TOKENS,
    AssetKind.DICE: FunctionalType.DICE,
    AssetKind.MEEPLES: FunctionalType.MEEPLES,
}
_COUNT_AWARE_STACK_KINDS = {AssetKind.TOKENS, AssetKind.DICE, AssetKind.MEEPLES, AssetKind.OTHER}
_TOTAL_STACK_Z_KINDS = {AssetKind.CARDS, AssetKind.SLEEVED_CARDS}
_ASSET_FIT_CAVITY_SUPPORTED_FUNCTIONAL_TYPES = {
    FunctionalType.TOKENS.value,
    FunctionalType.DICE.value,
    FunctionalType.MEEPLES.value,
    FunctionalType.OTHER.value,
}
_ASSET_FIT_CAVITY_POLICY = "single_asset_fit_rectangular_cavity_v0"
_ASSET_COMPARTMENT_CAVITY_POLICY = "per_source_asset_rectangular_compartments_v0"
_ASSET_ACCESS_POLICY = "per_compartment_top_open_rectangular_notch_v0"
_ASSET_ACCESS_TARGET_NOTCH_WIDTH_MM = 18.0
_ASSET_ACCESS_MIN_NOTCH_WIDTH_MM = 6.0
_ASSET_ACCESS_TARGET_DEPTH_FROM_TOP_MM = 10.0
_ASSET_ACCESS_MIN_DEPTH_FROM_TOP_MM = 4.0


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
    suggested_module = _suggested_module_for_assets(
        config=config,
        candidate_id=f"asset-group-candidate:{representative.kind.value}:{representative.containment_intent.value}:{representative.dimension_confidence.value}",
        name=f"Grouped candidate for {representative.kind.value}",
        functional_type=_functional_type(representative),
        assets=assets,
        clearance_mm=clearance_mm,
        clearance_source=clearance_source,
    )
    warnings = list(suggested_module.get("warnings", []))
    if representative.dimension_confidence.value != "exact":
        warnings.append(
            f"Grouped assets use {representative.dimension_confidence.value} dimensions; candidate dimensions need human review."
        )
    storage_sizing = suggested_module.get("storage_sizing", {})
    return {
        "candidate_id": suggested_module["id"].replace("candidate-module:", "asset-group-candidate:"),
        "source_asset_ids": [asset.id for asset in assets],
        "status": "candidate_only",
        "derivation": storage_sizing.get("derivation", "asset_group_dimension_padding"),
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
            *suggested_module.get("sizing_reasons", []),
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
        reasons.extend(suggested_module.get("sizing_reasons", []))
        warnings.extend(suggested_module.get("warnings", []))

    storage_sizing = suggested_module.get("storage_sizing", {}) if suggested_module is not None else {}
    return {
        "candidate_id": f"asset-candidate:{asset.id}",
        "source_asset_ids": [asset.id],
        "status": status,
        "derivation": storage_sizing.get("derivation", "asset_dimension_padding"),
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



def _suggested_module_for_assets(
    *,
    config: InsertConfig,
    candidate_id: str,
    name: str,
    functional_type: FunctionalType,
    assets: list[Asset],
    clearance_mm: float,
    clearance_source: str,
) -> dict[str, Any]:
    kind = assets[0].kind if assets else AssetKind.OTHER
    if assets and all(asset.kind in _COUNT_AWARE_STACK_KINDS for asset in assets):
        return _count_aware_stacked_module_from_assets(
            config=config,
            candidate_id=candidate_id,
            name=name,
            functional_type=functional_type,
            assets=assets,
            clearance_mm=clearance_mm,
            clearance_source=clearance_source,
        )

    dimensions = Dimension3D(
        x=max(asset.dimensions.x for asset in assets),
        y=max(asset.dimensions.y for asset in assets),
        z=max(asset.dimensions.z for asset in assets),
    )
    suggested = _suggested_module_from_values(
        config=config,
        candidate_id=candidate_id,
        name=name,
        functional_type=functional_type,
        dimensions=dimensions,
        clearance_mm=clearance_mm,
        clearance_source=clearance_source,
    )
    if kind in _TOTAL_STACK_Z_KINDS:
        z_semantics = "total_stack_height_mm"
        reasons = [
            "Cards use z_mm as total provided stack height in P13-ASSET-M002; count is reported but not multiplied.",
            "Candidate dimensions are derived from card stack dimensions, profile clearance and geometry defaults.",
        ]
        warnings = [
            "Card count is not multiplied into z_mm; provide deck/package height as z_mm for cards and sleeved_cards."
        ] if sum(asset.quantity.count for asset in assets) > 1 else []
    else:
        z_semantics = "representative_asset_height_mm"
        reasons = ["Candidate dimensions are derived from asset dimensions, profile clearance and geometry defaults."]
        warnings = []
    suggested["storage_sizing"] = {
        "policy": "total_stack_z_v0" if kind in _TOTAL_STACK_Z_KINDS else "representative_asset_envelope_v0",
        "derivation": "asset_total_stack_z_padding" if kind in _TOTAL_STACK_Z_KINDS else "asset_dimension_padding",
        "count_aware_applied": False,
        "count_aware_storage_sizing": "partial" if kind in _TOTAL_STACK_Z_KINDS else "no",
        "z_mm_semantics": z_semantics,
        "total_count_read": sum(asset.quantity.count for asset in assets),
        "declared_capacity_guarantee": "not_guaranteed",
        "asset_diagnostics": [
            {
                "asset_id": asset.id,
                "count_read": asset.quantity.count,
                "dimensions_read_mm": _dimension_to_dict(asset.dimensions),
                "count_used_for_sizing": False,
                "z_mm_semantics": z_semantics,
                "warning": warnings[0] if warnings else None,
            }
            for asset in assets
        ],
        "warnings": warnings,
    }
    suggested["sizing_reasons"] = reasons
    suggested["warnings"] = warnings
    return suggested


def _count_aware_stacked_module_from_assets(
    *,
    config: InsertConfig,
    candidate_id: str,
    name: str,
    functional_type: FunctionalType,
    assets: list[Asset],
    clearance_mm: float,
    clearance_source: str,
) -> dict[str, Any]:
    wall = config.defaults.wall_thickness_mm
    floor = config.defaults.floor_thickness_mm
    max_fit_height = _count_aware_max_asset_fit_height(config, floor)
    max_content_width = max(0.0, config.box.inner_dimensions.x - wall * 2.0 - clearance_mm * 2.0)
    max_asset_fit_width = max(0.0, config.box.inner_dimensions.x - wall * 2.0)
    max_asset_fit_depth = max(0.0, config.box.inner_dimensions.y - wall * 2.0)
    pile_rectangles: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    warnings: list[str] = []

    for asset in assets:
        diagnostic = _count_aware_asset_stack_diagnostic(asset, clearance_mm, max_fit_height)
        diagnostics.append(diagnostic)
        warning = diagnostic.get("warning")
        if warning:
            warnings.append(str(warning))
        for pile_index in range(int(diagnostic["pile_count"])):
            pile_rectangles.append(
                {
                    "asset_id": asset.id,
                    "pile_index": pile_index + 1,
                    "x": asset.dimensions.x,
                    "y": asset.dimensions.y,
                }
            )

    packed = _pack_count_aware_piles(pile_rectangles, max_content_width)
    if not packed["fits_width"]:
        warnings.append(
            "Count-aware pile layout exceeds the available module content width; downstream row/grid placement must reject or report the overflow."
        )
    compartment_layout = _count_aware_compartment_layout(
        assets=assets,
        diagnostics=diagnostics,
        wall_mm=wall,
        floor_mm=floor,
        clearance_mm=clearance_mm,
        max_content_width_mm=max_content_width,
        max_asset_fit_width_mm=max_asset_fit_width,
        max_asset_fit_depth_mm=max_asset_fit_depth,
    )
    if compartment_layout["status"] == "planned":
        content_x = compartment_layout["asset_fit_size_mm"]["x"]
        content_y = compartment_layout["asset_fit_size_mm"]["y"]
        stack_height = compartment_layout["asset_fit_size_mm"]["z"]
        inner = Dimension3D(x=content_x, y=content_y, z=stack_height)
    else:
        content_x = packed["content_size_mm"]["x"]
        content_y = packed["content_size_mm"]["y"]
        stack_height = max((diagnostic["stack_height_mm"] for diagnostic in diagnostics), default=0.0)
        if compartment_layout.get("reason"):
            warnings.append(str(compartment_layout["reason"]))
        inner = Dimension3D(
            x=content_x + clearance_mm * 2.0,
            y=content_y + clearance_mm * 2.0,
            z=stack_height + clearance_mm,
        )
    outer = Dimension3D(
        x=inner.x + wall * 2.0,
        y=inner.y + wall * 2.0,
        z=inner.z + floor,
    )
    total_count = sum(asset.quantity.count for asset in assets)
    declared_capacity = sum(int(diagnostic["declared_capacity_count"]) for diagnostic in diagnostics)
    storage_sizing = {
        "policy": "stacked_rectangular_piles_v0",
        "derivation": "count_aware_stacked_asset_piles",
        "count_aware_applied": True,
        "count_aware_storage_sizing": "yes",
        "z_mm_semantics": "unit_item_thickness_for_tokens_dice_meeples_generic",
        "max_asset_fit_height_mm": round(max_fit_height, 4),
        "total_count_read": total_count,
        "declared_capacity_count": declared_capacity,
        "declared_capacity_guarantee": "heuristic_envelope_only_not_physical_cavity",
        "asset_diagnostics": diagnostics,
        "pile_layout": packed["pile_layout"],
        "asset_compartment_layout": compartment_layout,
        "content_footprint_mm": packed["content_size_mm"],
        "asset_fit_size_mm": _dimension_to_dict(inner),
        "module_size_mm": _dimension_to_dict(outer),
        "warnings": warnings,
    }
    return {
        "id": candidate_id,
        "name": name,
        "functional_type": functional_type.value,
        "min_dimensions_mm": _dimension_to_dict(outer),
        "inner_asset_envelope_mm": _dimension_to_dict(inner),
        "clearance_source": clearance_source,
        "status": "candidate_only_not_placed",
        "storage_sizing": storage_sizing,
        "sizing_reasons": [
            "Count-aware V0 treats each asset item as a rectangular stackable proxy.",
            "Items are split into vertical piles using the usable height, then pile footprints are row-packed in XY without backtracking.",
        ],
        "warnings": warnings,
    }


def _count_aware_max_asset_fit_height(config: InsertConfig, floor_thickness_mm: float) -> float:
    usable_height = min(config.box.usable_height_mm, config.box.inner_dimensions.z)
    if config.volumetric_grid is not None:
        free_z_span = _max_free_contiguous_z_span(config)
        if free_z_span > 0:
            usable_height = min(usable_height, free_z_span * config.volumetric_grid.unit_size_mm.z)
    return round(max(0.0, usable_height - floor_thickness_mm), 4)


def _max_free_contiguous_z_span(config: InsertConfig) -> int:
    grid = config.volumetric_grid
    if grid is None:
        return 0
    occupied = _initial_occupied_cells(config)
    max_span = 0
    for x in range(grid.size_units.x):
        for y in range(grid.size_units.y):
            current = 0
            for z in range(grid.size_units.z):
                if (x, y, z) in occupied:
                    current = 0
                    continue
                current += 1
                max_span = max(max_span, current)
    return max_span


def _count_aware_asset_stack_diagnostic(asset: Asset, clearance_mm: float, max_fit_height_mm: float) -> dict[str, Any]:
    usable_stack_height = max_fit_height_mm - clearance_mm
    if usable_stack_height <= 0:
        capacity_per_stack = 1
        warning = "No positive stack height remains after clearance; using one item per pile and expecting placement rejection if too tall."
    else:
        capacity_per_stack = max(1, floor(usable_stack_height / asset.dimensions.z))
        warning = None
    pile_count = max(1, ceil(asset.quantity.count / capacity_per_stack))
    items_per_pile = max(1, ceil(asset.quantity.count / pile_count))
    stack_height = round(items_per_pile * asset.dimensions.z, 4)
    if stack_height + clearance_mm > max_fit_height_mm:
        warning = "Computed stack height exceeds usable asset-fit height; generated module may be rejected by box/grid constraints."
    return {
        "asset_id": asset.id,
        "count_read": asset.quantity.count,
        "dimensions_read_mm": _dimension_to_dict(asset.dimensions),
        "count_used_for_sizing": True,
        "capacity_per_stack": capacity_per_stack,
        "pile_count": pile_count,
        "items_per_pile": items_per_pile,
        "declared_capacity_count": pile_count * capacity_per_stack,
        "stack_height_mm": stack_height,
        "pile_footprint_mm": {"x": asset.dimensions.x, "y": asset.dimensions.y},
        "z_mm_semantics": "unit_item_thickness",
        "warning": warning,
    }


def _pack_count_aware_piles(piles: list[dict[str, Any]], max_width_mm: float) -> dict[str, Any]:
    if not piles:
        return {"fits_width": True, "content_size_mm": {"x": 0.0, "y": 0.0, "z": 0.0}, "pile_layout": []}

    row_x = 0.0
    row_y = 0.0
    row_depth = 0.0
    content_x = 0.0
    fits_width = max_width_mm > 0
    layout: list[dict[str, Any]] = []
    for pile in sorted(piles, key=lambda item: (-item["y"], -item["x"], str(item["asset_id"]), int(item["pile_index"]))):
        width = float(pile["x"])
        depth = float(pile["y"])
        rotated = False
        if width > max_width_mm and depth <= max_width_mm:
            width, depth = depth, width
            rotated = True
        if width > max_width_mm:
            fits_width = False
        if row_x > 0 and row_x + width > max_width_mm:
            row_y += row_depth
            row_x = 0.0
            row_depth = 0.0
        layout.append(
            {
                "asset_id": pile["asset_id"],
                "pile_index": pile["pile_index"],
                "origin_mm": {"x": round(row_x, 4), "y": round(row_y, 4), "z": 0.0},
                "size_mm": {"x": round(width, 4), "y": round(depth, 4), "z": 0.0},
                "rotated": rotated,
            }
        )
        row_x += width
        row_depth = max(row_depth, depth)
        content_x = max(content_x, row_x)
    content_y = row_y + row_depth
    return {
        "fits_width": fits_width,
        "content_size_mm": {"x": round(content_x, 4), "y": round(content_y, 4), "z": 0.0},
        "pile_layout": layout,
    }


def _count_aware_compartment_layout(
    *,
    assets: list[Asset],
    diagnostics: list[dict[str, Any]],
    wall_mm: float,
    floor_mm: float,
    clearance_mm: float,
    max_content_width_mm: float,
    max_asset_fit_width_mm: float,
    max_asset_fit_depth_mm: float,
) -> dict[str, Any]:
    if not assets:
        return {"status": "refused", "reason": "No assets available for per-source compartments."}
    if wall_mm <= 0 or floor_mm <= 0:
        return {
            "status": "refused",
            "reason": "Per-source compartments require positive wall_thickness_mm and floor_thickness_mm.",
        }

    diagnostics_by_asset = {str(item.get("asset_id")): item for item in diagnostics}
    compartments: list[dict[str, Any]] = []
    cursor_x = 0.0
    max_y = 0.0
    max_z = 0.0
    warnings: list[str] = []
    for index, asset in enumerate(assets):
        diagnostic = diagnostics_by_asset.get(asset.id)
        if diagnostic is None:
            return {
                "status": "refused",
                "reason": f"Missing count-aware sizing diagnostic for asset {asset.id}.",
            }
        pile_rectangles = [
            {
                "asset_id": asset.id,
                "pile_index": pile_index + 1,
                "x": asset.dimensions.x,
                "y": asset.dimensions.y,
            }
            for pile_index in range(int(diagnostic["pile_count"]))
        ]
        packed = _pack_count_aware_piles(pile_rectangles, max_content_width_mm)
        if not packed["fits_width"]:
            warnings.append(f"Asset {asset.id} compartment pile layout exceeds available content width.")
        content_size = packed["content_size_mm"]
        size = {
            "x": round(content_size["x"] + clearance_mm * 2.0, 4),
            "y": round(content_size["y"] + clearance_mm * 2.0, 4),
            "z": round(float(diagnostic["stack_height_mm"]) + clearance_mm, 4),
        }
        local_origin = {
            "x": round(wall_mm + cursor_x, 4),
            "y": round(wall_mm, 4),
            "z": round(floor_mm, 4),
        }
        compartments.append(
            {
                "id": f"asset-compartment:{asset.id}",
                "asset_id": asset.id,
                "source_asset_ids": [asset.id],
                "count_read": diagnostic["count_read"],
                "dimensions_read_mm": dict(diagnostic["dimensions_read_mm"]),
                "count_used_for_sizing": True,
                "capacity_per_stack": diagnostic["capacity_per_stack"],
                "pile_count": diagnostic["pile_count"],
                "items_per_pile": diagnostic["items_per_pile"],
                "declared_capacity_count": diagnostic["declared_capacity_count"],
                "pile_layout": packed["pile_layout"],
                "pile_footprint_mm": dict(diagnostic["pile_footprint_mm"]),
                "local_origin_mm": local_origin,
                "size_mm": size,
                "retained_floor_mm": round(floor_mm, 4),
                "expected_floor_mm": round(floor_mm, 4),
                "expected_walls_mm": {},
                "internal_wall_thickness_mm": round(wall_mm, 4) if index > 0 else 0.0,
                "operation_kind": "subtract_rectangular_cavity",
                "warning": diagnostic.get("warning"),
            }
        )
        cursor_x += size["x"] + wall_mm
        max_y = max(max_y, size["y"])
        max_z = max(max_z, size["z"])

    row_layout = _asset_compartment_oriented_layout(compartments, wall_mm, axis="x")
    column_layout = _asset_compartment_oriented_layout(compartments, wall_mm, axis="y")
    shelf_layout = _asset_compartment_shelf_layout(
        compartments,
        wall_mm,
        max_asset_fit_width_mm=max_asset_fit_width_mm,
        max_asset_fit_depth_mm=max_asset_fit_depth_mm,
    )
    candidate_layouts = [row_layout, column_layout]
    if shelf_layout["status"] == "planned":
        candidate_layouts.append(shelf_layout)
    fitting_layouts = [
        layout
        for layout in candidate_layouts
        if _asset_compartment_layout_fits(
            layout,
            max_asset_fit_width_mm=max_asset_fit_width_mm,
            max_asset_fit_depth_mm=max_asset_fit_depth_mm,
        )
    ]
    if fitting_layouts:
        layout = min(
            fitting_layouts,
            key=lambda item: (
                item["asset_fit_size_mm"]["x"] * item["asset_fit_size_mm"]["y"],
                item["asset_fit_size_mm"]["y"],
                item["layout_strategy"],
            ),
        )
    else:
        attempts = [
            {
                "layout_strategy": layout["layout_strategy"],
                "asset_fit_size_mm": layout.get("asset_fit_size_mm", {}),
                "status": layout.get("status", "planned"),
                "reason": layout.get("reason"),
            }
            for layout in [row_layout, column_layout, shelf_layout]
        ]
        return {
            "status": "refused",
            "code": "ASSET_COMPARTMENTS_DO_NOT_FIT",
            "reason": (
                "Per-source compartments do not fit the available box XY asset-fit envelope "
                "with deterministic row, column or shelf layouts."
            ),
            "policy": _ASSET_COMPARTMENT_CAVITY_POLICY,
            "max_asset_fit_size_mm": {
                "x": round(max_asset_fit_width_mm, 4),
                "y": round(max_asset_fit_depth_mm, 4),
            },
            "layout_attempts": attempts,
            "warnings": warnings,
        }

    return {
        "status": "planned",
        "policy": _ASSET_COMPARTMENT_CAVITY_POLICY,
        "layout_strategy": layout["layout_strategy"],
        "compartment_count": len(compartments),
        "internal_wall_thickness_mm": round(wall_mm, 4),
        "asset_fit_size_mm": layout["asset_fit_size_mm"],
        "compartments": layout["compartments"],
        "warnings": warnings,
    }


def _asset_compartment_oriented_layout(
    compartments: list[dict[str, Any]],
    wall_mm: float,
    *,
    axis: str,
) -> dict[str, Any]:
    laid_out = []
    cursor = 0.0
    max_cross = 0.0
    max_z = 0.0
    for index, source in enumerate(compartments):
        compartment = dict(source)
        size = dict(compartment["size_mm"])
        if axis == "x":
            origin = {"x": round(wall_mm + cursor, 4), "y": round(wall_mm, 4), "z": round(compartment["local_origin_mm"]["z"], 4)}
            cursor += size["x"] + wall_mm
            max_cross = max(max_cross, size["y"])
            if index > 0:
                compartment["wall_role_x_min"] = "internal_wall"
            if index < len(compartments) - 1:
                compartment["wall_role_x_max"] = "internal_wall"
            compartment.pop("wall_role_y_min", None)
            compartment.pop("wall_role_y_max", None)
        else:
            origin = {"x": round(wall_mm, 4), "y": round(wall_mm + cursor, 4), "z": round(compartment["local_origin_mm"]["z"], 4)}
            cursor += size["y"] + wall_mm
            max_cross = max(max_cross, size["x"])
            if index > 0:
                compartment["wall_role_y_min"] = "internal_wall"
            if index < len(compartments) - 1:
                compartment["wall_role_y_max"] = "internal_wall"
            compartment.pop("wall_role_x_min", None)
            compartment.pop("wall_role_x_max", None)
        compartment["local_origin_mm"] = origin
        laid_out.append(compartment)
        max_z = max(max_z, size["z"])

    if laid_out:
        cursor -= wall_mm
    if axis == "x":
        asset_fit_size = {"x": round(cursor, 4), "y": round(max_cross, 4), "z": round(max_z, 4)}
    else:
        asset_fit_size = {"x": round(max_cross, 4), "y": round(cursor, 4), "z": round(max_z, 4)}

    for compartment in laid_out:
        origin = compartment["local_origin_mm"]
        size = compartment["size_mm"]
        compartment["expected_walls_mm"] = {
            "x_min": round(origin["x"], 4),
            "x_max": round(wall_mm + asset_fit_size["x"] - (origin["x"] - wall_mm) - size["x"], 4),
            "y_min": round(origin["y"], 4),
            "y_max": round(wall_mm + asset_fit_size["y"] - (origin["y"] - wall_mm) - size["y"], 4),
        }

    return {
        "status": "planned",
        "layout_strategy": "deterministic_single_row_by_source_asset_v0" if axis == "x" else "deterministic_single_column_by_source_asset_v0",
        "asset_fit_size_mm": asset_fit_size,
        "compartments": laid_out,
    }


def _asset_compartment_shelf_layout(
    compartments: list[dict[str, Any]],
    wall_mm: float,
    *,
    max_asset_fit_width_mm: float,
    max_asset_fit_depth_mm: float,
) -> dict[str, Any]:
    laid_out: list[dict[str, Any]] = []
    rows: list[list[int]] = []
    row: list[int] = []
    cursor_x = 0.0
    cursor_y = 0.0
    row_depth = 0.0
    max_x = 0.0
    max_z = 0.0

    for source in compartments:
        size = dict(source["size_mm"])
        if size["x"] > max_asset_fit_width_mm or size["y"] > max_asset_fit_depth_mm:
            return {
                "status": "refused",
                "layout_strategy": "deterministic_shelf_by_source_asset_v0",
                "asset_fit_size_mm": {"x": round(size["x"], 4), "y": round(size["y"], 4), "z": round(size["z"], 4)},
                "reason": f"Compartment {source.get('id', 'unknown')} is larger than the available asset-fit envelope.",
                "compartments": [],
            }
        if row and cursor_x + size["x"] > max_asset_fit_width_mm:
            rows.append(row)
            cursor_y += row_depth + wall_mm
            cursor_x = 0.0
            row_depth = 0.0
            row = []
        if cursor_y + size["y"] > max_asset_fit_depth_mm:
            return {
                "status": "refused",
                "layout_strategy": "deterministic_shelf_by_source_asset_v0",
                "asset_fit_size_mm": {
                    "x": round(max(max_x, cursor_x + size["x"]), 4),
                    "y": round(cursor_y + size["y"], 4),
                    "z": round(max(max_z, size["z"]), 4),
                },
                "reason": f"Compartment {source.get('id', 'unknown')} exceeds available depth in shelf layout.",
                "compartments": laid_out,
            }
        compartment = dict(source)
        compartment["local_origin_mm"] = {
            "x": round(wall_mm + cursor_x, 4),
            "y": round(wall_mm + cursor_y, 4),
            "z": round(compartment["local_origin_mm"]["z"], 4),
        }
        laid_out.append(compartment)
        row.append(len(laid_out) - 1)
        cursor_x += size["x"] + wall_mm
        row_depth = max(row_depth, size["y"])
        max_x = max(max_x, cursor_x - wall_mm)
        max_z = max(max_z, size["z"])

    if row:
        rows.append(row)
    asset_fit_size = {"x": round(max_x, 4), "y": round(cursor_y + row_depth, 4), "z": round(max_z, 4)}

    index_to_row: dict[int, int] = {}
    for row_index, row_items in enumerate(rows):
        for item_index in row_items:
            index_to_row[item_index] = row_index

    for item_index, compartment in enumerate(laid_out):
        origin = compartment["local_origin_mm"]
        size = compartment["size_mm"]
        row_index = index_to_row[item_index]
        row_items = rows[row_index]
        position_in_row = row_items.index(item_index)
        if position_in_row > 0:
            compartment["wall_role_x_min"] = "internal_wall"
        if position_in_row < len(row_items) - 1:
            compartment["wall_role_x_max"] = "internal_wall"
        if row_index > 0:
            compartment["wall_role_y_min"] = "internal_wall"
        if row_index < len(rows) - 1:
            compartment["wall_role_y_max"] = "internal_wall"
        compartment["expected_walls_mm"] = {
            "x_min": round(origin["x"], 4),
            "x_max": round(wall_mm + asset_fit_size["x"] - (origin["x"] - wall_mm) - size["x"], 4),
            "y_min": round(origin["y"], 4),
            "y_max": round(wall_mm + asset_fit_size["y"] - (origin["y"] - wall_mm) - size["y"], 4),
        }

    return {
        "status": "planned",
        "layout_strategy": "deterministic_shelf_by_source_asset_v0",
        "asset_fit_size_mm": asset_fit_size,
        "compartments": laid_out,
    }


def _asset_compartment_layout_fits(
    layout: dict[str, Any],
    *,
    max_asset_fit_width_mm: float,
    max_asset_fit_depth_mm: float,
) -> bool:
    size = layout.get("asset_fit_size_mm", {})
    try:
        return (
            layout.get("status", "planned") == "planned"
            and float(size.get("x", 0.0)) <= max_asset_fit_width_mm
            and float(size.get("y", 0.0)) <= max_asset_fit_depth_mm
        )
    except (TypeError, ValueError):
        return False


def _suggested_module(
    config: InsertConfig,
    asset: Asset,
    clearance_mm: float,
    clearance_source: str,
) -> dict[str, Any]:
    return _suggested_module_for_assets(
        config=config,
        candidate_id=f"candidate-module:{asset.id}",
        name=f"Candidate module for {asset.name}",
        functional_type=_functional_type(asset),
        assets=[asset],
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




def build_executable_asset_module_plan(config: InsertConfig) -> dict[str, Any]:
    """Convert the recommended asset variant into a bounded grid placement plan.

    The plan is pure metadata for reports and CAD IR. It does not mutate
    config.modules, does not recalculate tolerances, and does not authorize any
    Fusion geometry generation.
    """

    candidates = build_module_candidates_from_assets(config)
    variants = build_asset_candidate_variants(config)
    recommended_variant = recommended_asset_candidate_variant(variants)
    candidate_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}

    if recommended_variant is None:
        return {
            "plan_id": "asset-module-plan:recommended",
            "source_variant_id": None,
            "status": "rejected",
            "score": 0.0,
            "generated_modules": [],
            "placements": [],
            "rejected_modules": _plan_rejections_from_variants(variants),
            "summary": _plan_summary(
                grid=None,
                generated_count=0,
                placed_count=0,
                rejected_count=0,
                placed_cell_count=0,
                free_cell_count_before_plan=None,
            ),
            "reasons": ["No recommended asset candidate variant is available."],
        }

    generated_modules = [
        _generated_module_from_candidate(candidate_by_id[candidate_id])
        for candidate_id in recommended_variant.get("candidate_ids", ())
        if candidate_id in candidate_by_id
    ]

    grid = config.volumetric_grid
    if grid is None:
        return {
            "plan_id": "asset-module-plan:recommended",
            "source_variant_id": recommended_variant["variant_id"],
            "status": "planned_without_grid",
            "score": recommended_variant["total_score"],
            "generated_modules": generated_modules,
            "placements": [],
            "rejected_modules": [
                _module_rejection(
                    module["module_id"],
                    module["candidate_id"],
                    "NO_VOLUMETRIC_GRID",
                    "No volumetric_grid is declared, so generated asset modules cannot receive X/Y/Z unit placement.",
                    "volumetric_grid",
                    "Declare a volumetric_grid to make the recommended asset variant executable.",
                )
                for module in generated_modules
            ],
            "summary": _plan_summary(
                grid=None,
                generated_count=len(generated_modules),
                placed_count=0,
                rejected_count=len(generated_modules),
                placed_cell_count=0,
                free_cell_count_before_plan=None,
            ),
            "reasons": [
                "A recommended asset variant exists, but executable grid placement needs volumetric_grid.",
                "Generated modules remain abstract metadata only.",
            ],
        }

    occupied = _initial_occupied_cells(config)
    free_cell_count_before_plan = _grid_cell_count(grid.size_units) - len(occupied)
    placements: list[dict[str, Any]] = []
    rejected_modules: list[dict[str, Any]] = []

    for module in generated_modules:
        size_units = _module_size_units(module["dimensions_mm"], grid.unit_size_mm)
        origin = _first_free_origin(size_units, grid.size_units, occupied)
        if origin is None:
            rejected_modules.append(
                _module_rejection(
                    module["module_id"],
                    module["candidate_id"],
                    "DOES_NOT_FIT",
                    (
                        f"Generated module needs {_grid_size_to_dict(size_units)} units, but no free "
                        "non-reserved span is available in the declared volumetric grid."
                    ),
                    "volumetric_grid.size_units / volumetric_grid.module_placements / volumetric_grid.zones",
                    "Increase the grid, reduce/group assets differently, or move reserved/occupied spans.",
                )
            )
            continue

        cells = span_cells(origin, size_units)
        occupied.update(cells)
        placements.append(
            {
                "module_id": module["module_id"],
                "candidate_id": module["candidate_id"],
                "module_source": "asset_candidate",
                "placement_source": "grid_placement",
                "source_asset_ids": list(module["source_asset_ids"]),
                "origin_units": _grid_point_to_dict(origin),
                "size_units": _grid_size_to_dict(size_units),
                "origin_mm": _grid_origin_to_mm(origin, grid.unit_size_mm),
                "size_mm": dict(module["printable_body_size_mm"]),
                "theoretical_grid_origin_mm": _grid_origin_to_mm(origin, grid.unit_size_mm),
                "theoretical_grid_extent_mm": _grid_size_to_mm(size_units, grid.unit_size_mm),
                "asset_fit_size_mm": dict(module["asset_fit_size_mm"]),
                "storage_sizing": dict(module.get("storage_sizing", {})),
                "asset_fit_cavity": dict(module.get("asset_fit_cavity", {})),
                "printable_body_origin_mm": _grid_origin_to_mm(origin, grid.unit_size_mm),
                "printable_body_size_mm": dict(module["printable_body_size_mm"]),
                "source_size_mm": dict(module["printable_body_size_mm"]),
                "grid_slack_mm": _dimension_delta(
                    _grid_size_to_mm(size_units, grid.unit_size_mm),
                    module["printable_body_size_mm"],
                ),
                "clearance_applied": dict(module["clearance_applied"]),
                "sizing_policy": (
                    "size_mm is the generated printable body envelope; "
                    "theoretical_grid_extent_mm is the occupied grid span."
                ),
                "occupied_cells": len(cells),
                "status": "placed",
                "heuristic": "greedy_z_y_x_first_free_span",
            }
        )

    status = "placed" if placements and not rejected_modules else "partial" if placements else "rejected"
    score = _plan_score(recommended_variant["total_score"], len(generated_modules), len(placements), len(rejected_modules))
    return {
        "plan_id": "asset-module-plan:recommended",
        "source_variant_id": recommended_variant["variant_id"],
        "status": status,
        "score": score,
        "generated_modules": generated_modules,
        "placements": placements,
        "rejected_modules": rejected_modules,
        "summary": _plan_summary(
            grid=grid,
            generated_count=len(generated_modules),
            placed_count=len(placements),
            rejected_count=len(rejected_modules),
            placed_cell_count=sum(placement["occupied_cells"] for placement in placements),
            free_cell_count_before_plan=free_cell_count_before_plan,
            placements=placements,
        ),
        "reasons": [
            "Recommended asset candidate variant was converted into generated module metadata.",
            "Generated modules were placed with a bounded greedy grid scan; no backtracking or global optimization was used.",
            "The plan is abstract CAD IR/report metadata and does not change Fusion generation.",
        ],
    }

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


def _generated_module_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    suggested = candidate["suggested_module"]
    constraints = candidate.get("constraints", {})
    dimensions_mm = dict(suggested["min_dimensions_mm"])
    inner_asset_envelope_mm = dict(suggested["inner_asset_envelope_mm"])
    module_id = f"generated:{suggested['id']}"
    clearance_applied = {
        "internal_asset_clearance_mm": constraints.get("clearance_mm", 0.0),
        "internal_asset_clearance_source": constraints.get("clearance_source", "unknown"),
        "wall_thickness_mm": constraints.get("wall_thickness_mm", 0.0),
        "floor_thickness_mm": constraints.get("floor_thickness_mm", 0.0),
        "peripheral_clearance_mm": 0.0,
        "inter_module_gap_mm": 0.0,
        "note": (
            "Generated asset modules use asset-fit clearance plus wall/floor defaults. "
            "Face-role peripheral and inter-module tolerance shrinking is not applied "
            "to this asset-first grid plan yet."
        ),
    }
    return {
        "module_id": module_id,
        "candidate_id": candidate["candidate_id"],
        "module_source": "asset_candidate",
        "name": suggested["name"],
        "functional_type": suggested["functional_type"],
        "source_asset_ids": list(candidate["source_asset_ids"]),
        "contained_asset_count": candidate["quantity"]["count"],
        "dimensions_mm": dimensions_mm,
        "inner_asset_envelope_mm": inner_asset_envelope_mm,
        "asset_fit_size_mm": inner_asset_envelope_mm,
        "printable_body_size_mm": dimensions_mm,
        "storage_sizing": dict(suggested.get("storage_sizing", {})),
        "asset_fit_cavity": _asset_cavity_payload(
            module_id=module_id,
            functional_type=suggested["functional_type"],
            asset_fit_size_mm=inner_asset_envelope_mm,
            module_size_mm=dimensions_mm,
            clearance_applied=clearance_applied,
            storage_sizing=suggested.get("storage_sizing", {}),
        ),
        "clearance_applied": clearance_applied,
        "status": "generated_from_recommended_asset_variant",
        "fusion_generation": "use_printable_body_size_mm",
    }




def _asset_cavity_payload(
    *,
    module_id: str,
    functional_type: str,
    asset_fit_size_mm: dict[str, float],
    module_size_mm: dict[str, float],
    clearance_applied: dict[str, Any],
    storage_sizing: dict[str, Any],
) -> dict[str, Any]:
    compartment_payload = _asset_compartment_cavity_payload(
        module_id=module_id,
        functional_type=functional_type,
        module_size_mm=module_size_mm,
        clearance_applied=clearance_applied,
        storage_sizing=storage_sizing,
    )
    if compartment_payload.get("status") == "planned":
        return compartment_payload
    layout = storage_sizing.get("asset_compartment_layout") if isinstance(storage_sizing, dict) else None
    if isinstance(layout, dict) and layout.get("status") == "refused":
        return {
            **compartment_payload,
            "fallback_suppressed": True,
            "fallback_suppressed_reason": (
                "Per-source asset compartments were required but refused; BGIG does not fall back "
                "to a single misleading asset-fit cavity."
            ),
            "layout_refusal": layout,
        }
    fallback = _asset_fit_cavity_payload(
        module_id=module_id,
        functional_type=functional_type,
        asset_fit_size_mm=asset_fit_size_mm,
        module_size_mm=module_size_mm,
        clearance_applied=clearance_applied,
    )
    return {
        **fallback,
        "fallback_from_policy": _ASSET_COMPARTMENT_CAVITY_POLICY,
        "fallback_reason": compartment_payload.get("reason") or compartment_payload.get("code") or "Per-source compartments were not available.",
    }


def _asset_access_notch_payload(
    *,
    compartment: dict[str, Any],
    wall_mm: float,
    floor_mm: float,
) -> dict[str, Any]:
    compartment_id = str(compartment.get("id") or "unknown-compartment")
    asset_id = str(compartment.get("asset_id") or "unknown-asset")
    origin = compartment.get("local_origin_mm", {})
    size = compartment.get("size_mm", {})
    base = {
        "id": f"asset-access-notch:{asset_id}",
        "policy": _ASSET_ACCESS_POLICY,
        "asset_id": asset_id,
        "compartment_id": compartment_id,
        "target_wall": "front",
        "placement": "front_center",
        "coordinate_frame": "compartment.local",
        "operation_kind": "rectangular_finger_notch_cut",
        "retained_floor_mm": round(floor_mm, 4),
    }
    try:
        origin_y = float(origin.get("y", 0.0))
        cavity_width = float(size.get("x", 0.0))
        cavity_height = float(size.get("z", 0.0))
    except (TypeError, ValueError):
        return {
            **base,
            "status": "refused",
            "notch_generated": False,
            "reason": "Compartment origin/size are not numeric enough to place an access notch.",
        }

    if origin_y > wall_mm + 0.0001:
        return {
            **base,
            "status": "refused",
            "notch_generated": False,
            "reason": "Compartment is not adjacent to the module front wall; V0 refuses to cut through another compartment or internal wall.",
        }
    if origin_y <= 0:
        return {
            **base,
            "status": "refused",
            "notch_generated": False,
            "reason": "Front wall thickness is not positive, so a safe access notch cut cannot be planned.",
        }

    side_margin_mm = max(wall_mm, 0.0)
    available_width = cavity_width - side_margin_mm * 2.0
    if available_width < _ASSET_ACCESS_MIN_NOTCH_WIDTH_MM:
        return {
            **base,
            "status": "refused",
            "notch_generated": False,
            "width_mm": round(max(available_width, 0.0), 4),
            "reason": (
                f"Compartment is too narrow for access notch V0: available width {available_width:.2f} mm "
                f"is below {_ASSET_ACCESS_MIN_NOTCH_WIDTH_MM:.2f} mm after side margins."
            ),
        }
    if cavity_height < _ASSET_ACCESS_MIN_DEPTH_FROM_TOP_MM:
        return {
            **base,
            "status": "refused",
            "notch_generated": False,
            "depth_from_top_mm": round(max(cavity_height, 0.0), 4),
            "reason": (
                f"Compartment is too shallow for access notch V0: depth {cavity_height:.2f} mm "
                f"is below {_ASSET_ACCESS_MIN_DEPTH_FROM_TOP_MM:.2f} mm."
            ),
        }

    width_mm = round(min(_ASSET_ACCESS_TARGET_NOTCH_WIDTH_MM, available_width), 4)
    depth_from_top_mm = round(min(_ASSET_ACCESS_TARGET_DEPTH_FROM_TOP_MM, cavity_height), 4)
    position_x = round((cavity_width - width_mm) / 2.0, 4)
    cut_depth_mm = round(origin_y, 4)
    return {
        **base,
        "status": "planned",
        "notch_generated": True,
        "width_mm": width_mm,
        "depth_from_top_mm": depth_from_top_mm,
        "target_wall_thickness_mm": cut_depth_mm,
        "position_mm": {"x": position_x, "y": 0.0, "z": 0.0},
        "size_mm": {"x": width_mm, "y": cut_depth_mm, "z": depth_from_top_mm},
        "bbox_size_mm": {"x": width_mm, "y": cut_depth_mm, "z": depth_from_top_mm},
        "reason": "Compartment touches the module front wall and has enough width/height for a rectangular top-open access notch V0.",
    }

def _asset_compartment_cavity_payload(
    *,
    module_id: str,
    functional_type: str,
    module_size_mm: dict[str, float],
    clearance_applied: dict[str, Any],
    storage_sizing: dict[str, Any],
) -> dict[str, Any]:
    wall = float(clearance_applied.get("wall_thickness_mm", 0.0) or 0.0)
    floor = float(clearance_applied.get("floor_thickness_mm", 0.0) or 0.0)
    base = {
        "id": "asset-source-compartments",
        "policy": _ASSET_COMPARTMENT_CAVITY_POLICY,
        "module_id": module_id,
        "functional_type": functional_type,
        "item_cavity_policy": "no_individual_item_or_pile_cavities_v0",
        "asset_items_visualized": False,
        "asset_compartments_generated": True,
        "fusion_generation": "subtract_rectangular_cavity",
        "operation_kind": "subtract_rectangular_cavity",
        "coordinate_frame": "body.local",
    }
    if functional_type not in _ASSET_FIT_CAVITY_SUPPORTED_FUNCTIONAL_TYPES:
        return {
            **base,
            "status": "refused",
            "code": "UNSUPPORTED_ASSET_COMPARTMENT_TYPE",
            "reason": f"Per-source compartment cavity V0 supports tokens/dice/meeples/generic, got {functional_type}.",
        }
    layout = storage_sizing.get("asset_compartment_layout") if isinstance(storage_sizing, dict) else None
    if not isinstance(layout, dict) or layout.get("status") != "planned":
        return {
            **base,
            "status": "refused",
            "code": "ASSET_COMPARTMENT_LAYOUT_UNAVAILABLE",
            "reason": "Count-aware per-source compartment layout is unavailable for this generated module.",
        }
    compartments = [dict(item) for item in layout.get("compartments", []) if isinstance(item, dict)]
    if not compartments:
        return {
            **base,
            "status": "refused",
            "code": "ASSET_COMPARTMENT_LAYOUT_EMPTY",
            "reason": "Count-aware per-source compartment layout produced no compartments.",
        }
    errors: list[str] = []
    for compartment in compartments:
        origin = compartment.get("local_origin_mm", {})
        size = compartment.get("size_mm", {})
        if not isinstance(origin, dict) or not isinstance(size, dict):
            errors.append(f"{compartment.get('id', 'unknown')} missing local_origin_mm or size_mm")
            continue
        size = dict(size)
        size["z"] = round(module_size_mm["z"] - floor, 4)
        compartment["size_mm"] = size
        retained_floor = round(module_size_mm["z"] - float(size.get("z", 0.0)), 4)
        expected_walls = {
            "x_min": round(float(origin.get("x", 0.0)), 4),
            "x_max": round(module_size_mm["x"] - float(origin.get("x", 0.0)) - float(size.get("x", 0.0)), 4),
            "y_min": round(float(origin.get("y", 0.0)), 4),
            "y_max": round(module_size_mm["y"] - float(origin.get("y", 0.0)) - float(size.get("y", 0.0)), 4),
        }
        compartment["retained_floor_mm"] = retained_floor
        compartment["expected_floor_mm"] = round(floor, 4)
        compartment["expected_walls_mm"] = expected_walls
        compartment["asset_access_notch"] = _asset_access_notch_payload(
            compartment=compartment,
            wall_mm=wall,
            floor_mm=floor,
        )
        if float(origin.get("x", 0.0)) + float(size.get("x", 0.0)) > module_size_mm["x"]:
            errors.append(f"{compartment.get('id', 'unknown')} exceeds module width")
        if float(origin.get("y", 0.0)) + float(size.get("y", 0.0)) > module_size_mm["y"]:
            errors.append(f"{compartment.get('id', 'unknown')} exceeds module depth")
        if float(size.get("z", 0.0)) >= module_size_mm["z"]:
            errors.append(f"{compartment.get('id', 'unknown')} must be lower than module height")
        if retained_floor < floor:
            errors.append(f"{compartment.get('id', 'unknown')} retained floor {retained_floor:.4f} mm is below floor_thickness_mm {floor:.4f} mm")
    if errors:
        return {
            **base,
            "status": "refused",
            "code": "ASSET_COMPARTMENT_CAVITY_INVALID_BOUNDS",
            "reason": "; ".join(errors),
            "compartments": compartments,
        }
    asset_access_notches_planned = sum(
        1
        for compartment in compartments
        if isinstance(compartment.get("asset_access_notch"), dict)
        and compartment["asset_access_notch"].get("status") == "planned"
    )
    asset_access_notches_refused = sum(
        1
        for compartment in compartments
        if isinstance(compartment.get("asset_access_notch"), dict)
        and compartment["asset_access_notch"].get("status") == "refused"
    )
    return {
        **base,
        "status": "planned",
        "layout_strategy": layout.get("layout_strategy", "deterministic_single_row_by_source_asset_v0"),
        "compartment_count": len(compartments),
        "asset_compartment_cavities_planned": len(compartments),
        "asset_fit_size_mm": dict(layout.get("asset_fit_size_mm", {})),
        "internal_wall_thickness_mm": round(wall, 4),
        "asset_access_policy": _ASSET_ACCESS_POLICY,
        "asset_access_features_generated": asset_access_notches_planned > 0,
        "asset_access_notches_planned": asset_access_notches_planned,
        "asset_access_notches_refused": asset_access_notches_refused,
        "compartments": compartments,
        "clearance_source": clearance_applied.get("internal_asset_clearance_source", "unknown"),
        "warning": "Per-source asset compartments V0; individual asset items and piles are not cut.",
    }

def _asset_fit_cavity_payload(
    *,
    module_id: str,
    functional_type: str,
    asset_fit_size_mm: dict[str, float],
    module_size_mm: dict[str, float],
    clearance_applied: dict[str, Any],
) -> dict[str, Any]:
    wall = float(clearance_applied.get("wall_thickness_mm", 0.0) or 0.0)
    floor = float(clearance_applied.get("floor_thickness_mm", 0.0) or 0.0)
    base = {
        "id": "asset-fit-cavity",
        "policy": _ASSET_FIT_CAVITY_POLICY,
        "module_id": module_id,
        "functional_type": functional_type,
        "item_cavity_policy": "no_individual_item_or_pile_cavities_v0",
        "asset_items_visualized": False,
        "fusion_generation": "subtract_rectangular_cavity",
        "operation_kind": "subtract_rectangular_cavity",
        "coordinate_frame": "body.local",
    }
    if functional_type not in _ASSET_FIT_CAVITY_SUPPORTED_FUNCTIONAL_TYPES:
        return {
            **base,
            "status": "refused",
            "code": "UNSUPPORTED_ASSET_CAVITY_TYPE",
            "reason": f"Asset-fit cavity V0 supports tokens/dice/meeples/generic, got {functional_type}.",
        }
    if wall <= 0 or floor <= 0:
        return {
            **base,
            "status": "refused",
            "code": "MISSING_WALL_OR_FLOOR_THICKNESS",
            "reason": "Asset-fit cavity requires positive wall_thickness_mm and floor_thickness_mm.",
        }
    local_origin = {"x": round(wall, 4), "y": round(wall, 4), "z": round(floor, 4)}
    retained_floor = round(module_size_mm["z"] - asset_fit_size_mm["z"], 4)
    expected_walls = {
        "x_min": round(local_origin["x"], 4),
        "x_max": round(module_size_mm["x"] - local_origin["x"] - asset_fit_size_mm["x"], 4),
        "y_min": round(local_origin["y"], 4),
        "y_max": round(module_size_mm["y"] - local_origin["y"] - asset_fit_size_mm["y"], 4),
    }
    errors: list[str] = []
    if local_origin["x"] + asset_fit_size_mm["x"] > module_size_mm["x"]:
        errors.append("asset_fit.x exceeds module width after wall offset")
    if local_origin["y"] + asset_fit_size_mm["y"] > module_size_mm["y"]:
        errors.append("asset_fit.y exceeds module depth after wall offset")
    if asset_fit_size_mm["z"] >= module_size_mm["z"]:
        errors.append("asset_fit.z must be lower than module height")
    if retained_floor < floor:
        errors.append(f"retained floor {retained_floor:.4f} mm is below floor_thickness_mm {floor:.4f} mm")
    too_thin = [name for name, value in expected_walls.items() if value < wall - 0.0001]
    if too_thin:
        errors.append("wall thinner than wall_thickness_mm: " + ", ".join(too_thin))
    if errors:
        return {
            **base,
            "status": "refused",
            "code": "ASSET_FIT_CAVITY_INVALID_BOUNDS",
            "reason": "; ".join(errors),
            "local_origin_mm": local_origin,
            "size_mm": dict(asset_fit_size_mm),
            "retained_floor_mm": retained_floor,
            "expected_walls_mm": expected_walls,
        }
    return {
        **base,
        "status": "planned",
        "local_origin_mm": local_origin,
        "size_mm": dict(asset_fit_size_mm),
        "retained_floor_mm": retained_floor,
        "expected_floor_mm": round(floor, 4),
        "expected_walls_mm": expected_walls,
        "clearance_source": clearance_applied.get("internal_asset_clearance_source", "unknown"),
        "warning": "Single asset-fit cavity only; individual asset items and piles are not cut in P13-ASSET-M003.",
    }


def _initial_occupied_cells(config: InsertConfig) -> set[tuple[int, int, int]]:
    summary = build_volumetric_summary(config)
    if summary is None:
        return set()
    occupied_states = {CELL_OCCUPIED, CELL_RESERVED, CELL_FORBIDDEN}
    return {
        (cell.coordinate.x, cell.coordinate.y, cell.coordinate.z)
        for cell in summary.cells
        if cell.state in occupied_states
    }


def _module_size_units(dimensions_mm: dict[str, float], unit_size_mm: Dimension3D) -> GridSize3D:
    return GridSize3D(
        x=max(1, ceil(dimensions_mm["x"] / unit_size_mm.x)),
        y=max(1, ceil(dimensions_mm["y"] / unit_size_mm.y)),
        z=max(1, ceil(dimensions_mm["z"] / unit_size_mm.z)),
    )


def _first_free_origin(
    size_units: GridSize3D,
    grid_size: GridSize3D,
    occupied: set[tuple[int, int, int]],
) -> GridPoint3D | None:
    for z in range(grid_size.z):
        for y in range(grid_size.y):
            for x in range(grid_size.x):
                origin = GridPoint3D(x=x, y=y, z=z)
                if not span_fits_grid(origin, size_units, grid_size):
                    continue
                if span_cells(origin, size_units).isdisjoint(occupied):
                    return origin
    return None


def _plan_score(base_score: float, generated_count: int, placed_count: int, rejected_count: int) -> float:
    if generated_count <= 0:
        return 0.0
    placement_ratio = placed_count / generated_count
    penalty = rejected_count * 15.0
    return round(max(0.0, base_score * placement_ratio - penalty), 4)


def _plan_summary(
    *,
    grid,
    generated_count: int,
    placed_count: int,
    rejected_count: int,
    placed_cell_count: int,
    free_cell_count_before_plan: int | None,
    placements: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    cell_volume = grid.unit_size_mm.x * grid.unit_size_mm.y * grid.unit_size_mm.z if grid is not None else 0.0
    total_cells = grid.size_units.x * grid.size_units.y * grid.size_units.z if grid is not None else 0
    placed_volume = placed_cell_count * cell_volume
    placement_summary = _placement_layer_summary(placements or [])
    return {
        "generated_module_count": generated_count,
        "placed_module_count": placed_count,
        "rejected_module_count": rejected_count,
        "grid_total_cell_count": total_cells,
        "placed_cell_count": placed_cell_count,
        "placed_cell_volume_mm3_approx": round(placed_volume, 4),
        "free_cell_count_before_plan": free_cell_count_before_plan,
        **placement_summary,
    }


def _placement_layer_summary(placements: list[dict[str, Any]]) -> dict[str, Any]:
    height_values = {
        round(placement["size_mm"]["z"], 4)
        for placement in placements
        if isinstance(placement.get("size_mm"), dict)
    }
    return {
        "multi_layer_module_count": sum(
            1
            for placement in placements
            if isinstance(placement.get("size_units"), dict)
            and placement["size_units"].get("z", 0) > 1
        ),
        "z_placed_module_count": sum(
            1
            for placement in placements
            if isinstance(placement.get("origin_units"), dict)
            and placement["origin_units"].get("z", 0) > 0
        ),
        "height_variant_count": len(height_values),
    }

def _grid_cell_count(size: GridSize3D) -> int:
    return size.x * size.y * size.z

def _module_rejection(
    module_id: str,
    candidate_id: str,
    code: str,
    message: str,
    constraint_ref: str,
    actionable: str,
) -> dict[str, Any]:
    return {
        "module_id": module_id,
        "candidate_id": candidate_id,
        "code": code,
        "category": "volumetric_placement",
        "severity": "error",
        "message": message,
        "constraint_ref": constraint_ref,
        "actionable": actionable,
    }


def _plan_rejections_from_variants(variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rejections: list[dict[str, Any]] = []
    for variant in variants:
        for reason in variant.get("rejection_reasons", ()):
            rejections.append(
                {
                    "module_id": None,
                    "candidate_id": ",".join(variant.get("candidate_ids", ())) or None,
                    "code": reason["code"],
                    "category": reason["category"],
                    "severity": reason["severity"],
                    "message": reason["message"],
                    "constraint_ref": reason["constraint_ref"],
                    "actionable": reason["actionable"],
                }
            )
    return rejections


def _grid_point_to_dict(point: GridPoint3D) -> dict[str, int]:
    return {"x": point.x, "y": point.y, "z": point.z}


def _grid_size_to_dict(size: GridSize3D) -> dict[str, int]:
    return {"x": size.x, "y": size.y, "z": size.z}


def _grid_origin_to_mm(origin: GridPoint3D, unit_size_mm: Dimension3D) -> dict[str, float]:
    return {
        "x": round(origin.x * unit_size_mm.x, 4),
        "y": round(origin.y * unit_size_mm.y, 4),
        "z": round(origin.z * unit_size_mm.z, 4),
    }


def _grid_size_to_mm(size: GridSize3D, unit_size_mm: Dimension3D) -> dict[str, float]:
    return {
        "x": round(size.x * unit_size_mm.x, 4),
        "y": round(size.y * unit_size_mm.y, 4),
        "z": round(size.z * unit_size_mm.z, 4),
    }

def _dimension_delta(outer: dict[str, float], inner: dict[str, float]) -> dict[str, float]:
    return {
        "x": round(outer["x"] - inner["x"], 4),
        "y": round(outer["y"] - inner["y"], 4),
        "z": round(outer["z"] - inner["z"], 4),
    }

def _dimension_to_dict(dimension: Dimension3D) -> dict[str, float]:
    return {"x": round(dimension.x, 4), "y": round(dimension.y, 4), "z": round(dimension.z, 4)}
