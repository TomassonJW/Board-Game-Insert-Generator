"""Fixtures publiques P64-L09T-G, sans nom ni chemin de projet personnel."""

from __future__ import annotations

from copy import deepcopy

from board_game_insert_generator.project_v1 import (
    blank_project_v1,
    normalize_project_draft,
)


CASE_02_VARIANTS = (
    "base",
    "content_only",
    "clearance_only",
    "combined",
)


def anonymized_case_01_plus_project() -> dict[str, object]:
    """Cas dense public avec réservations, proche de la famille CasLimite01+."""

    project = blank_project_v1()
    project["project_name"] = "P64-L09T-G cas 01 plus anonymise"
    project["box"] = {
        "inner_dimensions_mm": {"x": 250.0, "y": 180.0, "z": 70.0},
        "usable_height_mm": 69.8,
        "lid_clearance_mm": 0.2,
    }
    group_ids = tuple(f"container-{index:03d}" for index in range(1, 13))
    project["container_groups"] = [
        _group(group_id) for group_id in group_ids
    ]
    project["contents"] = [
        _content(
            f"content-{index:03d}",
            "container-001",
            (20.0, 20.0, 10.0),
            shape_kind="rectangle",
        )
        for index in range(1, 5)
    ]
    project["contents"].extend(
        _counted_card(
            f"content-{index:03d}",
            group_id,
        )
        for index, group_id in zip(
            range(5, 9),
            (
                "container-002",
                "container-003",
                "container-006",
                "container-007",
            ),
        )
    )
    project["contents"].extend(
        _content(
            f"content-{index:03d}",
            group_id,
            (16.0, 16.0, 16.0),
            shape_kind="cube",
            quantity=5,
        )
        for index, group_id in zip(
            range(9, 11),
            ("container-004", "container-005"),
        )
    )
    project["contents"].extend(
        _content(
            f"content-{index:03d}",
            group_id,
            (20.0, 20.0, 3.0),
            shape_kind="round",
            quantity=10,
        )
        for index, group_id in zip(
            range(11, 16),
            (
                "container-008",
                "container-009",
                "container-010",
                "container-011",
                "container-012",
            ),
        )
    )
    project["flat_items"] = [
        _flat_item(
            "flat-board",
            "board",
            (100.0, 100.0, 2.0),
            quantity=1,
            stack_order=0,
        ),
    ]
    return normalize_project_draft(project).project


def anonymized_case_02_variant(kind: str) -> dict[str, object]:
    """Isole contenu et jeux sur une reproduction publique de CasLimite02."""

    if kind not in CASE_02_VARIANTS:
        raise ValueError(f"Unknown P64-L09T-G case 02 variant: {kind!r}.")
    project = blank_project_v1()
    project["project_name"] = f"P64-L09T-G cas 02 anonymise {kind}"
    project["box"] = {
        "inner_dimensions_mm": {"x": 240.0, "y": 180.0, "z": 70.0},
        "usable_height_mm": 69.8,
        "lid_clearance_mm": 0.2,
    }
    clearance = 0.4 if kind in {"clearance_only", "combined"} else 0.6
    project["layout"] = {
        **deepcopy(project["layout"]),
        "layout_clearance_mm": clearance,
        "container_box_xy_clearance_mm": clearance,
        "container_z_clearance_mm": clearance,
        "default_content_clearance_mm": clearance,
    }
    project["container_groups"] = [
        _group("container-001"),
        _group(
            "container-002",
            dimension_modes={"x": "target", "y": "auto", "z": "auto"},
            target_x=80.0,
        ),
        _group("container-003"),
        _group(
            "container-004",
            dimension_modes={"x": "fixed", "y": "auto", "z": "auto"},
            locked_x=79.0667,
        ),
        _group("container-005"),
        _group("container-006"),
        _group("container-007"),
        _group("container-008"),
    ]
    project["contents"] = [
        _content(
            "content-001",
            "container-001",
            (18.0, 18.0, 2.5),
            shape_kind="round",
            quantity=12,
        ),
        _content(
            "content-002",
            "container-001",
            (12.0, 12.0, 12.0),
            shape_kind="cube",
            quantity=8,
        ),
        _card("content-003", "container-002", "flat", sleeved=True),
        _card(
            "content-004",
            "container-003",
            "upright_long_edge",
            sleeved=True,
        ),
        _card("content-005", "container-004", "flat"),
        _card("content-006", "container-005", "flat"),
        _card("content-007", "container-006", "flat"),
        _card("content-008", "container-007", "flat"),
        _card("content-009", "container-008", "flat"),
    ]
    if kind in {"content_only", "combined"}:
        project["contents"].extend(
            _content(
                f"content-{index:03d}",
                "container-006",
                (20.0, 20.0, 10.0),
                shape_kind="rectangle",
            )
            for index in range(10, 13)
        )
    project["flat_items"] = [
        _flat_item(
            "flat-001",
            "board",
            (110.0, 120.0, 4.0),
            quantity=1,
            stack_order=0,
        ),
        _flat_item(
            "flat-002",
            "rulebook",
            (60.0, 110.0, 2.0),
            quantity=1,
            stack_order=1,
            rotation_deg_z=90,
        ),
    ]
    return normalize_project_draft(project).project


