"""Atomic local personal element presets, independent from Fusion and cloud services."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft


PERSONAL_PRESETS_SCHEMA_V1 = "bgig.personal_element_presets.v1"


class PersonalPresetError(ValueError):
    """Raised when a personal preset collection cannot be trusted."""


def empty_personal_presets() -> dict[str, object]:
    return {"schema_version": PERSONAL_PRESETS_SCHEMA_V1, "presets": []}


def load_personal_presets(path: str | Path) -> dict[str, object]:
    source = Path(path)
    if not source.is_file():
        return empty_personal_presets()
    try:
        raw = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PersonalPresetError(f"Personal preset file is unreadable: {exc}.") from exc
    return normalize_personal_presets(raw)


def normalize_personal_presets(raw: object) -> dict[str, object]:
    if not isinstance(raw, dict) or raw.get("schema_version") != PERSONAL_PRESETS_SCHEMA_V1:
        raise PersonalPresetError(f"Expected schema {PERSONAL_PRESETS_SCHEMA_V1}.")
    values = raw.get("presets")
    if not isinstance(values, list):
        raise PersonalPresetError("Personal presets must be a list.")
    result = []
    ids: set[str] = set()
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            raise PersonalPresetError(f"Personal preset {index} must be an object.")
        preset_id = _text(value.get("id"), f"preset {index} id")
        name = _text(value.get("name"), f"preset {index} name")
        if preset_id in ids:
            raise PersonalPresetError(f"Duplicate personal preset id: {preset_id}.")
        ids.add(preset_id)
        content = _normalize_content_template(value.get("content"))
        result.append({"id": preset_id, "name": name, "content": content})
    return {"schema_version": PERSONAL_PRESETS_SCHEMA_V1, "presets": result}


def save_personal_preset(
    path: str | Path,
    *,
    name: str,
    content: dict[str, object],
) -> dict[str, object]:
    collection = load_personal_presets(path)
    preset_id = _slug(_text(name, "preset name"))
    normalized = _normalize_content_template(content)
    presets = [item for item in collection["presets"] if item["id"] != preset_id]
    presets.append({"id": preset_id, "name": name.strip(), "content": normalized})
    result = {"schema_version": PERSONAL_PRESETS_SCHEMA_V1, "presets": presets}
    write_personal_presets(path, result)
    return deepcopy(result)


def delete_personal_preset(path: str | Path, preset_id: str) -> dict[str, object]:
    collection = load_personal_presets(path)
    result = {
        "schema_version": PERSONAL_PRESETS_SCHEMA_V1,
        "presets": [item for item in collection["presets"] if item["id"] != preset_id],
    }
    write_personal_presets(path, result)
    return deepcopy(result)


def write_personal_presets(path: str | Path, raw: object) -> None:
    target = Path(path)
    collection = normalize_personal_presets(raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(collection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(target)


def _normalize_content_template(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise PersonalPresetError("Personal preset content must be an object.")
    template = deepcopy(value)
    template.pop("id", None)
    template.pop("container_group_id", None)
    project = blank_project_v1()
    project["container_groups"] = [
        {"id": "personal-preset", "name": "Preset", "wall_thickness_mm": None, "floor_thickness_mm": None}
    ]
    project["contents"] = [{**template, "id": "personal-content", "container_group_id": "personal-preset"}]
    try:
        normalized = normalize_project_draft(project).project["contents"][0]
    except Exception as exc:
        raise PersonalPresetError(f"Personal preset content is invalid: {exc}") from exc
    normalized.pop("id", None)
    normalized.pop("container_group_id", None)
    return normalized


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PersonalPresetError(f"{field} must be a non-empty string.")
    return value.strip()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "preset"
