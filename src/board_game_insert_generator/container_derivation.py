"""Pure, explainable V0.1 derivation of storage containers from a user project.

This module sits between the user-facing ``bgig.project.v1`` contract and the
future box-level solver.  It sizes *required* containers and their internal
compartments, but intentionally does not place those containers in the game
box and does not generate CAD geometry.
"""

from __future__ import annotations

from math import ceil, log
from board_game_insert_generator.project_v1 import ProjectNormalization, normalize_project_draft


CONTAINER_DERIVATION_SCHEMA_V1 = "bgig.container_derivation.v1"


def derive_container_plan(
    raw_project: object, *, max_container_height_mm: float | None = None
) -> dict[str, object]:
    """Derive preliminary container sizes without mutating the user project.

    The result is deliberately useful even when a requested container is too
    large: it carries an explicit blocker and the dimensions that caused it.
    P40 will account for flat items and P41 will decide the final box-level
    placement and fill.  Therefore this function never claims that the whole
    box is solved or printable.
    """

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    box = _mapping(project["box"])
    layout = _mapping(project["layout"])
    groups = [_mapping(value) for value in _values(project["container_groups"])]
    contents = [_mapping(value) for value in _values(project["contents"])]
    contents_by_group: dict[str, list[dict[str, object]]] = {str(group["id"]): [] for group in groups}
    for content in contents:
        contents_by_group[str(content["container_group_id"])].append(content)

    box_inner = _dimension(box["inner_dimensions_mm"])
    usable_height_mm = min(float(box["usable_height_mm"]), box_inner["z"])
    if max_container_height_mm is not None:
        usable_height_mm = min(usable_height_mm, float(max_container_height_mm))
    containers = [
        _derive_container(
            group=group,
            contents=contents_by_group[str(group["id"])],
            box_inner=box_inner,
            usable_height_mm=usable_height_mm,
            layout=layout,
        )
        for group in groups
    ]
    ready = [container for container in containers if container["status"] == "ready"]
    blocked = [container for container in containers if container["status"] == "blocked"]
    empty = [container for container in containers if container["status"] == "pending_fill_resolution"]
    blockers = [
        {
            "container_group_id": container["container_group_id"],
            "container_name": container["container_name"],
            "message": message,
        }
        for container in blocked
        for message in _values(container["blockers"])
    ]

    return {
        "schema_version": CONTAINER_DERIVATION_SCHEMA_V1,
        "source": _source_payload(normalization),
        "project_name": project["project_name"],
        "box_limits_mm": {
            "inner_dimensions_mm": box_inner,
            "usable_height_mm": _round(usable_height_mm),
            "container_height_limit_mm": (
                None if max_container_height_mm is None else _round(float(max_container_height_mm))
            ),
        },
        "containers": containers,
        "summary": {
            "status": "blocked" if blocked else "ready_for_p40",
            "requested_container_count": len(containers),
            "ready_container_count": len(ready),
            "blocked_container_count": len(blocked),
            "pending_fill_container_count": len(empty),
            "content_family_count": len(contents),
            "content_item_count": sum(int(content["quantity"]) for content in contents),
            "preliminary_outer_volume_mm3": _round(
                sum(_volume(_mapping(container["outer_dimensions_mm"])) for container in ready)
            ),
            "next_step": (
                "P40 must reserve the upper flat-item stack before final box placement."
                if max_container_height_mm is None
                else "P41 must place the height-constrained containers and close the remaining volume."
            ),
        },
        "blockers": blockers,
        "limitations": [
            "This plan sizes requested containers but does not place them in the game box.",
            "The shared layout clearance between containers is intentionally applied by P41, not inside a container.",
            "Round, square, cube and meeple contents currently use their safe rectangular envelopes; V0.2 may add ergonomic shapes without changing this input contract.",
            "No Fusion geometry, print validation or final volume-fill claim is produced here.",
        ],
    }


