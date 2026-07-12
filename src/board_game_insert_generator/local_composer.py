"""Loopback adapter for the P23 local BGIG composer.

This module is intentionally an adapter: it converts a versioned UI draft into
existing pure-engine contracts.  It never makes Fusion the source of truth and
never exposes the service beyond local loopback addresses.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import math
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from board_game_insert_generator.appearance import AppearanceError, default_appearance, normalize_appearance
from board_game_insert_generator.mechanism import (
    RAIL_JOIN_OPERATION_KIND,
    MechanismError,
    default_mechanism,
    normalize_mechanism,
    sliding_lid_coupon_geometry,
    sliding_lid_readiness,
)
from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.project_v1 import (
    PROJECT_SCHEMA_V1,
    ProjectContractError,
    blank_project_v1,
    normalize_project_draft,
)

from board_game_insert_generator.box_fill_solver import BoxFillCandidate, BoxFillSolveRequest
from board_game_insert_generator.box_fill_variants import (
    BoxFillVariantRequest,
    SUPPORTED_POLICY_IDS,
    generate_box_fill_variants,
    select_box_fill_variant,
    selected_variant_to_dict,
    standard_preference_profile,
    variant_portfolio_to_dict,
)
from board_game_insert_generator.cad_ir import (
    CAVITY_OPERATION_KIND,
    CadBody,
    CadCavity,
    CadComponent,
    CadOperation,
    build_blank_cad_scene,
)
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.models import (
    BOX_FILL_PLAN_SCHEMA_V0,
    Asset,
    AssetAllocation,
    AssetKind,
    AssetQuantity,
    AssetStorageOrientation,
    BoxFillBox,
    BoxFillLayer,
    BoxFillModule,
    BoxFillPlan,
    BoxFillReservation,
    BoxFillReservationKind,
    BoxSpec,
    ContainmentIntent,
    Dimension3D,
    DimensionConfidence,
    GeometryDefaults,
    FunctionalType,
    InsertConfig,
    LayoutSettings,
    Point3D,
    ToleranceProfile,
)


LOCAL_COMPOSER_SCHEMA_V0 = "bgig.local_composer.v0"
LOCAL_COMPOSER_EXPORT_SCHEMA_V0 = "bgig.local_composer_export.v0"
MAX_REQUEST_BYTES = 1_000_000
LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
CORS_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}


class LocalComposerError(ValueError):
    """Raised when a local composer draft cannot be converted safely."""


def starter_draft() -> dict[str, object]:
    """Return a useful local-only starter project with honest defaults."""

    return {
        "schema_version": LOCAL_COMPOSER_SCHEMA_V0,
        "project_name": "Mon premier insert",
        "box": {
            "inner_dimensions_mm": {"x": 240.0, "y": 160.0, "z": 60.0},
            "usable_height_mm": 56.0,
            "lid_clearance_mm": 2.0,
        },
        "assets": [
            _starter_asset("cards", "Cartes", "cards", 120, 64.0, 89.0, 24.0, "protect"),
            _starter_asset("tokens", "Jetons", "tokens", 80, 18.0, 18.0, 5.0, "store"),
            _starter_asset("dice", "Des", "dice", 10, 16.0, 16.0, 16.0, "store"),
        ],
        "layers": [
            {"id": "base", "origin_z_mm": 0.0, "height_mm": 36.0, "role": "storage"},
            {"id": "top", "origin_z_mm": 36.0, "height_mm": 20.0, "role": "rulebook"},
        ],
        "reservations": [
            {
                "id": "rulebook",
                "kind": "rulebook",
                "origin_mm": {"x": 0.0, "y": 0.0, "z": 36.0},
                "size_mm": {"x": 240.0, "y": 160.0, "z": 18.0},
                "layer_id": "top",
            }
        ],
        "manual_modules": [],
        "candidates": [
            _starter_candidate("card-tray", "Bac cartes", 72.0, 102.0, 30.0, "base", ["cards"]),
            _starter_candidate("token-tray", "Bac jetons", 62.0, 54.0, 22.0, "base", ["tokens"]),
            _starter_candidate("dice-tray", "Bac des", 48.0, 48.0, 24.0, "base", ["dice"]),
        ],
        "preference": "balanced",
        "appearance": default_appearance(),
        "mechanism": default_mechanism(),
    }


def starter_catalog() -> list[dict[str, object]]:
    """Return bounded local-only project starters; no remote library is involved."""

    mixed = starter_draft()
    card_game = {
        "schema_version": LOCAL_COMPOSER_SCHEMA_V0,
        "project_name": "Mon jeu de cartes",
        "box": {
            "inner_dimensions_mm": {"x": 190.0, "y": 130.0, "z": 55.0},
            "usable_height_mm": 51.0,
            "lid_clearance_mm": 2.0,
        },
        "assets": [
            _starter_asset("cards", "Cartes", "cards", 110, 64.0, 89.0, 24.0, "protect"),
            _starter_asset("tokens", "Marqueurs", "tokens", 40, 18.0, 18.0, 5.0, "store"),
        ],
        "layers": [{"id": "base", "origin_z_mm": 0.0, "height_mm": 51.0, "role": "storage"}],
        "reservations": [],
        "manual_modules": [],
        "candidates": [
            _starter_candidate("card-tray", "Bac cartes", 76.0, 100.0, 30.0, "base", ["cards"]),
            _starter_candidate("token-tray", "Bac marqueurs", 60.0, 50.0, 20.0, "base", ["tokens"]),
        ],
        "preference": "accessible",
        "appearance": default_appearance(),
        "mechanism": default_mechanism(),
    }
    board_game = {
        "schema_version": LOCAL_COMPOSER_SCHEMA_V0,
        "project_name": "Ma boite avec plateau",
        "box": {
            "inner_dimensions_mm": {"x": 280.0, "y": 200.0, "z": 70.0},
            "usable_height_mm": 66.0,
            "lid_clearance_mm": 2.0,
        },
        "assets": [
            _starter_asset("cards", "Cartes", "cards", 90, 64.0, 89.0, 22.0, "protect"),
            _starter_asset("tokens", "Jetons", "tokens", 100, 18.0, 18.0, 5.0, "store"),
            _starter_asset("dice", "Des", "dice", 12, 16.0, 16.0, 16.0, "store"),
        ],
        "layers": [
            {"id": "base", "origin_z_mm": 0.0, "height_mm": 42.0, "role": "storage"},
            {"id": "top", "origin_z_mm": 42.0, "height_mm": 24.0, "role": "board"},
        ],
        "reservations": [
            {
                "id": "board",
                "kind": "board",
                "origin_mm": {"x": 0.0, "y": 0.0, "z": 42.0},
                "size_mm": {"x": 280.0, "y": 200.0, "z": 20.0},
                "layer_id": "top",
            }
        ],
        "manual_modules": [],
        "candidates": [
            _starter_candidate("card-tray", "Bac cartes", 80.0, 110.0, 30.0, "base", ["cards"]),
            _starter_candidate("token-tray", "Bac jetons", 70.0, 70.0, 24.0, "base", ["tokens"]),
            _starter_candidate("dice-tray", "Bac des", 55.0, 55.0, 24.0, "base", ["dice"]),
        ],
        "preference": "balanced",
        "appearance": default_appearance(),
        "mechanism": default_mechanism(),
    }
    return [
        {
            "id": "mixed-box",
            "title": "Boite mixte",
            "description": "Cartes, jetons, des et livret dans une boite classique.",
            "highlights": ["Cartes", "Jetons", "Livret"],
            "draft": mixed,
        },
        {
            "id": "card-game",
            "title": "Jeu de cartes",
            "description": "Un point de depart compact pour un deck et ses marqueurs.",
            "highlights": ["Cartes", "Petit volume", "Sans reservation"],
            "draft": card_game,
        },
        {
            "id": "board-game",
            "title": "Plateau et accessoires",
            "description": "Une grande boite avec plateau protege et bacs de base.",
            "highlights": ["Plateau", "Cartes", "Des"],
            "draft": board_game,
        },
    ]

def starter_project_v1() -> dict[str, object]:
    """Return the blank user-first project consumed by the V0.1 Studio."""

    return blank_project_v1()


def normalize_project_v1(raw_project: object) -> dict[str, object]:
    """Validate a V0.1 project or migrate a legacy Studio project without I/O."""

    try:
        return normalize_project_draft(raw_project).to_dict()
    except ProjectContractError as exc:
        raise LocalComposerError(str(exc)) from exc


def derive_containers_v1(raw_project: object) -> dict[str, object]:
    """Return the P39 container plan for a V1 or migratable legacy project."""

    try:
        return derive_container_plan(raw_project)
    except ProjectContractError as exc:
        raise LocalComposerError(str(exc)) from exc


def portfolio_from_draft(raw_draft: object) -> dict[str, object]:
    """Build P21 output from a UI draft without mutating it or writing files."""

    config, candidates, preference, policies = _draft_to_engine(raw_draft)
    assert config.box_fill_plan is not None
    portfolio = generate_box_fill_variants(
        BoxFillVariantRequest(
            solve_request=BoxFillSolveRequest(config.box_fill_plan, candidates),
            preference=standard_preference_profile(preference),
            policies=policies,
        )
    )
    return variant_portfolio_to_dict(portfolio)


def export_from_draft(raw_draft: object, variant_id: str | None = None) -> dict[str, object]:
    """Export one explicit P21 selection as Fusion-consumable CAD IR, without Fusion execution."""

    config, candidates, preference, policies = _draft_to_engine(raw_draft)
    assert config.box_fill_plan is not None
    portfolio = generate_box_fill_variants(
        BoxFillVariantRequest(
            solve_request=BoxFillSolveRequest(config.box_fill_plan, candidates),
            preference=standard_preference_profile(preference),
            policies=policies,
        )
    )
    portfolio_payload = variant_portfolio_to_dict(portfolio)
    selected_variant = select_box_fill_variant(portfolio, variant_id)
    selection = selected_variant_to_dict(portfolio, variant_id)
    appearance = config.box_fill_plan.metadata["appearance"]
    mechanism = config.box_fill_plan.metadata["mechanism"]
    selection["appearance"] = appearance
    selection["mechanism"] = mechanism
    mechanism_readiness = [
        sliding_lid_readiness(
            module.id,
            {"x": module.size.x, "y": module.size.y, "z": module.size.z},
            mechanism,
        )
        for module in selected_variant.result.solved_plan.modules
        if module.printable
    ]
    scene_config = replace(config, box_fill_plan=selected_variant.result.solved_plan)
    scene = build_blank_cad_scene(scene_config, generate_basic_layout(scene_config)).to_dict()
    components, mechanism_coupon = _selection_bridge_components(
        selected_variant.result.solved_plan,
        selected_variant.id,
        config.defaults,
        mechanism,
        config.box.inner_dimensions,
    )
    scene["components"] = components
    scene["metadata"]["box_fill_variant_portfolio"] = portfolio_payload
    scene["metadata"]["box_fill_variant_selection"] = selection
    scene["metadata"]["box_fill_solution"] = selection["variant"]["solution"]
    scene["metadata"]["appearance"] = appearance
    scene["metadata"]["mechanism"] = mechanism
    scene["metadata"]["mechanism_readiness"] = mechanism_readiness
    scene["metadata"]["mechanism_coupon"] = mechanism_coupon
    scene["metadata"]["local_composer"] = {
        "schema_version": LOCAL_COMPOSER_SCHEMA_V0,
        "materialization_status": "prepared_open_top_trays_for_fusion_smoke",
        "selection_bridge": "p31_open_top_tray_from_selected_module.v0",
        "geometry_status": "open_top_tray_candidates",
        "appearance_status": "stored_for_preview_only_not_materialized",
        "mechanism_status": (
            "coupon_prepared_for_fusion_smoke"
            if mechanism_coupon["status"] == "prepared_for_fusion_smoke"
            else "experimental_contract_not_materialized"
        ),
        "mechanism_coupon_status": mechanism_coupon["status"],
        "print_validation_status": "not_validated",
        "reason": (
            "P31 turns each selected BoxFill module into an explicit open-top tray "
            "with walls, a retained floor, and one generic cavity; the Fusion smoke "
            "and physical print remain unobserved."
        ),
    }
    return {
        "schema_version": LOCAL_COMPOSER_EXPORT_SCHEMA_V0,
        "selection": selection,
        "appearance": appearance,
        "mechanism": mechanism,
        "mechanism_readiness": mechanism_readiness,
        "mechanism_coupon": mechanism_coupon,
        "cad_ir": scene,
        "limits": [
            "The CAD IR contains one open-top tray candidate per selected module, with one generic cavity and retained walls/floor.",
            "No Fusion operation was executed by this export.",
            "A requested sliding lid adds one separate two-piece coupon; Fusion must still confirm the joins.",
            "P21 scores are proxies and do not prove ergonomics or printability.",
            "No physical print or slicer validation is included.",
        ],
    }


def _selection_bridge_components(
    solved_plan: BoxFillPlan,
    selected_variant_id: str,
    defaults: GeometryDefaults,
    mechanism: dict[str, object],
    box_size: Dimension3D,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Materialize selected trays and one optional external-rail coupon."""

    components: list[dict[str, object]] = []
    for index, module in enumerate(solved_plan.modules):
        if not module.printable:
            continue
        instance_id = f"selection:{selected_variant_id}:{module.id}"
        body_id = f"body:{instance_id}"
        cavity, cavity_operation = _open_top_tray_cavity(module, body_id, defaults)
        source_asset_ids = sorted(
            {
                allocation.asset_id
                for allocation in solved_plan.allocations
                if allocation.module_id == module.id
            }
        )
        component = CadComponent(
            id=f"component:{instance_id}",
            name=f"Selection - {module.name} open tray",
            module_id=module.id,
            instance_id=instance_id,
            functional_type="box_fill_selected_open_top_tray",
            body=CadBody(
                id=body_id,
                name=f"{module.name} selected open-top tray",
                kind="rectangular_blank",
                source_cell_instance_id=instance_id,
                theoretical_origin=module.origin,
                theoretical_size=module.size,
                printable_origin=module.origin,
                printable_size=module.size,
                cavities=(cavity,),
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
                    cavity_operation,
                ),
            ),
            metadata={
                "label": module.name,
                "source_index": index,
                "source": module.source,
                "layer_id": module.layer_id,
                "orientation": module.orientation,
                "selected_variant_id": selected_variant_id,
                "selection_bridge": "p31_open_top_tray_from_selected_module.v0",
                "geometry_status": "open_top_tray_candidate",
                "source_asset_ids": source_asset_ids,
                "tray_projection": {
                    "policy": "open_top_tray_from_selected_module.v0",
                    "wall_thickness_mm": defaults.wall_thickness_mm,
                    "floor_thickness_mm": defaults.floor_thickness_mm,
                    "cavity_id": cavity.id,
                    "cavity_size_mm": {"x": cavity.size.x, "y": cavity.size.y, "z": cavity.size.z},
                },
            },
        )
        components.append(component.to_dict())
    if not components:
        raise LocalComposerError(
            "The selected variant has no printable modules to materialize for Fusion."
        )
    coupon_components, coupon_metadata = _sliding_lid_coupon_components(
        solved_plan,
        selected_variant_id,
        defaults,
        mechanism,
        box_size,
    )
    components.extend(coupon_components)
    return components, coupon_metadata


