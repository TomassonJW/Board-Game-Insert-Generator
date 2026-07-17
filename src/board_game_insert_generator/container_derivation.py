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
    arrangement = _arrange_compartments(compartments, wall_mm, box_inner)
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
    xy_fits = (
        outer["x"] <= box_inner["x"] and outer["y"] <= box_inner["y"]
    ) or (
        outer["x"] <= box_inner["y"] and outer["y"] <= box_inner["x"]
    )
    if not xy_fits:
        blockers.append(
            "L empreinte minimale calculee du conteneur ne tient dans aucune "
            "orientation X/Y autorisee de la boite."
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
            "policy": "bounded_shelf_candidates_v2",
            "candidate_count_evaluated": arrangement["candidate_count_evaluated"],
            "box_fit_orientation": arrangement["box_fit_orientation"],
            "order_strategy": arrangement["order_strategy"],
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
    effective_payload = content.get("clearance_effective_v1")
    if isinstance(effective_payload, dict):
        clearance = _dimension(_mapping(effective_payload["values_mm"]))
        clearance_source = dict(_mapping(effective_payload["source_by_axis"]))
    else:
        scalar = float(default_clearance_mm if configured_clearance is None else configured_clearance)
        clearance = {"x": scalar, "y": scalar, "z": scalar}
        clearance_source = {"x": "legacy_scalar", "y": "legacy_scalar", "z": "legacy_scalar"}
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
        content_height = unit["z"] + clearance["z"]
        sizing_policy = "declared_deck_height_v1"
        count_semantics = "count_is_reported__z_is_total_deck_height"
        warnings.append(
            "Card dimensions use the resolved storage orientation; the requested and resolved orientations are reported."
        )
    else:
        available_stack_height_mm = usable_height_mm - floor_mm - clearance["z"]
        if unit["z"] > available_stack_height_mm:
            blockers.append(
                f"'{content['name']}' is {unit['z']} mm tall, leaving no usable vertical clearance in this box."
            )
        capacity_per_stack = max(1, int(available_stack_height_mm // unit["z"]))
        pile_count = max(1, ceil(quantity / capacity_per_stack))
        items_per_pile = max(1, ceil(quantity / pile_count))
        grid_columns, grid_rows = _choose_pile_grid(pile_count, unit["x"], unit["y"], clearance["x"], clearance["y"])
        content_height = items_per_pile * unit["z"] + clearance["z"]
        sizing_policy = "count_aware_pile_grid_v1"
        count_semantics = "quantity_is_counted_as_stackable_items"

    inner = {
        "x": _round(grid_columns * unit["x"] + (grid_columns - 1) * clearance["x"] + clearance["x"] * 2.0),
        "y": _round(grid_rows * unit["y"] + (grid_rows - 1) * clearance["y"] + clearance["y"] * 2.0),
        "z": _round(content_height),
    }
    return {
        "id": f"compartment:{content['id']}",
        "content_id": content["id"],
        "content_name": content["name"],
        "shape_kind": shape_kind,
        "footprint_profile": _footprint_profile(shape_kind, unit),
        "inner_dimensions_mm": inner,
        "content_clearance_mm": _round(clearance["z"]),
        "clearance_effective_v1": {
            "role": "asset_cavity",
            "values_mm": _rounded_dimension(clearance),
            "source_by_axis": clearance_source,
        },
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
        "storage_orientation": content.get("storage_orientation", "flat"),
        "resolved_orientation": content.get("resolved_orientation", "flat"),
        "base_dimensions_mm": content.get("base_dimensions_mm", content["dimensions_mm"]),
        "resolved_dimensions_mm": content["dimensions_mm"],
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


def _choose_pile_grid(
    count: int, unit_x: float, unit_y: float, clearance_x_mm: float, clearance_y_mm: float
) -> tuple[int, int]:
    candidates: list[tuple[float, float, int, int]] = []
    # Only a constant-size neighbourhood around the balanced grid is needed.
    # This keeps a very large declared quantity from turning a single content
    # row into an unbounded search while preserving deterministic sizing.
    target_columns = max(1, int(round((count * max(unit_y, 0.0001) / max(unit_x, 0.0001)) ** 0.5)))
    candidate_columns = {1, count}
    candidate_columns.update(max(1, min(count, target_columns + delta)) for delta in range(-3, 4))
    for columns in sorted(candidate_columns):
        rows = ceil(count / columns)
        width = columns * unit_x + (columns - 1) * clearance_x_mm + clearance_x_mm * 2.0
        height = rows * unit_y + (rows - 1) * clearance_y_mm + clearance_y_mm * 2.0
        aspect_penalty = abs(log(max(width, height) / min(width, height))) if min(width, height) else 0.0
        score = width * height * (1.0 + aspect_penalty * 0.25)
        candidates.append((score, width * height, columns, rows))
    _, _, columns, rows = min(candidates)
    return columns, rows


def _arrange_compartments(
    compartments: list[dict[str, object]],
    wall_mm: float,
    box_inner: dict[str, float],
) -> dict[str, object]:
    """Choose a compact deterministic shelf layout that can fit the box XY."""

    max_inner_x = max(0.0, box_inner["x"] - wall_mm * 2.0)
    max_inner_y = max(0.0, box_inner["y"] - wall_mm * 2.0)
    legacy_candidates: dict[tuple[tuple[str, ...], ...], dict[str, object]] = {}
    for columns in range(1, len(compartments) + 1):
        rows = [
            compartments[index : index + columns]
            for index in range(0, len(compartments), columns)
        ]
        _register_arrangement_candidate(
            legacy_candidates,
            rows,
            wall_mm,
            box_inner,
            "source",
        )
    legacy_selected = min(legacy_candidates.values(), key=_legacy_arrangement_score)

    if legacy_selected["box_fit_orientation"] != "none":
        # Preserve the established canonical geometry whenever it is feasible.
        # The broader search is a corrective fallback, not a silent relayout of
        # every historical project.
        candidates = legacy_candidates
        selected = legacy_selected
    else:
        candidates: dict[tuple[tuple[str, ...], ...], dict[str, object]] = {}
        for order_strategy, ordered in _compartment_orderings(compartments):
            count = len(ordered)
            for columns in range(1, count + 1):
                rows = [
                    ordered[index : index + columns]
                    for index in range(0, count, columns)
                ]
                _register_arrangement_candidate(
                    candidates,
                    rows,
                    wall_mm,
                    box_inner,
                    order_strategy,
                )

            target_widths = _bounded_target_widths(
                ordered,
                wall_mm,
                max_inner_x,
                max_inner_y,
            )
            for target_width in target_widths:
                _register_arrangement_candidate(
                    candidates,
                    _next_fit_rows(ordered, target_width, wall_mm),
                    wall_mm,
                    box_inner,
                    order_strategy,
                )
                _register_arrangement_candidate(
                    candidates,
                    _best_fit_rows(ordered, target_width, wall_mm),
                    wall_mm,
                    box_inner,
                    order_strategy,
                )
        selected = min(candidates.values(), key=_arrangement_score)
    origins: dict[str, dict[str, float]] = {}
    y = 0.0
    for row, row_height in zip(
        _values(selected["row_values"]),
        _values(selected["row_heights"]),
    ):
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
        "candidate_count_evaluated": len(candidates),
        "box_fit_orientation": selected["box_fit_orientation"],
        "order_strategy": selected["order_strategy"],
    }


def _compartment_orderings(
    compartments: list[dict[str, object]],
) -> list[tuple[str, list[dict[str, object]]]]:
    def identifier(item: dict[str, object]) -> str:
        return str(item["id"])

    definitions = (
        ("source", list(compartments)),
        (
            "width_desc",
            sorted(
                compartments,
                key=lambda item: (
                    -_compartment_width(item),
                    -_compartment_height(item),
                    identifier(item),
                ),
            ),
        ),
        (
            "height_desc",
            sorted(
                compartments,
                key=lambda item: (
                    -_compartment_height(item),
                    -_compartment_width(item),
                    identifier(item),
                ),
            ),
        ),
        (
            "area_desc",
            sorted(
                compartments,
                key=lambda item: (
                    -_compartment_width(item) * _compartment_height(item),
                    -max(_compartment_width(item), _compartment_height(item)),
                    identifier(item),
                ),
            ),
        ),
        (
            "max_side_desc",
            sorted(
                compartments,
                key=lambda item: (
                    -max(_compartment_width(item), _compartment_height(item)),
                    -min(_compartment_width(item), _compartment_height(item)),
                    identifier(item),
                ),
            ),
        ),
    )
    result: list[tuple[str, list[dict[str, object]]]] = []
    seen: set[tuple[str, ...]] = set()
    for name, values in definitions:
        signature = tuple(identifier(item) for item in values)
        if signature in seen:
            continue
        seen.add(signature)
        result.append((name, values))
    return result


def _bounded_target_widths(
    ordered: list[dict[str, object]],
    wall_mm: float,
    max_inner_x: float,
    max_inner_y: float,
    *,
    maximum_count: int = 48,
) -> list[float]:
    """Bound the downstream shelf search while retaining representative widths."""

    maximum_item = max(_compartment_width(item) for item in ordered)
    values = {max_inner_x, max_inner_y, maximum_item}
    max_span = max(max_inner_x, max_inner_y)
    for first in range(len(ordered)):
        width = 0.0
        for last in range(first, len(ordered)):
            if last > first:
                width += wall_mm
            width += _compartment_width(ordered[last])
            if width <= max_span + 0.0001:
                values.add(_round(width))
    eligible = sorted(value for value in values if value + 0.0001 >= maximum_item)
    if len(eligible) <= maximum_count:
        return eligible
    mandatory = {maximum_item, max_inner_x, max_inner_y}
    remaining_slots = max(0, maximum_count - len(mandatory))
    sampled = {
        eligible[round(index * (len(eligible) - 1) / max(1, remaining_slots - 1))]
        for index in range(remaining_slots)
    }
    return sorted(mandatory | sampled)


def _next_fit_rows(
    ordered: list[dict[str, object]],
    target_width: float,
    wall_mm: float,
) -> list[list[dict[str, object]]]:
    rows: list[list[dict[str, object]]] = []
    widths: list[float] = []
    for item in ordered:
        width = _compartment_width(item)
        if rows and widths[-1] + wall_mm + width <= target_width + 0.0001:
            rows[-1].append(item)
            widths[-1] += wall_mm + width
        else:
            rows.append([item])
            widths.append(width)
    return rows


def _best_fit_rows(
    ordered: list[dict[str, object]],
    target_width: float,
    wall_mm: float,
) -> list[list[dict[str, object]]]:
    rows: list[list[dict[str, object]]] = []
    widths: list[float] = []
    heights: list[float] = []
    for item in ordered:
        width = _compartment_width(item)
        height = _compartment_height(item)
        fits: list[tuple[float, float, int]] = []
        for index, row_width in enumerate(widths):
            next_width = row_width + wall_mm + width
            if next_width <= target_width + 0.0001:
                fits.append(
                    (
                        max(heights[index], height) - heights[index],
                        target_width - next_width,
                        index,
                    )
                )
        if not fits:
            rows.append([item])
            widths.append(width)
            heights.append(height)
            continue
        _, _, index = min(fits)
        rows[index].append(item)
        widths[index] += wall_mm + width
        heights[index] = max(heights[index], height)
    return rows


def _register_arrangement_candidate(
    candidates: dict[tuple[tuple[str, ...], ...], dict[str, object]],
    rows: list[list[dict[str, object]]],
    wall_mm: float,
    box_inner: dict[str, float],
    order_strategy: str,
) -> None:
    signature = tuple(tuple(str(item["id"]) for item in row) for row in rows)
    if signature in candidates:
        return
    row_widths = [
        sum(_compartment_width(item) for item in row) + wall_mm * (len(row) - 1)
        for row in rows
    ]
    row_heights = [max(_compartment_height(item) for item in row) for row in rows]
    width = max(row_widths)
    height = sum(row_heights) + wall_mm * (len(rows) - 1)
    outer_x = width + wall_mm * 2.0
    outer_y = height + wall_mm * 2.0
    if outer_x <= box_inner["x"] + 0.0001 and outer_y <= box_inner["y"] + 0.0001:
        orientation = "direct"
    elif outer_x <= box_inner["y"] + 0.0001 and outer_y <= box_inner["x"] + 0.0001:
        orientation = "rotated_90"
    else:
        orientation = "none"
    candidates[signature] = {
        "columns": max(len(row) for row in rows),
        "rows": len(rows),
        "row_values": rows,
        "row_heights": row_heights,
        "size_mm": {"x": _round(width), "y": _round(height)},
        "outer_area_mm2": outer_x * outer_y,
        "box_fit_orientation": orientation,
        "order_strategy": order_strategy,
        "signature": signature,
    }


def _legacy_arrangement_score(value: dict[str, object]) -> tuple[object, ...]:
    size = _mapping(value["size_mm"])
    width = float(size["x"])
    height = float(size["y"])
    aspect_penalty = (
        abs(log(max(width, height) / min(width, height)))
        if min(width, height) > 0.0
        else 0.0
    )
    return (
        width * height * (1.0 + aspect_penalty * 0.25),
        int(value["columns"]),
    )


def _arrangement_score(value: dict[str, object]) -> tuple[object, ...]:
    size = _mapping(value["size_mm"])
    width = float(size["x"])
    height = float(size["y"])
    aspect_penalty = (
        abs(log(max(width, height) / min(width, height)))
        if min(width, height) > 0.0
        else 0.0
    )
    return (
        0 if value["box_fit_orientation"] != "none" else 1,
        _round(float(value["outer_area_mm2"])),
        _round(aspect_penalty),
        int(value["rows"]),
        str(value["order_strategy"]),
        value["signature"],
    )


def _compartment_width(item: dict[str, object]) -> float:
    return float(_mapping(item["inner_dimensions_mm"])["x"])


def _compartment_height(item: dict[str, object]) -> float:
    return float(_mapping(item["inner_dimensions_mm"])["y"])


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
