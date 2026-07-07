"""Testable helpers for the Fusion 360 adapter skeleton.

This module intentionally imports no Fusion 360 API. The add-in entry point can
use these helpers from inside Fusion, while unit tests can exercise the same
boundary checks in normal Python.
"""

from __future__ import annotations

import json
import os
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
BGIG_TOOLBAR_WORKSPACE_ID = "FusionSolidEnvironment"
BGIG_TOOLBAR_PANEL_IDS = (
    "SolidScriptsAddinsPanel",
    "SolidAddinsPanel",
    "ToolsTabAddinsPanel",
)
BGIG_TOOLBAR_LOCATION = "Design workspace > Utilities > Add-Ins"
BGIG_COMMAND_NAME = "Generate Board Game Insert"
BGIG_COMMAND_TOOLTIP = (
    "Open BGIG, choose a CAD IR or config JSON file and generate the selected Fusion scene."
)
BGIG_UI_REOPEN_POLICY = "toolbar_button_reopens_command_without_addin_restart"

FUSION_COMMAND_ACTION_GENERATE = "generate"
FUSION_COMMAND_ACTION_REGENERATE = "regenerate"
FUSION_COMMAND_ACTION_CLEAR = "clear_bgig_scene"
FUSION_COMMAND_ACTION_INSPECT = "inspect_bgig_scene"
SUPPORTED_FUSION_COMMAND_ACTIONS = (
    FUSION_COMMAND_ACTION_GENERATE,
    FUSION_COMMAND_ACTION_REGENERATE,
    FUSION_COMMAND_ACTION_CLEAR,
    FUSION_COMMAND_ACTION_INSPECT,
)
DEFAULT_FUSION_COMMAND_ACTION = FUSION_COMMAND_ACTION_GENERATE

FUSION_INPUT_MODE_CAD_IR_FILE = "cad_ir_file"
FUSION_INPUT_MODE_CONFIG_FILE = "config_file"
FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX = "quick_parametric_box"
SUPPORTED_FUSION_INPUT_MODES = (
    FUSION_INPUT_MODE_CAD_IR_FILE,
    FUSION_INPUT_MODE_CONFIG_FILE,
    FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
)
DEFAULT_FUSION_INPUT_MODE = FUSION_INPUT_MODE_CONFIG_FILE

BGIG_GENERATED_CONFIG_FILENAME = "bgig_ui_generated_config.json"
BGIG_GENERATED_CAD_IR_FILENAME = "bgig_ui_generated_cad_ir.json"
BGIG_UI_SETTINGS_FILENAME = "bgig_ui_settings.json"
BGIG_DEFAULT_DEV_PROJECT_ROOT = Path("C:/Users/janko/Documents/BGIG")
BGIG_ATTRIBUTE_GROUP = "bgig"
BGIG_LEGACY_ATTRIBUTE_GROUPS = ("BGIG",)
BGIG_ATTRIBUTE_KIND = "generated_by"
BGIG_ATTRIBUTE_ROLE_KEY = "role"
BGIG_ATTRIBUTE_SCENE_ID_KEY = "scene_id"
BGIG_ATTRIBUTE_MODULE_ID_KEY = "module_id"
BGIG_ATTRIBUTE_VERSION_KEY = "version"
BGIG_ATTRIBUTE_VERSION_VALUE = "p12-ui-m002v7"
BGIG_ATTRIBUTE_VALUE = "BoardGameInsertGenerator"
BGIG_CLEAR_SCOPE = "registry_scene_root_deleteMe_then_strict_bgig_legacy_cleanup"
BGIG_SCENE_ROOT_COMPONENT_NAME = "BGIG Generated Scene"
BGIG_SCENE_ROOT_ROLE = "scene_root"
BGIG_SCENE_OWNERSHIP_POLICY = "single_tagged_scene_root_occurrence_deleteMe"
BGIG_COMPONENT_CREATION_POLICY = "initial_addNewComponent_occurrence_is_compact"
BGIG_SOURCE_HELPER_POLICY = "source_helper_occurrences_not_used"
BGIG_VISIBLE_OCCURRENCE_POLICY = "compact_and_exploded_occurrences_only"
BGIG_GENERATE_EXISTING_SCENE_POLICY = "generate_refuses_when_bgig_scene_or_tagged_bgig_objects_exist"
BGIG_EXISTING_SCENE_MESSAGE = "BGIG scene already exists. Use regenerate or clear first."
BGIG_ACTION_GUIDANCE = (
    "generate creates one new scene only when no BGIG scene root or tagged BGIG objects exist; "
    "regenerate validates, deletes tagged BGIG scene roots with deleteMe, clears legacy BGIG tags, "
    "then creates one replacement scene; clear_bgig_scene deletes scene roots first and preserves non-BGIG objects; "
    "inspect_bgig_scene reports Fusion ownership without creating or deleting geometry."
)
BGIG_CLEARABLE_ROLES = (
    BGIG_SCENE_ROOT_ROLE,
    "scene_root_occurrence",
    "reference_outline",
    "compact_occurrence",
    "exploded_occurrence",
)
BGIG_PARAMETRIC_FIELDS_STATUS = "config_file_and_quick_parametric_box"
BGIG_QUICK_PARAMETRIC_BOX_STATUS = "enabled_generates_temporary_cad_ir_from_dialog_fields"

