"""Core value objects for the pure Python engine.

All domain dimensions are expressed in millimeters. These dataclasses stay
lightweight on purpose: aggregate validation lives in `validation.py` so the CLI
can report multiple actionable issues at once instead of failing on the first
constructor call.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FunctionalType(str, Enum):
    CARDS = "cards"
    SLEEVED_CARDS = "sleeved_cards"
    TOKENS = "tokens"
    MEEPLES = "meeples"
    DICE = "dice"
    FREE = "free"
    OTHER = "other"


class FeatureKind(str, Enum):
    FINGER_NOTCH = "finger_notch"
    SIDE_NOTCH = "side_notch"
    CENTER_NOTCH = "center_notch"
    HALF_MOON_NOTCH = "half_moon_notch"
    ROUNDED_FLOOR = "rounded_floor"
    GRIP_AID = "grip_aid"


class FeatureTaxonomyKind(str, Enum):
    TOP_OPEN_RECTANGULAR_NOTCH = "top_open_rectangular_notch"
    TOP_OPEN_HALF_MOON_NOTCH = "top_open_half_moon_notch"
    THROUGH_WALL_WINDOW = "through_wall_window"
    BLIND_INTERNAL_THUMB_SCOOP = "blind_internal_thumb_scoop"
    SIDE_RELIEF_NOTCH = "side_relief_notch"
    DUAL_SIDE_CARD_ACCESS = "dual_side_card_access"
    ROUNDED_FLOOR_INTENT = "rounded_floor_intent"


class VolumetricZoneKind(str, Enum):
    RESERVED = "reserved"
    FORBIDDEN = "forbidden"


class AssetKind(str, Enum):
    CARDS = "cards"
    SLEEVED_CARDS = "sleeved_cards"
    TOKENS = "tokens"
    DICE = "dice"
    MEEPLES = "meeples"
    BOARD = "board"
    RULEBOOK = "rulebook"
    TRAY = "tray"
    MINIATURE = "miniature"
    OTHER = "other"


class DimensionConfidence(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    UNKNOWN_Z = "unknown_z"


class ContainmentIntent(str, Enum):
    STORE = "store"
    SEPARATE = "separate"
    PROTECT = "protect"
    DISPLAY = "display"
    RESERVE = "reserve"
    ACCESS_FIRST = "access_first"


class AssetStorageOrientation(str, Enum):
    AUTO = "auto"
    FLAT_TRAY = "flat_tray"
    VERTICAL_STACK = "vertical_stack"


class VolumetricOwnerType(str, Enum):
    GRID_FLOOR = "grid_floor"
    MODULE_PLACEMENT = "module_placement"
    ZONE = "zone"


class VolumetricFace(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"


LAYOUT_STRATEGY_ROW_FILL = "row_fill"
LAYOUT_STRATEGY_GRID = "grid"
LAYOUT_STRATEGY_COLUMNS = "columns"

IMPLEMENTED_LAYOUT_STRATEGIES = (LAYOUT_STRATEGY_ROW_FILL, LAYOUT_STRATEGY_GRID)
RESERVED_LAYOUT_STRATEGIES = (LAYOUT_STRATEGY_COLUMNS,)


class FaceName(str, Enum):
    X_MIN = "x_min"
    X_MAX = "x_max"
    Y_MIN = "y_min"
    Y_MAX = "y_max"
    Z_MIN = "z_min"
    Z_MAX = "z_max"


class FaceRole(str, Enum):
    PERIPHERAL = "peripheral"
    NEIGHBOR = "neighbor"
    EXPOSED = "exposed"
    FUNCTIONAL = "functional"
    INTERNAL = "internal"
    WELDED = "welded"


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
class Feature:
    id: str
    kind: FeatureKind
    placement: str
    position: Point3D
    size: Dimension3D | None = None
    radius_mm: float | None = None
    comment: str = ""
    status: str = "abstract_only"
    fusion_generation: str = "not_implemented"
    taxonomy: FeatureTaxonomyKind | None = None


@dataclass(frozen=True)
class AssetQuantity:
    count: int
    grouping: str = "single"


@dataclass(frozen=True)
class Asset:
    id: str
    name: str
    kind: AssetKind
    quantity: AssetQuantity
    dimensions: Dimension3D
    dimension_confidence: DimensionConfidence
    containment_intent: ContainmentIntent
    reservation_ref: str | None = None
    module_hint: str | None = None
    storage_orientation: AssetStorageOrientation = AssetStorageOrientation.AUTO
    max_stack_height_mm: float | None = None
    comment: str = ""


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
    strategy: str = LAYOUT_STRATEGY_ROW_FILL
    allow_global_rotation: bool = False


@dataclass(frozen=True)
class GridPoint3D:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class GridSize3D:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class VolumetricLayer:
    id: str
    name: str
    z_start: int
    z_count: int
    role: str
    comment: str = ""


@dataclass(frozen=True)
class VolumetricModulePlacement:
    id: str
    module_id: str
    origin_units: GridPoint3D
    size_units: GridSize3D
    instance_id: str | None = None
    layer_id: str | None = None
    removal_order: int | None = None
    access_direction: str = "unspecified"
    support_surface_id: str | None = None
    comment: str = ""


@dataclass(frozen=True)
class VolumetricZone:
    id: str
    kind: VolumetricZoneKind
    purpose: str
    origin_units: GridPoint3D
    size_units: GridSize3D
    layer_id: str | None = None
    reservation_kind: str = "generic"
    asset_kind: str = "unspecified"
    removal_order: int | None = None
    access_direction: str = "unspecified"
    support_surface_id: str | None = None
    comment: str = ""


@dataclass(frozen=True)
class VolumetricSupportSurface:
    id: str
    owner_type: VolumetricOwnerType
    owner_id: str
    face: VolumetricFace
    origin_units: GridPoint3D
    size_units: GridSize3D
    layer_id: str | None = None
    purpose: str = "abstract_support"
    comment: str = ""


@dataclass(frozen=True)
class VolumetricGrid:
    unit_size_mm: Dimension3D
    size_units: GridSize3D
    layers: tuple[VolumetricLayer, ...] = ()
    module_placements: tuple[VolumetricModulePlacement, ...] = ()
    zones: tuple[VolumetricZone, ...] = ()
    support_surfaces: tuple[VolumetricSupportSurface, ...] = ()
    comment: str = ""

@dataclass(frozen=True)
class Cavity:
    id: str
    functional_type: FunctionalType
    origin: Point3D
    size: Dimension3D
    clearance_mm: float
    clearance_source: str = "explicit"
    comment: str = ""
    features: tuple[Feature, ...] = ()


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
    cavities: tuple[Cavity, ...] = ()


@dataclass(frozen=True)
class InsertConfig:
    project_name: str
    units: str
    box: BoxSpec
    tolerances: ToleranceProfile
    defaults: GeometryDefaults
    layout: LayoutSettings
    modules: tuple[ModuleRequest, ...]
    assets: tuple[Asset, ...] = ()
    print_profile: str = "default"
    source_path: str | None = None
    volumetric_grid: VolumetricGrid | None = None


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
class FaceOffsets:
    x_min: float = 0.0
    x_max: float = 0.0
    y_min: float = 0.0
    y_max: float = 0.0
    z_min: float = 0.0
    z_max: float = 0.0


@dataclass(frozen=True)
class FaceClassification:
    face: FaceName
    role: FaceRole
    reason: str
    neighbor_instance_id: str | None = None


@dataclass(frozen=True)
class FaceToleranceApplication:
    face: FaceName
    role: FaceRole
    offset_mm: float
    rule_id: str
    clearance_source: str
    receives_clearance: bool
    reason: str


@dataclass(frozen=True)
class PrintableBody:
    module_id: str
    instance_id: str
    body_id: str
    origin: Point3D
    size: Dimension3D
    offsets: FaceOffsets
    primitive_volumes: tuple[PrimitiveVolume, ...]
    face_classifications: tuple[FaceClassification, ...] = ()
    tolerance_applications: tuple[FaceToleranceApplication, ...] = ()


@dataclass(frozen=True)
class LayoutResult:
    cells: tuple[Cell, ...]
    printable_bodies: tuple[PrintableBody, ...]
    warnings: tuple[str, ...] = ()