def _derive_container(
    *,
    group: dict[str, object],
    contents: list[dict[str, object]],
    box_inner: dict[str, float],
    usable_height_mm: float,
    layout: dict[str, object],
) -> dict[str, object]:
    wall_mm = float(group["wall_thickness_mm"] or layout["default_wall_thickness_mm"])
    floor_mm = float(group["floor_thickness_mm"] or layout["default_floor_thickness_mm"])
    group_id = str(group["id"])
    if not contents:
        return {
            "container_group_id": group_id,
            "container_name": group["name"],
            "status": "pending_fill_resolution",
            "source_content_ids": [],
            "wall_thickness_mm": _round(wall_mm),
            "floor_thickness_mm": _round(floor_mm),
            "compartments": [],
            "inner_dimensions_mm": None,
            "outer_dimensions_mm": None,
            "blockers": [],
            "warnings": ["This requested container has no content yet; P41 may size it from a fill element."],
        }

    compartments = [
        _derive_compartment(
            content=content,
            usable_height_mm=usable_height_mm,
            floor_mm=floor_mm,
            default_clearance_mm=float(layout["default_content_clearance_mm"]),
        )
        for content in contents
    ]
    arrangement = _arrange_compartments(compartments, wall_mm)
    for compartment in compartments:
        origin = arrangement["origins"][str(compartment["id"])]
        compartment["local_origin_mm"] = {
            "x": _round(wall_mm + origin["x"]),
            "y": _round(wall_mm + origin["y"]),
            "z": _round(floor_mm),
        }

    inner = {
        "x": _round(arrangement["size_mm"]["x"]),
        "y": _round(arrangement["size_mm"]["y"]),
        "z": _round(max(float(_mapping(compartment["inner_dimensions_mm"])["z"]) for compartment in compartments)),
    }
    outer = {
        "x": _round(inner["x"] + wall_mm * 2.0),
        "y": _round(inner["y"] + wall_mm * 2.0),
        "z": _round(inner["z"] + floor_mm),
    }
    blockers = [
        str(blocker)
        for compartment in compartments
        for blocker in _values(compartment["blockers"])
    ]
    if outer["x"] > box_inner["x"]:
        blockers.append(
            f"The container needs {outer['x']} mm in width but the box allows {box_inner['x']} mm."
        )
    if outer["y"] > box_inner["y"]:
        blockers.append(
            f"The container needs {outer['y']} mm in depth but the box allows {box_inner['y']} mm."
        )
    if outer["z"] > usable_height_mm:
        blockers.append(
            f"The container needs {outer['z']} mm in height but the usable box height is {usable_height_mm} mm."
        )
    warnings = [
        str(warning)
        for compartment in compartments
        for warning in _values(compartment["warnings"])
    ]
    return {
        "container_group_id": group_id,
        "container_name": group["name"],
        "status": "blocked" if blockers else "ready",
        "source_content_ids": [compartment["content_id"] for compartment in compartments],
        "wall_thickness_mm": _round(wall_mm),
        "floor_thickness_mm": _round(floor_mm),
        "inner_dimensions_mm": inner,
        "outer_dimensions_mm": outer,
        "compartment_layout": {
            "policy": "deterministic_rows_with_internal_walls_v1",
            "columns": arrangement["columns"],
            "rows": arrangement["rows"],
            "internal_wall_thickness_mm": _round(wall_mm),
        },
        "compartments": compartments,
        "blockers": blockers,
        "warnings": warnings,
    }