def _sliding_lid_coupon_components(
    solved_plan: BoxFillPlan,
    selected_variant_id: str,
    defaults: GeometryDefaults,
    mechanism: dict[str, object],
    box_size: Dimension3D,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Build one separate coupon so a lid cannot collide with the packed layout."""

    if mechanism["kind"] != "sliding_lid":
        return [], {"status": "not_requested", "materialization_status": "not_materialized"}
    source_module = next(
        (
            module
            for module in solved_plan.modules
            if module.printable
            and sliding_lid_readiness(
                module.id,
                {"x": module.size.x, "y": module.size.y, "z": module.size.z},
                mechanism,
            )["status"] == "planned_for_coupon"
        ),
        None,
    )
    if source_module is None:
        return [], {
            "status": "refused",
            "materialization_status": "not_materialized",
            "reason": "No selected module is large enough for the sliding-lid coupon.",
        }

    coupon_origin = Point3D(box_size.x + 20.0, 20.0, 0.0)
    coupon_module = replace(
        source_module,
        id=f"{source_module.id}:sliding-lid-coupon-tray",
        name=f"{source_module.name} sliding-lid coupon tray",
        origin=coupon_origin,
    )
    geometry = sliding_lid_coupon_geometry(
        source_module.id,
        {"x": coupon_origin.x, "y": coupon_origin.y, "z": coupon_origin.z},
        {"x": source_module.size.x, "y": source_module.size.y, "z": source_module.size.z},
        mechanism,
    )
    if geometry is None:
        raise LocalComposerError("P34_SLIDING_LID_COUPON_NOT_FEASIBLE: readiness changed unexpectedly.")

    tray_instance_id = f"coupon:{selected_variant_id}:{source_module.id}:tray"
    tray_body_id = f"body:{tray_instance_id}"
    cavity, cavity_operation = _open_top_tray_cavity(coupon_module, tray_body_id, defaults)
    source_asset_ids = sorted(
        {
            allocation.asset_id
            for allocation in solved_plan.allocations
            if allocation.module_id == source_module.id
        }
    )
    tray_component = CadComponent(
        id=f"component:{tray_instance_id}",
        name=f"Coupon - {source_module.name} tray",
        module_id=source_module.id,
        instance_id=tray_instance_id,
        functional_type="sliding_lid_coupon_tray",
        body=CadBody(
            id=tray_body_id,
            name=f"{source_module.name} coupon tray",
            kind="rectangular_blank",
            source_cell_instance_id=tray_instance_id,
            theoretical_origin=coupon_module.origin,
            theoretical_size=coupon_module.size,
            printable_origin=coupon_module.origin,
            printable_size=coupon_module.size,
            cavities=(cavity,),
            face_classifications=(),
            applied_tolerances=(),
            operations=(
                CadOperation(
                    id=f"{tray_body_id}:create_rectangular_prism",
                    kind="create_rectangular_prism",
                    target_id=tray_body_id,
                    parameters={
                        "origin_source": "printable_origin_mm",
                        "size_source": "printable_size_mm",
                        "coordinate_frame": "scene.frame",
                    },
                ),
                cavity_operation,
            ),
        ),
        metadata={
            "coupon": True,
            "coupon_policy": geometry["policy"],
            "source_module_id": source_module.id,
            "source_asset_ids": source_asset_ids,
            "geometry_status": "sliding_lid_coupon_tray_candidate",
        },
    )
    lid = geometry["lid"]
    lid_origin = Point3D(**lid["origin_mm"])
    lid_size = Dimension3D(**lid["base_slab_size_mm"])
    lid_instance_id = f"coupon:{selected_variant_id}:{source_module.id}:lid"
    lid_body_id = f"body:{lid_instance_id}"
    rail_operations = tuple(
        CadOperation(
            id=f"{lid_body_id}:{rail['id']}:{RAIL_JOIN_OPERATION_KIND}",
            kind=RAIL_JOIN_OPERATION_KIND,
            target_id=lid_body_id,
            parameters={
                "coordinate_frame": "body.local",
                "local_origin_mm": rail["local_origin_mm"],
                "size_mm": rail["size_mm"],
                "mechanism_policy": geometry["policy"],
                "join_overlap_mm": lid["rail_join_overlap_mm"],
            },
        )
        for rail in lid["rails"]
    )
    lid_component = CadComponent(
        id=f"component:{lid_instance_id}",
        name=f"Coupon - {source_module.name} sliding lid",
        module_id=source_module.id,
        instance_id=lid_instance_id,
        functional_type="sliding_lid_coupon_cap",
        body=CadBody(
            id=lid_body_id,
            name=f"{source_module.name} coupon sliding lid",
            kind="rectangular_blank",
            source_cell_instance_id=lid_instance_id,
            theoretical_origin=lid_origin,
            theoretical_size=lid_size,
            printable_origin=lid_origin,
            printable_size=lid_size,
            cavities=(),
            face_classifications=(),
            applied_tolerances=(),
            operations=(
                CadOperation(
                    id=f"{lid_body_id}:create_rectangular_prism",
                    kind="create_rectangular_prism",
                    target_id=lid_body_id,
                    parameters={
                        "origin_source": "printable_origin_mm",
                        "size_source": "printable_size_mm",
                        "coordinate_frame": "scene.frame",
                    },
                ),
                *rail_operations,
            ),
        ),
        metadata={
            "coupon": True,
            "coupon_policy": geometry["policy"],
            "source_module_id": source_module.id,
            "source_asset_ids": source_asset_ids,
            "slide_axis": geometry["slide_axis"],
            "travel_end_overlap_mm": lid["travel_end_overlap_mm"],
            "rail_clearance_mm": lid["rail_clearance_mm"],
            "rail_join_overlap_mm": lid["rail_join_overlap_mm"],
            "geometry_status": "sliding_lid_coupon_cap_candidate",
        },
    )
    return [tray_component.to_dict(), lid_component.to_dict()], {
        "status": "prepared_for_fusion_smoke",
        "materialization_status": "two_piece_coupon_cad_ir",
        "policy": geometry["policy"],
        "source_module_id": source_module.id,
        "component_ids": [tray_component.id, lid_component.id],
        "piece_count": geometry["piece_count"],
    }

def _open_top_tray_cavity(
    module: BoxFillModule,
    body_id: str,
    defaults: GeometryDefaults,
) -> tuple[CadCavity, CadOperation]:
    """Derive one generic top-open cavity without asset-specific fit claims."""

    wall = defaults.wall_thickness_mm
    floor = defaults.floor_thickness_mm
    cavity_size = Dimension3D(
        x=module.size.x - (2 * wall),
        y=module.size.y - (2 * wall),
        z=module.size.z - floor,
    )
    if min(cavity_size.x, cavity_size.y, cavity_size.z) <= 0:
        raise LocalComposerError(
            "P31_TRAY_CAVITY_NOT_FEASIBLE: selected module "
            f"{module.id!r} cannot retain {wall:.2f} mm walls and a {floor:.2f} mm floor."
        )

    cavity_id = f"{module.id}:open-top-cavity"
    cavity = CadCavity(
        id=cavity_id,
        functional_type=FunctionalType.FREE.value,
        local_origin=Point3D(x=wall, y=wall, z=floor),
        size=cavity_size,
        clearance_mm=0.0,
        clearance_source="p31_open_top_tray_no_asset_fit_clearance",
        comment="P31 generic open-top tray cavity; source assets remain traceability only.",
        features=(),
        status="planned_for_fusion_smoke",
        fusion_generation="planned_for_fusion_smoke",
    )
    operation = CadOperation(
        id=f"{body_id}:{cavity_id}:{CAVITY_OPERATION_KIND}",
        kind=CAVITY_OPERATION_KIND,
        target_id=body_id,
        parameters={
            "cavity_id": cavity_id,
            "functional_type": FunctionalType.FREE.value,
            "local_origin_mm": {"x": wall, "y": wall, "z": floor},
            "size_mm": {"x": cavity_size.x, "y": cavity_size.y, "z": cavity_size.z},
            "clearance_mm": 0.0,
            "clearance_source": "p31_open_top_tray_no_asset_fit_clearance",
            "coordinate_frame": "body.local",
            "execution_status": "planned_for_fusion_smoke",
            "fusion_generation": "planned_for_fusion_smoke",
        },
    )
    return cavity, operation

def _draft_to_engine(
    raw_draft: object,
) -> tuple[InsertConfig, tuple[BoxFillCandidate, ...], str, tuple[str, ...]]:
    draft = _mapping(raw_draft, "draft")
    _reject_unknown(
        draft,
        {
            "schema_version",
            "project_name",
            "box",
            "assets",
            "layers",
            "reservations",
            "manual_modules",
            "candidates",
            "preference",
            "policies",
            "appearance",
            "mechanism",
        },
        "draft",
    )
    if _string(draft, "schema_version", "draft") != LOCAL_COMPOSER_SCHEMA_V0:
        raise LocalComposerError(
            f"Unsupported local composer schema; expected {LOCAL_COMPOSER_SCHEMA_V0!r}."
        )
    project_name = _string(draft, "project_name", "draft")
    box_spec = _box_spec(_mapping_value(draft, "box", "draft.box"))
    assets = _assets(_list_value(draft, "assets", "draft.assets"))
    layers = _layers(_list_value(draft, "layers", "draft.layers"))
    if not layers:
        raise LocalComposerError("draft.layers must contain at least one layer.")
    layer_ids = {layer.id for layer in layers}
    reservations = _reservations(_list_value(draft, "reservations", "draft.reservations"), layer_ids)
    manual_modules = _manual_modules(
        _list_value(draft, "manual_modules", "draft.manual_modules"), layer_ids
    )
    asset_ids = {asset.id: asset for asset in assets}
    candidates = _candidates(
        _list_value(draft, "candidates", "draft.candidates"),
        layer_ids,
        asset_ids,
        {module.id for module in manual_modules},
    )
    preference = _optional_string(draft, "preference", "draft", "balanced")
    try:
        appearance = normalize_appearance(draft.get("appearance"))
    except AppearanceError as exc:
        raise LocalComposerError(str(exc)) from exc
    try:
        mechanism = normalize_mechanism(draft.get("mechanism"))
    except MechanismError as exc:
        raise LocalComposerError(str(exc)) from exc
    standard_preference_profile(preference)
    policies_raw = draft.get("policies")
    policies = SUPPORTED_POLICY_IDS if policies_raw is None else tuple(
        _strings(_list(policies_raw, "draft.policies"), "draft.policies")
    )
    unknown_policies = sorted(set(policies) - set(SUPPORTED_POLICY_IDS))
    if unknown_policies:
        raise LocalComposerError("Unsupported P21 policies: " + ", ".join(unknown_policies))

    plan = BoxFillPlan(
        schema_version=BOX_FILL_PLAN_SCHEMA_V0,
        id="local-composer-plan",
        box=BoxFillBox(
            id="local-composer-box",
            inner_dimensions=box_spec.inner_dimensions,
            origin=Point3D(0.0, 0.0, 0.0),
            usable_height_mm=box_spec.usable_height_mm,
            lid_clearance_mm=box_spec.lid_clearance_mm,
            units="mm",
        ),
        assets=assets,
        layers=layers,
        reservations=reservations,
        modules=manual_modules,
        metadata={
            "source": "local_composer",
            "schema_version": LOCAL_COMPOSER_SCHEMA_V0,
            "ui_warning": "The draft is the interaction model; the engine contracts remain authoritative.",
            "appearance": appearance,
            "mechanism": mechanism,
        },
    )
    config = InsertConfig(
        project_name=project_name,
        units="mm",
        box=box_spec,
        tolerances=ToleranceProfile(),
        defaults=GeometryDefaults(),
        layout=LayoutSettings(),
        modules=(),
        assets=assets,
        print_profile="default",
        source_path="local-composer",
        box_fill_plan=plan,
    )
    return config, candidates, preference, policies


def _box_spec(raw: object) -> BoxSpec:
    box = _mapping(raw, "draft.box")
    _reject_unknown(box, {"inner_dimensions_mm", "usable_height_mm", "lid_clearance_mm"}, "draft.box")
    dimensions = _dimension(_mapping_value(box, "inner_dimensions_mm", "draft.box.inner_dimensions_mm"), "draft.box.inner_dimensions_mm")
    return BoxSpec(
        inner_dimensions=dimensions,
        usable_height_mm=_positive_number(box, "usable_height_mm", "draft.box"),
        lid_clearance_mm=_non_negative_number(box, "lid_clearance_mm", "draft.box"),
    )


def _assets(raw_assets: list[object]) -> tuple[Asset, ...]:
    assets: list[Asset] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_assets):
        field = f"draft.assets[{index}]"
        raw = _mapping(entry, field)
        _reject_unknown(
            raw,
            {
                "id",
                "name",
                "kind",
                "quantity",
                "dimensions_mm",
                "containment_intent",
                "dimension_confidence",
            },
            field,
        )
        asset_id = _string(raw, "id", field)
        if asset_id in seen:
            raise LocalComposerError(f"Duplicate asset id {asset_id!r}.")
        seen.add(asset_id)
        try:
            kind = AssetKind(_optional_string(raw, "kind", field, "other"))
            intent = ContainmentIntent(_optional_string(raw, "containment_intent", field, "store"))
            confidence = DimensionConfidence(
                _optional_string(raw, "dimension_confidence", field, "approximate")
            )
        except ValueError as exc:
            raise LocalComposerError(f"{field} contains an unsupported asset enum value.") from exc
        quantity_raw = _mapping_value(raw, "quantity", f"{field}.quantity")
        quantity = _mapping(quantity_raw, f"{field}.quantity")
        _reject_unknown(quantity, {"count", "grouping"}, f"{field}.quantity")
        count = _positive_int(quantity, "count", f"{field}.quantity")
        assets.append(
            Asset(
                id=asset_id,
                name=_string(raw, "name", field),
                kind=kind,
                quantity=AssetQuantity(count, _optional_string(quantity, "grouping", f"{field}.quantity", "single")),
                dimensions=_dimension(_mapping_value(raw, "dimensions_mm", f"{field}.dimensions_mm"), f"{field}.dimensions_mm"),
                dimension_confidence=confidence,
                containment_intent=intent,
                storage_orientation=AssetStorageOrientation.AUTO,
            )
        )
    return tuple(assets)


def _layers(raw_layers: list[object]) -> tuple[BoxFillLayer, ...]:
    layers: list[BoxFillLayer] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_layers):
        field = f"draft.layers[{index}]"
        raw = _mapping(entry, field)
        _reject_unknown(raw, {"id", "origin_z_mm", "height_mm", "role"}, field)
        layer_id = _string(raw, "id", field)
        if layer_id in seen:
            raise LocalComposerError(f"Duplicate layer id {layer_id!r}.")
        seen.add(layer_id)
        layers.append(
            BoxFillLayer(
                id=layer_id,
                origin_z_mm=_non_negative_number(raw, "origin_z_mm", field),
                height_mm=_positive_number(raw, "height_mm", field),
                role=_optional_string(raw, "role", field, "storage"),
            )
        )
    return tuple(layers)


def _reservations(raw_reservations: list[object], layer_ids: set[str]) -> tuple[BoxFillReservation, ...]:
    reservations: list[BoxFillReservation] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_reservations):
        field = f"draft.reservations[{index}]"
        raw = _mapping(entry, field)
        _reject_unknown(raw, {"id", "kind", "origin_mm", "size_mm", "layer_id"}, field)
        reservation_id = _string(raw, "id", field)
        if reservation_id in seen:
            raise LocalComposerError(f"Duplicate reservation id {reservation_id!r}.")
        seen.add(reservation_id)
        layer_id = _optional_string(raw, "layer_id", field, "") or None
        if layer_id is not None and layer_id not in layer_ids:
            raise LocalComposerError(f"{field}.layer_id references unknown layer {layer_id!r}.")
        try:
            kind = BoxFillReservationKind(_optional_string(raw, "kind", field, "generic"))
        except ValueError as exc:
            raise LocalComposerError(f"{field}.kind is not supported.") from exc
        reservations.append(
            BoxFillReservation(
                id=reservation_id,
                kind=kind,
                origin=_point(_mapping_value(raw, "origin_mm", f"{field}.origin_mm"), f"{field}.origin_mm"),
                size=_dimension(_mapping_value(raw, "size_mm", f"{field}.size_mm"), f"{field}.size_mm"),
                layer_id=layer_id,
                source="local_composer",
            )
        )
    return tuple(reservations)


def _manual_modules(raw_modules: list[object], layer_ids: set[str]) -> tuple[BoxFillModule, ...]:
    modules: list[BoxFillModule] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_modules):
        field = f"draft.manual_modules[{index}]"
        raw = _mapping(entry, field)
        _reject_unknown(raw, {"id", "name", "origin_mm", "size_mm", "layer_id", "locked"}, field)
        module_id = _string(raw, "id", field)
        if module_id in seen:
            raise LocalComposerError(f"Duplicate manual module id {module_id!r}.")
        seen.add(module_id)
        layer_id = _string(raw, "layer_id", field)
        if layer_id not in layer_ids:
            raise LocalComposerError(f"{field}.layer_id references unknown layer {layer_id!r}.")
        modules.append(
            BoxFillModule(
                id=module_id,
                name=_string(raw, "name", field),
                origin=_point(_mapping_value(raw, "origin_mm", f"{field}.origin_mm"), f"{field}.origin_mm"),
                size=_dimension(_mapping_value(raw, "size_mm", f"{field}.size_mm"), f"{field}.size_mm"),
                layer_id=layer_id,
                locked=_optional_bool(raw, "locked", field, True),
                manual=True,
                source="local_composer",
            )
        )
    return tuple(modules)


def _candidates(
    raw_candidates: list[object],
    layer_ids: set[str],
    assets_by_id: dict[str, Asset],
    reserved_module_ids: set[str],
) -> tuple[BoxFillCandidate, ...]:
    candidates: list[BoxFillCandidate] = []
    seen: set[str] = set(reserved_module_ids)
    assigned_assets: set[str] = set()
    for index, entry in enumerate(raw_candidates):
        field = f"draft.candidates[{index}]"
        raw = _mapping(entry, field)
        _reject_unknown(
            raw,
            {"id", "name", "size_mm", "allowed_layers", "allow_xy_rotation", "priority", "asset_ids"},
            field,
        )
        candidate_id = _string(raw, "id", field)
        if candidate_id in seen:
            raise LocalComposerError(f"Duplicate candidate/module id {candidate_id!r}.")
        seen.add(candidate_id)
        allowed_layers = tuple(_strings(_list_value(raw, "allowed_layers", f"{field}.allowed_layers"), f"{field}.allowed_layers"))
        if not allowed_layers or not set(allowed_layers).issubset(layer_ids):
            raise LocalComposerError(f"{field}.allowed_layers must reference at least one known layer.")
        asset_ids = tuple(_strings(_list_value(raw, "asset_ids", f"{field}.asset_ids"), f"{field}.asset_ids"))
        unknown_assets = sorted(set(asset_ids) - set(assets_by_id))
        if unknown_assets:
            raise LocalComposerError(f"{field}.asset_ids references unknown assets: {', '.join(unknown_assets)}.")
        duplicate_assets = sorted(set(asset_ids) & assigned_assets)
        if duplicate_assets:
            raise LocalComposerError(f"Assets may be assigned to only one candidate: {', '.join(duplicate_assets)}.")
        assigned_assets.update(asset_ids)
        allocations = tuple(
            AssetAllocation(
                asset_id=asset_id,
                quantity=assets_by_id[asset_id].quantity.count,
                module_id=candidate_id,
                source="local_composer",
                intent=assets_by_id[asset_id].containment_intent.value,
            )
            for asset_id in asset_ids
        )
        candidates.append(
            BoxFillCandidate(
                module_id=candidate_id,
                name=_string(raw, "name", field),
                size=_dimension(_mapping_value(raw, "size_mm", f"{field}.size_mm"), f"{field}.size_mm"),
                allocations=allocations,
                allowed_layer_ids=allowed_layers,
                allow_xy_rotation=_optional_bool(raw, "allow_xy_rotation", field, True),
                priority=_optional_int(raw, "priority", field, 0),
                source="local_composer",
                metadata={"asset_ids": list(asset_ids), "draft_index": index},
            )
        )
    return tuple(candidates)


def create_local_composer_server(host: str = "127.0.0.1", port: int = 8001) -> ThreadingHTTPServer:
    if host not in LOOPBACK_HOSTS:
        raise LocalComposerError("The local composer may bind only to 127.0.0.1 or localhost.")
    return ThreadingHTTPServer((host, port), LocalComposerRequestHandler)


class LocalComposerRequestHandler(BaseHTTPRequestHandler):
    server_version = "BGIGLocalComposer/0"

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors_headers()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        route = urlsplit(self.path).path
        if route == "/api/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "schema_version": LOCAL_COMPOSER_SCHEMA_V0,
                    "project_schema_version": PROJECT_SCHEMA_V1,
                },
            )
        elif route == "/api/starter":
            self._send_json(HTTPStatus.OK, {"draft": starter_draft()})
        elif route == "/api/starters":
            self._send_json(HTTPStatus.OK, {"starters": starter_catalog()})
        elif route == "/api/project-v1/starter":
            self._send_json(HTTPStatus.OK, {"project": starter_project_v1()})
        else:
            self._send_error(HTTPStatus.NOT_FOUND, "NOT_FOUND", "Unknown local composer route.")

    def do_POST(self) -> None:  # noqa: N802
        route = urlsplit(self.path).path
        try:
            payload = self._read_json()
            if route == "/api/portfolio":
                self._send_json(HTTPStatus.OK, {"portfolio": portfolio_from_draft(payload)})
            elif route == "/api/export":
                request = _mapping(payload, "request")
                self._send_json(
                    HTTPStatus.OK,
                    export_from_draft(request.get("draft"), _optional_nullable_string(request, "variant_id", "request")),
                )
            elif route == "/api/project-v1/normalize":
                self._send_json(HTTPStatus.OK, normalize_project_v1(payload))
            elif route == "/api/project-v1/derive-containers":
                self._send_json(HTTPStatus.OK, derive_containers_v1(payload))
            else:
                self._send_error(HTTPStatus.NOT_FOUND, "NOT_FOUND", "Unknown local composer route.")
        except LocalComposerError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "DRAFT_INVALID", str(exc))
        except ValueError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "ENGINE_REJECTED", str(exc))
        except json.JSONDecodeError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "JSON_INVALID", f"Invalid JSON: {exc.msg}.")

    def _read_json(self) -> object:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise LocalComposerError("Content-Length is required.")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise LocalComposerError("Content-Length must be an integer.") from exc
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise LocalComposerError(f"Request body must be between 0 and {MAX_REQUEST_BYTES} bytes.")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, status: HTTPStatus, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: HTTPStatus, code: str, message: str) -> None:
        self._send_json(status, {"error": {"code": code, "message": message}})

    def _cors_headers(self) -> None:
        origin = self.headers.get("Origin")
        if origin in CORS_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def log_message(self, format: str, *args: object) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local BGIG composer loopback adapter.")
    parser.add_argument("--host", default="127.0.0.1", choices=sorted(LOOPBACK_HOSTS))
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args(argv)
    server = create_local_composer_server(args.host, args.port)
    print(f"BGIG local composer API listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def _starter_asset(asset_id: str, name: str, kind: str, count: int, x: float, y: float, z: float, intent: str) -> dict[str, object]:
    return {
        "id": asset_id,
        "name": name,
        "kind": kind,
        "quantity": {"count": count, "grouping": "set"},
        "dimensions_mm": {"x": x, "y": y, "z": z},
        "containment_intent": intent,
        "dimension_confidence": "approximate",
    }


def _starter_candidate(candidate_id: str, name: str, x: float, y: float, z: float, layer_id: str, asset_ids: list[str]) -> dict[str, object]:
    return {
        "id": candidate_id,
        "name": name,
        "size_mm": {"x": x, "y": y, "z": z},
        "allowed_layers": [layer_id],
        "allow_xy_rotation": True,
        "priority": 0,
        "asset_ids": asset_ids,
    }


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise LocalComposerError(f"{field} must be an object.")
    return dict(value)


def _mapping_value(raw: dict[str, object], key: str, field: str) -> object:
    if key not in raw:
        raise LocalComposerError(f"Missing required field {field!r}.")
    return raw[key]


def _list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise LocalComposerError(f"{field} must be a list.")
    return value


def _list_value(raw: dict[str, object], key: str, field: str) -> list[object]:
    return _list(_mapping_value(raw, key, field), field)


def _string(raw: dict[str, object], key: str, field: str) -> str:
    value = _mapping_value(raw, key, f"{field}.{key}")
    if not isinstance(value, str) or not value.strip() or len(value) > 120:
        raise LocalComposerError(f"{field}.{key} must be a non-empty string up to 120 characters.")
    return value.strip()


def _optional_string(raw: dict[str, object], key: str, field: str, default: str) -> str:
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, str) or len(value) > 120:
        raise LocalComposerError(f"{field}.{key} must be a string up to 120 characters.")
    return value.strip()


def _optional_nullable_string(raw: dict[str, object], key: str, field: str) -> str | None:
    if key not in raw or raw[key] is None:
        return None
    return _optional_string(raw, key, field, "") or None


def _strings(values: list[object], field: str) -> list[str]:
    strings: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip() or len(value) > 120:
            raise LocalComposerError(f"{field}[{index}] must be a non-empty string up to 120 characters.")
        strings.append(value.strip())
    return strings


def _number(raw: dict[str, object], key: str, field: str) -> float:
    value = _mapping_value(raw, key, f"{field}.{key}")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise LocalComposerError(f"{field}.{key} must be a finite number.")
    return float(value)


def _positive_number(raw: dict[str, object], key: str, field: str) -> float:
    value = _number(raw, key, field)
    if value <= 0:
        raise LocalComposerError(f"{field}.{key} must be greater than zero.")
    return value


def _non_negative_number(raw: dict[str, object], key: str, field: str) -> float:
    value = _number(raw, key, field)
    if value < 0:
        raise LocalComposerError(f"{field}.{key} must be zero or greater.")
    return value


def _positive_int(raw: dict[str, object], key: str, field: str) -> int:
    value = _mapping_value(raw, key, f"{field}.{key}")
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise LocalComposerError(f"{field}.{key} must be a positive integer.")
    return value


def _optional_int(raw: dict[str, object], key: str, field: str, default: int) -> int:
    if key not in raw:
        return default
    value = raw[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise LocalComposerError(f"{field}.{key} must be an integer.")
    return value


def _optional_bool(raw: dict[str, object], key: str, field: str, default: bool) -> bool:
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, bool):
        raise LocalComposerError(f"{field}.{key} must be a boolean.")
    return value


def _point(value: object, field: str) -> Point3D:
    raw = _mapping(value, field)
    _reject_unknown(raw, {"x", "y", "z"}, field)
    return Point3D(_non_negative_number(raw, "x", field), _non_negative_number(raw, "y", field), _non_negative_number(raw, "z", field))


def _dimension(value: object, field: str) -> Dimension3D:
    raw = _mapping(value, field)
    _reject_unknown(raw, {"x", "y", "z"}, field)
    return Dimension3D(_positive_number(raw, "x", field), _positive_number(raw, "y", field), _positive_number(raw, "z", field))


def _reject_unknown(raw: dict[str, object], allowed: set[str], field: str) -> None:
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise LocalComposerError(f"Unknown fields in {field}: {', '.join(unknown)}.")


if __name__ == "__main__":
    raise SystemExit(main())