def _group(
    group_id: str,
    *,
    dimension_modes: dict[str, str] | None = None,
    target_x: float | None = None,
    locked_x: float | None = None,
) -> dict[str, object]:
    return {
        "id": group_id,
        "name": f"Conteneur public {group_id}",
        "wall_thickness_mm": None,
        "floor_thickness_mm": None,
        "dimension_modes": dimension_modes
        or {"x": "auto", "y": "auto", "z": "auto"},
        "target_outer_dimensions_mm": {
            "x": target_x,
            "y": None,
            "z": None,
        },
        "locked_outer_dimensions_mm": {
            "x": locked_x,
            "y": None,
            "z": None,
        },
    }


def _content(
    content_id: str,
    group_id: str,
    dimensions: tuple[float, float, float],
    *,
    shape_kind: str = "custom",
    quantity: int = 1,
) -> dict[str, object]:
    return {
        "id": content_id,
        "name": f"Contenu public {content_id}",
        "shape_kind": shape_kind,
        "dimensions_mm": {
            "x": dimensions[0],
            "y": dimensions[1],
            "z": dimensions[2],
        },
        "quantity": quantity,
        "container_group_id": group_id,
        "content_clearance_mm": None,
        "measurement_confidence": "exact",
    }


def _card(
    content_id: str,
    group_id: str,
    storage_orientation: str,
    *,
    sleeved: bool = False,
) -> dict[str, object]:
    value = _content(
        content_id,
        group_id,
        (63.0, 88.0, 24.0),
        shape_kind="cards",
    )
    value.update(
        {
            "storage_orientation": storage_orientation,
            "sleeved": sleeved,
            "card_stack_mode": "thickness",
            "card_thickness_mm": 0.32,
        }
    )
    return value


def _counted_card(
    content_id: str,
    group_id: str,
) -> dict[str, object]:
    value = _content(
        content_id,
        group_id,
        (63.5, 88.9, 19.2),
        shape_kind="cards",
        quantity=60,
    )
    value.update(
        {
            "storage_orientation": "auto",
            "sleeved": False,
            "card_stack_mode": "count",
            "card_thickness_mm": 0.32,
        }
    )
    return value


def _flat_item(
    item_id: str,
    kind: str,
    dimensions: tuple[float, float, float],
    *,
    quantity: int,
    stack_order: int,
    rotation_deg_z: int = 0,
) -> dict[str, object]:
    return {
        "id": item_id,
        "name": f"Element plat public {item_id}",
        "kind": kind,
        "dimensions_mm": {
            "x": dimensions[0],
            "y": dimensions[1],
            "z": dimensions[2],
        },
        "quantity": quantity,
        "stack_order": stack_order,
        "rotation_deg_z": rotation_deg_z,
        "origin_mm": None,
    }
