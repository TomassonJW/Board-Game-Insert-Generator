from __future__ import annotations

import json
from dataclasses import asdict, replace
from typing import Any

from board_game_insert_generator.layout import LayoutError, generate_basic_layout
from board_game_insert_generator.models import (
    IMPLEMENTED_LAYOUT_STRATEGIES,
    Dimension3D,
    InsertConfig,
    LayoutResult,
    Point3D,
)
from board_game_insert_generator.tolerance import ToleranceError
from board_game_insert_generator.validation import ValidationError


def layout_to_dict(config: InsertConfig, result: LayoutResult) -> dict[str, Any]:
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
        "tolerances": asdict(config.tolerances),
        "defaults": asdict(config.defaults),
        "summary": {
            "requested_module_count": len(config.modules),
            "expanded_instance_count": len(result.cells),
            "cell_count": len(result.cells),
            "printable_body_count": len(result.printable_bodies),
            "rotated_cell_count": sum(1 for cell in result.cells if cell.rotated),
            "layout_footprint_mm": _dim(_layout_footprint(result)),
            "max_printable_height_mm": _max_printable_height(result),
            "warning_count": len(result.warnings),
            "warnings": list(result.warnings),
        },
        "layout_comparison": _layout_comparison(config, result),
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
                "face_classifications": [
                    {
                        "face": classification.face.value,
                        "role": classification.role.value,
                        "reason": classification.reason,
                        "neighbor_instance_id": classification.neighbor_instance_id,
                    }
                    for classification in body.face_classifications
                ],
            }
            for body in result.printable_bodies
        ],
    }


def layout_to_json(config: InsertConfig, result: LayoutResult) -> str:
    return json.dumps(layout_to_dict(config, result), indent=2, ensure_ascii=False)


def layout_to_markdown(config: InsertConfig, result: LayoutResult) -> str:
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
        f"- Generated instances: {len(result.cells)}",
        f"- Printable bodies: {len(result.printable_bodies)}",
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
        "## Tolerance profile",
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
            "## Interpretation",
            "",
            "Cell size is the theoretical layout reservation. Printable size is the body after "
            "face-level tolerance offsets. Face classifications are preparatory metadata; "
            "V0 does not guarantee an optimized layout or physically validated tolerances.",
        ]
    )
    return "\n".join(lines)


def _dim(dimensions: Dimension3D) -> dict[str, float]:
    return {"x": _clean_float(dimensions.x), "y": _clean_float(dimensions.y), "z": _clean_float(dimensions.z)}


def _point(point: Point3D) -> dict[str, float]:
    return {"x": _clean_float(point.x), "y": _clean_float(point.y), "z": _clean_float(point.z)}


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


def _format_face_roles(body: Any) -> str:
    roles = {
        classification.face.value: classification.role.value
        for classification in body.face_classifications
    }
    ordered_faces = ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")
    return ", ".join(f"{face}: {roles.get(face, 'unknown')}" for face in ordered_faces)


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
