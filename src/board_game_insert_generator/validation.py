from __future__ import annotations

from dataclasses import asdict, dataclass

from board_game_insert_generator.feature_taxonomy import is_feature_taxonomy_compatible
from board_game_insert_generator.volumetric import span_cells, span_fits_grid
from board_game_insert_generator.models import (
    AssetStorageOrientation,
    Cavity,
    Dimension3D,
    DimensionConfidence,
    Feature,
    FeatureKind,
    FunctionalType,
    GridPoint3D,
    GridSize3D,
    IMPLEMENTED_LAYOUT_STRATEGIES,
    RESERVED_LAYOUT_STRATEGIES,
    InsertConfig,
    ToleranceProfile,
    VolumetricGrid,
    VolumetricModulePlacement,
    VolumetricOwnerType,
    VolumetricZone,
)


ACCESS_DIRECTIONS = {"unspecified", "top", "front", "back", "left", "right", "any"}
ASSET_STORAGE_ORIENTATIONS = {item.value for item in AssetStorageOrientation}


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
            config.tolerances,
            config.defaults.wall_thickness_mm,
            config.defaults.floor_thickness_mm,
            issues,
        )

    _validate_assets(config, issues)
    _validate_volumetric_grid(config, issues)

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


def _validate_assets(config: InsertConfig, issues: list[ValidationIssue]) -> None:
    seen_ids: set[str] = set()
    module_ids = {module.id for module in config.modules}
    reservation_ids = set()
    if config.volumetric_grid is not None:
        reservation_ids = {zone.id for zone in config.volumetric_grid.zones}

    for index, asset in enumerate(config.assets):
        prefix = f"assets[{index}]"
        if not asset.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Asset id cannot be empty."))
        if asset.id in seen_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate asset id '{asset.id}'."))
        seen_ids.add(asset.id)
        if not asset.name:
            issues.append(_issue(f"{prefix}.name", "EMPTY_VALUE", "Asset name cannot be empty."))
        _validate_positive_int(asset.quantity.count, f"{prefix}.quantity.count", issues)
        if not asset.quantity.grouping:
            issues.append(_issue(f"{prefix}.quantity.grouping", "EMPTY_VALUE", "Asset quantity grouping cannot be empty."))
        _validate_positive_number(asset.dimensions.x, f"{prefix}.dimensions_mm.x", issues)
        _validate_positive_number(asset.dimensions.y, f"{prefix}.dimensions_mm.y", issues)
        if asset.dimension_confidence == DimensionConfidence.UNKNOWN_Z:
            _validate_non_negative_number(asset.dimensions.z, f"{prefix}.dimensions_mm.z", issues)
        else:
            _validate_positive_number(asset.dimensions.z, f"{prefix}.dimensions_mm.z", issues)
        storage_orientation = getattr(asset.storage_orientation, "value", asset.storage_orientation)
        if storage_orientation not in ASSET_STORAGE_ORIENTATIONS:
            allowed = ", ".join(sorted(ASSET_STORAGE_ORIENTATIONS))
            issues.append(
                _issue(
                    f"{prefix}.storage_orientation",
                    "ASSET_STORAGE_ORIENTATION_UNSUPPORTED",
                    f"Allowed storage orientations: {allowed}.",
                )
            )
        if asset.max_stack_height_mm is not None:
            _validate_positive_number(asset.max_stack_height_mm, f"{prefix}.max_stack_height_mm", issues)
        if asset.reservation_ref is not None and asset.reservation_ref not in reservation_ids:
            issues.append(
                _issue(
                    f"{prefix}.reservation_ref",
                    "ASSET_UNKNOWN_RESERVATION",
                    f"Asset references unknown volumetric reservation '{asset.reservation_ref}'.",
                )
            )
        if asset.module_hint is not None and asset.module_hint not in module_ids:
            issues.append(
                _issue(
                    f"{prefix}.module_hint",
                    "ASSET_UNKNOWN_MODULE_HINT",
                    f"Asset references unknown module hint '{asset.module_hint}'.",
                )
            )

