"""Small local card catalogue and deterministic storage-orientation resolver."""

from __future__ import annotations

from copy import deepcopy


CARD_CATALOG_SCHEMA_V1 = "bgig.card_catalog.v1"
STORAGE_ORIENTATIONS = frozenset({"flat", "upright_long_edge", "upright_short_edge", "auto"})
CARD_STACK_MODES = frozenset({"thickness", "count"})

DEFAULT_SLEEVE_EXTRA_XY_MM = 2.0
DEFAULT_SLEEVE_EXTRA_Z_MM_PER_CARD = 0.08
_CARD_FORMATS = (
    {"id": "poker", "label": "Poker / Standard", "unsleeved_mm": {"x": 63.5, "y": 88.9}, "sleeved_mm": {"x": 66.0, "y": 91.0}},
    {"id": "standard_euro", "label": "Standard europeen", "unsleeved_mm": {"x": 59.0, "y": 92.0}, "sleeved_mm": {"x": 61.0, "y": 94.0}},
    {"id": "american", "label": "Standard americain", "unsleeved_mm": {"x": 56.0, "y": 87.0}, "sleeved_mm": {"x": 58.0, "y": 89.0}},
    {"id": "mini_euro", "label": "Mini europeen", "unsleeved_mm": {"x": 44.0, "y": 68.0}, "sleeved_mm": {"x": 46.0, "y": 70.0}},
    {"id": "tarot", "label": "Tarot", "unsleeved_mm": {"x": 70.0, "y": 120.0}, "sleeved_mm": {"x": 72.0, "y": 122.0}},
)


class AssetCatalogError(ValueError):
    """Raised when a catalogue reference or orientation is invalid."""


def card_catalog() -> dict[str, object]:
    """Return the versioned, local and deliberately small card catalogue."""

    return {"schema_version": CARD_CATALOG_SCHEMA_V1, "formats": deepcopy(list(_CARD_FORMATS))}


def card_format_dimensions(
    format_id: str,
    *,
    sleeved: bool,
    sleeve_extra_xy_mm: float | None = None,
) -> dict[str, float]:
    """Resolve the visible XY dimensions of one named card format."""

    for item in _CARD_FORMATS:
        if item["id"] == format_id:
            if not sleeved:
                return {axis: float(item["unsleeved_mm"][axis]) for axis in ("x", "y")}
            if sleeve_extra_xy_mm is None:
                return {axis: float(item["sleeved_mm"][axis]) for axis in ("x", "y")}
            return {
                axis: _round(float(item["unsleeved_mm"][axis]) + sleeve_extra_xy_mm)
                for axis in ("x", "y")
            }
    raise AssetCatalogError(f"Unknown card format: {format_id!r}.")


def card_stack_thickness_mm(
    *,
    mode: str,
    declared_thickness_mm: float,
    quantity: int,
    card_thickness_mm: float,
    sleeved: bool,
    sleeve_extra_z_mm_per_card: float | None = None,
) -> float:
    """Resolve a full deck thickness from a declaration or a counted stack."""

    if mode not in CARD_STACK_MODES:
        raise AssetCatalogError(f"Unsupported card stack mode: {mode!r}.")
    if mode == "thickness":
        return _round(declared_thickness_mm)
    sleeve_extra = (
        DEFAULT_SLEEVE_EXTRA_Z_MM_PER_CARD
        if sleeve_extra_z_mm_per_card is None
        else sleeve_extra_z_mm_per_card
    )
    per_card = card_thickness_mm + (sleeve_extra if sleeved else 0.0)
    return _round(quantity * per_card)


def orient_dimensions(
    base_dimensions_mm: dict[str, float],
    requested_orientation: str,
    *,
    max_height_mm: float,
) -> tuple[str, dict[str, float]]:
    """Resolve one card deck orientation into its actual XYZ envelope."""

    if requested_orientation not in STORAGE_ORIENTATIONS:
        raise AssetCatalogError(f"Unsupported storage orientation: {requested_orientation!r}.")
    x = float(base_dimensions_mm["x"])
    y = float(base_dimensions_mm["y"])
    z = float(base_dimensions_mm["z"])
    candidates = {
        "flat": {"x": x, "y": y, "z": z},
        "upright_long_edge": {"x": y, "y": z, "z": x},
        "upright_short_edge": {"x": x, "y": z, "z": y},
    }
    if requested_orientation != "auto":
        return requested_orientation, _dimension(candidates[requested_orientation])
    feasible = [
        (name, value) for name, value in candidates.items()
        if float(value["z"]) <= float(max_height_mm) + 0.0001
    ]
    pool = feasible or list(candidates.items())
    selected, dimensions = min(
        pool,
        key=lambda item: (
            float(item[1]["x"]) * float(item[1]["y"]),
            float(item[1]["z"]),
            item[0],
        ),
    )
    return selected, _dimension(dimensions)


def _dimension(value: dict[str, float]) -> dict[str, float]:
    return {axis: _round(value[axis]) for axis in ("x", "y", "z")}


def _round(value: float) -> float:
    return round(float(value), 4)
