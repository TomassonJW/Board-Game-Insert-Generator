from __future__ import annotations

from board_game_insert_generator.models import (
    Cell,
    Dimension3D,
    FaceClassification,
    FaceName,
    FaceOffsets,
    FaceRole,
    FaceToleranceApplication,
    InsertConfig,
    Point3D,
    PrimitiveVolume,
    PrintableBody,
)


EPSILON = 1e-6
ORDERED_FACE_NAMES = (
    FaceName.X_MIN,
    FaceName.X_MAX,
    FaceName.Y_MIN,
    FaceName.Y_MAX,
    FaceName.Z_MIN,
    FaceName.Z_MAX,
)
HORIZONTAL_FACE_NAMES = (FaceName.X_MIN, FaceName.X_MAX, FaceName.Y_MIN, FaceName.Y_MAX)


class ToleranceError(ValueError):
    """Raised when tolerance offsets make a printable body invalid."""


def build_printable_bodies(cells: tuple[Cell, ...], config: InsertConfig) -> tuple[PrintableBody, ...]:
    return tuple(printable_body_for_cell(cell, cells, config) for cell in cells)


def printable_body_for_cell(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    config: InsertConfig,
) -> PrintableBody:
    face_classifications = classify_cell_faces(cell, all_cells, config)
    tolerance_applications = face_tolerance_applications_from_classifications(
        face_classifications,
        config,
    )
    offsets = face_offsets_from_applications(tolerance_applications)
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
        face_classifications=face_classifications,
        tolerance_applications=tolerance_applications,
    )


def classify_cell_faces(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    config: InsertConfig,
) -> tuple[FaceClassification, ...]:
    return (
        _classify_horizontal_face(cell, all_cells, config, FaceName.X_MIN, axis="x", direction=-1),
        _classify_horizontal_face(cell, all_cells, config, FaceName.X_MAX, axis="x", direction=1),
        _classify_horizontal_face(cell, all_cells, config, FaceName.Y_MIN, axis="y", direction=-1),
        _classify_horizontal_face(cell, all_cells, config, FaceName.Y_MAX, axis="y", direction=1),
        FaceClassification(
            face=FaceName.Z_MIN,
            role=FaceRole.FUNCTIONAL,
            reason="Bottom face is anchored at Z=0; no V0 clearance is applied.",
        ),
        FaceClassification(
            face=FaceName.Z_MAX,
            role=FaceRole.FUNCTIONAL,
            reason="Top face receives vertical lid clearance in V0.",
        ),
    )


def face_offsets_for_cell(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    config: InsertConfig,
) -> FaceOffsets:
    return face_offsets_from_classifications(classify_cell_faces(cell, all_cells, config), config)


def face_offsets_from_classifications(
    classifications: tuple[FaceClassification, ...],
    config: InsertConfig,
) -> FaceOffsets:
    return face_offsets_from_applications(
        face_tolerance_applications_from_classifications(classifications, config)
    )


def face_tolerance_applications_from_classifications(
    classifications: tuple[FaceClassification, ...],
    config: InsertConfig,
) -> tuple[FaceToleranceApplication, ...]:
    by_face = {classification.face: classification for classification in classifications}
    missing_faces = [face.value for face in ORDERED_FACE_NAMES if face not in by_face]
    if missing_faces:
        raise ToleranceError(f"Missing face classifications: {', '.join(missing_faces)}.")
    return tuple(
        _tolerance_application_for_classification(by_face[face], config)
        for face in ORDERED_FACE_NAMES
    )


def face_offsets_from_applications(
    applications: tuple[FaceToleranceApplication, ...],
) -> FaceOffsets:
    by_face = {application.face: application for application in applications}
    missing_faces = [face.value for face in ORDERED_FACE_NAMES if face not in by_face]
    if missing_faces:
        raise ToleranceError(f"Missing face tolerance applications: {', '.join(missing_faces)}.")
    return FaceOffsets(
        x_min=by_face[FaceName.X_MIN].offset_mm,
        x_max=by_face[FaceName.X_MAX].offset_mm,
        y_min=by_face[FaceName.Y_MIN].offset_mm,
        y_max=by_face[FaceName.Y_MAX].offset_mm,
        z_min=by_face[FaceName.Z_MIN].offset_mm,
        z_max=by_face[FaceName.Z_MAX].offset_mm,
    )