def _validate_volumetric_grid(config: InsertConfig, issues: list[ValidationIssue]) -> None:
    grid = config.volumetric_grid
    if grid is None:
        return

    _validate_positive_dimensions(grid.unit_size_mm, "volumetric_grid.unit_mm", issues)
    _validate_positive_grid_size(grid.size_units, "volumetric_grid.size_units", issues)
    _validate_grid_coverage(config, grid, issues)

    layer_ids = _validate_volumetric_layers(grid, issues)
    module_ids = {module.id for module in config.modules}
    modules_by_id = {module.id: module for module in config.modules}
    occupied_cells: dict[tuple[int, int, int], tuple[str, str]] = {}
    support_surface_ids = {surface.id for surface in grid.support_surfaces}
    removal_orders: dict[int, tuple[str, str]] = {}

    seen_placement_ids: set[str] = set()
    for index, placement in enumerate(grid.module_placements):
        prefix = f"volumetric_grid.module_placements[{index}]"
        if not placement.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Module placement id cannot be empty."))
        if placement.id in seen_placement_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate module placement id '{placement.id}'."))
        seen_placement_ids.add(placement.id)

        if placement.module_id not in module_ids:
            issues.append(
                _issue(
                    f"{prefix}.module_id",
                    "VOLUMETRIC_UNKNOWN_MODULE",
                    f"Module placement references unknown module '{placement.module_id}'.",
                )
            )
        if placement.layer_id is not None and placement.layer_id not in layer_ids:
            issues.append(
                _issue(
                    f"{prefix}.layer_id",
                    "VOLUMETRIC_UNKNOWN_LAYER",
                    f"Module placement references unknown layer '{placement.layer_id}'.",
                )
            )
        _validate_access_direction(placement.access_direction, f"{prefix}.access_direction", issues)
        _record_removal_order(placement.removal_order, placement.id, "module_placement", prefix, removal_orders, issues)
        if placement.removal_order is not None and placement.access_direction == "unspecified":
            issues.append(
                _issue(
                    f"{prefix}.access_direction",
                    "VOLUMETRIC_ACCESS_DIRECTION_REQUIRED",
                    "A placement with removal_order must declare an access_direction.",
                )
            )
        if placement.support_surface_id is not None and placement.support_surface_id not in support_surface_ids:
            issues.append(
                _issue(
                    f"{prefix}.support_surface_id",
                    "VOLUMETRIC_UNKNOWN_SUPPORT_SURFACE",
                    f"Module placement references unknown support surface '{placement.support_surface_id}'.",
                )
            )
        if not span_fits_grid(placement.origin_units, placement.size_units, grid.size_units):
            issues.append(_issue(prefix, "VOLUMETRIC_SPAN_OUTSIDE_GRID", "Module placement span must stay inside the grid."))
        else:
            _validate_module_placement_size(config, placement, prefix, issues)
            _record_span_cells(placement.id, "module_placement", placement.origin_units, placement.size_units, occupied_cells, prefix, issues)

        if placement.module_id in modules_by_id:
            module = modules_by_id[placement.module_id]
            if placement.instance_id is not None and not _instance_id_can_match(placement.instance_id, module.id, module.quantity):
                issues.append(
                    _issue(
                        f"{prefix}.instance_id",
                        "VOLUMETRIC_INSTANCE_ID_UNSUPPORTED",
                        "Instance id must either be omitted or match the module quantity pattern '<module_id>-NN'.",
                    )
                )

    seen_zone_ids: set[str] = set()
    for index, zone in enumerate(grid.zones):
        prefix = f"volumetric_grid.zones[{index}]"
        if not zone.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Volumetric zone id cannot be empty."))
        if zone.id in seen_zone_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate volumetric zone id '{zone.id}'."))
        seen_zone_ids.add(zone.id)
        if zone.layer_id is not None and zone.layer_id not in layer_ids:
            issues.append(
                _issue(
                    f"{prefix}.layer_id",
                    "VOLUMETRIC_UNKNOWN_LAYER",
                    f"Zone references unknown layer '{zone.layer_id}'.",
                )
            )
        if not zone.reservation_kind:
            issues.append(_issue(f"{prefix}.reservation_kind", "EMPTY_VALUE", "Reservation kind cannot be empty."))
        if not zone.asset_kind:
            issues.append(_issue(f"{prefix}.asset_kind", "EMPTY_VALUE", "Asset kind cannot be empty."))
        _validate_access_direction(zone.access_direction, f"{prefix}.access_direction", issues)
        _record_removal_order(zone.removal_order, zone.id, f"zone:{zone.kind.value}", prefix, removal_orders, issues)
        if zone.kind.value == "forbidden" and zone.removal_order is not None:
            issues.append(
                _issue(
                    f"{prefix}.removal_order",
                    "VOLUMETRIC_FORBIDDEN_ZONE_NOT_REMOVABLE",
                    "Forbidden zones reserve unreachable space and cannot have a removal_order.",
                )
            )
        if zone.removal_order is not None and zone.access_direction == "unspecified":
            issues.append(
                _issue(
                    f"{prefix}.access_direction",
                    "VOLUMETRIC_ACCESS_DIRECTION_REQUIRED",
                    "A removable reservation must declare an access_direction.",
                )
            )
        if zone.support_surface_id is not None and zone.support_surface_id not in support_surface_ids:
            issues.append(
                _issue(
                    f"{prefix}.support_surface_id",
                    "VOLUMETRIC_UNKNOWN_SUPPORT_SURFACE",
                    f"Zone references unknown support surface '{zone.support_surface_id}'.",
                )
            )
        if not span_fits_grid(zone.origin_units, zone.size_units, grid.size_units):
            issues.append(_issue(prefix, "VOLUMETRIC_SPAN_OUTSIDE_GRID", "Zone span must stay inside the grid."))
        else:
            _record_span_cells(zone.id, f"zone:{zone.kind.value}", zone.origin_units, zone.size_units, occupied_cells, prefix, issues)

    _validate_volumetric_support_surfaces(grid, layer_ids, issues)


