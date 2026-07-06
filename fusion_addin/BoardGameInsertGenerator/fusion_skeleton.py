"""Testable helpers for the Fusion 360 adapter skeleton.

This module intentionally imports no Fusion 360 API. The add-in entry point can
use these helpers from inside Fusion, while unit tests can exercise the same
boundary checks in normal Python.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_CAD_IR_SCHEMA_VERSION = "cad_ir.v0"
SUPPORTED_UNITS = "mm"
DEFAULT_CAD_IR_INPUT_FILENAME = "cad_ir_input.json"
CAD_IR_PATH_OVERRIDE_FILENAME = "cad_ir_path.txt"
EXPLODED_VIEW_MODE_FILENAME = "exploded_view_mode.txt"

FUSION_GENERATION_MODE_COMPACT_ONLY = "compact_only"
FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED = "compact_and_exploded"
SUPPORTED_FUSION_GENERATION_MODES = (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED,
)
DEFAULT_FUSION_GENERATION_MODE = FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED

DOCUMENT_STATUS_READY = "ready"
DOCUMENT_STATUS_ZERO_DOC = "zero_doc"
ASSEMBLY_DOCUMENT_REQUIRED_STATUS = "assembly_document_required"
PART_DESIGN_SINGLE_COMPONENT_ERROR_TEXT = "Part Design documents can only contain one component"

PLAN_STATUS_PLANNED_ONLY = "planned_only"
CAVITY_CUT_OPERATION_KIND = "subtract_rectangular_cavity"
CAVITY_FEATURE_OPERATION_KIND = "describe_cavity_feature"
FINGER_NOTCH_CUT_OPERATION_KIND = "rectangular_finger_notch_cut"
GRID_PLACED_BLANK_OPERATION_KIND = "create_grid_positioned_asset_blank"
LINKED_OCCURRENCE_OPERATION_KIND = "create_linked_component_occurrence"
EXPLODED_VIEW_MARGIN_MM = 20.0
EXPLODED_VIEW_SPACING_MM = 10.0
EXPLODED_VIEW_MAX_SOLID_COUNT = 200
COMPACT_OCCURRENCE_ROLE = "compact_occurrence"
EXPLODED_OCCURRENCE_ROLE = "exploded_occurrence"
OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE = "component_source_name_with_plan_role_mapping"
SUPPORTED_SIMPLE_FINGER_NOTCH_KINDS = (
    "finger_notch",
    "side_notch",
    "center_notch",
    "half_moon_notch",
)
FINGER_NOTCH_WALL_FRONT = "front"
FINGER_NOTCH_WALL_BACK = "back"
FINGER_NOTCH_WALL_LEFT = "left"
FINGER_NOTCH_WALL_RIGHT = "right"
FUSION_SKETCH_PLANE_XZ = "xz"
FUSION_SKETCH_PLANE_YZ = "yz"
FUSION_EXTENT_POSITIVE = "positive"
FUSION_EXTENT_NEGATIVE = "negative"
FINGER_NOTCH_TOP_OPEN_OVERSHOOT_MM = 1.0
SUPPORTED_FINGER_NOTCH_PLACEMENT_WALLS = {
    "front": FINGER_NOTCH_WALL_FRONT,
    "front_center": FINGER_NOTCH_WALL_FRONT,
    "back": FINGER_NOTCH_WALL_BACK,
    "back_center": FINGER_NOTCH_WALL_BACK,
    "left": FINGER_NOTCH_WALL_LEFT,
    "left_side": FINGER_NOTCH_WALL_LEFT,
    "left_center": FINGER_NOTCH_WALL_LEFT,
    "right": FINGER_NOTCH_WALL_RIGHT,
    "right_side": FINGER_NOTCH_WALL_RIGHT,
    "right_center": FINGER_NOTCH_WALL_RIGHT,
}
FUSION_MANUAL_VALIDATION_REQUIRED = "manual_validation_required"


class FusionSkeletonError(ValueError):
    """Raised when a CAD IR payload cannot be consumed by the skeleton."""


class FusionAssemblyDocumentRequiredError(FusionSkeletonError):
    """Raised when linked occurrences require an Assembly-compatible document."""


@dataclass(frozen=True)
class FusionDocumentState:
    """Small document-state record independent from Fusion API classes."""

    status: str
    message: str
    document_name: str | None = None


@dataclass(frozen=True)
class FusionOperationPlan:
    """Non-executable plan item derived from one CAD IR operation."""

    component_id: str
    body_id: str
    operation_id: str
    operation_kind: str
    execution_status: str = PLAN_STATUS_PLANNED_ONLY
    reason: str = (
        "P4-M002 records the future Fusion operation intent only; "
        "no geometry is created."
    )

    def to_dict(self) -> dict[str, str]:
        return {
            "component_id": self.component_id,
            "body_id": self.body_id,
            "operation_id": self.operation_id,
            "operation_kind": self.operation_kind,
            "execution_status": self.execution_status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class FusionVectorMm:
    """3D vector stored in millimeters, matching the CAD IR contract."""

    x: float
    y: float
    z: float

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass(frozen=True)
class FusionSolidPlan:
    """One rectangular solid or reference outline to create in Fusion."""

    cad_id: str
    component_name: str
    body_name: str
    origin_mm: FusionVectorMm
    size_mm: FusionVectorMm
    role: str
    printable: bool
    operation_kind: str
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED
    grid_origin_units: tuple[int, int, int] | None = None
    grid_size_units: tuple[int, int, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "cad_id": self.cad_id,
            "component_name": self.component_name,
            "body_name": self.body_name,
            "origin_mm": self.origin_mm.to_dict(),
            "size_mm": self.size_mm.to_dict(),
            "role": self.role,
            "printable": self.printable,
            "operation_kind": self.operation_kind,
            "validation_status": self.validation_status,
        }
        if self.grid_origin_units is not None:
            payload["grid_origin_units"] = _grid_units_tuple_to_dict(self.grid_origin_units)
        if self.grid_size_units is not None:
            payload["grid_size_units"] = _grid_units_tuple_to_dict(self.grid_size_units)
        return payload


@dataclass(frozen=True)
class FusionOccurrencePlan:
    """One Fusion occurrence of a physical module component.

    ``occurrence_name`` is a planned report label only. The Fusion add-in must
    not assign it to ``Occurrence.name`` because some Fusion contexts expose
    occurrence names as read-only.
    """

    occurrence_name: str
    component_id: str
    source_body_id: str
    source_body_name: str
    origin_mm: FusionVectorMm
    view_role: str
    operation_kind: str = LINKED_OCCURRENCE_OPERATION_KIND
    linked_component: bool = True
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED

    def to_dict(self) -> dict[str, Any]:
        return {
            "occurrence_name": self.occurrence_name,
            "planned_occurrence_label": self.occurrence_name,
            "component_id": self.component_id,
            "source_body_id": self.source_body_id,
            "source_body_name": self.source_body_name,
            "origin_mm": self.origin_mm.to_dict(),
            "view_role": self.view_role,
            "occurrence_name_policy": OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
            "direct_occurrence_rename": False,
            "operation_kind": self.operation_kind,
            "linked_component": self.linked_component,
            "validation_status": self.validation_status,
        }


@dataclass(frozen=True)
class FusionGridModuleRejection:
    """One generated asset module refused before Fusion geometry creation."""

    module_id: str | None
    candidate_id: str | None
    code: str
    message: str
    constraint_ref: str
    actionable: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "candidate_id": self.candidate_id,
            "code": self.code,
            "message": self.message,
            "constraint_ref": self.constraint_ref,
            "actionable": self.actionable,
        }


@dataclass(frozen=True)
class FusionCavityCutPlan:
    """One top-open rectangular cavity cut to execute against a blank body."""

    component_id: str
    component_name: str
    target_body_id: str
    target_body_name: str
    operation_id: str
    cavity_id: str
    cut_origin_mm: FusionVectorMm
    cut_size_mm: FusionVectorMm
    requested_local_origin_mm: FusionVectorMm
    retained_floor_mm: float
    operation_kind: str = CAVITY_CUT_OPERATION_KIND
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "target_body_id": self.target_body_id,
            "target_body_name": self.target_body_name,
            "operation_id": self.operation_id,
            "operation_kind": self.operation_kind,
            "cavity_id": self.cavity_id,
            "cut_origin_mm": self.cut_origin_mm.to_dict(),
            "cut_size_mm": self.cut_size_mm.to_dict(),
            "requested_local_origin_mm": self.requested_local_origin_mm.to_dict(),
            "retained_floor_mm": self.retained_floor_mm,
            "validation_status": self.validation_status,
        }


@dataclass(frozen=True)
class FusionFingerNotchCutPlan:
    """One simple rectangular access notch cut to execute against a blank body."""

    component_id: str
    component_name: str
    target_body_id: str
    target_body_name: str
    operation_id: str
    cavity_id: str
    feature_id: str
    source_feature_kind: str
    placement: str
    wall: str
    sketch_plane: str
    sketch_plane_offset_mm: float
    extrude_direction: str
    cut_depth_mm: float
    top_open: bool
    notch_depth_from_top_mm: float
    profile_bottom_z_mm: float
    profile_top_z_mm: float
    top_open_overshoot_mm: float
    cut_origin_mm: FusionVectorMm
    cut_size_mm: FusionVectorMm
    profile_start_mm: FusionVectorMm
    profile_end_mm: FusionVectorMm
    cavity_local_origin_mm: FusionVectorMm
    feature_position_mm: FusionVectorMm
    operation_kind: str = FINGER_NOTCH_CUT_OPERATION_KIND
    geometry_approximation: str = "rectangular_bounding_cut"
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "target_body_id": self.target_body_id,
            "target_body_name": self.target_body_name,
            "operation_id": self.operation_id,
            "operation_kind": self.operation_kind,
            "cavity_id": self.cavity_id,
            "feature_id": self.feature_id,
            "source_feature_kind": self.source_feature_kind,
            "placement": self.placement,
            "wall": self.wall,
            "sketch_plane": self.sketch_plane,
            "sketch_plane_offset_mm": self.sketch_plane_offset_mm,
            "extrude_direction": self.extrude_direction,
            "cut_depth_mm": self.cut_depth_mm,
            "top_open": self.top_open,
            "notch_depth_from_top_mm": self.notch_depth_from_top_mm,
            "profile_bottom_z_mm": self.profile_bottom_z_mm,
            "profile_top_z_mm": self.profile_top_z_mm,
            "top_open_overshoot_mm": self.top_open_overshoot_mm,
            "cut_origin_mm": self.cut_origin_mm.to_dict(),
            "cut_size_mm": self.cut_size_mm.to_dict(),
            "profile_start_mm": self.profile_start_mm.to_dict(),
            "profile_end_mm": self.profile_end_mm.to_dict(),
            "cavity_local_origin_mm": self.cavity_local_origin_mm.to_dict(),
            "feature_position_mm": self.feature_position_mm.to_dict(),
            "geometry_approximation": self.geometry_approximation,
            "validation_status": self.validation_status,
        }


@dataclass(frozen=True)
class FusionGenerationPlan:
    """Pure-Python plan consumed by the Fusion API entry point."""

    project_name: str
    reference_box: FusionSolidPlan
    blanks: tuple[FusionSolidPlan, ...]
    grid_positioned_blanks: tuple[FusionSolidPlan, ...] = ()
    compact_occurrences: tuple[FusionOccurrencePlan, ...] = ()
    exploded_occurrences: tuple[FusionOccurrencePlan, ...] = ()
    rejected_grid_modules: tuple[FusionGridModuleRejection, ...] = ()
    cavity_cuts: tuple[FusionCavityCutPlan, ...] = ()
    finger_notch_cuts: tuple[FusionFingerNotchCutPlan, ...] = ()
    generation_mode: str = DEFAULT_FUSION_GENERATION_MODE
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED

    @property
    def module_component_count(self) -> int:
        return len(self.blanks) + len(self.grid_positioned_blanks)

    @property
    def multi_layer_grid_module_count(self) -> int:
        return sum(
            1
            for blank in self.grid_positioned_blanks
            if blank.grid_size_units is not None and blank.grid_size_units[2] > 1
        )

    @property
    def grid_modules_with_z_placement_count(self) -> int:
        return sum(
            1
            for blank in self.grid_positioned_blanks
            if (blank.grid_origin_units is not None and blank.grid_origin_units[2] > 0)
            or blank.origin_mm.z > self.reference_box.origin_mm.z
        )

    @property
    def grid_module_height_variant_count(self) -> int:
        return len({round(blank.size_mm.z, 4) for blank in self.grid_positioned_blanks})

    @property
    def linked_exploded_occurrences(self) -> bool:
        component_ids = {blank.cad_id for blank in (*self.blanks, *self.grid_positioned_blanks)}
        return all(
            occurrence.linked_component and occurrence.component_id in component_ids
            for occurrence in self.exploded_occurrences
        )

    @property
    def requires_assembly_document(self) -> bool:
        return self.module_component_count > 0

    @property
    def created_object_count(self) -> int:
        return (
            1
            + len(self.compact_occurrences)
            + len(self.exploded_occurrences)
            + len(self.cavity_cuts)
            + len(self.finger_notch_cuts)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "reference_box": self.reference_box.to_dict(),
            "blanks": [blank.to_dict() for blank in self.blanks],
            "grid_positioned_blanks": [blank.to_dict() for blank in self.grid_positioned_blanks],
            "multi_layer_grid_modules": self.multi_layer_grid_module_count,
            "grid_modules_with_z_placement": self.grid_modules_with_z_placement_count,
            "grid_module_height_variants": self.grid_module_height_variant_count,
            "compact_occurrences": [occurrence.to_dict() for occurrence in self.compact_occurrences],
            "exploded_occurrences": [occurrence.to_dict() for occurrence in self.exploded_occurrences],
            "linked_exploded_occurrences": self.linked_exploded_occurrences,
            "requires_assembly_document": self.requires_assembly_document,
            "rejected_grid_modules": [module.to_dict() for module in self.rejected_grid_modules],
            "cavity_cuts": [cut.to_dict() for cut in self.cavity_cuts],
            "finger_notch_cuts": [cut.to_dict() for cut in self.finger_notch_cuts],
            "generation_mode": self.generation_mode,
            "validation_status": self.validation_status,
        }


def _grid_units_tuple_to_dict(units: tuple[int, int, int]) -> dict[str, int]:
    return {"x": units[0], "y": units[1], "z": units[2]}


def is_part_design_component_limit_error(error: Any) -> bool:
    """Return True when Fusion reports a Part Design single-component limit."""

    return PART_DESIGN_SINGLE_COMPONENT_ERROR_TEXT in str(error)


def assembly_document_required_message(original_error: Any | None = None) -> str:
    """Build the actionable message shown when linked occurrences need Assembly."""

    lines = [
        "assembly document required",
        (
            "P7 linked occurrences use one Fusion Component per physical BGIG module, "
            "with compact and exploded Occurrence instances of that same Component."
        ),
        (
            "The active Fusion document rejected component creation. A Part Design "
            "document is not compatible with this linked compact/exploded view."
        ),
        (
            "Open or create an Assembly-compatible Fusion design, or use Fusion's "
            "'add this Part to an Assembly' workflow, then run the add-in again."
        ),
        "BGIG did not fall back to independent exploded body copies.",
    ]
    if original_error is not None:
        lines.append(f"Original Fusion error: {original_error}")
    return "\n".join(lines)


def describe_document_state(application: Any) -> FusionDocumentState:
    """Return a serializable status for Fusion's active document state.

    ``application`` is duck-typed so tests can pass small fake objects. In
    Fusion's "Zero Doc" state, ``activeDocument`` is absent or ``None``.
    """

    if application is None:
        return FusionDocumentState(
            status=DOCUMENT_STATUS_ZERO_DOC,
            message=(
                "Fusion application is unavailable. Open Fusion 360 with a "
                "design document before future generation."
            ),
        )

    active_document = getattr(application, "activeDocument", None)
    if active_document is None:
        return FusionDocumentState(
            status=DOCUMENT_STATUS_ZERO_DOC,
            message=(
                "No active Fusion document. Create or open a design document "
                "before future geometry generation."
            ),
        )

    document_name = (
        getattr(active_document, "name", None)
        or getattr(active_document, "title", None)
        or None
    )
    return FusionDocumentState(
        status=DOCUMENT_STATUS_READY,
        message=(
            "Active Fusion document detected. Fusion generation still requires "
            "manual validation."
        ),
        document_name=document_name,
    )


def resolve_cad_ir_input_path(
    addin_dir: str | Path,
    default_filename: str = DEFAULT_CAD_IR_INPUT_FILENAME,
    override_filename: str = CAD_IR_PATH_OVERRIDE_FILENAME,
) -> Path:
    """Resolve the CAD IR JSON file consumed by the add-in.

    By default the add-in loads ``cad_ir_input.json`` from its own folder. If a
    ``cad_ir_path.txt`` file exists next to the add-in, the first non-empty,
    non-comment line becomes the input path. Relative override paths are resolved
    from the add-in folder.
    """

    root = Path(addin_dir)
    override_path = root / override_filename
    default_path = root / default_filename

    if not override_path.is_file():
        return default_path

    configured_value = _first_path_value(override_path)
    if configured_value is None:
        raise FusionSkeletonError(
            f"CAD IR path override file is empty: {override_path}. "
            f"Delete it to use {default_filename!r}, or write a CAD IR JSON path."
        )

    configured_path = Path(configured_value).expanduser()
    if not configured_path.is_absolute():
        configured_path = root / configured_path
    configured_path = configured_path.resolve()

    if configured_path.is_dir():
        raise FusionSkeletonError(
            f"Configured CAD IR path points to a directory, not a JSON file: {configured_path}. "
            f"Check {override_path}."
        )
    if not configured_path.is_file():
        raise FusionSkeletonError(
            f"Configured CAD IR JSON file not found: {configured_path}. "
            f"Check {override_path}, or generate one with export-cad-ir."
        )

    return configured_path


def cad_ir_input_guidance(addin_dir: str | Path) -> str:
    """Return short user-facing guidance for Fusion CAD IR loading errors."""

    root = Path(addin_dir)
    return "\n".join(
        [
            "CAD IR input guidance:",
            f"- Default input: {root / DEFAULT_CAD_IR_INPUT_FILENAME}",
            f"- Optional path override: {root / CAD_IR_PATH_OVERRIDE_FILENAME}",
            (
                "- Override format: first non-empty line is an absolute path "
                "or a path relative to the add-in folder."
            ),
            (
                "- Generate from BGIG: python -m board_game_insert_generator "
                "export-cad-ir <config.json> --output <cad_ir_input.json>"
            ),
        ]
    )


def load_cad_ir_json(path: str | Path) -> dict[str, Any]:
    """Load and validate a serialized CAD IR payload from JSON."""

    source_path = Path(path)
    if not source_path.is_file():
        raise FusionSkeletonError(f"CAD IR JSON file not found: {source_path}.")

    try:
        raw_payload = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FusionSkeletonError(
            f"Invalid CAD IR JSON in {source_path}: {exc.msg}."
        ) from exc

    return validate_cad_ir_payload(raw_payload)


def validate_cad_ir_payload(payload: Any) -> dict[str, Any]:
    """Validate the minimum CAD IR contract consumed by the skeleton."""

    if not isinstance(payload, dict):
        raise FusionSkeletonError("CAD IR payload must be a JSON object.")

    schema_version = payload.get("schema_version")
    if schema_version != SUPPORTED_CAD_IR_SCHEMA_VERSION:
        raise FusionSkeletonError(
            "Unsupported CAD IR schema_version "
            f"{schema_version!r}; expected {SUPPORTED_CAD_IR_SCHEMA_VERSION!r}."
        )

    units = payload.get("units")
    if units != SUPPORTED_UNITS:
        raise FusionSkeletonError(
            f"Unsupported CAD IR units {units!r}; expected {SUPPORTED_UNITS!r}."
        )

    reference_payload = payload.get("box_reference")
    if not isinstance(reference_payload, dict):
        raise FusionSkeletonError("CAD IR payload must contain a box_reference object.")

    components = payload.get("components")
    if not isinstance(components, list):
        raise FusionSkeletonError("CAD IR payload must contain a components list.")
    if not components:
        raise FusionSkeletonError("CAD IR components list must contain at least one component.")
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise FusionSkeletonError(f"CAD IR components[{index}] must be an object.")

    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise FusionSkeletonError("CAD IR metadata must be an object when present.")

    return payload


def planned_operations_from_cad_ir(payload: Any) -> tuple[FusionOperationPlan, ...]:
    """Convert CAD IR operations into a non-executable Fusion plan.

    This is deliberately a planning layer only. P4-M002 must not create
    components, bodies, sketches, extrusions, or exports.
    """

    validated_payload = validate_cad_ir_payload(payload)
    planned_operations: list[FusionOperationPlan] = []

    for component in validated_payload["components"]:
        if not isinstance(component, dict):
            raise FusionSkeletonError("Each CAD IR component must be an object.")

        component_id = _required_text(component, "id", "component")
        body = component.get("body")
        if not isinstance(body, dict):
            raise FusionSkeletonError(
                f"CAD IR component {component_id!r} must contain a body object."
            )

        body_id = _required_text(body, "id", f"component {component_id} body")
        operations = body.get("operations", [])
        if not isinstance(operations, list):
            raise FusionSkeletonError(
                f"CAD IR body {body_id!r} operations must be a list."
            )

        for operation in operations:
            if not isinstance(operation, dict):
                raise FusionSkeletonError(
                    f"CAD IR body {body_id!r} operation must be an object."
                )
            planned_operations.append(
                FusionOperationPlan(
                    component_id=component_id,
                    body_id=body_id,
                    operation_id=_required_text(
                        operation,
                        "id",
                        f"body {body_id} operation",
                    ),
                    operation_kind=_required_text(
                        operation,
                        "kind",
                        f"body {body_id} operation",
                    ),
                )
            )

    return tuple(planned_operations)


def resolve_generation_mode(
    addin_dir: str | Path,
    mode_filename: str = EXPLODED_VIEW_MODE_FILENAME,
) -> str:
    """Resolve the optional local Fusion generation mode."""

    mode_path = Path(addin_dir) / mode_filename
    if not mode_path.is_file():
        return DEFAULT_FUSION_GENERATION_MODE

    configured_mode = _first_path_value(mode_path)
    if configured_mode is None:
        raise FusionSkeletonError(
            f"Fusion generation mode file is empty: {mode_path}. "
            f"Delete it or use {DEFAULT_FUSION_GENERATION_MODE!r}."
        )
    return _validated_generation_mode(configured_mode)


def generation_plan_from_cad_ir(
    payload: Any,
    generation_mode: str = DEFAULT_FUSION_GENERATION_MODE,
) -> FusionGenerationPlan:
    """Build the first executable Fusion generation plan from CAD IR.

    The plan only copies resolved CAD IR dimensions. It never computes layout,
    offsets, or tolerances.
    """

    validated_payload = validate_cad_ir_payload(payload)
    generation_mode = _validated_generation_mode(generation_mode)
    metadata = validated_payload.get("metadata", {})
    project_name = (
        metadata.get("project_name")
        if isinstance(metadata, dict) and isinstance(metadata.get("project_name"), str)
        else "BGIG CAD IR scene"
    )
    reference_payload = validated_payload.get("box_reference")
    if not isinstance(reference_payload, dict):
        raise FusionSkeletonError("CAD IR payload must contain a box_reference object.")

    reference_box = FusionSolidPlan(
        cad_id=_required_text(reference_payload, "id", "box_reference"),
        component_name=_fusion_name(
            _optional_text(reference_payload, "name")
            or "BGIG Box Reference - not printable"
        ),
        body_name=_fusion_name(
            f"{_required_text(reference_payload, 'id', 'box_reference')} outline"
        ),
        origin_mm=_vector_from_payload(reference_payload, "origin_mm", "box_reference origin"),
        size_mm=_vector_from_payload(reference_payload, "size_mm", "box_reference size"),
        role="reference_box",
        printable=False,
        operation_kind="create_reference_outline",
    )

    blanks: list[FusionSolidPlan] = []
    cavity_cuts: list[FusionCavityCutPlan] = []
    finger_notch_cuts: list[FusionFingerNotchCutPlan] = []
    for component in validated_payload["components"]:
        if not isinstance(component, dict):
            raise FusionSkeletonError("Each CAD IR component must be an object.")

        component_id = _required_text(component, "id", "component")
        component_name = _fusion_name(
            _optional_text(component, "name") or component_id
        )
        body = component.get("body")
        if not isinstance(body, dict):
            raise FusionSkeletonError(
                f"CAD IR component {component_id!r} must contain a body object."
            )

        body_kind = _required_text(body, "kind", f"component {component_id} body")
        if body_kind != "rectangular_blank":
            raise FusionSkeletonError(
                f"CAD IR body kind {body_kind!r} is not supported by current Fusion generation."
            )

        operations = body.get("operations")
        if not isinstance(operations, list) or not operations:
            raise FusionSkeletonError(
                f"CAD IR body for component {component_id!r} must contain operations."
            )
        operation = _single_rectangular_prism_operation(operations, component_id)
        body_id = _required_text(body, "id", f"component {component_id} body")
        blank = FusionSolidPlan(
            cad_id=body_id,
            component_name=component_name,
            body_name=_fusion_name(_optional_text(body, "name") or body_id),
            origin_mm=_vector_from_payload(
                body,
                "printable_origin_mm",
                f"component {component_id} printable origin",
            ),
            size_mm=_vector_from_payload(
                body,
                "printable_size_mm",
                f"component {component_id} printable size",
            ),
            role="rectangular_blank",
            printable=True,
            operation_kind=_required_text(
                operation,
                "kind",
                f"component {component_id} operation",
            ),
        )
        blanks.append(blank)
        cavity_cuts.extend(_cavity_cut_plans(component_id, component_name, blank, operations))
        finger_notch_cuts.extend(
            _finger_notch_cut_plans(component_id, component_name, blank, body, operations)
        )

    grid_positioned_blanks, rejected_grid_modules = _grid_positioned_asset_blanks_from_metadata(
        metadata if isinstance(metadata, dict) else {},
        reference_box,
        blanks,
    )
    source_blanks = [*blanks, *grid_positioned_blanks]
    compact_occurrences = _compact_occurrence_plans(source_blanks)
    exploded_occurrences = _exploded_view_occurrences(
        reference_box,
        source_blanks,
        generation_mode,
    )
    _validate_unique_body_names(source_blanks)
    _validate_unique_occurrence_names([*compact_occurrences, *exploded_occurrences])

    return FusionGenerationPlan(
        project_name=project_name,
        reference_box=reference_box,
        blanks=tuple(blanks),
        grid_positioned_blanks=tuple(grid_positioned_blanks),
        compact_occurrences=tuple(compact_occurrences),
        exploded_occurrences=tuple(exploded_occurrences),
        rejected_grid_modules=tuple(rejected_grid_modules),
        cavity_cuts=tuple(cavity_cuts),
        finger_notch_cuts=tuple(finger_notch_cuts),
        generation_mode=generation_mode,
    )



def _compact_occurrence_plans(source_blanks: list[FusionSolidPlan]) -> list[FusionOccurrencePlan]:
    return [
        _occurrence_plan_from_blank(
            source,
            origin_mm=source.origin_mm,
            view_role=COMPACT_OCCURRENCE_ROLE,
            suffix="compact occurrence",
        )
        for source in source_blanks
    ]


def _exploded_view_occurrences(
    reference_box: FusionSolidPlan,
    source_blanks: list[FusionSolidPlan],
    generation_mode: str,
) -> list[FusionOccurrencePlan]:
    if generation_mode == FUSION_GENERATION_MODE_COMPACT_ONLY:
        return []
    if generation_mode != FUSION_GENERATION_MODE_COMPACT_AND_EXPLODED:
        raise FusionSkeletonError(f"Unsupported Fusion generation mode {generation_mode!r}.")
    if len(source_blanks) > EXPLODED_VIEW_MAX_SOLID_COUNT:
        raise FusionSkeletonError(
            "Basic exploded view refuses more than "
            f"{EXPLODED_VIEW_MAX_SOLID_COUNT} rectangular bodies."
        )

    row_width_limit = max(
        reference_box.size_mm.x,
        max((blank.size_mm.x for blank in source_blanks), default=0.0),
    )
    start_x = reference_box.origin_mm.x + reference_box.size_mm.x + EXPLODED_VIEW_MARGIN_MM
    current_x = start_x
    current_y = reference_box.origin_mm.y
    row_height = 0.0
    column = 0
    exploded: list[FusionOccurrencePlan] = []

    for source in source_blanks:
        _validate_positive_solid_dimensions(source, f"exploded source {source.body_name}")
        used_width = current_x - start_x
        if column > 0 and used_width + source.size_mm.x > row_width_limit:
            column = 0
            current_x = start_x
            current_y += row_height + EXPLODED_VIEW_SPACING_MM
            row_height = 0.0

        exploded.append(
            _occurrence_plan_from_blank(
                source,
                origin_mm=FusionVectorMm(current_x, current_y, reference_box.origin_mm.z),
                view_role=EXPLODED_OCCURRENCE_ROLE,
                suffix="exploded occurrence",
            )
        )
        current_x += source.size_mm.x + EXPLODED_VIEW_SPACING_MM
        row_height = max(row_height, source.size_mm.y)
        column += 1

    return exploded


def _occurrence_plan_from_blank(
    source: FusionSolidPlan,
    origin_mm: FusionVectorMm,
    view_role: str,
    suffix: str,
) -> FusionOccurrencePlan:
    return FusionOccurrencePlan(
        occurrence_name=_fusion_name(f"{source.body_name} {suffix}"),
        component_id=source.cad_id,
        source_body_id=source.cad_id,
        source_body_name=source.body_name,
        origin_mm=origin_mm,
        view_role=view_role,
    )


def _validated_generation_mode(mode: str) -> str:
    if mode not in SUPPORTED_FUSION_GENERATION_MODES:
        raise FusionSkeletonError(
            f"Unsupported Fusion generation mode {mode!r}; expected one of "
            f"{', '.join(SUPPORTED_FUSION_GENERATION_MODES)}."
        )
    return mode


def _validate_unique_body_names(solids: list[FusionSolidPlan]) -> None:
    seen: set[str] = set()
    for solid in solids:
        if solid.body_name in seen:
            raise FusionSkeletonError(f"Fusion body name conflict: {solid.body_name!r}.")
        seen.add(solid.body_name)


def _validate_unique_occurrence_names(occurrences: list[FusionOccurrencePlan]) -> None:
    seen: set[str] = set()
    for occurrence in occurrences:
        if occurrence.occurrence_name in seen:
            raise FusionSkeletonError(
                f"Fusion occurrence name conflict: {occurrence.occurrence_name!r}."
            )
        seen.add(occurrence.occurrence_name)


def _validate_positive_solid_dimensions(solid: FusionSolidPlan, label: str) -> None:
    if solid.size_mm.x <= 0 or solid.size_mm.y <= 0 or solid.size_mm.z <= 0:
        raise FusionSkeletonError(f"CAD IR {label} dimensions must be greater than zero.")



def _grid_positioned_asset_blanks_from_metadata(
    metadata: dict[str, Any],
    reference_box: FusionSolidPlan,
    existing_blanks: list[FusionSolidPlan],
) -> tuple[list[FusionSolidPlan], list[FusionGridModuleRejection]]:
    plan = metadata.get("executable_asset_plan")
    if plan is None:
        return [], []
    if not isinstance(plan, dict):
        raise FusionSkeletonError("CAD IR metadata.executable_asset_plan must be an object when present.")

    generated_by_id = _generated_asset_modules_by_id(plan)
    rejected = _rejected_grid_modules_from_plan(plan)
    placements = plan.get("placements", [])
    if not isinstance(placements, list):
        raise FusionSkeletonError("CAD IR executable_asset_plan.placements must be a list.")

    grid_metadata = metadata.get("volumetric_grid")
    grid_size_units = _grid_size_units_from_metadata(grid_metadata) if grid_metadata is not None else None
    occupied = list(existing_blanks)
    grid_blanks: list[FusionSolidPlan] = []
    for index, placement in enumerate(placements):
        if not isinstance(placement, dict):
            raise FusionSkeletonError(f"CAD IR executable_asset_plan.placements[{index}] must be an object.")
        if placement.get("status") not in (None, "placed"):
            continue

        module_id = _required_text(placement, "module_id", f"executable_asset_plan placement[{index}]")
        candidate_id = _required_text(placement, "candidate_id", f"executable_asset_plan placement[{index}]")
        module = generated_by_id.get(module_id)
        if module is None:
            raise FusionSkeletonError(
                f"Grid placement for module {module_id!r} has no matching generated module metadata."
            )

        origin_units = _grid_units_from_payload(placement, "origin_units", f"placement {module_id} origin_units")
        size_units = _grid_units_from_payload(placement, "size_units", f"placement {module_id} size_units")
        if grid_size_units is not None:
            _validate_grid_span(origin_units, size_units, grid_size_units, module_id)

        origin_mm = _vector_from_payload(placement, "origin_mm", f"placement {module_id} origin_mm")
        size_mm = _positive_vector_from_payload(placement, "size_mm", f"placement {module_id} size_mm")
        source_size_mm = _positive_vector_from_payload(placement, "source_size_mm", f"placement {module_id} source_size_mm")
        _validate_grid_blank_bounds(reference_box, origin_mm, size_mm, module_id)
        _validate_source_size_inside_grid_size(source_size_mm, size_mm, module_id)

        blank = FusionSolidPlan(
            cad_id=_fusion_name(f"grid-placement:{module_id}"),
            component_name=_fusion_name(f"Grid placed {module.get('name') or module_id}"),
            body_name=_fusion_name(f"{module_id} grid positioned rectangular blank"),
            origin_mm=origin_mm,
            size_mm=size_mm,
            role="generated_asset_grid_blank",
            printable=True,
            operation_kind=GRID_PLACED_BLANK_OPERATION_KIND,
            grid_origin_units=origin_units,
            grid_size_units=size_units,
        )
        collision = _first_colliding_solid(blank, occupied)
        if collision is not None:
            raise FusionSkeletonError(
                f"Grid placement for module {module_id!r} collides with {collision.body_name!r}."
            )
        occupied.append(blank)
        grid_blanks.append(blank)

    return grid_blanks, rejected


def _generated_asset_modules_by_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    generated_modules = plan.get("generated_modules", [])
    if not isinstance(generated_modules, list):
        raise FusionSkeletonError("CAD IR executable_asset_plan.generated_modules must be a list.")
    modules: dict[str, dict[str, Any]] = {}
    for index, module in enumerate(generated_modules):
        if not isinstance(module, dict):
            raise FusionSkeletonError(f"CAD IR executable_asset_plan.generated_modules[{index}] must be an object.")
        module_id = _required_text(module, "module_id", f"generated module[{index}]")
        modules[module_id] = module
    return modules


def _rejected_grid_modules_from_plan(plan: dict[str, Any]) -> list[FusionGridModuleRejection]:
    rejected_payload = plan.get("rejected_modules", [])
    if not isinstance(rejected_payload, list):
        raise FusionSkeletonError("CAD IR executable_asset_plan.rejected_modules must be a list.")
    rejected: list[FusionGridModuleRejection] = []
    for index, entry in enumerate(rejected_payload):
        if not isinstance(entry, dict):
            raise FusionSkeletonError(f"CAD IR executable_asset_plan.rejected_modules[{index}] must be an object.")
        rejected.append(
            FusionGridModuleRejection(
                module_id=_optional_text(entry, "module_id"),
                candidate_id=_optional_text(entry, "candidate_id"),
                code=_required_text(entry, "code", f"rejected module[{index}]"),
                message=_required_text(entry, "message", f"rejected module[{index}]"),
                constraint_ref=_required_text(entry, "constraint_ref", f"rejected module[{index}]"),
                actionable=_required_text(entry, "actionable", f"rejected module[{index}]"),
            )
        )
    return rejected


def _grid_size_units_from_metadata(grid_metadata: Any) -> tuple[int, int, int]:
    if not isinstance(grid_metadata, dict):
        raise FusionSkeletonError("CAD IR metadata.volumetric_grid must be an object when present.")
    size_units = grid_metadata.get("size_units")
    if not isinstance(size_units, dict):
        raise FusionSkeletonError("CAD IR metadata.volumetric_grid.size_units must be an object.")
    return (
        _required_positive_int(size_units, "x", "volumetric_grid.size_units"),
        _required_positive_int(size_units, "y", "volumetric_grid.size_units"),
        _required_positive_int(size_units, "z", "volumetric_grid.size_units"),
    )


def _grid_units_from_payload(source: dict[str, Any], key: str, label: str) -> tuple[int, int, int]:
    value = source.get(key)
    if not isinstance(value, dict):
        raise FusionSkeletonError(f"CAD IR {label} must be an object.")
    return (
        _required_non_negative_int(value, "x", label),
        _required_non_negative_int(value, "y", label),
        _required_non_negative_int(value, "z", label),
    )


def _validate_grid_span(
    origin_units: tuple[int, int, int],
    size_units: tuple[int, int, int],
    grid_size_units: tuple[int, int, int],
    module_id: str,
) -> None:
    for axis_index, axis in enumerate(("x", "y", "z")):
        if size_units[axis_index] <= 0:
            raise FusionSkeletonError(f"Grid placement for module {module_id!r} has non-positive {axis} size.")
        if origin_units[axis_index] + size_units[axis_index] > grid_size_units[axis_index]:
            raise FusionSkeletonError(
                f"Grid placement for module {module_id!r} exceeds volumetric grid on {axis}."
            )


def _validate_grid_blank_bounds(
    reference_box: FusionSolidPlan,
    origin_mm: FusionVectorMm,
    size_mm: FusionVectorMm,
    module_id: str,
) -> None:
    if origin_mm.x < reference_box.origin_mm.x or origin_mm.y < reference_box.origin_mm.y or origin_mm.z < reference_box.origin_mm.z:
        raise FusionSkeletonError(f"Grid placement for module {module_id!r} starts outside the reference box.")
    if origin_mm.x + size_mm.x > reference_box.origin_mm.x + reference_box.size_mm.x:
        raise FusionSkeletonError(f"Grid placement for module {module_id!r} exceeds reference box width.")
    if origin_mm.y + size_mm.y > reference_box.origin_mm.y + reference_box.size_mm.y:
        raise FusionSkeletonError(f"Grid placement for module {module_id!r} exceeds reference box depth.")
    if origin_mm.z + size_mm.z > reference_box.origin_mm.z + reference_box.size_mm.z:
        raise FusionSkeletonError(f"Grid placement for module {module_id!r} exceeds reference box height.")


def _validate_source_size_inside_grid_size(source_size_mm: FusionVectorMm, grid_size_mm: FusionVectorMm, module_id: str) -> None:
    if source_size_mm.x > grid_size_mm.x or source_size_mm.y > grid_size_mm.y or source_size_mm.z > grid_size_mm.z:
        raise FusionSkeletonError(
            f"Grid placement for module {module_id!r} is smaller than its source module dimensions."
        )


def _first_colliding_solid(candidate: FusionSolidPlan, solids: list[FusionSolidPlan]) -> FusionSolidPlan | None:
    for solid in solids:
        if _solids_overlap(candidate, solid):
            return solid
    return None


def _solids_overlap(left: FusionSolidPlan, right: FusionSolidPlan) -> bool:
    return not (
        left.origin_mm.x + left.size_mm.x <= right.origin_mm.x
        or right.origin_mm.x + right.size_mm.x <= left.origin_mm.x
        or left.origin_mm.y + left.size_mm.y <= right.origin_mm.y
        or right.origin_mm.y + right.size_mm.y <= left.origin_mm.y
        or left.origin_mm.z + left.size_mm.z <= right.origin_mm.z
        or right.origin_mm.z + right.size_mm.z <= left.origin_mm.z
    )


def _cavity_cut_plans(
    component_id: str,
    component_name: str,
    blank: FusionSolidPlan,
    operations: list[Any],
) -> list[FusionCavityCutPlan]:
    cut_plans: list[FusionCavityCutPlan] = []
    for operation in operations:
        if not isinstance(operation, dict):
            raise FusionSkeletonError(
                f"CAD IR body {blank.cad_id!r} operation must be an object."
            )
        operation_kind = operation.get("kind")
        if operation_kind == CAVITY_FEATURE_OPERATION_KIND:
            continue
        if operation_kind != CAVITY_CUT_OPERATION_KIND:
            continue

        parameters = operation.get("parameters")
        if not isinstance(parameters, dict):
            raise FusionSkeletonError(
                f"CAD IR cavity operation for body {blank.cad_id!r} must contain parameters."
            )
        if parameters.get("coordinate_frame") != "body.local":
            raise FusionSkeletonError(
                f"CAD IR cavity operation for body {blank.cad_id!r} must use body.local coordinates."
            )

        local_origin = _vector_from_payload(
            parameters,
            "local_origin_mm",
            f"body {blank.cad_id} cavity local origin",
        )
        cavity_size = _positive_vector_from_payload(
            parameters,
            "size_mm",
            f"body {blank.cad_id} cavity size",
        )
        cavity_id = _required_text(
            parameters,
            "cavity_id",
            f"body {blank.cad_id} cavity operation",
        )
        _validate_cavity_cut_bounds(blank, local_origin, cavity_size, cavity_id)
        retained_floor_mm = blank.size_mm.z - cavity_size.z
        cut_plans.append(
            FusionCavityCutPlan(
                component_id=component_id,
                component_name=component_name,
                target_body_id=blank.cad_id,
                target_body_name=blank.body_name,
                operation_id=_required_text(
                    operation,
                    "id",
                    f"body {blank.cad_id} cavity operation",
                ),
                cavity_id=cavity_id,
                cut_origin_mm=FusionVectorMm(
                    x=blank.origin_mm.x + local_origin.x,
                    y=blank.origin_mm.y + local_origin.y,
                    z=blank.origin_mm.z + blank.size_mm.z,
                ),
                cut_size_mm=cavity_size,
                requested_local_origin_mm=local_origin,
                retained_floor_mm=retained_floor_mm,
            )
        )
    return cut_plans


def _validate_cavity_cut_bounds(
    blank: FusionSolidPlan,
    local_origin: FusionVectorMm,
    cavity_size: FusionVectorMm,
    cavity_id: str,
) -> None:
    if local_origin.x + cavity_size.x > blank.size_mm.x:
        raise FusionSkeletonError(
            f"Cavity {cavity_id!r} exceeds printable blank width for {blank.body_name!r}."
        )
    if local_origin.y + cavity_size.y > blank.size_mm.y:
        raise FusionSkeletonError(
            f"Cavity {cavity_id!r} exceeds printable blank depth for {blank.body_name!r}."
        )
    if cavity_size.z >= blank.size_mm.z:
        raise FusionSkeletonError(
            f"Cavity {cavity_id!r} depth must be lower than printable blank height for {blank.body_name!r}."
        )

    retained_floor_mm = blank.size_mm.z - cavity_size.z
    if retained_floor_mm < local_origin.z:
        raise FusionSkeletonError(
            f"Cavity {cavity_id!r} would leave {retained_floor_mm:.2f} mm of floor, "
            f"below CAD IR local_origin.z {local_origin.z:.2f} mm."
        )


def _finger_notch_cut_plans(
    component_id: str,
    component_name: str,
    blank: FusionSolidPlan,
    body: dict[str, Any],
    operations: list[Any],
) -> list[FusionFingerNotchCutPlan]:
    cavities = _cavities_by_id(body, blank.cad_id)
    cut_plans: list[FusionFingerNotchCutPlan] = []
    for operation in operations:
        if not isinstance(operation, dict):
            raise FusionSkeletonError(
                f"CAD IR body {blank.cad_id!r} operation must be an object."
            )
        if operation.get("kind") != CAVITY_FEATURE_OPERATION_KIND:
            continue

        parameters = operation.get("parameters")
        if not isinstance(parameters, dict):
            raise FusionSkeletonError(
                f"CAD IR feature operation for body {blank.cad_id!r} must contain parameters."
            )
        feature_kind = _required_text(
            parameters,
            "kind",
            f"body {blank.cad_id} cavity feature operation",
        )
        if feature_kind == "rounded_floor":
            continue
        if feature_kind not in SUPPORTED_SIMPLE_FINGER_NOTCH_KINDS:
            continue
        if parameters.get("coordinate_frame") != "cavity.local":
            raise FusionSkeletonError(
                f"CAD IR feature operation for body {blank.cad_id!r} must use cavity.local coordinates."
            )

        cavity_id = _required_text(
            parameters,
            "cavity_id",
            f"body {blank.cad_id} cavity feature operation",
        )
        cavity = cavities.get(cavity_id)
        if cavity is None:
            raise FusionSkeletonError(
                f"CAD IR feature references unknown cavity {cavity_id!r} for body {blank.cad_id!r}."
            )
        placement = _required_text(
            parameters,
            "placement",
            f"body {blank.cad_id} cavity feature operation",
        )
        wall = _wall_from_feature_placement(placement)
        if wall is None:
            raise FusionSkeletonError(
                f"Simple Fusion finger notch feature {parameters.get('feature_id')!r} uses unsupported placement {placement!r}."
            )

        feature_position = _vector_from_payload(
            parameters,
            "position_mm",
            f"body {blank.cad_id} feature position",
        )
        feature_size = _positive_vector_from_payload(
            parameters,
            "size_mm",
            f"body {blank.cad_id} feature size",
        )
        feature_id = _required_text(
            parameters,
            "feature_id",
            f"body {blank.cad_id} cavity feature operation",
        )
        cavity_origin = _vector_from_payload(
            cavity,
            "local_origin_mm",
            f"body {blank.cad_id} cavity {cavity_id} local origin",
        )
        cavity_size = _positive_vector_from_payload(
            cavity,
            "size_mm",
            f"body {blank.cad_id} cavity {cavity_id} size",
        )
        geometry = _finger_notch_cut_geometry(
            blank,
            cavity_id,
            feature_id,
            cavity_origin,
            cavity_size,
            feature_position,
            feature_size,
            wall,
        )
        cut_plans.append(
            FusionFingerNotchCutPlan(
                component_id=component_id,
                component_name=component_name,
                target_body_id=blank.cad_id,
                target_body_name=blank.body_name,
                operation_id=_required_text(
                    operation,
                    "id",
                    f"body {blank.cad_id} cavity feature operation",
                ),
                cavity_id=cavity_id,
                feature_id=feature_id,
                source_feature_kind=feature_kind,
                placement=placement,
                wall=wall,
                sketch_plane=geometry["sketch_plane"],
                sketch_plane_offset_mm=geometry["sketch_plane_offset_mm"],
                extrude_direction=geometry["extrude_direction"],
                cut_depth_mm=geometry["cut_depth_mm"],
                top_open=geometry["top_open"],
                notch_depth_from_top_mm=geometry["notch_depth_from_top_mm"],
                profile_bottom_z_mm=geometry["profile_bottom_z_mm"],
                profile_top_z_mm=geometry["profile_top_z_mm"],
                top_open_overshoot_mm=geometry["top_open_overshoot_mm"],
                cut_origin_mm=geometry["cut_origin_mm"],
                cut_size_mm=feature_size,
                profile_start_mm=geometry["profile_start_mm"],
                profile_end_mm=geometry["profile_end_mm"],
                cavity_local_origin_mm=cavity_origin,
                feature_position_mm=feature_position,
            )
        )
    return cut_plans


def _wall_from_feature_placement(placement: str) -> str | None:
    return SUPPORTED_FINGER_NOTCH_PLACEMENT_WALLS.get(placement)


def _finger_notch_cut_geometry(
    blank: FusionSolidPlan,
    cavity_id: str,
    feature_id: str,
    cavity_origin: FusionVectorMm,
    cavity_size: FusionVectorMm,
    feature_position: FusionVectorMm,
    feature_size: FusionVectorMm,
    wall: str,
) -> dict[str, Any]:
    profile_bottom_z, profile_top_z = _top_open_notch_z_range(
        blank,
        cavity_id,
        feature_id,
        cavity_origin,
        feature_size,
    )
    top_open_metadata = {
        "top_open": True,
        "notch_depth_from_top_mm": feature_size.z,
        "profile_bottom_z_mm": profile_bottom_z,
        "profile_top_z_mm": profile_top_z,
        "top_open_overshoot_mm": FINGER_NOTCH_TOP_OPEN_OVERSHOOT_MM,
    }

    if wall == FINGER_NOTCH_WALL_FRONT:
        _validate_front_or_back_finger_notch_bounds(
            blank,
            cavity_id,
            feature_id,
            cavity_origin,
            cavity_size,
            feature_position,
            feature_size,
            wall,
        )
        cut_origin = FusionVectorMm(
            x=blank.origin_mm.x + cavity_origin.x + feature_position.x,
            y=blank.origin_mm.y + cavity_origin.y - feature_size.y,
            z=profile_bottom_z,
        )
        return {
            **top_open_metadata,
            "sketch_plane": FUSION_SKETCH_PLANE_XZ,
            "sketch_plane_offset_mm": cut_origin.y,
            "extrude_direction": FUSION_EXTENT_POSITIVE,
            "cut_depth_mm": feature_size.y,
            "cut_origin_mm": cut_origin,
            "profile_start_mm": FusionVectorMm(cut_origin.x, cut_origin.y, profile_bottom_z),
            "profile_end_mm": FusionVectorMm(
                cut_origin.x + feature_size.x,
                cut_origin.y,
                profile_top_z,
            ),
        }

    if wall == FINGER_NOTCH_WALL_BACK:
        _validate_front_or_back_finger_notch_bounds(
            blank,
            cavity_id,
            feature_id,
            cavity_origin,
            cavity_size,
            feature_position,
            feature_size,
            wall,
        )
        cut_origin = FusionVectorMm(
            x=blank.origin_mm.x + cavity_origin.x + feature_position.x,
            y=blank.origin_mm.y + cavity_origin.y + cavity_size.y,
            z=profile_bottom_z,
        )
        plane_y = cut_origin.y + feature_size.y
        return {
            **top_open_metadata,
            "sketch_plane": FUSION_SKETCH_PLANE_XZ,
            "sketch_plane_offset_mm": plane_y,
            "extrude_direction": FUSION_EXTENT_NEGATIVE,
            "cut_depth_mm": feature_size.y,
            "cut_origin_mm": cut_origin,
            "profile_start_mm": FusionVectorMm(cut_origin.x, plane_y, profile_bottom_z),
            "profile_end_mm": FusionVectorMm(
                cut_origin.x + feature_size.x,
                plane_y,
                profile_top_z,
            ),
        }

    if wall == FINGER_NOTCH_WALL_LEFT:
        _validate_left_or_right_finger_notch_bounds(
            blank,
            cavity_id,
            feature_id,
            cavity_origin,
            cavity_size,
            feature_position,
            feature_size,
            wall,
        )
        cut_origin = FusionVectorMm(
            x=blank.origin_mm.x + cavity_origin.x - feature_size.x,
            y=blank.origin_mm.y + cavity_origin.y + feature_position.y,
            z=profile_bottom_z,
        )
        return {
            **top_open_metadata,
            "sketch_plane": FUSION_SKETCH_PLANE_YZ,
            "sketch_plane_offset_mm": cut_origin.x,
            "extrude_direction": FUSION_EXTENT_POSITIVE,
            "cut_depth_mm": feature_size.x,
            "cut_origin_mm": cut_origin,
            "profile_start_mm": FusionVectorMm(cut_origin.x, cut_origin.y, profile_bottom_z),
            "profile_end_mm": FusionVectorMm(
                cut_origin.x,
                cut_origin.y + feature_size.y,
                profile_top_z,
            ),
        }

    if wall == FINGER_NOTCH_WALL_RIGHT:
        _validate_left_or_right_finger_notch_bounds(
            blank,
            cavity_id,
            feature_id,
            cavity_origin,
            cavity_size,
            feature_position,
            feature_size,
            wall,
        )
        cut_origin = FusionVectorMm(
            x=blank.origin_mm.x + cavity_origin.x + cavity_size.x,
            y=blank.origin_mm.y + cavity_origin.y + feature_position.y,
            z=profile_bottom_z,
        )
        plane_x = cut_origin.x + feature_size.x
        return {
            **top_open_metadata,
            "sketch_plane": FUSION_SKETCH_PLANE_YZ,
            "sketch_plane_offset_mm": plane_x,
            "extrude_direction": FUSION_EXTENT_NEGATIVE,
            "cut_depth_mm": feature_size.x,
            "cut_origin_mm": cut_origin,
            "profile_start_mm": FusionVectorMm(plane_x, cut_origin.y, profile_bottom_z),
            "profile_end_mm": FusionVectorMm(
                plane_x,
                cut_origin.y + feature_size.y,
                profile_top_z,
            ),
        }

    raise FusionSkeletonError(f"Unsupported finger notch wall {wall!r}.")


def _top_open_notch_z_range(
    blank: FusionSolidPlan,
    cavity_id: str,
    feature_id: str,
    cavity_origin: FusionVectorMm,
    feature_size: FusionVectorMm,
) -> tuple[float, float]:
    body_top_z = blank.origin_mm.z + blank.size_mm.z
    cavity_floor_z = blank.origin_mm.z + cavity_origin.z
    profile_bottom_z = body_top_z - feature_size.z
    if profile_bottom_z < cavity_floor_z:
        raise FusionSkeletonError(
            f"Finger notch {feature_id!r} exceeds top-open depth before cavity {cavity_id!r} floor."
        )
    return profile_bottom_z, body_top_z + FINGER_NOTCH_TOP_OPEN_OVERSHOOT_MM


def _cavities_by_id(body: dict[str, Any], body_id: str) -> dict[str, dict[str, Any]]:
    cavities_payload = body.get("cavities", [])
    if not isinstance(cavities_payload, list):
        raise FusionSkeletonError(f"CAD IR body {body_id!r} cavities must be a list.")

    cavities: dict[str, dict[str, Any]] = {}
    for index, cavity in enumerate(cavities_payload):
        if not isinstance(cavity, dict):
            raise FusionSkeletonError(
                f"CAD IR body {body_id!r} cavity[{index}] must be an object."
            )
        cavity_id = _required_text(cavity, "id", f"body {body_id} cavity")
        cavities[cavity_id] = cavity
    return cavities


def _validate_front_or_back_finger_notch_bounds(
    blank: FusionSolidPlan,
    cavity_id: str,
    feature_id: str,
    cavity_origin: FusionVectorMm,
    cavity_size: FusionVectorMm,
    feature_position: FusionVectorMm,
    feature_size: FusionVectorMm,
    wall: str,
) -> None:
    if feature_position.x + feature_size.x > cavity_size.x:
        raise FusionSkeletonError(
            f"Finger notch {feature_id!r} exceeds cavity {cavity_id!r} width."
        )
    if wall == FINGER_NOTCH_WALL_FRONT:
        if not _almost_equal_mm(feature_position.y, 0):
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} for cavity {cavity_id!r} must start on the cavity front edge."
            )
        wall_thickness = cavity_origin.y
        if feature_size.y > wall_thickness:
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} exceeds the front wall thickness before cavity {cavity_id!r}."
            )
    elif wall == FINGER_NOTCH_WALL_BACK:
        if not _almost_equal_mm(feature_position.y + feature_size.y, cavity_size.y):
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} for cavity {cavity_id!r} must end on the cavity back edge."
            )
        wall_thickness = blank.size_mm.y - (cavity_origin.y + cavity_size.y)
        if feature_size.y > wall_thickness:
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} exceeds the back wall thickness after cavity {cavity_id!r}."
            )
    else:
        raise FusionSkeletonError(f"Unsupported front/back finger notch wall {wall!r}.")


def _validate_left_or_right_finger_notch_bounds(
    blank: FusionSolidPlan,
    cavity_id: str,
    feature_id: str,
    cavity_origin: FusionVectorMm,
    cavity_size: FusionVectorMm,
    feature_position: FusionVectorMm,
    feature_size: FusionVectorMm,
    wall: str,
) -> None:
    if feature_position.y + feature_size.y > cavity_size.y:
        raise FusionSkeletonError(
            f"Finger notch {feature_id!r} exceeds cavity {cavity_id!r} depth."
        )
    if wall == FINGER_NOTCH_WALL_LEFT:
        if not _almost_equal_mm(feature_position.x, 0):
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} for cavity {cavity_id!r} must start on the cavity left edge."
            )
        wall_thickness = cavity_origin.x
        if feature_size.x > wall_thickness:
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} exceeds the left wall thickness before cavity {cavity_id!r}."
            )
    elif wall == FINGER_NOTCH_WALL_RIGHT:
        if not _almost_equal_mm(feature_position.x + feature_size.x, cavity_size.x):
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} for cavity {cavity_id!r} must end on the cavity right edge."
            )
        wall_thickness = blank.size_mm.x - (cavity_origin.x + cavity_size.x)
        if feature_size.x > wall_thickness:
            raise FusionSkeletonError(
                f"Finger notch {feature_id!r} exceeds the right wall thickness after cavity {cavity_id!r}."
            )
    else:
        raise FusionSkeletonError(f"Unsupported left/right finger notch wall {wall!r}.")


def _almost_equal_mm(left: float, right: float) -> bool:
    return abs(left - right) <= 1e-9

def mm_to_cm(value_mm: float) -> float:
    """Convert CAD IR millimeters to Fusion API internal centimeters."""

    return value_mm / 10.0


def _single_rectangular_prism_operation(
    operations: list[Any],
    component_id: str,
) -> dict[str, Any]:
    rectangular_operations = [
        operation
        for operation in operations
        if isinstance(operation, dict)
        and operation.get("kind") == "create_rectangular_prism"
    ]
    if len(rectangular_operations) != 1:
        raise FusionSkeletonError(
            "Current Fusion generation expects exactly one create_rectangular_prism operation "
            f"for component {component_id!r}."
        )
    return rectangular_operations[0]


def _vector_from_payload(
    source: dict[str, Any],
    key: str,
    label: str,
) -> FusionVectorMm:
    value = source.get(key)
    if not isinstance(value, dict):
        raise FusionSkeletonError(f"CAD IR {label} must be an object.")

    return FusionVectorMm(
        x=_required_number(value, "x", label),
        y=_required_number(value, "y", label),
        z=_required_number(value, "z", label),
    )


def _positive_vector_from_payload(
    source: dict[str, Any],
    key: str,
    label: str,
) -> FusionVectorMm:
    value = source.get(key)
    if not isinstance(value, dict):
        raise FusionSkeletonError(f"CAD IR {label} must be an object.")

    return FusionVectorMm(
        x=_required_positive_number(value, "x", label),
        y=_required_positive_number(value, "y", label),
        z=_required_positive_number(value, "z", label),
    )


def _first_path_value(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            return value.strip('"')
    return None


def _required_number(source: dict[str, Any], key: str, label: str) -> float:
    value = source.get(key)
    if not isinstance(value, (int, float)):
        raise FusionSkeletonError(f"CAD IR {label} must contain numeric {key}.")
    number = float(value)
    if number < 0:
        raise FusionSkeletonError(f"CAD IR {label} {key} must be non-negative.")
    return number


def _required_non_negative_int(source: dict[str, Any], key: str, label: str) -> int:
    value = source.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise FusionSkeletonError(f"CAD IR {label} must contain integer {key}.")
    if value < 0:
        raise FusionSkeletonError(f"CAD IR {label} {key} must be non-negative.")
    return value


def _required_positive_int(source: dict[str, Any], key: str, label: str) -> int:
    value = _required_non_negative_int(source, key, label)
    if value <= 0:
        raise FusionSkeletonError(f"CAD IR {label} {key} must be greater than zero.")
    return value


def _required_positive_number(source: dict[str, Any], key: str, label: str) -> float:
    number = _required_number(source, key, label)
    if number <= 0:
        raise FusionSkeletonError(f"CAD IR {label} {key} must be greater than zero.")
    return number


def _optional_text(source: dict[str, Any], key: str) -> str | None:
    value = source.get(key)
    return value if isinstance(value, str) and value else None


def _fusion_name(value: str) -> str:
    return " ".join(value.replace(":", " - ").split())


def _required_text(source: dict[str, Any], key: str, label: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise FusionSkeletonError(f"CAD IR {label} must contain a non-empty {key}.")
    return value