def _tolerance_application_for_classification(
    classification: FaceClassification,
    config: InsertConfig,
) -> FaceToleranceApplication:
    profile = config.tolerances
    compensation = profile.printer_compensation_mm

    if classification.role == FaceRole.INTERNAL:
        return _application(
            classification,
            offset_mm=0.0,
            rule_id="internal_no_clearance",
            clearance_source="none",
            receives_clearance=False,
            rule_reason="Internal faces keep shared material and receive no clearance.",
        )
    if classification.role == FaceRole.WELDED:
        return _application(
            classification,
            offset_mm=0.0,
            rule_id="welded_no_clearance",
            clearance_source="none",
            receives_clearance=False,
            rule_reason="Welded faces keep continuous material and receive no clearance.",
        )

    if classification.face == FaceName.Z_MIN:
        return _application(
            classification,
            offset_mm=0.0,
            rule_id="bottom_anchor_no_clearance",
            clearance_source="none",
            receives_clearance=False,
            rule_reason="Bottom face remains anchored at Z=0.",
        )
    if classification.face == FaceName.Z_MAX and classification.role == FaceRole.FUNCTIONAL:
        return _application(
            classification,
            offset_mm=profile.vertical_lid_clearance_mm,
            rule_id="functional_vertical_lid_clearance",
            clearance_source="vertical_lid_clearance_mm",
            receives_clearance=True,
            rule_reason="Top functional face receives vertical lid clearance.",
        )

    if classification.face in HORIZONTAL_FACE_NAMES:
        if classification.role == FaceRole.PERIPHERAL:
            return _application(
                classification,
                offset_mm=profile.peripheral_clearance_mm + compensation,
                rule_id="peripheral_clearance",
                clearance_source="peripheral_clearance_mm + printer_compensation_mm",
                receives_clearance=True,
                rule_reason="Peripheral face receives box clearance.",
            )
        if classification.role == FaceRole.NEIGHBOR:
            return _application(
                classification,
                offset_mm=(profile.module_gap_mm / 2.0) + compensation,
                rule_id="neighbor_half_module_gap",
                clearance_source="module_gap_mm / 2 + printer_compensation_mm",
                receives_clearance=True,
                rule_reason="Neighbor face receives half of the inter-module gap.",
            )
        if classification.role == FaceRole.EXPOSED:
            return _application(
                classification,
                offset_mm=compensation,
                rule_id="exposed_printer_compensation_only",
                clearance_source=_compensation_source(compensation),
                receives_clearance=False,
                rule_reason="Exposed face receives no clearance; only printer compensation can apply.",
            )
        if classification.role == FaceRole.FUNCTIONAL:
            return _application(
                classification,
                offset_mm=compensation,
                rule_id="functional_printer_compensation_only",
                clearance_source=_compensation_source(compensation),
                receives_clearance=False,
                rule_reason="Horizontal functional face has no V0 dedicated clearance.",
            )

    return _application(
        classification,
        offset_mm=0.0,
        rule_id="no_v0_clearance_rule",
        clearance_source="none",
        receives_clearance=False,
        rule_reason="No V0 tolerance rule applies to this face and role.",
    )


def _application(
    classification: FaceClassification,
    *,
    offset_mm: float,
    rule_id: str,
    clearance_source: str,
    receives_clearance: bool,
    rule_reason: str,
) -> FaceToleranceApplication:
    return FaceToleranceApplication(
        face=classification.face,
        role=classification.role,
        offset_mm=offset_mm,
        rule_id=rule_id,
        clearance_source=clearance_source,
        receives_clearance=receives_clearance,
        reason=f"{classification.reason} Rule: {rule_reason}",
    )


def _compensation_source(compensation: float) -> str:
    if compensation == 0:
        return "none"
    return "printer_compensation_mm"


def _classify_horizontal_face(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    config: InsertConfig,
    face: FaceName,
    axis: str,
    direction: int,
) -> FaceClassification:
    if _touches_box_boundary(cell, config, face):
        return FaceClassification(
            face=face,
            role=FaceRole.PERIPHERAL,
            reason="Face touches the measured inner box boundary.",
        )

    neighbor_instance_id = _neighbor_instance_id(cell, all_cells, axis=axis, direction=direction)
    if neighbor_instance_id is not None:
        return FaceClassification(
            face=face,
            role=FaceRole.NEIGHBOR,
            reason="Face touches another theoretical layout cell.",
            neighbor_instance_id=neighbor_instance_id,
        )

    return FaceClassification(
        face=face,
        role=FaceRole.EXPOSED,
        reason="Face is exposed in free space; no box boundary or neighbor touches it.",
    )


def _touches_box_boundary(cell: Cell, config: InsertConfig, face: FaceName) -> bool:
    box = config.box.inner_dimensions
    if face == FaceName.X_MIN:
        return _almost_equal(cell.origin.x, 0.0)
    if face == FaceName.X_MAX:
        return _almost_equal(cell.origin.x + cell.size.x, box.x)
    if face == FaceName.Y_MIN:
        return _almost_equal(cell.origin.y, 0.0)
    if face == FaceName.Y_MAX:
        return _almost_equal(cell.origin.y + cell.size.y, box.y)
    return False


def _has_neighbor(cell: Cell, all_cells: tuple[Cell, ...], axis: str, direction: int) -> bool:
    return _neighbor_instance_id(cell, all_cells, axis=axis, direction=direction) is not None


def _neighbor_instance_id(
    cell: Cell,
    all_cells: tuple[Cell, ...],
    axis: str,
    direction: int,
) -> str | None:
    for other in all_cells:
        if other.instance_id == cell.instance_id:
            continue
        if axis == "x" and _touching_x(cell, other, direction):
            return other.instance_id
        if axis == "y" and _touching_y(cell, other, direction):
            return other.instance_id
    return None


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