def _validate_volumetric_support_surfaces(
    grid: VolumetricGrid,
    layer_ids: set[str],
    issues: list[ValidationIssue],
) -> None:
    seen_ids: set[str] = set()
    placement_ids = {placement.id for placement in grid.module_placements}
    zone_ids = {zone.id for zone in grid.zones}
    for index, surface in enumerate(grid.support_surfaces):
        prefix = f"volumetric_grid.support_surfaces[{index}]"
        if not surface.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Support surface id cannot be empty."))
        if surface.id in seen_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate support surface id '{surface.id}'."))
        seen_ids.add(surface.id)
        if surface.layer_id is not None and surface.layer_id not in layer_ids:
            issues.append(
                _issue(
                    f"{prefix}.layer_id",
                    "VOLUMETRIC_UNKNOWN_LAYER",
                    f"Support surface references unknown layer '{surface.layer_id}'.",
                )
            )
        if not span_fits_grid(surface.origin_units, surface.size_units, grid.size_units):
            issues.append(_issue(prefix, "VOLUMETRIC_SPAN_OUTSIDE_GRID", "Support surface span must stay inside the grid."))
        if not surface.owner_id:
            issues.append(_issue(f"{prefix}.owner_id", "EMPTY_ID", "Support surface owner_id cannot be empty."))
        if surface.owner_type == VolumetricOwnerType.MODULE_PLACEMENT and surface.owner_id not in placement_ids:
            issues.append(
                _issue(
                    f"{prefix}.owner_id",
                    "VOLUMETRIC_UNKNOWN_SUPPORT_OWNER",
                    f"Support surface references unknown module placement '{surface.owner_id}'.",
                )
            )
        if surface.owner_type == VolumetricOwnerType.ZONE and surface.owner_id not in zone_ids:
            issues.append(
                _issue(
                    f"{prefix}.owner_id",
                    "VOLUMETRIC_UNKNOWN_SUPPORT_OWNER",
                    f"Support surface references unknown zone '{surface.owner_id}'.",
                )
            )
        if surface.owner_type == VolumetricOwnerType.GRID_FLOOR and surface.owner_id != "grid":
            issues.append(
                _issue(
                    f"{prefix}.owner_id",
                    "VOLUMETRIC_GRID_FLOOR_OWNER_UNSUPPORTED",
                    "Grid-floor support surfaces must use owner_id 'grid'.",
                )
            )


def _validate_access_direction(direction: str, field: str, issues: list[ValidationIssue]) -> None:
    if direction not in ACCESS_DIRECTIONS:
        allowed = ", ".join(sorted(ACCESS_DIRECTIONS))
        issues.append(_issue(field, "VOLUMETRIC_ACCESS_DIRECTION_UNSUPPORTED", f"Allowed access directions: {allowed}."))