P12_PARAMETRIC_FIELD_DEFAULTS = {
    "box_inner_x_mm": "",
    "box_inner_y_mm": "",
    "box_inner_z_mm": "",
    "grid_units_x": "",
    "grid_units_y": "",
    "grid_units_z": "",
    "wall_thickness_mm": "",
    "floor_thickness_mm": "",
    "peripheral_clearance_mm": "",
    "inter_module_clearance_mm": "",
    "print_profile": "",
}
P12_PARAMETRIC_FIELD_LABELS = {
    "box_inner_x_mm": "Box inner X mm",
    "box_inner_y_mm": "Box inner Y mm",
    "box_inner_z_mm": "Box inner Z mm",
    "grid_units_x": "Grid units X",
    "grid_units_y": "Grid units Y",
    "grid_units_z": "Grid units Z",
    "wall_thickness_mm": "Wall thickness mm",
    "floor_thickness_mm": "Floor thickness mm",
    "peripheral_clearance_mm": "Peripheral clearance mm",
    "inter_module_clearance_mm": "Inter-module clearance mm",
    "print_profile": "Print profile",
}

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
class FusionCommandRequest:
    """User-selected add-in command values, validated outside Fusion API classes."""

    cad_ir_path: Path | None
    generation_mode: str
    action: str = DEFAULT_FUSION_COMMAND_ACTION
    input_mode: str = DEFAULT_FUSION_INPUT_MODE
    config_json_path: Path | None = None
    project_root: Path | None = None
    parameter_overrides: dict[str, Any] | None = None
    source_kind: str = "cad_ir"
    quick_parametric_status: str = BGIG_QUICK_PARAMETRIC_BOX_STATUS

    def to_dict(self) -> dict[str, Any]:
        return {
            "cad_ir_path": str(self.cad_ir_path) if self.cad_ir_path is not None else None,
            "config_json_path": str(self.config_json_path) if self.config_json_path is not None else None,
            "project_root": str(self.project_root) if self.project_root is not None else None,
            "generation_mode": self.generation_mode,
            "action": self.action,
            "input_mode": self.input_mode,
            "parameter_overrides": dict(self.parameter_overrides or {}),
            "source_kind": self.source_kind,
            "quick_parametric_status": self.quick_parametric_status,
        }

@dataclass(frozen=True)
class FusionUiLaunchPlan:
    """Testable description of the Fusion UI launch strategy."""

    command_name: str = BGIG_COMMAND_NAME
    toolbar_workspace_id: str = BGIG_TOOLBAR_WORKSPACE_ID
    toolbar_panel_ids: tuple[str, ...] = BGIG_TOOLBAR_PANEL_IDS
    toolbar_location: str = BGIG_TOOLBAR_LOCATION
    tooltip: str = BGIG_COMMAND_TOOLTIP
    reopen_policy: str = BGIG_UI_REOPEN_POLICY
    opens_dialog_on_run: bool = True
    legacy_files_are_defaults_only: bool = True
    command_actions: tuple[str, ...] = SUPPORTED_FUSION_COMMAND_ACTIONS
    input_modes: tuple[str, ...] = SUPPORTED_FUSION_INPUT_MODES
    parametric_fields: tuple[str, ...] = tuple(P12_PARAMETRIC_FIELD_DEFAULTS)
    config_input_supported: bool = True
    clear_scope: str = BGIG_CLEAR_SCOPE
    parametric_fields_status: str = BGIG_PARAMETRIC_FIELDS_STATUS
    quick_parametric_box_status: str = BGIG_QUICK_PARAMETRIC_BOX_STATUS

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_name": self.command_name,
            "toolbar_workspace_id": self.toolbar_workspace_id,
            "toolbar_panel_ids": list(self.toolbar_panel_ids),
            "toolbar_location": self.toolbar_location,
            "tooltip": self.tooltip,
            "reopen_policy": self.reopen_policy,
            "opens_dialog_on_run": self.opens_dialog_on_run,
            "legacy_files_are_defaults_only": self.legacy_files_are_defaults_only,
            "command_actions": list(self.command_actions),
            "input_modes": list(self.input_modes),
            "parametric_fields": list(self.parametric_fields),
            "config_input_supported": self.config_input_supported,
            "clear_scope": self.clear_scope,
            "parametric_fields_status": self.parametric_fields_status,
            "quick_parametric_box_status": self.quick_parametric_box_status,
        }


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
    module_source: str = "legacy_blank"
    placement_source: str = "cad_ir_component"
    source_asset_ids: tuple[str, ...] = ()
    candidate_id: str | None = None
    grid_origin_units: tuple[int, int, int] | None = None
    grid_size_units: tuple[int, int, int] | None = None
    theoretical_grid_origin_mm: FusionVectorMm | None = None
    theoretical_grid_extent_mm: FusionVectorMm | None = None
    asset_fit_size_mm: FusionVectorMm | None = None
    printable_body_size_mm: FusionVectorMm | None = None
    body_size_source: str | None = None
    clearance_applied: dict[str, Any] | None = None
    sizing_policy: str | None = None

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
            "module_source": self.module_source,
            "placement_source": self.placement_source,
            "source_asset_ids": list(self.source_asset_ids),
        }
        if self.candidate_id is not None:
            payload["candidate_id"] = self.candidate_id
        if self.grid_origin_units is not None:
            payload["grid_origin_units"] = _grid_units_tuple_to_dict(self.grid_origin_units)
        if self.grid_size_units is not None:
            payload["grid_size_units"] = _grid_units_tuple_to_dict(self.grid_size_units)
        if self.theoretical_grid_origin_mm is not None:
            payload["theoretical_grid_origin_mm"] = self.theoretical_grid_origin_mm.to_dict()
        if self.theoretical_grid_extent_mm is not None:
            payload["theoretical_grid_extent_mm"] = self.theoretical_grid_extent_mm.to_dict()
        if self.asset_fit_size_mm is not None:
            payload["asset_fit_size_mm"] = self.asset_fit_size_mm.to_dict()
        if self.printable_body_size_mm is not None:
            payload["printable_body_size_mm"] = self.printable_body_size_mm.to_dict()
        if self.body_size_source is not None:
            payload["body_size_source"] = self.body_size_source
        if self.clearance_applied is not None:
            payload["clearance_applied"] = dict(self.clearance_applied)
        if self.sizing_policy is not None:
            payload["sizing_policy"] = self.sizing_policy
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
                "- Generate from BGIG CLI: python -m board_game_insert_generator "
                "export-cad-ir <config.json> --output <cad_ir_input.json>"
            ),
            (
                "- Generate from Fusion UI: fill BGIG config JSON path and, when auto-detection "
                "does not find the repo, BGIG project root containing src/board_game_insert_generator."
            ),
        ]
    )


