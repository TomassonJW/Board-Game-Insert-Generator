"""User-first V0.1 project contract and migration from the local composer V0.

The contract intentionally describes a game box in product language.  It does
not expose candidates, layers, CAD IR or Fusion concepts.  Later V0.1 services
derive those technical objects from this stable project input.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from board_game_insert_generator.asset_catalog import (
    CARD_STACK_MODES,
    STORAGE_ORIENTATIONS,
    AssetCatalogError,
    card_format_dimensions,
    card_stack_thickness_mm,
    explicit_card_xy_dimensions,
    orient_dimensions,
)


PROJECT_SCHEMA_V1 = "bgig.project.v1"
LEGACY_LOCAL_COMPOSER_SCHEMA_V0 = "bgig.local_composer.v0"

SHAPE_KINDS = frozenset({"round", "square", "rectangle", "cards", "cube", "meeple", "custom"})
FLAT_ITEM_KINDS = frozenset({"board", "rulebook", "other"})
FILL_ELEMENT_KINDS = frozenset({"hollow", "solid", "separator"})
FILL_MODES = frozenset({"auto", "exact"})
MEASUREMENT_CONFIDENCE = frozenset({"exact", "approximate"})
_CLEARANCE_DEFAULT_SOURCES = frozenset({"compatibility_legacy_scalar", "project_default"})
SOLVER_PREFERENCES = frozenset({"balanced", "compact", "accessible", "print_simple", "material_reduced"})
SURPLUS_PREFERENCES = frozenset({"balanced", "walls", "floor"})
DIMENSION_MODES = frozenset({"auto", "target", "fixed"})


class ProjectContractError(ValueError):
    """Raised when a user project cannot be normalized safely."""


@dataclass(frozen=True)
class ProjectNormalization:
    """A validated V0.1 project and the provenance of its input."""

    project: dict[str, object]
    source_schema: str
    migrated: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "project": deepcopy(self.project),
            "source_schema": self.source_schema,
            "migrated": self.migrated,
        }


def blank_project_v1() -> dict[str, object]:
    """Return a valid empty project for the user-first Studio."""

    return {
        "schema_version": PROJECT_SCHEMA_V1,
        "project_name": "Mon insert",
        "box": {
            "inner_dimensions_mm": {"x": 200.0, "y": 150.0, "z": 60.0},
            "usable_height_mm": 56.0,
            "lid_clearance_mm": 2.0,
        },
        "layout": {
            "layout_clearance_mm": 0.6,
            "container_box_xy_clearance_mm": 0.6,
            "container_z_clearance_mm": 0.6,
            "default_wall_thickness_mm": 1.2,
            "default_floor_thickness_mm": 1.2,
            "default_content_clearance_mm": 0.6,
        },
        "contents": [],
        "container_groups": [],
        "flat_items": [],
        "fill_elements": [],
        "solver_preference": "balanced",
        "deferred_features": {"appearance": None, "mechanism": None},
    }


def normalize_project_draft(raw_project: object) -> ProjectNormalization:
    """Normalize a native V0.1 project or migrate a local composer V0 draft.

    The function never mutates the input.  It is deliberately separate from the
    legacy composer adapter: P37 establishes the product contract, while P39
    will derive storage bodies and P41 will resolve the complete box volume.
    """

    raw = _mapping(raw_project, "project")
    schema_version = _required_text(raw, "schema_version", "project")
    if schema_version == PROJECT_SCHEMA_V1:
        return ProjectNormalization(
            project=_validate_v1(raw),
            source_schema=PROJECT_SCHEMA_V1,
            migrated=False,
        )
    if schema_version == LEGACY_LOCAL_COMPOSER_SCHEMA_V0:
        return ProjectNormalization(
            project=migrate_local_composer_v0(raw),
            source_schema=LEGACY_LOCAL_COMPOSER_SCHEMA_V0,
            migrated=True,
        )
    raise ProjectContractError(
        "Unsupported project schema. Expected 'bgig.project.v1' or "
        "'bgig.local_composer.v0'."
    )


def migrate_local_composer_v0(raw_legacy: object) -> dict[str, object]:
    """Convert a P23 local composer draft without losing deferred information."""

    legacy = _mapping(raw_legacy, "legacy project")
    if _required_text(legacy, "schema_version", "legacy project") != LEGACY_LOCAL_COMPOSER_SCHEMA_V0:
        raise ProjectContractError("Only bgig.local_composer.v0 can be migrated by this function.")

    box = _mapping(_required_value(legacy, "box", "legacy project"), "legacy project.box")
    dimensions = _dimension(
        _required_value(box, "inner_dimensions_mm", "legacy project.box"),
        "legacy project.box.inner_dimensions_mm",
    )
    usable_height_mm = _positive_number(box, "usable_height_mm", "legacy project.box")
    lid_clearance_mm = _non_negative_number(box, "lid_clearance_mm", "legacy project.box")
    assets = _list(_required_value(legacy, "assets", "legacy project"), "legacy project.assets")
    candidates = _list(legacy.get("candidates", []), "legacy project.candidates")
    candidate_groups, asset_group_ids = _migrate_candidate_groups(candidates, assets)

    contents: list[dict[str, object]] = []
    for index, asset_value in enumerate(assets):
        asset = _mapping(asset_value, f"legacy project.assets[{index}]")
        asset_id = _required_text(asset, "id", f"legacy project.assets[{index}]")
        group_id = asset_group_ids.get(asset_id)
        if group_id is None:
            group_id = f"group:{asset_id}"
            candidate_groups.append(
                {
                    "id": group_id,
                    "name": f"Bac - {_required_text(asset, 'name', f'legacy project.assets[{index}]')}",
                    "wall_thickness_mm": None,
                    "floor_thickness_mm": None,
                }
            )
        contents.append(_migrate_asset(asset, index, group_id))

    flat_items = _migrate_flat_items(legacy.get("reservations", []))
    migrated = {
        "schema_version": PROJECT_SCHEMA_V1,
        "project_name": _required_text(legacy, "project_name", "legacy project"),
        "box": {
            "inner_dimensions_mm": dimensions,
            "usable_height_mm": usable_height_mm,
            "lid_clearance_mm": lid_clearance_mm,
        },
        "layout": {
            "layout_clearance_mm": 0.6,
            "container_box_xy_clearance_mm": 0.6,
            "container_z_clearance_mm": 0.6,
            "default_wall_thickness_mm": 1.2,
            "default_floor_thickness_mm": 1.2,
            "default_content_clearance_mm": 0.6,
        },
        "contents": contents,
        "container_groups": candidate_groups,
        "flat_items": flat_items,
        "fill_elements": [],
        "solver_preference": _optional_enum(
            legacy.get("preference"),
            SOLVER_PREFERENCES,
            "balanced",
            "legacy project.preference",
        ),
        "deferred_features": {
            "appearance": deepcopy(legacy.get("appearance")),
            "mechanism": deepcopy(legacy.get("mechanism")),
        },
        "migration": {
            "source_schema": LEGACY_LOCAL_COMPOSER_SCHEMA_V0,
            "legacy_snapshot": {
                "layers": deepcopy(legacy.get("layers", [])),
                "reservations": deepcopy(legacy.get("reservations", [])),
                "manual_modules": deepcopy(legacy.get("manual_modules", [])),
                "candidates": deepcopy(candidates),
            },
        },
    }
    return _validate_v1(migrated)


def _validate_v1(raw: dict[str, object]) -> dict[str, object]:
    _reject_unknown(
        raw,
        {
            "schema_version",
            "project_name",
            "box",
            "layout",
            "contents",
            "container_groups",
            "flat_items",
            "fill_elements",
            "solver_preference",
            "deferred_features",
            "migration",
        },
        "project",
    )
    if _required_text(raw, "schema_version", "project") != PROJECT_SCHEMA_V1:
        raise ProjectContractError("project.schema_version must be 'bgig.project.v1'.")
    project_name = _required_text(raw, "project_name", "project")
    if len(project_name) > 120:
        raise ProjectContractError("project.project_name must stay under 120 characters.")

    box = _validate_box(_mapping(_required_value(raw, "box", "project"), "project.box"))
    layout = _validate_layout(_mapping(_required_value(raw, "layout", "project"), "project.layout"))
    groups = _validate_container_groups(
        _list(_required_value(raw, "container_groups", "project"), "project.container_groups"),
        layout=layout,
    )
    contents = _validate_contents(
        _list(_required_value(raw, "contents", "project"), "project.contents"),
        groups,
        usable_height_mm=float(box["usable_height_mm"]),
        layout=layout,
    )
    group_ids = {str(group["id"]) for group in groups}
    flat_items = _validate_flat_items(
        _list(_required_value(raw, "flat_items", "project"), "project.flat_items"),
        layout=layout,
    )
    fill_elements = _validate_fill_elements(
        _list(_required_value(raw, "fill_elements", "project"), "project.fill_elements"), group_ids
    )
    preference = _optional_enum(
        raw.get("solver_preference"), SOLVER_PREFERENCES, "balanced", "project.solver_preference"
    )
    deferred_features = _validate_deferred_features(raw.get("deferred_features"))
    migration = _validate_migration(raw.get("migration"))

    project: dict[str, object] = {
        "schema_version": PROJECT_SCHEMA_V1,
        "project_name": project_name,
        "box": box,
        "layout": layout,
        "contents": contents,
        "container_groups": groups,
        "flat_items": flat_items,
        "fill_elements": fill_elements,
        "solver_preference": preference,
        "deferred_features": deferred_features,
    }
    if migration is not None:
        project["migration"] = migration
    return project


def _validate_box(raw: dict[str, object]) -> dict[str, object]:
    _reject_unknown(raw, {"inner_dimensions_mm", "usable_height_mm", "lid_clearance_mm"}, "project.box")
    return {
        "inner_dimensions_mm": _dimension(
            _required_value(raw, "inner_dimensions_mm", "project.box"),
            "project.box.inner_dimensions_mm",
        ),
        "usable_height_mm": _positive_number(raw, "usable_height_mm", "project.box"),
        "lid_clearance_mm": _non_negative_number(raw, "lid_clearance_mm", "project.box"),
    }


def _validate_layout(raw: dict[str, object]) -> dict[str, object]:
    _reject_unknown(raw, {
        "layout_clearance_mm", "container_z_clearance_mm", "container_box_xy_clearance_mm",
        "default_wall_thickness_mm", "default_floor_thickness_mm", "default_content_clearance_mm",
        "clearance_defaults_v1", "clearance_default_sources_v1",
    }, "project.layout")
    xy = _non_negative_number(raw, "layout_clearance_mm", "project.layout")
    z = _non_negative_number(raw, "container_z_clearance_mm", "project.layout") if "container_z_clearance_mm" in raw else xy
    box_xy = _non_negative_number(raw, "container_box_xy_clearance_mm", "project.layout") if "container_box_xy_clearance_mm" in raw else xy
    content = _non_negative_number(raw, "default_content_clearance_mm", "project.layout")
    explicit = raw.get("clearance_defaults_v1")
    if explicit is None:
        defaults = {
            "asset_cavity_mm": {"x": content, "y": content, "z": content},
            "flat_inset_mm": {"x": xy, "y": xy, "z": 0.0},
            "container_between_mm": {"x": xy, "y": xy, "z": z},
            "container_box_per_side_xy_mm": {"x": box_xy, "y": box_xy},
        }
        default_sources = _clearance_default_sources(None, "compatibility_legacy_scalar")
    else:
        defaults = _validate_clearance_defaults_v1(explicit, "project.layout.clearance_defaults_v1")
        default_sources = _clearance_default_sources(raw.get("clearance_default_sources_v1"), "project_default")
    return {
        "layout_clearance_mm": xy, "container_z_clearance_mm": z, "container_box_xy_clearance_mm": box_xy,
        "default_wall_thickness_mm": _positive_number(raw, "default_wall_thickness_mm", "project.layout"),
        "default_floor_thickness_mm": _positive_number(raw, "default_floor_thickness_mm", "project.layout"),
        "default_content_clearance_mm": content, "clearance_defaults_v1": defaults,
        "clearance_default_sources_v1": default_sources,
    }


def _clearance_default_sources(value: object, fallback: str) -> dict[str, dict[str, str]]:
    axes_by_vector = {
        "asset_cavity_mm": ("x", "y", "z"),
        "flat_inset_mm": ("x", "y", "z"),
        "container_between_mm": ("x", "y", "z"),
        "container_box_per_side_xy_mm": ("x", "y"),
    }
    if value is None:
        return {name: {axis: fallback for axis in axes} for name, axes in axes_by_vector.items()}
    raw = _mapping(value, "project.layout.clearance_default_sources_v1")
    _reject_unknown(raw, set(axes_by_vector), "project.layout.clearance_default_sources_v1")
    result: dict[str, dict[str, str]] = {}
    for name, axes in axes_by_vector.items():
        values = _mapping(_required_value(raw, name, "project.layout.clearance_default_sources_v1"), f"project.layout.clearance_default_sources_v1.{name}")
        _reject_unknown(values, set(axes), f"project.layout.clearance_default_sources_v1.{name}")
        result[name] = {}
        for axis in axes:
            source_name = _required_text(
                values,
                axis,
                f"project.layout.clearance_default_sources_v1.{name}",
            )
            if source_name not in _CLEARANCE_DEFAULT_SOURCES:
                raise ProjectContractError(
                    f"project.layout.clearance_default_sources_v1.{name}.{axis} "
                    "must be a known provenance."
                )
            result[name][axis] = source_name
    return result


def _validate_clearance_defaults_v1(value: object, field: str) -> dict[str, dict[str, float]]:
    raw = _mapping(value, field)
    _reject_unknown(raw, {"asset_cavity_mm", "flat_inset_mm", "container_between_mm", "container_box_per_side_xy_mm"}, field)
    return {
        "asset_cavity_mm": _clearance_vector(_required_value(raw, "asset_cavity_mm", field), ("x", "y", "z"), f"{field}.asset_cavity_mm"),
        "flat_inset_mm": _clearance_vector(_required_value(raw, "flat_inset_mm", field), ("x", "y", "z"), f"{field}.flat_inset_mm"),
        "container_between_mm": _clearance_vector(_required_value(raw, "container_between_mm", field), ("x", "y", "z"), f"{field}.container_between_mm"),
        "container_box_per_side_xy_mm": _clearance_vector(_required_value(raw, "container_box_per_side_xy_mm", field), ("x", "y"), f"{field}.container_box_per_side_xy_mm"),
    }


def _clearance_vector(value: object, axes: tuple[str, ...], field: str) -> dict[str, float]:
    raw = _mapping(value, field); _reject_unknown(raw, set(axes), field)
    return {a: _non_negative_number(raw, a, field) for a in axes}


def _optional_clearance_vector(value: object, axes: tuple[str, ...], field: str) -> dict[str, float | None]:
    if value is None: return {a: None for a in axes}
    raw = _mapping(value, field); _reject_unknown(raw, set(axes), field)
    return {a: _optional_non_negative_number(raw.get(a), field) for a in axes}


def _resolved_clearance(override: dict[str, float | None], defaults: dict[str, float], sources: dict[str, object], *, legacy_scalar: float | None = None, legacy_source: str = "legacy_scalar") -> tuple[dict[str, float], dict[str, str]]:
    values: dict[str, float] = {}; provenance: dict[str, str] = {}
    for a, default in defaults.items():
        if override[a] is not None: values[a], provenance[a] = float(override[a]), "object_override"
        elif legacy_scalar is not None: values[a], provenance[a] = float(legacy_scalar), legacy_source
        else: values[a], provenance[a] = float(default), str(sources[a])
    return values, provenance


def _validate_container_groups(values: list[object], *, layout: dict[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    ids: set[str] = set()
    for index, value in enumerate(values):
        field = f"project.container_groups[{index}]"
        raw = _mapping(value, field)
        _reject_unknown(
            raw,
            {
                "id", "name", "wall_thickness_mm", "floor_thickness_mm",
                "expansion_axes", "locked_outer_dimensions_mm", "surplus_preference",
                "dimension_modes", "target_outer_dimensions_mm",
                "clearance_overrides_v1", "clearance_effective_v1",
            },
            field,
        )
        group_id = _required_text(raw, "id", field)
        if group_id in ids:
            raise ProjectContractError(f"{field}.id duplicates '{group_id}'.")
        ids.add(group_id)
        expansion_axes = _validate_expansion_axes(raw.get("expansion_axes"), field)
        locked_dimensions = _validate_locked_dimensions(raw.get("locked_outer_dimensions_mm"), field)
        dimension_modes, target_dimensions, expansion_axes, locked_dimensions = _validate_dimension_contract(
            raw, expansion_axes, locked_dimensions, field
        )
        overrides = _validate_container_clearance_overrides(raw.get("clearance_overrides_v1"), field)
        defaults = dict(layout["clearance_defaults_v1"]); sources = dict(layout["clearance_default_sources_v1"])
        # Les anciens overrides par bac restent sérialisables pour un roundtrip non
        # destructif, mais le produit applique désormais exclusivement les jeux globaux.
        between = dict(defaults["container_between_mm"])
        between_sources = dict(sources["container_between_mm"])
        box_clearance = dict(defaults["container_box_per_side_xy_mm"])
        box_sources = dict(sources["container_box_per_side_xy_mm"])
        result.append(
            {
                "id": group_id,
                "name": _required_text(raw, "name", field),
                "wall_thickness_mm": _optional_positive_number(raw.get("wall_thickness_mm"), field),
                "floor_thickness_mm": _optional_positive_number(raw.get("floor_thickness_mm"), field),
                "expansion_axes": expansion_axes,
                "locked_outer_dimensions_mm": locked_dimensions,
                "dimension_modes": dimension_modes,
                "target_outer_dimensions_mm": target_dimensions,
                "surplus_preference": _optional_enum(
                    raw.get("surplus_preference"), SURPLUS_PREFERENCES, "balanced",
                    f"{field}.surplus_preference",
                ),
                "clearance_overrides_v1": overrides,
                "clearance_effective_v1": {
                    "role": "external_container", "between_mm": between, "box_per_side_xy_mm": box_clearance,
                    "source_by_vector": {"between_mm": between_sources, "box_per_side_xy_mm": box_sources},
                },
            }
        )
    return result


def _validate_container_clearance_overrides(value: object, field: str) -> dict[str, dict[str, float | None]]:
    if value is None: return {"between_mm": {"x": None, "y": None, "z": None}, "box_per_side_xy_mm": {"x": None, "y": None}}
    raw = _mapping(value, f"{field}.clearance_overrides_v1")
    _reject_unknown(raw, {"between_mm", "box_per_side_xy_mm"}, f"{field}.clearance_overrides_v1")
    return {
        "between_mm": _optional_clearance_vector(raw.get("between_mm"), ("x", "y", "z"), f"{field}.clearance_overrides_v1.between_mm"),
        "box_per_side_xy_mm": _optional_clearance_vector(raw.get("box_per_side_xy_mm"), ("x", "y"), f"{field}.clearance_overrides_v1.box_per_side_xy_mm"),
    }


def _validate_expansion_axes(value: object, field: str) -> dict[str, bool]:
    if value is None:
        return {"x": True, "y": True, "z": True}
    raw = _mapping(value, f"{field}.expansion_axes")
    _reject_unknown(raw, {"x", "y", "z"}, f"{field}.expansion_axes")
    result: dict[str, bool] = {}
    for axis in ("x", "y", "z"):
        axis_value = raw.get(axis, True)
        if not isinstance(axis_value, bool):
            raise ProjectContractError(f"{field}.expansion_axes.{axis} must be a boolean.")
        result[axis] = axis_value
    return result


def _validate_locked_dimensions(value: object, field: str) -> dict[str, float | None]:
    if value is None:
        return {"x": None, "y": None, "z": None}
    raw = _mapping(value, f"{field}.locked_outer_dimensions_mm")
    _reject_unknown(raw, {"x", "y", "z"}, f"{field}.locked_outer_dimensions_mm")
    return {
        axis: _optional_positive_number(raw.get(axis), f"{field}.locked_outer_dimensions_mm")
        for axis in ("x", "y", "z")
    }


def _validate_dimension_contract(
    raw: dict[str, object],
    expansion_axes: dict[str, bool],
    locked_dimensions: dict[str, float | None],
    field: str,
) -> tuple[dict[str, str], dict[str, float | None], dict[str, bool], dict[str, float | None]]:
    modes_value = raw.get("dimension_modes")
    targets = _validate_target_dimensions(raw.get("target_outer_dimensions_mm"), field)
    if modes_value is None:
        modes = {
            axis: (
                "fixed" if locked_dimensions[axis] is not None or not expansion_axes[axis]
                else "target" if targets[axis] is not None
                else "auto"
            )
            for axis in ("x", "y", "z")
        }
    else:
        mode_raw = _mapping(modes_value, f"{field}.dimension_modes")
        _reject_unknown(mode_raw, {"x", "y", "z"}, f"{field}.dimension_modes")
        modes = {
            axis: _optional_enum(
                mode_raw.get(axis), DIMENSION_MODES, "auto", f"{field}.dimension_modes.{axis}"
            )
            for axis in ("x", "y", "z")
        }

    normalized_expansion = dict(expansion_axes)
    normalized_locked = dict(locked_dimensions)
    normalized_targets = dict(targets)
    for axis in ("x", "y", "z"):
        mode = modes[axis]
        locked = locked_dimensions[axis]
        target = targets[axis]
        if locked is not None:
            if modes_value is not None and mode != "fixed":
                raise ProjectContractError(
                    f"{field}.dimension_modes.{axis} must be 'fixed' while a locked dimension exists."
                )
            if target is not None and abs(float(target) - float(locked)) > 0.0001:
                raise ProjectContractError(
                    f"{field}.target_outer_dimensions_mm.{axis} conflicts with the locked dimension."
                )
            mode = "fixed"
            modes[axis] = mode
            normalized_targets[axis] = float(locked)
        if mode == "auto":
            if target is not None:
                raise ProjectContractError(
                    f"{field}.target_outer_dimensions_mm.{axis} must be null in auto mode."
                )
            normalized_expansion[axis] = True
            normalized_locked[axis] = None
        elif mode == "target":
            if target is None:
                raise ProjectContractError(
                    f"{field}.target_outer_dimensions_mm.{axis} is required in target mode."
                )
            normalized_expansion[axis] = True
            normalized_locked[axis] = None
        else:
            normalized_expansion[axis] = False
            if normalized_targets[axis] is not None:
                normalized_locked[axis] = float(normalized_targets[axis])
    return modes, normalized_targets, normalized_expansion, normalized_locked


def _validate_target_dimensions(value: object, field: str) -> dict[str, float | None]:
    if value is None:
        return {"x": None, "y": None, "z": None}
    raw = _mapping(value, f"{field}.target_outer_dimensions_mm")
    _reject_unknown(raw, {"x", "y", "z"}, f"{field}.target_outer_dimensions_mm")
    return {
        axis: _optional_positive_number(raw.get(axis), f"{field}.target_outer_dimensions_mm")
        for axis in ("x", "y", "z")
    }


def _validate_contents(
    values: list[object],
    groups: list[dict[str, object]],
    *,
    usable_height_mm: float,
    layout: dict[str, object],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    groups_by_id = {str(group["id"]): group for group in groups}
    group_ids = set(groups_by_id)
    ids: set[str] = set()
    for index, value in enumerate(values):
        field = f"project.contents[{index}]"
        raw = _mapping(value, field)
        _reject_unknown(
            raw,
            {
                "id", "name", "shape_kind", "dimensions_mm", "base_dimensions_mm",
                "quantity", "container_group_id", "content_clearance_mm",
                "clearance_override_mm", "clearance_effective_v1",
                "measurement_confidence", "dimension_source", "card_format_id",
                "sleeved", "storage_orientation", "resolved_orientation",
                "card_stack_mode", "card_thickness_mm",
                "sleeve_extra_xy_mm", "sleeve_extra_z_mm_per_card",
                "card_stack_declared_thickness_mm", "card_declared_xy_mm",
            },
            field,
        )
        item_id = _required_text(raw, "id", field)
        if item_id in ids:
            raise ProjectContractError(f"{field}.id duplicates '{item_id}'.")
        ids.add(item_id)
        shape_kind = _required_enum(raw, "shape_kind", SHAPE_KINDS, field)
        group_id = _required_text(raw, "container_group_id", field)
        if group_id not in group_ids:
            raise ProjectContractError(f"{field}.container_group_id references unknown group '{group_id}'.")
        quantity = _positive_int(raw, "quantity", field)
        content_clearance = _optional_non_negative_number(raw.get("content_clearance_mm"), field)
        override = _optional_clearance_vector(raw.get("clearance_override_mm"), ("x", "y", "z"), f"{field}.clearance_override_mm")
        defaults = dict(layout["clearance_defaults_v1"]); sources = dict(layout["clearance_default_sources_v1"])
        effective, effective_sources = _resolved_clearance(override, dict(defaults["asset_cavity_mm"]), dict(sources["asset_cavity_mm"]), legacy_scalar=content_clearance, legacy_source="legacy_content_clearance_mm")
        group = groups_by_id[group_id]
        effective_floor = float(group["floor_thickness_mm"] or layout["default_floor_thickness_mm"])
        max_content_height = max(0.0001, usable_height_mm - effective_floor - effective["z"])
        geometry = _validate_content_geometry(
            raw, shape_kind=shape_kind, quantity=quantity,
            max_height_mm=max_content_height, field=field
        )
        result.append(
            {
                "id": item_id,
                "name": _required_text(raw, "name", field),
                "shape_kind": shape_kind,
                **geometry,
                "quantity": quantity,
                "container_group_id": group_id,
                "content_clearance_mm": content_clearance, "clearance_override_mm": override,
                "clearance_effective_v1": {"role": "asset_cavity", "values_mm": effective, "source_by_axis": effective_sources},
                "measurement_confidence": _optional_enum(
                    raw.get("measurement_confidence"),
                    MEASUREMENT_CONFIDENCE,
                    "exact",
                    f"{field}.measurement_confidence",
                ),
            }
        )
    return result


def _validate_content_geometry(
    raw: dict[str, object],
    *,
    shape_kind: str,
    quantity: int,
    max_height_mm: float,
    field: str,
) -> dict[str, object]:
    base_value = (
        raw["base_dimensions_mm"]
        if "base_dimensions_mm" in raw
        else _required_value(raw, "dimensions_mm", field)
    )
    base = _dimension(base_value, f"{field}.base_dimensions_mm")
    if shape_kind != "cards":
        return {"dimensions_mm": base}

    dimension_source = _optional_enum(
        raw.get("dimension_source"), frozenset({"explicit", "catalog"}), "explicit",
        f"{field}.dimension_source",
    )
    format_value = raw.get("card_format_id")
    card_format_id = None
    if format_value is not None:
        if not isinstance(format_value, str) or not format_value.strip():
            raise ProjectContractError(f"{field}.card_format_id must be a non-empty string or null.")
        card_format_id = format_value.strip()
    sleeved = _optional_bool(raw.get("sleeved"), False, f"{field}.sleeved")
    sleeve_extra_xy = _optional_non_negative_number(
        raw.get("sleeve_extra_xy_mm"), f"{field}.sleeve_extra_xy_mm"
    )
    sleeve_extra_z = _optional_non_negative_number(
        raw.get("sleeve_extra_z_mm_per_card"), f"{field}.sleeve_extra_z_mm_per_card"
    )
    declared_xy = (
        _xy_dimension(raw.get("card_declared_xy_mm"), f"{field}.card_declared_xy_mm")
        if "card_declared_xy_mm" in raw
        else {axis: base[axis] for axis in ("x", "y")}
    )
    stack_mode = _optional_enum(
        raw.get("card_stack_mode"), CARD_STACK_MODES, "thickness", f"{field}.card_stack_mode"
    )
    declared_stack_thickness = (
        _optional_positive_number(
            raw.get("card_stack_declared_thickness_mm"),
            f"{field}.card_stack_declared_thickness_mm",
        )
        if "card_stack_declared_thickness_mm" in raw
        else base["z"]
    )
    assert declared_stack_thickness is not None
    card_thickness = _optional_positive_number(
        raw.get("card_thickness_mm", 0.32), f"{field}.card_thickness_mm"
    )
    assert card_thickness is not None
    if dimension_source == "catalog":
        if card_format_id is None:
            raise ProjectContractError(f"{field}.card_format_id is required for catalog dimensions.")
        try:
            catalog_xy = card_format_dimensions(
                card_format_id,
                sleeved=sleeved,
                sleeve_extra_xy_mm=sleeve_extra_xy,
            )
        except AssetCatalogError as exc:
            raise ProjectContractError(f"{field}.card_format_id is not supported: {card_format_id!r}.") from exc
        base.update(catalog_xy)
    else:
        try:
            base.update(
                explicit_card_xy_dimensions(
                    declared_xy,
                    sleeved=sleeved,
                    sleeve_extra_xy_mm=sleeve_extra_xy,
                )
            )
        except AssetCatalogError as exc:
            raise ProjectContractError(f"{field} has invalid explicit card dimensions: {exc}") from exc
    try:
        base["z"] = card_stack_thickness_mm(
            mode=stack_mode, declared_thickness_mm=declared_stack_thickness, quantity=quantity,
            card_thickness_mm=card_thickness,
            sleeved=sleeved,
            sleeve_extra_z_mm_per_card=sleeve_extra_z,
        )
        requested_orientation = _optional_enum(
            raw.get("storage_orientation"), STORAGE_ORIENTATIONS, "flat",
            f"{field}.storage_orientation",
        )
        resolved_orientation, resolved = orient_dimensions(
            base, requested_orientation, max_height_mm=max_height_mm
        )
    except AssetCatalogError as exc:
        raise ProjectContractError(f"{field} has an invalid card configuration: {exc}") from exc
    geometry = {
        "dimensions_mm": resolved,
        "base_dimensions_mm": base,
        "dimension_source": dimension_source,
        "card_format_id": card_format_id,
        "sleeved": sleeved,
        "storage_orientation": requested_orientation,
        "resolved_orientation": resolved_orientation,
        "card_stack_mode": stack_mode,
        "card_thickness_mm": card_thickness,
    }
    if "sleeve_extra_xy_mm" in raw:
        geometry["sleeve_extra_xy_mm"] = sleeve_extra_xy
    if "sleeve_extra_z_mm_per_card" in raw:
        geometry["sleeve_extra_z_mm_per_card"] = sleeve_extra_z
    if "card_stack_declared_thickness_mm" in raw or (
        stack_mode == "thickness" and sleeved and sleeve_extra_z is not None
    ):
        geometry["card_stack_declared_thickness_mm"] = declared_stack_thickness
    if "card_declared_xy_mm" in raw or (
        dimension_source == "explicit" and sleeve_extra_xy is not None
    ):
        geometry["card_declared_xy_mm"] = declared_xy
    return geometry


def _validate_flat_items(values: list[object], *, layout: dict[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    ids: set[str] = set()
    orders: set[int] = set()
    for index, value in enumerate(values):
        field = f"project.flat_items[{index}]"
        raw = _mapping(value, field)
        _reject_unknown(
            raw,
            {
                "id", "name", "kind", "dimensions_mm", "quantity", "stack_order",
                "origin_mm", "rotation_deg_z", "clearance_override_mm", "clearance_effective_v1",
            },
            field,
        )
        item_id = _required_text(raw, "id", field)
        if item_id in ids:
            raise ProjectContractError(f"{field}.id duplicates '{item_id}'.")
        ids.add(item_id)
        stack_order = _optional_non_negative_int(raw.get("stack_order"), f"{field}.stack_order")
        if stack_order is not None:
            if stack_order in orders:
                raise ProjectContractError(f"{field}.stack_order duplicates '{stack_order}'.")
            orders.add(stack_order)
        override = _optional_clearance_vector(raw.get("clearance_override_mm"), ("x", "y", "z"), f"{field}.clearance_override_mm")
        defaults = dict(layout["clearance_defaults_v1"]); sources = dict(layout["clearance_default_sources_v1"])
        effective, effective_sources = _resolved_clearance(override, dict(defaults["flat_inset_mm"]), dict(sources["flat_inset_mm"]))
        result.append(
            {
                "id": item_id,
                "name": _required_text(raw, "name", field),
                "kind": _required_enum(raw, "kind", FLAT_ITEM_KINDS, field),
                "dimensions_mm": _dimension(
                    _required_value(raw, "dimensions_mm", field), f"{field}.dimensions_mm"
                ),
                "quantity": _positive_int(raw, "quantity", field),
                "stack_order": stack_order,
                "origin_mm": _optional_xy_origin(raw.get("origin_mm"), f"{field}.origin_mm"),
                "rotation_deg_z": _optional_right_angle_rotation(
                    raw.get("rotation_deg_z"), f"{field}.rotation_deg_z"
                ),
                "clearance_override_mm": override,
                "clearance_effective_v1": {"role": "flat_inset", "values_mm": effective, "source_by_axis": effective_sources},
            }
        )
    return result


def _validate_fill_elements(values: list[object], group_ids: set[str]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    ids: set[str] = set()
    for index, value in enumerate(values):
        field = f"project.fill_elements[{index}]"
        raw = _mapping(value, field)
        _reject_unknown(
            raw,
            {"id", "name", "kind", "mode", "dimensions_mm", "container_group_id"},
            field,
        )
        element_id = _required_text(raw, "id", field)
        if element_id in ids:
            raise ProjectContractError(f"{field}.id duplicates '{element_id}'.")
        ids.add(element_id)
        mode = _required_enum(raw, "mode", FILL_MODES, field)
        dimensions_value = raw.get("dimensions_mm")
        if mode == "exact" and dimensions_value is None:
            raise ProjectContractError(f"{field}.dimensions_mm is required when mode is 'exact'.")
        if mode == "auto" and dimensions_value is not None:
            raise ProjectContractError(f"{field}.dimensions_mm must be null when mode is 'auto'.")
        group_id = raw.get("container_group_id")
        if group_id is not None:
            if not isinstance(group_id, str) or not group_id.strip():
                raise ProjectContractError(f"{field}.container_group_id must be a non-empty string or null.")
            if group_id not in group_ids:
                raise ProjectContractError(f"{field}.container_group_id references unknown group '{group_id}'.")
        result.append(
            {
                "id": element_id,
                "name": _required_text(raw, "name", field),
                "kind": _required_enum(raw, "kind", FILL_ELEMENT_KINDS, field),
                "mode": mode,
                "dimensions_mm": (
                    None if dimensions_value is None else _dimension(dimensions_value, f"{field}.dimensions_mm")
                ),
                "container_group_id": group_id,
            }
        )
    return result


def _validate_deferred_features(value: object) -> dict[str, object | None]:
    if value is None:
        return {"appearance": None, "mechanism": None}
    raw = _mapping(value, "project.deferred_features")
    _reject_unknown(raw, {"appearance", "mechanism"}, "project.deferred_features")
    for key in ("appearance", "mechanism"):
        if key in raw and raw[key] is not None and not isinstance(raw[key], dict):
            raise ProjectContractError(f"project.deferred_features.{key} must be an object or null.")
    return {"appearance": deepcopy(raw.get("appearance")), "mechanism": deepcopy(raw.get("mechanism"))}


def _validate_migration(value: object) -> dict[str, object] | None:
    if value is None:
        return None
    raw = _mapping(value, "project.migration")
    _reject_unknown(raw, {"source_schema", "legacy_snapshot"}, "project.migration")
    source_schema = _required_text(raw, "source_schema", "project.migration")
    snapshot = _mapping(_required_value(raw, "legacy_snapshot", "project.migration"), "project.migration.legacy_snapshot")
    return {"source_schema": source_schema, "legacy_snapshot": deepcopy(snapshot)}


def _migrate_candidate_groups(
    candidates: list[object], assets: list[object]
) -> tuple[list[dict[str, object]], dict[str, str]]:
    known_asset_ids = {
        _required_text(_mapping(asset, f"legacy project.assets[{index}]"), "id", f"legacy project.assets[{index}]")
        for index, asset in enumerate(assets)
    }
    groups: list[dict[str, object]] = []
    asset_group_ids: dict[str, str] = {}
    group_ids: set[str] = set()
    for index, value in enumerate(candidates):
        field = f"legacy project.candidates[{index}]"
        candidate = _mapping(value, field)
        candidate_id = _required_text(candidate, "id", field)
        if candidate_id in group_ids:
            raise ProjectContractError(f"{field}.id duplicates '{candidate_id}'.")
        group_ids.add(candidate_id)
        groups.append(
            {
                "id": candidate_id,
                "name": _required_text(candidate, "name", field),
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
        )
        for asset_id in _list(candidate.get("asset_ids", []), f"{field}.asset_ids"):
            if not isinstance(asset_id, str) or not asset_id:
                raise ProjectContractError(f"{field}.asset_ids must contain non-empty strings.")
            if asset_id not in known_asset_ids:
                raise ProjectContractError(f"{field}.asset_ids references unknown asset '{asset_id}'.")
            if asset_id in asset_group_ids:
                raise ProjectContractError(f"Legacy asset '{asset_id}' belongs to more than one candidate.")
            asset_group_ids[asset_id] = candidate_id
    return groups, asset_group_ids


def _migrate_asset(asset: dict[str, object], index: int, group_id: str) -> dict[str, object]:
    field = f"legacy project.assets[{index}]"
    quantity = _mapping(_required_value(asset, "quantity", field), f"{field}.quantity")
    legacy_kind = _required_text(asset, "kind", field)
    shape_kind = {"cards": "cards", "dice": "cube", "meeples": "meeple"}.get(legacy_kind, "custom")
    confidence = _optional_enum(
        asset.get("dimension_confidence"), MEASUREMENT_CONFIDENCE, "approximate", f"{field}.dimension_confidence"
    )
    return {
        "id": _required_text(asset, "id", field),
        "name": _required_text(asset, "name", field),
        "shape_kind": shape_kind,
        "dimensions_mm": _dimension(_required_value(asset, "dimensions_mm", field), f"{field}.dimensions_mm"),
        "quantity": _positive_int(quantity, "count", f"{field}.quantity"),
        "container_group_id": group_id,
        "content_clearance_mm": None,
        "measurement_confidence": confidence,
    }


def _migrate_flat_items(value: object) -> list[dict[str, object]]:
    reservations = _list(value, "legacy project.reservations")
    result: list[dict[str, object]] = []
    for index, value in enumerate(reservations):
        field = f"legacy project.reservations[{index}]"
        reservation = _mapping(value, field)
        kind = reservation.get("kind")
        if kind not in {"board", "rulebook"}:
            continue
        result.append(
            {
                "id": _required_text(reservation, "id", field),
                "name": "Plateau" if kind == "board" else "Livret de regles",
                "kind": kind,
                "dimensions_mm": _dimension(_required_value(reservation, "size_mm", field), f"{field}.size_mm"),
                "quantity": 1,
                "stack_order": None,
            }
        )
    return result


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ProjectContractError(f"{field} must be an object.")
    return value


def _list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ProjectContractError(f"{field} must be a list.")
    return value


def _required_value(raw: dict[str, object], key: str, field: str) -> object:
    if key not in raw:
        raise ProjectContractError(f"{field}.{key} is required.")
    return raw[key]


def _required_text(raw: dict[str, object], key: str, field: str) -> str:
    value = _required_value(raw, key, field)
    if not isinstance(value, str) or not value.strip():
        raise ProjectContractError(f"{field}.{key} must be a non-empty string.")
    return value.strip()


def _required_enum(raw: dict[str, object], key: str, values: frozenset[str], field: str) -> str:
    value = _required_text(raw, key, field)
    if value not in values:
        raise ProjectContractError(f"{field}.{key} is not supported: '{value}'.")
    return value


def _optional_bool(value: object, default: bool, field: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ProjectContractError(f"{field} must be a boolean.")
    return value


def _optional_xy_origin(value: object, field: str) -> dict[str, float] | None:
    if value is None:
        return None
    raw = _mapping(value, field)
    _reject_unknown(raw, {"x", "y"}, field)
    return {
        axis: _non_negative_number(raw, axis, field)
        for axis in ("x", "y")
    }


def _optional_right_angle_rotation(value: object, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProjectContractError(f"{field} must be 0, 90 or null.")
    rotation = int(value)
    if float(value) != float(rotation) or rotation not in {0, 90}:
        raise ProjectContractError(f"{field} must be 0, 90 or null.")
    return rotation


def _optional_enum(value: object, values: frozenset[str], default: str, field: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str) or value not in values:
        raise ProjectContractError(f"{field} is not supported.")
    return value


def _dimension(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value, field)
    _reject_unknown(raw, {"x", "y", "z"}, field)
    return {axis: _positive_number(raw, axis, field) for axis in ("x", "y", "z")}


def _xy_dimension(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value, field)
    _reject_unknown(raw, {"x", "y"}, field)
    return {axis: _positive_number(raw, axis, field) for axis in ("x", "y")}


def _positive_number(raw: dict[str, object], key: str, field: str) -> float:
    value = _required_value(raw, key, field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ProjectContractError(f"{field}.{key} must be a number greater than zero.")
    return float(value)


def _non_negative_number(raw: dict[str, object], key: str, field: str) -> float:
    value = _required_value(raw, key, field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ProjectContractError(f"{field}.{key} must be a number greater than or equal to zero.")
    return float(value)


def _positive_int(raw: dict[str, object], key: str, field: str) -> int:
    value = _required_value(raw, key, field)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ProjectContractError(f"{field}.{key} must be an integer greater than zero.")
    return value


def _optional_positive_number(value: object, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ProjectContractError(f"{field} must be a positive number or null.")
    return float(value)


def _optional_non_negative_number(value: object, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ProjectContractError(f"{field} must be a non-negative number or null.")
    return float(value)


def _optional_non_negative_int(value: object, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProjectContractError(f"{field} must be a non-negative integer or null.")
    return value


def _reject_unknown(raw: dict[str, object], allowed: set[str], field: str) -> None:
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ProjectContractError(f"{field} contains unknown field(s): {', '.join(unknown)}.")
