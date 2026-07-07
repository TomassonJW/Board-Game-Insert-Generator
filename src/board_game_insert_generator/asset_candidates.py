from __future__ import annotations

from math import ceil
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
    return {
        "module_id": f"generated:{suggested['id']}",
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
        "clearance_applied": {
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
        },
        "status": "generated_from_recommended_asset_variant",
        "fusion_generation": "use_printable_body_size_mm",
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
