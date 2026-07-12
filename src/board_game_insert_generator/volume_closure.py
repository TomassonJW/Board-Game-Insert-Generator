"""Deterministic V0.1 placement and classification of the complete box volume."""

from __future__ import annotations

from itertools import product

from board_game_insert_generator.flat_stack_reservation import derive_flat_stack_reservation
from board_game_insert_generator.project_v1 import normalize_project_draft


VOLUME_CLOSURE_SCHEMA_V1 = "bgig.volume_closure.v1"


def solve_project_volume(raw_project: object) -> dict[str, object]:
    """Place derived containers and classify every remaining rectangular region.

    This is a bounded deterministic product solver, not a CAD generator.  It
    lays containers on the box base, reserves the upper flat stack, and emits
    explicit hollow-fill candidates for usable remaining regions.  P42 alone
    materializes the selected bodies.
    """

    normalized = normalize_project_draft(raw_project)
    project = normalized.project
    stack_plan = derive_flat_stack_reservation(raw_project)
    box = _mapping(project["box"])
    layout = _mapping(project["layout"])
    box_size = _dimension(box["inner_dimensions_mm"])
    usable_height = min(float(box["usable_height_mm"]), box_size["z"])
    clearance = float(layout["layout_clearance_mm"])
    preexisting_blockers = [str(value) for value in _values(stack_plan["blockers"])]

    reservations: list[dict[str, object]] = []
    flat_stack = _mapping(stack_plan["flat_stack"])
    if flat_stack["reservation_size_mm"] is not None:
        reservations.append(
            {
                "id": "reservation:upper-flat-stack",
                "kind": "upper_flat_stack",
                "origin_mm": _mapping(flat_stack["preferred_reservation_origin_mm"]),
                "size_mm": _mapping(flat_stack["reservation_size_mm"]),
                "printable": False,
            }
        )

    placements, placement_blockers = _place_containers(
        _values(_mapping(stack_plan["container_plan"])["containers"]), box_size, clearance
    )
    fill_placements, fill_blockers = _place_exact_fills(
        _values(project["fill_elements"]),
        placements,
        box_size,
        float(_mapping(stack_plan["flat_stack"])["storage_height_mm"]),
        clearance,
    )
    blockers = [*preexisting_blockers, *placement_blockers, *fill_blockers]
    occupied = [
        {"id": item["id"], "kind": "container", "origin_mm": item["origin_mm"], "size_mm": item["size_mm"], "printable": True}
        for item in placements
    ] + fill_placements + reservations
    free_regions = _free_regions(box_size, usable_height, occupied)
    fill_preferences = _fill_preferences(_values(project["fill_elements"]))
    classified_regions = _classify_regions(free_regions, clearance, reservations, fill_preferences)
    validation = _validate_solution(box_size, usable_height, occupied, classified_regions)
    if not validation["no_collisions"]:
        blockers.append("The placement solver produced colliding volumes; no constructible plan is returned.")
    if not validation["volume_conserved"]:
        blockers.append("The volume accounting is inconsistent; no constructible plan is returned.")
    support = _support_status(reservations, [*placements, *fill_placements], classified_regions)
    if support["status"] == "unresolved":
        blockers.append("The upper flat stack has no continuous planned support.")
    return {
        "schema_version": VOLUME_CLOSURE_SCHEMA_V1,
        "source": {"source_schema": normalized.source_schema, "migrated": normalized.migrated},
        "project_name": project["project_name"],
        "box": {"inner_dimensions_mm": _rounded(box_size), "usable_height_mm": _round(usable_height)},
        "container_plan": _mapping(stack_plan["container_plan"]),
        "reservations": reservations,
        "placements": placements,
        "fill_placements": fill_placements,
        "free_regions": classified_regions,
        "support": support,
        "validation": validation,
        "summary": {
            "status": "impossible" if blockers else "constructed_plan",
            "placed_container_count": len(placements),
            "reservation_count": len(reservations),
            "explicit_fill_placement_count": len(fill_placements),
            "classified_free_region_count": len(classified_regions),
            "hollow_fill_candidate_count": sum(1 for region in classified_regions if region["classification"] == "hollow_fill_candidate"),
            "solid_fill_candidate_count": sum(1 for region in classified_regions if region["classification"] == "solid_fill_requested"),
            "next_step": "P42 must materialize the selected containers and fill candidates as CAD geometry.",
        },
        "blockers": blockers,
        "limitations": [
            "Placement is deterministic and bounded; it does not claim global mathematical optimality.",
            "Hollow-fill candidates classify useful remaining volume but are not CAD bodies yet.",
            "No Fusion or print validation is claimed by this plan.",
        ],
    }


