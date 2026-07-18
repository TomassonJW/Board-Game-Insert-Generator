"""Deterministic global container-variant fixtures for P64-V2H03C."""

from __future__ import annotations

from copy import deepcopy

from p64_v2h03b_fixture_cases import multi_cavity_tradeoff_project


def multi_container_variant_dead_end_project() -> dict[str, object]:
    """Two canonical envelopes fail side-by-side; certified relayouts fit."""

    project = multi_cavity_tradeoff_project()
    project["project_name"] = "P64-V2H03C multi-container variant dead end"
    project["box"] = {
        "inner_dimensions_mm": {"x": 148.0, "y": 80.0, "z": 10.0},
        "usable_height_mm": 10.0,
        "lid_clearance_mm": 0.0,
    }
    source_group = project["container_groups"][0]
    source_group["id"] = "left"
    source_group["name"] = "Bac gauche"
    for item in project["contents"]:
        item["container_group_id"] = "left"

    right_group = deepcopy(source_group)
    right_group["id"] = "right"
    right_group["name"] = "Bac droit"
    project["container_groups"].append(right_group)
    for item in deepcopy(project["contents"]):
        item["id"] = "right-" + item["id"]
        item["name"] = "Droite " + item["name"]
        item["container_group_id"] = "right"
        project["contents"].append(item)
    return project


def localized_variant_compatibility_project() -> dict[str, object]:
    """A top inset rejects the canonical cavity position, not every relayout."""

    project = multi_cavity_tradeoff_project()
    project["project_name"] = "P64-V2H03C localized variant compatibility"
    project["box"] = {
        "inner_dimensions_mm": {"x": 92.0, "y": 86.0, "z": 10.0},
        "usable_height_mm": 10.0,
        "lid_clearance_mm": 0.0,
    }
    project["flat_items"] = [
        {
            "id": "localized-board",
            "name": "Plateau localise",
            "kind": "board",
            "dimensions_mm": {"x": 16.0, "y": 16.0, "z": 3.0},
            "quantity": 1,
            "stack_order": 0,
            "origin_mm": {"x": 3.0, "y": 53.0},
            "rotation_deg_z": 0,
        }
    ]
    return project

def multi_container_variant_unsolved_project() -> dict[str, object]:
    """Same local frontiers in a globally undersized box; no proof is claimed."""

    project = multi_container_variant_dead_end_project()
    project["project_name"] = "P64-V2H03C bounded unsolved variant case"
    project["box"] = {
        "inner_dimensions_mm": {"x": 100.0, "y": 76.0, "z": 10.0},
        "usable_height_mm": 10.0,
        "lid_clearance_mm": 0.0,
    }
    return project