def build_fusion_command_request(
    cad_ir_path_text: str,
    generation_mode: str,
    addin_dir: str | Path,
    action: str = DEFAULT_FUSION_COMMAND_ACTION,
    config_json_path_text: str = "",
    project_root_text: str = "",
    parameter_values: dict[str, str] | None = None,
    input_mode: str = "",
) -> FusionCommandRequest:
    """Validate command UI values without importing Fusion API types."""

    root = Path(addin_dir)
    validated_action = _validated_command_action(action)
    validated_mode = _validated_generation_mode(generation_mode)
    validated_input_mode = _validated_input_mode(
        input_mode,
        cad_ir_path_text,
        config_json_path_text,
    )
    parameter_overrides = parse_parametric_overrides(parameter_values or {})

    if validated_action == FUSION_COMMAND_ACTION_CLEAR:
        return FusionCommandRequest(
            cad_ir_path=None,
            generation_mode=validated_mode,
            action=validated_action,
            input_mode=validated_input_mode,
            parameter_overrides=parameter_overrides,
            source_kind="clear_only",
        )
    if validated_action == FUSION_COMMAND_ACTION_INSPECT:
        return FusionCommandRequest(
            cad_ir_path=None,
            generation_mode=validated_mode,
            action=validated_action,
            input_mode=validated_input_mode,
            parameter_overrides=parameter_overrides,
            source_kind="inspect_only",
        )

    if validated_input_mode == FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX:
        return FusionCommandRequest(
            cad_ir_path=None,
            generation_mode=validated_mode,
            action=validated_action,
            input_mode=validated_input_mode,
            parameter_overrides=parameter_overrides,
            source_kind="quick_parametric_box",
        )

    if validated_input_mode == FUSION_INPUT_MODE_CONFIG_FILE:
        config_path = _resolve_optional_json_path(
            config_json_path_text,
            root,
            "BGIG config JSON",
        )
        if config_path is None:
            raise FusionSkeletonError(
                "BGIG config JSON path is required in config_file mode. "
                "Select a config file or switch Input mode to cad_ir_file."
            )
        project_root = resolve_bgig_project_root(project_root_text, config_path, root)
        return FusionCommandRequest(
            cad_ir_path=None,
            generation_mode=validated_mode,
            action=validated_action,
            input_mode=validated_input_mode,
            config_json_path=config_path,
            project_root=project_root,
            parameter_overrides=parameter_overrides,
            source_kind="config",
        )

    if parameter_overrides:
        raise FusionSkeletonError(
            "Parametric override fields are active only in config_file or quick_parametric_box mode. "
            "Switch Input mode to config_file, quick_parametric_box, or leave all override fields blank."
        )
    cad_ir_path = _resolve_optional_json_path(
        cad_ir_path_text,
        root,
        "CAD IR JSON",
    )
    if cad_ir_path is None:
        raise FusionSkeletonError(
            "CAD IR JSON path is required in cad_ir_file mode. "
            "Select a CAD IR file or switch Input mode to config_file."
        )

    return FusionCommandRequest(
        cad_ir_path=cad_ir_path,
        generation_mode=validated_mode,
        action=validated_action,
        input_mode=validated_input_mode,
        parameter_overrides=parameter_overrides,
        source_kind="cad_ir",
    )


def default_fusion_command_values(addin_dir: str | Path) -> FusionCommandRequest:
    """Return default command UI values from settings, dev auto-detection and legacy files."""

    defaults = default_fusion_ui_settings(addin_dir)
    return build_fusion_command_request(
        defaults.get("cad_ir_path", ""),
        defaults.get("generation_mode", DEFAULT_FUSION_GENERATION_MODE),
        addin_dir,
        action=defaults.get("action", DEFAULT_FUSION_COMMAND_ACTION),
        config_json_path_text=defaults.get("config_json_path", ""),
        project_root_text=defaults.get("project_root", ""),
        parameter_values={},
        input_mode=defaults.get("input_mode", DEFAULT_FUSION_INPUT_MODE),
    )


def default_fusion_ui_settings(addin_dir: str | Path) -> dict[str, str]:
    """Return UI defaults without requiring manual developer paths every run."""

    root = Path(addin_dir)
    saved = load_fusion_ui_settings(root)
    project_root = _valid_project_root_or_none(saved.get("project_root", ""))
    config_path = _valid_existing_file_or_none(saved.get("config_json_path", ""))
    cad_ir_path = _valid_existing_file_or_none(saved.get("cad_ir_path", ""))

    if project_root is None and config_path is not None:
        project_root = detect_bgig_project_root(config_path, root)
    if project_root is None:
        project_root = _env_project_root_or_none()
    if project_root is None:
        project_root = _valid_project_root_or_none(BGIG_DEFAULT_DEV_PROJECT_ROOT)

    if config_path is None and project_root is not None:
        example_path = project_root / "examples" / "simple_asset_product_scene.json"
        if example_path.is_file():
            config_path = example_path.resolve()

    if cad_ir_path is None:
        try:
            cad_ir_path = resolve_cad_ir_input_path(root)
        except FusionSkeletonError:
            cad_ir_path = root / DEFAULT_CAD_IR_INPUT_FILENAME

    try:
        generation_mode = resolve_generation_mode(root)
    except FusionSkeletonError:
        generation_mode = DEFAULT_FUSION_GENERATION_MODE

    input_mode = FUSION_INPUT_MODE_CONFIG_FILE if config_path is not None else FUSION_INPUT_MODE_CAD_IR_FILE
    return {
        "action": DEFAULT_FUSION_COMMAND_ACTION,
        "input_mode": input_mode,
        "cad_ir_path": str(cad_ir_path) if cad_ir_path is not None else "",
        "config_json_path": str(config_path) if config_path is not None else "",
        "project_root": str(project_root) if project_root is not None else "",
        "generation_mode": generation_mode,
        "settings_path": str(fusion_ui_settings_path(root)),
        "parametric_fields_status": BGIG_PARAMETRIC_FIELDS_STATUS,
        "quick_parametric_box_status": BGIG_QUICK_PARAMETRIC_BOX_STATUS,
    }