def _place_containers(containers: list[object], box_size: dict[str, float], clearance: float) -> tuple[list[dict[str, object]], list[str]]:
    candidates = [_mapping(value) for value in containers if _mapping(value)["status"] == "ready"]
    blockers = [
        f"{_mapping(value)['container_name']}: container derivation is blocked before global placement."
        for value in containers
        if _mapping(value)["status"] == "blocked"
    ]
    placed: list[dict[str, object]] = []
    for container in sorted(candidates, key=lambda item: (-_area(_mapping(item["outer_dimensions_mm"])), str(item["container_group_id"]))):
        size = _dimension(container["outer_dimensions_mm"])
        placement = _find_xy_placement(size, placed, box_size, clearance)
        if placement is None:
            blockers.append(f"{container['container_name']}: no collision-free X/Y placement fits in the box with the requested clearance.")
            continue
        origin, rotated, placed_size = placement
        placed.append(
            {
                "id": f"container:{container['container_group_id']}",
                "container_group_id": container["container_group_id"],
                "name": container["container_name"],
                "origin_mm": origin,
                "size_mm": _rounded(placed_size),
                "rotated_xy": rotated,
                "source_content_ids": container["source_content_ids"],
                "printable": True,
            }
        )
    return placed, blockers


def _place_exact_fills(values: list[object], placed: list[dict[str, object]], box_size: dict[str, float], storage_height: float, clearance: float) -> tuple[list[dict[str, object]], list[str]]:
    result: list[dict[str, object]] = []
    blockers: list[str] = []
    occupied = list(placed)
    for value in values:
        fill = _mapping(value)
        if fill["mode"] != "exact":
            continue
        size = _dimension(fill["dimensions_mm"])
        if size["z"] > storage_height:
            blockers.append(f"{fill['name']}: requested fill height exceeds the storage height left below the upper stack.")
            continue
        placement = _find_xy_placement(size, occupied, box_size, clearance)
        if placement is None:
            blockers.append(f"{fill['name']}: requested exact fill cannot be placed without collision.")
            continue
        origin, rotated, placed_size = placement
        item = {"id": f"fill:{fill['id']}", "kind": f"fill:{fill['kind']}", "origin_mm": origin, "size_mm": _rounded(placed_size), "printable": True, "requested_fill_id": fill["id"], "associated_container_group_id": fill["container_group_id"]}
        result.append(item)
        occupied.append(item)
    return result, blockers

def _find_xy_placement(size: dict[str, float], placed: list[dict[str, object]], box_size: dict[str, float], clearance: float) -> tuple[dict[str, float], bool, dict[str, float]] | None:
    x_values = {clearance}
    y_values = {clearance}
    for item in placed:
        origin = _mapping(item["origin_mm"])
        dimensions = _mapping(item["size_mm"])
        x_values.add(float(origin["x"]) + float(dimensions["x"]) + clearance)
        y_values.add(float(origin["y"]) + float(dimensions["y"]) + clearance)
    orientations = [(size, False)]
    if size["x"] != size["y"]:
        orientations.append(({"x": size["y"], "y": size["x"], "z": size["z"]}, True))
    for dimensions, rotated in orientations:
        for y, x in product(sorted(y_values), sorted(x_values)):
            if x + dimensions["x"] + clearance > box_size["x"] or y + dimensions["y"] + clearance > box_size["y"]:
                continue
            if dimensions["z"] > box_size["z"]:
                continue
            candidate = {"x": _round(x), "y": _round(y), "z": 0.0}
            if all(_separated_xy(candidate, dimensions, _mapping(item["origin_mm"]), _mapping(item["size_mm"]), clearance) for item in placed):
                return candidate, rotated, dimensions
    return None


