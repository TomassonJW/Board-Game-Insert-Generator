"""CAD-agnostic intermediate representation for future CAD adapters.

This module intentionally contains no Fusion 360 dependency. It converts the
resolved pure-Python engine output into a small, serializable scene contract that
future adapters can consume without recalculating layout or tolerances.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from board_game_insert_generator.asset_candidates import (
    build_asset_candidate_variants,
    build_executable_asset_module_plan,
    build_module_candidates_from_assets,
    recommended_asset_candidate_variant,
)
from board_game_insert_generator.feature_taxonomy import feature_taxonomy_to_dict
from board_game_insert_generator.volumetric import build_volumetric_summary
from board_game_insert_generator.models import (
    Cavity,
    Dimension3D,
    FaceClassification,
    Feature,
    FaceToleranceApplication,
    InsertConfig,
    LayoutResult,
    ModuleRequest,
    Point3D,
    PrintableBody,
)

CAD_IR_SCHEMA_VERSION = "cad_ir.v0"
CAD_IR_UNITS = "mm"
CAD_IR_COORDINATE_SYSTEM = "right_handed_z_up_mm"
CAVITY_OPERATION_KIND = "subtract_rectangular_cavity"
CAVITY_FEATURE_OPERATION_KIND = "describe_cavity_feature"

class CadIrError(ValueError):
    """Raised when resolved engine output cannot be represented as CAD IR."""

@dataclass(frozen=True)
class CadFrame:
    """Global coordinate frame used by the CAD IR scene."""

    origin: Point3D
    x_axis: str = "+x"
    y_axis: str = "+y"
    z_axis: str = "+z"
    handedness: str = "right"

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin_mm": _point_to_dict(self.origin),
            "x_axis": self.x_axis,
            "y_axis": self.y_axis,
            "z_axis": self.z_axis,
            "handedness": self.handedness,
        }

@dataclass(frozen=True)
class CadParameter:
    id: str
    value: float | str | bool
    unit: str | None
    category: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "value": self.value,
            "unit": self.unit,
            "category": self.category,
            "description": self.description,
        }

@dataclass(frozen=True)
class CadOperation:
    id: str
    kind: str
    target_id: str
    parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "target_id": self.target_id,
            "parameters": self.parameters,
        }

@dataclass(frozen=True)
class CadBoxReference:
    id: str
    name: str
    origin: Point3D
    size: Dimension3D
    printable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "origin_mm": _point_to_dict(self.origin),
            "size_mm": _dimension_to_dict(self.size),
            "printable": self.printable,
            "role": "reference_box",
        }

@dataclass(frozen=True)
class CadFaceRecord:
    face: str
    role: str
    reason: str
    neighbor_instance_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "face": self.face,
            "role": self.role,
            "reason": self.reason,
            "neighbor_instance_id": self.neighbor_instance_id,
        }

@dataclass(frozen=True)
class CadToleranceRecord:
    face: str
    role: str
    offset_mm: float
    rule_id: str
    clearance_source: str
    receives_clearance: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "face": self.face,
            "role": self.role,
            "offset_mm": self.offset_mm,
            "rule_id": self.rule_id,
            "clearance_source": self.clearance_source,
            "receives_clearance": self.receives_clearance,
            "reason": self.reason,
        }

@dataclass(frozen=True)
class CadFeature:
    id: str
    kind: str
    placement: str
    position: Point3D
    size: Dimension3D | None
    radius_mm: float | None
    comment: str
    status: str = "abstract_only"
    fusion_generation: str = "not_implemented"
    taxonomy: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "placement": self.placement,
            "position_mm": _point_to_dict(self.position),
            "size_mm": _dimension_to_dict(self.size) if self.size is not None else None,
            "radius_mm": self.radius_mm,
            "comment": self.comment,
            "status": self.status,
            "fusion_generation": self.fusion_generation,
            "taxonomy": self.taxonomy,
        }

@dataclass(frozen=True)
class CadCavity:
    id: str
    functional_type: str
    local_origin: Point3D
    size: Dimension3D
    clearance_mm: float
    clearance_source: str
    comment: str
    features: tuple[CadFeature, ...]
    status: str = "abstract_only"
    fusion_generation: str = "not_implemented"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "functional_type": self.functional_type,
            "local_origin_mm": _point_to_dict(self.local_origin),
            "size_mm": _dimension_to_dict(self.size),
            "clearance_mm": self.clearance_mm,
            "clearance_source": self.clearance_source,
            "comment": self.comment,
            "features": [feature.to_dict() for feature in self.features],
            "status": self.status,
            "fusion_generation": self.fusion_generation,
        }

@dataclass(frozen=True)
class CadBody:
    id: str
    name: str
    kind: str
    source_cell_instance_id: str
    theoretical_origin: Point3D
    theoretical_size: Dimension3D
    printable_origin: Point3D
    printable_size: Dimension3D
    cavities: tuple[CadCavity, ...]
    face_classifications: tuple[CadFaceRecord, ...]
    applied_tolerances: tuple[CadToleranceRecord, ...]
    operations: tuple[CadOperation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "source_cell_instance_id": self.source_cell_instance_id,
            "theoretical_origin_mm": _point_to_dict(self.theoretical_origin),
            "theoretical_size_mm": _dimension_to_dict(self.theoretical_size),
            "printable_origin_mm": _point_to_dict(self.printable_origin),
            "printable_size_mm": _dimension_to_dict(self.printable_size),
            "cavities": [cavity.to_dict() for cavity in self.cavities],
            "face_classifications": [entry.to_dict() for entry in self.face_classifications],
            "applied_tolerances": [entry.to_dict() for entry in self.applied_tolerances],
            "operations": [operation.to_dict() for operation in self.operations],
        }

@dataclass(frozen=True)
class CadComponent:
    id: str
    name: str
    module_id: str
    instance_id: str
    functional_type: str
    body: CadBody
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "module_id": self.module_id,
            "instance_id": self.instance_id,
            "functional_type": self.functional_type,
            "body": self.body.to_dict(),
            "metadata": self.metadata,
        }

@dataclass(frozen=True)
class CadSceneMetadata:
    project_name: str
    source_path: str | None
    layout_strategy: str
    print_profile: str
    warnings: tuple[str, ...]
    assets: tuple[dict[str, Any], ...] = ()
    module_candidates: tuple[dict[str, Any], ...] = ()
    asset_candidate_variants: tuple[dict[str, Any], ...] = ()
    recommended_asset_candidate_variant: dict[str, Any] | None = None
    executable_asset_plan: dict[str, Any] | None = None
    volumetric_grid: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "source_path": self.source_path,
            "layout_strategy": self.layout_strategy,
            "print_profile": self.print_profile,
            "warnings": list(self.warnings),
            "assets": list(self.assets),
            "module_candidates": list(self.module_candidates),
            "asset_candidate_variants": list(self.asset_candidate_variants),
            "recommended_asset_candidate_variant": self.recommended_asset_candidate_variant,
            "executable_asset_plan": self.executable_asset_plan,
            "volumetric_grid": self.volumetric_grid,
        }

@dataclass(frozen=True)
class CadScene:
    schema_version: str
    units: str
    coordinate_system: str
    frame: CadFrame
    box_reference: CadBoxReference
    parameters: tuple[CadParameter, ...]
    components: tuple[CadComponent, ...]
    metadata: CadSceneMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "units": self.units,
            "coordinate_system": self.coordinate_system,
            "frame": self.frame.to_dict(),
            "box_reference": self.box_reference.to_dict(),
            "parameters": [parameter.to_dict() for parameter in self.parameters],
            "components": [component.to_dict() for component in self.components],
            "metadata": self.metadata.to_dict(),
        }

def build_blank_cad_scene(config: InsertConfig, layout: LayoutResult) -> CadScene:
    """Build the CAD IR contract for rectangular blanks and abstract cavities.

    The scene mirrors already-resolved engine output. It does not infer layout,
    change tolerances, cut cavities in Fusion 360, call Fusion 360, or export files.
    """

    if config.units != CAD_IR_UNITS:
        raise CadIrError(f"CAD IR V0 supports only millimeters, got {config.units!r}.")

    printable_by_instance = {body.instance_id: body for body in layout.printable_bodies}
    cell_instance_ids = {cell.instance_id for cell in layout.cells}
    missing_body_ids = sorted(cell_instance_ids - set(printable_by_instance))
    extra_body_ids = sorted(set(printable_by_instance) - cell_instance_ids)
    if missing_body_ids:
        raise CadIrError("Missing printable bodies for cells: " + ", ".join(missing_body_ids))
    if extra_body_ids:
        raise CadIrError("Printable bodies without cells: " + ", ".join(extra_body_ids))

    modules_by_id = {module.id: module for module in config.modules}
    missing_module_ids = sorted({cell.module_id for cell in layout.cells} - set(modules_by_id))
    if missing_module_ids:
        raise CadIrError("Missing module requests for cells: " + ", ".join(missing_module_ids))

    components = tuple(
        _component_from_cell_and_body(
            cell,
            printable_by_instance[cell.instance_id],
            modules_by_id[cell.module_id],
        )
        for cell in layout.cells
    )
    volumetric_summary = build_volumetric_summary(config)
    module_candidates = build_module_candidates_from_assets(config)
    asset_candidate_variants = build_asset_candidate_variants(config)
    recommended_asset_variant = recommended_asset_candidate_variant(asset_candidate_variants)
    executable_asset_plan = build_executable_asset_module_plan(config)
    return CadScene(
        schema_version=CAD_IR_SCHEMA_VERSION,
        units=CAD_IR_UNITS,
        coordinate_system=CAD_IR_COORDINATE_SYSTEM,
        frame=CadFrame(origin=Point3D(x=0.0, y=0.0, z=0.0)),
        box_reference=CadBoxReference(
            id="box-reference",
            name="Box reference - not printable",
            origin=Point3D(x=0.0, y=0.0, z=0.0),
            size=config.box.inner_dimensions,
        ),
        parameters=_parameters_from_config(config),
        components=components,
        metadata=CadSceneMetadata(
            project_name=config.project_name,
            source_path=config.source_path,
            layout_strategy=config.layout.strategy,
            print_profile=config.print_profile,
            warnings=layout.warnings,
            assets=tuple(_asset_metadata(asset) for asset in config.assets),
            module_candidates=tuple(module_candidates),
            asset_candidate_variants=tuple(asset_candidate_variants),
            recommended_asset_candidate_variant=recommended_asset_variant,
            executable_asset_plan=executable_asset_plan,
            volumetric_grid=volumetric_summary.to_dict() if volumetric_summary is not None else None,
        ),
    )

def _component_from_cell_and_body(cell, body: PrintableBody, module: ModuleRequest) -> CadComponent:
    component_id = f"component:{cell.instance_id}"
    body_name = f"{cell.instance_id} rectangular blank"
    cad_cavities = _cad_cavities(module.cavities)
    cad_body = CadBody(
        id=body.body_id,
        name=body_name,
        kind="rectangular_blank",
        source_cell_instance_id=cell.instance_id,
        theoretical_origin=cell.origin,
        theoretical_size=cell.size,
        printable_origin=body.origin,
        printable_size=body.size,
        cavities=cad_cavities,
        face_classifications=_face_records(body.face_classifications),
        applied_tolerances=_tolerance_records(body.tolerance_applications),
        operations=(
            CadOperation(
                id=f"{body.body_id}:create_rectangular_prism",
                kind="create_rectangular_prism",
                target_id=body.body_id,
                parameters={
                    "origin_source": "printable_origin_mm",
                    "size_source": "printable_size_mm",
                    "coordinate_frame": "scene.frame",
                },
            ),
            *_cavity_operations(body.body_id, module.cavities),
        ),
    )
    return CadComponent(
        id=component_id,
        name=f"{cell.instance_id} - {cell.label}",
        module_id=cell.module_id,
        instance_id=cell.instance_id,
        functional_type=cell.functional_type.value,
        body=cad_body,
        metadata={
            "label": cell.label,
            "source_index": cell.source_index,
            "rotated": cell.rotated,
        },
    )

def _cad_cavities(cavities: tuple[Cavity, ...]) -> tuple[CadCavity, ...]:
    return tuple(
        CadCavity(
            id=cavity.id,
            functional_type=cavity.functional_type.value,
            local_origin=cavity.origin,
            size=cavity.size,
            clearance_mm=cavity.clearance_mm,
            clearance_source=cavity.clearance_source,
            comment=cavity.comment,
            features=_cad_features(cavity.features),
        )
        for cavity in cavities
    )

def _cad_features(features: tuple[Feature, ...]) -> tuple[CadFeature, ...]:
    return tuple(
        CadFeature(
            id=feature.id,
            kind=feature.kind.value,
            placement=feature.placement,
            position=feature.position,
            size=feature.size,
            radius_mm=feature.radius_mm,
            comment=feature.comment,
            status=feature.status,
            fusion_generation=feature.fusion_generation,
            taxonomy=feature_taxonomy_to_dict(feature),
        )
        for feature in features
    )

def _cavity_operations(body_id: str, cavities: tuple[Cavity, ...]) -> tuple[CadOperation, ...]:
    operations: list[CadOperation] = []
    for cavity in cavities:
        operations.append(
            CadOperation(
                id=f"{body_id}:{cavity.id}:{CAVITY_OPERATION_KIND}",
                kind=CAVITY_OPERATION_KIND,
                target_id=body_id,
                parameters={
                    "cavity_id": cavity.id,
                    "functional_type": cavity.functional_type.value,
                    "local_origin_mm": _point_to_dict(cavity.origin),
                    "size_mm": _dimension_to_dict(cavity.size),
                    "clearance_mm": cavity.clearance_mm,
                    "clearance_source": cavity.clearance_source,
                    "coordinate_frame": "body.local",
                    "execution_status": "abstract_only",
                    "fusion_generation": "not_implemented",
                },
            )
        )
        for feature in cavity.features:
            operations.append(
                CadOperation(
                    id=f"{body_id}:{cavity.id}:{feature.id}:{CAVITY_FEATURE_OPERATION_KIND}",
                    kind=CAVITY_FEATURE_OPERATION_KIND,
                    target_id=body_id,
                    parameters={
                        "cavity_id": cavity.id,
                        "feature_id": feature.id,
                        "kind": feature.kind.value,
                        "placement": feature.placement,
                        "taxonomy": feature_taxonomy_to_dict(feature),
                        "position_mm": _point_to_dict(feature.position),
                        "size_mm": _dimension_to_dict(feature.size) if feature.size is not None else None,
                        "radius_mm": feature.radius_mm,
                        "coordinate_frame": "cavity.local",
                        "execution_status": "abstract_only",
                        "fusion_generation": "not_implemented",
                    },
                )
            )
    return tuple(operations)
def _asset_metadata(asset) -> dict[str, Any]:
    return {
        "id": asset.id,
        "name": asset.name,
        "kind": asset.kind.value,
        "quantity": {
            "count": asset.quantity.count,
            "grouping": asset.quantity.grouping,
        },
        "dimensions_mm": _dimension_to_dict(asset.dimensions),
        "dimension_confidence": asset.dimension_confidence.value,
        "containment_intent": asset.containment_intent.value,
        "reservation_ref": asset.reservation_ref,
        "module_hint": asset.module_hint,
        "status": "loaded_only",
    }

def _parameters_from_config(config: InsertConfig) -> tuple[CadParameter, ...]:
    defaults = config.defaults
    tolerances = config.tolerances
    return (
        _parameter("wall_thickness_mm", defaults.wall_thickness_mm, "geometry_default", "Default wall thickness."),
        _parameter("floor_thickness_mm", defaults.floor_thickness_mm, "geometry_default", "Default floor thickness."),
        _parameter("corner_radius_mm", defaults.corner_radius_mm, "geometry_default", "Default corner radius."),
        _parameter("default_chamfer_mm", tolerances.default_chamfer_mm, "tolerance", "Default chamfer value."),
        _parameter("peripheral_clearance_mm", tolerances.peripheral_clearance_mm, "tolerance", "Box boundary clearance."),
        _parameter("module_gap_mm", tolerances.module_gap_mm, "tolerance", "Inter-module gap."),
        _parameter("vertical_lid_clearance_mm", tolerances.vertical_lid_clearance_mm, "tolerance", "Vertical lid clearance."),
        _parameter("printer_compensation_mm", tolerances.printer_compensation_mm, "tolerance", "Printer compensation."),
    )

def _parameter(id: str, value: float, category: str, description: str) -> CadParameter:
    return CadParameter(
        id=id,
        value=value,
        unit=CAD_IR_UNITS,
        category=category,
        description=description,
    )

def _face_records(classifications: tuple[FaceClassification, ...]) -> tuple[CadFaceRecord, ...]:
    return tuple(
        CadFaceRecord(
            face=classification.face.value,
            role=classification.role.value,
            reason=classification.reason,
            neighbor_instance_id=classification.neighbor_instance_id,
        )
        for classification in classifications
    )

def _tolerance_records(
    applications: tuple[FaceToleranceApplication, ...],
) -> tuple[CadToleranceRecord, ...]:
    return tuple(
        CadToleranceRecord(
            face=application.face.value,
            role=application.role.value,
            offset_mm=application.offset_mm,
            rule_id=application.rule_id,
            clearance_source=application.clearance_source,
            receives_clearance=application.receives_clearance,
            reason=application.reason,
        )
        for application in applications
    )

def _point_to_dict(point: Point3D) -> dict[str, float]:
    return {"x": point.x, "y": point.y, "z": point.z}

def _dimension_to_dict(dimension: Dimension3D) -> dict[str, float]:
    return {"x": dimension.x, "y": dimension.y, "z": dimension.z}
