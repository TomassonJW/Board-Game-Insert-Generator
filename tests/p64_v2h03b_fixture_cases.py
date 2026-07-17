"""Deterministic local-variant fixtures for P64-V2H03B."""

from __future__ import annotations

from copy import deepcopy

from board_game_insert_generator.project_v1 import blank_project_v1


def multi_cavity_tradeoff_project() -> dict[str, object]:
    """One real multi-cavity body with useful X/Y envelope trade-offs."""

    project = blank_project_v1()
    project["project_name"] = "P64-V2H03B multi-cavity trade-off"
    project["box"] = {
        "inner_dimensions_mm": {"x": 180.0, "y": 140.0, "z": 50.0},
        "usable_height_mm": 48.0,
        "lid_clearance_mm": 2.0,
    }
    project["container_groups"] = [
        {
            "id": "tradeoff",
            "name": "Bac multi-cavites",
            "wall_thickness_mm": 2.0,
            "floor_thickness_mm": 2.0,
        }
    ]
    dimensions = (
        ("long", 48.0, 18.0, 8.0),
        ("wide", 36.0, 28.0, 7.0),
        ("tall", 24.0, 42.0, 6.0),
        ("small", 18.0, 18.0, 5.0),
    )
    project["contents"] = [
        _content("tradeoff", content_id, x, y, z)
        for content_id, x, y, z in dimensions
    ]
    return project


def project_with_dimension_mode(mode: str) -> dict[str, object]:
    project = multi_cavity_tradeoff_project()
    group = project["container_groups"][0]
    if mode == "auto":
        return project
    group["dimension_modes"] = {"x": mode, "y": "auto", "z": "auto"}
    group["target_outer_dimensions_mm"] = {"x": 100.0, "y": None, "z": None}
    return project


def localized_reservation_project() -> dict[str, object]:
    project = multi_cavity_tradeoff_project()
    project["flat_items"] = [
        {
            "id": "localized-board",
            "name": "Plateau localise",
            "kind": "board",
            "dimensions_mm": {"x": 72.0, "y": 48.0, "z": 3.0},
            "quantity": 1,
            "stack_order": 0,
            "origin_mm": {"x": 82.0, "y": 12.0},
            "rotation_deg_z": 0,
        }
    ]
    return project


def dense_11_containers_34_contents_project() -> dict[str, object]:
    """Anonymised 11-container/34-content mechanism snapshot.

    The fixture exercises one genuinely dense multi-cavity container and ten
    smaller two-cavity containers. It records the mechanism, not an assertion
    that a global solution exists.
    """

    project = blank_project_v1()
    project["project_name"] = "P64-V2H03B anonymised dense mechanism"
    project["box"] = {
        "inner_dimensions_mm": {"x": 250.0, "y": 180.0, "z": 70.0},
        "usable_height_mm": 69.8,
        "lid_clearance_mm": 0.2,
    }
    group_ids = ["dense-core", *(f"satellite-{index:02d}" for index in range(10))]
    project["container_groups"] = [
        {
            "id": group_id,
            "name": f"Bac {group_id}",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
        for group_id in group_ids
    ]
    dimensions = (
        (18.0, 12.0, 4.0),
        (24.0, 16.0, 6.0),
        (14.0, 28.0, 5.0),
        (32.0, 10.0, 7.0),
        (20.0, 20.0, 8.0),
        (26.0, 14.0, 5.0),
        (16.0, 30.0, 6.0),
    )
    contents: list[dict[str, object]] = []
    for index in range(14):
        x, y, z = dimensions[index % len(dimensions)]
        contents.append(_content("dense-core", f"core-{index:02d}", x, y, z, clearance=0.4))
    for group_index, group_id in enumerate(group_ids[1:]):
        for item_index in range(2):
            x, y, z = dimensions[(group_index * 2 + item_index) % len(dimensions)]
            contents.append(
                _content(
                    group_id,
                    f"satellite-{group_index:02d}-{item_index}",
                    x,
                    y,
                    z,
                    clearance=0.4,
                )
            )
    project["contents"] = contents
    project["flat_items"] = [
        {
            "id": "dense-board",
            "name": "Plateau anonymise",
            "kind": "board",
            "dimensions_mm": {"x": 115.0, "y": 110.0, "z": 3.0},
            "quantity": 2,
            "stack_order": 0,
            "origin_mm": {"x": 10.0, "y": 10.0},
            "rotation_deg_z": 0,
        }
    ]
    assert len(group_ids) == 11
    assert len(contents) == 34
    return project


def with_external_container_override(project: dict[str, object]) -> dict[str, object]:
    result = deepcopy(project)
    result["container_groups"][0]["clearance_overrides_v1"] = {
        "between_mm": {"x": 9.0, "y": 8.0, "z": 7.0},
        "box_per_side_xy_mm": {"x": 6.0, "y": 5.0},
    }
    return result


def with_asset_clearance_override(project: dict[str, object]) -> dict[str, object]:
    result = deepcopy(project)
    result["contents"][0]["clearance_override_mm"] = {"x": 1.0, "y": 0.5, "z": 0.25}
    return result


def _content(
    group_id: str,
    content_id: str,
    x: float,
    y: float,
    z: float,
    *,
    clearance: float = 0.0,
) -> dict[str, object]:
    return {
        "id": content_id,
        "name": f"Element {content_id}",
        "shape_kind": "rectangle",
        "dimensions_mm": {"x": x, "y": y, "z": z},
        "quantity": 1,
        "container_group_id": group_id,
        "content_clearance_mm": clearance,
        "measurement_confidence": "exact",
    }