def _separated_xy(left_origin: dict[str, float], left_size: dict[str, float], right_origin: dict[str, object], right_size: dict[str, object], clearance: float) -> bool:
    epsilon = 0.000001
    return (
        left_origin["x"] + left_size["x"] + clearance <= float(right_origin["x"]) + epsilon
        or float(right_origin["x"]) + float(right_size["x"]) + clearance <= left_origin["x"] + epsilon
        or left_origin["y"] + left_size["y"] + clearance <= float(right_origin["y"]) + epsilon
        or float(right_origin["y"]) + float(right_size["y"]) + clearance <= left_origin["y"] + epsilon
    )


def _free_regions(box_size: dict[str, float], usable_height: float, occupied: list[dict[str, object]]) -> list[dict[str, object]]:
    xs = {0.0, box_size["x"]}
    ys = {0.0, box_size["y"]}
    zs = {0.0, usable_height}
    for item in occupied:
        origin, size = _mapping(item["origin_mm"]), _mapping(item["size_mm"])
        xs.update({float(origin["x"]), float(origin["x"]) + float(size["x"])})
        ys.update({float(origin["y"]), float(origin["y"]) + float(size["y"])})
        zs.update({float(origin["z"]), float(origin["z"]) + float(size["z"])})
    regions: list[dict[str, object]] = []
    for x0, x1 in _intervals(xs):
        for y0, y1 in _intervals(ys):
            for z0, z1 in _intervals(zs):
                origin = {"x": x0, "y": y0, "z": z0}
                size = {"x": x1 - x0, "y": y1 - y0, "z": z1 - z0}
                if not any(_intersects(origin, size, _mapping(item["origin_mm"]), _mapping(item["size_mm"])) for item in occupied):
                    regions.append({"origin_mm": _rounded(origin), "size_mm": _rounded(size)})
    return regions


def _classify_regions(regions: list[dict[str, object]], clearance: float, reservations: list[dict[str, object]], preferences: list[dict[str, object]]) -> list[dict[str, object]]:
    classified: list[dict[str, object]] = []
    for index, region in enumerate(regions, start=1):
        origin, size = _mapping(region["origin_mm"]), _mapping(region["size_mm"])
        thin = min(float(size["x"]), float(size["y"]), float(size["z"])) <= max(clearance, 0.001)
        under_flat = any(_touches_underside(origin, size, _mapping(item["origin_mm"]), _mapping(item["size_mm"])) for item in reservations)
        preference = preferences[0] if preferences and index == 1 else None
        if thin:
            classification = "technical_clearance"
        elif preference is not None and preference["kind"] == "solid":
            classification = "solid_fill_requested"
        elif under_flat:
            classification = "support_hollow_fill_candidate"
        else:
            classification = "hollow_fill_candidate"
        classified.append({
            "id": f"free:{index}", "origin_mm": origin, "size_mm": size,
            "classification": classification, "printable": classification not in {"technical_clearance"},
            "requested_fill_id": None if preference is None else preference["id"],
        })
    return classified


