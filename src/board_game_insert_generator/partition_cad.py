"""P59 CAD IR materialization from the Fusion-only P57 partition plan."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

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
from board_game_insert_generator.incremental_project_state import canonical_digest
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
SCENE_ARTIFACT_IDENTITY_SCHEMA_V1 = "bgig.scene_artifact_identity.v1"
ARTIFACT_KIND_MINIMAL = "minimal_layout"
ARTIFACT_KIND_FINALIZED = "finalized_plan"
COMPOSITE_PRISM_JOIN_OPERATION_KIND = "join_rectangular_prism"
COMPOSITE_BODY_SCHEMA_V1 = "bgig.xy_composite_cad_body.v1"
COMPOSITE_BODY_SCHEMA_V2 = "bgig.xy_composite_cad_body.v2"
COMPOSITE_BODY_SCHEMA_V3 = "bgig.xy_composite_container_body.v3"
_EPSILON = 0.0001


class PartitionCadBuildError(ValueError):
    """Raised when a P64 plan cannot be materialized without changing it."""


@dataclass(frozen=True)
class _BuildResult:
    components: tuple[CadComponent, ...]
    blockers: tuple[str, ...]


def build_partition_cad(
    raw_project: object,
    *,
    partition: object | None = None,
    solver_method: str | None = None,
    effort_profile: str = "normal",
    artifact_identity: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build CAD IR from one exact minimal or finalized P64 artifact.

    Calls without ``artifact_identity`` keep the historical certified-partition
    validation path. The staged Fusion palette always supplies an explicit
    identity and therefore never recomputes or silently transforms its source.
    """

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    if artifact_identity is None:
        expected_plan = solve_partition_plan(
            project,
            solver_method=solver_method,
            effort_profile=effort_profile,
        )
        plan = expected_plan if partition is None else _mapping(partition, "partition")
        if partition is not None and _plan_for_semantic_comparison(plan) != _plan_for_semantic_comparison(expected_plan):
            raise PartitionCadBuildError("Le plan P64 fourni est obsolete ou ne correspond pas au projet courant.")
        identity = None
    else:
        if partition is None:
            raise PartitionCadBuildError("Un artefact selectionne exige son plan P64 exact.")
        plan = _mapping(partition, "partition")
        identity = _normalize_artifact_identity(artifact_identity, plan)
    if plan.get("schema_version") != PARTITION_PLAN_SCHEMA_V1:
        raise PartitionCadBuildError("P59 exige un plan bgig.partition_plan.v1.")
    summary = _mapping(plan.get("summary"), "partition.summary")
    semantic_summary = deepcopy(summary)
    semantic_summary.pop("result_status", None)
    semantic_summary.pop("result_label", None)
    base = {
        "schema_version": PARTITION_CAD_BUILD_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "source_plan_digest": str(plan.get("plan_digest", "")),
        "artifact_kind": identity.get("artifact_kind") if identity else "legacy_partition",
        "artifact_identity": None,
        "partition": _plan_for_semantic_comparison(plan),
    }
    cad_eligible = (
        _selected_plan_is_cad_eligible(plan, identity)
        if identity is not None
        else summary.get("status") == "constructed" and bool(summary.get("materializable", False))
    )
    if not cad_eligible:
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
    if (
        identity is not None
        and identity.get("artifact_kind") == ARTIFACT_KIND_FINALIZED
    ):
        _assert_finalized_container_geometry_certificate(plan)

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
    expected_count = len(_mappings(plan.get("placements", []), "partition.placements")) if identity else int(summary["final_body_count"])
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
            layout_strategy=("p64_minimal_layout_v1" if identity and identity["artifact_kind"] == ARTIFACT_KIND_MINIMAL else "p64_bounded_volumetric_stage_v1"),
            print_profile="fusion_only_mvp_v0_1",
            warnings=(
                "CAD IR derivee du plan P64 ; Fusion ne doit recalculer aucun etage, placement, dimension ou cavite.",
                "Les jeux, la pile plate et les regions libres ne sont pas materialises.",
                "Fusion et impression restent non validees tant que les gates correspondantes ne sont pas observees.",
            ),
            box_fill_plan={
                "schema_version": plan["schema_version"],
                "plan_digest": plan.get("plan_digest"),
                "summary": semantic_summary,
                "support": plan.get("support"),
                "stages": plan.get("stages"),
                "stage_support": plan.get("stage_support"),
                "removal_sequence": plan.get("removal_sequence"),
                "residuals": plan.get("residuals"),
                "suggestions": plan.get("suggestions"),
                "score_breakdown": plan.get("score_breakdown"),
                "volume_conservation": plan.get("validation"),
                "top_inset_reservations": plan.get("top_inset_reservations"),
                "composite_materialization_certificate": (
                    _mapping(plan.get("finalization"), "partition.finalization").get(
                        "composite_materialization_certificate"
                    )
                    if isinstance(plan.get("finalization"), dict)
                    else None
                ),
                "finalized_container_geometry_certificate": (
                    _mapping(
                        plan.get("finalization"),
                        "partition.finalization",
                    ).get("finalized_container_geometry_certificate")
                    if isinstance(plan.get("finalization"), dict)
                    else None
                ),
                "invariants": plan.get("invariants"),
                "free_regions_materialized": False,
                "automatic_body_count": 0,
            },
        ),
    )
    cad_ir = scene.to_dict()
    if identity is not None:
        cad_ir["metadata"]["artifact_identity"] = deepcopy(identity)
    # The digest covers the complete CAD geometry and immutable source identity,
    # excluding only its own recursive ``cad_ir_digest`` field.
    digest = hashlib.sha256(json.dumps(cad_ir, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    full_identity = None
    if identity is not None:
        full_identity = {**identity, "cad_ir_digest": digest}
        cad_ir["metadata"]["artifact_identity"] = deepcopy(full_identity)
    cavity_count = sum(len(component.body.cavities) for component in build.components)
    top_inset_cut_count = sum(
        1
        for component in build.components
        for operation in component.body.operations
        if operation.kind in {TOP_INSET_OPERATION_KIND, TOP_INSET_GRIP_OPERATION_KIND}
    )
    composite_join_count = sum(
        1
        for component in build.components
        for operation in component.body.operations
        if operation.kind == COMPOSITE_PRISM_JOIN_OPERATION_KIND
    )
    composite_owner_count = sum(
        1
        for component in build.components
        if component.body.kind == "composite_rectangular_union"
    )
    return {
        **base,
        "status": PARTITION_CAD_STATUS_READY,
        "artifact_identity": full_identity,
        "cad_ir": cad_ir,
        "cad_ir_digest": digest,
        "materialization": {
            "status": PARTITION_CAD_STATUS_READY,
            "component_count": len(build.components),
            "container_component_count": sum(1 for item in build.components if item.functional_type == "v0_1_storage_container"),
            "explicit_complement_component_count": sum(1 for item in build.components if item.functional_type != "v0_1_storage_container"),
            "cavity_count": cavity_count,
            "top_inset_cut_count": top_inset_cut_count,
            "composite_owner_count": composite_owner_count,
            "joined_composite_prism_count": composite_join_count,
            "automatic_body_count": 0,
            "source_plan_digest": plan.get("plan_digest"),
            "artifact_kind": identity.get("artifact_kind") if identity else "legacy_partition",
        },
        "blockers": [],
        "invariants": {
            "source_plan_unchanged": True,
            "component_count_matches_plan": True,
            "cavities_from_p55_only": True,
            "top_insets_are_reservations_not_cavities": True,
            "top_inset_cut_count_matches_plan": top_inset_cut_count == len(_mappings(_mapping(plan.get("top_inset_reservations"), "partition.top_inset_reservations").get("cuts", []), "partition.top_inset_reservations.cuts")),
            "composite_owners_are_single_user_components": (
                composite_owner_count == 0
                or composite_owner_count == sum(
                    1
                    for item in _mappings(plan.get("placements", []), "partition.placements")
                    if isinstance(item.get("composite_body"), dict)
                )
            ),
            "composite_joins_precede_all_cuts": True,
            "automatic_body_count": 0,
            "free_regions_materialized": False,
            "selected_artifact_identity_exact": identity is None or full_identity is not None,
            "minimal_residual_distributed": False if identity and identity["artifact_kind"] == ARTIFACT_KIND_MINIMAL else None,
        },
        "limitations": [
            "P59 V0.1 materialise des prismes et cavites rectangulaires ouverts par le dessus.",
            "Les formes non rectangulaires utilisent leur enveloppe de cavite calibree V0.1.",
            "La construction de CAD IR ne vaut ni observation Fusion ni validation d impression.",
        ],
    }


def _normalize_artifact_identity(
    value: Mapping[str, object],
    plan: Mapping[str, object],
) -> dict[str, object]:
    artifact_kind = str(value.get("artifact_kind", ""))
    if artifact_kind not in {ARTIFACT_KIND_MINIMAL, ARTIFACT_KIND_FINALIZED}:
        raise PartitionCadBuildError(
            "artifact_kind doit etre minimal_layout ou finalized_plan."
        )
    artifact_digest = str(value.get("artifact_digest", ""))
    partition_plan_digest = str(value.get("partition_plan_digest", ""))
    source_revision = value.get("source_revision")
    if not artifact_digest:
        raise PartitionCadBuildError("L artefact selectionne exige un digest non vide.")
    if partition_plan_digest != str(plan.get("plan_digest", "")):
        raise PartitionCadBuildError(
            "Le digest du plan ne correspond pas a l artefact selectionne."
        )
    if not isinstance(source_revision, int) or isinstance(source_revision, bool) or source_revision < 0:
        raise PartitionCadBuildError("source_revision doit etre un entier positif ou nul.")
    return {
        "schema_version": SCENE_ARTIFACT_IDENTITY_SCHEMA_V1,
        "artifact_kind": artifact_kind,
        "artifact_digest": artifact_digest,
        "partition_plan_digest": partition_plan_digest,
        "source_revision": source_revision,
    }


def _selected_plan_is_cad_eligible(
    plan: dict[str, object],
    identity: Mapping[str, object],
) -> bool:
    summary = _mapping(plan.get("summary"), "partition.summary")
    if summary.get("status") != "constructed" or int(summary.get("automatic_body_count", -1)) != 0:
        return False
    if identity["artifact_kind"] == ARTIFACT_KIND_FINALIZED:
        finalization = plan.get("finalization")
        certificate = finalization.get("certificate") if isinstance(finalization, Mapping) else None
        return bool(
            summary.get("materializable") is True
            and isinstance(finalization, Mapping)
            and finalization.get("artifact_kind") == ARTIFACT_KIND_FINALIZED
            and isinstance(certificate, Mapping)
            and certificate.get("certified") is True
        )

    minimal = plan.get("minimal_layout")
    invariants = plan.get("invariants")
    solver = plan.get("solver")
    result = solver.get("result") if isinstance(solver, Mapping) else None
    certificate = minimal.get("global_certificate") if isinstance(minimal, Mapping) else None
    if not (
        summary.get("placement_certified") is True
        and isinstance(minimal, Mapping)
        and minimal.get("artifact_kind") == ARTIFACT_KIND_MINIMAL
        and minimal.get("finalization_applied") is False
        and isinstance(certificate, Mapping)
        and certificate.get("certified") is True
        and isinstance(result, Mapping)
        and result.get("status") == "solution_found"
        and isinstance(invariants, Mapping)
        and invariants.get("minimal_artifact_directly_materializable") is True
        and invariants.get("residual_distributed") is False
        and invariants.get("automatic_body_count") == 0
    ):
        return False
    placements = _mappings(plan.get("placements", []), "partition.placements")
    if not placements or any(
        value.get("role") not in {"container", "explicit_complement"}
        for value in placements
    ):
        return False
    for placement in placements:
        if placement.get("role") != "container":
            continue
        minimum = _dimension(
            placement.get("minimum_outer_envelope_mm"),
            "placement.minimum_outer_envelope_mm",
        )
        final = _dimension(
            placement.get("final_outer_dimensions_mm"),
            "placement.final_outer_dimensions_mm",
        )
        if any(
            abs(minimum[axis] - final[axis]) > _EPSILON
            for axis in ("x", "y")
        ):
            return False
        compensation = placement.get(
            "reservation_required_z_compensation_mm", 0.0
        )
        if (
            not isinstance(compensation, (int, float))
            or isinstance(compensation, bool)
            or float(compensation) < 0.0
            or abs(
                final["z"] - minimum["z"] - float(compensation)
            ) > _EPSILON
        ):
            return False
    return True


def _assert_finalized_container_geometry_certificate(
    plan: Mapping[str, object],
) -> None:
    finalization = _mapping(
        plan.get("finalization"),
        "partition.finalization",
    )
    certificate = _mapping(
        finalization.get("finalized_container_geometry_certificate"),
        "partition.finalization.finalized_container_geometry_certificate",
    )
    placements = _mappings(
        plan.get("placements", []),
        "partition.placements",
    )
    if (
        certificate.get("schema_version")
        != "bgig.finalized_container_geometry.v1"
        or certificate.get("certified") is not True
        or int(certificate.get("container_positive_body_count", -1))
        != len(placements)
        or int(certificate.get("flat_positive_body_count", -1)) != 0
        or int(certificate.get("flat_positive_union_count", -1)) != 0
        or abs(
            float(certificate.get("flat_positive_volume_mm3", -1.0))
        )
        > _EPSILON
        or int(
            certificate.get(
                "new_printable_body_count_attributed_to_flat_items",
                -1,
            )
        )
        != 0
        or certificate.get(
            "positive_geometry_frozen_before_flat_subtractions"
        )
        is not True
        or int(
            certificate.get(
                "ambiguous_cad_geometry_field_count",
                -1,
            )
        )
        != 0
        or not str(certificate.get("positive_geometry_digest", ""))
    ):
        raise PartitionCadBuildError(
            "Le certificat de geometrie positive des conteneurs "
            "finalises est absent ou invalide."
        )


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
    composite_body = (
        _mapping(
            placement["composite_body"],
            f"placement[{index}].composite_body",
        )
        if isinstance(placement.get("composite_body"), dict)
        else None
    )
    composite_uses_frozen_world_geometry = bool(
        composite_body is not None
        and composite_body.get("schema_version")
        in {
            COMPOSITE_BODY_SCHEMA_V2,
            COMPOSITE_BODY_SCHEMA_V3,
        }
    )
    frozen_contracts = (
        _mappings(
            placement.get("frozen_cavities_v1", []),
            f"placement[{index}].frozen_cavities_v1",
        )
        if isinstance(placement.get("frozen_cavities_v1"), list)
        else []
    )
    raw_cavities = _mappings(
        placement.get("cavity_layout", []),
        f"placement[{index}].cavity_layout",
    )
    if frozen_contracts and len(frozen_contracts) != len(raw_cavities):
        raise PartitionCadBuildError(
            f"Le nombre de cavites figees diverge pour {placement['id']!r}."
        )
    cavities: list[CadCavity] = []
    for cavity_index, cavity in enumerate(raw_cavities):
        if frozen_contracts:
            frozen = frozen_contracts[cavity_index]
            world_origin = _dimension(
                frozen["world_origin_mm"],
                f"placement[{index}].frozen_cavities_v1[{cavity_index}].world_origin_mm",
            )
            local_origin = {
                axis: _round(world_origin[axis] - body_origin[axis])
                for axis in ("x", "y", "z")
            }
            local_size = _dimension(
                frozen["world_size_mm"],
                f"placement[{index}].frozen_cavities_v1[{cavity_index}].world_size_mm",
            )
        else:
            local_origin, local_size = _transformed_cavity(
                cavity,
                final_local,
                minimum_origin,
                rotation,
            )
        cavity_id = str(cavity["cavity_id"])
        _assert_cavity(
            str(placement["name"]),
            cavity_id,
            local_origin,
            local_size,
            body_size,
            require_top_open=(
                not frozen_contracts
                or (
                    not composite_uses_frozen_world_geometry
                    and frozen_contracts[cavity_index].get(
                        "anchor_kind"
                    )
                    == "open_top"
                )
            ),
        )
        effective = cavity.get("clearance_effective_v1")
        values = _mapping(effective["values_mm"], "cavity.clearance_effective_v1.values_mm") if isinstance(effective, dict) else {"x": cavity["content_clearance_mm"], "y": cavity["content_clearance_mm"], "z": cavity["content_clearance_mm"]}
        sources = _mapping(effective["source_by_axis"], "cavity.clearance_effective_v1.source_by_axis") if isinstance(effective, dict) else {"x": "legacy_content_clearance_mm", "y": "legacy_content_clearance_mm", "z": "legacy_content_clearance_mm"}
        source_label = "asset_cavity x={x}, y={y}, z={z}".format(
            x=sources["x"], y=sources["y"], z=sources["z"]
        )
        cavities.append(
            CadCavity(
                id=cavity_id,
                functional_type=str(cavity["shape_kind"]),
                local_origin=_as_point(local_origin),
                size=_as_dimension(local_size),
                clearance_mm=float(values["z"]),
                clearance_source=f"bgig.project.v1 {source_label}",
                comment=(
                    f"Cavite P55 calibree pour {cavity['content_id']}; jeux effectifs "
                    f"X/Y/Z = {values['x']}/{values['y']}/{values['z']} mm; ouverte par le dessus."
                ),
                features=(),
                status=PARTITION_CAD_STATUS_READY,
                fusion_generation=PARTITION_CAD_STATUS_READY,
            )
        )
    if frozen_contracts:
        _validate_frozen_cavities(
            placement,
            body_origin,
            tuple(cavities),
            index,
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
            "final_cavity_anchors": bool(frozen_contracts),
            "automatic": False,
        },
        composite_body=composite_body,
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


def _assert_cavity(
    name: str,
    cavity_id: str,
    origin: dict[str, float],
    size: dict[str, float],
    body: dict[str, float],
    *,
    require_top_open: bool = True,
) -> None:
    if min(size.values()) <= 0.0 or min(origin.values()) < -_EPSILON:
        raise PartitionCadBuildError(f"La cavite {cavity_id!r} du bac {name!r} a des dimensions invalides.")
    if any(origin[axis] + size[axis] > body[axis] + _EPSILON for axis in ("x", "y", "z")):
        raise PartitionCadBuildError(f"La cavite {cavity_id!r} depasse le corps {name!r}.")
    if (
        require_top_open
        and abs(origin["z"] + size["z"] - body["z"]) > _EPSILON
    ):
        raise PartitionCadBuildError(f"La cavite {cavity_id!r} du bac {name!r} n est pas ouverte sur la face superieure.")


def _component(
    *, placement: dict[str, object], index: int, functional_type: str,
    origin: dict[str, float], size: dict[str, float], cavities: tuple[CadCavity, ...],
    metadata: dict[str, object], composite_body: dict[str, object] | None = None,
) -> CadComponent:
    instance_id = str(placement["id"])
    body_id = f"body:{instance_id}"
    name = str(placement["name"])
    body_kind = "rectangular_blank"
    frozen_cavity_anchors = bool(metadata.get("final_cavity_anchors"))
    anchor_contracts = (
        _mappings(
            placement.get("frozen_cavities_v1", []),
            f"placement[{index}].frozen_cavities_v1",
        )
        if frozen_cavity_anchors
        else []
    )
    create_parameters: dict[str, object] = {
        "origin_source": "printable_origin_mm",
        "size_source": "printable_size_mm",
        "coordinate_frame": "scene.frame",
    }
    join_operations: tuple[CadOperation, ...] = ()
    composite_schema = ""
    if composite_body is not None:
        composite_schema = str(composite_body.get("schema_version", ""))
        if composite_schema not in {
            COMPOSITE_BODY_SCHEMA_V1,
            COMPOSITE_BODY_SCHEMA_V2,
            COMPOSITE_BODY_SCHEMA_V3,
        }:
            raise PartitionCadBuildError(
                f"Schema composite inconnu pour {instance_id!r}."
            )
        if composite_body.get("certified") is not True:
            raise PartitionCadBuildError(
                f"Le corps composite {instance_id!r} n est pas certifie."
            )
        if composite_schema in {
            COMPOSITE_BODY_SCHEMA_V2,
            COMPOSITE_BODY_SCHEMA_V3,
        }:
            declared_digest = str(
                composite_body.get("geometry_digest", "")
            )
            digest_payload = {
                key: deepcopy(value)
                for key, value in composite_body.items()
                if key != "geometry_digest"
            }
            if (
                not declared_digest
                or declared_digest != canonical_digest(digest_payload)
            ):
                raise PartitionCadBuildError(
                    f"Le corps composite {instance_id!r} diverge de son certificat."
                )
        if composite_schema == COMPOSITE_BODY_SCHEMA_V3:
            raw_v3_prisms = composite_body.get("prisms", ())
            if (
                not isinstance(raw_v3_prisms, (list, tuple))
                or any(
                    isinstance(value, Mapping)
                    and (
                        "cad_origin_mm" in value
                        or "cad_size_mm" in value
                    )
                    for value in raw_v3_prisms
                )
            ):
                raise PartitionCadBuildError(
                    "Le corps finalise contient encore un champ CAD "
                    f"ambigu pour {instance_id!r}."
                )
            positive_geometry_digest = str(
                composite_body.get("positive_geometry_digest", "")
            )
            if (
                not positive_geometry_digest
                or positive_geometry_digest
                != canonical_digest(
                    _composite_positive_geometry_payload(composite_body)
                )
            ):
                raise PartitionCadBuildError(
                    "La geometrie positive du conteneur finalise "
                    f"{instance_id!r} diverge de son certificat."
                )
        prisms = _mappings(
            composite_body.get("prisms", []),
            f"placement[{index}].composite_body.prisms",
        )
        if not prisms or prisms[0].get("kind") != "core":
            raise PartitionCadBuildError(
                f"Le corps composite {instance_id!r} exige un coeur en premier."
            )
        core = prisms[0]
        executable_origin_key = (
            "final_origin_mm"
            if composite_schema == COMPOSITE_BODY_SCHEMA_V3
            else "cad_origin_mm"
        )
        executable_size_key = (
            "final_size_mm"
            if composite_schema == COMPOSITE_BODY_SCHEMA_V3
            else "cad_size_mm"
        )
        create_parameters = {
            "origin_mm": deepcopy(core[executable_origin_key]),
            "size_mm": deepcopy(core[executable_size_key]),
            "origin_source": (
                "finalized_container_core_prism"
                if composite_schema == COMPOSITE_BODY_SCHEMA_V3
                else "composite_core_prism"
            ),
            "size_source": (
                "finalized_container_core_prism"
                if composite_schema == COMPOSITE_BODY_SCHEMA_V3
                else "composite_core_prism"
            ),
            "core_prism_id": core["prism_id"],
            "coordinate_frame": "scene.frame",
        }
        if composite_schema == COMPOSITE_BODY_SCHEMA_V3:
            create_parameters.update(
                {
                    "geometry_role": "finalized_container",
                    "positive_geometry_source": (
                        "container_finalization"
                    ),
                    "positive_geometry_digest": composite_body[
                        "positive_geometry_digest"
                    ],
                }
            )
        join_operations = _composite_join_operations(
            body_id,
            composite_body,
            prisms,
        )
        body_kind = "composite_rectangular_union"
        metadata = {
            **metadata,
            "composite_body_schema": composite_schema,
            "composite_owner_id": composite_body.get("owner_id"),
            "composite_core_prism_id": composite_body.get("core_prism_id"),
            "composite_prism_count": len(prisms),
            "composite_annex_count": max(0, len(prisms) - 1),
            "one_user_component_for_composite_owner": True,
        }
    body = CadBody(
        id=body_id,
        name=f"{name} - corps BGIG {index + 1}",
        kind=body_kind,
        source_cell_instance_id=instance_id,
        theoretical_origin=_as_point(origin), theoretical_size=_as_dimension(size),
        printable_origin=_as_point(origin), printable_size=_as_dimension(size),
        cavities=cavities, face_classifications=(), applied_tolerances=(),
        operations=(
            CadOperation(
                id=f"{body_id}:create_rectangular_prism",
                kind="create_rectangular_prism",
                target_id=body_id,
                parameters=create_parameters,
            ),
            *join_operations,
            *tuple(
                _cavity_operation(
                    body_id,
                    cavity,
                    frozen_world_pose=(
                        composite_schema == COMPOSITE_BODY_SCHEMA_V2
                        or composite_schema == COMPOSITE_BODY_SCHEMA_V3
                        or frozen_cavity_anchors
                    ),
                    frozen_contract=(
                        anchor_contracts[cavity_index]
                        if cavity_index < len(anchor_contracts)
                        else None
                    ),
                )
                for cavity_index, cavity in enumerate(cavities)
            ),
            *tuple(
                _frozen_cavity_access_operation(body_id, cut)
                for cut in _mappings(
                    (
                        composite_body.get("frozen_cavity_access_cuts", [])
                        if composite_body is not None
                        else []
                    ),
                    f"placement[{index}].composite_body.frozen_cavity_access_cuts",
                )
            ),
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


def _composite_positive_geometry_payload(
    composite_body: Mapping[str, object],
) -> dict[str, object]:
    raw_prisms = composite_body.get("prisms", ())
    prisms = (
        tuple(
            value
            for value in raw_prisms
            if isinstance(value, Mapping)
        )
        if isinstance(raw_prisms, (list, tuple))
        else ()
    )
    return {
        "schema_version": COMPOSITE_BODY_SCHEMA_V3,
        "owner_id": str(composite_body.get("owner_id", "")),
        "geometry_role": str(
            composite_body.get("geometry_role", "")
        ),
        "positive_geometry_source": str(
            composite_body.get("positive_geometry_source", "")
        ),
        "core_prism_id": str(
            composite_body.get("core_prism_id", "")
        ),
        "prisms": [
            {
                key: deepcopy(prism.get(key))
                for key in (
                    "prism_id",
                    "owner_id",
                    "kind",
                    "geometry_role",
                    "positive_geometry_source",
                    "closure_origin_mm",
                    "closure_size_mm",
                    "final_origin_mm",
                    "final_size_mm",
                    "local_origin_from_core_mm",
                    "attached_to_prism_id",
                    "attachment_axis",
                )
            }
            for prism in prisms
        ],
    }


def _composite_join_operations(
    body_id: str,
    composite_body: dict[str, object],
    prisms: list[dict[str, Any]],
) -> tuple[CadOperation, ...]:
    core_prism_id = str(composite_body.get("core_prism_id", ""))
    if str(prisms[0].get("prism_id", "")) != core_prism_id:
        raise PartitionCadBuildError("Le premier prisme composite ne correspond pas au coeur.")
    resolved = {core_prism_id}
    operations: list[CadOperation] = []
    policy = str(composite_body.get("policy", ""))
    if policy not in {
        "bounded_xy_composite_v1",
        "hybrid_xy_composite_v2",
        "finalized_container_union_v3",
    }:
        raise PartitionCadBuildError(
            f"Politique composite inconnue : {policy!r}."
        )
    for prism in prisms[1:]:
        prism_id = str(prism.get("prism_id", ""))
        parent_id = str(prism.get("attached_to_prism_id", ""))
        axis = str(prism.get("attachment_axis", ""))
        if not prism_id or parent_id not in resolved or axis not in {"x", "y"}:
            raise PartitionCadBuildError(
                f"Ordre ou attache composite invalide pour {prism_id!r}."
            )
        operations.append(
            CadOperation(
                id=f"{body_id}:{prism_id}:{COMPOSITE_PRISM_JOIN_OPERATION_KIND}",
                kind=COMPOSITE_PRISM_JOIN_OPERATION_KIND,
                target_id=body_id,
                parameters={
                    "mechanism_policy": policy,
                    "prism_id": prism_id,
                    "core_prism_id": core_prism_id,
                    "attached_to_prism_id": parent_id,
                    "attachment_axis": axis,
                    "local_origin_mm": deepcopy(prism["local_origin_from_core_mm"]),
                    "size_mm": deepcopy(
                        prism[
                            "final_size_mm"
                            if policy == "finalized_container_union_v3"
                            else "cad_size_mm"
                        ]
                    ),
                    "final_size_mm": deepcopy(prism["final_size_mm"]),
                    **(
                        {
                            "closure_size_mm": deepcopy(
                                prism["closure_size_mm"]
                            ),
                            "geometry_role": "finalized_container",
                            "positive_geometry_source": (
                                "container_finalization"
                            ),
                        }
                        if policy == "finalized_container_union_v3"
                        else {}
                    ),
                    "coordinate_frame": "body.local",
                    "execution_status": PARTITION_CAD_STATUS_READY,
                    "fusion_generation": PARTITION_CAD_STATUS_READY,
                },
            )
        )
        resolved.add(prism_id)
    return tuple(operations)


def _validate_frozen_cavities(
    placement: dict[str, object],
    body_origin: dict[str, float],
    cavities: tuple[CadCavity, ...],
    index: int,
) -> None:
    raw_contracts = _mappings(
        placement.get("frozen_cavities_v1", []),
        f"placement[{index}].frozen_cavities_v1",
    )
    composite_body = (
        _mapping(
            placement["composite_body"],
            f"placement[{index}].composite_body",
        )
        if isinstance(placement.get("composite_body"), dict)
        else None
    )
    declared_pose_digests = (
        [
            str(value)
            for value in composite_body.get(
                "frozen_cavity_pose_digests",
                [],
            )
        ]
        if composite_body is not None
        else [str(value.get("pose_digest", "")) for value in raw_contracts]
    )
    if len(raw_contracts) != len(cavities):
        raise PartitionCadBuildError(
            f"Le nombre de cavites figees diverge pour {placement['id']!r}."
        )
    if len(declared_pose_digests) != len(raw_contracts):
        raise PartitionCadBuildError(
            f"Le certificat des cavites figees diverge pour {placement['id']!r}."
        )
    for cavity_index, (contract, cavity) in enumerate(
        zip(raw_contracts, cavities)
    ):
        if int(contract.get("cavity_index", -1)) != cavity_index:
            raise PartitionCadBuildError(
                f"L identite de cavite figee diverge pour {placement['id']!r}."
            )
        expected_origin = _dimension(
            contract["world_origin_mm"],
            f"placement[{index}].frozen_cavities_v1[{cavity_index}].world_origin_mm",
        )
        expected_size = _dimension(
            contract["world_size_mm"],
            f"placement[{index}].frozen_cavities_v1[{cavity_index}].world_size_mm",
        )
        source_origin = _dimension(
            contract["source_owner_origin_mm"],
            (
                f"placement[{index}].frozen_cavities_v1"
                f"[{cavity_index}].source_owner_origin_mm"
            ),
        )
        source_size = _dimension(
            contract["source_owner_world_size_mm"],
            (
                f"placement[{index}].frozen_cavities_v1"
                f"[{cavity_index}].source_owner_world_size_mm"
            ),
        )
        identity = {
            "owner_id": str(contract.get("owner_id", "")),
            "cavity_index": cavity_index,
            "world_origin_mm": _rounded(expected_origin),
            "world_size_mm": _rounded(expected_size),
            "source_owner_origin_mm": _rounded(source_origin),
            "source_owner_world_size_mm": _rounded(source_size),
            "source_rotation_deg_z": int(
                contract.get("source_rotation_deg_z", -1)
            ),
        }
        if "anchor_kind" in contract:
            for key in (
                "minimum_world_origin_mm",
                "minimum_world_size_mm",
                "final_owner_origin_mm",
                "final_owner_world_size_mm",
            ):
                identity[key] = _rounded(
                    _dimension(
                        contract[key],
                        (
                            f"placement[{index}].frozen_cavities_v1"
                            f"[{cavity_index}].{key}"
                        ),
                    )
                )
            identity.update(
                {
                    key: contract[key]
                    for key in (
                        "anchor_kind",
                        "responsible_reservation_id",
                        "responsible_local_region_id",
                        "calibrated_depth_source_mm",
                        "calibrated_depth_final_mm",
                        "retained_floor_mm",
                        "minimum_floor_mm",
                        "top_separation_mm",
                        "minimum_top_separation_mm",
                        "intermediate_material_thickness_mm",
                        "top_interface_kind",
                        "top_void_continuity_certified",
                        "functional_top_z_mm",
                        "functional_top_access_certified",
                    )
                }
            )
        pose_digest = str(contract.get("pose_digest", ""))
        if (
            identity["owner_id"] != str(placement["id"])
            or pose_digest != canonical_digest(identity)
            or pose_digest != declared_pose_digests[cavity_index]
        ):
            raise PartitionCadBuildError(
                f"L empreinte de cavite figee diverge pour {placement['id']!r}."
            )
        actual_origin = {
            "x": body_origin["x"] + cavity.local_origin.x,
            "y": body_origin["y"] + cavity.local_origin.y,
            "z": body_origin["z"] + cavity.local_origin.z,
        }
        actual_size = _dimension_dict(cavity.size)
        if any(
            abs(actual_origin[axis] - expected_origin[axis]) > _EPSILON
            or abs(actual_size[axis] - expected_size[axis]) > _EPSILON
            for axis in ("x", "y", "z")
        ):
            raise PartitionCadBuildError(
                f"La pose monde de la cavite figee {cavity.id!r} diverge."
            )
        anchor_kind = str(contract.get("anchor_kind", "open_top"))
        if anchor_kind not in {"open_top", "below_top_inset"}:
            raise PartitionCadBuildError(
                f"L ancrage final de la cavite {cavity.id!r} est inconnu."
            )
        if (
            anchor_kind == "open_top"
            and contract.get("top_open") is not True
        ):
            raise PartitionCadBuildError(
                f"La cavite figee {cavity.id!r} n est pas ouverte."
            )
        if anchor_kind == "open_top":
            actual_top = expected_origin["z"] + expected_size["z"]
            if (
                contract.get("functional_top_access_certified")
                is not True
                or abs(
                    actual_top
                    - float(
                        contract.get("functional_top_z_mm", -1.0)
                    )
                )
                > _EPSILON
            ):
                raise PartitionCadBuildError(
                    f"L ouverture fonctionnelle de {cavity.id!r} diverge."
                )
        if (
            anchor_kind == "below_top_inset"
            and (
                float(contract.get("top_separation_mm", -1.0))
                + _EPSILON
                < float(
                    contract.get(
                        "minimum_top_separation_mm",
                        0.0,
                    )
                )
            )
        ):
            raise PartitionCadBuildError(
                f"La separation superieure de {cavity.id!r} est insuffisante."
            )
        if (
            anchor_kind == "below_top_inset"
            and (
                abs(
                    float(
                        contract.get(
                            "intermediate_material_thickness_mm",
                            -1.0,
                        )
                    )
                )
                > _EPSILON
                or abs(
                    float(contract.get("top_separation_mm", -1.0))
                )
                > _EPSILON
                or contract.get("top_interface_kind")
                != "direct_void_to_removable_top_inset"
                or contract.get("top_void_continuity_certified")
                is not True
            )
        ):
            raise PartitionCadBuildError(
                f"La cavite figee {cavity.id!r} est fermee sous son plateau."
            )

def _cavity_operation(
    body_id: str,
    cavity: CadCavity,
    *,
    frozen_world_pose: bool = False,
    frozen_contract: dict[str, object] | None = None,
) -> CadOperation:
    parameters = {
        "cavity_id": cavity.id,
        "functional_type": cavity.functional_type,
        "local_origin_mm": _point_dict(cavity.local_origin),
        "size_mm": _dimension_dict(cavity.size),
        "clearance_mm": cavity.clearance_mm,
        "clearance_source": cavity.clearance_source,
        "coordinate_frame": "body.local",
        "execution_status": PARTITION_CAD_STATUS_READY,
        "fusion_generation": PARTITION_CAD_STATUS_READY,
    }
    if frozen_world_pose:
        parameters.update(
            {
                "cavity_source": "frozen_content_cavity",
                "cut_plane_local_z_mm": _round(
                    cavity.local_origin.z + cavity.size.z
                ),
            }
        )
    if frozen_contract is not None:
        parameters.update(
            {
                "anchor_kind": frozen_contract.get(
                    "anchor_kind",
                    "open_top",
                ),
                "calibrated_depth_source_mm": frozen_contract.get(
                    "calibrated_depth_source_mm",
                    cavity.size.z,
                ),
                "calibrated_depth_final_mm": frozen_contract.get(
                    "calibrated_depth_final_mm",
                    cavity.size.z,
                ),
                "top_separation_mm": frozen_contract.get(
                    "top_separation_mm",
                    0.0,
                ),
                "intermediate_material_thickness_mm": frozen_contract.get(
                    "intermediate_material_thickness_mm",
                    0.0,
                ),
                "top_interface_kind": frozen_contract.get(
                    "top_interface_kind",
                    "open_functional_face",
                ),
                "top_void_continuity_certified": frozen_contract.get(
                    "top_void_continuity_certified",
                    False,
                ),
                "functional_top_z_mm": frozen_contract.get(
                    "functional_top_z_mm",
                ),
                "functional_top_access_certified": frozen_contract.get(
                    "functional_top_access_certified",
                    False,
                ),
                "responsible_reservation_id": frozen_contract.get(
                    "responsible_reservation_id",
                    "",
                ),
                "responsible_local_region_id": frozen_contract.get(
                    "responsible_local_region_id",
                    "",
                ),
            }
        )
    return CadOperation(
        id=f"{body_id}:{cavity.id}:{CAVITY_OPERATION_KIND}",
        kind=CAVITY_OPERATION_KIND,
        target_id=body_id,
        parameters=parameters,
    )


def _frozen_cavity_access_operation(
    body_id: str,
    cut: dict[str, object],
) -> CadOperation:
    if cut.get("kind") != "frozen_cavity_access":
        raise PartitionCadBuildError(
            "Type de coupe d acces de cavite composite inconnu."
        )
    return CadOperation(
        id=f"{body_id}:{cut['id']}:{CAVITY_OPERATION_KIND}",
        kind=CAVITY_OPERATION_KIND,
        target_id=body_id,
        parameters={
            "cavity_id": cut["reservation_id"],
            "functional_type": "frozen_cavity_vertical_access",
            "local_origin_mm": deepcopy(cut["local_origin_mm"]),
            "size_mm": deepcopy(cut["size_mm"]),
            "clearance_mm": 0.0,
            "clearance_source": "frozen_cavity_world_pose_v1",
            "cavity_source": "frozen_cavity_vertical_access",
            "cut_plane_local_z_mm": _round(
                float(cut["local_origin_mm"]["z"])
                + float(cut["size_mm"]["z"])
            ),
            "coordinate_frame": "body.local",
            "execution_status": PARTITION_CAD_STATUS_READY,
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
            "local_region_id": cut.get("local_region_id", ""),
            "overlapping_reservation_ids": deepcopy(
                cut.get("overlapping_reservation_ids", [])
            ),
            "local_interval_z_mm": deepcopy(
                cut.get("local_interval_z_mm")
            ),
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


def _plan_for_semantic_comparison(plan: dict[str, object]) -> dict[str, object]:
    """Ignore additive H04 observability when guarding a materializable plan."""

    canonical = deepcopy(plan)
    canonical.pop("plan_digest", None)
    source = canonical.get("source")
    if isinstance(source, dict):
        source.pop("migrated", None)
    summary = canonical.get("summary")
    if isinstance(summary, dict):
        summary.pop("result_status", None)
        summary.pop("result_label", None)
    solver = canonical.get("solver")
    if isinstance(solver, dict):
        solver.pop("result", None)
        solver.pop("telemetry", None)
    return canonical


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
