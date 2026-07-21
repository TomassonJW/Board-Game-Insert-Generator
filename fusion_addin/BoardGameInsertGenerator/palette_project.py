"""Pure project bridge for the embedded Fusion palette.

This module deliberately has no ``adsk`` dependency.  The HTML palette edits a
draft, while this bridge owns normalization, validation, P55 envelope
derivation and atomic local persistence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from typing import Any


PALETTE_REQUEST_SCHEMA = "bgig.palette.request.v1"
PALETTE_RESPONSE_SCHEMA = "bgig.palette.response.v1"
CURRENT_PROJECT_FILENAME = "bgig_project_v1.json"
PROJECT_EXPORT_DIRECTORY = "projects"
PERSONAL_PRESETS_FILENAME = "bgig_personal_element_presets_v1.json"
DOCUMENT_STATE_FILENAME = "bgig_document_state_v1.json"
DOCUMENT_STATE_SCHEMA = "bgig.document_state.v1"
SUPPORTED_ACTIONS = frozenset({
    "load_project", "new_project", "validate_project",
    "save_project", "autosave_project", "save_document", "save_project_as",
    "open_project_file", "open_recent_project", "import_project", "export_project",
    "solve_project", "finalize_project", "materialize_project", "regenerate_project",
    "save_personal_preset", "delete_personal_preset",
    "import_personal_presets", "export_personal_presets", "save_solver_settings",
})
_LOCAL_ANALYSIS_ENGINE_LIMIT = 8
_LOCAL_ANALYSIS_ENGINES: OrderedDict[tuple[str, str], object] = OrderedDict()
_STAGED_CALCULATION_SESSION_LIMIT = 8
_STAGED_CALCULATION_SESSIONS: OrderedDict[str, object] = OrderedDict()


class PaletteProjectError(ValueError):
    """Raised when a palette request cannot be handled safely."""


def handle_palette_request(
    raw_request: object,
    addin_dir: str | Path,
    project_root: str | Path | None = None,
) -> dict[str, object]:
    """Handle one versioned palette request and return a versioned response."""

    request_id = "unknown"
    try:
        request = _mapping(raw_request, "request")
        request_id = _text(request.get("request_id"), "request.request_id")
        if request.get("schema") != PALETTE_REQUEST_SCHEMA:
            raise PaletteProjectError(f"Schema de message non pris en charge : {request.get('schema')!r}.")
        action = _text(request.get("action"), "request.action")
        if action not in SUPPORTED_ACTIONS:
            raise PaletteProjectError(f"Action de palette inconnue : {action}.")
        _ensure_engine_available(Path(addin_dir), None if project_root is None else Path(project_root))
        return _dispatch(action, request, Path(addin_dir), request_id)
    except Exception as exc:
        return _response(
            request_id,
            "invalid",
            errors=[_french_error(exc)],
            solver_result=_invalid_solver_result(request_id, _request_revision(raw_request)),
        )


def load_current_project(addin_dir: str | Path, project_root: str | Path | None = None) -> dict[str, object]:
    """Load and normalize the current project, or return a valid blank project."""

    root = Path(addin_dir)
    _ensure_engine_available(root, None if project_root is None else Path(project_root))
    from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft

    path = current_project_path(root)
    if not path.is_file():
        return blank_project_v1()
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PaletteProjectError(f"Le projet local est illisible : {exc}.") from exc
    return normalize_project_draft(raw).project


def current_project_path(addin_dir: str | Path) -> Path:
    """Return update-safe local storage, distinct from technical add-in settings."""

    override = os.environ.get("BGIG_USER_DATA_DIR", "").strip()
    root = Path(override) if override else Path.home() / "Documents" / "BGIG" / PROJECT_EXPORT_DIRECTORY
    return root / CURRENT_PROJECT_FILENAME


def current_personal_presets_path(addin_dir: str | Path) -> Path:
    """Return update-safe personal preset storage beside the current project."""

    return current_project_path(addin_dir).parent / PERSONAL_PRESETS_FILENAME


def document_state_path(addin_dir: str | Path) -> Path:
    """Return local metadata for the named document and recent documents."""

    return current_project_path(addin_dir).parent / DOCUMENT_STATE_FILENAME


def project_document_directory(addin_dir: str | Path) -> Path:
    """Return the user-visible default folder for BGIG documents."""

    return current_project_path(addin_dir).parent


def load_document_state(addin_dir: str | Path) -> dict[str, object]:
    """Load local document metadata without making a document mandatory."""

    path = document_state_path(addin_dir)
    default = {
        "schema_version": DOCUMENT_STATE_SCHEMA,
        "current_path": "",
        "recent_paths": [],
        "solver_settings": _normalize_solver_settings(None),
    }
    if not path.is_file():
        return default
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return default
    if not isinstance(raw, dict) or raw.get("schema_version") != DOCUMENT_STATE_SCHEMA:
        return default
    current = raw.get("current_path")
    recent = raw.get("recent_paths")
    return {
        "schema_version": DOCUMENT_STATE_SCHEMA,
        "current_path": current if isinstance(current, str) else "",
        "recent_paths": [item for item in recent if isinstance(item, str)] if isinstance(recent, list) else [],
        "solver_settings": _normalize_solver_settings(raw.get("solver_settings")),
    }


def _write_document_state(addin_dir: Path, state: dict[str, object]) -> None:
    payload = {
        "schema_version": DOCUMENT_STATE_SCHEMA,
        "current_path": str(state.get("current_path") or ""),
        "recent_paths": [str(item) for item in state.get("recent_paths", []) if isinstance(item, str)][:12],
        "solver_settings": _normalize_solver_settings(state.get("solver_settings")),
    }
    _write_json_atomic(document_state_path(addin_dir), payload)


def _normalize_solver_settings(value: object) -> dict[str, str]:
    """Keep palette-local solver choices within the core public vocabulary."""

    from board_game_insert_generator.solver_settings import normalize_solver_settings

    return normalize_solver_settings(value)


def _record_current_document(state: dict[str, object], document_path: Path) -> dict[str, object]:
    resolved = str(document_path.resolve())
    previous = [str(item) for item in state.get("recent_paths", []) if isinstance(item, str)]
    state["current_path"] = resolved
    state["recent_paths"] = [resolved, *[item for item in previous if item != resolved]][:12]
    return state


def _document_info(addin_dir: Path, state: dict[str, object]) -> dict[str, object]:
    current = str(state.get("current_path") or "")
    recent_paths = [str(item) for item in state.get("recent_paths", []) if isinstance(item, str)]
    existing_recent = [item for item in recent_paths if Path(item).is_file()]
    if current and not Path(current).is_file():
        current = ""
    return {
        "schema_version": DOCUMENT_STATE_SCHEMA,
        "current_path": current,
        "current_name": Path(current).name if current else "",
        "project_directory": str(project_document_directory(addin_dir)),
        "recovery_path": str(current_project_path(addin_dir)),
        "recovery_available": current_project_path(addin_dir).is_file(),
        "recent_documents": [
            {"path": item, "name": Path(item).name}
            for item in existing_recent
        ],
    }


def _document_path_from_request(
    request: dict[str, object],
    *,
    field: str = "document_path",
    must_exist: bool = False,
) -> Path:
    value = request.get(field)
    if not isinstance(value, str) or not value.strip():
        raise PaletteProjectError("Le chemin du document doit etre renseigne.")
    path = Path(value).expanduser()
    if path.suffix.lower() != ".json":
        path = path.with_suffix(".bgig.json")
    resolved = path.resolve()
    if must_exist and not resolved.is_file():
        raise PaletteProjectError("Le document choisi est introuvable.")
    return resolved


def _load_project_document(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PaletteProjectError(f"Le document choisi est illisible : {exc}.") from exc


def _dispatch(action: str, request: dict[str, object], addin_dir: Path, request_id: str) -> dict[str, object]:
    from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
    from board_game_insert_generator.top_inset_reservation import (
        compatibility_flat_stack_payload, derive_top_inset_reservations,
    )
    from board_game_insert_generator.partition_cad import build_partition_cad
    from board_game_insert_generator.partition_result_view import build_partition_result_view
    from board_game_insert_generator.container_sizing_view import build_container_sizing_view
    from board_game_insert_generator.personal_presets import (
        delete_personal_preset, load_personal_presets, normalize_personal_presets,
        save_personal_preset, write_personal_presets,
    )
    from board_game_insert_generator.project_presets import build_creation_presets
    from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft

    document_state = load_document_state(addin_dir)
    solver_settings = _normalize_solver_settings(
        request.get("solver_settings", document_state.get("solver_settings"))
    )
    if action == "save_solver_settings":
        document_state["solver_settings"] = solver_settings
        _write_document_state(addin_dir, document_state)
        return _response(
            request_id,
            "ready",
            solver_settings=solver_settings,
            document=_document_info(addin_dir, document_state),
        )
    if action == "load_project":
        project = load_current_project(addin_dir)
        return _response(
            request_id,
            "ready",
            project=project,
            creation_presets=build_creation_presets(project),
            personal_presets=load_personal_presets(current_personal_presets_path(addin_dir)),
            saved=current_project_path(addin_dir).is_file(),
            recovery_saved=current_project_path(addin_dir).is_file(),
            document=_document_info(addin_dir, document_state),
            solver_settings=solver_settings,
        )
    if action == "new_project":
        project = blank_project_v1()
        fresh_state = {
            "schema_version": DOCUMENT_STATE_SCHEMA,
            "current_path": "",
            "recent_paths": document_state.get("recent_paths", []),
            "solver_settings": solver_settings,
        }
        _write_document_state(addin_dir, fresh_state)
        return _response(
            request_id,
            "ready",
            project=project,
            creation_presets=build_creation_presets(project),
            personal_presets=load_personal_presets(current_personal_presets_path(addin_dir)),
            document=_document_info(addin_dir, fresh_state),
            solver_settings=solver_settings,
        )

    project_value = request.get("project")
    opened_document: Path | None = None
    if action == "open_project_file":
        opened_document = _document_path_from_request(request, must_exist=True)
        project_value = _load_project_document(opened_document)
    elif action == "open_recent_project":
        opened_document = _document_path_from_request(request, must_exist=True)
        allowed = {str(item) for item in document_state.get("recent_paths", []) if isinstance(item, str)}
        if str(opened_document) not in allowed:
            raise PaletteProjectError("Ce document ne fait pas partie des projets recents BGIG.")
        project_value = _load_project_document(opened_document)
    elif action == "import_project" and isinstance(request.get("project_json"), str):
        try:
            project_value = json.loads(str(request["project_json"]))
        except json.JSONDecodeError as exc:
            raise PaletteProjectError(f"Le fichier importe n est pas un JSON valide : {exc.msg}.") from exc

    normalization = normalize_project_draft(project_value)
    project = normalization.project
    envelopes = derive_expandable_envelope_contract(project)
    top_insets = derive_top_inset_reservations(project)
    flat_stack = {
        "schema_version": top_insets["schema_version"],
        "flat_stack": compatibility_flat_stack_payload(top_insets),
        "top_inset_reservations": top_insets,
        "summary": top_insets["summary"],
        "blockers": top_insets["blockers"],
    }
    local_analysis = _contextual_local_analysis(
        project,
        addin_dir,
        effort_profile=solver_settings["effort"],
    )
    local_frontiers, local_frontier_digests = _local_analysis_artifacts(
        addin_dir,
        effort_profile=solver_settings["effort"],
    )
    staged_session = _staged_calculation_session(project, addin_dir, solver_settings)
    staged_calculation = staged_session.synchronize(
        project,
        local_analysis,
        solver_settings=solver_settings,
        container_frontiers=local_frontiers,
        frontier_digests=local_frontier_digests,
    )
    creation_presets = build_creation_presets(
        project,
        storage_height_mm=float(top_insets["design_top_z_mm"]),
    )
    preset_path = current_personal_presets_path(addin_dir)
    personal_presets = load_personal_presets(preset_path)
    if action == "save_personal_preset":
        content_id = _text(request.get("content_id"), "request.content_id")
        preset_name = _text(request.get("preset_name"), "request.preset_name")
        content = next((item for item in project["contents"] if item["id"] == content_id), None)
        if content is None:
            raise PaletteProjectError(f"Element introuvable pour le preset : {content_id}.")
        personal_presets = save_personal_preset(preset_path, name=preset_name, content=content)
    elif action == "delete_personal_preset":
        personal_presets = delete_personal_preset(
            preset_path, _text(request.get("preset_id"), "request.preset_id")
        )
    elif action == "import_personal_presets":
        raw_json = _text(request.get("preset_json"), "request.preset_json")
        try:
            imported = normalize_personal_presets(json.loads(raw_json))
        except json.JSONDecodeError as exc:
            raise PaletteProjectError(f"Le fichier de presets n est pas un JSON valide : {exc.msg}.") from exc
        write_personal_presets(preset_path, imported)
        personal_presets = imported

    staged_solver_result: dict[str, object] | None = None
    partition: dict[str, object] | None = None
    artifact_selection: dict[str, object] | None = None
    artifact_kind = str(request.get("artifact_kind") or "minimal_layout")
    if (
        action == "validate_project"
        and staged_calculation.get("local_reuse", {}).get("status")
        == "placement_reused"
    ):
        partition = staged_session.current_minimal_partition()
        staged_solver_result = _partition_solver_result(partition)
    elif action == "solve_project":
        staged_action = staged_session.calculate_layout(
            request_id=request_id,
            request_revision=_request_revision(request),
        )
        partition = staged_action["partition"]
        staged_solver_result = staged_action["solver_result"]
        staged_calculation = staged_action["staged_calculation"]
    elif action == "finalize_project":
        staged_action = staged_session.finalize_volume()
        partition = staged_action["partition"]
        staged_solver_result = staged_action["solver_result"]
        staged_calculation = staged_action["staged_calculation"]
    elif action in {"materialize_project", "regenerate_project"}:
        artifact_selection = staged_session.select_materializable_artifact(artifact_kind)
        partition = artifact_selection["partition"]
        staged_solver_result = _partition_solver_result(partition)
    container_sizing = build_container_sizing_view(project, envelopes, partition)
    result_view = (
        build_partition_result_view(partition)
        if partition is not None
        and partition["summary"]["status"] in {"constructed", "proposal_with_residuals"}
        else None
    )
    if result_view is not None:
        if action in {"solve_project", "validate_project"}:
            minimal_current = bool(
                staged_calculation.get("minimal_layout", {}).get("placement_certified")
            )
            result_view["artifact_kind"] = "minimal_layout"
            result_view["materializable"] = minimal_current
            result_view.setdefault("invariants", {})[
                "minimal_materialization_without_finalization"
            ] = minimal_current
        elif artifact_selection is not None:
            result_view["artifact_kind"] = artifact_selection["artifact_kind"]
            result_view["materializable"] = True
            result_view.setdefault("invariants", {})[
                "selected_artifact_identity_exact"
            ] = True
    cad_build = (
        build_partition_cad(
            project,
            partition=partition,
            solver_method=solver_settings["method"],
            effort_profile=solver_settings["effort"],
            artifact_identity=artifact_selection,
        )
        if action in {"materialize_project", "regenerate_project"}
        else None
    )
    if cad_build is not None and cad_build.get("status") == "ready_for_fusion":
        staged_session.record_cad_ready(cad_build)
        staged_calculation = staged_session.snapshot()
    saved = False
    recovery_saved = False
    export_path = ""
    if action in {"save_project", "autosave_project"}:
        _write_json_atomic(current_project_path(addin_dir), project)
        recovery_saved = True
        saved = action == "save_project"
    elif action == "import_project":
        _write_json_atomic(current_project_path(addin_dir), project)
        document_state["current_path"] = ""
        _write_document_state(addin_dir, document_state)
        recovery_saved = True
        saved = True
    elif action == "save_document":
        current = str(document_state.get("current_path") or "")
        if not current:
            raise PaletteProjectError("Ce nouveau projet n a pas encore de fichier. Utilise Enregistrer sous.")
        named_path = Path(current)
        _write_json_atomic(named_path, project)
        _write_json_atomic(current_project_path(addin_dir), project)
        _record_current_document(document_state, named_path)
        _write_document_state(addin_dir, document_state)
        saved = True
        recovery_saved = True
    elif action == "save_project_as":
        named_path = _document_path_from_request(request)
        _write_json_atomic(named_path, project)
        _write_json_atomic(current_project_path(addin_dir), project)
        _record_current_document(document_state, named_path)
        _write_document_state(addin_dir, document_state)
        saved = True
        recovery_saved = True
        export_path = str(named_path)
    elif action in {"open_project_file", "open_recent_project"}:
        if opened_document is None:
            raise PaletteProjectError("Le document choisi est introuvable.")
        _write_json_atomic(current_project_path(addin_dir), project)
        _record_current_document(document_state, opened_document)
        _write_document_state(addin_dir, document_state)
        recovery_saved = True
    elif action == "export_project":
        export_path = str(_export_project(addin_dir, project))
    elif action == "export_personal_presets":
        preset_export = current_project_path(addin_dir).parent / "mes-presets-elements.bgig.json"
        write_personal_presets(preset_export, personal_presets)
        export_path = str(preset_export)

    warnings: list[str] = []
    if normalization.migrated:
        warnings.append(f"Projet migre depuis {normalization.source_schema} vers bgig.project.v1.")
    return _response(
        request_id,
        "ready",
        project=project,
        creation_presets=creation_presets,
        personal_presets=personal_presets,
        envelopes=envelopes,
        container_sizing=container_sizing,
        flat_stack=flat_stack,
        local_analysis=local_analysis,
        staged_calculation=staged_calculation,
        partition=partition,
        result_view=result_view,
        solver_result=staged_solver_result or _partition_solver_result(partition),
        cad_build=cad_build,
        saved=saved,
        recovery_saved=recovery_saved,
        migrated=normalization.migrated,
        warnings=warnings,
        export_path=export_path,
        document=_document_info(addin_dir, document_state),
        solver_settings=solver_settings,
    )


def _response(
    request_id: str,
    status: str,
    *,
    project: dict[str, object] | None = None,
    creation_presets: dict[str, object] | None = None,
    personal_presets: dict[str, object] | None = None,
    envelopes: dict[str, object] | None = None,
    container_sizing: dict[str, object] | None = None,
    flat_stack: dict[str, object] | None = None,
    local_analysis: dict[str, object] | None = None,
    staged_calculation: dict[str, object] | None = None,
    partition: dict[str, object] | None = None,
    result_view: dict[str, object] | None = None,
    cad_build: dict[str, object] | None = None,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    saved: bool = False,
    migrated: bool = False,
    export_path: str = "",
    document: dict[str, object] | None = None,
    recovery_saved: bool = False,
    solver_result: dict[str, object] | None = None,
    solver_settings: dict[str, str] | None = None,
) -> dict[str, object]:
    return {
        "schema": PALETTE_RESPONSE_SCHEMA,
        "request_id": request_id,
        "status": status,
        "project": deepcopy(project),
        "project_digest": _project_digest(project),
        "lifecycle": {
            "source": "current" if project is not None else "invalid",
            "derived": "current" if envelopes is not None and flat_stack is not None else "pending",
            "solved": "current" if partition is not None else "not_computed",
            "materialized": (
                "cad_ready"
                if isinstance(cad_build, dict) and cad_build.get("status") == "ready_for_fusion"
                else "blocked"
                if cad_build is not None
                else "not_materialized"
            ),
        },
        "creation_presets": deepcopy(creation_presets),
        "personal_presets": deepcopy(personal_presets),
        "envelopes": deepcopy(envelopes),
        "container_sizing": deepcopy(container_sizing),
        "flat_stack": deepcopy(flat_stack),
        "local_analysis": deepcopy(local_analysis),
        "staged_calculation": deepcopy(staged_calculation),
        "partition": deepcopy(partition),
        "result_view": deepcopy(result_view),
        "solver_result": deepcopy(solver_result),
        "solver_settings": deepcopy(solver_settings),
        "cad_build": deepcopy(cad_build),
        "errors": list(errors or []),
        "warnings": list(warnings or []),
        "saved": saved,
        "migrated": migrated,
        "export_path": export_path,
        "document": deepcopy(document),
        "recovery_saved": recovery_saved,
    }



def _contextual_local_analysis(
    project: dict[str, object],
    addin_dir: Path,
    *,
    effort_profile: str,
) -> dict[str, object]:
    """Reuse one bounded in-memory L01/L02 engine per local document and effort."""

    from board_game_insert_generator.contextual_local_analysis import (
        IncrementalLocalAnalysisEngine,
    )

    engine_key = (str(current_project_path(addin_dir).resolve()), effort_profile)
    engine = _LOCAL_ANALYSIS_ENGINES.get(engine_key)
    if engine is None:
        engine = IncrementalLocalAnalysisEngine(
            project,
            effort_profile=effort_profile,
        )
        _LOCAL_ANALYSIS_ENGINES[engine_key] = engine
        while len(_LOCAL_ANALYSIS_ENGINES) > _LOCAL_ANALYSIS_ENGINE_LIMIT:
            _LOCAL_ANALYSIS_ENGINES.popitem(last=False)
        return engine.snapshot()
    _LOCAL_ANALYSIS_ENGINES.move_to_end(engine_key)
    return engine.update_project(project)


def _local_analysis_artifacts(
    addin_dir: Path,
    *,
    effort_profile: str,
) -> tuple[tuple[object, ...], tuple[tuple[str, str], ...]]:
    """Expose the exact cached L02 frontiers consumed by the minimal solver."""

    engine_key = (str(current_project_path(addin_dir).resolve()), effort_profile)
    engine = _LOCAL_ANALYSIS_ENGINES.get(engine_key)
    if engine is None:
        raise PaletteProjectError(
            "Les frontieres locales courantes sont indisponibles ; relance l analyse locale."
        )
    return tuple(engine.certified_frontiers()), tuple(engine.frontier_digests())

def _staged_calculation_session(
    project: dict[str, object],
    addin_dir: Path,
    solver_settings: dict[str, str],
) -> object:
    """Reuse one bounded in-memory P64-L03 session per local document."""

    from board_game_insert_generator.staged_calculation import (
        StagedCalculationSession,
    )

    session_key = str(current_project_path(addin_dir).resolve())
    session = _STAGED_CALCULATION_SESSIONS.get(session_key)
    if session is None:
        session = StagedCalculationSession(
            project,
            solver_settings=solver_settings,
        )
        _STAGED_CALCULATION_SESSIONS[session_key] = session
        while len(_STAGED_CALCULATION_SESSIONS) > _STAGED_CALCULATION_SESSION_LIMIT:
            _STAGED_CALCULATION_SESSIONS.popitem(last=False)
        return session
    _STAGED_CALCULATION_SESSIONS.move_to_end(session_key)
    return session


def _request_revision(raw_request: object) -> int | None:
    if not isinstance(raw_request, dict):
        return None
    value = raw_request.get("source_revision")
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _partition_solver_result(partition: dict[str, object] | None) -> dict[str, object] | None:
    if not isinstance(partition, dict):
        return None
    solver = partition.get("solver")
    if not isinstance(solver, dict):
        return None
    result = solver.get("result")
    if not isinstance(result, dict):
        return None
    payload = deepcopy(result)
    payload["telemetry"] = deepcopy(solver.get("telemetry"))
    return payload


def _invalid_solver_result(request_id: str, request_revision: int | None) -> dict[str, object]:
    from board_game_insert_generator.solver_outcome import invalid_input_result

    return invalid_input_result(request_id, request_revision)


def _project_digest(project: dict[str, object] | None) -> str:
    """Return a stable source digest without moving business logic to the palette."""

    if project is None:
        return ""
    canonical = json.dumps(project, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _export_project(addin_dir: Path, project: dict[str, object]) -> Path:
    name = str(project.get("project_name", "projet-bgig"))
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "projet-bgig"
    path = current_project_path(addin_dir).parent / f"{slug}.bgig.json"
    _write_json_atomic(path, project)
    return path


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _ensure_engine_available(addin_dir: Path, project_root: Path | None) -> None:
    candidates = [addin_dir / "lib"]
    if project_root is not None:
        candidates.insert(0, project_root / "src")
    for candidate in candidates:
        if candidate.is_dir() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    try:
        __import__("board_game_insert_generator.project_v1")
    except ImportError as exc:
        raise PaletteProjectError(
            "Le moteur BGIG est absent de l add-in. Reinstalle BGIG avant de reessayer."
        ) from exc


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PaletteProjectError(f"{field} doit etre un objet JSON.")
    return value


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PaletteProjectError(f"{field} doit etre renseigne.")
    return value.strip()


def _french_error(exc: Exception) -> str:
    if isinstance(exc, PaletteProjectError):
        return str(exc)
    return f"Le projet n est pas valide : {exc}"