def _support_status(reservations: list[dict[str, object]], placements: list[dict[str, object]], regions: list[dict[str, object]]) -> dict[str, object]:
    flat = next((item for item in reservations if item["kind"] == "upper_flat_stack"), None)
    if flat is None:
        return {"status": "not_required", "note": "No upper flat stack requires support."}
    reservation_origin = _mapping(flat["origin_mm"])
    support_regions = [item for item in regions if item["classification"] == "support_hollow_fill_candidate" and _touches_underside(_mapping(item["origin_mm"]), _mapping(item["size_mm"]), reservation_origin, _mapping(flat["size_mm"]))]
    has_direct_top = any(abs(float(_mapping(item["origin_mm"])["z"]) + float(_mapping(item["size_mm"])["z"]) - float(reservation_origin["z"])) < 1e-6 for item in placements)
    if has_direct_top or support_regions:
        return {"status": "planned_continuous_with_hollow_fillers", "note": "P41 classifies support below the upper stack; P42 must materialize the selected hollow fillers."}
    return {"status": "unresolved", "note": "No container top or planned hollow filler reaches the upper stack."}


def _validate_solution(box_size: dict[str, float], usable_height: float, occupied: list[dict[str, object]], regions: list[dict[str, object]]) -> dict[str, object]:
    total = box_size["x"] * box_size["y"] * usable_height
    occupied_volume = sum(_volume(_mapping(item["size_mm"])) for item in occupied)
    free_volume = sum(_volume(_mapping(item["size_mm"])) for item in regions)
    return {
        "no_collisions": not any(_intersects(_mapping(left["origin_mm"]), _mapping(left["size_mm"]), _mapping(right["origin_mm"]), _mapping(right["size_mm"])) for index, left in enumerate(occupied) for right in occupied[index + 1 :]),
        "volume_conserved": abs(total - occupied_volume - free_volume) < 0.0001,
        "box_volume_mm3": _round(total), "occupied_volume_mm3": _round(occupied_volume), "classified_free_volume_mm3": _round(free_volume),
    }


def _fill_preferences(values: list[object]) -> list[dict[str, object]]:
    return [_mapping(value) for value in values]

def _touches_underside(
    origin: dict[str, object], size: dict[str, object], reservation_origin: dict[str, object], reservation_size: dict[str, object]
) -> bool:
    reaches_stack = abs(float(origin["z"]) + float(size["z"]) - float(reservation_origin["z"])) < 1e-6
    overlaps_xy = (
        float(origin["x"]) < float(reservation_origin["x"]) + float(reservation_size["x"])
        and float(reservation_origin["x"]) < float(origin["x"]) + float(size["x"])
        and float(origin["y"]) < float(reservation_origin["y"]) + float(reservation_size["y"])
        and float(reservation_origin["y"]) < float(origin["y"]) + float(size["y"])
    )
    return reaches_stack and overlaps_xy

def _intervals(values: set[float]) -> list[tuple[float, float]]:
    ordered = sorted(values)
    return [(left, right) for left, right in zip(ordered, ordered[1:]) if right > left]

def _intersects(a_origin: dict[str, object], a_size: dict[str, object], b_origin: dict[str, object], b_size: dict[str, object]) -> bool:
    return all(float(a_origin[axis]) < float(b_origin[axis]) + float(b_size[axis]) and float(b_origin[axis]) < float(a_origin[axis]) + float(a_size[axis]) for axis in ("x", "y", "z"))

def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict): raise TypeError("Internal plan value must be a mapping.")
    return value

def _values(value: object) -> list[object]:
    if not isinstance(value, list): raise TypeError("Internal plan value must be a list.")
    return value

def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value); return {axis: float(raw[axis]) for axis in ("x", "y", "z")}

def _rounded(value: dict[str, object] | dict[str, float]) -> dict[str, float]:
    return {axis: _round(float(value[axis])) for axis in ("x", "y", "z")}

def _area(size: dict[str, object]) -> float: return float(size["x"]) * float(size["y"])
def _volume(size: dict[str, object]) -> float: return float(size["x"]) * float(size["y"]) * float(size["z"])
def _round(value: float) -> float: return round(float(value), 4)
