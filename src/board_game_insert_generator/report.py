from __future__ import annotations

import json
from dataclasses import asdict, replace
from typing import Any

from board_game_insert_generator.feature_taxonomy import feature_taxonomy_to_dict, resolve_feature_taxonomy
from board_game_insert_generator.layout import LayoutError, generate_basic_layout
from board_game_insert_generator.models import (
    IMPLEMENTED_LAYOUT_STRATEGIES,
    Cavity,
    Dimension3D,
    Feature,
    InsertConfig,
    LayoutResult,
    ModuleRequest,
    Point3D,
)
from board_game_insert_generator.print_profiles import print_profile_label, print_profile_note
from board_game_insert_generator.tolerance import ToleranceError
from board_game_insert_generator.validation import ValidationError
from board_game_insert_generator.volumetric import VolumetricSummary, build_volumetric_summary

def layout_to_dict(config: InsertConfig, result: LayoutResult) -> dict[str, Any]:
    planned_cavities = _planned_cavities_by_instance(config, result)
    volumetric_summary = build_volumetric_summary(config)
    return {
        "project_name": config.project_name,
        "units": config.units,
        "source_path": config.source_path,
        "box": {
            "inner_dimensions_mm": _dim(config.box.inner_dimensions),
            "usable_height_mm": config.box.usable_height_mm,
            "lid_clearance_mm": config.box.lid_clearance_mm,
        },
        "layout": asdict(config.layout),
        "print_profile": {
            "id": config.print_profile,
            "label": print_profile_label(config.print_profile),
            "note": print_profile_note(config.print_profile),
        },
        "tolerances": asdict(config.tolerances),
        "defaults": asdict(config.defaults),
        "summary": {
            "requested_module_count": len(config.modules),
            "asset_count": len(config.assets),
            "expanded_instance_count": len(result.cells),
            "cell_count": len(result.cells),
            "printable_body_count": len(result.printable_bodies),
            "planned_cavity_count": sum(len(entries) for entries in planned_cavities.values()),
            "planned_feature_count": _planned_feature_count(planned_cavities),
            "rotated_cell_count": sum(1 for cell in result.cells if cell.rotated),
            "layout_footprint_mm": _dim(_layout_footprint(result)),
            "max_printable_height_mm": _max_printable_height(result),
            "warning_count": len(result.warnings),
            "warnings": list(result.warnings),
        },
        "layout_comparison": _layout_comparison(config, result),
        "variant_comparison": _variant_comparison(config, result),
        "volumetric_grid": volumetric_summary.to_dict() if volumetric_summary is not None else None,
        "assets": [_asset_to_dict(asset) for asset in config.assets],
        "module_requests": [
            {
                "id": module.id,
                "name": module.name,
                "functional_type": module.functional_type.value,
                "quantity": module.quantity,
                "min_dimensions_mm": _dim(module.min_dimensions),
                "desired_height_mm": _clean_float(module.desired_height_mm),
                "priority": module.priority,
                "allow_rotation": module.allow_rotation,
                "cavities": [_cavity_to_dict(cavity) for cavity in module.cavities],
            }
            for module in config.modules
        ],
        "cells": [
            {
                "module_id": cell.module_id,
                "instance_id": cell.instance_id,
                "label": cell.label,
                "functional_type": cell.functional_type.value,
                "origin_mm": _point(cell.origin),
                "size_mm": _dim(cell.size),
                "rotated": cell.rotated,
            }
            for cell in result.cells
        ],
        "printable_bodies": [
            {
                "module_id": body.module_id,
                "instance_id": body.instance_id,
                "body_id": body.body_id,
                "origin_mm": _point(body.origin),
                "size_mm": _dim(body.size),
                "offsets_mm": asdict(body.offsets),
                "primitive_count": len(body.primitive_volumes),
                "planned_cavities": [
                    _cavity_to_dict(cavity)
                    for cavity in planned_cavities.get(body.instance_id, ())
                ],
                "face_classifications": [
                    {
                        "face": classification.face.value,
                        "role": classification.role.value,
                        "reason": classification.reason,
                        "neighbor_instance_id": classification.neighbor_instance_id,
                    }
                    for classification in body.face_classifications
                ],
                "applied_tolerances": [
                    {
                        "face": application.face.value,
                        "role": application.role.value,
                        "offset_mm": _clean_float(application.offset_mm),
                        "rule_id": application.rule_id,
                        "clearance_source": application.clearance_source,
                        "receives_clearance": application.receives_clearance,
                        "reason": application.reason,
                    }
                    for application in body.tolerance_applications
                ],
            }
            for body in result.printable_bodies
        ],
    }

