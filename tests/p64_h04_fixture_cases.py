"""Anonymised P64-H04 regression corpus; no local Fusion path or project name."""

from __future__ import annotations

from copy import deepcopy

from board_game_insert_generator.project_v1 import blank_project_v1


def simple_success_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {"inner_dimensions_mm": {"x": 240.0, "y": 180.0, "z": 70.0}, "usable_height_mm": 66.0, "lid_clearance_mm": 2.0}
    project["container_groups"] = [_group("simple")]
    project["contents"] = [_content("simple", "simple-content", {"x": 18.0, "y": 18.0, "z": 5.0}, quantity=4)]
    return project


def h01_dense_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {"inner_dimensions_mm": {"x": 400.0, "y": 300.0, "z": 183.0}, "usable_height_mm": 183.0, "lid_clearance_mm": 0.0}
    dimensions = ((30.0, 22.0, 12.0), (24.0, 35.0, 18.0), (42.0, 18.0, 10.0), (28.0, 28.0, 16.0), (36.0, 24.0, 14.0))
    project["container_groups"] = [_group(f"dense-{index:02d}") for index in range(30)]
    project["contents"] = [
        _content(f"dense-{index:02d}", f"dense-content-{index:02d}", _dimension(dimensions[index % len(dimensions)]))
        for index in range(30)
    ]
    return project


def h02_reservations_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {"inner_dimensions_mm": {"x": 250.0, "y": 180.0, "z": 70.0}, "usable_height_mm": 69.8, "lid_clearance_mm": 0.2}
    definitions = (
        ("tokens", {"x": 25.0, "y": 47.4, "z": 30.0}),
        ("c0", {"x": 69.0, "y": 91.0, "z": 35.0}),
        ("c1", {"x": 89.0, "y": 62.72, "z": 64.0}),
        ("c2", {"x": 63.0, "y": 88.0, "z": 24.0}),
        ("c3", {"x": 63.0, "y": 88.0, "z": 24.0}),
        ("c4", {"x": 63.0, "y": 88.0, "z": 24.0}),
        ("c5", {"x": 88.9, "y": 19.2, "z": 63.5}),
        ("c6", {"x": 38.4, "y": 32.6, "z": 48.0}),
    )
    project["container_groups"] = [_group(group_id) for group_id, _ in definitions]
    project["contents"] = [_content(group_id, f"content-{group_id}", dimensions) for group_id, dimensions in definitions]
    project["flat_items"] = [
        {"id": "flat-a", "name": "Plateau", "kind": "board", "dimensions_mm": {"x": 115.0, "y": 110.0, "z": 3.0}, "quantity": 3, "stack_order": 1, "origin_mm": {"x": 10.0, "y": 10.0}},
        {"id": "flat-b", "name": "Livret", "kind": "rulebook", "dimensions_mm": {"x": 110.0, "y": 60.0, "z": 3.0}, "quantity": 1, "stack_order": 0, "origin_mm": {"x": 10.0, "y": 20.0}},
    ]
    return project


def h03_contextual_unresolved_project() -> dict[str, object]:
    project = h02_reservations_project()
    token = next(item for item in project["contents"] if item["container_group_id"] == "tokens")
    token["dimensions_mm"]["y"] = 69.8
    for index in range(6):
        group_id = f"stress-{index:02d}"
        project["container_groups"].append(_group(group_id))
        project["contents"].append(_content(group_id, f"stress-content-{index:02d}", {"x": 20.0, "y": 20.0, "z": 10.0}))
    return project


def formal_conflict_project() -> dict[str, object]:
    project = blank_project_v1()
    project["box"] = {"inner_dimensions_mm": {"x": 40.0, "y": 40.0, "z": 20.0}, "usable_height_mm": 20.0, "lid_clearance_mm": 0.0}
    project["container_groups"] = [_group("oversized")]
    project["contents"] = [_content("oversized", "oversized-content", {"x": 50.0, "y": 10.0, "z": 10.0})]
    return project


def _group(group_id: str) -> dict[str, object]:
    return {"id": group_id, "name": f"Bac {group_id}", "wall_thickness_mm": None, "floor_thickness_mm": None}


def _content(group_id: str, content_id: str, dimensions: dict[str, float], *, quantity: int = 1) -> dict[str, object]:
    return {"id": content_id, "name": f"Élément {content_id}", "shape_kind": "custom", "dimensions_mm": deepcopy(dimensions), "quantity": quantity, "container_group_id": group_id, "content_clearance_mm": None, "measurement_confidence": "exact"}


def _dimension(value: tuple[float, float, float]) -> dict[str, float]:
    return {"x": value[0], "y": value[1], "z": value[2]}
