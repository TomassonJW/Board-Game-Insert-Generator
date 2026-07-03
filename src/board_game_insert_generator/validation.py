from __future__ import annotations

from dataclasses import asdict, dataclass

from board_game_insert_generator.models import (
    Cavity,
    Dimension3D,
    IMPLEMENTED_LAYOUT_STRATEGIES,
    RESERVED_LAYOUT_STRATEGIES,
    InsertConfig,
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    field: str
    message: str


class ValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        message = "\n".join(f"[{issue.code}] {issue.field}: {issue.message}" for issue in issues)
        super().__init__(message)


def validate_config(config: InsertConfig) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if config.units != "mm":
        issues.append(_issue("units", "UNSUPPORTED_UNITS", "Only millimeters are supported."))

    _validate_positive_dimensions(config.box.inner_dimensions, "box.inner_dimensions_mm", issues)
    _validate_positive_number(config.box.usable_height_mm, "box.usable_height_mm", issues)
    _validate_non_negative_number(config.box.lid_clearance_mm, "box.lid_clearance_mm", issues)

    max_usable_height = config.box.inner_dimensions.z - config.box.lid_clearance_mm
    if config.box.usable_height_mm > max_usable_height:
        issues.append(
            _issue(
                "box.usable_height_mm",
                "USABLE_HEIGHT_TOO_TALL",
                (
                    "Usable height must be lower than inner Z minus lid clearance "
                    f"({max_usable_height:.2f} mm)."
                ),
            )
        )

    for name, value in asdict(config.tolerances).items():
        _validate_non_negative_number(float(value), f"tolerances.{name}", issues)

    _validate_positive_number(
        config.defaults.wall_thickness_mm,
        "defaults.wall_thickness_mm",
        issues,
    )
    _validate_positive_number(
        config.defaults.floor_thickness_mm,
        "defaults.floor_thickness_mm",
        issues,
    )
    _validate_non_negative_number(
        config.defaults.corner_radius_mm,
        "defaults.corner_radius_mm",
        issues,
    )

    seen_ids: set[str] = set()
    for index, module in enumerate(config.modules):
        prefix = f"modules[{index}]"
        if not module.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Module id cannot be empty."))
        if module.id in seen_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate id '{module.id}'."))
        seen_ids.add(module.id)

        _validate_positive_dimensions(module.min_dimensions, f"{prefix}.min_dimensions_mm", issues)
        _validate_positive_number(module.desired_height_mm, f"{prefix}.height_mm", issues)
        _validate_positive_int(module.quantity, f"{prefix}.quantity", issues)

        if module.desired_height_mm > config.box.usable_height_mm:
            issues.append(
                _issue(
                    f"{prefix}.height_mm",
                    "MODULE_TOO_TALL",
                    "Module height is greater than usable box height.",
                )
            )

        fits_normal = (
            module.min_dimensions.x <= config.box.inner_dimensions.x
            and module.min_dimensions.y <= config.box.inner_dimensions.y
        )
        fits_rotated = (
            module.allow_rotation
            and module.min_dimensions.y <= config.box.inner_dimensions.x
            and module.min_dimensions.x <= config.box.inner_dimensions.y
        )
        if not (fits_normal or fits_rotated):
            issues.append(
                _issue(
                    f"{prefix}.min_dimensions_mm",
                    "MODULE_FOOTPRINT_TOO_LARGE",
                    "Module footprint cannot fit in the box in any allowed orientation.",
                )
            )

        _validate_module_cavities(
            module.cavities,
            prefix,
            module.min_dimensions,
            module.desired_height_mm,
            config.defaults.wall_thickness_mm,
            config.defaults.floor_thickness_mm,
            issues,
        )

    if config.layout.strategy not in IMPLEMENTED_LAYOUT_STRATEGIES:
        implemented = ", ".join(f"'{strategy}'" for strategy in IMPLEMENTED_LAYOUT_STRATEGIES)
        message = f"V0 supports only these layout strategies: {implemented}."
        if config.layout.strategy in RESERVED_LAYOUT_STRATEGIES:
            message += " This strategy is reserved for a later layout mission."
        issues.append(
            _issue(
                "layout.strategy",
                "UNSUPPORTED_LAYOUT_STRATEGY",
                message,
            )
        )

    return issues


def assert_valid_config(config: InsertConfig) -> None:
    issues = validate_config(config)
    if issues:
        raise ValidationError(issues)


def _validate_module_cavities(
    cavities: tuple[Cavity, ...],
    module_field: str,
    module_size: Dimension3D,
    module_height_mm: float,
    wall_thickness_mm: float,
    floor_thickness_mm: float,
    issues: list[ValidationIssue],
) -> None:
    seen_ids: set[str] = set()
    for index, cavity in enumerate(cavities):
        prefix = f"{module_field}.cavities[{index}]"
        if not cavity.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Cavity id cannot be empty."))
        if cavity.id in seen_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate cavity id '{cavity.id}'."))
        seen_ids.add(cavity.id)

        _validate_non_negative_number(cavity.origin.x, f"{prefix}.origin_mm.x", issues)
        _validate_non_negative_number(cavity.origin.y, f"{prefix}.origin_mm.y", issues)
        _validate_non_negative_number(cavity.origin.z, f"{prefix}.origin_mm.z", issues)
        _validate_positive_dimensions(cavity.size, f"{prefix}.size_mm", issues)
        _validate_non_negative_number(cavity.clearance_mm, f"{prefix}.clearance_mm", issues)

        right_wall = module_size.x - (cavity.origin.x + cavity.size.x)
        back_wall = module_size.y - (cavity.origin.y + cavity.size.y)
        top_remaining = module_height_mm - (cavity.origin.z + cavity.size.z)
        if right_wall < 0 or back_wall < 0 or top_remaining < 0:
            issues.append(
                _issue(
                    prefix,
                    "CAVITY_OUTSIDE_MODULE",
                    "Cavity must stay inside the module external dimensions.",
                )
            )

        min_side_wall = min(cavity.origin.x, cavity.origin.y, right_wall, back_wall)
        if min_side_wall < wall_thickness_mm:
            issues.append(
                _issue(
                    prefix,
                    "CAVITY_WALL_TOO_THIN",
                    (
                        "Cavity must preserve the configured wall thickness "
                        f"({wall_thickness_mm:.2f} mm) on X/Y sides."
                    ),
                )
            )

        if cavity.origin.z < floor_thickness_mm:
            issues.append(
                _issue(
                    prefix,
                    "CAVITY_FLOOR_TOO_THIN",
                    (
                        "Cavity must preserve the configured floor thickness "
                        f"({floor_thickness_mm:.2f} mm)."
                    ),
                )
            )

def _validate_positive_dimensions(
    dimensions: Dimension3D,
    field: str,
    issues: list[ValidationIssue],
) -> None:
    _validate_positive_number(dimensions.x, f"{field}.x", issues)
    _validate_positive_number(dimensions.y, f"{field}.y", issues)
    _validate_positive_number(dimensions.z, f"{field}.z", issues)


def _validate_positive_number(value: float, field: str, issues: list[ValidationIssue]) -> None:
    if value <= 0:
        issues.append(_issue(field, "NOT_POSITIVE", "Value must be greater than zero."))


def _validate_non_negative_number(value: float, field: str, issues: list[ValidationIssue]) -> None:
    if value < 0:
        issues.append(_issue(field, "NEGATIVE_VALUE", "Value must be greater than or equal to zero."))


def _validate_positive_int(value: int, field: str, issues: list[ValidationIssue]) -> None:
    if value <= 0:
        issues.append(_issue(field, "NOT_POSITIVE", "Value must be greater than zero."))


def _issue(field: str, code: str, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, field=field, message=message)
