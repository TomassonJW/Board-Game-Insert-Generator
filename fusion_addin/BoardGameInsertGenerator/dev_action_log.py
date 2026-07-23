"""Local, append-only development trail for the embedded Fusion palette.

The product UI emits concise semantic events.  This module persists them beside
the user's BGIG projects and deduplicates full project snapshots by digest.
Nothing is promoted to the repository and no domain operation is invoked.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from copy import deepcopy
from pathlib import Path
from typing import Mapping

try:
    from .palette_project import current_project_path
except ImportError:  # pragma: no cover - Fusion may load the add-in as a script.
    from palette_project import current_project_path  # type: ignore[no-redef]


DEV_ACTION_LOG_EVENT_SCHEMA_V1 = "bgig.dev_action_log_event.v1"
DEV_ACTION_LOG_DIRECTORY = "dev-action-logs"
DEV_ACTION_LOG_FILENAME = "events.jsonl"
DEV_ACTION_LOG_PRODUCER_ID = "fusion_palette_action_log_v1"
DEV_ACTION_LOG_PRODUCER_VERSION = "1"
_SESSION_ID_PATTERN = re.compile(r"^session-[a-z0-9-]{8,80}$")
_FORBIDDEN_KEY_PARTS = (
    "credential",
    "document_path",
    "file_path",
    "password",
    "secret",
    "token",
)
_MAX_TEXT_LENGTH = 4096
_MAX_LIST_ITEMS = 256
_MAX_DEPTH = 10
_LOG_LOCK = threading.Lock()


class DevActionLogError(ValueError):
    """Raised when an automatic development event is unsafe or malformed."""


def append_dev_action_event(
    raw_event: object,
    addin_dir: str | Path,
) -> dict[str, object]:
    """Validate and append one event, storing a project snapshot only once."""

    event = _mapping(raw_event, "event")
    if event.get("schema") != DEV_ACTION_LOG_EVENT_SCHEMA_V1:
        raise DevActionLogError(
            f"Unsupported development log schema: {event.get('schema')!r}."
        )
    session_id = _text(event.get("session_id"), "event.session_id")
    if not _SESSION_ID_PATTERN.fullmatch(session_id):
        raise DevActionLogError("Invalid development log session id.")
    sequence = _non_negative_int(event.get("sequence"), "event.sequence")
    occurred_at_ms = _non_negative_int(
        event.get("occurred_at_ms"),
        "event.occurred_at_ms",
    )
    event_type = _text(event.get("event_type"), "event.event_type")
    source_revision = _non_negative_int(
        event.get("source_revision", 0),
        "event.source_revision",
    )
    active_view = _bounded_text(event.get("active_view", ""), "event.active_view")
    details = _sanitize_value(event.get("details", {}), "event.details", depth=0)
    if not isinstance(details, dict):
        raise DevActionLogError("event.details must be an object.")

    root = current_project_path(addin_dir).parent / DEV_ACTION_LOG_DIRECTORY
    session_directory = root / session_id
    snapshot_reference: dict[str, object] | None = None
    project_snapshot = event.get("project_snapshot")

    with _LOG_LOCK:
        if project_snapshot is not None:
            snapshot = _mapping(project_snapshot, "event.project_snapshot")
            _reject_forbidden_keys(snapshot, "event.project_snapshot")
            snapshot_reference = _persist_project_snapshot(
                session_directory,
                snapshot,
            )
        payload: dict[str, object] = {
            "schema_version": DEV_ACTION_LOG_EVENT_SCHEMA_V1,
            "session_id": session_id,
            "sequence": sequence,
            "occurred_at_ms": occurred_at_ms,
            "event_type": event_type,
            "source_revision": source_revision,
            "active_view": active_view,
            "details": details,
            "producer": {
                "id": DEV_ACTION_LOG_PRODUCER_ID,
                "version": DEV_ACTION_LOG_PRODUCER_VERSION,
            },
        }
        if snapshot_reference is not None:
            payload["project_snapshot"] = snapshot_reference
        log_path = session_directory / DEV_ACTION_LOG_FILENAME
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                + "\n"
            )

    return {
        "schema_version": DEV_ACTION_LOG_EVENT_SCHEMA_V1,
        "session_id": session_id,
        "sequence": sequence,
        "event_type": event_type,
        "log_path": str(log_path),
        "snapshot": deepcopy(snapshot_reference),
    }


def _persist_project_snapshot(
    session_directory: Path,
    project: dict[str, object],
) -> dict[str, object]:
    canonical = json.dumps(
        project,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    relative_path = Path("snapshots") / f"project-{digest}.bgig.json"
    path = session_directory / relative_path
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(project, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    return {
        "digest": digest,
        "relative_path": relative_path.as_posix(),
    }


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise DevActionLogError(f"{label} must be an object.")
    return {str(key): deepcopy(item) for key, item in value.items()}


def _text(value: object, label: str) -> str:
    text = _bounded_text(value, label)
    if not text:
        raise DevActionLogError(f"{label} must not be empty.")
    return text


def _bounded_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise DevActionLogError(f"{label} must be text.")
    if len(value) > _MAX_TEXT_LENGTH:
        raise DevActionLogError(f"{label} is too long.")
    return value


def _non_negative_int(value: object, label: str) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise DevActionLogError(f"{label} must be a non-negative integer.")
    return value


def _sanitize_value(value: object, label: str, *, depth: int) -> object:
    if depth > _MAX_DEPTH:
        raise DevActionLogError(f"{label} is nested too deeply.")
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _bounded_text(value, label)
    if isinstance(value, Mapping):
        result: dict[str, object] = {}
        for raw_key, item in value.items():
            key = str(raw_key)
            _reject_forbidden_key(key, label)
            result[key] = _sanitize_value(
                item,
                f"{label}.{key}",
                depth=depth + 1,
            )
        return result
    if isinstance(value, (list, tuple)):
        if len(value) > _MAX_LIST_ITEMS:
            raise DevActionLogError(f"{label} contains too many items.")
        return [
            _sanitize_value(item, f"{label}[{index}]", depth=depth + 1)
            for index, item in enumerate(value)
        ]
    raise DevActionLogError(f"{label} contains an unsupported value.")


def _reject_forbidden_keys(value: Mapping[str, object], label: str) -> None:
    for raw_key, item in value.items():
        key = str(raw_key)
        _reject_forbidden_key(key, label)
        if isinstance(item, Mapping):
            _reject_forbidden_keys(item, f"{label}.{key}")
        elif isinstance(item, (list, tuple)):
            for index, nested in enumerate(item):
                if isinstance(nested, Mapping):
                    _reject_forbidden_keys(
                        nested,
                        f"{label}.{key}[{index}]",
                    )


def _reject_forbidden_key(key: str, label: str) -> None:
    normalized = key.lower()
    if any(part in normalized for part in _FORBIDDEN_KEY_PARTS):
        raise DevActionLogError(f"{label} contains forbidden key {key!r}.")
