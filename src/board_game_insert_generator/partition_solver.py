"""P57 deterministic partition solver for the Fusion-only MVP.

The solver partitions the printable storage volume between requested container
bodies and explicitly sized complements.  It never turns a free region into an
automatic body.  Cavities remain local to their P55 minimum envelope.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from itertools import product
from math import isclose
from typing import Any

from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
from board_game_insert_generator.flat_stack_reservation import derive_flat_stack_reservation
from board_game_insert_generator.project_v1 import normalize_project_draft


PARTITION_PLAN_SCHEMA_V1 = "bgig.partition_plan.v1"
_EPSILON = 0.0001


def solve_partition_plan(raw_project: object) -> dict[str, object]:
    """Return a bounded, explainable P57 partition without automatic fillers."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    stack = derive_flat_stack_reservation(project)
    flat = _mapping(stack["flat_stack"])
    box = _dimension(_mapping(project["box"])["inner_dimensions_mm"])
    storage_height = float(flat["storage_height_mm"])
    clearance = float(_mapping(project["layout"])["layout_clearance_mm"])
    diagnostics = [
        _diagnostic("FLAT_STACK_BLOCKED", message, "Corrige les dimensions ou la quantite des plateaux et livrets.")
        for message in _values(stack["blockers"])
    ]

    envelope_report = derive_expandable_envelope_contract(
        project,
        max_container_height_mm=max(storage_height, 0.001),
    )
    diagnostics.extend(
        _diagnostic("CONTAINER_MINIMUM_BLOCKED", str(item["message"]), "Corrige la piece, le bac ou la hauteur disponible.", str(item["container_group_id"]))
        for item in _mappings(envelope_report["blockers"])
    )
    containers = [item for item in _mappings(envelope_report["containers"]) if item["status"] == "ready"]
    requested_group_count = len(_values(project["container_groups"]))
    if not requested_group_count:
        diagnostics.append(_diagnostic("NO_CONTAINER_GROUP", "Aucun bac n est demande.", "Ajoute au moins un bac cible et une famille de pieces."))
    if len(containers) != requested_group_count:
        diagnostics.append(
            _diagnostic(
                "CONTAINER_SET_INCOMPLETE",
                "Tous les bacs demandes ne possedent pas une enveloppe minimale constructible.",
                "Corrige les bacs bloques avant de recalculer la partition.",
            )
        )

    participants = [_container_participant(item) for item in containers]
    explicit_complements = _values(project["fill_elements"])
    for value in explicit_complements:
        complement = _mapping(value)
        if complement["mode"] != "exact":
            diagnostics.append(
                _diagnostic(
                    "EXPLICIT_COMPLEMENT_NEEDS_EXACT_SIZE",
                    f"Le complement '{complement['name']}' utilise encore le mode auto.",
                    "Renseigne des dimensions exactes ; BGIG ne cree aucun volume automatique.",
                    str(complement["id"]),
                )
            )
            continue
        dimensions = _dimension(complement["dimensions_mm"])
        if not isclose(dimensions["z"], storage_height, abs_tol=_EPSILON):
            diagnostics.append(
                _diagnostic(
                    "EXPLICIT_COMPLEMENT_HEIGHT_BREAKS_PARTITION",
                    f"Le complement '{complement['name']}' mesure {dimensions['z']} mm en Z, mais la hauteur de rangement est {storage_height} mm.",
                    "Aligne sa hauteur Z sur la hauteur de rangement affichee, ou retire ce complement.",
                    str(complement["id"]),
                )
            )
            continue
        participants.append(_complement_participant(complement))

    if diagnostics or not participants or storage_height <= 0.0:
        return _result(
            normalization,
            project,
            stack,
            envelope_report,
            diagnostics,
            status="incomplete" if not requested_group_count else "impossible",
            evaluated=0,
        )

    candidates: list[dict[str, object]] = []
    evaluated = 0
    for order_name, ordered in _orders(participants):
        for columns in range(1, len(ordered) + 1):
            rows = [ordered[index : index + columns] for index in range(0, len(ordered), columns)]
            for orientation_strategy in ("width", "height", "balanced"):
                evaluated += 1
                candidate = _build_candidate(
                    rows,
                    box,
                    storage_height,
                    clearance,
                    order_name=order_name,
                    orientation_strategy=orientation_strategy,
                )
                if candidate is not None:
                    candidates.append(candidate)

    if not candidates:
        diagnostics.append(
            _diagnostic(
                "NO_COMPLETE_PARTITION",
                "Aucune partition complete ne respecte les minima, jeux, axes extensibles et dimensions verrouillees.",
                "Agrandis la boite, reduis un contenu ou libere un axe/dimension de bac.",
            )
        )
        return _result(
            normalization,
            project,
            stack,
            envelope_report,
            diagnostics,
            status="impossible",
            evaluated=evaluated,
        )

    chosen = max(candidates, key=lambda value: (float(value["simplicity_score"]), str(value["candidate_id"])))
    proposals = {
        str(item["container_group_id"]): _mapping(item["final_outer_dimensions_mm"])
        for item in _mappings(chosen["placements"])
        if item["role"] == "container"
    }
    validated_envelopes = derive_expandable_envelope_contract(
        project,
        final_outer_dimensions_by_group=proposals,
        max_container_height_mm=storage_height,
    )
    if validated_envelopes["summary"]["status"] == "blocked":
        diagnostics.extend(
            _diagnostic("FINAL_ENVELOPE_REJECTED", str(item["message"]), "Relache la contrainte de bac indiquee.", str(item["container_group_id"]))
            for item in _mappings(validated_envelopes["blockers"])
        )
        return _result(
            normalization,
            project,
            stack,
            validated_envelopes,
            diagnostics,
            status="impossible",
            evaluated=evaluated,
        )

    envelope_by_group = {str(item["container_group_id"]): item for item in _mappings(validated_envelopes["containers"])}
    placements: list[dict[str, object]] = []
    for placement in _mappings(chosen["placements"]):
        final = deepcopy(placement)
        if final["role"] == "container":
            contract = envelope_by_group[str(final["container_group_id"])]
            final["cavity_layout"] = deepcopy(contract["cavity_layout"])
            final["minimum_outer_envelope_mm"] = deepcopy(contract["minimum_outer_envelope_mm"])
            final["surplus_distribution_mm"] = deepcopy(contract["surplus_distribution_mm"])
            final["minimum_envelope_origin_in_final_mm"] = deepcopy(contract["minimum_envelope_origin_in_final_mm"])
            final["source_content_ids"] = [str(cavity["content_id"]) for cavity in _mappings(contract["cavity_layout"])]
        placements.append(final)

    validation = _validate_placements(placements, box, storage_height, clearance)
    if not validation["inside_box"] or not validation["no_collisions"] or not validation["clearances_respected"]:
        diagnostics.append(_diagnostic("INTERNAL_PARTITION_INVALID", "La partition choisie viole une borne geometrique interne.", "Conserve le projet et signale ce cas pour correction."))
        return _result(
            normalization,
            project,
            stack,
            validated_envelopes,
            diagnostics,
            status="impossible",
            evaluated=evaluated,
        )

    support = _support_plan(flat, placements)
    summary = {
        "status": "constructed",
        "requested_container_count": requested_group_count,
        "placed_container_count": sum(1 for item in placements if item["role"] == "container"),
        "explicit_complement_count": sum(1 for item in placements if item["role"] == "explicit_complement"),
        "final_body_count": len(placements),
        "automatic_body_count": 0,
        "row_count": chosen["row_count"],
        "rotation_count": chosen["rotation_count"],
        "simplicity_score": chosen["simplicity_score"],
        "complete_printable_partition": True,
        "technical_voids_are_clearances_only": True,
        "candidate_count_evaluated": evaluated,
        "candidate_count_feasible": len(candidates),
    }
    plan = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "box": {"inner_dimensions_mm": _rounded(box), "storage_height_mm": _round(storage_height)},
        "clearance_policy": {
            "box_perimeter_mm": _round(clearance),
            "between_bodies_mm": _round(clearance),
            "materialize_clearances": False,
        },
        "flat_stack": deepcopy(flat),
        "support": support,
        "placements": placements,
        "diagnostics": diagnostics,
        "validation": validation,
        "summary": summary,
        "solver": {
            "kind": "bounded_shelf_partition",
            "candidate_id": chosen["candidate_id"],
            "order": chosen["order_name"],
            "orientation_strategy": chosen["orientation_strategy"],
            "deterministic": True,
            "globally_optimal": False,
        },
        "invariants": {
            "fixed_cavity_layouts": True,
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    plan["plan_digest"] = _digest(plan)
    return plan


def _result(
    normalization: Any,
    project: dict[str, object],
    stack: dict[str, object],
    envelopes: dict[str, object],
    diagnostics: list[dict[str, object]],
    *,
    status: str,
    evaluated: int,
) -> dict[str, object]:
    result = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "box": {
            "inner_dimensions_mm": deepcopy(_mapping(project["box"])["inner_dimensions_mm"]),
            "storage_height_mm": _mapping(stack["flat_stack"])["storage_height_mm"],
        },
        "clearance_policy": {
            "box_perimeter_mm": _mapping(project["layout"])["layout_clearance_mm"],
            "between_bodies_mm": _mapping(project["layout"])["layout_clearance_mm"],
            "materialize_clearances": False,
        },
        "flat_stack": deepcopy(stack["flat_stack"]),
        "support": {"status": "unresolved", "top_support_count": 0, "coverage_ratio": 0.0},
        "placements": [],
        "diagnostics": diagnostics,
        "validation": {"inside_box": False, "no_collisions": False, "clearances_respected": False},
        "summary": {
            "status": status,
            "requested_container_count": len(_values(project["container_groups"])),
            "placed_container_count": 0,
            "explicit_complement_count": 0,
            "final_body_count": 0,
            "automatic_body_count": 0,
            "complete_printable_partition": False,
            "technical_voids_are_clearances_only": False,
            "candidate_count_evaluated": evaluated,
            "candidate_count_feasible": 0,
        },
        "solver": {"kind": "bounded_shelf_partition", "deterministic": True, "globally_optimal": False},
        "envelope_contract": deepcopy(envelopes),
        "invariants": {
            "fixed_cavity_layouts": True,
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    result["plan_digest"] = _digest(result)
    return result


def _container_participant(contract: dict[str, object]) -> dict[str, object]:
    minimum = _dimension(contract["minimum_outer_envelope_mm"])
    constraints = _mapping(contract["constraints"])
    locked = _mapping(constraints["locked_outer_dimensions_mm"])
    axes = _mapping(constraints["expansion_axes"])
    base = {
        axis: float(locked[axis]) if locked[axis] is not None else minimum[axis]
        for axis in ("x", "y", "z")
    }
    return {
        "id": f"container:{contract['container_group_id']}",
        "role": "container",
        "container_group_id": contract["container_group_id"],
        "name": contract["container_name"],
        "minimum_local_mm": minimum,
        "base_local_mm": base,
        "expand_local": {
            axis: bool(axes[axis]) and locked[axis] is None
            for axis in ("x", "y", "z")
        },
        "surplus_preference": constraints["surplus_preference"],
    }


def _complement_participant(value: dict[str, object]) -> dict[str, object]:
    dimensions = _dimension(value["dimensions_mm"])
    return {
        "id": f"complement:{value['id']}",
        "role": "explicit_complement",
        "requested_complement_id": value["id"],
        "complement_kind": value["kind"],
        "name": value["name"],
        "minimum_local_mm": dimensions,
        "base_local_mm": dimensions,
        "expand_local": {"x": False, "y": False, "z": False},
        "surplus_preference": "fixed",
    }


def _orders(values: list[dict[str, object]]) -> list[tuple[str, list[dict[str, object]]]]:
    orders = [
        ("input", list(values)),
        ("area_desc", sorted(values, key=lambda item: (-_area(_mapping(item["base_local_mm"])), str(item["id"])))),
        ("long_side_desc", sorted(values, key=lambda item: (-max(float(_mapping(item["base_local_mm"])["x"]), float(_mapping(item["base_local_mm"])["y"])), str(item["id"])))),
    ]
    unique: list[tuple[str, list[dict[str, object]]]] = []
    seen: set[tuple[str, ...]] = set()
    for name, order in orders:
        signature = tuple(str(item["id"]) for item in order)
        if signature not in seen:
            seen.add(signature)
            unique.append((name, order))
    return unique


def _build_candidate(
    row_items: list[list[dict[str, object]]],
    box: dict[str, float],
    storage_height: float,
    clearance: float,
    *,
    order_name: str,
    orientation_strategy: str,
) -> dict[str, object] | None:
    inner_x = box["x"] - 2.0 * clearance
    inner_y = box["y"] - 2.0 * clearance
    if inner_x <= 0.0 or inner_y <= 0.0 or storage_height <= 0.0:
        return None
    rows: list[list[dict[str, object]]] = []
    for values in row_items:
        oriented = _orient_row(values, inner_x, inner_y, clearance, orientation_strategy)
        if oriented is None:
            return None
        rows.append(oriented)
    base_heights = [max(float(item["base_world_mm"]["y"]) for item in row) for row in rows]
    minimum_y = sum(base_heights) + clearance * max(0, len(rows) - 1)
    if minimum_y > inner_y + _EPSILON:
        return None
    for row, row_height in zip(rows, base_heights):
        if any(float(item["base_world_mm"]["y"]) < row_height - _EPSILON and not bool(item["expand_world"]["y"]) for item in row):
            return None
    extra_y = inner_y - minimum_y
    y_expandable_rows = [index for index, row in enumerate(rows) if all(bool(item["expand_world"]["y"]) for item in row)]
    if extra_y > _EPSILON and not y_expandable_rows:
        return None
    row_heights = list(base_heights)
    _distribute(row_heights, y_expandable_rows, extra_y)

    placements: list[dict[str, object]] = []
    cursor_y = clearance
    rotations = 0
    surplus_values: list[float] = []
    for row, row_height in zip(rows, row_heights):
        base_widths = [float(item["base_world_mm"]["x"]) for item in row]
        printable_width = inner_x - clearance * max(0, len(row) - 1)
        extra_x = printable_width - sum(base_widths)
        if extra_x < -_EPSILON:
            return None
        expandable = [index for index, item in enumerate(row) if bool(item["expand_world"]["x"])]
        if extra_x > _EPSILON and not expandable:
            return None
        widths = list(base_widths)
        _distribute(widths, expandable, max(0.0, extra_x))
        cursor_x = clearance
        for item, width in zip(row, widths):
            base_world = _mapping(item["base_world_mm"])
            expand_world = _mapping(item["expand_world"])
            if storage_height < float(base_world["z"]) - _EPSILON:
                return None
            if storage_height > float(base_world["z"]) + _EPSILON and not bool(expand_world["z"]):
                return None
            world_size = {"x": _round(width), "y": _round(row_height), "z": _round(storage_height)}
            rotated = bool(item["rotated_xy"])
            local_final = {
                "x": world_size["y"] if rotated else world_size["x"],
                "y": world_size["x"] if rotated else world_size["y"],
                "z": world_size["z"],
            }
            minimum_local = _mapping(item["minimum_local_mm"])
            surplus_values.extend(max(0.0, local_final[axis] - float(minimum_local[axis])) for axis in ("x", "y", "z"))
            placement = {
                "id": item["id"],
                "role": item["role"],
                "name": item["name"],
                "origin_mm": {"x": _round(cursor_x), "y": _round(cursor_y), "z": 0.0},
                "world_size_mm": world_size,
                "rotation_deg_z": 90 if rotated else 0,
                "final_outer_dimensions_mm": _rounded(local_final),
                "printable": True,
                "automatic": False,
            }
            for key in ("container_group_id", "requested_complement_id", "complement_kind"):
                if key in item:
                    placement[key] = item[key]
            placements.append(placement)
            cursor_x += width + clearance
            rotations += int(rotated)
        cursor_y += row_height + clearance
    if not isclose(cursor_y - clearance + clearance, box["y"], abs_tol=0.001):
        return None
    imbalance = max(surplus_values, default=0.0) - min(surplus_values, default=0.0)
    score = 1000.0 - len(rows) * 20.0 - rotations * 4.0 - imbalance * 0.05
    candidate_id = f"{order_name}:{len(row_items[0])}:{orientation_strategy}"
    return {
        "candidate_id": candidate_id,
        "order_name": order_name,
        "orientation_strategy": orientation_strategy,
        "row_count": len(rows),
        "rotation_count": rotations,
        "simplicity_score": _round(score),
        "placements": placements,
    }


def _orient_row(
    values: list[dict[str, object]],
    inner_x: float,
    inner_y: float,
    clearance: float,
    strategy: str,
) -> list[dict[str, object]] | None:
    option_sets = [_orientation_options(value) for value in values]
    combinations = product(*option_sets) if len(values) <= 10 else [tuple(_greedy_orientation(value, strategy) for value in values)]
    feasible: list[tuple[tuple[float, float, int], list[dict[str, object]]]] = []
    for combination in combinations:
        width = sum(float(item["base_world_mm"]["x"]) for item in combination) + clearance * max(0, len(values) - 1)
        height = max(float(item["base_world_mm"]["y"]) for item in combination)
        if width > inner_x + _EPSILON or height > inner_y + _EPSILON:
            continue
        rotations = sum(int(bool(item["rotated_xy"])) for item in combination)
        if strategy == "width":
            key = (width, height, rotations)
        elif strategy == "height":
            key = (height, width, rotations)
        else:
            key = (width / inner_x + height / inner_y, rotations, width)
        feasible.append((key, [dict(item) for item in combination]))
    return min(feasible, key=lambda item: item[0])[1] if feasible else None


def _orientation_options(value: dict[str, object]) -> list[dict[str, object]]:
    base = _dimension(value["base_local_mm"])
    expand = _mapping(value["expand_local"])
    options = [_oriented(value, base, expand, False)]
    if not isclose(base["x"], base["y"], abs_tol=_EPSILON):
        options.append(
            _oriented(
                value,
                {"x": base["y"], "y": base["x"], "z": base["z"]},
                {"x": expand["y"], "y": expand["x"], "z": expand["z"]},
                True,
            )
        )
    return options


def _greedy_orientation(value: dict[str, object], strategy: str) -> dict[str, object]:
    options = _orientation_options(value)
    if strategy == "height":
        return min(options, key=lambda item: (float(item["base_world_mm"]["y"]), float(item["base_world_mm"]["x"])))
    return min(options, key=lambda item: (float(item["base_world_mm"]["x"]), float(item["base_world_mm"]["y"])))


def _oriented(value: dict[str, object], base: dict[str, object], expand: dict[str, object], rotated: bool) -> dict[str, object]:
    result = deepcopy(value)
    result["base_world_mm"] = _dimension(base)
    result["expand_world"] = {axis: bool(expand[axis]) for axis in ("x", "y", "z")}
    result["rotated_xy"] = rotated
    return result


def _distribute(values: list[float], indexes: list[int], amount: float) -> None:
    if amount <= _EPSILON or not indexes:
        return
    share = amount / len(indexes)
    distributed = 0.0
    for position, index in enumerate(indexes):
        addition = amount - distributed if position == len(indexes) - 1 else share
        values[index] += addition
        distributed += addition


def _validate_placements(
    placements: list[dict[str, object]],
    box: dict[str, float],
    storage_height: float,
    clearance: float,
) -> dict[str, object]:
    inside = all(
        all(float(_mapping(item["origin_mm"])[axis]) >= -_EPSILON for axis in ("x", "y", "z"))
        and float(_mapping(item["origin_mm"])["x"]) + float(_mapping(item["world_size_mm"])["x"]) <= box["x"] + _EPSILON
        and float(_mapping(item["origin_mm"])["y"]) + float(_mapping(item["world_size_mm"])["y"]) <= box["y"] + _EPSILON
        and float(_mapping(item["origin_mm"])["z"]) + float(_mapping(item["world_size_mm"])["z"]) <= storage_height + _EPSILON
        for item in placements
    )
    no_collisions = all(
        not _intersects(left, right)
        for index, left in enumerate(placements)
        for right in placements[index + 1 :]
    )
    clearances = all(
        _separated_with_clearance(left, right, clearance)
        for index, left in enumerate(placements)
        for right in placements[index + 1 :]
    )
    body_volume = sum(_volume(_mapping(item["world_size_mm"])) for item in placements)
    storage_volume = box["x"] * box["y"] * storage_height
    return {
        "inside_box": inside,
        "no_collisions": no_collisions,
        "clearances_respected": clearances,
        "body_volume_mm3": _round(body_volume),
        "storage_volume_mm3": _round(storage_volume),
        "technical_void_volume_mm3": _round(max(0.0, storage_volume - body_volume)),
        "unassigned_printable_volume_mm3": 0.0,
    }


def _support_plan(flat: dict[str, object], placements: list[dict[str, object]]) -> dict[str, object]:
    reservation = flat.get("reservation_size_mm")
    if reservation is None:
        return {"status": "not_required", "top_support_count": 0, "coverage_ratio": 1.0, "supports": []}
    origin = _mapping(flat["preferred_reservation_origin_mm"])
    size = _mapping(reservation)
    support_area = 0.0
    supports: list[dict[str, object]] = []
    for item in placements:
        item_origin = _mapping(item["origin_mm"])
        item_size = _mapping(item["world_size_mm"])
        if not isclose(float(item_origin["z"]) + float(item_size["z"]), float(origin["z"]), abs_tol=0.001):
            continue
        overlap_x = max(0.0, min(float(item_origin["x"]) + float(item_size["x"]), float(origin["x"]) + float(size["x"])) - max(float(item_origin["x"]), float(origin["x"])))
        overlap_y = max(0.0, min(float(item_origin["y"]) + float(item_size["y"]), float(origin["y"]) + float(size["y"])) - max(float(item_origin["y"]), float(origin["y"])))
        area = overlap_x * overlap_y
        if area > _EPSILON:
            support_area += area
            supports.append({"placement_id": item["id"], "area_mm2": _round(area), "top_z_mm": _round(float(origin["z"]))})
    required_area = float(size["x"]) * float(size["y"])
    ratio = min(1.0, support_area / required_area) if required_area else 1.0
    return {
        "status": "supported_by_requested_bodies" if supports else "unresolved",
        "top_support_count": len(supports),
        "required_area_mm2": _round(required_area),
        "supported_area_mm2": _round(support_area),
        "coverage_ratio": _round(ratio),
        "supports": supports,
        "note": "Les jeux techniques restent des vides entre les faces alignees ; aucun support automatique n est cree.",
    }


def _intersects(left: dict[str, object], right: dict[str, object]) -> bool:
    lo, ls = _mapping(left["origin_mm"]), _mapping(left["world_size_mm"])
    ro, rs = _mapping(right["origin_mm"]), _mapping(right["world_size_mm"])
    return all(float(lo[a]) < float(ro[a]) + float(rs[a]) - _EPSILON and float(ro[a]) < float(lo[a]) + float(ls[a]) - _EPSILON for a in ("x", "y", "z"))


def _separated_with_clearance(left: dict[str, object], right: dict[str, object], clearance: float) -> bool:
    lo, ls = _mapping(left["origin_mm"]), _mapping(left["world_size_mm"])
    ro, rs = _mapping(right["origin_mm"]), _mapping(right["world_size_mm"])
    return any(
        float(lo[a]) + float(ls[a]) + clearance <= float(ro[a]) + _EPSILON
        or float(ro[a]) + float(rs[a]) + clearance <= float(lo[a]) + _EPSILON
        for a in ("x", "y")
    )


def _diagnostic(code: str, message: str, action: str, reference_id: str = "") -> dict[str, object]:
    return {"code": code, "severity": "blocker", "message": message, "action": action, "reference_id": reference_id}


def _digest(value: dict[str, object]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Internal partition value must be a mapping.")
    return value


def _mappings(value: object) -> list[dict[str, Any]]:
    return [_mapping(item) for item in _values(value)]


def _values(value: object) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError("Internal partition value must be a list.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _rounded(value: dict[str, object]) -> dict[str, float]:
    return {axis: _round(float(value[axis])) for axis in ("x", "y", "z")}


def _area(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"])


def _volume(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"]) * float(value["z"])


def _round(value: float) -> float:
    return round(float(value), 4)
