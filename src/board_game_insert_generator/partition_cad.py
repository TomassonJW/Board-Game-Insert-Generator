"""P59 CAD IR materialization from the Fusion-only P57 partition plan."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
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
from board_game_insert_generator.partition_solver import PARTITION_PLAN_SCHEMA_V1, solve_partition_plan
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.top_inset_reservation import (
    TOP_INSET_CUT_KIND,
    TOP_INSET_GRIP_CUT_KIND,
    TOP_INSET_GRIP_OPERATION_KIND,
    TOP_INSET_OPERATION_KIND,
)


PARTITION_CAD_BUILD_SCHEMA_V1 = "bgig.partition_cad_build.v1"
PARTITION_CAD_STATUS_READY = "ready_for_fusion"
_EPSILON = 0.0001


class PartitionCadBuildError(ValueError):
    """Raised when a P64 plan cannot be materialized without changing it."""


@dataclass(frozen=True)
class _BuildResult:
    components: tuple[CadComponent, ...]
    blockers: tuple[str, ...]


def build_partition_cad(raw_project: object, *, partition: object | None = None) -> dict[str, object]:
    """Build CAD IR exclusively from a complete, materializable P64 plan."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    expected_plan = solve_partition_plan(project)
    plan = expected_plan if partition is None else _mapping(partition, "partition")
    if partition is not None and plan != expected_plan:
        raise PartitionCadBuildError("Le plan P64 fourni est obsolete ou ne correspond pas au projet courant.")
    if plan.get("schema_version") != PARTITION_PLAN_SCHEMA_V1:
        raise PartitionCadBuildError("P59 exige un plan bgig.partition_plan.v1.")
    summary = _mapping(plan.get("summary"), "partition.summary")
    base = {
        "schema_version": PARTITION_CAD_BUILD_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "source_plan_digest": str(plan.get("plan_digest", "")),
        "partition": plan,
    }
    if summary.get("status") != "constructed" or not bool(summary.get("materializable", False)):
        partial = summary.get("status") == "proposal_with_residuals"
        blockers = [
            str(item.get("message", "Partition impossible."))
            for item in _mappings(plan.get("diagnostics", []), "partition.diagnostics")
        ]
        if partial:
            blockers.insert(
                0,
                "La proposition contient des volumes residuels : confirme un corps explicite ou ajuste les contraintes avant de materialiser.",
            )
        return {
            **base,
            "status": "not_materializable" if partial else "impossible",
            "cad_ir": None,
            "cad_ir_digest": None,
            "materialization": {
                "status": "blocked_partial" if partial else "not_started",
                "component_count": 0,
                "automatic_body_count": 0,
            },
            "blockers": blockers,
        }
    if int(summary.get("automatic_body_count", -1)) != 0:
        raise PartitionCadBuildError("P59 refuse tout plan dont automatic_body_count n est pas zero.")

    build = _components(project, plan)
    if build.blockers:
        return {
            **base,
            "status": "impossible",
            "cad_ir": None,
            "cad_ir_digest": None,
            "materialization": {"status": "blocked", "component_count": 0, "automatic_body_count": 0},
            "blockers": list(build.blockers),
        }
    expected_count = int(summary["final_body_count"])
    if len(build.components) != expected_count:
        raise PartitionCadBuildError(
            f"P59 a produit {len(build.components)} composants mais le plan P64 en exige {expected_count}."
        )

    layout = _mapping(project["layout"], "project.layout")
    box = _mapping(project["box"], "project.box")
    box_size = _dimension(box["inner_dimensions_mm"], "project.box.inner_dimensions_mm")
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
            _parameter("layout_clearance_mm", float(layout["layout_clearance_mm"]), "clearance", "Jeu total X-Y entre conteneurs, conserve comme vide."),
            _parameter("container_box_xy_clearance_mm", float(layout["container_box_xy_clearance_mm"]), "clearance", "Jeu X-Y par cote entre un conteneur et la boite, conserve comme vide."),
            _parameter("container_z_clearance_mm", float(layout["container_z_clearance_mm"]), "clearance", "Jeu total Z entre conteneurs, conserve comme vide."),
            _parameter("box_top_z_clearance_mm", float(box["lid_clearance_mm"]), "clearance", "Jeu unique entre les conteneurs et le haut interieur de la boite."),
            _parameter("default_wall_thickness_mm", float(layout["default_wall_thickness_mm"]), "geometry_default", "Paroi minimale pour complement creux explicite."),
            _parameter("default_floor_thickness_mm", float(layout["default_floor_thickness_mm"]), "geometry_default", "Fond minimal pour complement creux explicite."),
        ),
        components=build.components,
        metadata=CadSceneMetadata(
            project_name=str(project["project_name"]),
            source_path=None,
            layout_strategy="p64_bounded_volumetric_stage_v1",
            print_profile="fusion_only_mvp_v0_1",
            warnings=(
                "CAD IR derivee du plan P64 ; Fusion ne doit recalculer aucun etage, placement, dimension ou cavite.",
                "Les jeux, la pile plate et les regions libres ne sont pas materialises.",
                "Fusion et impression restent non validees tant que les gates correspondantes ne sont pas observees.",
            ),
            box_fill_plan={
                "schema_version": plan["schema_version"],
                "plan_digest": plan.get("plan_digest"),
                "summary": summary,
                "support": plan.get("support"),
                "stages": plan.get("stages"),
                "stage_support": plan.get("stage_support"),
                "removal_sequence": plan.get("removal_sequence"),
                "residuals": plan.get("residuals"),
                "suggestions": plan.get("suggestions"),
                "score_breakdown": plan.get("score_breakdown"),
                "volume_conservation": plan.get("validation"),
                "top_inset_reservations": plan.get("top_inset_reservations"),
                "invariants": plan.get("invariants"),
                "free_regions_materialized": False,
                "automatic_body_count": 0,
            },
        ),
    )
    cad_ir = scene.to_dict()
    digest = hashlib.sha256(json.dumps(cad_ir, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    cavity_count = sum(len(component.body.cavities) for component in build.components)
    top_inset_cut_count = sum(
        1
        for component in build.components
        for operation in component.body.operations
        if operation.kind in {TOP_INSET_OPERATION_KIND, TOP_INSET_GRIP_OPERATION_KIND}
    )
    return {
        **base,
        "status": PARTITION_CAD_STATUS_READY,
        "cad_ir": cad_ir,
        "cad_ir_digest": digest,
        "materialization": {
            "status": PARTITION_CAD_STATUS_READY,
            "component_count": len(build.components),
            "container_component_count": sum(1 for item in build.components if item.functional_type == "v0_1_storage_container"),
            "explicit_complement_component_count": sum(1 for item in build.components if item.functional_type != "v0_1_storage_container"),
            "cavity_count": cavity_count,
            "top_inset_cut_count": top_inset_cut_count,
            "automatic_body_count": 0,
            "source_plan_digest": plan.get("plan_digest"),
        },
        "blockers": [],
        "invariants": {
            "source_plan_unchanged": True,
            "component_count_matches_plan": True,
            "cavities_from_p55_only": True,
            "top_insets_are_reservations_not_cavities": True,
            "top_inset_cut_count_matches_plan": top_inset_cut_count == len(_mappings(_mapping(plan.get("top_inset_reservations"), "partition.top_inset_reservations").get("cuts", []), "partition.top_inset_reservations.cuts")),
            "automatic_body_count": 0,
            "free_regions_materialized": False,
        },
        "limitations": [
            "P59 V0.1 materialise des prismes et cavites rectangulaires ouverts par le dessus.",
            "Les formes non rectangulaires utilisent leur enveloppe de cavite calibree V0.1.",
            "La construction de CAD IR ne vaut ni observation Fusion ni validation d impression.",
        ],
    }


def _components(project: dict[str, object], plan: dict[str, object]) -> _BuildResult:
    layout = _mapping(project["layout"], "project.layout")
    components: list[CadComponent] = []
    blockers: list[str] = []
    for index, value in enumerate(_mappings(plan["placements"], "partition.placements")):
        try:
            if value["role"] == "container":
                components.append(_container_component(value, index))
            elif value["role"] == "explicit_complement":
                components.append(_complement_component(value, layout, index))
            else:
                raise PartitionCadBuildError(f"Role de placement P59 inconnu : {value.get('role')!r}.")
        except PartitionCadBuildError as exc:
            blockers.append(str(exc))
    return _BuildResult(tuple(components), tuple(blockers))


def _container_component(placement: dict[str, object], index: int) -> CadComponent:
    body_size = _dimension(placement["world_size_mm"], f"placement[{index}].world_size_mm")
    body_origin = _dimension(placement["origin_mm"], f"placement[{index}].origin_mm")
    final_local = _dimension(placement["final_outer_dimensions_mm"], f"placement[{index}].final_outer_dimensions_mm")
    minimum_origin = _dimension(placement["minimum_envelope_origin_in_final_mm"], f"placement[{index}].minimum_envelope_origin_in_final_mm")
    rotation = int(placement.get("rotation_deg_z", 0))
    cavities: list[CadCavity] = []
    for cavity_index, cavity in enumerate(_mappings(placement.get("cavity_layout", []), f"placement[{index}].cavity_layout")):
        local_origin, local_size = _transformed_cavity(cavity, final_local, minimum_origin, rotation)
        cavity_id = str(cavity["cavity_id"])
        _assert_cavity(str(placement["name"]), cavity_id, local_origin, local_size, body_size)
        cavities.append(
            CadCavity(
                id=cavity_id,
                functional_type=str(cavity["shape_kind"]),
                local_origin=_as_point(local_origin),
                size=_as_dimension(local_size),
                clearance_mm=float(cavity["content_clearance_mm"]),
                clearance_source="bgig.project.v1 content_clearance_mm",
                comment=f"Cavite P55 calibree pour {cavity['content_id']}; ouverte par le dessus.",
                features=(),
                status=PARTITION_CAD_STATUS_READY,
                fusion_generation=PARTITION_CAD_STATUS_READY,
            )
        )
    return _component(
        placement=placement,
        index=index,
        functional_type="v0_1_storage_container",
        origin=body_origin,
        size=body_size,
        cavities=tuple(cavities),
        metadata={
            "source": "p64_partition_plan_v1",
            "role": "container",
            "container_group_id": placement["container_group_id"],
            "source_contents": placement.get("source_contents", []),
            "rotation_deg_z": rotation,
            "minimum_outer_envelope_mm": placement.get("minimum_outer_envelope_mm"),
            "final_outer_dimensions_mm": placement.get("final_outer_dimensions_mm"),
            "surplus_distribution_mm": placement.get("surplus_distribution_mm"),
            "automatic": False,
        },
    )


def _complement_component(placement: dict[str, object], layout: dict[str, object], index: int) -> CadComponent:
    size = _dimension(placement["world_size_mm"], f"placement[{index}].world_size_mm")
    origin = _dimension(placement["origin_mm"], f"placement[{index}].origin_mm")
    kind = str(placement.get("complement_kind", ""))
    if kind not in {"hollow", "solid", "separator"}:
        raise PartitionCadBuildError(f"Type de complement explicite inconnu : {kind!r}.")
    cavities: tuple[CadCavity, ...] = ()
    if kind == "hollow":
        wall = float(layout["default_wall_thickness_mm"])
        floor = float(layout["default_floor_thickness_mm"])
        cavity_size = {"x": size["x"] - 2.0 * wall, "y": size["y"] - 2.0 * wall, "z": size["z"] - floor}
        if min(cavity_size.values()) <= 0.0:
            raise PartitionCadBuildError(f"Le complement creux {placement['name']!r} est trop petit pour les parois et le fond minimaux.")
        cavities = (
            CadCavity(
                id=f"{placement['id']}:open-top-cavity",
                functional_type="free",
                local_origin=Point3D(x=wall, y=wall, z=floor),
                size=_as_dimension(cavity_size),
                clearance_mm=0.0,
                clearance_source="explicit_complement_exact_dimensions",
                comment="Complement creux explicitement demande ; ouvert par le dessus.",
                features=(), status=PARTITION_CAD_STATUS_READY, fusion_generation=PARTITION_CAD_STATUS_READY,
            ),
        )
    return _component(
        placement=placement,
        index=index,
        functional_type={"hollow": "v0_1_hollow_fill", "solid": "v0_1_solid_fill", "separator": "v0_1_separator"}[kind],
        origin=origin,
        size=size,
        cavities=cavities,
        metadata={
            "source": "p59_explicit_complement_v1", "role": "explicit_complement",
            "requested_complement_id": placement.get("requested_complement_id"),
            "complement_kind": kind, "automatic": False,
        },
    )


def _transformed_cavity(
    cavity: dict[str, object],
    final_local: dict[str, float],
    minimum_origin: dict[str, float],
    rotation: int,
) -> tuple[dict[str, float], dict[str, float]]:
    cavity_origin = _dimension(cavity["local_origin_mm"], "cavity.local_origin_mm")
    cavity_size = _dimension(cavity["inner_dimensions_mm"], "cavity.inner_dimensions_mm")
    local = {axis: minimum_origin[axis] + cavity_origin[axis] for axis in ("x", "y", "z")}
    # P55 keeps cavity dimensions fixed while P64 assigns the body within its stage.
    # Every storage cavity must therefore stay open on the final top face.
    local["z"] = final_local["z"] - cavity_size["z"]
    if rotation == 0:
        return _rounded(local), _rounded(cavity_size)
    if rotation == 90:
        return (
            {
                "x": _round(final_local["y"] - local["y"] - cavity_size["y"]),
                "y": _round(local["x"]),
                "z": _round(local["z"]),
            },
            {"x": _round(cavity_size["y"]), "y": _round(cavity_size["x"]), "z": _round(cavity_size["z"])},
        )
    raise PartitionCadBuildError(f"Rotation Z P59 non prise en charge : {rotation}.")


def _assert_cavity(name: str, cavity_id: str, origin: dict[str, float], size: dict[str, float], body: dict[str, float]) -> None:
    if min(size.values()) <= 0.0 or min(origin.values()) < -_EPSILON:
        raise PartitionCadBuildError(f"La cavite {cavity_id!r} du bac {name!r} a des dimensions invalides.")
    if any(origin[axis] + size[axis] > body[axis] + _EPSILON for axis in ("x", "y", "z")):
        raise PartitionCadBuildError(f"La cavite {cavity_id!r} depasse le corps {name!r}.")
    if abs(origin["z"] + size["z"] - body["z"]) > _EPSILON:
        raise PartitionCadBuildError(f"La cavite {cavity_id!r} du bac {name!r} n est pas ouverte sur la face superieure.")


def _component(
    *, placement: dict[str, object], index: int, functional_type: str,
    origin: dict[str, float], size: dict[str, float], cavities: tuple[CadCavity, ...],
    metadata: dict[str, object],
) -> CadComponent:
    instance_id = str(placement["id"])
    body_id = f"body:{instance_id}"
    name = str(placement["name"])
    body = CadBody(
        id=body_id,
        name=f"{name} - corps BGIG {index + 1}",
        kind="rectangular_blank",
        source_cell_instance_id=instance_id,
        theoretical_origin=_as_point(origin), theoretical_size=_as_dimension(size),
        printable_origin=_as_point(origin), printable_size=_as_dimension(size),
        cavities=cavities, face_classifications=(), applied_tolerances=(),
        operations=(
            CadOperation(
                id=f"{body_id}:create_rectangular_prism", kind="create_rectangular_prism", target_id=body_id,
                parameters={"origin_source": "printable_origin_mm", "size_source": "printable_size_mm", "coordinate_frame": "scene.frame"},
            ),
            *tuple(_cavity_operation(body_id, cavity) for cavity in cavities),
            *tuple(
                _top_inset_operation(body_id, cut)
                for cut in _mappings(placement.get("top_inset_cuts", []), f"placement[{index}].top_inset_cuts")
            ),
        ),
    )
    module_id = str(placement.get("container_group_id") or placement.get("requested_complement_id") or f"body-{index}")
    return CadComponent(
        id=f"component:{instance_id}", name=name, module_id=module_id, instance_id=instance_id,
        functional_type=functional_type, body=body, metadata=metadata,
    )


def _cavity_operation(body_id: str, cavity: CadCavity) -> CadOperation:
    return CadOperation(
        id=f"{body_id}:{cavity.id}:{CAVITY_OPERATION_KIND}", kind=CAVITY_OPERATION_KIND, target_id=body_id,
        parameters={
            "cavity_id": cavity.id, "functional_type": cavity.functional_type,
            "local_origin_mm": _point_dict(cavity.local_origin), "size_mm": _dimension_dict(cavity.size),
            "clearance_mm": cavity.clearance_mm, "clearance_source": cavity.clearance_source,
            "coordinate_frame": "body.local", "execution_status": PARTITION_CAD_STATUS_READY,
            "fusion_generation": PARTITION_CAD_STATUS_READY,
        },
    )



def _top_inset_operation(body_id: str, cut: dict[str, object]) -> CadOperation:
    cut_kind = str(cut.get("kind", ""))
    if cut_kind == TOP_INSET_CUT_KIND:
        operation_kind = TOP_INSET_OPERATION_KIND
    elif cut_kind == TOP_INSET_GRIP_CUT_KIND:
        operation_kind = TOP_INSET_GRIP_OPERATION_KIND
    else:
        raise PartitionCadBuildError(f"Type de coupe superieure inconnu : {cut_kind!r}.")
    return CadOperation(
        id=f"{body_id}:{cut['id']}:{operation_kind}",
        kind=operation_kind,
        target_id=body_id,
        parameters={
            "cut_id": cut["id"],
            "cut_kind": cut_kind,
            "reservation_id": cut["reservation_id"],
            "flat_item_id": cut["flat_item_id"],
            "removal_order": cut["removal_order"],
            "local_origin_mm": deepcopy(cut["local_origin_mm"]),
            "size_mm": deepcopy(cut["size_mm"]),
            "retained_body_below_mm": cut["retained_body_below_mm"],
            "minimum_floor_mm": cut["minimum_floor_mm"],
            "non_perforating": bool(cut["non_perforating"]),
            "coordinate_frame": "body.local",
            "execution_status": PARTITION_CAD_STATUS_READY,
            "fusion_generation": PARTITION_CAD_STATUS_READY,
        },
    )

def _parameter(identifier: str, value: float, category: str, description: str) -> CadParameter:
    return CadParameter(id=identifier, value=_round(value), unit=CAD_IR_UNITS, category=category, description=description)


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PartitionCadBuildError(f"{field} doit etre un objet.")
    return value


def _mappings(value: object, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PartitionCadBuildError(f"{field} doit etre une liste.")
    return [_mapping(item, f"{field}[{index}]") for index, item in enumerate(value)]


def _dimension(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value, field)
    try:
        return {axis: float(raw[axis]) for axis in ("x", "y", "z")}
    except (KeyError, TypeError, ValueError) as exc:
        raise PartitionCadBuildError(f"{field} doit contenir x, y et z numeriques.") from exc


def _as_point(value: dict[str, float]) -> Point3D:
    return Point3D(x=value["x"], y=value["y"], z=value["z"])


def _as_dimension(value: dict[str, float]) -> Dimension3D:
    return Dimension3D(x=value["x"], y=value["y"], z=value["z"])


def _point_dict(value: Point3D) -> dict[str, float]:
    return {"x": value.x, "y": value.y, "z": value.z}


def _dimension_dict(value: Dimension3D) -> dict[str, float]:
    return {"x": value.x, "y": value.y, "z": value.z}


def _rounded(value: dict[str, float]) -> dict[str, float]:
    return {axis: _round(value[axis]) for axis in ("x", "y", "z")}


def _round(value: float) -> float:
    return round(float(value), 4)
