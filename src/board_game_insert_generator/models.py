"""Core value objects for the pure Python engine.

All domain dimensions are expressed in millimeters. These dataclasses stay
lightweight on purpose: aggregate validation lives in `validation.py` so the CLI
can report multiple actionable issues at once instead of failing on the first
constructor call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FunctionalType(str, Enum):
    CARDS = "cards"
    SLEEVED_CARDS = "sleeved_cards"
    TOKENS = "tokens"
    MEEPLES = "meeples"
    DICE = "dice"
    FREE = "free"
    OTHER = "other"


@dataclass(frozen=True)
class Dimension3D:
    x: float
    y: float
    z: float

    def rotated_xy(self) -> "Dimension3D":
        return Dimension3D(x=self.y, y=self.x, z=self.z)


@dataclass(frozen=True)
class Point3D:
    x: float
    y: float
    z: float = 0.0


@dataclass(frozen=True)
class BoxSpec:
    inner_dimensions: Dimension3D
    usable_height_mm: float
    lid_clearance_mm: float


@dataclass(frozen=True)
class ToleranceProfile:
    peripheral_clearance_mm: float = 0.8
    module_gap_mm: float = 0.6
    vertical_lid_clearance_mm: float = 1.0
    card_clearance_mm: float = 0.5
    sleeved_card_clearance_mm: float = 1.0
    token_clearance_mm: float = 0.6
    meeple_clearance_mm: float = 1.0
    sliding_lid_clearance_mm: float = 0.35
    hinge_clearance_mm: float = 0.4
    printer_compensation_mm: float = 0.0
    default_corner_radius_mm: float = 1.5
    default_chamfer_mm: float = 0.4


@dataclass(frozen=True)
class GeometryDefaults:
    wall_thickness_mm: float = 1.2
    floor_thickness_mm: float = 1.2
    corner_radius_mm: float = 1.5


@dataclass(frozen=True)
class LayoutSettings:
    strategy: str = "row_fill"
    allow_global_rotation: bool = False


@dataclass(frozen=True)
class ModuleRequest:
    id: str
    name: str
    functional_type: FunctionalType
    min_dimensions: Dimension3D
    desired_height_mm: float
    priority: int
    allow_rotation: bool
    quantity: int = 1
    comment: str = ""


@dataclass(frozen=True)
class InsertConfig:
    project_name: str
    units: str
    box: BoxSpec
    tolerances: ToleranceProfile
    defaults: GeometryDefaults
    layout: LayoutSettings
    modules: tuple[ModuleRequest, ...]
    source_path: str | None = None


@dataclass(frozen=True)
class Cell:
    module_id: str
    instance_id: str
    label: str
    functional_type: FunctionalType
    origin: Point3D
    size: Dimension3D
    source_index: int
    rotated: bool = False


@dataclass(frozen=True)
class PrimitiveVolume:
    id: str
    origin: Point3D
    size: Dimension3D


@dataclass(frozen=True)
class CompositeModule:
    id: str
    primitive_volumes: tuple[PrimitiveVolume, ...]
    note: str = ""


@dataclass(frozen=True)
class Cavity:
    id: str
    functional_type: FunctionalType
    origin: Point3D
    size: Dimension3D
    clearance_mm: float


@dataclass(frozen=True)
class Feature:
    id: str
    kind: str
    parameters: dict[str, float | str | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class FaceOffsets:
    x_min: float = 0.0
    x_max: float = 0.0
    y_min: float = 0.0
    y_max: float = 0.0
    z_min: float = 0.0
    z_max: float = 0.0


@dataclass(frozen=True)
class PrintableBody:
    module_id: str
    instance_id: str
    body_id: str
    origin: Point3D
    size: Dimension3D
    offsets: FaceOffsets
    primitive_volumes: tuple[PrimitiveVolume, ...]


@dataclass(frozen=True)
class LayoutResult:
    cells: tuple[Cell, ...]
    printable_bodies: tuple[PrintableBody, ...]
    warnings: tuple[str, ...] = ()
