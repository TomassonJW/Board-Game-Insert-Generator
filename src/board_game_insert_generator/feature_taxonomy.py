"""Taxonomy for cavity ergonomic access features.

The taxonomy is CAD-agnostic. It clarifies what a feature means before any
adapter decides whether a real CAD operation is available. Fusion 360 generation
must consume resolved CAD IR metadata and must not reinterpret this taxonomy as
new geometry permission.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from board_game_insert_generator.models import Feature, FeatureKind, FeatureTaxonomyKind


FEATURE_PROFILE_RECTANGLE = "rectangle"
FEATURE_PROFILE_HALF_MOON = "half_moon"
FEATURE_PROFILE_ROUNDED_RECT = "rounded_rect"
FEATURE_PROFILE_SCOOP = "scoop"
FEATURE_PROFILE_FLOOR_RADIUS = "floor_radius"

FUSION_STATUS_VALIDATED = "fusion-validated"
FUSION_STATUS_ABSTRACT_ONLY = "abstract_only"
FUSION_STATUS_RECTANGULAR_FALLBACK = "abstract_profile_with_validated_rectangular_fallback"


@dataclass(frozen=True)
class FeatureTaxonomySpec:
    taxonomy: FeatureTaxonomyKind
    label: str
    profile: str
    opens_to_top: bool
    through_wall: bool
    requires_size: bool
    requires_radius: bool
    requires_outer_skin: bool
    fusion_status: str
    print_validated: bool
    description: str
    fusion_fallback_taxonomy: FeatureTaxonomyKind | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "taxonomy": self.taxonomy.value,
            "label": self.label,
            "profile": self.profile,
            "opens_to_top": self.opens_to_top,
            "through_wall": self.through_wall,
            "requires_size": self.requires_size,
            "requires_radius": self.requires_radius,
            "requires_outer_skin": self.requires_outer_skin,
            "fusion_status": self.fusion_status,
            "print_validated": self.print_validated,
            "fusion_fallback_taxonomy": (
                self.fusion_fallback_taxonomy.value
                if self.fusion_fallback_taxonomy is not None
                else None
            ),
            "description": self.description,
        }


FEATURE_TAXONOMY_SPECS: dict[FeatureTaxonomyKind, FeatureTaxonomySpec] = {
    FeatureTaxonomyKind.TOP_OPEN_RECTANGULAR_NOTCH: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.TOP_OPEN_RECTANGULAR_NOTCH,
        label="Top-open rectangular notch",
        profile=FEATURE_PROFILE_RECTANGLE,
        opens_to_top=True,
        through_wall=True,
        requires_size=True,
        requires_radius=False,
        requires_outer_skin=False,
        fusion_status=FUSION_STATUS_VALIDATED,
        print_validated=False,
        description="Rectangular bite cut from the top rim of a target wall.",
    ),
    FeatureTaxonomyKind.TOP_OPEN_HALF_MOON_NOTCH: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.TOP_OPEN_HALF_MOON_NOTCH,
        label="Top-open half-moon notch",
        profile=FEATURE_PROFILE_HALF_MOON,
        opens_to_top=True,
        through_wall=True,
        requires_size=True,
        requires_radius=True,
        requires_outer_skin=False,
        fusion_status=FUSION_STATUS_RECTANGULAR_FALLBACK,
        print_validated=False,
        fusion_fallback_taxonomy=FeatureTaxonomyKind.TOP_OPEN_RECTANGULAR_NOTCH,
        description="Future curved half-moon notch; current Fusion fallback is rectangular.",
    ),
    FeatureTaxonomyKind.THROUGH_WALL_WINDOW: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.THROUGH_WALL_WINDOW,
        label="Through-wall window",
        profile=FEATURE_PROFILE_RECTANGLE,
        opens_to_top=False,
        through_wall=True,
        requires_size=True,
        requires_radius=False,
        requires_outer_skin=False,
        fusion_status=FUSION_STATUS_ABSTRACT_ONLY,
        print_validated=False,
        description="Closed wall opening, explicitly distinct from a top-open notch.",
    ),
    FeatureTaxonomyKind.BLIND_INTERNAL_THUMB_SCOOP: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.BLIND_INTERNAL_THUMB_SCOOP,
        label="Blind internal thumb scoop",
        profile=FEATURE_PROFILE_SCOOP,
        opens_to_top=False,
        through_wall=False,
        requires_size=True,
        requires_radius=True,
        requires_outer_skin=True,
        fusion_status=FUSION_STATUS_ABSTRACT_ONLY,
        print_validated=False,
        description="Internal non-through scoop that preserves an outside skin.",
    ),
    FeatureTaxonomyKind.SIDE_RELIEF_NOTCH: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.SIDE_RELIEF_NOTCH,
        label="Side relief notch",
        profile=FEATURE_PROFILE_RECTANGLE,
        opens_to_top=True,
        through_wall=True,
        requires_size=True,
        requires_radius=False,
        requires_outer_skin=False,
        fusion_status=FUSION_STATUS_ABSTRACT_ONLY,
        print_validated=False,
        description="Side relief for flat assets such as cards or tiles.",
    ),
    FeatureTaxonomyKind.DUAL_SIDE_CARD_ACCESS: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.DUAL_SIDE_CARD_ACCESS,
        label="Dual-side card access",
        profile=FEATURE_PROFILE_RECTANGLE,
        opens_to_top=True,
        through_wall=True,
        requires_size=True,
        requires_radius=False,
        requires_outer_skin=False,
        fusion_status=FUSION_STATUS_ABSTRACT_ONLY,
        print_validated=False,
        description="Paired side access for lifting a stack of cards or flat assets.",
    ),
    FeatureTaxonomyKind.ROUNDED_FLOOR_INTENT: FeatureTaxonomySpec(
        taxonomy=FeatureTaxonomyKind.ROUNDED_FLOOR_INTENT,
        label="Rounded floor intent",
        profile=FEATURE_PROFILE_FLOOR_RADIUS,
        opens_to_top=False,
        through_wall=False,
        requires_size=False,
        requires_radius=True,
        requires_outer_skin=False,
        fusion_status=FUSION_STATUS_ABSTRACT_ONLY,
        print_validated=False,
        description="Abstract floor radius intent; no Fusion fillet or curved floor yet.",
    ),
}

DEFAULT_TAXONOMY_BY_FEATURE_KIND: dict[FeatureKind, FeatureTaxonomyKind] = {
    FeatureKind.FINGER_NOTCH: FeatureTaxonomyKind.TOP_OPEN_RECTANGULAR_NOTCH,
    FeatureKind.SIDE_NOTCH: FeatureTaxonomyKind.SIDE_RELIEF_NOTCH,
    FeatureKind.CENTER_NOTCH: FeatureTaxonomyKind.BLIND_INTERNAL_THUMB_SCOOP,
    FeatureKind.HALF_MOON_NOTCH: FeatureTaxonomyKind.TOP_OPEN_HALF_MOON_NOTCH,
    FeatureKind.ROUNDED_FLOOR: FeatureTaxonomyKind.ROUNDED_FLOOR_INTENT,
    FeatureKind.GRIP_AID: FeatureTaxonomyKind.DUAL_SIDE_CARD_ACCESS,
}

COMPATIBLE_FEATURE_KINDS_BY_TAXONOMY: dict[FeatureTaxonomyKind, tuple[FeatureKind, ...]] = {
    FeatureTaxonomyKind.TOP_OPEN_RECTANGULAR_NOTCH: (
        FeatureKind.FINGER_NOTCH,
        FeatureKind.SIDE_NOTCH,
        FeatureKind.CENTER_NOTCH,
    ),
    FeatureTaxonomyKind.TOP_OPEN_HALF_MOON_NOTCH: (FeatureKind.HALF_MOON_NOTCH,),
    FeatureTaxonomyKind.THROUGH_WALL_WINDOW: (
        FeatureKind.FINGER_NOTCH,
        FeatureKind.SIDE_NOTCH,
        FeatureKind.CENTER_NOTCH,
        FeatureKind.GRIP_AID,
    ),
    FeatureTaxonomyKind.BLIND_INTERNAL_THUMB_SCOOP: (
        FeatureKind.CENTER_NOTCH,
        FeatureKind.GRIP_AID,
    ),
    FeatureTaxonomyKind.SIDE_RELIEF_NOTCH: (FeatureKind.SIDE_NOTCH,),
    FeatureTaxonomyKind.DUAL_SIDE_CARD_ACCESS: (
        FeatureKind.GRIP_AID,
        FeatureKind.SIDE_NOTCH,
        FeatureKind.CENTER_NOTCH,
    ),
    FeatureTaxonomyKind.ROUNDED_FLOOR_INTENT: (FeatureKind.ROUNDED_FLOOR,),
}


def resolve_feature_taxonomy(feature: Feature) -> FeatureTaxonomySpec:
    taxonomy = feature.taxonomy or DEFAULT_TAXONOMY_BY_FEATURE_KIND[feature.kind]
    return FEATURE_TAXONOMY_SPECS[taxonomy]


def is_feature_taxonomy_compatible(kind: FeatureKind, taxonomy: FeatureTaxonomyKind) -> bool:
    return kind in COMPATIBLE_FEATURE_KINDS_BY_TAXONOMY[taxonomy]


def feature_taxonomy_to_dict(feature: Feature) -> dict[str, Any]:
    return resolve_feature_taxonomy(feature).to_dict()
