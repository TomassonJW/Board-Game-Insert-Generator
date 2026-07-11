"""Versioned, non-destructive appearance preferences for the BGIG Studio."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


APPEARANCE_SCHEMA_V0 = "bgig.appearance.v0"

DEFAULT_APPEARANCE_V0: dict[str, object] = {
    "schema_version": APPEARANCE_SCHEMA_V0,
    "shape": {
        "corner_style": "rounded",
        "corner_radius_mm": 3.0,
        "chamfer_mm": 1.5,
        "notch_style": "none",
    },
    "visual": {
        "theme": "atelier",
        "label_mode": "module_name",
        "typography": "quiet",
    },
}


class AppearanceError(ValueError):
    """Raised when a saved appearance preference cannot be used safely."""


def default_appearance() -> dict[str, object]:
    """Return an independent default appearance payload."""

    return deepcopy(DEFAULT_APPEARANCE_V0)


def normalize_appearance(raw: object | None) -> dict[str, object]:
    """Validate a P33 appearance input without changing any printable geometry."""

    if raw is None:
        return default_appearance()
    if not isinstance(raw, dict):
        raise AppearanceError("draft.appearance must be an object.")
    _reject_unknown(raw, {"schema_version", "shape", "visual"}, "draft.appearance")
    if raw.get("schema_version") != APPEARANCE_SCHEMA_V0:
        raise AppearanceError(f"draft.appearance.schema_version must be {APPEARANCE_SCHEMA_V0!r}.")
    shape = _mapping(raw.get("shape"), "draft.appearance.shape")
    visual = _mapping(raw.get("visual"), "draft.appearance.visual")
    _reject_unknown(shape, {"corner_style", "corner_radius_mm", "chamfer_mm", "notch_style"}, "draft.appearance.shape")
    _reject_unknown(visual, {"theme", "label_mode", "typography"}, "draft.appearance.visual")
    return {
        "schema_version": APPEARANCE_SCHEMA_V0,
        "shape": {
            "corner_style": _choice(shape, "corner_style", {"rounded", "straight", "chamfered"}, "draft.appearance.shape"),
            "corner_radius_mm": _bounded_number(shape, "corner_radius_mm", 0.0, 12.0, "draft.appearance.shape"),
            "chamfer_mm": _bounded_number(shape, "chamfer_mm", 0.0, 6.0, "draft.appearance.shape"),
            "notch_style": _choice(shape, "notch_style", {"none", "front_scoop", "thumb_notch"}, "draft.appearance.shape"),
        },
        "visual": {
            "theme": _choice(visual, "theme", {"atelier", "graphite", "playful"}, "draft.appearance.visual"),
            "label_mode": _choice(visual, "label_mode", {"none", "module_name", "module_name_and_role"}, "draft.appearance.visual"),
            "typography": _choice(visual, "typography", {"quiet", "bold"}, "draft.appearance.visual"),
        },
    }


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AppearanceError(f"{field} must be an object.")
    return dict(value)


def _reject_unknown(raw: dict[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise AppearanceError(f"{field} contains unsupported field(s): {', '.join(unknown)}.")


def _choice(raw: dict[str, Any], key: str, allowed: set[str], field: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or value not in allowed:
        raise AppearanceError(f"{field}.{key} must be one of: {', '.join(sorted(allowed))}.")
    return value


def _bounded_number(raw: dict[str, Any], key: str, minimum: float, maximum: float, field: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not minimum <= float(value) <= maximum:
        raise AppearanceError(f"{field}.{key} must be between {minimum:g} and {maximum:g} mm.")
    return float(value)