def fusion_ui_settings_path(addin_dir: str | Path) -> Path:
    return Path(addin_dir) / BGIG_UI_SETTINGS_FILENAME


def load_fusion_ui_settings(addin_dir: str | Path) -> dict[str, str]:
    path = fusion_ui_settings_path(addin_dir)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items() if value is not None}


def fusion_command_summary(request: FusionCommandRequest) -> str:
    """Return the short read-only summary displayed by the Fusion command."""

    source = "CAD IR JSON"
    source_path = request.cad_ir_path
    if request.source_kind == "config":
        source = "BGIG config JSON"
        source_path = request.config_json_path
    elif request.source_kind == "clear_only":
        source = "Clear tagged BGIG scene objects"
        source_path = None
    elif request.source_kind == "inspect_only":
        source = "Inspect BGIG scene ownership"
        source_path = None
    elif request.source_kind == "quick_parametric_box":
        source = "Quick parametric box UI fields"
        source_path = None

    overrides = request.parameter_overrides or {}
    override_summary = ", ".join(sorted(overrides)) if overrides else "none"
    return "\n".join(
        [
            "BGIG command UI V0 uses explicit input modes: cad_ir_file, config_file, quick_parametric_box.",
            f"Action: {request.action}",
            f"Input mode: {request.input_mode}",
            f"Source: {source}",
            f"Source path: {source_path if source_path is not None else 'n/a'}",
            f"Project root: {request.project_root if request.project_root is not None else 'auto/not required'}",
            f"Generation mode: {request.generation_mode}",
            f"Parametric overrides: {override_summary}",
            f"Parametric fields status: {BGIG_PARAMETRIC_FIELDS_STATUS}",
            f"Quick parametric box: {BGIG_QUICK_PARAMETRIC_BOX_STATUS}",
            f"Clear scope: {BGIG_CLEAR_SCOPE}",
            f"Generate existing scene policy: {BGIG_GENERATE_EXISTING_SCENE_POLICY}",
            f"Component creation policy: {BGIG_COMPONENT_CREATION_POLICY}",
            f"Source/helper policy: {BGIG_SOURCE_HELPER_POLICY}",
            f"Scene ownership policy: {BGIG_SCENE_OWNERSHIP_POLICY}",
            f"Visible occurrence policy: {BGIG_VISIBLE_OCCURRENCE_POLICY}",
            f"Action guidance: {BGIG_ACTION_GUIDANCE}",
            "Fusion will not recalculate layout, clearances or tolerances.",
        ]
    )

def parse_parametric_overrides(values: dict[str, str]) -> dict[str, Any]:
    """Parse optional P12 UI fields into config override values."""

    overrides: dict[str, Any] = {}
    for key, raw_value in values.items():
        if key not in P12_PARAMETRIC_FIELD_DEFAULTS:
            raise FusionSkeletonError(f"Unsupported P12 UI parameter {key!r}.")
        value = str(raw_value).strip()
        if not value:
            continue
        if key == "print_profile":
            overrides[key] = value
        elif key.startswith("grid_units_"):
            overrides[key] = _parse_positive_int(value, key)
        elif key in {"peripheral_clearance_mm", "inter_module_clearance_mm"}:
            overrides[key] = _parse_non_negative_float(value, key)
        else:
            overrides[key] = _parse_positive_float(value, key)
    return overrides


