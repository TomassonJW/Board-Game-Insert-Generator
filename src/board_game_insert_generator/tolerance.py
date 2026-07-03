from __future__ import annotations

from board_game_insert_generator.models import (
    Cell,
    Dimension3D,
    FaceOffsets,
    InsertConfig,
    Point3D,
    PrimitiveVolume,
    PrintableBody,
)


EPSILON = 1e-6


class ToleranceError(ValueError):
    """Raised when tolerance offsets make a printable body invalid."""


def build_printable_bodies(cells: tuple[Cell, ...], config: InsertConfig) -> tuple[PrintableBody, ...]:
    return tuple(printable_body_for_cell(cell, cells, config) for cell in cells)


def printable_body_for_cell(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    config: InsertConfig,
) -> PrintableBody:
    offsets = face_offsets_for_cell(cell, all_cells, config)
    printable_size = Dimension3D(
        x=cell.size.x - offsets.x_min - offsets.x_max,
        y=cell.size.y - offsets.y_min - offsets.y_max,
        z=cell.size.z - offsets.z_min - offsets.z_max,
    )
    if printable_size.x <= 0 or printable_size.y <= 0 or printable_size.z <= 0:
        raise ToleranceError(
            f"Tolerance offsets make module '{cell.instance_id}' non-positive: "
            f"{printable_size.x:.2f} x {printable_size.y:.2f} x {printable_size.z:.2f} mm."
        )

    origin = Point3D(
        x=cell.origin.x + offsets.x_min,
        y=cell.origin.y + offsets.y_min,
        z=cell.origin.z + offsets.z_min,
    )
    primitive = PrimitiveVolume(
        id=f"{cell.instance_id}-primitive-01",
        origin=origin,
        size=printable_size,
    )
    return PrintableBody(
        module_id=cell.module_id,
        instance_id=cell.instance_id,
        body_id=f"{cell.instance_id}-body",
        origin=origin,
        size=printable_size,
        offsets=offsets,
        primitive_volumes=(primitive,),
    )


def face_offsets_for_cell(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    config: InsertConfig,
) -> FaceOffsets:
    profile = config.tolerances
    box = config.box.inner_dimensions
    compensation = profile.printer_compensation_mm

    return FaceOffsets(
        x_min=_horizontal_offset(
            touches_boundary=_almost_equal(cell.origin.x, 0.0),
            has_neighbor=_has_neighbor(cell, all_cells, axis="x", direction=-1),
            peripheral_clearance=profile.peripheral_clearance_mm,
            module_gap=profile.module_gap_mm,
            printer_compensation=compensation,
        ),
        x_max=_horizontal_offset(
            touches_boundary=_almost_equal(cell.origin.x + cell.size.x, box.x),
            has_neighbor=_has_neighbor(cell, all_cells, axis="x", direction=1),
            peripheral_clearance=profile.peripheral_clearance_mm,
            module_gap=profile.module_gap_mm,
            printer_compensation=compensation,
        ),
        y_min=_horizontal_offset(
            touches_boundary=_almost_equal(cell.origin.y, 0.0),
            has_neighbor=_has_neighbor(cell, all_cells, axis="y", direction=-1),
            peripheral_clearance=profile.peripheral_clearance_mm,
            module_gap=profile.module_gap_mm,
            printer_compensation=compensation,
        ),
        y_max=_horizontal_offset(
            touches_boundary=_almost_equal(cell.origin.y + cell.size.y, box.y),
            has_neighbor=_has_neighbor(cell, all_cells, axis="y", direction=1),
            peripheral_clearance=profile.peripheral_clearance_mm,
            module_gap=profile.module_gap_mm,
            printer_compensation=compensation,
        ),
        z_min=0.0,
        z_max=profile.vertical_lid_clearance_mm,
    )


def _horizontal_offset(
    touches_boundary: bool,
    has_neighbor: bool,
    peripheral_clearance: float,
    module_gap: float,
    printer_compensation: float,
) -> float:
    if touches_boundary:
        return peripheral_clearance + printer_compensation
    if has_neighbor:
        return (module_gap / 2.0) + printer_compensation
    return printer_compensation


def _has_neighbor(cell: Cell, all_cells: tuple[Cell, ...], axis: str, direction: int) -> bool:
    for other in all_cells:
        if other.instance_id == cell.instance_id:
            continue
        if axis == "x" and _touching_x(cell, other, direction):
            return True
        if axis == "y" and _touching_y(cell, other, direction):
            return True
    return False


def _touching_x(cell: Cell, other: Cell, direction: int) -> bool:
    target_x = cell.origin.x + cell.size.x if direction > 0 else cell.origin.x
    other_x = other.origin.x if direction > 0 else other.origin.x + other.size.x
    return _almost_equal(target_x, other_x) and _intervals_overlap(
        cell.origin.y,
        cell.origin.y + cell.size.y,
        other.origin.y,
        other.origin.y + other.size.y,
    )


def _touching_y(cell: Cell, other: Cell, direction: int) -> bool:
    target_y = cell.origin.y + cell.size.y if direction > 0 else cell.origin.y
    other_y = other.origin.y if direction > 0 else other.origin.y + other.size.y
    return _almost_equal(target_y, other_y) and _intervals_overlap(
        cell.origin.x,
        cell.origin.x + cell.size.x,
        other.origin.x,
        other.origin.x + other.size.x,
    )


def _intervals_overlap(a_min: float, a_max: float, b_min: float, b_max: float) -> bool:
    return min(a_max, b_max) - max(a_min, b_min) > EPSILON


def _almost_equal(left: float, right: float) -> bool:
    return abs(left - right) <= EPSILON
