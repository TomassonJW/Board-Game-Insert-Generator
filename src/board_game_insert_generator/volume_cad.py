"""Pure V0.1 materialisation from a resolved volume plan to CAD IR.

The module consumes the deterministic P41 result.  It deliberately does not
recalculate placement, dimensions, clearances or any V0.2/V0.3 feature, and it
does not import Fusion.  Fusion remains an adapter of the scene produced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from board_game_insert_generator.cad_ir import (
    CAD_IR_COORDINATE_SYSTEM,
    CAD_IR_SCHEMA_VERSION,
    CAD_IR_UNITS,
    CAVITY_OPERATION_KIND,
    CadBody,
    CadBoxReference,
    CadCavity,
    CadComponent,
    CadFrame,
    CadOperation,
    CadParameter,
    CadScene,
    CadSceneMetadata,
)
from board_game_insert_generator.models import Dimension3D, Point3D
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.volume_closure import solve_project_volume


FUNCTIONAL_CAD_BUILD_SCHEMA_V1 = "bgig.functional_cad_build.v1"
_FUSION_SMOKE_STATUS = "planned_for_fusion_smoke"


class FunctionalCadBuildError(ValueError):
    """Raised when a resolved V0.1 volume cannot become valid CAD geometry."""


@dataclass(frozen=True)
class _Materialization:
    components: tuple[CadComponent, ...]
    skipped_regions: tuple[dict[str, object], ...]
    blockers: tuple[str, ...]


def build_functional_cad(raw_project: object) -> dict[str, object]:
    """Build the printable V0.1 bodies after the complete-volume solve.

    A volume plan which is already impossible is returned unchanged with no CAD
    scene.  An exact user request which cannot retain its requested walls is a
    constructibility error, never silently downgraded to a thinner object.
    Automatically proposed residual regions may be intentionally left as a
    documented technical clearance when their usable inset is too small.
    """

    normalized = normalize_project_draft(raw_project)
    project = normalized.project
    volume_plan = solve_project_volume(raw_project)
    base = {
        "schema_version": FUNCTIONAL_CAD_BUILD_SCHEMA_V1,
        "source": volume_plan["source"],
        "project_name": project["project_name"],
        "volume_plan": volume_plan,
    }
    if _mapping(volume_plan["summary"])["status"] != "constructed_plan":
        return {
            **base,
            "status": "impossible",
            "cad_ir": None,
            "materialization": {
                "status": "not_started",
                "component_count": 0,
                "reason": "The complete-volume plan is impossible, so no CAD body is generated.",
                "skipped_regions": [],
            },
            "blockers": list(_values(volume_plan["blockers"])),
            "limitations": [
                "No CAD geometry is produced from an impossible volume plan.",
                "No Fusion or physical-print validation is claimed.",
            ],
        }

    materialization = _materialize(project, volume_plan)
    if materialization.blockers:
        return {
            **base,
            "status": "impossible",
            "cad_ir": None,
            "materialization": {
                "status": "blocked",
                "component_count": 0,
                "reason": "At least one exact requested volume cannot retain the configured walls or floor.",
                "skipped_regions": list(materialization.skipped_regions),
            },
            "blockers": list(materialization.blockers),
            "limitations": [
                "The V0.1 volume plan was solved, but its exact requested geometry is not printable with the configured minimum walls.",
                "No Fusion or physical-print validation is claimed.",
            ],
        }

    layout = _mapping(project["layout"])
    box = _mapping(project["box"])
    box_size = _dimension(box["inner_dimensions_mm"])
    scene = CadScene(
        schema_version=CAD_IR_SCHEMA_VERSION,
        units=CAD_IR_UNITS,
        coordinate_system=CAD_IR_COORDINATE_SYSTEM,
        frame=CadFrame(origin=Point3D(x=0.0, y=0.0, z=0.0)),
        box_reference=CadBoxReference(
            id="box-reference",
            name="Boite de reference - non imprimable",
            origin=Point3D(x=0.0, y=0.0, z=0.0),
            size=_as_dimension(box_size),
        ),
        parameters=(
            _parameter("layout_clearance_mm", float(layout["layout_clearance_mm"]), "clearance", "Jeu commun entre les bacs et la boite."),
            _parameter("default_wall_thickness_mm", float(layout["default_wall_thickness_mm"]), "geometry_default", "Epaisseur minimale de paroi par defaut."),
            _parameter("default_floor_thickness_mm", float(layout["default_floor_thickness_mm"]), "geometry_default", "Epaisseur minimale de fond par defaut."),
        ),
        components=materialization.components,
        metadata=CadSceneMetadata(
            project_name=str(project["project_name"]),
            source_path=None,
            layout_strategy="project_v1_complete_volume_v1",
            print_profile="project_v1_functional_v0_1",
            warnings=tuple(
                [
                    "Geometrie V0.1 preparee pour un smoke Fusion ; aucun statut Fusion ou impression n est revendique.",
                    "Les arrondis, encoches, finitions et couvercles sont exclus de cette scene V0.1.",
                ]
                + (
                    ["Certaines regions automatiques restent du jeu technique car elles sont trop petites pour les parois minimales."]
                    if materialization.skipped_regions
                    else []
                )
            ),
            box_fill_plan={
                "schema_version": str(volume_plan["schema_version"]),
                "summary": _mapping(volume_plan["summary"]),
                "support": _mapping(volume_plan["support"]),
                "reservations": _values(volume_plan["reservations"]),
            },
        ),
    )
    cad_ir = scene.to_dict()
    return {
        **base,
        "status": _FUSION_SMOKE_STATUS,
        "cad_ir": cad_ir,
        "materialization": {
            "status": _FUSION_SMOKE_STATUS,
            "component_count": len(materialization.components),
            "container_component_count": sum(1 for component in materialization.components if component.functional_type == "v0_1_storage_container"),
            "hollow_fill_component_count": sum(1 for component in materialization.components if component.functional_type == "v0_1_hollow_fill"),
            "solid_component_count": sum(1 for component in materialization.components if component.functional_type in {"v0_1_solid_fill", "v0_1_separator"}),
            "cavity_count": sum(len(component.body.cavities) for component in materialization.components),
            "skipped_regions": list(materialization.skipped_regions),
        },
        "blockers": [],
        "limitations": [
            "The scene is CAD IR prepared for Fusion; Fusion has not yet executed or observed it.",
            "V0.1 uses rectangular functional bodies only: no aesthetic rounding, ergonomic cut-out or lid is materialized.",
            "A skipped automatic residual region is retained as intentional technical clearance, never represented as a thinner-than-requested tray.",
            "No physical print, fit or slicer validation is claimed.",
        ],
    }


def _materialize(project: dict[str, object], volume_plan: dict[str, object]) -> _Materialization:
    container_plan = _mapping(volume_plan["container_plan"])
    containers_by_group = {
        str(_mapping(item)["container_group_id"]): _mapping(item)
        for item in _values(container_plan["containers"])
        if _mapping(item)["status"] == "ready"
    }
    layout = _mapping(project["layout"])
    clearance = float(layout["layout_clearance_mm"])
    components: list[CadComponent] = []
    blockers: list[str] = []

    for placement_value in _values(volume_plan["placements"]):
        placement = _mapping(placement_value)
        group_id = str(placement["container_group_id"])
        container = containers_by_group.get(group_id)
        if container is None:
            blockers.append(f"Le bac {placement['name']!r} n a plus de plan de logements associe.")
            continue
        try:
            components.append(_container_component(placement, container))
        except FunctionalCadBuildError as error:
            blockers.append(str(error))

    for fill_value in _values(volume_plan["fill_placements"]):
        fill = _mapping(fill_value)
        try:
            components.append(_exact_fill_component(fill, layout))
        except FunctionalCadBuildError as error:
            blockers.append(str(error))

    skipped_regions: list[dict[str, object]] = []
    for region_value in _values(volume_plan["free_regions"]):
        region = _mapping(region_value)
        classification = str(region["classification"])
        if classification == "technical_clearance":
            continue
        candidate = _inset_automatic_region(region, clearance)
        if candidate is None:
            skipped_regions.append(
                {
                    "region_id": region["id"],
                    "classification": classification,
                    "reason": "The common clearance leaves no printable automatic body in this region.",
                }
            )
            continue
        try:
            components.append(_automatic_fill_component(region, candidate, layout))
        except FunctionalCadBuildError as error:
            skipped_regions.append(
                {"region_id": region["id"], "classification": classification, "reason": str(error)}
            )

    if not components and not blockers:
        blockers.append("Le plan ne contient aucun bac ou remplissage imprimable a materialiser.")
    return _Materialization(tuple(components), tuple(skipped_regions), tuple(blockers))


def _container_component(placement: dict[str, object], container: dict[str, object]) -> CadComponent:
    body_id = f"body:{placement['id']}"
    original_outer = _dimension(container["outer_dimensions_mm"])
    placed_size = _dimension(placement["size_mm"])
    origin = _point(placement["origin_mm"])
    floor = float(container["floor_thickness_mm"])
    cavities: list[CadCavity] = []
    rotated = bool(placement["rotated_xy"])
    for compartment_value in _values(container["compartments"]):
        compartment = _mapping(compartment_value)
        local_origin = _dimension(compartment["local_origin_mm"])
        cavity_xy = _dimension(compartment["inner_dimensions_mm"])
        cavity_size = {"x": cavity_xy["x"], "y": cavity_xy["y"], "z": placed_size["z"] - floor}
        if cavity_size["z"] <= 0:
            raise FunctionalCadBuildError(
                f"Le bac {placement['name']!r} ne peut pas garder son fond minimal de {floor:.2f} mm."
            )
        if rotated:
            local_origin, cavity_size = _rotate_xy(local_origin, cavity_size, original_outer)
        cavity_id = f"{placement['id']}:{compartment['id']}"
        _assert_cavity_fits(placement["name"], cavity_id, local_origin, cavity_size, placed_size, floor)
        cavities.append(
            CadCavity(
                id=cavity_id,
                functional_type="asset_compartment",
                local_origin=_as_point(local_origin),
                size=_as_dimension(cavity_size),
                clearance_mm=float(compartment["content_clearance_mm"]),
                clearance_source="project_v1_content_clearance_mm",
                comment=f"Logement V0.1 pour {compartment['content_name']}; ouvert par le dessus.",
                features=(),
                status=_FUSION_SMOKE_STATUS,
                fusion_generation=_FUSION_SMOKE_STATUS,
            )
        )
    return _component(
        component_id=f"component:{placement['id']}",
        name=f"{placement['name']} - bac fonctionnel",
        module_id=str(placement["container_group_id"]),
        instance_id=str(placement["id"]),
        functional_type="v0_1_storage_container",
        body_id=body_id,
        origin=origin,
        size=placed_size,
        cavities=tuple(cavities),
        metadata={
            "source": "p42_functional_volume_materialization_v1",
            "container_group_id": placement["container_group_id"],
            "source_content_ids": placement["source_content_ids"],
            "rotated_xy": rotated,
            "wall_thickness_mm": container["wall_thickness_mm"],
            "floor_thickness_mm": container["floor_thickness_mm"],
            "compartment_layout": container["compartment_layout"],
        },
    )


def _exact_fill_component(fill: dict[str, object], layout: dict[str, object]) -> CadComponent:
    kind = str(fill["kind"])
    fill_kind = kind.removeprefix("fill:")
    return _fill_component(
        component_id=f"component:{fill['id']}",
        name=f"{fill_kind.replace('_', ' ').capitalize()} demande",
        instance_id=str(fill["id"]),
        fill_kind=fill_kind,
        origin=_point(fill["origin_mm"]),
        size=_dimension(fill["size_mm"]),
        layout=layout,
        metadata={
            "source": "p42_exact_requested_fill_v1",
            "requested_fill_id": fill["requested_fill_id"],
            "associated_container_group_id": fill["associated_container_group_id"],
        },
        exact=True,
    )


def _automatic_fill_component(region: dict[str, object], candidate: dict[str, dict[str, float]], layout: dict[str, object]) -> CadComponent:
    classification = str(region["classification"])
    fill_kind = "solid" if classification == "solid_fill_requested" else "hollow"
    label = "Support vide" if classification == "support_hollow_fill_candidate" else ("Bac vide propose" if fill_kind == "hollow" else "Remplissage plein propose")
    return _fill_component(
        component_id=f"component:{region['id']}",
        name=f"{label} - {region['id']}",
        instance_id=str(region["id"]),
        fill_kind=fill_kind,
        origin=candidate["origin_mm"],
        size=candidate["size_mm"],
        layout=layout,
        metadata={
            "source": "p42_automatic_residual_fill_v1",
            "source_region_id": region["id"],
            "source_classification": classification,
            "support_role": "upper_flat_stack" if classification == "support_hollow_fill_candidate" else None,
            "requested_fill_id": region["requested_fill_id"],
            "clearance_inset_mm": candidate["clearance_inset_mm"],
        },
        exact=False,
    )


def _fill_component(
    *,
    component_id: str,
    name: str,
    instance_id: str,
    fill_kind: str,
    origin: dict[str, float],
    size: dict[str, float],
    layout: dict[str, object],
    metadata: dict[str, object],
    exact: bool,
) -> CadComponent:
    if fill_kind not in {"hollow", "solid", "separator"}:
        raise FunctionalCadBuildError(f"Le type de remplissage {fill_kind!r} est inconnu.")
    body_id = f"body:{instance_id}"
    cavities: tuple[CadCavity, ...] = ()
    functional_type = {"hollow": "v0_1_hollow_fill", "solid": "v0_1_solid_fill", "separator": "v0_1_separator"}[fill_kind]
    if fill_kind == "hollow":
        wall = float(layout["default_wall_thickness_mm"])
        floor = float(layout["default_floor_thickness_mm"])
        cavity_size = {"x": size["x"] - (2.0 * wall), "y": size["y"] - (2.0 * wall), "z": size["z"] - floor}
        if min(cavity_size.values()) <= 0:
            qualifier = "demande" if exact else "automatique"
            raise FunctionalCadBuildError(
                f"Le bac vide {qualifier} {name!r} est trop petit pour conserver des parois de {wall:.2f} mm et un fond de {floor:.2f} mm."
            )
        cavity_id = f"{instance_id}:open-top-cavity"
        cavities = (
            CadCavity(
                id=cavity_id,
                functional_type="free",
                local_origin=Point3D(x=wall, y=wall, z=floor),
                size=_as_dimension(cavity_size),
                clearance_mm=0.0,
                clearance_source="p42_empty_fill_no_asset_fit_clearance",
                comment="Bac vide V0.1 ouvert par le dessus.",
                features=(),
                status=_FUSION_SMOKE_STATUS,
                fusion_generation=_FUSION_SMOKE_STATUS,
            ),
        )
    return _component(
        component_id=component_id,
        name=name,
        module_id=instance_id,
        instance_id=instance_id,
        functional_type=functional_type,
        body_id=body_id,
        origin=origin,
        size=size,
        cavities=cavities,
        metadata={**metadata, "fill_kind": fill_kind, "exact_requested": exact},
    )


def _component(
    *,
    component_id: str,
    name: str,
    module_id: str,
    instance_id: str,
    functional_type: str,
    body_id: str,
    origin: dict[str, float],
    size: dict[str, float],
    cavities: tuple[CadCavity, ...],
    metadata: dict[str, object],
) -> CadComponent:
    body = CadBody(
        id=body_id,
        name=name,
        kind="rectangular_blank",
        source_cell_instance_id=instance_id,
        theoretical_origin=_as_point(origin),
        theoretical_size=_as_dimension(size),
        printable_origin=_as_point(origin),
        printable_size=_as_dimension(size),
        cavities=cavities,
        face_classifications=(),
        applied_tolerances=(),
        operations=(
            CadOperation(
                id=f"{body_id}:create_rectangular_prism",
                kind="create_rectangular_prism",
                target_id=body_id,
                parameters={
                    "origin_source": "printable_origin_mm",
                    "size_source": "printable_size_mm",
                    "coordinate_frame": "scene.frame",
                },
            ),
            *tuple(_cavity_operation(body_id, cavity) for cavity in cavities),
        ),
    )
    return CadComponent(
        id=component_id,
        name=name,
        module_id=module_id,
        instance_id=instance_id,
        functional_type=functional_type,
        body=body,
        metadata=metadata,
    )


def _cavity_operation(body_id: str, cavity: CadCavity) -> CadOperation:
    return CadOperation(
        id=f"{body_id}:{cavity.id}:{CAVITY_OPERATION_KIND}",
        kind=CAVITY_OPERATION_KIND,
        target_id=body_id,
        parameters={
            "cavity_id": cavity.id,
            "functional_type": cavity.functional_type,
            "local_origin_mm": _point_dict(cavity.local_origin),
            "size_mm": _dimension_dict(cavity.size),
            "clearance_mm": cavity.clearance_mm,
            "clearance_source": cavity.clearance_source,
            "coordinate_frame": "body.local",
            "execution_status": _FUSION_SMOKE_STATUS,
            "fusion_generation": _FUSION_SMOKE_STATUS,
        },
    )


def _inset_automatic_region(region: dict[str, object], clearance: float) -> dict[str, dict[str, float]] | None:
    """Reserve the shared gap around an automatically proposed residual body.

    The placement solver's free cells include the physical gap itself.  A body
    built from the full cell would touch a neighbour or the original box.  The
    top of a declared upper-stack support is an intentional contact surface;
    the box bottom is likewise allowed to support a body directly.
    """

    origin = _dimension(region["origin_mm"])
    size = _dimension(region["size_mm"])
    support = str(region["classification"]) == "support_hollow_fill_candidate"
    inset = {"x": clearance, "y": clearance, "z": 0.0 if origin["z"] == 0.0 else clearance}
    size_after = {
        "x": size["x"] - 2.0 * clearance,
        "y": size["y"] - 2.0 * clearance,
        "z": size["z"] - inset["z"] - (0.0 if support else clearance),
    }
    if min(size_after.values()) <= 0:
        return None
    return {
        "origin_mm": {"x": _round(origin["x"] + inset["x"]), "y": _round(origin["y"] + inset["y"]), "z": _round(origin["z"] + inset["z"])},
        "size_mm": {axis: _round(value) for axis, value in size_after.items()},
        "clearance_inset_mm": {"x": _round(clearance), "y": _round(clearance), "z": _round(inset["z"])},
    }


def _rotate_xy(origin: dict[str, float], size: dict[str, float], original_outer: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    """Rotate a local cavity 90 degrees clockwise with its placed container."""

    return (
        {"x": _round(original_outer["y"] - (origin["y"] + size["y"])), "y": _round(origin["x"]), "z": _round(origin["z"])},
        {"x": _round(size["y"]), "y": _round(size["x"]), "z": _round(size["z"])},
    )


def _assert_cavity_fits(name: object, cavity_id: str, origin: dict[str, float], size: dict[str, float], body_size: dict[str, float], floor: float) -> None:
    if min(size.values()) <= 0 or origin["x"] < 0 or origin["y"] < 0 or origin["z"] < 0:
        raise FunctionalCadBuildError(f"Le logement {cavity_id!r} du bac {name!r} a des dimensions invalides.")
    if origin["x"] + size["x"] > body_size["x"] + 0.0001 or origin["y"] + size["y"] > body_size["y"] + 0.0001:
        raise FunctionalCadBuildError(f"Le logement {cavity_id!r} depasse les parois du bac {name!r}.")
    if size["z"] >= body_size["z"] or abs(body_size["z"] - size["z"] - floor) > 0.0001:
        raise FunctionalCadBuildError(f"Le logement {cavity_id!r} du bac {name!r} ne conserve pas le fond minimal.")


def _parameter(id: str, value: float, category: str, description: str) -> CadParameter:
    return CadParameter(id=id, value=_round(value), unit=CAD_IR_UNITS, category=category, description=description)


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError("Internal V0.1 value must be a mapping.")
    return value


def _values(value: object) -> list[object]:
    if not isinstance(value, list):
        raise TypeError("Internal V0.1 value must be a list.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _point(value: object) -> dict[str, float]:
    return _dimension(value)


def _as_point(value: dict[str, float]) -> Point3D:
    return Point3D(x=value["x"], y=value["y"], z=value["z"])


def _as_dimension(value: dict[str, float]) -> Dimension3D:
    return Dimension3D(x=value["x"], y=value["y"], z=value["z"])


def _point_dict(value: Point3D) -> dict[str, float]:
    return {"x": value.x, "y": value.y, "z": value.z}


def _dimension_dict(value: Dimension3D) -> dict[str, float]:
    return {"x": value.x, "y": value.y, "z": value.z}


def _round(value: float) -> float:
    return round(float(value), 4)