def apply_parametric_overrides_to_config_payload(
    payload: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Return a copied BGIG config payload with P12 UI overrides applied."""

    if not isinstance(payload, dict):
        raise FusionSkeletonError("BGIG config payload must be a JSON object.")
    updated = json.loads(json.dumps(payload))
    if not overrides:
        return updated

    if "print_profile" in overrides:
        updated["print_profile"] = overrides["print_profile"]

    box_dimension_keys = {
        "box_inner_x_mm": "x",
        "box_inner_y_mm": "y",
        "box_inner_z_mm": "z",
    }
    if any(key in overrides for key in box_dimension_keys):
        box = _ensure_config_object(updated, "box")
        inner = _ensure_config_object(box, "inner_dimensions_mm")
        for override_key, axis in box_dimension_keys.items():
            if override_key in overrides:
                inner[axis] = overrides[override_key]

    grid_unit_keys = {
        "grid_units_x": "x",
        "grid_units_y": "y",
        "grid_units_z": "z",
    }
    if any(key in overrides for key in grid_unit_keys):
        grid = updated.get("volumetric_grid")
        if not isinstance(grid, dict):
            raise FusionSkeletonError("Grid unit overrides require config.volumetric_grid.")
        size_units = _ensure_config_object(grid, "size_units")
        for override_key, axis in grid_unit_keys.items():
            if override_key in overrides:
                size_units[axis] = overrides[override_key]

    default_keys = {
        "wall_thickness_mm": "wall_thickness_mm",
        "floor_thickness_mm": "floor_thickness_mm",
    }
    if any(key in overrides for key in default_keys):
        defaults = _ensure_config_object(updated, "defaults")
        for override_key, config_key in default_keys.items():
            if override_key in overrides:
                defaults[config_key] = overrides[override_key]

    tolerance_keys = {
        "peripheral_clearance_mm": "peripheral_clearance_mm",
        "inter_module_clearance_mm": "module_gap_mm",
    }
    if any(key in overrides for key in tolerance_keys):
        tolerances = _ensure_config_object(updated, "tolerances")
        for override_key, config_key in tolerance_keys.items():
            if override_key in overrides:
                tolerances[config_key] = overrides[override_key]

    return updated


def build_quick_parametric_box_cad_ir_payload(overrides: dict[str, Any]) -> dict[str, Any]:
    """Build a minimal CAD IR scene directly from quick_parametric_box UI fields."""

    required = (
        "box_inner_x_mm",
        "box_inner_y_mm",
        "box_inner_z_mm",
        "grid_units_x",
        "grid_units_y",
        "grid_units_z",
        "wall_thickness_mm",
        "floor_thickness_mm",
        "peripheral_clearance_mm",
        "inter_module_clearance_mm",
    )
    missing = [field for field in required if field not in overrides]
    if missing:
        raise FusionSkeletonError(
            "quick_parametric_box requires these filled fields: " + ", ".join(missing) + "."
        )
    print_profile = str(overrides.get("print_profile") or "default").strip() or "default"
    box_x = float(overrides["box_inner_x_mm"])
    box_y = float(overrides["box_inner_y_mm"])
    box_z = float(overrides["box_inner_z_mm"])
    grid_x = int(overrides["grid_units_x"])
    grid_y = int(overrides["grid_units_y"])
    grid_z = int(overrides["grid_units_z"])
    wall = float(overrides["wall_thickness_mm"])
    floor = float(overrides["floor_thickness_mm"])
    peripheral = float(overrides["peripheral_clearance_mm"])
    inter_module = float(overrides["inter_module_clearance_mm"])
    cell_x = round(box_x / grid_x, 4)
    cell_y = round(box_y / grid_y, 4)
    cell_z = round(box_z / grid_z, 4)
    printable_x = _quick_printable_dimension(cell_x, peripheral, inter_module, "X")
    printable_y = _quick_printable_dimension(cell_y, peripheral, inter_module, "Y")
    printable_z = _quick_printable_height(cell_z, floor)
    asset_fit_x = max(round(printable_x - (2 * wall), 4), 0.1)
    asset_fit_y = max(round(printable_y - (2 * wall), 4), 0.1)
    asset_fit_z = max(round(printable_z - floor, 4), 0.1)
    clearances = {
        "peripheral_clearance_mm": peripheral,
        "inter_module_gap_mm": inter_module,
        "wall_thickness_mm": wall,
        "floor_thickness_mm": floor,
        "note": "quick_parametric_box V0 creates one printable module from one grid cell; Fusion consumes this CAD IR without recalculating layout or tolerances.",
    }
    return {
        "schema_version": SUPPORTED_CAD_IR_SCHEMA_VERSION,
        "units": SUPPORTED_UNITS,
        "coordinate_system": "right_handed_z_up_mm",
        "frame": {"origin_mm": _vector_payload(0.0, 0.0, 0.0)},
        "box_reference": {
            "id": "quick-parametric-box-reference",
            "name": "Quick parametric box reference - not printable",
            "origin_mm": _vector_payload(0.0, 0.0, 0.0),
            "size_mm": _vector_payload(box_x, box_y, box_z),
            "printable": False,
        },
        "parameters": [
            _parameter_payload("box_inner_x_mm", box_x, "ui", "Quick box inner X."),
            _parameter_payload("box_inner_y_mm", box_y, "ui", "Quick box inner Y."),
            _parameter_payload("box_inner_z_mm", box_z, "ui", "Quick box inner Z."),
            _parameter_payload("grid_units_x", grid_x, "ui", "Quick grid X units."),
            _parameter_payload("grid_units_y", grid_y, "ui", "Quick grid Y units."),
            _parameter_payload("grid_units_z", grid_z, "ui", "Quick grid Z units."),
            _parameter_payload("wall_thickness_mm", wall, "ui", "Quick wall thickness."),
            _parameter_payload("floor_thickness_mm", floor, "ui", "Quick floor thickness."),
            _parameter_payload("peripheral_clearance_mm", peripheral, "ui", "Quick peripheral clearance."),
            _parameter_payload("inter_module_clearance_mm", inter_module, "ui", "Quick inter-module clearance."),
        ],
        "components": [
            {
                "id": "component:quick-parametric-module",
                "name": "Quick parametric module",
                "module_id": "quick-parametric-module",
                "instance_id": "quick-parametric-module-01",
                "functional_type": "quick_parametric_box",
                "body": {
                    "id": "body:quick-parametric-module",
                    "name": "Quick parametric module body",
                    "kind": "rectangular_blank",
                    "theoretical_origin_mm": _vector_payload(0.0, 0.0, 0.0),
                    "theoretical_size_mm": _vector_payload(cell_x, cell_y, cell_z),
                    "printable_origin_mm": _vector_payload(peripheral, peripheral, 0.0),
                    "printable_size_mm": _vector_payload(printable_x, printable_y, printable_z),
                    "clearance_applied": clearances,
                    "operations": [
                        {
                            "id": "operation:create-quick-parametric-module",
                            "kind": "create_rectangular_prism",
                            "parameters": {
                                "source": "quick_parametric_box",
                                "theoretical_grid_extent_mm": _vector_payload(cell_x, cell_y, cell_z),
                                "printable_body_size_mm": _vector_payload(printable_x, printable_y, printable_z),
                            },
                        }
                    ],
                },
                "metadata": {
                    "source": "quick_parametric_box",
                    "print_profile": print_profile,
                    "grid_origin_units": _grid_units_tuple_to_dict((0, 0, 0)),
                    "grid_size_units": _grid_units_tuple_to_dict((1, 1, 1)),
                    "theoretical_grid_extent_mm": _vector_payload(cell_x, cell_y, cell_z),
                    "asset_fit_size_mm": _vector_payload(asset_fit_x, asset_fit_y, asset_fit_z),
                    "printable_body_size_mm": _vector_payload(printable_x, printable_y, printable_z),
                    "clearance_applied": clearances,
                },
            }
        ],
        "metadata": {
            "project_name": "Quick parametric box",
            "source": "quick_parametric_box",
            "print_profile": print_profile,
            "quick_parametric_box": {
                "box_inner_mm": _vector_payload(box_x, box_y, box_z),
                "grid_units": _grid_units_tuple_to_dict((grid_x, grid_y, grid_z)),
                "grid_unit_mm": _vector_payload(cell_x, cell_y, cell_z),
                "wall_thickness_mm": wall,
                "floor_thickness_mm": floor,
                "peripheral_clearance_mm": peripheral,
                "inter_module_clearance_mm": inter_module,
                "theoretical_grid_extent_mm": _vector_payload(cell_x, cell_y, cell_z),
                "asset_fit_size_mm": _vector_payload(asset_fit_x, asset_fit_y, asset_fit_z),
                "printable_body_size_mm": _vector_payload(printable_x, printable_y, printable_z),
                "generation_scope": "one_module_one_grid_cell_v0",
                "print_validation": False,
            },
            "warnings": [
                "quick_parametric_box V0 creates one simple rectangular module for Fusion smoke testing.",
                "No physical print validation is implied.",
            ],
        },
    }


def quick_parametric_box_summary(payload: dict[str, Any] | None) -> str:
    """Return concise report lines for a quick_parametric_box CAD IR payload."""

    if not isinstance(payload, dict):
        return "Quick parametric box: n/a\n"
    metadata = payload.get("metadata")
    quick = metadata.get("quick_parametric_box") if isinstance(metadata, dict) else None
    if not isinstance(quick, dict):
        return "Quick parametric box: n/a\n"
    return "".join(
        [
            "Quick parametric box inputs:\n",
            f"- box_inner_mm: {_format_vector_payload(quick.get('box_inner_mm'))}\n",
            f"- grid_units: {_format_grid_units_payload(quick.get('grid_units'))}\n",
            f"- grid_unit_mm: {_format_vector_payload(quick.get('grid_unit_mm'))}\n",
            f"- wall_thickness_mm: {quick.get('wall_thickness_mm')}\n",
            f"- floor_thickness_mm: {quick.get('floor_thickness_mm')}\n",
            f"- peripheral_clearance_mm: {quick.get('peripheral_clearance_mm')}\n",
            f"- inter_module_clearance_mm: {quick.get('inter_module_clearance_mm')}\n",
            f"- print_profile: {metadata.get('print_profile', 'default') if isinstance(metadata, dict) else 'default'}\n",
            f"- theoretical_grid_extent_mm: {_format_vector_payload(quick.get('theoretical_grid_extent_mm'))}\n",
            f"- printable_body_size_mm: {_format_vector_payload(quick.get('printable_body_size_mm'))}\n",
            "- temporary_cad_ir_created: yes\n",
        ]
    )


def _quick_printable_dimension(cell_size_mm: float, peripheral_clearance_mm: float, inter_module_clearance_mm: float, axis: str) -> float:
    printable = cell_size_mm - (2 * peripheral_clearance_mm) - inter_module_clearance_mm
    if printable <= 0:
        raise FusionSkeletonError(
            f"quick_parametric_box {axis} printable size must remain positive after peripheral and inter-module clearances."
        )
    return round(printable, 4)


def _quick_printable_height(cell_size_mm: float, floor_thickness_mm: float) -> float:
    printable = cell_size_mm - floor_thickness_mm
    if printable <= 0:
        raise FusionSkeletonError(
            "quick_parametric_box Z printable size must remain positive after floor thickness."
        )
    return round(printable, 4)


def _vector_payload(x: float, y: float, z: float) -> dict[str, float]:
    return {"x": round(float(x), 4), "y": round(float(y), 4), "z": round(float(z), 4)}


def _parameter_payload(name: str, value: float | int, source: str, description: str) -> dict[str, Any]:
    return {"name": name, "value": value, "source": source, "description": description}


def _format_vector_payload(value: Any) -> str:
    if not isinstance(value, dict):
        return "n/a"
    return f"{value.get('x')} x {value.get('y')} x {value.get('z')} mm"


def _format_grid_units_payload(value: Any) -> str:
    if not isinstance(value, dict):
        return "n/a"
    return f"{value.get('x')} x {value.get('y')} x {value.get('z')}"
def resolve_bgig_project_root(
    project_root_text: str,
    config_path: Path,
    addin_dir: str | Path,
) -> Path:
    """Resolve the project root used to import the pure BGIG engine from Fusion."""

    explicit_root = _path_text_or_none(project_root_text)
    if explicit_root is not None:
        if not explicit_root.is_absolute():
            explicit_root = Path(addin_dir) / explicit_root
        return _validated_bgig_project_root(explicit_root.resolve())

    environment_root = _env_project_root_or_none()
    if environment_root is not None:
        return environment_root

    detected = detect_bgig_project_root(config_path, addin_dir)
    if detected is None:
        raise FusionSkeletonError(
            "BGIG project root could not be auto-detected. "
            "Set BGIG_PROJECT_ROOT or use the advanced UI field with the repo folder "
            "containing src/board_game_insert_generator."
        )
    return detected


def detect_bgig_project_root(config_path: Path, addin_dir: str | Path) -> Path | None:
    """Find a repo root containing src/board_game_insert_generator."""

    candidates: list[Path] = []
    env_root = _env_project_root_or_none()
    if env_root is not None:
        candidates.append(env_root)
    candidates.extend([config_path, Path(addin_dir), BGIG_DEFAULT_DEV_PROJECT_ROOT])
    for candidate in candidates:
        for parent in [candidate, *candidate.parents]:
            valid = _valid_project_root_or_none(parent)
            if valid is not None:
                return valid
    return None


def _env_project_root_or_none() -> Path | None:
    return _valid_project_root_or_none(os.environ.get("BGIG_PROJECT_ROOT", ""))


def _valid_project_root_or_none(value: str | Path) -> Path | None:
    if value is None:
        return None
    try:
        path = Path(value).expanduser()
    except TypeError:
        return None
    if not str(path).strip():
        return None
    try:
        resolved = path.resolve()
    except OSError:
        return None
    src_dir = resolved / "src" / "board_game_insert_generator"
    return resolved if src_dir.is_dir() else None


def _valid_existing_file_or_none(value: str | Path) -> Path | None:
    if value is None:
        return None
    try:
        path = Path(value).expanduser()
    except TypeError:
        return None
    if not str(path).strip():
        return None
    try:
        resolved = path.resolve()
    except OSError:
        return None
    return resolved if resolved.is_file() else None


def _path_text_or_none(value: str) -> Path | None:
    raw = str(value or "").strip().strip('"')
    return Path(raw).expanduser() if raw else None

def _resolve_optional_json_path(path_text: str, addin_dir: Path, label: str) -> Path | None:
    raw_path = path_text.strip().strip('"')
    if not raw_path:
        return None
    configured_path = Path(raw_path).expanduser()
    if not configured_path.is_absolute():
        configured_path = addin_dir / configured_path
    configured_path = configured_path.resolve()
    if configured_path.is_dir():
        raise FusionSkeletonError(f"{label} path points to a directory, not a JSON file: {configured_path}.")
    if not configured_path.is_file():
        raise FusionSkeletonError(f"{label} file not found: {configured_path}.")
    return configured_path


def _validated_bgig_project_root(project_root: Path) -> Path:
    src_dir = project_root / "src" / "board_game_insert_generator"
    if not src_dir.is_dir():
        raise FusionSkeletonError(
            f"BGIG project root must contain src/board_game_insert_generator: {project_root}."
        )
    return project_root


def _ensure_config_object(source: dict[str, Any], key: str) -> dict[str, Any]:
    value = source.get(key)
    if value is None:
        value = {}
        source[key] = value
    if not isinstance(value, dict):
        raise FusionSkeletonError(f"BGIG config field {key!r} must be an object before applying UI overrides.")
    return value


def _parse_positive_float(value: str, field_name: str) -> float:
    parsed = _parse_float(value, field_name)
    if parsed <= 0:
        raise FusionSkeletonError(f"P12 UI parameter {field_name} must be greater than zero.")
    return parsed


def _parse_non_negative_float(value: str, field_name: str) -> float:
    parsed = _parse_float(value, field_name)
    if parsed < 0:
        raise FusionSkeletonError(f"P12 UI parameter {field_name} must be non-negative.")
    return parsed


def _parse_float(value: str, field_name: str) -> float:
    try:
        return float(value.replace(",", "."))
    except ValueError as exc:
        raise FusionSkeletonError(f"P12 UI parameter {field_name} must be numeric.") from exc


def _parse_positive_int(value: str, field_name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise FusionSkeletonError(f"P12 UI parameter {field_name} must be an integer.") from exc
    if parsed <= 0:
        raise FusionSkeletonError(f"P12 UI parameter {field_name} must be greater than zero.")
    return parsed


def _validated_command_action(action: str) -> str:
    if action not in SUPPORTED_FUSION_COMMAND_ACTIONS:
        raise FusionSkeletonError(f"Unsupported Fusion command action {action!r}.")
    return action

def _validated_input_mode(input_mode: str, cad_ir_path_text: str, config_json_path_text: str) -> str:
    requested = str(input_mode or "").strip()
    if not requested:
        requested = (
            FUSION_INPUT_MODE_CONFIG_FILE
            if str(config_json_path_text or "").strip()
            else FUSION_INPUT_MODE_CAD_IR_FILE
        )
    if requested not in SUPPORTED_FUSION_INPUT_MODES:
        raise FusionSkeletonError(f"Unsupported Fusion input mode {requested!r}.")
    return requested

def fusion_ui_launch_plan() -> FusionUiLaunchPlan:
    """Return the supported P12 launch strategy for the Fusion add-in UI."""

    return FusionUiLaunchPlan()


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

    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise FusionSkeletonError("CAD IR metadata must be an object when present.")
    if not components and not _metadata_has_executable_asset_placements(metadata):
        raise FusionSkeletonError(
            "CAD IR components list must contain at least one component unless "
            "metadata.executable_asset_plan.placements provides generated asset modules."
        )
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise FusionSkeletonError(f"CAD IR components[{index}] must be an object.")

    return payload


def _metadata_has_executable_asset_placements(metadata: Any) -> bool:
    if not isinstance(metadata, dict):
        return False
    plan = metadata.get("executable_asset_plan")
    if not isinstance(plan, dict):
        return False
    placements = plan.get("placements")
    return isinstance(placements, list) and len(placements) > 0

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
            module_source="legacy_blank",
            placement_source="cad_ir_component",
            clearance_applied=_clearance_summary_from_cad_body(body),
            body_size_source="printable_size_mm",
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

        legacy_origin_mm = _vector_from_payload(placement, "origin_mm", f"placement {module_id} origin_mm")
        legacy_size_mm = _positive_vector_from_payload(placement, "size_mm", f"placement {module_id} size_mm")
        theoretical_grid_origin_mm = _optional_vector_from_payload(
            placement,
            "theoretical_grid_origin_mm",
            f"placement {module_id} theoretical_grid_origin_mm",
        ) or legacy_origin_mm
        theoretical_grid_extent_mm = _optional_positive_vector_from_payload(
            placement,
            "theoretical_grid_extent_mm",
            f"placement {module_id} theoretical_grid_extent_mm",
        ) or legacy_size_mm
        source_size_mm = _optional_positive_vector_from_payload(
            placement,
            "source_size_mm",
            f"placement {module_id} source_size_mm",
        ) or _positive_vector_from_payload(module, "dimensions_mm", f"generated module {module_id} dimensions_mm")
        asset_fit_size_mm = _optional_positive_vector_from_payload(
            placement,
            "asset_fit_size_mm",
            f"placement {module_id} asset_fit_size_mm",
        ) or _optional_positive_vector_from_payload(
            module,
            "asset_fit_size_mm",
            f"generated module {module_id} asset_fit_size_mm",
        )
        printable_body_origin_mm = _optional_vector_from_payload(
            placement,
            "printable_body_origin_mm",
            f"placement {module_id} printable_body_origin_mm",
        ) or legacy_origin_mm
        printable_body_size_mm = _optional_positive_vector_from_payload(
            placement,
            "printable_body_size_mm",
            f"placement {module_id} printable_body_size_mm",
        ) or _optional_positive_vector_from_payload(
            module,
            "printable_body_size_mm",
            f"generated module {module_id} printable_body_size_mm",
        )
        if printable_body_size_mm is None:
            if "theoretical_grid_extent_mm" in placement or "theoretical_grid_origin_mm" in placement:
                raise FusionSkeletonError(
                    f"Grid placement for module {module_id!r} declares a theoretical grid span but "
                    "does not provide printable_body_size_mm; refusing to size a Fusion body from "
                    "the grid span."
                )
            printable_body_size_mm = source_size_mm
            body_size_source = "legacy_source_size_mm"
        else:
            body_size_source = "printable_body_size_mm"
        _validate_grid_blank_bounds(reference_box, theoretical_grid_origin_mm, theoretical_grid_extent_mm, module_id)
        _validate_grid_blank_bounds(reference_box, printable_body_origin_mm, printable_body_size_mm, module_id)
        _validate_size_inside_size(source_size_mm, theoretical_grid_extent_mm, module_id, "source module", "grid span")
        _validate_size_inside_size(printable_body_size_mm, theoretical_grid_extent_mm, module_id, "printable body", "grid span")
        if asset_fit_size_mm is not None:
            _validate_size_inside_size(asset_fit_size_mm, printable_body_size_mm, module_id, "asset-fit envelope", "printable body")

        source_asset_ids = _text_list(module.get("source_asset_ids", []), f"generated module {module_id} source_asset_ids")
        blank = FusionSolidPlan(
            cad_id=_fusion_name(f"grid-placement:{module_id}"),
            component_name=_fusion_name(f"Grid placed {module.get('name') or module_id}"),
            body_name=_fusion_name(f"{module_id} grid positioned rectangular blank"),
            origin_mm=printable_body_origin_mm,
            size_mm=printable_body_size_mm,
            role="generated_asset_grid_blank",
            printable=True,
            operation_kind=GRID_PLACED_BLANK_OPERATION_KIND,
            grid_origin_units=origin_units,
            grid_size_units=size_units,
            theoretical_grid_origin_mm=theoretical_grid_origin_mm,
            theoretical_grid_extent_mm=theoretical_grid_extent_mm,
            asset_fit_size_mm=asset_fit_size_mm,
            printable_body_size_mm=printable_body_size_mm,
            body_size_source=body_size_source,
            module_source="asset_candidate",
            placement_source="grid_placement",
            source_asset_ids=tuple(source_asset_ids),
            candidate_id=candidate_id,
            clearance_applied=placement.get("clearance_applied") if isinstance(placement.get("clearance_applied"), dict) else None,
            sizing_policy=_optional_text(placement, "sizing_policy"),
        )
        collision = _first_colliding_solid(blank, occupied)
        if collision is not None:
            raise FusionSkeletonError(
                f"Grid placement for module {module_id!r} collides with {collision.body_name!r}."
            )
        occupied.append(blank)
        grid_blanks.append(blank)

    return grid_blanks, rejected


def _clearance_summary_from_cad_body(body: dict[str, Any]) -> dict[str, Any] | None:
    applied_tolerances = body.get("applied_tolerances", [])
    if not isinstance(applied_tolerances, list):
        return None
    return {
        "peripheral_clearance_mm": _max_tolerance_offset_for_role(applied_tolerances, "peripheral"),
        "inter_module_gap_mm": _max_tolerance_offset_for_role(applied_tolerances, "neighbor"),
        "source": "cad_ir.applied_tolerances",
    }


def _max_tolerance_offset_for_role(applied_tolerances: list[Any], role: str) -> float:
    offsets: list[float] = []
    for entry in applied_tolerances:
        if not isinstance(entry, dict) or entry.get("role") != role:
            continue
        try:
            offsets.append(abs(float(entry.get("offset_mm", 0.0))))
        except (TypeError, ValueError):
            continue
    return round(max(offsets, default=0.0), 4)


def _text_list(value: Any, field_path: str) -> list[str]:
    if not isinstance(value, list):
        raise FusionSkeletonError(f"CAD IR {field_path} must be a list.")
    texts: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            raise FusionSkeletonError(f"CAD IR {field_path}[{index}] must be a non-empty string.")
        texts.append(item)
    return texts

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
    _validate_size_inside_size(source_size_mm, grid_size_mm, module_id, "source module", "grid span")


def _validate_size_inside_size(
    inner_size_mm: FusionVectorMm,
    outer_size_mm: FusionVectorMm,
    module_id: str,
    inner_label: str,
    outer_label: str,
) -> None:
    if (
        inner_size_mm.x > outer_size_mm.x
        or inner_size_mm.y > outer_size_mm.y
        or inner_size_mm.z > outer_size_mm.z
    ):
        raise FusionSkeletonError(
            f"Grid placement for module {module_id!r} has {inner_label} larger than its {outer_label}."
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


def _optional_vector_from_payload(
    source: dict[str, Any],
    key: str,
    label: str,
) -> FusionVectorMm | None:
    value = source.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise FusionSkeletonError(f"CAD IR {label} must be an object.")
    return FusionVectorMm(
        x=_required_number(value, "x", label),
        y=_required_number(value, "y", label),
        z=_required_number(value, "z", label),
    )


def _optional_positive_vector_from_payload(
    source: dict[str, Any],
    key: str,
    label: str,
) -> FusionVectorMm | None:
    value = source.get(key)
    if value is None:
        return None
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