def layout_to_json(config: InsertConfig, result: LayoutResult) -> str:
    return json.dumps(layout_to_dict(config, result), indent=2, ensure_ascii=False)

def layout_to_markdown(config: InsertConfig, result: LayoutResult) -> str:
    planned_cavities = _planned_cavities_by_instance(config, result)
    volumetric_summary = build_volumetric_summary(config)
    planned_cavity_count = sum(len(entries) for entries in planned_cavities.values())
    planned_feature_count = _planned_feature_count(planned_cavities)
    lines = [
        f"# Layout report - {config.project_name}",
        "",
        f"- Units: `{config.units}`",
        f"- Source: `{config.source_path or 'in-memory'}`",
        f"- Box inner dimensions: {_format_dim(config.box.inner_dimensions)}",
        f"- Usable height: {config.box.usable_height_mm:.2f} mm",
        f"- Lid clearance: {config.box.lid_clearance_mm:.2f} mm",
        "",
        "## Summary",
        "",
        f"- Layout strategy: `{config.layout.strategy}`",
        f"- Requested modules: {len(config.modules)}",
        f"- Declared assets: {len(config.assets)}",
        f"- Generated instances: {len(result.cells)}",
        f"- Printable bodies: {len(result.printable_bodies)}",
        f"- Planned cavities: {planned_cavity_count}",
        f"- Planned cavity features: {planned_feature_count}",
        f"- Rotated cells: {sum(1 for cell in result.cells if cell.rotated)}",
        f"- Layout footprint: {_format_dim(_layout_footprint(result))}",
        f"- Max printable height: {_max_printable_height(result):.2f} mm",
        "",
        "## Layout comparison",
        "",
        (
            "Simple score: higher means a smaller XY footprint inside the box and fewer "
            "warnings. It is not a global optimization proof."
        ),
        "",
        "| Strategy | Status | Footprint | Occupation | Warnings | Simple score |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
        *_format_comparison_rows(_layout_comparison(config, result)),
        "",
        *_format_volumetric_grid_section(volumetric_summary),
        *_format_assets_section(config),
        "## Variant comparison",
        "",
        "Variants are deterministic report-only comparisons of already implemented layout strategies. They are not a global optimization proof.",
        "",
        "| Variant | Status | Total | Compact | Access | Reservations | Print | Setup | Confidence | Reasons |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        *_format_variant_rows(_variant_comparison(config, result)),
        "",
        "## Tolerance profile",
        "",
        f"- Print profile: `{config.print_profile}` ({print_profile_label(config.print_profile)})",
        f"- Profile note: {print_profile_note(config.print_profile)}",
        "",
        "| Setting | Value |",
        "| --- | ---: |",
        f"| Peripheral clearance | {config.tolerances.peripheral_clearance_mm:.2f} mm |",
        f"| Module gap | {config.tolerances.module_gap_mm:.2f} mm |",
        f"| Vertical lid clearance | {config.tolerances.vertical_lid_clearance_mm:.2f} mm |",
        f"| Printer compensation | {config.tolerances.printer_compensation_mm:.2f} mm |",
        "",
        "## Warnings",
        "",
    ]
    if result.warnings:
        for warning in result.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No warnings.")

    lines.extend(
        [
            "",
            "## Modules",
            "",
            "| Instance | Type | Cell origin | Cell size | Printable origin | Printable size | Offsets |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )

    bodies_by_instance = {body.instance_id: body for body in result.printable_bodies}
    for cell in result.cells:
        body = bodies_by_instance[cell.instance_id]
        lines.append(
            "| "
            f"{cell.instance_id} | "
            f"{cell.functional_type.value} | "
            f"{_format_point(cell.origin)} | "
            f"{_format_dim(cell.size)} | "
            f"{_format_point(body.origin)} | "
            f"{_format_dim(body.size)} | "
            f"{_format_offsets(body.offsets)} |"
        )

    lines.extend(
        [
            "",
            "## Planned cavities",
            "",
        ]
    )
    if planned_cavity_count:
        lines.extend(
            [
                "| Instance | Cavity | Type | Local origin | Size | Clearance | Source | Status |",
                "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
                *_format_cavity_rows(planned_cavities),
            ]
        )
    else:
        lines.append("- No planned cavities.")

    lines.extend(
        [
            "",
            "## Planned cavity features",
            "",
        ]
    )
    if planned_feature_count:
        lines.extend(
            [
                "| Instance | Cavity | Feature | Kind | Placement | Taxonomy | Position | Size | Radius | Status |",
                "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
                *_format_feature_rows(planned_cavities),
            ]
        )
    else:
        lines.append("- No planned cavity features.")

    lines.extend(
        [
            "",
            "## Face classifications",
            "",
            "| Instance | Roles |",
            "| --- | --- |",
        ]
    )
    for body in result.printable_bodies:
        lines.append(f"| {body.instance_id} | {_format_face_roles(body)} |")

    lines.extend(
        [
            "",
            "## Applied tolerances",
            "",
            "| Instance | Face | Role | Offset | Source | Rule |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for body in result.printable_bodies:
        lines.extend(_format_applied_tolerance_rows(body))

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Cell size is the theoretical layout reservation. Printable size is the body after "
            "face-level tolerance offsets. Face classifications drive explicit tolerance rules. "
            "Planned cavities and cavity features are abstract engine/CAD IR intent only; Fusion "
            "does not cut cavities, generate notches or create rounded floors yet in P5-M004. V0 "
            "does not guarantee an optimized layout or physically validated tolerances.",
        ]
    )
    return "\n".join(lines)
def _variant_comparison(config: InsertConfig, current_result: LayoutResult) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for entry in _layout_comparison(config, current_result):
        strategy = entry["strategy"]
        variant_id = f"layout:{strategy}"
        if entry["status"] != "ok":
            variants.append(
                {
                    "variant_id": variant_id,
                    "strategy": strategy,
                    "status": "rejected",
                    "total_score": 0.0,
                    "subscores": {},
                    "reasons": [entry.get("error", "Variant could not be generated.")],
                }
            )
            continue
        subscores = _variant_subscores(config, entry)
        total_score = _clean_float(sum(subscores.values()))
        variants.append(
            {
                "variant_id": variant_id,
                "strategy": strategy,
                "status": "explain_only",
                "total_score": total_score,
                "subscores": subscores,
                "reasons": _variant_reasons(config, entry),
            }
        )
    return variants


def _variant_subscores(config: InsertConfig, entry: dict[str, Any]) -> dict[str, float]:
    occupation = float(entry.get("occupation_percent", 100.0))
    cell_count = float(entry.get("cell_count", 0.0))
    warning_count = float(entry.get("warning_count", 0.0))
    return {
        "compactness": _clean_float(max(0.0, 30.0 - occupation * 0.2 - warning_count * 2.0)),
        "accessibility": _variant_accessibility_score(config),
        "reservation_integrity": _variant_reservation_score(config),
        "print_simplicity": _clean_float(max(0.0, 20.0 - cell_count * 1.5)),
        "setup": _variant_setup_score(config),
        "measurement_confidence": _variant_measurement_confidence_score(config),
    }


def _variant_accessibility_score(config: InsertConfig) -> float:
    summary = build_volumetric_summary(config)
    if summary is None:
        return 10.0
    if summary.to_dict()["removal_sequence"]:
        return 20.0
    return 12.0


def _variant_reservation_score(config: InsertConfig) -> float:
    grid = config.volumetric_grid
    if grid is None:
        return 10.0
    if grid.zones:
        return 20.0
    return 12.0


def _variant_setup_score(config: InsertConfig) -> float:
    if any(asset.containment_intent.value in {"access_first", "reserve"} for asset in config.assets):
        return 10.0
    summary = build_volumetric_summary(config)
    if summary is not None and summary.to_dict()["removal_sequence"]:
        return 8.0
    return 5.0


def _variant_measurement_confidence_score(config: InsertConfig) -> float:
    if not config.assets:
        return 10.0
    values = []
    for asset in config.assets:
        if asset.dimension_confidence.value == "exact":
            values.append(10.0)
        elif asset.dimension_confidence.value == "approximate":
            values.append(6.0)
        else:
            values.append(3.0)
    return _clean_float(sum(values) / len(values))


def _variant_reasons(config: InsertConfig, entry: dict[str, Any]) -> list[str]:
    reasons = [
        f"Strategy {entry['strategy']} produced {entry.get('cell_count', 0)} cells.",
        f"Layout occupation is {entry.get('occupation_percent', 0.0):.2f}% of box XY.",
    ]
    summary = build_volumetric_summary(config)
    if summary is not None and summary.to_dict()["removal_sequence"]:
        reasons.append("Declared removal sequence improves explainability but is not ergonomic validation.")
    if config.assets:
        reasons.append(f"{len(config.assets)} assets are loaded as metadata only, not converted into modules.")
    if entry.get("warning_count", 0):
        reasons.append(f"Variant has {entry['warning_count']} layout warnings.")
    return reasons


def _format_variant_rows(variants: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for variant in variants:
        subscores = variant.get("subscores", {})
        rows.append(
            "| "
            f"{variant['variant_id']} | "
            f"{variant['status']} | "
            f"{variant['total_score']:.2f} | "
            f"{subscores.get('compactness', 0.0):.2f} | "
            f"{subscores.get('accessibility', 0.0):.2f} | "
            f"{subscores.get('reservation_integrity', 0.0):.2f} | "
            f"{subscores.get('print_simplicity', 0.0):.2f} | "
            f"{subscores.get('setup', 0.0):.2f} | "
            f"{subscores.get('measurement_confidence', 0.0):.2f} | "
            f"{'; '.join(variant['reasons'])} |"
        )
    return rows

def _format_volumetric_grid_section(summary: VolumetricSummary | None) -> list[str]:
    if summary is None:
        return []

    grid = summary.grid
    lines = [
        "## Volumetric grid",
        "",
        f"- Unit size: {_format_dim(grid.unit_size_mm)}",
        f"- Grid units: {grid.size_units.x} x {grid.size_units.y} x {grid.size_units.z}",
        f"- Total cells: {summary.total_cell_count}",
        f"- Occupied cells: {summary.occupied_cell_count}",
        f"- Reserved cells: {summary.reserved_cell_count}",
        f"- Forbidden cells: {summary.forbidden_cell_count}",
        f"- Free cells: {summary.free_cell_count}",
        f"- Approximate free volume: {summary.approximate_free_volume_mm3:.2f} mm^3",
        f"- Support surfaces: {len(grid.support_surfaces)}",
        f"- Removal sequence entries: {len(summary.to_dict()['removal_sequence'])}",
        "",
        "### Layers",
        "",
    ]
    if grid.layers:
        lines.extend(
            [
                "| Layer | Z start | Z count | Role |",
                "| --- | ---: | ---: | --- |",
            ]
        )
        for layer in grid.layers:
            lines.append(f"| {layer.id} | {layer.z_start} | {layer.z_count} | {layer.role} |")
    else:
        lines.append("- No layers declared.")

    lines.extend(["", "### Module occupancy", ""])
    if grid.module_placements:
        lines.extend(
            [
                "| Placement | Module | Origin units | Size units | Layer | Removal | Access | Support |",
                "| --- | --- | ---: | ---: | --- | ---: | --- | --- |",
            ]
        )
        for placement in grid.module_placements:
            lines.append(
                "| "
                f"{placement.id} | "
                f"{placement.module_id} | "
                f"{_format_grid_point(placement.origin_units)} | "
                f"{_format_grid_size(placement.size_units)} | "
                f"{placement.layer_id or 'n/a'} | "
                f"{placement.removal_order if placement.removal_order is not None else 'n/a'} | "
                f"{placement.access_direction} | "
                f"{placement.support_surface_id or 'n/a'} |"
            )
    else:
        lines.append("- No module placements declared.")

    lines.extend(["", "### Reserved and forbidden zones", ""])
    if grid.zones:
        lines.extend(
            [
                "| Zone | Kind | Reservation | Asset | Purpose | Origin units | Size units | Layer | Removal | Access | Support |",
                "| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | --- | --- |",
            ]
        )
        for zone in grid.zones:
            lines.append(
                "| "
                f"{zone.id} | "
                f"{zone.kind.value} | "
                f"{zone.reservation_kind} | "
                f"{zone.asset_kind} | "
                f"{zone.purpose} | "
                f"{_format_grid_point(zone.origin_units)} | "
                f"{_format_grid_size(zone.size_units)} | "
                f"{zone.layer_id or 'n/a'} | "
                f"{zone.removal_order if zone.removal_order is not None else 'n/a'} | "
                f"{zone.access_direction} | "
                f"{zone.support_surface_id or 'n/a'} |"
            )
    else:
        lines.append("- No reserved or forbidden zones declared.")

    lines.extend(["", "### Support surfaces", ""])
    if grid.support_surfaces:
        lines.extend(
            [
                "| Surface | Owner | Face | Origin units | Size units | Layer | Purpose | Status |",
                "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for surface in grid.support_surfaces:
            lines.append(
                "| "
                f"{surface.id} | "
                f"{surface.owner_type.value}:{surface.owner_id} | "
                f"{surface.face.value} | "
                f"{_format_grid_point(surface.origin_units)} | "
                f"{_format_grid_size(surface.size_units)} | "
                f"{surface.layer_id or 'n/a'} | "
                f"{surface.purpose} | "
                "abstract_only; physical_validation=not_validated |"
            )
    else:
        lines.append("- No support surfaces declared.")

    removal_sequence = summary.to_dict()["removal_sequence"]
    lines.extend(["", "### Removal sequence", ""])
    if removal_sequence:
        lines.extend(
            [
                "| Order | Target | Type | Access | Support |",
                "| ---: | --- | --- | --- | --- |",
            ]
        )
        for entry in removal_sequence:
            lines.append(
                "| "
                f"{entry['order']} | "
                f"{entry['target_id']} | "
                f"{entry['target_type']} | "
                f"{entry['access_direction']} | "
                f"{entry['support_surface_id'] or 'n/a'} |"
            )
    else:
        lines.append("- No removal sequence declared.")
    lines.append("")
    return lines


def _format_grid_point(point: Any) -> str:
    return f"({point.x}, {point.y}, {point.z})"


def _format_grid_size(size: Any) -> str:
    return f"{size.x} x {size.y} x {size.z}"
def _asset_to_dict(asset) -> dict[str, Any]:
    return {
        "id": asset.id,
        "name": asset.name,
        "kind": asset.kind.value,
        "quantity": {
            "count": asset.quantity.count,
            "grouping": asset.quantity.grouping,
        },
        "dimensions_mm": _dim(asset.dimensions),
        "dimension_confidence": asset.dimension_confidence.value,
        "containment_intent": asset.containment_intent.value,
        "reservation_ref": asset.reservation_ref,
        "module_hint": asset.module_hint,
        "comment": asset.comment,
        "status": "loaded_only",
    }


def _format_assets_section(config: InsertConfig) -> list[str]:
    lines = ["## Assets", ""]
    if not config.assets:
        return lines + ["- No assets declared.", ""]
    lines.extend(
        [
            "| Asset | Kind | Quantity | Dimensions | Confidence | Intent | Reservation | Module hint | Status |",
            "| --- | --- | ---: | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for asset in config.assets:
        lines.append(
            "| "
            f"{asset.id} | "
            f"{asset.kind.value} | "
            f"{asset.quantity.count} {asset.quantity.grouping} | "
            f"{_format_dim(asset.dimensions)} | "
            f"{asset.dimension_confidence.value} | "
            f"{asset.containment_intent.value} | "
            f"{asset.reservation_ref or 'n/a'} | "
            f"{asset.module_hint or 'n/a'} | "
            "loaded_only |"
        )
    lines.append("")
    return lines

def _dim(dimensions: Dimension3D) -> dict[str, float]:
    return {"x": _clean_float(dimensions.x), "y": _clean_float(dimensions.y), "z": _clean_float(dimensions.z)}

def _point(point: Point3D) -> dict[str, float]:
    return {"x": _clean_float(point.x), "y": _clean_float(point.y), "z": _clean_float(point.z)}

def _cavity_to_dict(cavity: Cavity) -> dict[str, Any]:
    return {
        "id": cavity.id,
        "functional_type": cavity.functional_type.value,
        "local_origin_mm": _point(cavity.origin),
        "size_mm": _dim(cavity.size),
        "clearance_mm": _clean_float(cavity.clearance_mm),
        "clearance_source": cavity.clearance_source,
        "comment": cavity.comment,
        "features": [_feature_to_dict(feature) for feature in cavity.features],
        "status": "abstract_only",
    }

def _feature_to_dict(feature: Feature) -> dict[str, Any]:
    return {
        "id": feature.id,
        "kind": feature.kind.value,
        "placement": feature.placement,
        "taxonomy": feature_taxonomy_to_dict(feature),
        "position_mm": _point(feature.position),
        "size_mm": _dim(feature.size) if feature.size is not None else None,
        "radius_mm": _clean_float(feature.radius_mm) if feature.radius_mm is not None else None,
        "comment": feature.comment,
        "status": feature.status,
        "fusion_generation": feature.fusion_generation,
    }

def _planned_cavities_by_instance(
    config: InsertConfig,
    result: LayoutResult,
) -> dict[str, tuple[Cavity, ...]]:
    modules_by_id: dict[str, ModuleRequest] = {module.id: module for module in config.modules}
    planned: dict[str, tuple[Cavity, ...]] = {}
    for cell in result.cells:
        module = modules_by_id.get(cell.module_id)
        planned[cell.instance_id] = module.cavities if module is not None else ()
    return planned

def _clean_float(value: float) -> float:
    return round(value, 4)

def _format_dim(dimensions: Dimension3D) -> str:
    return f"{dimensions.x:.2f} x {dimensions.y:.2f} x {dimensions.z:.2f} mm"

def _format_point(point: Point3D) -> str:
    return f"({point.x:.2f}, {point.y:.2f}, {point.z:.2f})"

def _format_offsets(offsets: Any) -> str:
    return (
        f"x-{offsets.x_min:.2f}, x+{offsets.x_max:.2f}, "
        f"y-{offsets.y_min:.2f}, y+{offsets.y_max:.2f}, "
        f"z-{offsets.z_min:.2f}, z+{offsets.z_max:.2f}"
    )

def _planned_feature_count(planned_cavities: dict[str, tuple[Cavity, ...]]) -> int:
    return sum(len(cavity.features) for cavities in planned_cavities.values() for cavity in cavities)

def _format_cavity_rows(planned_cavities: dict[str, tuple[Cavity, ...]]) -> list[str]:
    rows: list[str] = []
    for instance_id, cavities in planned_cavities.items():
        for cavity in cavities:
            rows.append(
                "| "
                f"{instance_id} | "
                f"{cavity.id} | "
                f"{cavity.functional_type.value} | "
                f"{_format_point(cavity.origin)} | "
                f"{_format_dim(cavity.size)} | "
                f"{cavity.clearance_mm:.2f} mm | "
                f"{cavity.clearance_source} | "
                "abstract_only |"
            )
    return rows

def _format_feature_rows(planned_cavities: dict[str, tuple[Cavity, ...]]) -> list[str]:
    rows: list[str] = []
    for instance_id, cavities in planned_cavities.items():
        for cavity in cavities:
            for feature in cavity.features:
                rows.append(
                    "| "
                    f"{instance_id} | "
                    f"{cavity.id} | "
                    f"{feature.id} | "
                    f"{feature.kind.value} | "
                    f"{feature.placement} | "
                    f"{resolve_feature_taxonomy(feature).taxonomy.value} | "
                    f"{_format_point(feature.position)} | "
                    f"{_format_optional_dim(feature.size)} | "
                    f"{_format_optional_radius(feature)} | "
                    f"{feature.status}; fusion={resolve_feature_taxonomy(feature).fusion_status} |"
                )
    return rows

def _format_optional_dim(dimensions: Dimension3D | None) -> str:
    return _format_dim(dimensions) if dimensions is not None else "n/a"

def _format_optional_radius(feature: Feature) -> str:
    return f"{feature.radius_mm:.2f} mm" if feature.radius_mm is not None else "n/a"

def _format_face_roles(body: Any) -> str:
    roles = {
        classification.face.value: classification.role.value
        for classification in body.face_classifications
    }
    ordered_faces = ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")
    return ", ".join(f"{face}: {roles.get(face, 'unknown')}" for face in ordered_faces)

def _format_applied_tolerance_rows(body: Any) -> list[str]:
    return [
        "| "
        f"{body.instance_id} | "
        f"{application.face.value} | "
        f"{application.role.value} | "
        f"{application.offset_mm:.2f} mm | "
        f"{application.clearance_source} | "
        f"{application.rule_id} |"
        for application in body.tolerance_applications
    ]

def _layout_footprint(result: LayoutResult) -> Dimension3D:
    if not result.cells:
        return Dimension3D(x=0.0, y=0.0, z=0.0)
    return Dimension3D(
        x=max(cell.origin.x + cell.size.x for cell in result.cells),
        y=max(cell.origin.y + cell.size.y for cell in result.cells),
        z=max(cell.size.z for cell in result.cells),
    )

def _max_printable_height(result: LayoutResult) -> float:
    if not result.printable_bodies:
        return 0.0
    return max(body.size.z for body in result.printable_bodies)

def _layout_comparison(config: InsertConfig, current_result: LayoutResult) -> list[dict[str, Any]]:
    comparison: list[dict[str, Any]] = []
    for strategy in IMPLEMENTED_LAYOUT_STRATEGIES:
        if strategy == config.layout.strategy:
            result = current_result
        else:
            candidate = replace(config, layout=replace(config.layout, strategy=strategy))
            try:
                result = generate_basic_layout(candidate)
            except (LayoutError, ToleranceError, ValidationError) as exc:
                comparison.append(
                    {
                        "strategy": strategy,
                        "status": "error",
                        "error": str(exc),
                        "score": 0.0,
                    }
                )
                continue

        footprint = _layout_footprint(result)
        occupation_percent = _occupation_percent(config, footprint)
        comparison.append(
            {
                "strategy": strategy,
                "status": "ok",
                "cell_count": len(result.cells),
                "rotated_cell_count": sum(1 for cell in result.cells if cell.rotated),
                "footprint_mm": _dim(footprint),
                "occupation_percent": occupation_percent,
                "warning_count": len(result.warnings),
                "warnings": list(result.warnings),
                "score": _simple_layout_score(occupation_percent, len(result.warnings)),
            }
        )
    return comparison

def _format_comparison_rows(comparison: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for entry in comparison:
        if entry["status"] != "ok":
            rows.append(f"| `{entry['strategy']}` | error | n/a | n/a | n/a | 0.00 |")
            continue

        footprint = entry["footprint_mm"]
        footprint_text = (
            f"{footprint['x']:.2f} x {footprint['y']:.2f} x {footprint['z']:.2f} mm"
        )
        rows.append(
            "| "
            f"`{entry['strategy']}` | "
            f"{entry['status']} | "
            f"{footprint_text} | "
            f"{entry['occupation_percent']:.2f}% | "
            f"{entry['warning_count']} | "
            f"{entry['score']:.2f} |"
        )
    return rows

def _occupation_percent(config: InsertConfig, footprint: Dimension3D) -> float:
    box_area = config.box.inner_dimensions.x * config.box.inner_dimensions.y
    if box_area <= 0:
        return 0.0
    return _clean_float((footprint.x * footprint.y / box_area) * 100.0)

def _simple_layout_score(occupation_percent: float, warning_count: int) -> float:
    return _clean_float(max(0.0, 100.0 - occupation_percent - warning_count * 5.0))
