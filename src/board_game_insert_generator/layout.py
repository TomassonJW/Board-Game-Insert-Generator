from __future__ import annotations

from board_game_insert_generator.models import (
    IMPLEMENTED_LAYOUT_STRATEGIES,
    LAYOUT_STRATEGY_GRID,
    LAYOUT_STRATEGY_ROW_FILL,
    Cell,
    Dimension3D,
    InsertConfig,
    LayoutResult,
    Point3D,
)
from board_game_insert_generator.tolerance import build_printable_bodies
from board_game_insert_generator.validation import assert_valid_config


class LayoutError(ValueError):
    """Raised when the configured modules cannot be placed by the V0 strategy."""


def generate_basic_layout(config: InsertConfig) -> LayoutResult:
    assert_valid_config(config)

    if config.layout.strategy == LAYOUT_STRATEGY_ROW_FILL:
        cells = _row_fill_cells(config)
        layout_warning = "V0 row_fill layout is deterministic but not optimized."
    elif config.layout.strategy == LAYOUT_STRATEGY_GRID:
        cells = _grid_cells(config)
        layout_warning = "V0 grid layout uses regular cells and is not optimized."
    else:
        raise LayoutError(
            f"Unsupported layout strategy: {config.layout.strategy}. "
            f"Implemented strategies: {_implemented_strategies_label()}."
        )

    printable_bodies = build_printable_bodies(cells, config)
    warnings = (
        layout_warning,
        "Printable dimensions still require real print validation.",
    )
    return LayoutResult(cells=cells, printable_bodies=printable_bodies, warnings=warnings)


def _row_fill_cells(config: InsertConfig) -> tuple[Cell, ...]:
    box = config.box.inner_dimensions
    cursor_x = 0.0
    cursor_y = 0.0
    row_depth = 0.0
    cells: list[Cell] = []

    instances = _expanded_instances(config)
    for source_index, module, instance_number in instances:
        size, rotated = _choose_orientation(
            desired=Dimension3D(
                x=module.min_dimensions.x,
                y=module.min_dimensions.y,
                z=module.desired_height_mm,
            ),
            allow_rotation=module.allow_rotation,
            remaining_x=box.x - cursor_x,
            max_x=box.x,
        )

        if size.x > box.x:
            raise LayoutError(
                f"Module '{module.id}' is wider than the box even after allowed rotation."
            )

        if cursor_x > 0 and size.x > box.x - cursor_x:
            cursor_x = 0.0
            cursor_y += row_depth
            row_depth = 0.0
            size, rotated = _choose_orientation(
                desired=Dimension3D(
                    x=module.min_dimensions.x,
                    y=module.min_dimensions.y,
                    z=module.desired_height_mm,
                ),
                allow_rotation=module.allow_rotation,
                remaining_x=box.x,
                max_x=box.x,
            )

        if cursor_y + size.y > box.y:
            raise LayoutError(
                f"Module '{module.id}' cannot fit with V0 row_fill layout. "
                f"Needed Y up to {cursor_y + size.y:.2f} mm, box has {box.y:.2f} mm."
            )

        instance_id = f"{module.id}-{instance_number:02d}"
        cells.append(
            Cell(
                module_id=module.id,
                instance_id=instance_id,
                label=module.name,
                functional_type=module.functional_type,
                origin=Point3D(x=cursor_x, y=cursor_y, z=0.0),
                size=size,
                source_index=source_index,
                rotated=rotated,
            )
        )
        cursor_x += size.x
        row_depth = max(row_depth, size.y)

    return tuple(cells)


def _grid_cells(config: InsertConfig) -> tuple[Cell, ...]:
    box = config.box.inner_dimensions
    planned_cells = []

    instances = _expanded_instances(config)
    for source_index, module, instance_number in instances:
        size, rotated = _choose_box_orientation(
            desired=Dimension3D(
                x=module.min_dimensions.x,
                y=module.min_dimensions.y,
                z=module.desired_height_mm,
            ),
            allow_rotation=module.allow_rotation,
            max_x=box.x,
            max_y=box.y,
        )

        if size.x > box.x or size.y > box.y:
            raise LayoutError(
                f"Module '{module.id}' cannot fit in one V0 grid cell "
                "even after allowed rotation."
            )

        planned_cells.append((source_index, module, instance_number, size, rotated))

    if not planned_cells:
        return ()

    cell_width = max(size.x for _, _, _, size, _ in planned_cells)
    cell_depth = max(size.y for _, _, _, size, _ in planned_cells)
    columns = int(box.x // cell_width)
    if columns < 1:
        raise LayoutError(
            f"Grid cell width {cell_width:.2f} mm cannot fit in box width {box.x:.2f} mm."
        )

    row_count = (len(planned_cells) + columns - 1) // columns
    needed_y = row_count * cell_depth
    if needed_y > box.y:
        raise LayoutError(
            f"Grid layout cannot fit {len(planned_cells)} instance(s). "
            f"Needed Y up to {needed_y:.2f} mm, box has {box.y:.2f} mm."
        )

    cells: list[Cell] = []
    for index, (source_index, module, instance_number, size, rotated) in enumerate(planned_cells):
        column = index % columns
        row = index // columns
        instance_id = f"{module.id}-{instance_number:02d}"
        cells.append(
            Cell(
                module_id=module.id,
                instance_id=instance_id,
                label=module.name,
                functional_type=module.functional_type,
                origin=Point3D(x=column * cell_width, y=row * cell_depth, z=0.0),
                size=Dimension3D(x=cell_width, y=cell_depth, z=size.z),
                source_index=source_index,
                rotated=rotated,
            )
        )

    return tuple(cells)


def _choose_orientation(
    desired: Dimension3D,
    allow_rotation: bool,
    remaining_x: float,
    max_x: float,
) -> tuple[Dimension3D, bool]:
    normal_fits_remaining = desired.x <= remaining_x
    normal_fits_box = desired.x <= max_x
    rotated = desired.rotated_xy()
    rotated_fits_remaining = allow_rotation and rotated.x <= remaining_x
    rotated_fits_box = allow_rotation and rotated.x <= max_x

    if normal_fits_remaining:
        return desired, False
    if rotated_fits_remaining:
        return rotated, True
    if normal_fits_box:
        return desired, False
    if rotated_fits_box:
        return rotated, True
    return desired, False


def _choose_box_orientation(
    desired: Dimension3D,
    allow_rotation: bool,
    max_x: float,
    max_y: float,
) -> tuple[Dimension3D, bool]:
    normal_fits = desired.x <= max_x and desired.y <= max_y
    rotated = desired.rotated_xy()
    rotated_fits = allow_rotation and rotated.x <= max_x and rotated.y <= max_y

    if normal_fits:
        return desired, False
    if rotated_fits:
        return rotated, True
    return desired, False


def _expanded_instances(config: InsertConfig):
    ordered = sorted(
        enumerate(config.modules),
        key=lambda item: (-item[1].priority, item[0]),
    )
    for source_index, module in ordered:
        for instance_number in range(1, module.quantity + 1):
            yield source_index, module, instance_number


def _implemented_strategies_label() -> str:
    return ", ".join(IMPLEMENTED_LAYOUT_STRATEGIES)