def _record_removal_order(
    removal_order: int | None,
    owner_id: str,
    owner_type: str,
    prefix: str,
    removal_orders: dict[int, tuple[str, str]],
    issues: list[ValidationIssue],
) -> None:
    if removal_order is None:
        return
    if removal_order <= 0:
        issues.append(_issue(f"{prefix}.removal_order", "VOLUMETRIC_REMOVAL_ORDER_INVALID", "Removal order must be greater than zero."))
        return
    previous = removal_orders.get(removal_order)
    if previous is not None:
        issues.append(
            _issue(
                f"{prefix}.removal_order",
                "VOLUMETRIC_REMOVAL_ORDER_DUPLICATE",
                f"Removal order {removal_order} is already used by {previous[1]} '{previous[0]}'.",
            )
        )
        return
    removal_orders[removal_order] = (owner_id, owner_type)

def _validate_grid_coverage(config: InsertConfig, grid: VolumetricGrid, issues: list[ValidationIssue]) -> None:
    coverage_x = grid.unit_size_mm.x * grid.size_units.x
    coverage_y = grid.unit_size_mm.y * grid.size_units.y
    coverage_z = grid.unit_size_mm.z * grid.size_units.z
    if not _same_dimension(coverage_x, config.box.inner_dimensions.x):
        issues.append(
            _issue(
                "volumetric_grid.size_units.x",
                "VOLUMETRIC_GRID_COVERAGE_MISMATCH",
                "Grid X units must cover the full box inner X dimension exactly in P8-M001.",
            )
        )
    if not _same_dimension(coverage_y, config.box.inner_dimensions.y):
        issues.append(
            _issue(
                "volumetric_grid.size_units.y",
                "VOLUMETRIC_GRID_COVERAGE_MISMATCH",
                "Grid Y units must cover the full box inner Y dimension exactly in P8-M001.",
            )
        )
    if not _same_dimension(coverage_z, config.box.usable_height_mm):
        issues.append(
            _issue(
                "volumetric_grid.size_units.z",
                "VOLUMETRIC_GRID_COVERAGE_MISMATCH",
                "Grid Z units must cover usable_height_mm exactly, not the full lid-reserved box height.",
            )
        )


def _validate_volumetric_layers(grid: VolumetricGrid, issues: list[ValidationIssue]) -> set[str]:
    layer_ids: set[str] = set()
    occupied_z: dict[int, str] = {}
    for index, layer in enumerate(grid.layers):
        prefix = f"volumetric_grid.layers[{index}]"
        if not layer.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Layer id cannot be empty."))
        if layer.id in layer_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate layer id '{layer.id}'."))
        layer_ids.add(layer.id)
        _validate_non_negative_int(layer.z_start, f"{prefix}.z_start", issues)
        _validate_positive_int(layer.z_count, f"{prefix}.z_count", issues)
        if layer.z_start + layer.z_count > grid.size_units.z:
            issues.append(_issue(prefix, "VOLUMETRIC_LAYER_OUTSIDE_GRID", "Layer Z span must stay inside the grid."))
        for z in range(layer.z_start, layer.z_start + max(layer.z_count, 0)):
            existing = occupied_z.get(z)
            if existing is not None:
                issues.append(
                    _issue(prefix, "VOLUMETRIC_LAYER_OVERLAP", f"Layer overlaps Z unit {z} already used by '{existing}'.")
                )
            else:
                occupied_z[z] = layer.id
    return layer_ids


def _validate_module_placement_size(
    config: InsertConfig,
    placement: VolumetricModulePlacement,
    prefix: str,
    issues: list[ValidationIssue],
) -> None:
    module = next((candidate for candidate in config.modules if candidate.id == placement.module_id), None)
    if module is None:
        return
    span_x = placement.size_units.x * config.volumetric_grid.unit_size_mm.x  # type: ignore[union-attr]
    span_y = placement.size_units.y * config.volumetric_grid.unit_size_mm.y  # type: ignore[union-attr]
    span_z = placement.size_units.z * config.volumetric_grid.unit_size_mm.z  # type: ignore[union-attr]
    if span_x < module.min_dimensions.x or span_y < module.min_dimensions.y or span_z < module.desired_height_mm:
        issues.append(
            _issue(
                prefix,
                "VOLUMETRIC_PLACEMENT_TOO_SMALL",
                "Module placement units must translate to millimeter dimensions at least as large as the module request.",
            )
        )