def _derive_compartment(
    *,
    content: dict[str, object],
    usable_height_mm: float,
    floor_mm: float,
    default_clearance_mm: float,
) -> dict[str, object]:
    dimensions = _dimension(content["dimensions_mm"])
    shape_kind = str(content["shape_kind"])
    quantity = int(content["quantity"])
    configured_clearance = content["content_clearance_mm"]
    clearance_mm = float(default_clearance_mm if configured_clearance is None else configured_clearance)
    unit = _shape_envelope(shape_kind, dimensions)
    blockers: list[str] = []
    warnings: list[str] = []
    if str(content["measurement_confidence"]) != "exact":
        warnings.append("The entered measurements are approximate; verify them before printing.")

    if shape_kind == "cards":
        pile_count = 1
        grid_columns = 1
        grid_rows = 1
        capacity_per_stack = quantity
        items_per_pile = quantity
        content_height = unit["z"] + clearance_mm
        sizing_policy = "declared_deck_height_v1"
        count_semantics = "count_is_reported__z_is_total_deck_height"
        warnings.append("For cards, the entered thickness is treated as the full deck height, not one card thickness.")
    else:
        available_stack_height_mm = usable_height_mm - floor_mm - clearance_mm
        if unit["z"] > available_stack_height_mm:
            blockers.append(
                f"'{content['name']}' is {unit['z']} mm tall, leaving no usable vertical clearance in this box."
            )
        capacity_per_stack = max(1, int(available_stack_height_mm // unit["z"]))
        pile_count = max(1, ceil(quantity / capacity_per_stack))
        items_per_pile = max(1, ceil(quantity / pile_count))
        grid_columns, grid_rows = _choose_pile_grid(pile_count, unit["x"], unit["y"], clearance_mm)
        content_height = items_per_pile * unit["z"] + clearance_mm
        sizing_policy = "count_aware_pile_grid_v1"
        count_semantics = "quantity_is_counted_as_stackable_items"

    inner = {
        "x": _round(grid_columns * unit["x"] + (grid_columns - 1) * clearance_mm + clearance_mm * 2.0),
        "y": _round(grid_rows * unit["y"] + (grid_rows - 1) * clearance_mm + clearance_mm * 2.0),
        "z": _round(content_height),
    }
    return {
        "id": f"compartment:{content['id']}",
        "content_id": content["id"],
        "content_name": content["name"],
        "shape_kind": shape_kind,
        "footprint_profile": _footprint_profile(shape_kind, unit),
        "inner_dimensions_mm": inner,
        "content_clearance_mm": _round(clearance_mm),
        "quantity": {
            "declared_count": quantity,
            "capacity_per_stack": capacity_per_stack,
            "pile_count": pile_count,
            "items_per_pile": items_per_pile,
            "pile_grid_columns": grid_columns,
            "pile_grid_rows": grid_rows,
            "count_semantics": count_semantics,
        },
        "sizing_policy": sizing_policy,
        "local_origin_mm": None,
        "blockers": blockers,
        "warnings": warnings,
    }


def _shape_envelope(shape_kind: str, dimensions: dict[str, float]) -> dict[str, float]:
    if shape_kind in {"round", "square"}:
        side = max(dimensions["x"], dimensions["y"])
        return {"x": side, "y": side, "z": dimensions["z"]}
    if shape_kind == "cube":
        side = max(dimensions["x"], dimensions["y"], dimensions["z"])
        return {"x": side, "y": side, "z": side}
    return dimensions


def _footprint_profile(shape_kind: str, unit: dict[str, float]) -> dict[str, object]:
    profile = {
        "round": "round_bounding_box_v1",
        "square": "square_bounding_box_v1",
        "rectangle": "rectangular_bounding_box_v1",
        "cards": "card_deck_bounding_box_v1",
        "cube": "cube_bounding_box_v1",
        "meeple": "meeple_bounding_box_v1",
        "custom": "custom_bounding_box_v1",
    }[shape_kind]
    result: dict[str, object] = {"policy": profile, "unit_envelope_mm": _rounded_dimension(unit)}
    if shape_kind == "round":
        result["diameter_mm"] = _round(unit["x"])
    return result


def _choose_pile_grid(count: int, unit_x: float, unit_y: float, clearance_mm: float) -> tuple[int, int]:
    candidates: list[tuple[float, float, int, int]] = []
    # Only a constant-size neighbourhood around the balanced grid is needed.
    # This keeps a very large declared quantity from turning a single content
    # row into an unbounded search while preserving deterministic sizing.
    target_columns = max(1, int(round((count * max(unit_y, 0.0001) / max(unit_x, 0.0001)) ** 0.5)))
    candidate_columns = {1, count}
    candidate_columns.update(max(1, min(count, target_columns + delta)) for delta in range(-3, 4))
    for columns in sorted(candidate_columns):
        rows = ceil(count / columns)
        width = columns * unit_x + (columns - 1) * clearance_mm + clearance_mm * 2.0
        height = rows * unit_y + (rows - 1) * clearance_mm + clearance_mm * 2.0
        aspect_penalty = abs(log(max(width, height) / min(width, height))) if min(width, height) else 0.0
        score = width * height * (1.0 + aspect_penalty * 0.25)
        candidates.append((score, width * height, columns, rows))
    _, _, columns, rows = min(candidates)
    return columns, rows


def _arrange_compartments(compartments: list[dict[str, object]], wall_mm: float) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for columns in range(1, len(compartments) + 1):
        rows = [compartments[index : index + columns] for index in range(0, len(compartments), columns)]
        row_widths = [
            sum(float(_mapping(item["inner_dimensions_mm"])["x"]) for item in row) + wall_mm * (len(row) - 1)
            for row in rows
        ]
        row_heights = [max(float(_mapping(item["inner_dimensions_mm"])["y"]) for item in row) for row in rows]
        width = max(row_widths)
        height = sum(row_heights) + wall_mm * (len(rows) - 1)
        aspect_penalty = abs(log(max(width, height) / min(width, height))) if min(width, height) else 0.0
        candidates.append(
            {
                "columns": columns,
                "rows": len(rows),
                "row_values": rows,
                "row_heights": row_heights,
                "size_mm": {"x": _round(width), "y": _round(height)},
                "score": width * height * (1.0 + aspect_penalty * 0.25),
            }
        )
    selected = min(candidates, key=lambda item: (float(item["score"]), int(item["columns"])))
    origins: dict[str, dict[str, float]] = {}
    y = 0.0
    for row, row_height in zip(_values(selected["row_values"]), _values(selected["row_heights"])):
        x = 0.0
        for item in _values(row):
            compartment = _mapping(item)
            dimensions = _mapping(compartment["inner_dimensions_mm"])
            origins[str(compartment["id"])] = {"x": _round(x), "y": _round(y)}
            x += float(dimensions["x"]) + wall_mm
        y += float(row_height) + wall_mm
    return {
        "columns": selected["columns"],
        "rows": selected["rows"],
        "size_mm": selected["size_mm"],
        "origins": origins,
    }


def _source_payload(normalization: ProjectNormalization) -> dict[str, object]:
    return {
        "source_schema": normalization.source_schema,
        "migrated": normalization.migrated,
        "project_schema": str(normalization.project["schema_version"]),
    }


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):  # normalized project values are always mappings
        raise TypeError("Internal normalized project value must be a mapping.")
    return value


def _values(value: object) -> list[object]:
    if not isinstance(value, list):  # normalized project values are always lists
        raise TypeError("Internal normalized project value must be a list.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _rounded_dimension(value: dict[str, float]) -> dict[str, float]:
    return {axis: _round(value[axis]) for axis in ("x", "y", "z")}


def _volume(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"]) * float(value["z"])


def _round(value: float) -> float:
    return round(float(value), 4)
