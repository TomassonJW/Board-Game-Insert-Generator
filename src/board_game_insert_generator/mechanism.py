"""Experimental, non-materialized mechanism contracts for BGIG."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


MECHANISM_SCHEMA_V0 = "bgig.mechanism.v0"
SLIDING_LID_POLICY_V0 = "sliding_lid_experimental_v0"

DEFAULT_MECHANISM_V0: dict[str, object] = {
    "schema_version": MECHANISM_SCHEMA_V0,
    "kind": "none",
    "slide_axis": "x",
    "lid_thickness_mm": 1.2,
    "rail_height_mm": 1.2,
    "rail_clearance_mm": 0.3,
    "end_overlap_mm": 8.0,
}


class MechanismError(ValueError):
    """Raised when an experimental mechanism preference is not safe to plan."""


def default_mechanism() -> dict[str, object]:
    """Return a fresh default: an open tray with no closing mechanism."""

    return deepcopy(DEFAULT_MECHANISM_V0)


def normalize_mechanism(raw: object | None) -> dict[str, object]:
    """Validate a mechanism preference without changing global tolerances."""

    if raw is None:
        return default_mechanism()
    if not isinstance(raw, dict):
        raise MechanismError("draft.mechanism must be an object.")
    _reject_unknown(
        raw,
        {"schema_version", "kind", "slide_axis", "lid_thickness_mm", "rail_height_mm", "rail_clearance_mm", "end_overlap_mm"},
        "draft.mechanism",
    )
    if raw.get("schema_version") != MECHANISM_SCHEMA_V0:
        raise MechanismError(f"draft.mechanism.schema_version must be {MECHANISM_SCHEMA_V0!r}.")
    return {
        "schema_version": MECHANISM_SCHEMA_V0,
        "kind": _choice(raw, "kind", {"none", "sliding_lid"}, "draft.mechanism"),
        "slide_axis": _choice(raw, "slide_axis", {"x", "y"}, "draft.mechanism"),
        "lid_thickness_mm": _bounded_number(raw, "lid_thickness_mm", 0.8, 3.0, "draft.mechanism"),
        "rail_height_mm": _bounded_number(raw, "rail_height_mm", 0.8, 3.0, "draft.mechanism"),
        "rail_clearance_mm": _bounded_number(raw, "rail_clearance_mm", 0.15, 0.6, "draft.mechanism"),
        "end_overlap_mm": _bounded_number(raw, "end_overlap_mm", 6.0, 20.0, "draft.mechanism"),
    }


def sliding_lid_readiness(module_id: str, size_mm: Mapping[str, object], mechanism: Mapping[str, object]) -> dict[str, object]:
    """Report whether a module is large enough for a future sliding-lid coupon.

    This is a contract and preprint warning only. It does not add rails, a lid,
    dimensions, or any CAD operation to the module.
    """

    normalized = normalize_mechanism(dict(mechanism))
    if normalized["kind"] != "sliding_lid":
        return {
            "module_id": module_id,
            "policy": SLIDING_LID_POLICY_V0,
            "status": "not_requested",
            "physical_validation": "required",
        }
    size = _size(size_mm, module_id)
    axis = str(normalized["slide_axis"])
    length = size[axis]
    cross_axis = "y" if axis == "x" else "x"
    width = size[cross_axis]
    lid_thickness = float(normalized["lid_thickness_mm"])
    rail_height = float(normalized["rail_height_mm"])
    rail_clearance = float(normalized["rail_clearance_mm"])
    overlap = float(normalized["end_overlap_mm"])
    minimum_length = 2 * overlap + 8.0
    minimum_width = 2 * rail_height + 2 * rail_clearance + 8.0
    added_envelope = {
        "x": 0.0 if axis == "x" else 2 * (rail_height + rail_clearance),
        "y": 2 * (rail_height + rail_clearance) if axis == "x" else 0.0,
        "z": lid_thickness + rail_height,
    }
    common = {
        "module_id": module_id,
        "policy": SLIDING_LID_POLICY_V0,
        "slide_axis": axis,
        "minimum_module_size_mm": {axis: minimum_length, cross_axis: minimum_width},
        "added_envelope_mm": added_envelope,
        "physical_validation": "required",
        "materialization_status": "not_materialized",
    }
    if length < minimum_length:
        return {
            **common,
            "status": "refused",
            "code": "SLIDING_LID_MODULE_TOO_SHORT",
            "reason": f"module length on slide axis {axis} is below {minimum_length:g} mm",
        }
    if width < minimum_width:
        return {
            **common,
            "status": "refused",
            "code": "SLIDING_LID_MODULE_TOO_NARROW",
            "reason": f"module width across slide axis is below {minimum_width:g} mm",
        }
    return {
        **common,
        "status": "planned_for_coupon",
        "code": "SLIDING_LID_PRINT_COUPON_REQUIRED",
        "reason": "geometry is not materialized; rail clearance and added height require a measured print coupon",
    }


def _size(raw: Mapping[str, object], module_id: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for axis in ("x", "y", "z"):
        value = raw.get(axis)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
            raise MechanismError(f"module {module_id} size_mm.{axis} must be a positive number.")
        values[axis] = float(value)
    return values


def _reject_unknown(raw: Mapping[str, object], allowed: set[str], field: str) -> None:
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise MechanismError(f"{field} contains unsupported field(s): {', '.join(unknown)}.")


def _choice(raw: Mapping[str, object], key: str, allowed: set[str], field: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or value not in allowed:
        raise MechanismError(f"{field}.{key} must be one of: {', '.join(sorted(allowed))}.")
    return value


def _bounded_number(raw: Mapping[str, object], key: str, minimum: float, maximum: float, field: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not minimum <= float(value) <= maximum:
        raise MechanismError(f"{field}.{key} must be between {minimum:g} and {maximum:g} mm.")
    return float(value)