def _record_span_cells(
    owner_id: str,
    owner_type: str,
    origin: GridPoint3D,
    size: GridSize3D,
    occupied_cells: dict[tuple[int, int, int], tuple[str, str]],
    prefix: str,
    issues: list[ValidationIssue],
) -> None:
    for cell in span_cells(origin, size):
        previous = occupied_cells.get(cell)
        if previous is not None:
            issues.append(
                _issue(
                    prefix,
                    "VOLUMETRIC_CELL_COLLISION",
                    f"Cell {cell} is already used by {previous[1]} '{previous[0]}'.",
                )
            )
        else:
            occupied_cells[cell] = (owner_id, owner_type)


def _validate_positive_grid_size(size: GridSize3D, field: str, issues: list[ValidationIssue]) -> None:
    _validate_positive_int(size.x, f"{field}.x", issues)
    _validate_positive_int(size.y, f"{field}.y", issues)
    _validate_positive_int(size.z, f"{field}.z", issues)


def _validate_non_negative_int(value: int, field: str, issues: list[ValidationIssue]) -> None:
    if value < 0:
        issues.append(_issue(field, "NEGATIVE_VALUE", "Value must be greater than or equal to zero."))


def _same_dimension(left: float, right: float) -> bool:
    return abs(left - right) < 1e-6


def _instance_id_can_match(instance_id: str, module_id: str, quantity: int) -> bool:
    prefix, separator, suffix = instance_id.rpartition("-")
    if separator != "-" or prefix != module_id or not suffix.isdigit():
        return False
    return 1 <= int(suffix) <= quantity

