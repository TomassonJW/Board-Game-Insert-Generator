"""Pure project bridge for the embedded Fusion palette.

This module deliberately has no ``adsk`` dependency.  The HTML palette edits a
draft, while this bridge owns normalization, validation, P55 envelope
derivation and atomic local persistence.
"""

from __future__ import annotations

import json
import os
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


PALETTE_REQUEST_SCHEMA = "bgig.palette.request.v1"
PALETTE_RESPONSE_SCHEMA = "bgig.palette.response.v1"
CURRENT_PROJECT_FILENAME = "bgig_project_v1.json"
PROJECT_EXPORT_DIRECTORY = "projects"
SUPPORTED_ACTIONS = frozenset({"load_project", "validate_project", "save_project", "import_project", "export_project", "solve_project"})


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
        return _response(request_id, "invalid", errors=[_french_error(exc)])


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


def _dispatch(action: str, request: dict[str, object], addin_dir: Path, request_id: str) -> dict[str, object]:
    from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
    from board_game_insert_generator.flat_stack_reservation import derive_flat_stack_reservation
    from board_game_insert_generator.partition_result_view import build_partition_result_view
    from board_game_insert_generator.partition_solver import solve_partition_plan
    from board_game_insert_generator.project_v1 import normalize_project_draft

    if action == "load_project":
        project = load_current_project(addin_dir)
        return _response(request_id, "ready", project=project, saved=current_project_path(addin_dir).is_file())

    project_value = request.get("project")
    if action == "import_project" and isinstance(request.get("project_json"), str):
        try:
            project_value = json.loads(str(request["project_json"]))
        except json.JSONDecodeError as exc:
            raise PaletteProjectError(f"Le fichier importe n est pas un JSON valide : {exc.msg}.") from exc

    normalization = normalize_project_draft(project_value)
    project = normalization.project
    envelopes = derive_expandable_envelope_contract(project)
    flat_stack = derive_flat_stack_reservation(project)
    partition = solve_partition_plan(project) if action == "solve_project" else None
    result_view = (
        build_partition_result_view(partition)
        if partition is not None and partition["summary"]["status"] == "constructed"
        else None
    )
    saved = False
    export_path = ""
    if action in {"save_project", "import_project"}:
        _write_json_atomic(current_project_path(addin_dir), project)
        saved = True
    elif action == "export_project":
        export_path = str(_export_project(addin_dir, project))

    warnings: list[str] = []
    if normalization.migrated:
        warnings.append(f"Projet migre depuis {normalization.source_schema} vers bgig.project.v1.")
    return _response(
        request_id,
        "ready",
        project=project,
        envelopes=envelopes,
        flat_stack=flat_stack,
        partition=partition,
        result_view=result_view,
        saved=saved,
        migrated=normalization.migrated,
        warnings=warnings,
        export_path=export_path,
    )


def _response(
    request_id: str,
    status: str,
    *,
    project: dict[str, object] | None = None,
    envelopes: dict[str, object] | None = None,
    flat_stack: dict[str, object] | None = None,
    partition: dict[str, object] | None = None,
    result_view: dict[str, object] | None = None,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    saved: bool = False,
    migrated: bool = False,
    export_path: str = "",
) -> dict[str, object]:
    return {
        "schema": PALETTE_RESPONSE_SCHEMA,
        "request_id": request_id,
        "status": status,
        "project": deepcopy(project),
        "envelopes": deepcopy(envelopes),
        "flat_stack": deepcopy(flat_stack),
        "partition": deepcopy(partition),
        "result_view": deepcopy(result_view),
        "errors": list(errors or []),
        "warnings": list(warnings or []),
        "saved": saved,
        "migrated": migrated,
        "export_path": export_path,
    }


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
