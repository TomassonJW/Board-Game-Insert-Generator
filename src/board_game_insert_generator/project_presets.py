"""Deterministic creation presets for the embedded Fusion project editor.

Presets only seed an editable draft. They never solve a partition and never
depend on Fusion APIs.
"""

from __future__ import annotations

from copy import deepcopy

from board_game_insert_generator.asset_catalog import card_catalog
from board_game_insert_generator.project_v1 import normalize_project_draft


CREATION_PRESETS_SCHEMA_V1 = "bgig.creation_presets.v1"


_CONTENT_PRESETS = (
    {
        "key": "tokens",
        "label": "Jetons",
        "group_name": "Bac jetons",
        "content": {
            "name": "Jetons",
            "shape_kind": "round",
            "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 3.0},
            "quantity": 10,
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
    },
    {
        "key": "cards",
        "label": "Cartes sleevees",
        "group_name": "Bac cartes",
        "content": {
            "name": "Cartes sleevees",
            "shape_kind": "cards",
            "dimensions_mm": {"x": 66.0, "y": 91.0, "z": 24.0},
            "base_dimensions_mm": {"x": 66.0, "y": 91.0, "z": 24.0},
            "dimension_source": "catalog",
            "card_format_id": "poker",
            "sleeved": True,
            "storage_orientation": "auto",
            "card_stack_mode": "count",
            "card_thickness_mm": 0.32,
            "quantity": 60,
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
    },
    {
        "key": "dice",
        "label": "Des",
        "group_name": "Bac des",
        "content": {
            "name": "Des",
            "shape_kind": "cube",
            "dimensions_mm": {"x": 16.0, "y": 16.0, "z": 16.0},
            "quantity": 5,
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
    },
    {
        "key": "pawns",
        "label": "Pions",
        "group_name": "Bac pions",
        "content": {
            "name": "Pions",
            "shape_kind": "meeple",
            "dimensions_mm": {"x": 20.0, "y": 12.0, "z": 30.0},
            "quantity": 5,
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
    },
)


def build_creation_presets(raw_project: object, *, storage_height_mm: float | None = None) -> dict[str, object]:
    """Return UI seed values adapted to the current usable storage height."""

    project = normalize_project_draft(raw_project).project
    available_height = (
        float(storage_height_mm)
        if storage_height_mm is not None
        else float(project["box"]["usable_height_mm"])
    )
    default_height = round(max(1.0, available_height), 4)
    complements = (
        {
            "key": "hollow",
            "label": "Bac vide",
            "element": {
                "name": "Bac vide",
                "kind": "hollow",
                "mode": "exact",
                "dimensions_mm": {"x": 40.0, "y": 40.0, "z": default_height},
                "container_group_id": None,
            },
        },
        {
            "key": "solid",
            "label": "Bloc plein / cale",
            "element": {
                "name": "Bloc plein",
                "kind": "solid",
                "mode": "exact",
                "dimensions_mm": {"x": 20.0, "y": 20.0, "z": default_height},
                "container_group_id": None,
            },
        },
        {
            "key": "separator",
            "label": "Separateur",
            "element": {
                "name": "Separateur",
                "kind": "separator",
                "mode": "exact",
                "dimensions_mm": {"x": 2.0, "y": 50.0, "z": default_height},
                "container_group_id": None,
            },
        },
    )
    return {
        "schema_version": CREATION_PRESETS_SCHEMA_V1,
        "card_catalog": card_catalog(),
        "contents": deepcopy(list(_CONTENT_PRESETS)),
        "complements": deepcopy(list(complements)),
        "defaults": {
            "container_group": {
                "name": "Nouveau bac",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
                "expansion_axes": {"x": True, "y": True, "z": True},
                "locked_outer_dimensions_mm": {"x": None, "y": None, "z": None},
                "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
                "target_outer_dimensions_mm": {"x": None, "y": None, "z": None},
                "surplus_preference": "balanced",
            }
        },
    }