def _validate_module_cavities(
    cavities: tuple[Cavity, ...],
    module_field: str,
    module_size: Dimension3D,
    module_height_mm: float,
    tolerances: ToleranceProfile,
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
        minimum_clearance = _minimum_profile_cavity_clearance(cavity, tolerances)
        if minimum_clearance is not None:
            minimum_value, source = minimum_clearance
            if cavity.clearance_mm < minimum_value:
                issues.append(
                    _issue(
                        f"{prefix}.clearance_mm",
                        _clearance_issue_code(cavity),
                        (
                            "Cavity clearance must be at least the active profile value "
                            f"from {source} ({minimum_value:.2f} mm)."
                        ),
                    )
                )

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

        _validate_cavity_features(cavity.features, prefix, cavity.size, issues)


def _validate_cavity_features(
    features: tuple[Feature, ...],
    cavity_field: str,
    cavity_size: Dimension3D,
    issues: list[ValidationIssue],
) -> None:
    seen_ids: set[str] = set()
    size_required_kinds = {
        FeatureKind.FINGER_NOTCH,
        FeatureKind.SIDE_NOTCH,
        FeatureKind.CENTER_NOTCH,
        FeatureKind.HALF_MOON_NOTCH,
        FeatureKind.GRIP_AID,
    }
    radius_required_kinds = {FeatureKind.HALF_MOON_NOTCH, FeatureKind.ROUNDED_FLOOR}

    for index, feature in enumerate(features):
        prefix = f"{cavity_field}.features[{index}]"
        if not feature.id:
            issues.append(_issue(f"{prefix}.id", "EMPTY_ID", "Feature id cannot be empty."))
        if feature.id in seen_ids:
            issues.append(_issue(f"{prefix}.id", "DUPLICATE_ID", f"Duplicate feature id '{feature.id}'."))
        seen_ids.add(feature.id)

        if not feature.placement:
            issues.append(_issue(f"{prefix}.placement", "EMPTY_PLACEMENT", "Feature placement cannot be empty."))
        if feature.taxonomy is not None and not is_feature_taxonomy_compatible(feature.kind, feature.taxonomy):
            issues.append(
                _issue(
                    f"{prefix}.taxonomy",
                    "FEATURE_TAXONOMY_INCOMPATIBLE",
                    (
                        f"Feature taxonomy '{feature.taxonomy.value}' is not compatible "
                        f"with kind '{feature.kind.value}'."
                    ),
                )
            )
        if feature.status != "abstract_only":
            issues.append(
                _issue(
                    f"{prefix}.status",
                    "FEATURE_STATUS_UNSUPPORTED",
                    "Cavity features must remain abstract_only in P5-M004.",
                )
            )
        if feature.fusion_generation != "not_implemented":
            issues.append(
                _issue(
                    f"{prefix}.fusion_generation",
                    "FEATURE_FUSION_GENERATION_UNSUPPORTED",
                    "Fusion generation for cavity features is gated and must be not_implemented.",
                )
            )

        _validate_non_negative_number(feature.position.x, f"{prefix}.position_mm.x", issues)
        _validate_non_negative_number(feature.position.y, f"{prefix}.position_mm.y", issues)
        _validate_non_negative_number(feature.position.z, f"{prefix}.position_mm.z", issues)

        if feature.size is None and feature.kind in size_required_kinds:
            issues.append(
                _issue(
                    f"{prefix}.size_mm",
                    "CAVITY_FEATURE_SIZE_REQUIRED",
                    f"Feature kind '{feature.kind.value}' requires size_mm.",
                )
            )
        if feature.size is not None:
            _validate_positive_dimensions(feature.size, f"{prefix}.size_mm", issues)
            if (
                feature.position.x + feature.size.x > cavity_size.x
                or feature.position.y + feature.size.y > cavity_size.y
                or feature.position.z + feature.size.z > cavity_size.z
            ):
                issues.append(
                    _issue(
                        prefix,
                        "CAVITY_FEATURE_OUTSIDE_CAVITY",
                        "Feature position plus size must stay inside the cavity local dimensions.",
                    )
                )
        elif (
            feature.position.x > cavity_size.x
            or feature.position.y > cavity_size.y
            or feature.position.z > cavity_size.z
        ):
            issues.append(
                _issue(
                    prefix,
                    "CAVITY_FEATURE_OUTSIDE_CAVITY",
                    "Feature position must stay inside the cavity local dimensions.",
                )
            )

        if feature.radius_mm is None and feature.kind in radius_required_kinds:
            issues.append(
                _issue(
                    f"{prefix}.radius_mm",
                    "CAVITY_FEATURE_RADIUS_REQUIRED",
                    f"Feature kind '{feature.kind.value}' requires radius_mm.",
                )
            )
        if feature.radius_mm is not None:
            _validate_positive_number(feature.radius_mm, f"{prefix}.radius_mm", issues)
            max_radius = min(cavity_size.x, cavity_size.y) / 2.0
            if feature.radius_mm > max_radius:
                issues.append(
                    _issue(
                        f"{prefix}.radius_mm",
                        "CAVITY_FEATURE_RADIUS_TOO_LARGE",
                        f"Feature radius must not exceed half the smallest cavity XY dimension ({max_radius:.2f} mm).",
                    )
                )



def _minimum_profile_cavity_clearance(
    cavity: Cavity,
    tolerances: ToleranceProfile,
) -> tuple[float, str] | None:
    if cavity.functional_type == FunctionalType.CARDS:
        return tolerances.card_clearance_mm, "tolerances.card_clearance_mm"
    if cavity.functional_type == FunctionalType.SLEEVED_CARDS:
        return tolerances.sleeved_card_clearance_mm, "tolerances.sleeved_card_clearance_mm"
    if cavity.functional_type == FunctionalType.TOKENS:
        return tolerances.token_clearance_mm, "tolerances.token_clearance_mm"
    if cavity.functional_type == FunctionalType.DICE:
        return tolerances.token_clearance_mm, "tolerances.token_clearance_mm"
    if cavity.functional_type == FunctionalType.MEEPLES:
        return tolerances.meeple_clearance_mm, "tolerances.meeple_clearance_mm"
    return None


def _clearance_issue_code(cavity: Cavity) -> str:
    if cavity.functional_type in (FunctionalType.CARDS, FunctionalType.SLEEVED_CARDS):
        return "CARD_CAVITY_CLEARANCE_TOO_LOW"
    return "OPEN_RECEPTACLE_CLEARANCE_TOO_LOW"


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
