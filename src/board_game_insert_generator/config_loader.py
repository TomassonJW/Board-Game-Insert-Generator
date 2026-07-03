from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any

from board_game_insert_generator.models import (
    BoxSpec,
    Dimension3D,
    FunctionalType,
    GeometryDefaults,
    LAYOUT_STRATEGY_ROW_FILL,
    InsertConfig,
    LayoutSettings,
    ModuleRequest,
    ToleranceProfile,
)
from board_game_insert_generator.print_profiles import (
    PRINT_PROFILE_DEFAULT,
    resolve_print_profile,
)


ROOT_FIELDS = {"project_name", "units", "box", "print_profile", "tolerances", "defaults", "layout", "modules"}
BOX_FIELDS = {"inner_dimensions_mm", "usable_height_mm", "lid_clearance_mm"}
MODULE_FIELDS = {
    "id",
    "name",
    "functional_type",
    "min_dimensions_mm",
    "height_mm",
    "priority",
    "allow_rotation",
    "quantity",
    "comment",
}


class ConfigError(ValueError):
    """Raised when a configuration file cannot be parsed."""


def load_config(path: str | Path) -> InsertConfig:
    config_path = Path(path)
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Cannot read configuration {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Configuration root must be a JSON object.")

    _reject_unknown_fields(raw, ROOT_FIELDS, "root")

    units = _optional_string(raw, "units", "root", default="mm")
    if units != "mm":
        raise ConfigError(f"Unsupported units '{units}'. V0 only supports millimeters.")

    box = _parse_box(_required_mapping(raw, "box", "root.box"))
    print_profile = _optional_string(raw, "print_profile", "root", default=PRINT_PROFILE_DEFAULT)
    tolerances = _parse_tolerances(raw.get("tolerances", {}), print_profile)
    defaults = _parse_float_dataclass(GeometryDefaults, raw.get("defaults", {}), "defaults")
    layout = _parse_layout(raw.get("layout", {}))
    modules = tuple(_parse_modules(raw.get("modules", [])))

    return InsertConfig(
        project_name=_optional_string(
            raw,
            "project_name",
            "root",
            default=config_path.stem,
        ),
        units=units,
        box=box,
        tolerances=tolerances,
        defaults=defaults,
        layout=layout,
        modules=modules,
        print_profile=print_profile,
        source_path=str(config_path),
    )


def _parse_box(raw: dict[str, Any]) -> BoxSpec:
    _reject_unknown_fields(raw, BOX_FIELDS, "box")
    dimensions = _parse_dimensions(
        _required_mapping(raw, "inner_dimensions_mm", "box.inner_dimensions_mm"),
        field_name="box.inner_dimensions_mm",
    )
    return BoxSpec(
        inner_dimensions=dimensions,
        usable_height_mm=_float(raw, "usable_height_mm", "box.usable_height_mm"),
        lid_clearance_mm=_float(raw, "lid_clearance_mm", "box.lid_clearance_mm"),
    )


def _parse_modules(raw_modules: Any) -> list[ModuleRequest]:
    if not isinstance(raw_modules, list):
        raise ConfigError("'modules' must be a list.")

    parsed: list[ModuleRequest] = []
    for index, raw in enumerate(raw_modules):
        if not isinstance(raw, dict):
            raise ConfigError(f"modules[{index}] must be an object.")

        module_field = f"modules[{index}]"
        _reject_unknown_fields(raw, MODULE_FIELDS, module_field)
        height = _float(raw, "height_mm", f"{module_field}.height_mm")
        min_dimensions = _parse_dimensions(
            _required_mapping(raw, "min_dimensions_mm", f"{module_field}.min_dimensions_mm"),
            field_name=f"{module_field}.min_dimensions_mm",
            default_z=height,
        )
        functional_type = _parse_functional_type(raw.get("functional_type", "other"), index)
        module_id = _optional_string(raw, "id", module_field, default=f"module-{index + 1}")
        module_name = _optional_string(
            raw,
            "name",
            module_field,
            default=module_id if "id" in raw else f"Module {index + 1}",
        )
        parsed.append(
            ModuleRequest(
                id=module_id,
                name=module_name,
                functional_type=functional_type,
                min_dimensions=min_dimensions,
                desired_height_mm=height,
                priority=_int(raw, "priority", module_field, default=0),
                allow_rotation=_bool(raw, "allow_rotation", module_field, default=False),
                quantity=_int(raw, "quantity", module_field, default=1),
                comment=_optional_string(raw, "comment", module_field, default=""),
            )
        )
    return parsed


def _parse_functional_type(value: Any, index: int) -> FunctionalType:
    try:
        return FunctionalType(str(value))
    except ValueError as exc:
        allowed = ", ".join(item.value for item in FunctionalType)
        raise ConfigError(
            f"Unsupported functional_type for modules[{index}]: {value!r}. "
            f"Allowed values: {allowed}."
        ) from exc


def _parse_tolerances(raw: Any, print_profile: str) -> ToleranceProfile:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError("'tolerances' must be an object.")

    allowed = {field.name for field in fields(ToleranceProfile)}
    _reject_unknown_fields(raw, allowed, "tolerances")
    overrides = {
        field.name: _number_value(raw[field.name], f"tolerances.{field.name}")
        for field in fields(ToleranceProfile)
        if field.name in raw
    }
    try:
        return resolve_print_profile(print_profile, overrides)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc

def _parse_float_dataclass(cls: type[Any], raw: Any, field_name: str) -> Any:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError(f"'{field_name}' must be an object.")

    allowed = {field.name for field in fields(cls)}
    _reject_unknown_fields(raw, allowed, field_name)

    values = {
        field.name: _number_value(raw[field.name], f"{field_name}.{field.name}")
        for field in fields(cls)
        if field.name in raw
    }
    return cls(**values)


def _parse_layout(raw: Any) -> LayoutSettings:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError("'layout' must be an object.")

    allowed = {field.name for field in fields(LayoutSettings)}
    _reject_unknown_fields(raw, allowed, "layout")

    return LayoutSettings(
        strategy=_optional_string(raw, "strategy", "layout", default=LAYOUT_STRATEGY_ROW_FILL),
        allow_global_rotation=_bool(
            raw,
            "allow_global_rotation",
            "layout",
            default=False,
        ),
    )


def _parse_dimensions(
    raw: dict[str, Any],
    field_name: str,
    default_z: float | None = None,
) -> Dimension3D:
    _reject_unknown_fields(raw, {"x", "y", "z"}, field_name)
    return Dimension3D(
        x=_number(raw, "x", field_name),
        y=_number(raw, "y", field_name),
        z=_number(raw, "z", field_name) if "z" in raw else _default_z(default_z, field_name),
    )


def _default_z(default_z: float | None, field_name: str) -> float:
    if default_z is None:
        raise ConfigError(f"Missing required field '{field_name}.z'.")
    return float(default_z)


def _required_mapping(raw: dict[str, Any], key: str, field_path: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Missing or invalid object field '{field_path}'.")
    return value


def _float(raw: dict[str, Any], key: str, field_path: str) -> float:
    if key not in raw:
        raise ConfigError(f"Missing required field '{field_path}'.")
    return _number_value(raw[key], field_path)


def _number(raw: dict[str, Any], key: str, field_name: str) -> float:
    return _number_value(raw.get(key), f"{field_name}.{key}")


def _number_value(value: Any, field_path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"Field '{field_path}' must be a number.")
    return float(value)


def _int(raw: dict[str, Any], key: str, field_name: str, default: int) -> int:
    if key not in raw:
        return default
    value = raw[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"Field '{field_name}.{key}' must be an integer.")
    return value


def _bool(raw: dict[str, Any], key: str, field_name: str, default: bool) -> bool:
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, bool):
        raise ConfigError(f"Field '{field_name}.{key}' must be a boolean.")
    return value


def _optional_string(raw: dict[str, Any], key: str, field_name: str, default: str) -> str:
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, str):
        raise ConfigError(f"Field '{field_name}.{key}' must be a string.")
    return value


def _reject_unknown_fields(raw: dict[str, Any], allowed: set[str], field_name: str) -> None:
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ConfigError(f"Unknown field(s) in '{field_name}': {', '.join(unknown)}.")
