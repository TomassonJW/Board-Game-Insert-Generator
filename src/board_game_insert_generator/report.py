from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from board_game_insert_generator.models import Dimension3D, InsertConfig, LayoutResult, Point3D


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
        "tolerances": asdict(config.tolerances),
        "summary": {
            "cell_count": len(result.cells),
            "printable_body_count": len(result.printable_bodies),
            "warnings": list(result.warnings),
        },
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
        "## Warnings",
        "",
    ]
    for warning in result.warnings:
        lines.append(f"- {warning}")

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
            "## Interpretation",
            "",
            "Cell size is the theoretical layout reservation. Printable size is the body after "
            "face-level tolerance offsets. V0 does not guarantee an optimized layout.",
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
