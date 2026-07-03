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
    InsertConfig,
    LayoutSettings,
    ModuleRequest,
    ToleranceProfile,
)


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

    units = str(raw.get("units", "mm"))
    if units != "mm":
        raise ConfigError(f"Unsupported units '{units}'. V0 only supports millimeters.")

    box = _parse_box(_required_mapping(raw, "box"))
    tolerances = _parse_dataclass(
        ToleranceProfile,
        raw.get("tolerances", {}),
        "tolerances",
    )
    defaults = _parse_dataclass(
        GeometryDefaults,
        raw.get("defaults", {}),
        "defaults",
    )
    layout = _parse_dataclass(
        LayoutSettings,
        raw.get("layout", {}),
        "layout",
    )
    modules = tuple(_parse_modules(raw.get("modules", [])))

    return InsertConfig(
        project_name=str(raw.get("project_name", config_path.stem)),
        units=units,
        box=box,
        tolerances=tolerances,
        defaults=defaults,
        layout=layout,
        modules=modules,
        source_path=str(config_path),
    )


def _parse_box(raw: dict[str, Any]) -> BoxSpec:
    dimensions = _parse_dimensions(
        _required_mapping(raw, "inner_dimensions_mm"),
        field_name="box.inner_dimensions_mm",
    )
    return BoxSpec(
        inner_dimensions=dimensions,
        usable_height_mm=_float(raw, "usable_height_mm"),
        lid_clearance_mm=_float(raw, "lid_clearance_mm"),
    )


def _parse_modules(raw_modules: Any) -> list[ModuleRequest]:
    if not isinstance(raw_modules, list):
        raise ConfigError("'modules' must be a list.")

    parsed: list[ModuleRequest] = []
    for index, raw in enumerate(raw_modules):
        if not isinstance(raw, dict):
            raise ConfigError(f"modules[{index}] must be an object.")

        height = _float(raw, "height_mm")
        min_dimensions = _parse_dimensions(
            _required_mapping(raw, "min_dimensions_mm"),
            field_name=f"modules[{index}].min_dimensions_mm",
            default_z=height,
        )
        functional_type = _parse_functional_type(raw.get("functional_type", "other"), index)
        parsed.append(
            ModuleRequest(
                id=str(raw.get("id", f"module-{index + 1}")),
                name=str(raw.get("name", raw.get("id", f"Module {index + 1}"))),
                functional_type=functional_type,
                min_dimensions=min_dimensions,
                desired_height_mm=height,
                priority=int(raw.get("priority", 0)),
                allow_rotation=bool(raw.get("allow_rotation", False)),
                quantity=int(raw.get("quantity", 1)),
                comment=str(raw.get("comment", "")),
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


def _parse_dataclass(cls: type[Any], raw: Any, field_name: str) -> Any:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError(f"'{field_name}' must be an object.")

    allowed = {field.name for field in fields(cls)}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ConfigError(f"Unknown field(s) in '{field_name}': {', '.join(unknown)}.")

    return cls(**raw)


def _parse_dimensions(
    raw: dict[str, Any],
    field_name: str,
    default_z: float | None = None,
) -> Dimension3D:
    return Dimension3D(
        x=_number(raw, "x", field_name),
        y=_number(raw, "y", field_name),
        z=_number(raw, "z", field_name) if "z" in raw else _default_z(default_z, field_name),
    )


def _default_z(default_z: float | None, field_name: str) -> float:
    if default_z is None:
        raise ConfigError(f"Missing required field '{field_name}.z'.")
    return float(default_z)


def _required_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Missing or invalid object field '{key}'.")
    return value


def _float(raw: dict[str, Any], key: str) -> float:
    if key not in raw:
        raise ConfigError(f"Missing required field '{key}'.")
    return _number(raw, key, key)


def _number(raw: dict[str, Any], key: str, field_name: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"Field '{field_name}.{key}' must be a number.")
    return float(value)
