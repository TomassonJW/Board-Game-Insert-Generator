"""Fusion 360 add-in entry point for Board Game Insert Generator.

P7-M001 creates one Fusion component per physical BGIG module, then places
linked compact and exploded occurrences of that component from a serialized CAD
IR. Fusion consumes already resolved CAD IR dimensions and must not recalculate
layout, cavities, clearances, placements, or tolerances.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from dataclasses import replace
from pathlib import Path

try:
    from .fusion_skeleton import (
        BGIG_ATTRIBUTE_GROUP,
        BGIG_ATTRIBUTE_KIND,
        BGIG_ATTRIBUTE_MODULE_ID_KEY,
        BGIG_ATTRIBUTE_ROLE_KEY,
        BGIG_ATTRIBUTE_SCENE_ID_KEY,
        BGIG_ATTRIBUTE_VALUE,
        BGIG_ATTRIBUTE_VERSION_KEY,
        BGIG_ATTRIBUTE_VERSION_VALUE,
        BGIG_LEGACY_ATTRIBUTE_GROUPS,
        BGIG_ACTION_GUIDANCE,
        BGIG_CLEARABLE_ROLES,
        BGIG_CLEAR_SCOPE,
        BGIG_EXISTING_SCENE_MESSAGE,
        BGIG_GENERATE_EXISTING_SCENE_POLICY,
        BGIG_COMMAND_NAME,
        BGIG_COMMAND_TOOLTIP,
        BGIG_GENERATED_CAD_IR_FILENAME,
        BGIG_GENERATED_CONFIG_FILENAME,
        BGIG_SCENE_ROOT_COMPONENT_NAME,
        BGIG_SCENE_ROOT_ROLE,
        BGIG_SCENE_OWNERSHIP_POLICY,
        BGIG_COMPONENT_CREATION_POLICY,
        BGIG_SOURCE_HELPER_POLICY,
        BGIG_VISIBLE_OCCURRENCE_POLICY,
        BGIG_TOOLBAR_LOCATION,
        BGIG_TOOLBAR_PANEL_IDS,
        BGIG_TOOLBAR_WORKSPACE_ID,
        BGIG_UI_REOPEN_POLICY,
        COMPACT_OCCURRENCE_ROLE,
        DEFAULT_CAD_IR_INPUT_FILENAME,
        DEFAULT_FUSION_COMMAND_ACTION,
        DEFAULT_FUSION_INPUT_MODE,
        DEFAULT_FUSION_GENERATION_MODE,
        FUSION_GENERATION_MODE_COMPACT_ONLY,
        DOCUMENT_STATUS_ZERO_DOC,
        FUSION_INPUT_MODE_CAD_IR_FILE,
        FUSION_INPUT_MODE_CONFIG_FILE,
        FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
        FUSION_INPUT_MODE_QUICK_ASSET_BOX,
        FUSION_COMMAND_ACTION_CLEAR,
        FUSION_COMMAND_ACTION_GENERATE,
        FUSION_COMMAND_ACTION_INSPECT,
        FUSION_COMMAND_ACTION_EXPORT_PRINTABLES,
        FUSION_COMMAND_ACTION_REGENERATE,
        BGIG_EXPORT_FORMAT_STL,
        BGIG_EXPORT_POLICY,
        BGIG_EXPORT_MANIFEST_JSON_FILENAME,
        BGIG_EXPORT_MANIFEST_MARKDOWN_FILENAME,
        EXPLODED_OCCURRENCE_ROLE,
        FUSION_EXTENT_NEGATIVE,
        FUSION_EXTENT_POSITIVE,
        FUSION_SKETCH_PLANE_XZ,
        FUSION_SKETCH_PLANE_YZ,
        OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
        P12_PARAMETRIC_FIELD_DEFAULTS,
        BGIG_PARAMETRIC_FIELDS_STATUS,
        BGIG_QUICK_PARAMETRIC_BOX_STATUS,
        BGIG_QUICK_ASSET_BOX_DEFAULT_ASSETS,
        BGIG_QUICK_ASSET_BOX_FIELD,
        BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD,
        BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD,
        BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD,
        BGIG_PARAMETRIC_FIELD_HELP_TEXT,
        BGIG_QUICK_ASSET_BOX_HELP_TITLE,
        BGIG_QUICK_ASSET_BOX_HELP_TEXT,
        BGIG_QUICK_ASSET_BOX_STATUS,
        P12_PARAMETRIC_FIELD_LABELS,
        SUPPORTED_FUSION_GENERATION_MODES,
        SUPPORTED_FUSION_INPUT_MODES,
        FusionAssemblyDocumentRequiredError,
        FusionAdditivePrismPlan,
        FusionCavityCutPlan,
        FusionFingerNotchCutPlan,
        FusionGenerationPlan,
        FusionSkeletonError,
        FusionSolidPlan,
        FusionVectorMm,
        apply_parametric_overrides_to_config_payload,
        assembly_document_required_message,
        build_fusion_command_request,
        build_quick_parametric_box_cad_ir_payload,
        build_quick_asset_box_config_payload,
        cad_ir_input_guidance,
        default_fusion_command_values,
        default_fusion_ui_settings,
        describe_document_state,
        parametric_values_from_ui_settings,
        fusion_command_summary,
        fusion_ui_settings_summary,
        fusion_ui_settings_path,
        quick_parametric_box_summary,
        quick_asset_box_metadata,
        quick_asset_box_summary,
        printable_export_filename,
        printable_export_result_summary,
        generation_plan_from_cad_ir,
        is_part_design_component_limit_error,
        load_cad_ir_json,
        load_fusion_ui_settings,
        mm_to_cm,
        resolve_cad_ir_input_path,
        resolve_generation_mode,
    )
except ImportError:  # pragma: no cover - Fusion may load the file as a script.
    from fusion_skeleton import (  # type: ignore[no-redef]
        BGIG_ATTRIBUTE_GROUP,
        BGIG_ATTRIBUTE_KIND,
        BGIG_ATTRIBUTE_MODULE_ID_KEY,
        BGIG_ATTRIBUTE_ROLE_KEY,
        BGIG_ATTRIBUTE_SCENE_ID_KEY,
        BGIG_ATTRIBUTE_VALUE,
        BGIG_ATTRIBUTE_VERSION_KEY,
        BGIG_ATTRIBUTE_VERSION_VALUE,
        BGIG_LEGACY_ATTRIBUTE_GROUPS,
        BGIG_ACTION_GUIDANCE,
        BGIG_CLEARABLE_ROLES,
        BGIG_CLEAR_SCOPE,
        BGIG_EXISTING_SCENE_MESSAGE,
        BGIG_GENERATE_EXISTING_SCENE_POLICY,
        BGIG_COMMAND_NAME,
        BGIG_COMMAND_TOOLTIP,
        BGIG_GENERATED_CAD_IR_FILENAME,
        BGIG_GENERATED_CONFIG_FILENAME,
        BGIG_SCENE_ROOT_COMPONENT_NAME,
        BGIG_SCENE_ROOT_ROLE,
        BGIG_SCENE_OWNERSHIP_POLICY,
        BGIG_COMPONENT_CREATION_POLICY,
        BGIG_SOURCE_HELPER_POLICY,
        BGIG_VISIBLE_OCCURRENCE_POLICY,
        BGIG_TOOLBAR_LOCATION,
        BGIG_TOOLBAR_PANEL_IDS,
        BGIG_TOOLBAR_WORKSPACE_ID,
        BGIG_UI_REOPEN_POLICY,
        COMPACT_OCCURRENCE_ROLE,
        DEFAULT_CAD_IR_INPUT_FILENAME,
        DEFAULT_FUSION_COMMAND_ACTION,
        DEFAULT_FUSION_INPUT_MODE,
        DEFAULT_FUSION_GENERATION_MODE,
        FUSION_GENERATION_MODE_COMPACT_ONLY,
        DOCUMENT_STATUS_ZERO_DOC,
        FUSION_INPUT_MODE_CAD_IR_FILE,
        FUSION_INPUT_MODE_CONFIG_FILE,
        FUSION_INPUT_MODE_QUICK_PARAMETRIC_BOX,
        FUSION_INPUT_MODE_QUICK_ASSET_BOX,
        FUSION_COMMAND_ACTION_CLEAR,
        FUSION_COMMAND_ACTION_GENERATE,
        FUSION_COMMAND_ACTION_INSPECT,
        FUSION_COMMAND_ACTION_EXPORT_PRINTABLES,
        FUSION_COMMAND_ACTION_REGENERATE,
        BGIG_EXPORT_FORMAT_STL,
        BGIG_EXPORT_POLICY,
        BGIG_EXPORT_MANIFEST_JSON_FILENAME,
        BGIG_EXPORT_MANIFEST_MARKDOWN_FILENAME,
        EXPLODED_OCCURRENCE_ROLE,
        FUSION_EXTENT_NEGATIVE,
        FUSION_EXTENT_POSITIVE,
        FUSION_SKETCH_PLANE_XZ,
        FUSION_SKETCH_PLANE_YZ,
        OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
        P12_PARAMETRIC_FIELD_DEFAULTS,
        BGIG_PARAMETRIC_FIELDS_STATUS,
        BGIG_QUICK_PARAMETRIC_BOX_STATUS,
        BGIG_QUICK_ASSET_BOX_DEFAULT_ASSETS,
        BGIG_QUICK_ASSET_BOX_FIELD,
        BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD,
        BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD,
        BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD,
        BGIG_PARAMETRIC_FIELD_HELP_TEXT,
        BGIG_QUICK_ASSET_BOX_HELP_TITLE,
        BGIG_QUICK_ASSET_BOX_HELP_TEXT,
        BGIG_QUICK_ASSET_BOX_STATUS,
        P12_PARAMETRIC_FIELD_LABELS,
        SUPPORTED_FUSION_GENERATION_MODES,
        SUPPORTED_FUSION_INPUT_MODES,
        FusionAssemblyDocumentRequiredError,
        FusionAdditivePrismPlan,
        FusionCavityCutPlan,
        FusionFingerNotchCutPlan,
        FusionGenerationPlan,
        FusionSkeletonError,
        FusionSolidPlan,
        FusionVectorMm,
        apply_parametric_overrides_to_config_payload,
        assembly_document_required_message,
        build_fusion_command_request,
        build_quick_parametric_box_cad_ir_payload,
        build_quick_asset_box_config_payload,
        cad_ir_input_guidance,
        default_fusion_command_values,
        default_fusion_ui_settings,
        describe_document_state,
        parametric_values_from_ui_settings,
        fusion_command_summary,
        fusion_ui_settings_summary,
        fusion_ui_settings_path,
        quick_parametric_box_summary,
        quick_asset_box_metadata,
        quick_asset_box_summary,
        printable_export_filename,
        printable_export_result_summary,
        generation_plan_from_cad_ir,
        is_part_design_component_limit_error,
        load_cad_ir_json,
        load_fusion_ui_settings,
        mm_to_cm,
        resolve_cad_ir_input_path,
        resolve_generation_mode,
    )

try:
    import adsk.core  # type: ignore[import-not-found]
    import adsk.fusion  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised only outside Fusion.
    adsk = None  # type: ignore[assignment]



BGIG_LEGACY_COMMAND_ID = "board_game_insert_generator.generate_scene"
BGIG_COMMAND_ID = "board_game_insert_generator_generate_scene"
BGIG_PALETTE_ID = "board_game_insert_generator_palette"
BGIG_PALETTE_TITLE = "BGIG - Atelier de rangement"
BGIG_PALETTE_HTML_FILENAME = "palette.html"
BGIG_PALETTE_STATE_ACTION = "bgig_palette_state"
BGIG_PALETTE_NOTICE_ACTION = "bgig_palette_notice"
BGIG_PALETTE_PROJECT_ACTION = "bgig_palette_project"
BGIG_PALETTE_PROJECT_RESPONSE_ACTION = "bgig_palette_project_response"
BGIG_PALETTE_TRANSPORT_RESPONSE_ACTION = "response"
BGIG_PALETTE_READY_ACTION = "bgig_palette_ready"
BGIG_PALETTE_BOOTSTRAP_REQUEST_ID = "palette-bootstrap"
BGIG_PALETTE_REQUEST_SCHEMA = "bgig.palette.request.v1"
BGIG_COMMAND_RESOURCE_FOLDER = "resources"
BGIG_PALETTE_DEFAULT_WIDTH = 1280
BGIG_PALETTE_DEFAULT_HEIGHT = 1100
ACTION_INPUT_ID = "bgig_command_action"
INPUT_MODE_INPUT_ID = "bgig_input_mode"
CAD_IR_PATH_INPUT_ID = "bgig_cad_ir_path"
CONFIG_JSON_PATH_INPUT_ID = "bgig_config_json_path"
PROJECT_ROOT_INPUT_ID = "bgig_project_root"
GENERATION_MODE_INPUT_ID = "bgig_generation_mode"
SUMMARY_INPUT_ID = "bgig_command_summary"
QUICK_ASSET_BOX_MAX_STACK_HEIGHT_INPUT_ID = "bgig_quick_asset_box_max_stack_height"
QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_INPUT_ID = "bgig_quick_asset_box_target_aspect_ratio"
QUICK_ASSET_BOX_MAX_MODULE_LENGTH_INPUT_ID = "bgig_quick_asset_box_max_module_length"
QUICK_ASSET_BOX_ASSETS_INPUT_ID = "bgig_quick_asset_box_assets"
PARAMETER_INPUT_PREFIX = "bgig_param_"

_app = None
_ui = None
_handlers = []


def run(context) -> None:  # noqa: ANN001 - Fusion controls the signature.
    """Fusion 360 add-in startup hook."""

    global _app, _ui

    if adsk is None:
        return

    _app = adsk.core.Application.get()
    _ui = _app.userInterface if _app else None
    state = describe_document_state(_app)

    if state.status == DOCUMENT_STATUS_ZERO_DOC:
        _show_message(
            "Board Game Insert Generator cannot generate blanks.\n"
            f"{state.message}\n"
            "Open or create a Fusion design, then run the add-in again."
        )
        return

    try:
        _register_command_and_show_palette(Path(__file__).resolve().parent)
    except FusionSkeletonError as exc:
        _show_message(
            "Board Game Insert Generator command setup error:\n"
            f"{exc}\n\n"
            f"{cad_ir_input_guidance(Path(__file__).resolve().parent)}"
        )
    except Exception as exc:  # pragma: no cover - Fusion runtime boundary.
        _show_message(f"Board Game Insert Generator Fusion command error:\n{exc}")


def stop(context) -> None:  # noqa: ANN001 - Fusion controls the signature.
    """Fusion 360 add-in shutdown hook."""

    global _handlers
    if adsk is not None and _ui is not None:
        _delete_palette()
        _delete_command_control(BGIG_COMMAND_ID)
        _delete_command_definition(BGIG_COMMAND_ID)
        _delete_command_definition(BGIG_LEGACY_COMMAND_ID)
    _handlers = []
    _show_message("Board Game Insert Generator adapter stopped.")

if adsk is not None:
    class _BgigPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):  # type: ignore[misc]
        def __init__(self, addin_dir: Path) -> None:
            super().__init__()
            self.addin_dir = addin_dir

        def notify(self, args) -> None:  # noqa: ANN001 - Fusion event args.
            try:
                _ensure_palette(self.addin_dir)
            except Exception as exc:
                _show_message(f"BGIG palette error:\n{exc}")


    class _BgigPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):  # type: ignore[misc]
        def __init__(self, addin_dir: Path) -> None:
            super().__init__()
            self.addin_dir = addin_dir

        def notify(self, args) -> None:  # noqa: ANN001 - Fusion event args.
            execute_handler = _BgigPaletteCommandExecuteHandler(self.addin_dir)
            args.command.execute.add(execute_handler)
            _handlers.append(execute_handler)


    class _BgigCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):  # type: ignore[misc]
        def __init__(self, addin_dir: Path) -> None:
            super().__init__()
            self.addin_dir = addin_dir

        def notify(self, args) -> None:  # noqa: ANN001 - Fusion event args.
            try:
                command = args.command
                try:
                    command.okButtonText = "Run"
                except Exception:
                    pass
                inputs = command.commandInputs
                defaults = default_fusion_ui_settings(self.addin_dir)
                default_request = _safe_default_command_request(self.addin_dir)
                if _active_bgig_scene_exists():
                    default_request = replace(default_request, action=FUSION_COMMAND_ACTION_REGENERATE)
                action_input = inputs.addDropDownCommandInput(
                    ACTION_INPUT_ID,
                    "Action",
                    adsk.core.DropDownStyles.TextListDropDownStyle,
                )
                for action in (
                    DEFAULT_FUSION_COMMAND_ACTION,
                    FUSION_COMMAND_ACTION_REGENERATE,
                    FUSION_COMMAND_ACTION_CLEAR,
                    FUSION_COMMAND_ACTION_INSPECT,
                    FUSION_COMMAND_ACTION_EXPORT_PRINTABLES,
                ):
                    action_input.listItems.add(action, action == default_request.action, "")
                inputs.addTextBoxCommandInput(
                    "bgig_action_guidance",
                    "Action safety",
                    BGIG_ACTION_GUIDANCE,
                    3,
                    True,
                )
                input_mode = inputs.addDropDownCommandInput(
                    INPUT_MODE_INPUT_ID,
                    "Input mode",
                    adsk.core.DropDownStyles.TextListDropDownStyle,
                )
                for mode in SUPPORTED_FUSION_INPUT_MODES:
                    input_mode.listItems.add(mode, mode == default_request.input_mode, "")
                inputs.addStringValueInput(
                    CAD_IR_PATH_INPUT_ID,
                    "CAD IR JSON path (cad_ir_file)",
                    defaults.get("cad_ir_path", str(default_request.cad_ir_path or "")),
                )
                inputs.addStringValueInput(
                    CONFIG_JSON_PATH_INPUT_ID,
                    "BGIG config JSON path (config_file)",
                    defaults.get("config_json_path", ""),
                )
                inputs.addStringValueInput(
                    PROJECT_ROOT_INPUT_ID,
                    "BGIG project root (auto/memorized, optional)",
                    defaults.get("project_root", ""),
                )
                mode_input = inputs.addDropDownCommandInput(
                    GENERATION_MODE_INPUT_ID,
                    "Generation mode",
                    adsk.core.DropDownStyles.TextListDropDownStyle,
                )
                for mode in SUPPORTED_FUSION_GENERATION_MODES:
                    mode_input.listItems.add(mode, mode == default_request.generation_mode, "")
                inputs.addTextBoxCommandInput(
                    "bgig_parametric_status",
                    "Mode and field guide",
                    (
                        "Saved in bgig_ui_settings.json and restored when BGIG is reopened. "
                        "Active in config_file, quick_parametric_box and quick_asset_box modes; ignored in cad_ir_file mode. "
                        f"quick_parametric_box: {BGIG_QUICK_PARAMETRIC_BOX_STATUS}. "
                        f"quick_asset_box: {BGIG_QUICK_ASSET_BOX_STATUS}. "
                        f"{BGIG_PARAMETRIC_FIELD_HELP_TEXT}"
                    ),
                    5,
                    True,
                )
                inputs.addTextBoxCommandInput(
                    "bgig_quick_asset_box_help",
                    BGIG_QUICK_ASSET_BOX_HELP_TITLE,
                    BGIG_QUICK_ASSET_BOX_HELP_TEXT,
                    4,
                    True,
                )
                inputs.addStringValueInput(
                    QUICK_ASSET_BOX_MAX_STACK_HEIGHT_INPUT_ID,
                    "Max stack height mm (quick_asset_box, optional)",
                    defaults.get(BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD, ""),
                )
                inputs.addStringValueInput(
                    QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_INPUT_ID,
                    "Target aspect ratio (quick_asset_box, optional)",
                    defaults.get(BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD, ""),
                )
                inputs.addStringValueInput(
                    QUICK_ASSET_BOX_MAX_MODULE_LENGTH_INPUT_ID,
                    "Max module length mm (quick_asset_box, optional)",
                    defaults.get(BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD, ""),
                )
                inputs.addTextBoxCommandInput(
                    QUICK_ASSET_BOX_ASSETS_INPUT_ID,
                    "Assets (quick_asset_box)",
                    defaults.get(BGIG_QUICK_ASSET_BOX_FIELD, BGIG_QUICK_ASSET_BOX_DEFAULT_ASSETS),
                    6,
                    False,
                )
                for parameter_id, label in P12_PARAMETRIC_FIELD_LABELS.items():
                    inputs.addStringValueInput(
                        _parameter_input_id(parameter_id),
                        _ui_parameter_label(parameter_id, label),
                        defaults.get(parameter_id, P12_PARAMETRIC_FIELD_DEFAULTS[parameter_id]),
                    )
                inputs.addTextBoxCommandInput(
                    "bgig_ui_settings_status",
                    "UI settings",
                    fusion_ui_settings_summary(defaults),
                    6,
                    True,
                )
                inputs.addTextBoxCommandInput(
                    SUMMARY_INPUT_ID,
                    "Summary",
                    fusion_command_summary(default_request),
                    10,
                    True,
                )
                execute_handler = _BgigCommandExecuteHandler(self.addin_dir)
                command.execute.add(execute_handler)
                _handlers.append(execute_handler)
            except Exception as exc:  # pragma: no cover - Fusion runtime boundary.
                _show_message(f"Board Game Insert Generator command creation error:\n{exc}")


    class _BgigCommandExecuteHandler(adsk.core.CommandEventHandler):  # type: ignore[misc]
        def __init__(self, addin_dir: Path) -> None:
            super().__init__()
            self.addin_dir = addin_dir

        def notify(self, args) -> None:  # noqa: ANN001 - Fusion event args.
            try:
                inputs = args.command.commandInputs
                cad_ir_path_input = inputs.itemById(CAD_IR_PATH_INPUT_ID)
                config_path_input = inputs.itemById(CONFIG_JSON_PATH_INPUT_ID)
                project_root_input = inputs.itemById(PROJECT_ROOT_INPUT_ID)
                generation_mode_input = inputs.itemById(GENERATION_MODE_INPUT_ID)
                action_input = inputs.itemById(ACTION_INPUT_ID)
                input_mode_input = inputs.itemById(INPUT_MODE_INPUT_ID)
                quick_asset_input = inputs.itemById(QUICK_ASSET_BOX_ASSETS_INPUT_ID)
                quick_asset_max_stack_input = inputs.itemById(QUICK_ASSET_BOX_MAX_STACK_HEIGHT_INPUT_ID)
                quick_asset_target_aspect_input = inputs.itemById(QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_INPUT_ID)
                quick_asset_max_length_input = inputs.itemById(QUICK_ASSET_BOX_MAX_MODULE_LENGTH_INPUT_ID)
                request = build_fusion_command_request(
                    getattr(cad_ir_path_input, "value", ""),
                    _selected_dropdown_value(generation_mode_input, DEFAULT_FUSION_GENERATION_MODE),
                    self.addin_dir,
                    action=_selected_dropdown_value(action_input, DEFAULT_FUSION_COMMAND_ACTION),
                    config_json_path_text=getattr(config_path_input, "value", ""),
                    project_root_text=getattr(project_root_input, "value", ""),
                    parameter_values=_parameter_input_values(inputs),
                    input_mode=_selected_dropdown_value(input_mode_input, DEFAULT_FUSION_INPUT_MODE),
                    quick_asset_box_assets_text=getattr(quick_asset_input, "text", getattr(quick_asset_input, "formattedText", "")),
                    quick_asset_box_max_stack_height_mm=getattr(quick_asset_max_stack_input, "value", ""),
                    quick_asset_box_target_aspect_ratio=getattr(quick_asset_target_aspect_input, "value", ""),
                    quick_asset_box_max_module_length_mm=getattr(quick_asset_max_length_input, "value", ""),
                )
                _show_message(_execute_generation_request(request, self.addin_dir))
            except FusionAssemblyDocumentRequiredError as exc:
                _show_message(
                    "Board Game Insert Generator requires an Assembly-compatible Fusion document.\n"
                    f"{exc}\n\n"
                    "Status: assembly document required."
                )
            except FusionSkeletonError as exc:
                _show_message(
                    "Board Game Insert Generator CAD IR error:\n"
                    f"{exc}\n\n"
                    f"{cad_ir_input_guidance(self.addin_dir)}"
                )
            except Exception as exc:  # pragma: no cover - Fusion runtime boundary.
                if is_part_design_component_limit_error(exc):
                    _show_message(
                        "Board Game Insert Generator requires an Assembly-compatible Fusion document.\n"
                        f"{assembly_document_required_message(exc)}\n\n"
                        "Status: assembly document required."
                    )
                    return
                _show_message(f"Board Game Insert Generator Fusion error:\n{exc}")


    class _BgigPaletteIncomingHandler(adsk.core.HTMLEventHandler):  # type: ignore[misc]
        """Keeps the small product palette connected to the existing Fusion adapter."""

        def __init__(self, addin_dir: Path, palette) -> None:  # noqa: ANN001 - Fusion API object.
            super().__init__()
            self.addin_dir = addin_dir
            self.palette = palette

        def notify(self, args) -> None:  # noqa: ANN001 - Fusion event args.
            action = str(getattr(args, "action", ""))
            if _is_palette_transport_response(action):
                return
            try:
                try:
                    args.returnData = "OK"
                except Exception:
                    pass
                if action == BGIG_PALETTE_READY_ACTION:
                    request = _safe_default_command_request(self.addin_dir)
                    response = _handle_palette_project_request(
                        _palette_bootstrap_request(),
                        self.addin_dir,
                        project_root=request.project_root,
                    )
                    self.palette.sendInfoToHTML(
                        BGIG_PALETTE_PROJECT_RESPONSE_ACTION,
                        json.dumps(response, ensure_ascii=False),
                    )
                    return
                if action == BGIG_PALETTE_PROJECT_ACTION:
                    raw_request = json.loads(str(getattr(args, "data", "{}") or "{}"))
                    try:
                        request = _safe_default_command_request(self.addin_dir)
                        response = _handle_palette_project_request(
                            raw_request,
                            self.addin_dir,
                            project_root=request.project_root,
                        )
                        project_action = str(raw_request.get("action", "")) if isinstance(raw_request, dict) else ""
                        if project_action in {"materialize_project", "regenerate_project"}:
                            response = _synchronize_palette_cad_response(response, project_action, self.addin_dir)
                    except Exception as exc:
                        response = _palette_project_bridge_error_response(raw_request, exc)
                    self.palette.sendInfoToHTML(
                        BGIG_PALETTE_PROJECT_RESPONSE_ACTION,
                        json.dumps(response, ensure_ascii=False),
                    )
                    return
                if action in {"refresh", "preview", "inspect"}:
                    request = replace(_safe_default_command_request(self.addin_dir), action=FUSION_COMMAND_ACTION_INSPECT)
                    result = _execute_generation_request(request, self.addin_dir)
                    _publish_palette_state(self.palette, self.addin_dir, technical_detail=result)
                    return
                if action == "clear":
                    request = replace(_safe_default_command_request(self.addin_dir), action=FUSION_COMMAND_ACTION_CLEAR)
                    result = _execute_generation_request(request, self.addin_dir)
                    _publish_palette_state(self.palette, self.addin_dir, result)
                    return
                if action == "expert":
                    command_definition = _ui.commandDefinitions.itemById(BGIG_COMMAND_ID)
                    if command_definition is None or not command_definition.execute():
                        raise FusionSkeletonError("Fusion could not open the expert settings dialog.")
                    _publish_palette_notice(
                        self.palette,
                        "Les reglages experts sont ouverts. Ils restent un outil de diagnostic et de secours.",
                    )
                    return
                if action == "update":
                    request = _safe_default_command_request(self.addin_dir)
                    request = replace(
                        request,
                        action=FUSION_COMMAND_ACTION_REGENERATE if _active_bgig_scene_exists() else FUSION_COMMAND_ACTION_GENERATE,
                    )
                    _execute_generation_request(request, self.addin_dir)
                    _publish_palette_state(
                        self.palette,
                        self.addin_dir,
                        "Scene Fusion mise a jour. Verifie les bacs dans la zone de travail avant export.",
                    )
                    return
                if action == "export":
                    request = replace(_safe_default_command_request(self.addin_dir), action=FUSION_COMMAND_ACTION_EXPORT_PRINTABLES)
                    result = _execute_generation_request(request, self.addin_dir)
                    _publish_palette_state(self.palette, self.addin_dir, _palette_export_notice(result))
                    return
                _publish_palette_notice(self.palette, "Action inconnue. Actualise la palette ou ouvre les reglages experts.")
            except Exception as exc:  # pragma: no cover - Fusion runtime boundary.
                _publish_palette_state(
                    self.palette,
                    self.addin_dir,
                    "L action n a pas abouti. Ouvre les reglages experts pour le detail technique.",
                    technical_detail=str(exc),
                )
else:  # pragma: no cover - imported outside Fusion only.
    class _BgigCommandCreatedHandler:  # type: ignore[no-redef]
        pass

    class _BgigCommandExecuteHandler:  # type: ignore[no-redef]
        pass

    class _BgigPaletteIncomingHandler:  # type: ignore[no-redef]
        pass

def _register_command_and_show_palette(addin_dir: Path) -> None:
    command_definitions = _ui.commandDefinitions
    _delete_command_control(BGIG_COMMAND_ID)
    _delete_command_definition(BGIG_COMMAND_ID)
    _delete_command_definition(BGIG_LEGACY_COMMAND_ID)
    resource_folder = addin_dir / BGIG_COMMAND_RESOURCE_FOLDER
    command_definition = command_definitions.addButtonDefinition(
        BGIG_COMMAND_ID,
        BGIG_COMMAND_NAME,
        BGIG_COMMAND_TOOLTIP,
        str(resource_folder),
    )
    if command_definition is None:
        raise FusionSkeletonError("Fusion command definition creation failed for Generate Board Game Insert.")

    created_handler = _BgigPaletteCommandCreatedHandler(addin_dir)
    command_definition.commandCreated.add(created_handler)
    _handlers.append(created_handler)
    _add_toolbar_button(command_definition)
    adsk.autoTerminate(False)
    _ensure_palette(addin_dir)


def _ensure_palette(addin_dir: Path):  # noqa: ANN001 - Fusion API object.
    palette = _ui.palettes.itemById(BGIG_PALETTE_ID)
    if palette is None:
        html_path = addin_dir / BGIG_PALETTE_HTML_FILENAME
        if not html_path.is_file():
            raise FusionSkeletonError(f"Fusion palette file is missing: {html_path}")
        palette = _ui.palettes.add(
            BGIG_PALETTE_ID,
            BGIG_PALETTE_TITLE,
            html_path.resolve().as_uri(),
            True,
            True,
            True,
            BGIG_PALETTE_DEFAULT_WIDTH,
            BGIG_PALETTE_DEFAULT_HEIGHT,
        )
        if palette is None:
            raise FusionSkeletonError("Fusion palette creation failed.")
        incoming_handler = _BgigPaletteIncomingHandler(addin_dir, palette)
        palette.incomingFromHTML.add(incoming_handler)
        _handlers.append(incoming_handler)
    try:
        if int(getattr(palette, "width", 0)) < BGIG_PALETTE_DEFAULT_WIDTH:
            palette.width = BGIG_PALETTE_DEFAULT_WIDTH
        if int(getattr(palette, "height", 0)) < BGIG_PALETTE_DEFAULT_HEIGHT:
            palette.height = BGIG_PALETTE_DEFAULT_HEIGHT
        palette.isVisible = True
    except Exception:
        pass
    return palette


def _delete_palette() -> None:
    palette = _ui.palettes.itemById(BGIG_PALETTE_ID)
    if palette is not None:
        palette.deleteMe()


def _publish_palette_state(palette, addin_dir: Path, notice: str = "", technical_detail: str = "") -> None:  # noqa: ANN001
    payload = _palette_state(addin_dir, notice=notice, technical_detail=technical_detail)
    palette.sendInfoToHTML(BGIG_PALETTE_STATE_ACTION, json.dumps(payload, ensure_ascii=False))


def _publish_palette_notice(palette, notice: str) -> None:  # noqa: ANN001
    palette.sendInfoToHTML(BGIG_PALETTE_NOTICE_ACTION, json.dumps({"notice": notice}, ensure_ascii=False))


def _handle_palette_project_request(
    raw_request: object,
    addin_dir: Path,
    *,
    project_root: Path | None,
) -> dict[str, object]:
    """Keep the palette bridge importable outside Fusion and free of business rules."""

    try:
        from .palette_project import handle_palette_request
    except ImportError:  # pragma: no cover - Fusion may load the add-in as a script.
        from palette_project import handle_palette_request  # type: ignore[no-redef]
    return handle_palette_request(raw_request, addin_dir, project_root)


def _palette_bootstrap_request() -> dict[str, str]:
    """Return the deterministic load request sent only after Fusion proves readiness."""

    return {
        "schema": BGIG_PALETTE_REQUEST_SCHEMA,
        "request_id": BGIG_PALETTE_BOOTSTRAP_REQUEST_ID,
        "action": "load_project",
    }

def _is_palette_transport_response(action: str) -> bool:
    """Ignore the asynchronous acknowledgement emitted by Fusion QT."""

    return action == BGIG_PALETTE_TRANSPORT_RESPONSE_ACTION


def _synchronize_palette_cad_response(
    response: dict[str, object],
    project_action: str,
    addin_dir: Path,
) -> dict[str, object]:
    """Write the P59 CAD IR atomically and synchronize the owned BGIG scene."""

    synchronized = dict(response)
    cad_build = response.get("cad_build")
    if response.get("status") != "ready" or not isinstance(cad_build, dict):
        return synchronized
    if cad_build.get("status") != "ready_for_fusion" or not isinstance(cad_build.get("cad_ir"), dict):
        synchronized["scene_status"] = "blocked"
        synchronized["scene_result"] = "La partition ne peut pas etre materialisee dans Fusion."
        lifecycle = dict(synchronized.get("lifecycle") or {})
        lifecycle["materialized"] = "blocked"
        synchronized["lifecycle"] = lifecycle
        return synchronized

    cad_ir_path = addin_dir / BGIG_GENERATED_CAD_IR_FILENAME
    temporary = cad_ir_path.with_suffix(cad_ir_path.suffix + ".tmp")
    temporary.write_text(json.dumps(cad_build["cad_ir"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(cad_ir_path)
    inspection_before = _inspect_palette_scene()
    fusion_action = _palette_materialization_action(project_action, inspection_before)
    request = build_fusion_command_request(
        str(cad_ir_path),
        FUSION_GENERATION_MODE_COMPACT_ONLY,
        addin_dir,
        action=fusion_action,
        input_mode=FUSION_INPUT_MODE_CAD_IR_FILE,
    )
    synchronized["scene_result"] = _execute_generation_request(request, addin_dir)
    inspection_after = _inspect_palette_scene()
    scene_verified = _palette_scene_matches_cad_build(inspection_after, cad_build)
    generation_refused = BGIG_EXISTING_SCENE_MESSAGE in str(synchronized["scene_result"])
    synchronized["scene_status"] = "synchronized" if scene_verified and not generation_refused else "blocked"
    synchronized["scene_inspection"] = inspection_after
    lifecycle = dict(synchronized.get("lifecycle") or {})
    lifecycle["materialized"] = "current" if synchronized["scene_status"] == "synchronized" else "blocked"
    synchronized["lifecycle"] = lifecycle
    synchronized["cad_ir_path"] = str(cad_ir_path)
    return synchronized


def _inspect_palette_scene() -> dict[str, object]:
    """Inspect the active Fusion document around one explicit palette mutation."""

    return BgigFusionRegistry(_active_design(_app)).inspect()


def _palette_scene_is_safely_owned(inspection: dict[str, object]) -> bool:
    """Return whether exactly one rediscoverable, tagged BGIG scene owns the result."""

    return (
        int(inspection.get("bgig_scene_roots_total", 0)) == 1
        and int(inspection.get("scene_roots_by_attribute", 0)) == 1
        and int(inspection.get("tagged_bgig_entities", 0)) > 0
        and int(inspection.get("bgig_name_like_untagged_entities", 0)) == 0
    )


def _palette_scene_matches_cad_build(
    inspection: dict[str, object],
    cad_build: dict[str, object],
) -> bool:
    """Verify registry ownership and the exact number of requested Fusion bodies."""

    materialization = cad_build.get("materialization")
    if not isinstance(materialization, dict):
        return False
    expected_bodies = int(materialization.get("component_count", -1))
    return (
        _palette_scene_is_safely_owned(inspection)
        and int(inspection.get("bodies_tagged", -1)) == expected_bodies
    )


def _palette_materialization_action(project_action: str, inspection: dict[str, object]) -> str:
    """Create a first scene or safely replace the single owned BGIG scene."""

    if project_action == "regenerate_project" or _palette_scene_is_safely_owned(inspection):
        return FUSION_COMMAND_ACTION_REGENERATE
    return FUSION_COMMAND_ACTION_GENERATE


def _palette_project_bridge_error_response(raw_request: object, exc: Exception) -> dict[str, object]:
    request_id = str(raw_request.get("request_id", "unknown")) if isinstance(raw_request, dict) else "unknown"
    return {
        "schema": "bgig.palette.response.v1",
        "request_id": request_id,
        "status": "bridge_error",
        "project": None,
        "project_digest": "",
        "lifecycle": {"source": "invalid", "derived": "invalid", "solved": "invalid", "materialized": "error"},
        "envelopes": None,
        "flat_stack": None,
        "partition": None,
        "result_view": None,
        "cad_build": None,
        "errors": [f"La synchronisation Fusion a echoue : {exc}"],
        "warnings": [],
        "saved": False,
        "migrated": False,
        "export_path": "",
        "scene_status": "error",
        "scene_result": "",
    }

def _palette_state(addin_dir: Path, notice: str = "", technical_detail: str = "") -> dict[str, object]:
    """Returns a concise, product-facing state; raw diagnostics remain optional."""

    request = _safe_default_command_request(addin_dir)
    source_ready = bool(request.cad_ir_path and request.cad_ir_path.is_file())
    inspection: dict[str, object] = {}
    inspection_error = ""
    try:
        inspection = BgigFusionRegistry(_active_design(_app)).inspect()
    except Exception as exc:
        inspection_error = str(exc)

    scene_roots = int(inspection.get("bgig_scene_roots_total", 0))
    modules = int(inspection.get("bodies_tagged", 0))
    warnings: list[str] = []
    if not source_ready:
        warnings.append("Aucun projet BGIG pret. Cree ou importe le projet dans la palette Fusion ; les reglages experts restent disponibles.")
    if inspection_error:
        warnings.append("Fusion ne peut pas encore lire la scene active. Ouvre ou cree un design Fusion.")
    elif scene_roots > 1:
        warnings.append("Plusieurs scenes BGIG sont presentes. Utilise les reglages experts avant toute mise a jour.")
    elif int(inspection.get("bgig_name_like_untagged_entities", 0)) > 0:
        warnings.append("Des objets BGIG anciens ou non identifies existent. Le detail est disponible en mode expert.")

    if scene_roots == 1:
        scene_status = "Bacs visibles dans Fusion"
        scene_detail = f"{modules} corps de bac reconnus dans la scene actuelle."
    elif scene_roots > 1:
        scene_status = "Scene a verifier"
        scene_detail = "La mise a jour est bloquee tant que les scenes existantes ne sont pas clarifiees."
    else:
        scene_status = "Pret a materialiser"
        scene_detail = "Aucune scene BGIG n est encore presente dans ce document."

    return {
        "source_status": "Design recu" if source_ready else "Design manquant",
        "source_detail": "Le plan BGIG courant est pret a etre applique." if source_ready else "L editeur Fusion complet sera active par P56 ; aucun plan externe n est requis par le MVP.",
        "scene_status": scene_status,
        "scene_detail": scene_detail,
        "manufacturing_status": "Geometrie Fusion verifiee — impression non validee",
        "manufacturing_detail": "Les bacs ouverts sont observes dans Fusion. L ajustement reel et l impression restent a mesurer.",
        "warnings": warnings,
        "notice": notice,
        "technical_detail": technical_detail or inspection_error,
        "expert_available": True,
    }


def _palette_export_notice(result: str) -> str:
    if "Export status: exported" in result:
        return "Export termine. Le manifeste indique les fichiers prepares et ce qui reste a verifier dans le slicer."
    if "Export status: no_exportable_modules" in result:
        return "Aucun bac exportable n a ete trouve. Verifie la scene Fusion avant de relancer l export."
    return "Export a verifier. Le detail technique est disponible dans les reglages experts."

def _add_toolbar_button(command_definition) -> bool:  # noqa: ANN001 - Fusion API object.
    panel = _find_toolbar_panel()
    if panel is None:
        return False
    controls = panel.controls
    control = controls.itemById(BGIG_COMMAND_ID)
    if control is None:
        control = controls.addCommand(command_definition)
    if control is None:
        return False
    try:
        control.isVisible = True
    except Exception:
        pass
    try:
        control.isPromotedByDefault = True
        control.isPromoted = True
    except Exception:
        pass
    return True


def _find_toolbar_panel():  # noqa: ANN001 - Fusion API object.
    workspace = _ui.workspaces.itemById(BGIG_TOOLBAR_WORKSPACE_ID)
    if workspace is None:
        return None
    for panel_id in BGIG_TOOLBAR_PANEL_IDS:
        panel = workspace.toolbarPanels.itemById(panel_id)
        if panel is not None:
            return panel
    return None


def _delete_command_control(command_id: str) -> None:
    panel = _find_toolbar_panel()
    if panel is None:
        return
    control = panel.controls.itemById(command_id)
    if control is not None:
        control.deleteMe()


def _delete_command_definition(command_id: str) -> None:
    command_definition = _ui.commandDefinitions.itemById(command_id)
    if command_definition is not None:
        command_definition.deleteMe()

def _safe_default_command_request(addin_dir: Path):
    try:
        return default_fusion_command_values(addin_dir)
    except FusionSkeletonError:
        return build_fusion_command_request(
            str(addin_dir / DEFAULT_CAD_IR_INPUT_FILENAME),
            DEFAULT_FUSION_GENERATION_MODE,
            addin_dir,
        )


def _active_bgig_scene_exists() -> bool:
    try:
        design = _active_design(_app)
        inspection = BgigFusionRegistry(design).inspect()
    except Exception:
        return False
    return int(inspection.get("bgig_scene_roots_total", 0)) > 0



def _ui_parameter_label(parameter_id: str, label: str) -> str:
    if parameter_id.startswith("box_inner_"):
        return f"{label} (box inner size, mm)"
    if parameter_id.startswith("grid_units_"):
        return f"{label} (grid cell count)"
    if parameter_id in {"wall_thickness_mm", "floor_thickness_mm"}:
        return f"{label} (printable wall/floor, mm)"
    if parameter_id in {"peripheral_clearance_mm", "inter_module_clearance_mm"}:
        return f"{label} (clearance, mm)"
    if parameter_id == "print_profile":
        return f"{label} (default, draft or fine)"
    return f"{label} (config_file override / quick box value)"
def _parameter_input_id(parameter_id: str) -> str:
    return f"{PARAMETER_INPUT_PREFIX}{parameter_id}"


def _selected_dropdown_value(dropdown_input, default_value: str) -> str:  # noqa: ANN001 - Fusion API object.
    selected_item = getattr(dropdown_input, "selectedItem", None)
    selected_name = getattr(selected_item, "name", None)
    if isinstance(selected_name, str) and selected_name.endswith(" (disabled)"):
        selected_name = selected_name[: -len(" (disabled)")]
    return selected_name or default_value


def _parameter_input_values(inputs) -> dict[str, str]:  # noqa: ANN001 - Fusion API object.
    values = {}
    for parameter_id in P12_PARAMETRIC_FIELD_DEFAULTS:
        parameter_input = inputs.itemById(_parameter_input_id(parameter_id))
        values[parameter_id] = getattr(parameter_input, "value", "")
    return values


def _execute_generation_request(request, addin_dir: Path) -> str:  # noqa: ANN001 - FusionCommandRequest kept testable in skeleton.
    design = _active_design(_app)
    registry = BgigFusionRegistry(design)
    inspection_before = registry.inspect()
    scene_roots_before = int(inspection_before["bgig_scene_roots_total"])
    bgig_objects_before = int(inspection_before["tagged_bgig_entities"])
    bgig_named_before = int(inspection_before["bgig_name_like_untagged_entities"])

    if request.action == FUSION_COMMAND_ACTION_INSPECT:
        return _inspection_result_message(inspection_before)

    if request.action == FUSION_COMMAND_ACTION_CLEAR:
        clear_result = registry.clear(scene_roots_before=scene_roots_before)
        return _clear_result_message(clear_result)

    if request.action == FUSION_COMMAND_ACTION_EXPORT_PRINTABLES:
        export_result = _export_printables_from_scene(design, registry, addin_dir, inspection_before)
        return printable_export_result_summary(export_result)

    if request.action == FUSION_COMMAND_ACTION_GENERATE and (
        scene_roots_before > 0 or bgig_objects_before > 0 or bgig_named_before > 0
    ):
        return _generate_existing_scene_blocked_message(
            scene_roots_before,
            bgig_objects_before,
            bgig_named_before,
        )

    cad_ir_path = request.cad_ir_path
    quick_parametric_payload = None
    quick_asset_payload = None
    if request.source_kind == "config":        cad_ir_path = _generate_cad_ir_from_config_request(request, addin_dir)
    elif request.source_kind == "quick_parametric_box":
        cad_ir_path, quick_parametric_payload = _generate_cad_ir_from_quick_parametric_box_request(request, addin_dir)
    elif request.source_kind == "quick_asset_box":
        cad_ir_path, quick_asset_payload = _generate_cad_ir_from_quick_asset_box_request(request, addin_dir)
    if cad_ir_path is None:        raise FusionSkeletonError("No CAD IR path is available for generation.")

    payload = load_cad_ir_json(cad_ir_path)
    generation_plan = generation_plan_from_cad_ir(
        payload,
        generation_mode=request.generation_mode,
    )

    clear_result = None
    if request.action == FUSION_COMMAND_ACTION_REGENERATE:
        clear_result = registry.clear(scene_roots_before=scene_roots_before)
        if int(clear_result.get("bgig_objects_remaining", 0)) != 0:
            raise FusionSkeletonError(
                "Clear BGIG Scene did not remove all tagged BGIG objects. "
                "Generation refused to avoid stacking duplicate Fusion geometry. "
                f"Remaining BGIG objects: {clear_result.get('bgig_objects_remaining', 'unknown')}."
            )

    scene_id = registry.create_scene_id()
    result = _generate_from_plan(design, generation_plan, registry, scene_id)
    validation = registry.inspect()
    result["registry_validation"] = validation
    result["registry_validation_status"] = _validate_generated_scene_registry(validation)
    scene_roots_after = int(validation["bgig_scene_roots_total"])
    settings_saved = _save_command_settings(addin_dir, request, cad_ir_path)
    return _generation_result_message(
        generation_plan,
        result,
        cad_ir_path,
        request,
        scene_roots_before,
        scene_roots_after,
        clear_result,
        settings_saved,
        quick_parametric_payload,
        quick_asset_payload,
    )


def _export_printables_from_scene(design, registry: BgigFusionRegistry, addin_dir: Path, inspection: dict[str, object]) -> dict[str, object]:  # noqa: ANN001
    targets, refused = _collect_printable_export_targets(registry)
    scene_roots = int(inspection.get("bgig_scene_roots_total", 0))
    if scene_roots != 1:
        refused.append(
            {
                "name": "BGIG scene",
                "role": "scene_root",
                "reason": f"export requires exactly one BGIG scene root; found {scene_roots}",
            }
        )
        return _printable_export_result("blocked", addin_dir, targets, [], refused, [])

    export_dir = _default_printable_export_dir(addin_dir, registry, targets)
    export_dir.mkdir(parents=True, exist_ok=True)

    if not targets:
        result = _printable_export_result("no_exportable_modules", export_dir, targets, [], refused, [])
        return _write_printable_export_manifest(export_dir, result, addin_dir)

    export_manager = getattr(design, "exportManager", None)
    if export_manager is None:
        refused.append(
            {
                "name": "Fusion export manager",
                "role": "technical_gate",
                "reason": "design.exportManager is unavailable; STL export cannot be verified in this Fusion runtime",
            }
        )
        result = _printable_export_result("technical_gate", export_dir, targets, [], refused, [])
        return _write_printable_export_manifest(export_dir, result, addin_dir)

    exported_files: list[str] = []
    exported_modules: list[dict[str, object]] = []
    for index, target in enumerate(targets, start=1):
        filename = printable_export_filename(index, str(target["module_id"]), str(target["role"]))
        output_path = export_dir / filename
        try:
            options = export_manager.createSTLExportOptions(target["entity"], str(output_path))
            if options is None:
                raise FusionSkeletonError("createSTLExportOptions returned null")
            try:
                options.sendToPrintUtility = False
            except Exception:
                pass
            try:
                options.isBinaryFormat = True
            except Exception:
                pass
            exported = export_manager.execute(options)
            if exported is False:
                raise FusionSkeletonError("ExportManager.execute returned false")
            exported_files.append(str(output_path))
            exported_modules.append(
                {
                    "module_id": target["module_id"],
                    "name": target["name"],
                    "role": target["role"],
                    "file": str(output_path),
                }
            )
        except Exception as exc:
            refused.append(
                {
                    "name": target["name"],
                    "role": target["role"],
                    "module_id": target["module_id"],
                    "reason": f"STL export failed: {exc}",
                }
            )

    status = "exported" if exported_files and len(exported_files) == len(targets) else "partial_or_failed"
    result = _printable_export_result(status, export_dir, targets, exported_files, refused, exported_modules)
    return _write_printable_export_manifest(export_dir, result, addin_dir)


def _collect_printable_export_targets(registry: BgigFusionRegistry) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    targets: list[dict[str, object]] = []
    refused: list[dict[str, object]] = []
    seen = set()
    for entity, role in registry.tagged_entities():
        module_id = registry.module_id(entity) or "unassigned-module"
        name = _safe_entity_name(entity) or module_id
        if role == "module_body":
            key = registry.entity_key(entity)
            if key in seen:
                continue
            seen.add(key)
            targets.append(
                {
                    "entity": entity,
                    "name": name,
                    "role": role,
                    "module_id": module_id,
                    "reason": "tagged BGIG module body selected for STL export",
                }
            )
            continue
        refused_reason = _non_exportable_role_reason(role)
        if refused_reason:
            refused.append(
                {
                    "name": name,
                    "role": role or "n/a",
                    "module_id": module_id,
                    "reason": refused_reason,
                }
            )
    return targets, refused


def _non_exportable_role_reason(role: str | None) -> str | None:
    if role in {"module_component", COMPACT_OCCURRENCE_ROLE}:
        return "not exported directly; P17-M002 exports tagged module_body geometry only"
    if role == EXPLODED_OCCURRENCE_ROLE:
        return "exploded view occurrence excluded from printable export V0"
    if role in {BGIG_SCENE_ROOT_ROLE, "scene_root_occurrence", "scene_root_component"}:
        return "scene ownership entity excluded from printable export"
    if role in {"box_reference", "reference_outline"} or (role and role.endswith("_sketch")):
        return "reference or debug sketch excluded from printable export"
    if role == "module_extrude" or (role and role.endswith("_cut")):
        return "feature history object excluded from printable export"
    return None


def _default_printable_export_dir(addin_dir: Path, registry: BgigFusionRegistry, targets: list[dict[str, object]]) -> Path:
    scene_id = "bgig-scene"
    for target in targets:
        entity = target.get("entity")
        if entity is not None:
            scene_id = registry.scene_id(entity) or scene_id
            break
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path.home() / "Documents" / "BGIG" / "exports" / f"{scene_id}-{timestamp}"


def _printable_export_result(
    status: str,
    export_dir: Path,
    targets: list[dict[str, object]],
    exported_files: list[str],
    refused: list[dict[str, object]],
    exported_modules: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "status": status,
        "export_policy": BGIG_EXPORT_POLICY,
        "export_format": BGIG_EXPORT_FORMAT_STL,
        "export_directory": str(export_dir),
        "printable_modules_detected": len(targets),
        "printable_modules_exported": len(exported_files),
        "printable_modules_refused": len(refused),
        "exported_files": exported_files,
        "exported_modules": exported_modules,
        "refused_modules": refused,
        "manifest_json": "not generated",
        "manifest_markdown": "not generated",
        "print_validated": False,
    }


def _write_printable_export_manifest(export_dir: Path, result: dict[str, object], addin_dir: Path) -> dict[str, object]:
    manifest_json = export_dir / BGIG_EXPORT_MANIFEST_JSON_FILENAME
    manifest_markdown = export_dir / BGIG_EXPORT_MANIFEST_MARKDOWN_FILENAME
    settings = load_fusion_ui_settings(addin_dir)
    cad_ir_payload = _load_export_cad_ir_payload(settings)
    manifest = _printable_export_manifest_payload(result, settings, cad_ir_payload)
    manifest_json.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest_markdown.write_text(_printable_export_manifest_markdown(manifest), encoding="utf-8")
    updated = dict(result)
    updated["manifest_json"] = str(manifest_json)
    updated["manifest_markdown"] = str(manifest_markdown)
    return updated


def _load_export_cad_ir_payload(settings: dict[str, str]) -> dict[str, object] | None:
    for key in ("generated_cad_ir_path", "cad_ir_path"):
        value = str(settings.get(key, "")).strip()
        if not value:
            continue
        path = Path(value)
        if not path.is_file():
            continue
        try:
            return load_cad_ir_json(path)
        except Exception:
            return None
    return None


def _printable_export_manifest_payload(
    result: dict[str, object],
    settings: dict[str, str],
    cad_ir_payload: dict[str, object] | None,
) -> dict[str, object]:
    metadata = cad_ir_payload.get("metadata", {}) if isinstance(cad_ir_payload, dict) else {}
    executable_plan = metadata.get("executable_asset_plan", {}) if isinstance(metadata, dict) else {}
    quick_asset = metadata.get("quick_asset_box", {}) if isinstance(metadata, dict) else {}
    return {
        "schema_version": "bgig.export_manifest.v0",
        "export_policy": result.get("export_policy", BGIG_EXPORT_POLICY),
        "export_format": result.get("export_format", BGIG_EXPORT_FORMAT_STL),
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": result.get("status", "unknown"),
        "print_validated": False,
        "printability_validated_by_print": "no",
        "export_directory": result.get("export_directory", ""),
        "manifest_json": result.get("manifest_json", ""),
        "manifest_markdown": result.get("manifest_markdown", ""),
        "settings": {
            "input_mode": settings.get("input_mode", ""),
            "action": settings.get("action", ""),
            "generation_mode": settings.get("generation_mode", ""),
            "project_root": settings.get("project_root", ""),
            "cad_ir_path": settings.get("cad_ir_path", ""),
            "generated_cad_ir_path": settings.get("generated_cad_ir_path", ""),
        },
        "source": {
            "project_name": cad_ir_payload.get("project_name", "") if isinstance(cad_ir_payload, dict) else "",
            "schema_version": cad_ir_payload.get("schema_version", "") if isinstance(cad_ir_payload, dict) else "",
            "units": cad_ir_payload.get("units", "") if isinstance(cad_ir_payload, dict) else "",
            "box": cad_ir_payload.get("box", {}) if isinstance(cad_ir_payload, dict) else {},
            "volumetric_grid": cad_ir_payload.get("volumetric_grid", {}) if isinstance(cad_ir_payload, dict) else {},
            "quick_asset_box": quick_asset,
        },
        "assets": metadata.get("assets", []) if isinstance(metadata, dict) else [],
        "modules": executable_plan.get("generated_modules", []) if isinstance(executable_plan, dict) else [],
        "summary": {
            "printable_modules_detected": result.get("printable_modules_detected", 0),
            "printable_modules_exported": result.get("printable_modules_exported", 0),
            "printable_modules_refused": result.get("printable_modules_refused", 0),
        },
        "exported_modules": result.get("exported_modules", []),
        "exported_files": result.get("exported_files", []),
        "refused_modules": result.get("refused_modules", []),
        "warnings": [
            "Export manifest V0 is a preprint audit artifact, not physical print validation.",
            "print_validated remains false until a real printed prototype is measured.",
        ],
    }


def _printable_export_manifest_markdown(manifest: dict[str, object]) -> str:
    summary = manifest.get("summary", {}) if isinstance(manifest.get("summary"), dict) else {}
    lines = [
        "# BGIG Export Manifest V0",
        "",
        f"- Status: `{manifest.get('status', 'unknown')}`",
        f"- Export policy: `{manifest.get('export_policy', BGIG_EXPORT_POLICY)}`",
        f"- Export format: `{manifest.get('export_format', BGIG_EXPORT_FORMAT_STL)}`",
        f"- Export directory: `{manifest.get('export_directory', '')}`",
        "- Print validated: `false`",
        f"- Printable modules detected: {summary.get('printable_modules_detected', 0)}",
        f"- Printable modules exported: {summary.get('printable_modules_exported', 0)}",
        f"- Printable modules refused: {summary.get('printable_modules_refused', 0)}",
        "",
        "## Exported files",
    ]
    exported_files = manifest.get("exported_files", [])
    if isinstance(exported_files, list) and exported_files:
        lines.extend(f"- `{path}`" for path in exported_files)
    else:
        lines.append("- none")
    lines.extend(["", "## Refusals"])
    refused = manifest.get("refused_modules", [])
    if isinstance(refused, list) and refused:
        for item in refused:
            if isinstance(item, dict):
                lines.append(f"- `{item.get('name', 'unknown')}` role `{item.get('role', 'n/a')}`: {item.get('reason', 'refused')}")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings"])
    warnings = manifest.get("warnings", [])
    if isinstance(warnings, list):
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"

def _generate_cad_ir_from_quick_parametric_box_request(request, addin_dir: Path):  # noqa: ANN001
    payload = build_quick_parametric_box_cad_ir_payload(request.parameter_overrides or {})
    cad_ir_path = addin_dir / BGIG_GENERATED_CAD_IR_FILENAME
    cad_ir_path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    return cad_ir_path, payload

def _generate_cad_ir_from_quick_asset_box_request(request, addin_dir: Path):  # noqa: ANN001
    if request.project_root is None:
        raise FusionSkeletonError("BGIG project root is required for quick_asset_box generation.")
    _ensure_bgig_engine_on_path(request.project_root)
    try:
        from board_game_insert_generator.cad_ir import build_blank_cad_scene
        from board_game_insert_generator.config_loader import load_config
        from board_game_insert_generator.layout import generate_basic_layout
    except Exception as exc:  # pragma: no cover - depends on Fusion Python path.
        raise FusionSkeletonError(
            "Could not import the pure BGIG engine from BGIG project root. "
            f"Project root: {request.project_root}. Original error: {exc}"
        ) from exc

    temp_config_payload = build_quick_asset_box_config_payload(
        request.parameter_overrides or {},
        request.quick_asset_box_assets_text,
        getattr(request, "quick_asset_box_max_stack_height_mm", ""),
        getattr(request, "quick_asset_box_target_aspect_ratio", ""),
        getattr(request, "quick_asset_box_max_module_length_mm", ""),
    )
    temp_config_path = addin_dir / BGIG_GENERATED_CONFIG_FILENAME
    temp_config_path.write_text(
        json.dumps(temp_config_payload, indent=2) + "\n",
        encoding="utf-8",
    )

    try:
        config = load_config(temp_config_path)
        layout = generate_basic_layout(config)
        scene = build_blank_cad_scene(config, layout)
        payload = scene.to_dict()
        payload.setdefault("metadata", {})["quick_asset_box"] = quick_asset_box_metadata(
            temp_config_payload,
            request.quick_asset_box_assets_text,
            payload,
        )
    except Exception as exc:
        raise FusionSkeletonError(
            "quick_asset_box config-to-CAD-IR generation failed. "
            f"Temporary config: {temp_config_path}. Original error: {exc}"
        ) from exc

    cad_ir_path = addin_dir / BGIG_GENERATED_CAD_IR_FILENAME
    cad_ir_path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    return cad_ir_path, payload


def _generate_cad_ir_from_config_request(request, addin_dir: Path) -> Path:  # noqa: ANN001
    if request.config_json_path is None:
        raise FusionSkeletonError("BGIG config JSON path is required for config generation.")
    if request.project_root is None:
        raise FusionSkeletonError("BGIG project root is required for config generation.")

    _ensure_bgig_engine_on_path(request.project_root)
    try:
        from board_game_insert_generator.cad_ir import build_blank_cad_scene
        from board_game_insert_generator.config_loader import load_config
        from board_game_insert_generator.layout import generate_basic_layout
    except Exception as exc:  # pragma: no cover - depends on Fusion Python path.
        raise FusionSkeletonError(
            "Could not import the pure BGIG engine from BGIG project root. "
            f"Project root: {request.project_root}. Original error: {exc}"
        ) from exc

    try:
        raw_config = json.loads(request.config_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FusionSkeletonError(
            f"Invalid BGIG config JSON in {request.config_json_path}: {exc.msg}."
        ) from exc

    temp_config_payload = apply_parametric_overrides_to_config_payload(
        raw_config,
        request.parameter_overrides or {},
    )
    temp_config_path = addin_dir / BGIG_GENERATED_CONFIG_FILENAME
    temp_config_path.write_text(
        json.dumps(temp_config_payload, indent=2) + "\n",
        encoding="utf-8",
    )

    try:
        config = load_config(temp_config_path)
        layout = generate_basic_layout(config)
        scene = build_blank_cad_scene(config, layout)
    except Exception as exc:
        raise FusionSkeletonError(
            "BGIG config-to-CAD-IR generation failed. "
            f"Temporary config: {temp_config_path}. Original error: {exc}"
        ) from exc

    cad_ir_path = addin_dir / BGIG_GENERATED_CAD_IR_FILENAME
    cad_ir_path.write_text(
        json.dumps(scene.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    return cad_ir_path


def _ensure_bgig_engine_on_path(project_root: Path) -> None:
    src_path = project_root / "src"
    src_text = str(src_path)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)

def _save_command_settings(addin_dir: Path, request, cad_ir_path: Path | None = None) -> bool:  # noqa: ANN001
    settings = load_fusion_ui_settings(addin_dir)
    settings.update(
        {
            "action": request.action,
            "input_mode": request.input_mode,
            "generation_mode": request.generation_mode,
        }
    )
    if request.cad_ir_path is not None:
        settings["cad_ir_path"] = str(request.cad_ir_path)
    elif cad_ir_path is not None:
        settings.setdefault("cad_ir_path", str(cad_ir_path))
        settings["generated_cad_ir_path"] = str(cad_ir_path)
    if request.config_json_path is not None:
        settings["config_json_path"] = str(request.config_json_path)
    if request.project_root is not None:
        settings["project_root"] = str(request.project_root)
    settings[BGIG_QUICK_ASSET_BOX_FIELD] = str(getattr(request, "quick_asset_box_assets_text", "") or "").strip()
    settings[BGIG_QUICK_ASSET_BOX_MAX_STACK_HEIGHT_FIELD] = str(
        getattr(request, "quick_asset_box_max_stack_height_mm", "") or ""
    ).strip()
    settings[BGIG_QUICK_ASSET_BOX_TARGET_ASPECT_RATIO_FIELD] = str(
        getattr(request, "quick_asset_box_target_aspect_ratio", "") or ""
    ).strip()
    settings[BGIG_QUICK_ASSET_BOX_MAX_MODULE_LENGTH_FIELD] = str(
        getattr(request, "quick_asset_box_max_module_length_mm", "") or ""
    ).strip()
    for key, value in parametric_values_from_ui_settings(request.parameter_values or {}).items():
        settings[key] = value
    try:
        fusion_ui_settings_path(addin_dir).write_text(
            json.dumps(settings, indent=2) + "\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def _generate_existing_scene_blocked_message(
    scene_roots_before: int,
    bgig_objects_before: int,
    bgig_named_before: int = 0,
) -> str:
    return (
        "Board Game Insert Generator generate refused.\n"
        f"{BGIG_EXISTING_SCENE_MESSAGE}\n"
        f"Generate existing scene policy: {BGIG_GENERATE_EXISTING_SCENE_POLICY}\n"
        f"BGIG scene roots before: {scene_roots_before}\n"
        f"BGIG tagged objects before: {bgig_objects_before}\n"
        f"BGIG-looking untagged objects before: {bgig_named_before}\n"
        f"BGIG scene roots after: {scene_roots_before}\n"
        "BGIG objects deleted: 0\n"
        "Non-BGIG objects preserved: yes\n"
        "Use Action = regenerate to replace the tagged BGIG scene, Action = clear_bgig_scene to remove it first, "
        "or Action = inspect_bgig_scene to diagnose ownership.\n"
        "Status: manual validation required in Fusion 360."
    )


def _inspection_result_message(inspection: dict[str, object]) -> str:
    tagged_lines = _limited_report_lines(inspection.get("tagged_entity_lines", []), limit=10)
    name_like_lines = _limited_report_lines(inspection.get("name_like_untagged_lines", []), limit=8)
    inconsistencies = _limited_report_lines(inspection.get("inconsistency_lines", []), limit=8)
    return (
        "Board Game Insert Generator scene inspection.\n"
        "Action: inspect_bgig_scene\n"
        "Read-only: yes\n"
        f"Root occurrences visible: {inspection.get('root_occurrences_count', 0)}\n"
        f"Root occurrence names: {inspection.get('root_occurrence_names', 'none')}\n"
        f"BGIG scene root occurrences: {inspection.get('bgig_scene_root_occurrences', 0)}\n"
        f"BGIG Generated Scene by name: {inspection.get('scene_roots_by_name', 0)}\n"
        f"BGIG Generated Scene by scene_root attribute: {inspection.get('scene_roots_by_attribute', 0)}\n"
        f"BGIG scene roots total: {inspection.get('bgig_scene_roots_total', 0)}\n"
        f"Tagged BGIG attributes found: {inspection.get('tagged_bgig_attributes_found', 0)}\n"
        f"Tagged BGIG unique entities: {inspection.get('tagged_bgig_unique_entities', inspection.get('tagged_bgig_entities', 0))}\n"
        f"Occurrences tagged: {inspection.get('occurrences_tagged', 0)}\n"
        f"Components tagged: {inspection.get('components_tagged', 0)}\n"
        f"Bodies tagged: {inspection.get('bodies_tagged', 0)}\n"
        f"Sketches tagged: {inspection.get('sketches_tagged', 0)}\n"
        f"Features tagged: {inspection.get('features_tagged', 0)}\n"
        f"Tagged roles: {inspection.get('role_count_summary', 'none')}\n"
        f"BGIG-looking untagged entities: {inspection.get('bgig_name_like_untagged_entities', 0)}\n"
        "Tagged BGIG unique entities sample:\n"
        f"{tagged_lines}\n"
        "BGIG-looking untagged entities sample:\n"
        f"{name_like_lines}\n"
        "Inconsistencies:\n"
        f"{inconsistencies}\n"
        f"Registry validation status: {inspection.get('registry_status', 'inspect_only')}\n"
        "Status: manual validation required in Fusion 360."
    )


def _limited_report_lines(lines, limit: int = 10) -> str:  # noqa: ANN001
    if not isinstance(lines, list) or not lines:
        return "- none"
    rendered = [str(line) for line in lines[:limit]]
    remaining = len(lines) - len(rendered)
    if remaining > 0:
        rendered.append(f"- ... {remaining} more omitted from standard report")
    return "\n".join(rendered)


def _clear_result_message(clear_result: dict[str, object]) -> str:
    return (
        "Board Game Insert Generator clear completed.\n"
        f"Clear scope: {clear_result.get('scope', BGIG_CLEAR_SCOPE)}\n"
        f"BGIG scene roots before: {clear_result.get('scene_roots_before', 0)}\n"
        f"BGIG scene roots found: {clear_result.get('scene_roots_found', 0)}\n"
        f"BGIG scene roots deleted: {clear_result.get('scene_roots_deleted', 0)}\n"
        f"Tagged BGIG objects found: {clear_result.get('tagged_objects_found', 0)}\n"
        f"Legacy BGIG objects deleted: {clear_result.get('legacy_bgig_objects_deleted', 0)}\n"
        f"Tagged BGIG objects deleted total: {clear_result.get('deleted_objects', 0)}\n"
        f"Tagged BGIG objects skipped: {clear_result.get('skipped_objects', 0)}\n"
        f"BGIG scene roots after: {clear_result.get('scene_roots_after', 0)}\n"
        f"BGIG objects remaining after clear: {clear_result.get('bgig_objects_remaining', 0)}\n"
        f"Visible BGIG source/helper occurrences after clear: {clear_result.get('visible_source_helper_occurrences_after', 0)}\n"
        f"Non-BGIG objects preserved: {clear_result.get('non_bgig_objects_preserved', 'yes')}\n"
        "Legacy untagged BGIG-looking objects are reported by inspect_bgig_scene; only strict scene roots or tagged BGIG objects are deleted.\n"
        "Status: manual validation required in Fusion 360."
    )

def _generation_result_message(
    generation_plan: FusionGenerationPlan,
    result: dict[str, object],
    cad_ir_path: Path,
    request,
    scene_roots_before: int,
    scene_roots_after: int,
    clear_result: dict[str, object] | None = None,
    settings_saved: bool = False,
    quick_parametric_payload: dict[str, object] | None = None,
    quick_asset_payload: dict[str, object] | None = None,
) -> str:
    result = _stable_generation_result(result)
    body_size_report = _body_size_report_message(result.get("body_size_reports", []))
    module_mapping_report = _module_mapping_report_message(generation_plan)
    quick_parametric_report = quick_parametric_box_summary(quick_parametric_payload) if request.source_kind == "quick_parametric_box" else ""
    quick_asset_report = quick_asset_box_summary(quick_asset_payload) if request.source_kind == "quick_asset_box" else ""
    clear_lines = ""
    if clear_result is not None:
        clear_lines = (
            f"Regenerate clear scope: {clear_result.get('scope', BGIG_CLEAR_SCOPE)}\n"
            f"Regenerate BGIG scene roots before clear: {clear_result.get('scene_roots_before', 0)}\n"
            f"Regenerate BGIG scene roots deleted: {clear_result.get('scene_roots_deleted', 0)}\n"
            f"Regenerate legacy BGIG objects deleted: {clear_result.get('legacy_bgig_objects_deleted', 0)}\n"
            f"Regenerate tagged BGIG objects deleted total: {clear_result.get('deleted_objects', 0)}\n"
            f"Regenerate tagged BGIG objects skipped: {clear_result.get('skipped_objects', 0)}\n"
            f"Regenerate BGIG scene roots after clear: {clear_result.get('scene_roots_after', 0)}\n"
            f"Regenerate BGIG objects remaining after clear: {clear_result.get('bgig_objects_remaining', 0)}\n"
            f"Regenerate non-BGIG objects preserved: {clear_result.get('non_bgig_objects_preserved', 'yes')}\n"
        )
    source_path = request.config_json_path if request.source_kind == "config" else cad_ir_path
    overrides = request.parameter_overrides or {}
    return (
        "Board Game Insert Generator generated CAD IR scene from command UI.\n"
        f"Project: {generation_plan.project_name}\n"
        f"Action: {request.action}\n"
        f"Input mode used: {request.input_mode}\n"
        f"Source used: {request.source_kind}\n"
        f"Project root: {request.project_root if request.project_root is not None else 'not required'}\n"
        f"Config path: {request.config_json_path if request.config_json_path is not None else 'n/a'}\n"
        f"Source path: {source_path}\n"
        f"Input CAD IR: {cad_ir_path}\n"
        f"UI settings saved: {'yes' if settings_saved else 'no'}\n"
        f"Parametric overrides: {', '.join(sorted(overrides)) if overrides else 'none'}\n"
        f"Generation mode: {generation_plan.generation_mode}\n"
        f"{quick_parametric_report}"
        f"{quick_asset_report}"
        f"Reference outlines: {result['reference_outlines']}\n"
        f"Reference outline policy: {result.get('reference_outline_policy', 'single_xy_outline')}\n"
        f"Asset debug visualizations: {result.get('asset_debug_visualizations', 0)}\n"
        f"BGIG scene roots before: {scene_roots_before}\n"
        f"CAD IR module blanks planned: {len(generation_plan.blanks)}\n"
        f"Grid-positioned asset modules planned: {len(generation_plan.grid_positioned_blanks)}\n"
        f"Multi-layer grid modules planned: {generation_plan.multi_layer_grid_module_count}\n"
        f"Grid modules with Z placement: {generation_plan.grid_modules_with_z_placement_count}\n"
        f"Grid module height variants: {generation_plan.grid_module_height_variant_count}\n"
        f"Module components planned: {generation_plan.module_component_count}\n"
        f"Physical module count: {result['physical_module_count']}\n"
        f"Compact occurrences planned: {len(generation_plan.compact_occurrences)}\n"
        f"Exploded occurrences planned: {len(generation_plan.exploded_occurrences)}\n"
        f"BGIG scene id: {result.get('scene_id', 'unknown')}\n"
        f"BGIG scene roots created: {result['scene_roots_created']}\n"
        f"BGIG scene roots after: {scene_roots_after}\n"
        f"Registry validation: {result.get('registry_validation_status', 'not_run')}\n"
        f"Registry tagged BGIG entities after generation: {result.get('registry_tagged_bgig_entities', 0)}\n"
        f"Registry BGIG-looking untagged entities after generation: {result.get('registry_bgig_name_like_untagged_entities', 0)}\n"
        f"Module components created: {result['module_components_created']}\n"
        f"Source components created: {result['source_components_created']}\n"
        f"Component creation policy: {BGIG_COMPONENT_CREATION_POLICY}\n"
        f"Source/helper policy: {BGIG_SOURCE_HELPER_POLICY}\n"
        f"Scene ownership policy: {BGIG_SCENE_OWNERSHIP_POLICY}\n"
        f"Visible occurrence policy: {BGIG_VISIBLE_OCCURRENCE_POLICY}\n"
        f"Source/helper occurrences created: {result['source_helper_occurrences_created']}\n"
        f"Visible BGIG source/helper occurrences: {result['visible_source_helper_occurrences']}\n"
        f"Compact occurrences created: {result['compact_occurrences_created']}\n"
        f"Exploded occurrences created: {result['exploded_occurrences_created']}\n"
        f"Visible BGIG occurrences expected: {result['visible_bgig_occurrences_expected']}\n"
        f"Visible BGIG occurrences actual: {result['visible_bgig_occurrences_actual']}\n"
        f"Legacy bodies created: {result['legacy_bodies_created']}\n"
        f"Linked exploded occurrences: {result['linked_exploded_occurrences']}\n"
        "Occurrence direct rename attempted: no\n"
        f"Occurrence naming policy: {OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE}\n"
        "Occurrence Browser names: Fusion-generated; BGIG source Component names and plan roles are authoritative.\n"
        f"Grid-positioned modules refused: {len(generation_plan.rejected_grid_modules)}\n"
        f"Rectangular cuts total: {result['cavity_cuts']}\n"
        f"Top inset cuts planned/generated: {result['top_inset_cuts_planned']}/{result['top_inset_cuts_generated']}\n"
        f"Top inset grips planned/generated: {result['top_inset_grips_planned']}/{result['top_inset_grips_generated']}\n"
        f"Joined cap rails: {result.get('joined_rectangular_prisms', 0)}\n"
        f"Asset cavity policy: {result['asset_cavity_policy']}\n"
        f"Asset-fit cavities planned: {result['asset_fit_cavities_planned']}\n"
        f"Asset-fit cavities generated: {result['asset_fit_cavities_generated']}\n"
        f"Asset compartment cavities planned: {result['asset_compartment_cavities_planned']}\n"
        f"Asset compartment cavities generated: {result['asset_compartment_cavities_generated']}\n"
        f"Asset access features generated: {result['asset_access_features_generated']}\n"
        f"Asset access policy: {result['asset_access_policy']}\n"
        f"Asset access notches planned: {result['asset_access_notches_planned']}\n"
        f"Asset access notches generated: {result['asset_access_notches_generated']}\n"
        f"Asset access notches refused: {result['asset_access_notches_refused']}\n"
        f"Simple finger notch features planned: {result['finger_notch_features_planned']}\n"
        f"Simple finger notch sketches: {result['finger_notch_sketches']}\n"
        f"Simple top-open finger notch cuts: {result['finger_notch_cuts']}\n"
        f"Non-BGIG objects preserved: {result['non_bgig_objects_preserved']}\n"
        f"{clear_lines}"
        f"{module_mapping_report}"
        f"{body_size_report}"
        f"UI reopen policy: {BGIG_UI_REOPEN_POLICY}.\n"
        "Print validation: false.\n"
        "Status: manual validation required in Fusion 360."
    )


def _stable_generation_result(result: dict[str, object]) -> dict[str, object]:
    registry = result.get("registry_validation")
    defaults: dict[str, object] = {
        "scene_id": "unknown",
        "scene_roots_created": 0,
        "reference_outlines": 0,
        "asset_debug_visualizations": 0,
        "physical_module_count": 0,
        "module_components_created": 0,
        "source_components_created": 0,
        "source_helper_occurrences_created": 0,
        "source_helper_occurrences_visible": 0,
        "visible_source_helper_occurrences": 0,
        "compact_occurrences_created": 0,
        "exploded_occurrences_created": 0,
        "visible_bgig_occurrences_expected": 0,
        "visible_bgig_occurrences_actual": 0,
        "legacy_bodies_created": 0,
        "linked_exploded_occurrences": "no",
        "cavity_cuts": 0,
        "top_inset_cuts_planned": 0,
        "top_inset_cuts_generated": 0,
        "top_inset_grips_planned": 0,
        "top_inset_grips_generated": 0,
        "joined_rectangular_prisms": 0,
        "asset_cavity_policy": "none",
        "asset_fit_cavities_planned": 0,
        "asset_fit_cavities_generated": 0,
        "asset_compartment_cavities_planned": 0,
        "asset_compartment_cavities_generated": 0,
        "asset_access_features_generated": "no",
        "asset_access_policy": "none",
        "asset_access_notches_planned": 0,
        "asset_access_notches_generated": 0,
        "asset_access_notches_refused": 0,
        "finger_notch_features_planned": 0,
        "finger_notch_sketches": 0,
        "finger_notch_cuts": 0,
        "body_size_reports": [],
        "non_bgig_objects_preserved": "yes",
        "registry_validation_status": "not_run",
        "registry_tagged_bgig_entities": 0,
        "registry_bgig_name_like_untagged_entities": 0,
    }
    merged = {**defaults, **result}
    if isinstance(registry, dict):
        merged["registry_tagged_bgig_entities"] = registry.get("tagged_bgig_entities", 0)
        merged["registry_bgig_name_like_untagged_entities"] = registry.get("bgig_name_like_untagged_entities", 0)
    return merged


def _validate_generated_scene_registry(inspection: dict[str, object]) -> str:
    scene_roots = int(inspection.get("bgig_scene_roots_total", 0))
    if scene_roots != 1:
        raise FusionSkeletonError(
            "BGIG generation failed registry validation: generated scene could not be rediscovered. "
            f"BGIG scene roots found after generation: {scene_roots}."
        )
    if int(inspection.get("bgig_name_like_untagged_entities", 0)) != 0:
        return "ok_with_name_like_untagged_reported"
    return "ok"


def _bgig_attribute_groups() -> tuple[str, ...]:
    return (BGIG_ATTRIBUTE_GROUP, *BGIG_LEGACY_ATTRIBUTE_GROUPS)


class BgigFusionRegistry:
    """Central registry for BGIG Fusion ownership tags and scene cleanup."""

    def __init__(self, design) -> None:  # noqa: ANN001 - Fusion API object.
        self.design = design

    def create_scene_id(self) -> str:
        return f"bgig-{uuid.uuid4().hex[:12]}"

    def tag(self, entity, role: str, scene_id: str | None = None, module_id: str | None = None) -> bool:  # noqa: ANN001
        attributes = getattr(entity, "attributes", None)
        if attributes is None:
            return False
        try:
            attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_KIND, BGIG_ATTRIBUTE_VALUE)
            attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_ROLE_KEY, role)
            attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_VERSION_KEY, BGIG_ATTRIBUTE_VERSION_VALUE)
            if scene_id:
                attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_SCENE_ID_KEY, scene_id)
            if module_id:
                attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_MODULE_ID_KEY, module_id)
            return True
        except Exception:
            return False

    def inspect(self) -> dict[str, object]:
        root_occurrences = self.root_occurrences()
        all_occurrences = self.all_occurrences()
        components = self.components()
        bodies = self.bodies(components)
        sketches = self.sketches(components)
        features = self.features(components)
        tagged_entities = self.tagged_entities()
        scene_roots_by_attribute = self.scene_root_occurrences_by_attribute(root_occurrences)
        scene_roots_by_name = self.scene_root_occurrences_by_name(root_occurrences)
        scene_roots = self._unique_entities([*scene_roots_by_attribute, *scene_roots_by_name])
        tagged_keys = {self.entity_key(entity) for entity, _role in tagged_entities}
        candidate_entities = self._unique_entities([*root_occurrences, *components, *bodies, *sketches, *features])
        name_like = [
            entity
            for entity in candidate_entities
            if self.entity_key(entity) not in tagged_keys
            and not self.has_bgig_attribute(entity)
            and _looks_like_bgig_name(entity)
        ]
        role_counts = self.role_counts(tagged_entities)
        type_counts = self.type_counts(tagged_entities)
        tagged_lines = [self.entity_report_line(entity, role) for entity, role in tagged_entities]
        name_like_lines = [self.entity_report_line(entity, None) for entity in name_like]
        inconsistencies: list[str] = []
        if name_like:
            inconsistencies.append("- BGIG-looking visible/name-like entity without bgig attribute")
        if scene_roots_by_name and not scene_roots_by_attribute:
            inconsistencies.append("- BGIG Generated Scene found by name but not by scene_root attribute")
        if not scene_roots and tagged_entities:
            inconsistencies.append("- tagged BGIG entities exist but no root occurrence was found")
        if not inconsistencies:
            inconsistencies.append("- none")

        return {
            "root_occurrences_count": len(root_occurrences),
            "root_occurrence_names": _join_names(root_occurrences),
            "all_occurrences_count": len(all_occurrences),
            "components_count": len(components),
            "component_names": _join_names(components),
            "bodies_count": len(bodies),
            "body_names": _join_names(bodies),
            "sketches_count": len(sketches),
            "sketch_names": _join_names(sketches),
            "features_count": len(features),
            "feature_names": _join_names(features),
            "scene_roots_by_name": len(scene_roots_by_name),
            "scene_roots_by_attribute": len(scene_roots_by_attribute),
            "bgig_scene_roots_total": len(scene_roots),
            "bgig_scene_root_occurrences": len(scene_roots),
            "tagged_bgig_entities": len(tagged_entities),
            "tagged_bgig_unique_entities": len(tagged_entities),
            "tagged_bgig_attributes_found": self.bgig_attribute_count(),
            "bgig_name_like_untagged_entities": len(name_like),
            "occurrences_tagged": type_counts.get("occurrence", 0),
            "components_tagged": type_counts.get("component", 0),
            "bodies_tagged": type_counts.get("body", 0),
            "sketches_tagged": type_counts.get("sketch", 0),
            "features_tagged": type_counts.get("feature", 0),
            "role_count_summary": _format_counts(role_counts),
            "type_count_summary": _format_counts(type_counts),
            "tagged_entity_lines": tagged_lines,
            "name_like_untagged_lines": name_like_lines,
            "inconsistency_lines": inconsistencies,
            "registry_status": "inspect_only",
        }

    def clear(self, scene_roots_before: int | None = None) -> dict[str, object]:
        before = self.inspect()
        if scene_roots_before is None:
            scene_roots_before = int(before["bgig_scene_roots_total"])
        tagged_before = self.tagged_entities()
        root_occurrences = self.root_occurrences()
        scene_roots = self._unique_entities([
            *self.scene_root_occurrences_by_attribute(root_occurrences),
            *self.scene_root_occurrences_by_name(root_occurrences),
        ])
        scene_roots_deleted = 0
        skipped = 0
        for scene_root in scene_roots:
            delete_method = getattr(scene_root, "deleteMe", None)
            if delete_method is None:
                skipped += 1
                continue
            try:
                if delete_method() is False:
                    skipped += 1
                else:
                    scene_roots_deleted += 1
            except Exception:
                skipped += 1

        legacy_bgig_objects_deleted = 0
        for entity, role in self.tagged_entities():
            if role not in BGIG_CLEARABLE_ROLES and self.generated_by(entity) != BGIG_ATTRIBUTE_VALUE:
                skipped += 1
                continue
            delete_method = getattr(entity, "deleteMe", None)
            if delete_method is None:
                skipped += 1
                continue
            try:
                if delete_method() is False:
                    skipped += 1
                else:
                    legacy_bgig_objects_deleted += 1
            except Exception:
                skipped += 1

        after = self.inspect()
        deleted_objects = scene_roots_deleted + legacy_bgig_objects_deleted
        return {
            "scope": BGIG_CLEAR_SCOPE,
            "scene_roots_before": scene_roots_before,
            "scene_roots_found": len(scene_roots),
            "scene_roots_deleted": scene_roots_deleted,
            "tagged_objects_found": len(tagged_before),
            "legacy_bgig_objects_deleted": legacy_bgig_objects_deleted,
            "deleted_objects": deleted_objects,
            "skipped_objects": skipped,
            "scene_roots_after": after.get("bgig_scene_roots_total", 0),
            "bgig_objects_remaining": after.get("tagged_bgig_entities", 0),
            "visible_source_helper_occurrences_after": 0,
            "non_bgig_objects_preserved": "yes",
        }

    def tagged_entities(self) -> list[tuple[object, str | None]]:
        tagged_entities: list[tuple[object, str | None]] = []
        seen_entities = set()
        for group_name in _bgig_attribute_groups():
            for attribute in self.find_attributes(group_name, ""):
                entity = getattr(attribute, "parent", None)
                if entity is None:
                    continue
                entity_key = self.entity_key(entity)
                if entity_key in seen_entities:
                    continue
                role = self.role(entity)
                generated_by = self.generated_by(entity)
                if role is None and generated_by != BGIG_ATTRIBUTE_VALUE:
                    continue
                seen_entities.add(entity_key)
                tagged_entities.append((entity, role))
        return tagged_entities

    def find_attributes(self, group_name: str, attribute_name: str) -> list[object]:
        try:
            attributes = self.design.findAttributes(group_name, attribute_name)
        except Exception as exc:
            raise FusionSkeletonError(
                "Fusion could not inspect BGIG attributes for safe scene ownership. "
                "Generation refused to avoid duplicate or destructive behavior. "
                f"Original error: {exc}"
            ) from exc
        return list(_iter_fusion_collection(attributes))

    def root_occurrences(self) -> list[object]:
        root_component = getattr(self.design, "rootComponent", None)
        return list(_iter_fusion_collection(getattr(root_component, "occurrences", None)))

    def components(self) -> list[object]:
        components = []
        seen = set()
        root_component = getattr(self.design, "rootComponent", None)
        if root_component is not None:
            components.append(root_component)
            seen.add(id(root_component))
        for occurrence in self.all_occurrences():
            component = getattr(occurrence, "component", None)
            if component is not None and id(component) not in seen:
                components.append(component)
                seen.add(id(component))
        return components

    def all_occurrences(self) -> list[object]:
        all_occurrences: list[object] = []
        stack = list(self.root_occurrences())
        seen = set()
        while stack:
            occurrence = stack.pop(0)
            key = self.entity_key(occurrence)
            if key in seen:
                continue
            seen.add(key)
            all_occurrences.append(occurrence)
            component = getattr(occurrence, "component", None)
            child_occurrences = getattr(component, "occurrences", None)
            stack.extend(_iter_fusion_collection(child_occurrences))
        return all_occurrences

    def bodies(self, components: list[object]) -> list[object]:
        bodies: list[object] = []
        for component in components:
            bodies.extend(_iter_fusion_collection(getattr(component, "bRepBodies", None)))
        return self._unique_entities(bodies)

    def sketches(self, components: list[object]) -> list[object]:
        sketches: list[object] = []
        for component in components:
            sketches.extend(_iter_fusion_collection(getattr(component, "sketches", None)))
        return self._unique_entities(sketches)

    def features(self, components: list[object]) -> list[object]:
        features: list[object] = []
        for component in components:
            component_features = getattr(component, "features", None)
            if component_features is None:
                continue
            features.extend(_iter_fusion_collection(getattr(component_features, "extrudeFeatures", None)))
        return self._unique_entities(features)

    def scene_root_occurrences_by_attribute(self, root_occurrences: list[object]) -> list[object]:
        return [
            occurrence
            for occurrence in root_occurrences
            if self.role(occurrence) in (BGIG_SCENE_ROOT_ROLE, "scene_root_occurrence")
        ]

    def scene_root_occurrences_by_name(self, root_occurrences: list[object]) -> list[object]:
        roots = []
        for occurrence in root_occurrences:
            if _strict_bgig_scene_root_name(occurrence):
                roots.append(occurrence)
        return self._unique_entities(roots)

    def bgig_attribute_count(self) -> int:
        return sum(len(self.find_attributes(group_name, "")) for group_name in _bgig_attribute_groups())

    def has_bgig_attribute(self, entity) -> bool:  # noqa: ANN001
        return self.role(entity) is not None or self.generated_by(entity) == BGIG_ATTRIBUTE_VALUE

    def role_counts(self, tagged_entities: list[tuple[object, str | None]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for _entity, role in tagged_entities:
            key = role or "unknown"
            counts[key] = counts.get(key, 0) + 1
        return counts

    def type_counts(self, tagged_entities: list[tuple[object, str | None]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entity, _role in tagged_entities:
            key = _bgig_entity_category(entity)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def entity_key(self, entity) -> str:  # noqa: ANN001
        return _stable_entity_key(entity)

    def role(self, entity) -> str | None:  # noqa: ANN001
        return _bgig_attribute_value(entity, BGIG_ATTRIBUTE_ROLE_KEY)

    def scene_id(self, entity) -> str | None:  # noqa: ANN001
        return _bgig_attribute_value(entity, BGIG_ATTRIBUTE_SCENE_ID_KEY)

    def module_id(self, entity) -> str | None:  # noqa: ANN001
        return _bgig_attribute_value(entity, BGIG_ATTRIBUTE_MODULE_ID_KEY)

    def generated_by(self, entity) -> str | None:  # noqa: ANN001
        return _bgig_attribute_value(entity, BGIG_ATTRIBUTE_KIND)

    def entity_report_line(self, entity, role: str | None) -> str:  # noqa: ANN001
        return (
            f"- type={_fusion_entity_type(entity)}; "
            f"name={_safe_entity_name(entity)}; "
            f"role={role or self.role(entity) or 'n/a'}; "
            f"scene_id={self.scene_id(entity) or 'n/a'}; "
            f"module_id={self.module_id(entity) or 'n/a'}; "
            f"parent={_entity_context_name(entity)}; "
            f"visible={_bgig_entity_is_visible(entity)}"
        )

    def _unique_entities(self, entities: list[object]) -> list[object]:
        unique = []
        seen = set()
        for entity in entities:
            key = self.entity_key(entity)
            if key in seen:
                continue
            seen.add(key)
            unique.append(entity)
        return unique


def _iter_fusion_collection(collection) -> list[object]:  # noqa: ANN001
    if collection is None:
        return []
    if isinstance(collection, (list, tuple)):
        return list(collection)
    count = getattr(collection, "count", None)
    item = getattr(collection, "item", None)
    if isinstance(count, int) and callable(item):
        return [item(index) for index in range(count)]
    try:
        return list(collection)
    except TypeError:
        return []


def _stable_entity_key(entity) -> str:  # noqa: ANN001
    if entity is None:
        return "none"
    for attribute_name in ("entityToken", "tempId", "id"):
        try:
            value = getattr(entity, attribute_name, None)
            if value not in (None, ""):
                return f"{attribute_name}:{value}"
        except Exception:
            pass
    component = getattr(entity, "component", None)
    parent_component = getattr(entity, "parentComponent", None)
    assembly_context = getattr(entity, "assemblyContext", None)
    context = _safe_entity_name(component) or _safe_entity_name(parent_component) or _safe_entity_name(assembly_context)
    return f"{_bgig_entity_category(entity)}:{_fusion_entity_type(entity)}:{context}:{_safe_entity_name(entity)}"


def _bgig_entity_category(entity) -> str:  # noqa: ANN001
    type_text = _fusion_entity_type(entity).lower()
    if "occurrence" in type_text:
        return "occurrence"
    if "component" in type_text:
        return "component"
    if "body" in type_text or "brep" in type_text:
        return "body"
    if "sketch" in type_text:
        return "sketch"
    if "feature" in type_text or "extrude" in type_text:
        return "feature"
    role = _bgig_entity_role(entity)
    if role in (COMPACT_OCCURRENCE_ROLE, EXPLODED_OCCURRENCE_ROLE, BGIG_SCENE_ROOT_ROLE, "scene_root_occurrence"):
        return "occurrence"
    if role in ("scene_root_component", "module_component"):
        return "component"
    if role == "module_body":
        return "body"
    if (role and role.endswith("_sketch")) or role in {"box_reference", "reference_outline"}:
        return "sketch"
    if (role and role.endswith("_cut")) or role == "module_extrude":
        return "feature"
    return "other"


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _find_bgig_attributes(design, group_name: str, attribute_name: str):  # noqa: ANN001 - Fusion API object.
    return BgigFusionRegistry(design).find_attributes(group_name, attribute_name)


def _collect_bgig_tagged_entities(design) -> list[tuple[object, str | None]]:  # noqa: ANN001 - Fusion API object.
    return BgigFusionRegistry(design).tagged_entities()


def _bgig_scene_root_occurrences(design) -> list[object]:  # noqa: ANN001 - Fusion API object.
    registry = BgigFusionRegistry(design)
    root_occurrences = registry.root_occurrences()
    return registry._unique_entities([
        *registry.scene_root_occurrences_by_attribute(root_occurrences),
        *registry.scene_root_occurrences_by_name(root_occurrences),
    ])


def _count_bgig_scene_roots(design) -> int:  # noqa: ANN001 - Fusion API object.
    return len(_bgig_scene_root_occurrences(design))


def _count_bgig_tagged_objects(design) -> int:  # noqa: ANN001 - Fusion API object.
    return len(_collect_bgig_tagged_entities(design))


def _count_visible_bgig_occurrences_by_role(design, roles: tuple[str, ...]) -> int:  # noqa: ANN001 - Fusion API object.
    try:
        tagged_entities = _collect_bgig_tagged_entities(design)
    except Exception:
        return 0

    visible = 0
    for entity, role in tagged_entities:
        if role not in roles:
            continue
        if _bgig_entity_is_visible(entity):
            visible += 1
    return visible


def _bgig_entity_is_visible(entity) -> bool:  # noqa: ANN001 - Fusion API object.
    try:
        light_bulb = getattr(entity, "isLightBulbOn")
        if light_bulb is False:
            return False
    except Exception:
        pass
    try:
        return bool(getattr(entity, "isVisible"))
    except Exception:
        return True


def _clear_bgig_scene(design, scene_roots_before: int | None = None) -> dict[str, object]:  # noqa: ANN001 - Fusion API object.
    return BgigFusionRegistry(design).clear(scene_roots_before=scene_roots_before)


def _tag_bgig_entity(
    entity,
    role: str,
    scene_id: str | None = None,
    module_id: str | None = None,
    registry: BgigFusionRegistry | None = None,
) -> bool:  # noqa: ANN001 - Fusion API object.
    active_registry = registry
    if active_registry is None:
        return _tag_bgig_entity_direct(entity, role, scene_id=scene_id, module_id=module_id)
    return active_registry.tag(entity, role, scene_id=scene_id, module_id=module_id)


def _tag_bgig_entity_direct(entity, role: str, scene_id: str | None = None, module_id: str | None = None) -> bool:  # noqa: ANN001
    attributes = getattr(entity, "attributes", None)
    if attributes is None:
        return False
    try:
        attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_KIND, BGIG_ATTRIBUTE_VALUE)
        attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_ROLE_KEY, role)
        attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_VERSION_KEY, BGIG_ATTRIBUTE_VERSION_VALUE)
        if scene_id:
            attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_SCENE_ID_KEY, scene_id)
        if module_id:
            attributes.add(BGIG_ATTRIBUTE_GROUP, BGIG_ATTRIBUTE_MODULE_ID_KEY, module_id)
        return True
    except Exception:
        return False


def _bgig_entity_role(entity) -> str | None:  # noqa: ANN001 - Fusion API object.
    return _bgig_attribute_value(entity, BGIG_ATTRIBUTE_ROLE_KEY)


def _bgig_entity_generated_by(entity) -> str | None:  # noqa: ANN001 - Fusion API object.
    return _bgig_attribute_value(entity, BGIG_ATTRIBUTE_KIND)


def _bgig_attribute_value(entity, attribute_name: str) -> str | None:  # noqa: ANN001
    attributes = getattr(entity, "attributes", None)
    if attributes is None:
        return None
    for group_name in _bgig_attribute_groups():
        try:
            attribute = attributes.itemByName(group_name, attribute_name)
            if attribute is not None:
                return getattr(attribute, "value", None)
        except Exception:
            continue
    return None


def _strict_bgig_scene_root_name(entity) -> bool:  # noqa: ANN001
    if _safe_entity_name(entity) == BGIG_SCENE_ROOT_COMPONENT_NAME:
        return True
    component = getattr(entity, "component", None)
    return _safe_entity_name(component) == BGIG_SCENE_ROOT_COMPONENT_NAME


def _looks_like_bgig_name(entity) -> bool:  # noqa: ANN001
    name = _safe_entity_name(entity).lower()
    if not name:
        return False
    return "bgig" in name or "board game insert generator" in name or name == BGIG_SCENE_ROOT_COMPONENT_NAME.lower()


def _safe_entity_name(entity) -> str:  # noqa: ANN001
    if entity is None:
        return "n/a"
    try:
        name = getattr(entity, "name", "")
        if isinstance(name, str) and name:
            return name
    except Exception:
        pass
    return "n/a"


def _fusion_entity_type(entity) -> str:  # noqa: ANN001
    try:
        return type(entity).__name__
    except Exception:
        return "unknown"


def _entity_context_name(entity) -> str:  # noqa: ANN001
    for attr_name in ("parentComponent", "assemblyContext", "component", "parent"):
        try:
            parent = getattr(entity, attr_name, None)
            name = _safe_entity_name(parent)
            if name != "n/a":
                return name
        except Exception:
            continue
    return "n/a"


def _join_names(entities: list[object]) -> str:
    names = [_safe_entity_name(entity) for entity in entities]
    clean = [name for name in names if name != "n/a"]
    if not clean:
        return "none"
    return ", ".join(clean[:20]) + (" ..." if len(clean) > 20 else "")

def _active_design(application):  # noqa: ANN001 - Fusion API object.
    active_product = application.activeProduct if application else None
    if active_product is None:
        raise RuntimeError("No active Fusion product. Open or create a design first.")

    design = adsk.fusion.Design.cast(active_product)
    if design is None:
        raise RuntimeError("The active Fusion product is not a Design workspace.")
    return design


def _create_bgig_scene_root(root_component, registry: BgigFusionRegistry, scene_id: str):  # noqa: ANN001 - Fusion API object.
    transform = _matrix_for_origin(FusionVectorMm(0.0, 0.0, 0.0))
    try:
        occurrence = root_component.occurrences.addNewComponent(transform)
    except Exception as exc:
        if is_part_design_component_limit_error(exc):
            raise FusionAssemblyDocumentRequiredError(
                assembly_document_required_message(exc)
            ) from exc
        raise
    if occurrence is None:
        raise RuntimeError("Fusion component creation failed for BGIG Generated Scene.")
    _apply_occurrence_transform(occurrence, transform)
    _tag_bgig_entity(occurrence, BGIG_SCENE_ROOT_ROLE, scene_id=scene_id, registry=registry)
    component = occurrence.component
    if component is None:
        raise RuntimeError("BGIG Generated Scene component is unavailable.")
    component.name = BGIG_SCENE_ROOT_COMPONENT_NAME
    _tag_bgig_entity(component, "scene_root_component", scene_id=scene_id, registry=registry)
    return occurrence, component

def _generate_from_plan(design, plan: FusionGenerationPlan, registry: BgigFusionRegistry, scene_id: str) -> dict[str, object]:  # noqa: ANN001
    root_component = design.rootComponent
    _scene_occurrence, scene_component = _create_bgig_scene_root(root_component, registry, scene_id)
    reference_outlines = _create_reference_box_outlines(scene_component, plan.reference_box)
    for reference_outline in reference_outlines:
        _tag_bgig_entity(reference_outline, "box_reference", scene_id=scene_id, registry=registry)

    source_blanks = [*plan.blanks, *plan.grid_positioned_blanks]
    compact_occurrences_by_component_id = {
        occurrence.component_id: occurrence for occurrence in plan.compact_occurrences
    }
    created_bodies = {}
    created_components = {}
    compact_occurrence_count = 0
    asset_debug_visualization_count = 0

    for blank in source_blanks:
        occurrence_plan = compact_occurrences_by_component_id.get(blank.cad_id)
        if occurrence_plan is None:
            raise RuntimeError(f"Missing compact occurrence plan for {blank.body_name}.")
        occurrence, body, asset_debug_count = _create_module_component_occurrence(
            scene_component,
            blank,
            occurrence_plan,
            registry,
            scene_id,
        )
        created_bodies[blank.cad_id] = body
        asset_debug_visualization_count += asset_debug_count
        created_components[blank.cad_id] = occurrence.component
        compact_occurrence_count += 1

    source_blanks_by_id = {blank.cad_id: blank for blank in source_blanks}

    additive_prism_join_count = 0
    for join_plan in plan.additive_prism_joins:
        target_body = created_bodies.get(join_plan.target_body_id)
        target_component = created_components.get(join_plan.target_body_id)
        if target_body is None or target_component is None:
            raise RuntimeError(
                f"Additive prism {join_plan.operation_id} targets unknown body "
                f"{join_plan.target_body_id}."
            )
        _create_joined_rectangular_prism(
            target_component,
            join_plan,
            target_body,
            registry,
            scene_id,
        )
        additive_prism_join_count += 1

    asset_fit_cavity_cuts_planned = sum(
        1 for cavity_cut in plan.cavity_cuts if getattr(cavity_cut, "cavity_source", "") in {"asset_fit_cavity", "asset_compartment_cavity"}
    )
    asset_compartment_cavity_cuts_planned = sum(
        1 for cavity_cut in plan.cavity_cuts if getattr(cavity_cut, "cavity_source", "") == "asset_compartment_cavity"
    )
    planned_asset_cavity_policies = [
        str(getattr(cavity_cut, "policy", "") or "")
        for cavity_cut in plan.cavity_cuts
        if getattr(cavity_cut, "cavity_source", "") in {"asset_fit_cavity", "asset_compartment_cavity"}
    ]
    top_inset_cuts_planned = sum(
        1 for cavity_cut in plan.cavity_cuts
        if getattr(cavity_cut, "cavity_source", "") == "top_inset_reservation"
    )
    top_inset_grips_planned = sum(
        1 for cavity_cut in plan.cavity_cuts
        if getattr(cavity_cut, "cavity_source", "") == "top_inset_grip"
    )
    asset_fit_cavity_cuts_generated = 0
    asset_compartment_cavity_cuts_generated = 0
    top_inset_cuts_generated = 0
    top_inset_grips_generated = 0
    cavity_cut_count = 0
    for cavity_cut in plan.cavity_cuts:
        target_body = created_bodies.get(cavity_cut.target_body_id)
        target_component = created_components.get(cavity_cut.target_body_id)
        source_blank = source_blanks_by_id.get(cavity_cut.target_body_id)
        if target_body is None or target_component is None or source_blank is None:
            raise RuntimeError(
                f"Cavity {cavity_cut.cavity_id} targets unknown body "
                f"{cavity_cut.target_body_id}."
            )
        _create_rectangular_cavity_cut(
            target_component,
            cavity_cut,
            target_body,
            source_blank.origin_mm,
            registry,
            scene_id,
        )
        cavity_cut_count += 1
        if getattr(cavity_cut, "cavity_source", "") in {"asset_fit_cavity", "asset_compartment_cavity"}:
            asset_fit_cavity_cuts_generated += 1
        if getattr(cavity_cut, "cavity_source", "") == "asset_compartment_cavity":
            asset_compartment_cavity_cuts_generated += 1
        if getattr(cavity_cut, "cavity_source", "") == "top_inset_reservation":
            top_inset_cuts_generated += 1
        if getattr(cavity_cut, "cavity_source", "") == "top_inset_grip":
            top_inset_grips_generated += 1

    asset_access_notch_cuts_planned = sum(
        1 for notch_cut in plan.finger_notch_cuts if getattr(notch_cut, "source_feature_kind", "") == "asset_access_notch"
    )
    finger_notch_sketch_count = 0
    finger_notch_cut_count = 0
    asset_access_notch_cut_count = 0
    for notch_cut in plan.finger_notch_cuts:
        target_body = created_bodies.get(notch_cut.target_body_id)
        target_component = created_components.get(notch_cut.target_body_id)
        source_blank = source_blanks_by_id.get(notch_cut.target_body_id)
        if target_body is None or target_component is None or source_blank is None:
            raise RuntimeError(
                f"Finger notch {notch_cut.feature_id} targets unknown body "
                f"{notch_cut.target_body_id}."
            )
        result = _create_rectangular_finger_notch_cut(
            target_component,
            notch_cut,
            target_body,
            source_blank.origin_mm,
            registry,
            scene_id,
        )
        finger_notch_sketch_count += result["sketches"]
        finger_notch_cut_count += result["cuts"]
        if getattr(notch_cut, "source_feature_kind", "") == "asset_access_notch":
            asset_access_notch_cut_count += result["cuts"]

    body_size_reports = [
        _fusion_body_size_report(blank, created_bodies[blank.cad_id])
        for blank in source_blanks
    ]

    exploded_occurrence_count = 0
    for occurrence_plan in plan.exploded_occurrences:
        module_component = created_components.get(occurrence_plan.component_id)
        if module_component is None:
            raise RuntimeError(
                f"Exploded occurrence {occurrence_plan.occurrence_name!r} targets unknown "
                f"component {occurrence_plan.component_id!r}."
            )
        _create_linked_module_occurrence(
            scene_component,
            module_component,
            occurrence_plan,
            EXPLODED_OCCURRENCE_ROLE,
            registry,
            scene_id,
        )
        exploded_occurrence_count += 1

    visible_occurrences_expected = compact_occurrence_count + exploded_occurrence_count
    visible_occurrences_actual = _count_visible_bgig_occurrences_by_role(
        design,
        (COMPACT_OCCURRENCE_ROLE, EXPLODED_OCCURRENCE_ROLE),
    )
    visible_source_helpers = 0

    return {
        "scene_id": scene_id,
        "scene_roots_created": 1,
        "reference_outlines": len(reference_outlines),
        "reference_outline_policy": "bottom_and_top_box_xy_outlines",
        "asset_debug_visualizations": asset_debug_visualization_count,
        "physical_module_count": len(source_blanks),
        "module_components_created": len(created_components),
        "source_components_created": len(created_components),
        "source_helper_occurrences_created": 0,
        "source_helper_occurrences_visible": 0,
        "visible_source_helper_occurrences": visible_source_helpers,
        "compact_occurrences_created": compact_occurrence_count,
        "exploded_occurrences_created": exploded_occurrence_count,
        "visible_bgig_occurrences_expected": visible_occurrences_expected,
        "visible_bgig_occurrences_actual": visible_occurrences_actual,
        "legacy_bodies_created": 0,
        "linked_exploded_occurrences": "yes" if plan.linked_exploded_occurrences else "no",
        "cavity_cuts": cavity_cut_count,
        "top_inset_cuts_planned": top_inset_cuts_planned,
        "top_inset_cuts_generated": top_inset_cuts_generated,
        "top_inset_grips_planned": top_inset_grips_planned,
        "top_inset_grips_generated": top_inset_grips_generated,
        "joined_rectangular_prisms": additive_prism_join_count,
        "asset_cavity_policy": planned_asset_cavity_policies[0] if planned_asset_cavity_policies else "none",
        "asset_fit_cavities_planned": asset_fit_cavity_cuts_planned,
        "asset_fit_cavities_generated": asset_fit_cavity_cuts_generated,
        "asset_compartment_cavities_planned": asset_compartment_cavity_cuts_planned,
        "asset_compartment_cavities_generated": asset_compartment_cavity_cuts_generated,
        "asset_access_features_generated": "yes" if asset_access_notch_cut_count > 0 else "no",
        "asset_access_policy": "per_compartment_top_open_rectangular_notch_v0" if asset_access_notch_cuts_planned > 0 else "none",
        "asset_access_notches_planned": asset_access_notch_cuts_planned,
        "asset_access_notches_generated": asset_access_notch_cut_count,
        "asset_access_notches_refused": 0,
        "finger_notch_features_planned": len(plan.finger_notch_cuts),
        "finger_notch_sketches": finger_notch_sketch_count,
        "finger_notch_cuts": finger_notch_cut_count,
        "body_size_reports": body_size_reports,
        "non_bgig_objects_preserved": "yes",
    }

def _fusion_body_size_report(solid_plan: FusionSolidPlan, body) -> dict[str, object]:  # noqa: ANN001
    planned_size_mm = solid_plan.printable_body_size_mm or solid_plan.size_mm
    actual_bbox_mm = _body_bounding_box_size_mm(body)
    return {
        "module_id": solid_plan.cad_id,
        "body_name": solid_plan.body_name,
        "body_size_source": solid_plan.body_size_source or ("printable_body_size_mm" if solid_plan.printable_body_size_mm else "size_mm"),
        "grid_semantics": solid_plan.grid_semantics,
        "body_snap_to_grid": solid_plan.body_snap_to_grid,
        "grid_span_is_reserved_space": solid_plan.grid_span_is_reserved_space,
        "body_size_may_be_smaller_than_grid_span": solid_plan.body_size_may_be_smaller_than_grid_span,
        "grid_span_mm": _vector_to_optional_dict(solid_plan.theoretical_grid_extent_mm),
        "asset_fit_size_mm": _vector_to_optional_dict(solid_plan.asset_fit_size_mm),
        "printable_body_size_planned_mm": planned_size_mm.to_dict(),
        "actual_fusion_body_bbox_mm": _vector_to_optional_dict(actual_bbox_mm),
        "size_match": _vectors_match_mm(planned_size_mm, actual_bbox_mm) if actual_bbox_mm is not None else "unknown",
    }


def _body_bounding_box_size_mm(body) -> FusionVectorMm | None:  # noqa: ANN001
    try:
        bounding_box = body.boundingBox
    except Exception:
        return None
    if bounding_box is None:
        return None
    return FusionVectorMm(
        round((bounding_box.maxPoint.x - bounding_box.minPoint.x) * 10.0, 4),
        round((bounding_box.maxPoint.y - bounding_box.minPoint.y) * 10.0, 4),
        round((bounding_box.maxPoint.z - bounding_box.minPoint.z) * 10.0, 4),
    )


def _vectors_match_mm(expected: FusionVectorMm, actual: FusionVectorMm, tolerance_mm: float = 0.05) -> bool:
    return (
        abs(expected.x - actual.x) <= tolerance_mm
        and abs(expected.y - actual.y) <= tolerance_mm
        and abs(expected.z - actual.z) <= tolerance_mm
    )


def _vector_to_optional_dict(vector: FusionVectorMm | None) -> dict[str, float] | None:
    return vector.to_dict() if vector is not None else None


def _module_mapping_report_message(generation_plan: FusionGenerationPlan) -> str:
    source_blanks = [*generation_plan.blanks, *generation_plan.grid_positioned_blanks]
    if not source_blanks:
        return "Module source mapping: none\n"
    compact_ids = {occurrence.component_id for occurrence in generation_plan.compact_occurrences}
    exploded_ids = {occurrence.component_id for occurrence in generation_plan.exploded_occurrences}
    lines = ["Module source mapping:"]
    for blank in source_blanks:
        view_roles = []
        if blank.cad_id in compact_ids:
            view_roles.append("compact")
        if blank.cad_id in exploded_ids:
            view_roles.append("exploded")
        clearance = blank.clearance_applied or {}
        assets = ", ".join(blank.source_asset_ids) if blank.source_asset_ids else "n/a"
        candidate = blank.candidate_id or "n/a"
        lines.append(
            f"- {blank.cad_id}: "
            f"source {blank.module_source}; "
            f"placement {blank.placement_source}; "
            f"assets {assets}; "
            f"candidate {candidate}; "
            f"views {'/'.join(view_roles) if view_roles else 'none'}; "
            f"origin {_format_size_mm(blank.origin_mm.to_dict())}; "
            f"grid span {_format_size_mm(_vector_to_optional_dict(blank.theoretical_grid_extent_mm))}; "
            f"grid semantics {blank.grid_semantics or 'n/a'}; "
            f"body snap to grid {blank.body_snap_to_grid or 'n/a'}; "
            f"grid span reserved {blank.grid_span_is_reserved_space or 'n/a'}; "
            f"body may be smaller than grid span {blank.body_size_may_be_smaller_than_grid_span or 'n/a'}; "
            f"printable body {_format_size_mm((blank.printable_body_size_mm or blank.size_mm).to_dict())}; "
            f"peripheral clearance {_format_clearance_value(clearance.get('peripheral_clearance_mm'))}; "
            f"inter-module clearance {_format_clearance_value(clearance.get('inter_module_gap_mm'))}; "
            f"size source {blank.body_size_source or 'size_mm'}"
        )
    return "\n".join(lines) + "\n"

def _body_size_report_message(reports) -> str:  # noqa: ANN001
    if not isinstance(reports, list) or not reports:
        return ""
    lines = ["Body sizing report:"]
    for report in reports:
        lines.append(
            f"- {report.get('module_id')}: "
            f"source {report.get('body_size_source')}; "
            f"grid span {_format_size_mm(report.get('grid_span_mm'))}; "
            f"grid semantics {report.get('grid_semantics') or 'n/a'}; "
            f"body snap to grid {report.get('body_snap_to_grid') or 'n/a'}; "
            f"grid span reserved {report.get('grid_span_is_reserved_space') or 'n/a'}; "
            f"body may be smaller than grid span {report.get('body_size_may_be_smaller_than_grid_span') or 'n/a'}; "
            f"asset fit {_format_size_mm(report.get('asset_fit_size_mm'))}; "
            f"printable body planned {_format_size_mm(report.get('printable_body_size_planned_mm'))}; "
            f"actual Fusion body bbox {_format_size_mm(report.get('actual_fusion_body_bbox_mm'))}; "
            f"size match {_format_size_match(report.get('size_match'))}"
        )
    return "\n".join(lines) + "\n"


def _format_size_mm(value) -> str:  # noqa: ANN001
    if not isinstance(value, dict):
        return "n/a"
    return f"{value.get('x')} x {value.get('y')} x {value.get('z')} mm"


def _format_clearance_value(value) -> str:  # noqa: ANN001
    if isinstance(value, (int, float)):
        return f"{value} mm"
    return "n/a"

def _format_size_match(value) -> str:  # noqa: ANN001
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown"


def _create_reference_box_outlines(root_component, solid_plan: FusionSolidPlan) -> list:  # noqa: ANN001
    if solid_plan.origin_mm.z != 0:
        raise RuntimeError("Reference box outline must stay on Z origin 0 mm.")
    bottom = _create_reference_outline_at_z(root_component, solid_plan, 0.0, "bottom")
    top = _create_reference_outline_at_z(root_component, solid_plan, solid_plan.size_mm.z, "top")
    return [bottom, top]


def _create_reference_outline_at_z(root_component, solid_plan: FusionSolidPlan, z_mm: float, label: str):  # noqa: ANN001
    sketch_plane = _xy_plane_for_z(root_component, z_mm, f"{solid_plan.component_name} {label} outline plane")
    sketch = root_component.sketches.add(sketch_plane)
    sketch.name = f"{solid_plan.component_name} {label} outline"
    _add_scene_rectangle(sketch, solid_plan)
    return sketch


def _create_module_component_occurrence(
    root_component,  # noqa: ANN001
    solid_plan: FusionSolidPlan,
    occurrence_plan,  # noqa: ANN001
    registry: BgigFusionRegistry,
    scene_id: str,
):
    transform = _matrix_for_origin(occurrence_plan.origin_mm)
    try:
        occurrence = root_component.occurrences.addNewComponent(transform)
    except Exception as exc:
        if is_part_design_component_limit_error(exc):
            raise FusionAssemblyDocumentRequiredError(
                assembly_document_required_message(exc)
            ) from exc
        raise
    if occurrence is None:
        raise RuntimeError(
            "Fusion component creation failed. Use an assembly-capable Fusion design "
            "for linked compact/exploded module occurrences."
        )
    _apply_occurrence_transform(occurrence, transform)
    _tag_bgig_entity(
        occurrence,
        COMPACT_OCCURRENCE_ROLE,
        scene_id=scene_id,
        module_id=solid_plan.cad_id,
        registry=registry,
    )

    module_component = occurrence.component
    if module_component is None:
        raise RuntimeError(f"Fusion component is unavailable for {solid_plan.body_name}.")
    module_component.name = solid_plan.component_name
    _tag_bgig_entity(
        module_component,
        "module_component",
        scene_id=scene_id,
        module_id=solid_plan.cad_id,
        registry=registry,
    )
    body = _create_rectangular_blank(
        module_component,
        _local_solid_plan(solid_plan),
        registry=registry,
        scene_id=scene_id,
        module_id=solid_plan.cad_id,
    )
    asset_debug_count = _create_asset_fit_debug_outline(
        module_component,
        solid_plan,
        registry=registry,
        scene_id=scene_id,
        module_id=solid_plan.cad_id,
    )
    return occurrence, body, asset_debug_count


def _create_asset_fit_debug_outline(
    target_component,  # noqa: ANN001
    solid_plan: FusionSolidPlan,
    registry: BgigFusionRegistry | None = None,
    scene_id: str | None = None,
    module_id: str | None = None,
) -> int:
    if solid_plan.module_source != "asset_candidate" or solid_plan.asset_fit_size_mm is None:
        return 0
    clearance = solid_plan.clearance_applied or {}
    origin_x = float(clearance.get("wall_thickness_mm", 0.0) or 0.0)
    origin_y = float(clearance.get("wall_thickness_mm", 0.0) or 0.0)
    if origin_x + solid_plan.asset_fit_size_mm.x > solid_plan.size_mm.x:
        origin_x = 0.0
    if origin_y + solid_plan.asset_fit_size_mm.y > solid_plan.size_mm.y:
        origin_y = 0.0
    sketch_plane = _xy_plane_for_z(
        target_component,
        solid_plan.size_mm.z,
        f"{solid_plan.component_name} asset-fit debug plane",
    )
    sketch = target_component.sketches.add(sketch_plane)
    sketch.name = f"{solid_plan.component_name} asset-fit debug outline"
    if registry is not None:
        _tag_bgig_entity(sketch, "asset_debug_sketch", scene_id=scene_id, module_id=module_id, registry=registry)
    _add_scene_rectangle_from_mm(
        sketch,
        origin_x,
        origin_y,
        solid_plan.asset_fit_size_mm.x,
        solid_plan.asset_fit_size_mm.y,
        f"{solid_plan.component_name} asset-fit debug outline",
    )
    payload = solid_plan.asset_fit_cavity
    if isinstance(payload, dict) and payload.get("policy") == "per_source_asset_rectangular_compartments_v0":
        compartments = payload.get("compartments")
        if isinstance(compartments, list):
            for compartment in compartments:
                if not isinstance(compartment, dict):
                    continue
                local_origin = compartment.get("local_origin_mm")
                size = compartment.get("size_mm")
                if not isinstance(local_origin, dict) or not isinstance(size, dict):
                    continue
                try:
                    _add_scene_rectangle_from_mm(
                        sketch,
                        float(local_origin.get("x", 0.0)),
                        float(local_origin.get("y", 0.0)),
                        float(size.get("x", 0.0)),
                        float(size.get("y", 0.0)),
                        str(compartment.get("id") or "asset-compartment"),
                    )
                except Exception:
                    continue
    return 1


def _create_linked_module_occurrence(
    scene_component,  # noqa: ANN001
    module_component,  # noqa: ANN001
    occurrence_plan,  # noqa: ANN001
    occurrence_role: str,
    registry: BgigFusionRegistry,
    scene_id: str,
):
    transform = _matrix_for_origin(occurrence_plan.origin_mm)
    try:
        occurrence = scene_component.occurrences.addExistingComponent(module_component, transform)
    except Exception as exc:
        if is_part_design_component_limit_error(exc):
            raise FusionAssemblyDocumentRequiredError(
                assembly_document_required_message(exc)
            ) from exc
        raise
    if occurrence is None:
        raise RuntimeError(
            f"Fusion linked occurrence failed for {occurrence_plan.occurrence_name}."
        )
    _apply_occurrence_transform(occurrence, transform)
    _tag_bgig_entity(
        occurrence,
        occurrence_role,
        scene_id=scene_id,
        module_id=occurrence_plan.component_id,
        registry=registry,
    )
    return occurrence

def _create_rectangular_blank(target_component, solid_plan: FusionSolidPlan, registry: BgigFusionRegistry | None = None, scene_id: str | None = None, module_id: str | None = None):  # noqa: ANN001
    sketch_plane = _xy_plane_for_z(target_component, solid_plan.origin_mm.z, f"{solid_plan.component_name} footprint plane")
    sketch = target_component.sketches.add(sketch_plane)
    sketch.name = f"{solid_plan.component_name} footprint"
    if registry is not None:
        _tag_bgig_entity(sketch, "module_sketch", scene_id=scene_id, module_id=module_id, registry=registry)
    _add_scene_rectangle(sketch, solid_plan)

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed profile was created for {solid_plan.body_name}.")

    profile = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByString(f"{solid_plan.size_mm.z} mm")
    extrude = target_component.features.extrudeFeatures.addSimple(
        profile,
        distance,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    if extrude is None:
        raise RuntimeError(f"Fusion extrusion failed for {solid_plan.body_name}.")

    extrude.name = f"{solid_plan.component_name} extrusion"
    if extrude.bodies.count < 1:
        raise RuntimeError(f"Fusion extrusion created no body for {solid_plan.body_name}.")
    body = extrude.bodies.item(0)
    body.name = solid_plan.body_name
    if registry is not None:
        _tag_bgig_entity(body, "module_body", scene_id=scene_id, module_id=module_id, registry=registry)
        _tag_bgig_entity(extrude, "module_extrude", scene_id=scene_id, module_id=module_id, registry=registry)
    return body


def _create_joined_rectangular_prism(
    target_component,  # noqa: ANN001
    join_plan: FusionAdditivePrismPlan,
    target_body,  # noqa: ANN001
    registry: BgigFusionRegistry | None = None,
    scene_id: str | None = None,
) -> None:
    plane = _create_offset_xy_plane(
        target_component,
        join_plan.local_origin_mm.z,
        f"{join_plan.component_name} {join_plan.operation_id} additive prism plane",
    )
    sketch = target_component.sketches.add(plane)
    sketch.name = f"{join_plan.component_name} {join_plan.operation_id} additive prism footprint"
    if registry is not None:
        _tag_bgig_entity(
            sketch,
            "mechanism_rail_sketch",
            scene_id=scene_id,
            module_id=join_plan.target_body_id,
            registry=registry,
        )
    _add_scene_rectangle_from_mm(
        sketch,
        join_plan.local_origin_mm.x,
        join_plan.local_origin_mm.y,
        join_plan.size_mm.x,
        join_plan.size_mm.y,
        join_plan.operation_id,
    )
    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed additive profile was created for {join_plan.operation_id}.")
    extrudes = target_component.features.extrudeFeatures
    join_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    if join_input is None:
        raise RuntimeError(f"Fusion join input failed for {join_plan.operation_id}.")
    distance = adsk.core.ValueInput.createByString(f"{join_plan.size_mm.z} mm")
    extent = adsk.fusion.DistanceExtentDefinition.create(distance)
    if extent is None:
        raise RuntimeError(f"Fusion join extent failed for {join_plan.operation_id}.")
    if not join_input.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection):
        raise RuntimeError(f"Fusion join distance failed for {join_plan.operation_id}.")
    join_input.participantBodies = [target_body]
    feature = extrudes.add(join_input)
    if feature is None:
        raise RuntimeError(f"Fusion join failed for {join_plan.operation_id}.")
    feature.name = f"{join_plan.component_name} {join_plan.operation_id} joined rail"
    if registry is not None:
        _tag_bgig_entity(
            feature,
            "mechanism_rail_join",
            scene_id=scene_id,
            module_id=join_plan.target_body_id,
            registry=registry,
        )

def _create_rectangular_cavity_cut(
    target_component,  # noqa: ANN001
    cut_plan: FusionCavityCutPlan,
    target_body,  # noqa: ANN001
    body_origin_mm: FusionVectorMm,
    registry: BgigFusionRegistry | None = None,
    scene_id: str | None = None,
) -> None:
    local_cut_origin = _relative_vector(cut_plan.cut_origin_mm, body_origin_mm)
    is_top_inset = str(getattr(cut_plan, "cavity_source", "")).startswith("top_inset")
    feature_label = "top inset" if is_top_inset else "cavity"
    sketch_role = "top_inset_sketch" if is_top_inset else "cavity_sketch"
    cut_role = "top_inset_cut" if is_top_inset else "cavity_cut"
    cut_plane = _create_offset_xy_plane(
        target_component,
        local_cut_origin.z,
        f"{cut_plan.component_name} {cut_plan.cavity_id} {feature_label} cut plane",
    )
    sketch = target_component.sketches.add(cut_plane)
    sketch.name = f"{cut_plan.component_name} {cut_plan.cavity_id} {feature_label} footprint"
    if registry is not None:
        _tag_bgig_entity(sketch, sketch_role, scene_id=scene_id, module_id=cut_plan.target_body_id, registry=registry)
    _add_scene_rectangle_from_mm(
        sketch,
        local_cut_origin.x,
        local_cut_origin.y,
        cut_plan.cut_size_mm.x,
        cut_plan.cut_size_mm.y,
        cut_plan.cavity_id,
    )

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed cut profile was created for {cut_plan.cavity_id}.")

    profile = sketch.profiles.item(0)
    extrudes = target_component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    if cut_input is None:
        raise RuntimeError(f"Fusion cut input failed for cavity {cut_plan.cavity_id}.")

    distance = adsk.core.ValueInput.createByString(f"{cut_plan.cut_size_mm.z} mm")
    extent = adsk.fusion.DistanceExtentDefinition.create(distance)
    if extent is None:
        raise RuntimeError(f"Fusion cut extent failed for cavity {cut_plan.cavity_id}.")
    ok = cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    if not ok:
        raise RuntimeError(f"Fusion cut distance failed for cavity {cut_plan.cavity_id}.")

    cut_input.participantBodies = [target_body]
    cut_feature = extrudes.add(cut_input)
    if cut_feature is None:
        raise RuntimeError(f"Fusion cut failed for cavity {cut_plan.cavity_id}.")
    cut_feature.name = f"{cut_plan.component_name} {cut_plan.cavity_id} {feature_label} cut"
    if registry is not None:
        _tag_bgig_entity(cut_feature, cut_role, scene_id=scene_id, module_id=cut_plan.target_body_id, registry=registry)


def _create_rectangular_finger_notch_cut(
    target_component,  # noqa: ANN001
    cut_plan: FusionFingerNotchCutPlan,
    target_body,  # noqa: ANN001
    body_origin_mm: FusionVectorMm,
    registry: BgigFusionRegistry | None = None,
    scene_id: str | None = None,
) -> dict[str, int]:
    cut_plane = _create_finger_notch_plane(target_component, cut_plan, body_origin_mm)
    sketch = target_component.sketches.add(cut_plane)
    sketch.name = f"{cut_plan.component_name} {cut_plan.feature_id} finger notch wall footprint"
    if registry is not None:
        _tag_bgig_entity(sketch, "finger_notch_sketch", scene_id=scene_id, module_id=cut_plan.target_body_id, registry=registry)
    _add_model_space_rectangle_on_sketch(
        sketch,
        _relative_vector(cut_plan.profile_start_mm, body_origin_mm),
        _relative_vector(cut_plan.profile_end_mm, body_origin_mm),
        cut_plan.feature_id,
    )

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed wall cut profile was created for {cut_plan.feature_id}.")

    profile = sketch.profiles.item(0)
    extrudes = target_component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    if cut_input is None:
        raise RuntimeError(f"Fusion cut input failed for finger notch {cut_plan.feature_id}.")

    distance = adsk.core.ValueInput.createByString(f"{cut_plan.cut_depth_mm} mm")
    extent = adsk.fusion.DistanceExtentDefinition.create(distance)
    if extent is None:
        raise RuntimeError(f"Fusion cut extent failed for finger notch {cut_plan.feature_id}.")
    ok = cut_input.setOneSideExtent(
        extent,
        _fusion_extent_direction(cut_plan.extrude_direction),
    )
    if not ok:
        raise RuntimeError(f"Fusion cut distance failed for finger notch {cut_plan.feature_id}.")

    cut_input.participantBodies = [target_body]
    cut_feature = extrudes.add(cut_input)
    if cut_feature is None:
        raise RuntimeError(f"Fusion cut failed for finger notch {cut_plan.feature_id}.")
    cut_feature.name = f"{cut_plan.component_name} {cut_plan.feature_id} finger notch wall cut"
    if registry is not None:
        _tag_bgig_entity(cut_feature, "finger_notch_cut", scene_id=scene_id, module_id=cut_plan.target_body_id, registry=registry)
    return {"sketches": 1, "cuts": 1}


def _create_finger_notch_plane(
    target_component,  # noqa: ANN001
    cut_plan: FusionFingerNotchCutPlan,
    body_origin_mm: FusionVectorMm,
):
    if cut_plan.sketch_plane == FUSION_SKETCH_PLANE_XZ:
        return _create_offset_xz_plane(
            target_component,
            cut_plan.sketch_plane_offset_mm - body_origin_mm.y,
            f"{cut_plan.component_name} {cut_plan.feature_id} finger notch XZ wall cut plane",
        )
    if cut_plan.sketch_plane == FUSION_SKETCH_PLANE_YZ:
        return _create_offset_yz_plane(
            target_component,
            cut_plan.sketch_plane_offset_mm - body_origin_mm.x,
            f"{cut_plan.component_name} {cut_plan.feature_id} finger notch YZ wall cut plane",
        )
    raise RuntimeError(
        f"Unsupported finger notch sketch plane {cut_plan.sketch_plane!r} for {cut_plan.feature_id}."
    )


def _fusion_extent_direction(direction: str):  # noqa: ANN001
    if direction == FUSION_EXTENT_POSITIVE:
        return adsk.fusion.ExtentDirections.PositiveExtentDirection
    if direction == FUSION_EXTENT_NEGATIVE:
        return adsk.fusion.ExtentDirections.NegativeExtentDirection
    raise RuntimeError(f"Unsupported Fusion extent direction {direction!r}.")



def _matrix_for_origin(origin_mm: FusionVectorMm):  # noqa: ANN001
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(
        mm_to_cm(origin_mm.x),
        mm_to_cm(origin_mm.y),
        mm_to_cm(origin_mm.z),
    )
    return transform


def _apply_occurrence_transform(occurrence, transform) -> None:  # noqa: ANN001
    try:
        occurrence.transform2 = transform
    except Exception:
        try:
            occurrence.transform = transform
        except Exception:
            pass


def _local_solid_plan(solid_plan: FusionSolidPlan) -> FusionSolidPlan:
    return FusionSolidPlan(
        cad_id=solid_plan.cad_id,
        component_name=solid_plan.component_name,
        body_name=solid_plan.body_name,
        origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
        size_mm=solid_plan.size_mm,
        role=solid_plan.role,
        printable=solid_plan.printable,
        operation_kind=solid_plan.operation_kind,
        validation_status=solid_plan.validation_status,
    )


def _relative_vector(vector: FusionVectorMm, origin: FusionVectorMm) -> FusionVectorMm:
    return FusionVectorMm(
        vector.x - origin.x,
        vector.y - origin.y,
        vector.z - origin.z,
    )


def _xy_plane_for_z(root_component, offset_z_mm: float, name: str):  # noqa: ANN001
    if offset_z_mm == 0:
        return root_component.xYConstructionPlane
    return _create_offset_xy_plane(root_component, offset_z_mm, name)

def _create_offset_xy_plane(root_component, offset_z_mm: float, name: str):  # noqa: ANN001
    plane_input = root_component.constructionPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(f"{offset_z_mm} mm")
    ok = plane_input.setByOffset(root_component.xYConstructionPlane, offset)
    if not ok:
        raise RuntimeError(f"Fusion construction plane offset failed for {name}.")
    plane = root_component.constructionPlanes.add(plane_input)
    if plane is None:
        raise RuntimeError(f"Fusion construction plane creation failed for {name}.")
    plane.name = name
    return plane


def _create_offset_xz_plane(root_component, offset_y_mm: float, name: str):  # noqa: ANN001
    plane_input = root_component.constructionPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(f"{offset_y_mm} mm")
    ok = plane_input.setByOffset(root_component.xZConstructionPlane, offset)
    if not ok:
        raise RuntimeError(f"Fusion construction plane offset failed for {name}.")
    plane = root_component.constructionPlanes.add(plane_input)
    if plane is None:
        raise RuntimeError(f"Fusion construction plane creation failed for {name}.")
    plane.name = name
    return plane


def _create_offset_yz_plane(root_component, offset_x_mm: float, name: str):  # noqa: ANN001
    plane_input = root_component.constructionPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(f"{offset_x_mm} mm")
    ok = plane_input.setByOffset(root_component.yZConstructionPlane, offset)
    if not ok:
        raise RuntimeError(f"Fusion construction plane offset failed for {name}.")
    plane = root_component.constructionPlanes.add(plane_input)
    if plane is None:
        raise RuntimeError(f"Fusion construction plane creation failed for {name}.")
    plane.name = name
    return plane


def _add_scene_rectangle(sketch, solid_plan: FusionSolidPlan) -> None:  # noqa: ANN001
    _add_scene_rectangle_from_mm(
        sketch,
        solid_plan.origin_mm.x,
        solid_plan.origin_mm.y,
        solid_plan.size_mm.x,
        solid_plan.size_mm.y,
        solid_plan.body_name,
    )


def _add_scene_rectangle_from_mm(
    sketch,  # noqa: ANN001
    origin_x_mm: float,
    origin_y_mm: float,
    size_x_mm: float,
    size_y_mm: float,
    label: str,
) -> None:
    start = adsk.core.Point3D.create(
        mm_to_cm(origin_x_mm),
        mm_to_cm(origin_y_mm),
        0,
    )
    end = adsk.core.Point3D.create(
        mm_to_cm(origin_x_mm + size_x_mm),
        mm_to_cm(origin_y_mm + size_y_mm),
        0,
    )
    lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(start, end)
    if lines is None:
        raise RuntimeError(f"Fusion rectangle sketch failed for {label}.")


def _add_model_space_rectangle_on_sketch(
    sketch,  # noqa: ANN001
    start_mm,  # noqa: ANN001
    end_mm,  # noqa: ANN001
    label: str,
) -> None:
    model_start = adsk.core.Point3D.create(
        mm_to_cm(start_mm.x),
        mm_to_cm(start_mm.y),
        mm_to_cm(start_mm.z),
    )
    model_end = adsk.core.Point3D.create(
        mm_to_cm(end_mm.x),
        mm_to_cm(end_mm.y),
        mm_to_cm(end_mm.z),
    )
    start = sketch.modelToSketchSpace(model_start)
    end = sketch.modelToSketchSpace(model_end)
    if start is None or end is None:
        raise RuntimeError(f"Fusion model-to-sketch conversion failed for {label}.")

    lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(start, end)
    if lines is None:
        raise RuntimeError(f"Fusion wall rectangle sketch failed for {label}.")


def _show_message(message: str) -> None:
    if _ui is not None:
        _ui.messageBox(message)
