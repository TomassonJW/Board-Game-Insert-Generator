"""Material-aware support certificate for rectangular BGIG bodies.

The certificate deliberately reasons on load-bearing material at the upper
plane of a body.  A container contributes its rectangular rim (outer face
minus every cavity that reaches the top); an explicit solid body contributes a
full face.  ``has_lid`` is intentionally ignored until a separate closure
certificate exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


SUPPORTED_ON_MATERIAL = "supported_on_material"
BRIDGED_ON_MATERIAL = "bridged_on_material"
FALLS_THROUGH_OPENING = "falls_through_opening"
INSUFFICIENT_MATERIAL_SUPPORT = "insufficient_material_support"
UNSTABLE_SUPPORT_POLYGON = "unstable_support_polygon"
SUPPORTED_ON_ENVELOPE = "supported_on_envelope"
BRIDGED_ON_ENVELOPES = "bridged_on_envelopes"
INSUFFICIENT_ENVELOPE_SUPPORT = "insufficient_envelope_support"

MIN_SUPPORT_RATIO = 0.25
_EPSILON = 0.0001
_AXES = ("x", "y", "z")
_Rect = tuple[float, float, float, float]


@dataclass(frozen=True)
class MaterialSupportEvaluation:
    """One deterministic support decision for an upper body."""

    status: str
    supporting_ids: tuple[str, ...]
    coverage_ratio: float
    material_contact_area_mm2: float
    stable_support_polygon: bool
    falls_through_opening: bool

    @property
    def certified(self) -> bool:
        return self.status in {
            SUPPORTED_ON_MATERIAL,
            BRIDGED_ON_MATERIAL,
            SUPPORTED_ON_ENVELOPE,
            BRIDGED_ON_ENVELOPES,
        }


@dataclass(frozen=True)
class _Surface:
    placement_id: str
    outer: _Rect
    openings: tuple[_Rect, ...]


def evaluate_search_support(
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
    placements: Sequence[object],
    participant: Mapping[str, object],
    participants_by_id: Mapping[str, Mapping[str, object]],
    fallback_xy_clearance: float,
    fallback_z_clearance: float,
) -> MaterialSupportEvaluation:
    """Evaluate one search option from immutable placements and participants."""

    if origin[2] <= _EPSILON:
        return _floor_evaluation()
    surfaces: list[_Surface] = []
    for lower in placements:
        lower_id = str(getattr(lower, "participant_id"))
        lower_participant = participants_by_id.get(lower_id)
        if lower_participant is None:
            continue
        clearance = max(
            _participant_clearance(participant, "z", fallback_z_clearance),
            _participant_clearance(lower_participant, "z", fallback_z_clearance),
        )
        lower_origin = tuple(float(value) for value in getattr(lower, "origin_mm"))
        lower_world = tuple(float(value) for value in getattr(lower, "world_size_mm"))
        lower_top = lower_origin[2] + lower_world[2]
        if abs(origin[2] - (lower_top + clearance)) > 0.001:
            continue
        surfaces.append(_search_surface(lower, lower_participant))
    xy_clearance = max(
        _participant_clearance(participant, "x", fallback_xy_clearance),
        _participant_clearance(participant, "y", fallback_xy_clearance),
    )
    return _evaluate(
        (origin[0], origin[1], origin[0] + size[0], origin[1] + size[1]),
        tuple(surfaces),
        xy_clearance,
    )


def evaluate_envelope_search_support(
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
    placements: Sequence[object],
    participant: Mapping[str, object],
    participants_by_id: Mapping[str, Mapping[str, object]],
    fallback_xy_clearance: float,
    fallback_z_clearance: float,
) -> MaterialSupportEvaluation:
    """Evaluate hard support on lower bodies' complete outer XY envelopes."""

    if origin[2] <= _EPSILON:
        return _as_envelope_evaluation(_floor_evaluation())
    surfaces: list[_Surface] = []
    for lower in placements:
        lower_id = str(getattr(lower, "participant_id"))
        lower_participant = participants_by_id.get(lower_id)
        if lower_participant is None:
            continue
        clearance = max(
            _participant_clearance(participant, "z", fallback_z_clearance),
            _participant_clearance(lower_participant, "z", fallback_z_clearance),
        )
        lower_origin = tuple(float(value) for value in getattr(lower, "origin_mm"))
        lower_world = tuple(float(value) for value in getattr(lower, "world_size_mm"))
        lower_top = lower_origin[2] + lower_world[2]
        if abs(origin[2] - (lower_top + clearance)) > 0.001:
            continue
        surface = _search_surface(lower, lower_participant)
        surfaces.append(
            _Surface(
                placement_id=surface.placement_id,
                outer=surface.outer,
                openings=(),
            )
        )
    xy_clearance = max(
        _participant_clearance(participant, "x", fallback_xy_clearance),
        _participant_clearance(participant, "y", fallback_xy_clearance),
    )
    return _as_envelope_evaluation(
        _evaluate(
            (origin[0], origin[1], origin[0] + size[0], origin[1] + size[1]),
            tuple(surfaces),
            xy_clearance,
        )
    )


def envelope_support_contract(
    placements: Sequence[Mapping[str, object]],
    *,
    fallback_xy_clearance: float,
    fallback_z_clearance: float,
) -> dict[str, object]:
    """Build the hard plan-level support contract from complete XY envelopes."""

    supports: list[dict[str, object]] = []
    minimum_ratio = 1.0
    for placement in placements:
        placement_id = str(placement.get("id") or placement.get("placement_id"))
        origin = _vector(placement.get("origin_mm"))
        size = _vector(placement.get("world_size_mm"))
        if origin[2] <= _EPSILON:
            evaluation = _as_envelope_evaluation(_floor_evaluation())
            vertical_gap = 0.0
        else:
            surfaces: list[_Surface] = []
            gaps: list[float] = []
            for lower in placements:
                lower_id = str(lower.get("id") or lower.get("placement_id"))
                if lower_id == placement_id:
                    continue
                lower_origin = _vector(lower.get("origin_mm"))
                lower_size = _vector(lower.get("world_size_mm"))
                required_gap = max(
                    _plan_clearance(placement, "z", fallback_z_clearance),
                    _plan_clearance(lower, "z", fallback_z_clearance),
                )
                actual_gap = origin[2] - (lower_origin[2] + lower_size[2])
                if abs(actual_gap - required_gap) > 0.001:
                    continue
                surface = _plan_surface(lower)
                surfaces.append(
                    _Surface(
                        placement_id=surface.placement_id,
                        outer=surface.outer,
                        openings=(),
                    )
                )
                gaps.append(actual_gap)
            xy_clearance = max(
                _plan_clearance(placement, "x", fallback_xy_clearance),
                _plan_clearance(placement, "y", fallback_xy_clearance),
            )
            evaluation = _as_envelope_evaluation(
                _evaluate(
                    (origin[0], origin[1], origin[0] + size[0], origin[1] + size[1]),
                    tuple(surfaces),
                    xy_clearance,
                )
            )
            vertical_gap = min(gaps) if gaps else 0.0
        minimum_ratio = min(minimum_ratio, evaluation.coverage_ratio)
        supports.append(
            {
                "placement_id": placement_id,
                "stage_id": str(placement.get("stage_id", "")),
                "supporting_ids": list(evaluation.supporting_ids),
                "coverage_ratio": _round(evaluation.coverage_ratio),
                "envelope_contact_area_mm2": _round(
                    evaluation.material_contact_area_mm2
                ),
                "status": evaluation.status,
                "supported": evaluation.certified,
                "stable_support_polygon": evaluation.stable_support_polygon,
                "vertical_gap_mm": _round(vertical_gap),
            }
        )
    rejected = [value for value in supports if not bool(value["supported"])]
    return {
        "status": "unsupported" if rejected else "supported",
        "certificate_kind": "outer_envelope_v1",
        "minimum_coverage_ratio": _round(minimum_ratio),
        "minimum_required_ratio": MIN_SUPPORT_RATIO,
        "vertical_gap_mm": _round(fallback_z_clearance),
        "supports": supports,
        "unsupported_body_ids": [str(value["placement_id"]) for value in rejected],
        "rejection_statuses": sorted({str(value["status"]) for value in rejected}),
        "invariants": {
            "outer_envelope_is_hard_support": True,
            "openings_are_diagnostic_only": True,
            "support_polygon_contains_center_of_mass_projection": True,
        },
    }

def material_support_contract(
    placements: Sequence[Mapping[str, object]],
    *,
    fallback_xy_clearance: float,
    fallback_z_clearance: float,
) -> dict[str, object]:
    """Build the common plan-level support contract from material surfaces."""

    supports: list[dict[str, object]] = []
    minimum_ratio = 1.0
    for placement in placements:
        placement_id = str(placement.get("id") or placement.get("placement_id"))
        origin = _vector(placement.get("origin_mm"))
        size = _vector(placement.get("world_size_mm"))
        if origin[2] <= _EPSILON:
            evaluation = _floor_evaluation()
            vertical_gap = 0.0
        else:
            surfaces: list[_Surface] = []
            gaps: list[float] = []
            for lower in placements:
                lower_id = str(lower.get("id") or lower.get("placement_id"))
                if lower_id == placement_id:
                    continue
                lower_origin = _vector(lower.get("origin_mm"))
                lower_size = _vector(lower.get("world_size_mm"))
                required_gap = max(
                    _plan_clearance(placement, "z", fallback_z_clearance),
                    _plan_clearance(lower, "z", fallback_z_clearance),
                )
                actual_gap = origin[2] - (lower_origin[2] + lower_size[2])
                if abs(actual_gap - required_gap) > 0.001:
                    continue
                surfaces.append(_plan_surface(lower))
                gaps.append(actual_gap)
            xy_clearance = max(
                _plan_clearance(placement, "x", fallback_xy_clearance),
                _plan_clearance(placement, "y", fallback_xy_clearance),
            )
            evaluation = _evaluate(
                (origin[0], origin[1], origin[0] + size[0], origin[1] + size[1]),
                tuple(surfaces),
                xy_clearance,
            )
            vertical_gap = min(gaps) if gaps else 0.0
        minimum_ratio = min(minimum_ratio, evaluation.coverage_ratio)
        supports.append(
            {
                "placement_id": placement_id,
                "stage_id": str(placement.get("stage_id", "")),
                "supporting_ids": list(evaluation.supporting_ids),
                "coverage_ratio": _round(evaluation.coverage_ratio),
                "material_contact_area_mm2": _round(evaluation.material_contact_area_mm2),
                "status": evaluation.status,
                "supported": evaluation.certified,
                "stable_support_polygon": evaluation.stable_support_polygon,
                "falls_through_opening": evaluation.falls_through_opening,
                "vertical_gap_mm": _round(vertical_gap),
            }
        )
    rejected = [value for value in supports if not bool(value["supported"])]
    return {
        "status": "unsupported" if rejected else "supported",
        "certificate_kind": "material_surface_v1",
        "minimum_coverage_ratio": _round(minimum_ratio),
        "minimum_required_ratio": MIN_SUPPORT_RATIO,
        "vertical_gap_mm": _round(fallback_z_clearance),
        "supports": supports,
        "unsupported_body_ids": [str(value["placement_id"]) for value in rejected],
        "rejection_statuses": sorted({str(value["status"]) for value in rejected}),
        "invariants": {
            "open_container_uses_rims_only": True,
            "solid_body_uses_full_face": True,
            "uncertified_lid_ignored": True,
            "support_polygon_contains_center_of_mass_projection": True,
        },
    }


def _floor_evaluation() -> MaterialSupportEvaluation:
    return MaterialSupportEvaluation(
        status=SUPPORTED_ON_MATERIAL,
        supporting_ids=("box-floor",),
        coverage_ratio=1.0,
        material_contact_area_mm2=0.0,
        stable_support_polygon=True,
        falls_through_opening=False,
    )


def _as_envelope_evaluation(
    evaluation: MaterialSupportEvaluation,
) -> MaterialSupportEvaluation:
    status = {
        SUPPORTED_ON_MATERIAL: SUPPORTED_ON_ENVELOPE,
        BRIDGED_ON_MATERIAL: BRIDGED_ON_ENVELOPES,
        INSUFFICIENT_MATERIAL_SUPPORT: INSUFFICIENT_ENVELOPE_SUPPORT,
    }.get(evaluation.status, evaluation.status)
    return MaterialSupportEvaluation(
        status=status,
        supporting_ids=evaluation.supporting_ids,
        coverage_ratio=evaluation.coverage_ratio,
        material_contact_area_mm2=evaluation.material_contact_area_mm2,
        stable_support_polygon=evaluation.stable_support_polygon,
        falls_through_opening=False,
    )

def _evaluate(
    upper: _Rect,
    surfaces: tuple[_Surface, ...],
    xy_clearance: float,
) -> MaterialSupportEvaluation:
    footprint = max(0.0, upper[2] - upper[0]) * max(0.0, upper[3] - upper[1])
    if footprint <= _EPSILON:
        return MaterialSupportEvaluation(
            status=SUPPORTED_ON_MATERIAL,
            supporting_ids=(),
            coverage_ratio=1.0,
            material_contact_area_mm2=0.0,
            stable_support_polygon=True,
            falls_through_opening=False,
        )
    clipped_surfaces = tuple(
        surface for surface in surfaces if _rectangles_overlap(upper, surface.outer)
    )
    xs = {upper[0], upper[2]}
    ys = {upper[1], upper[3]}
    for surface in clipped_surfaces:
        for rectangle in (surface.outer, *surface.openings):
            clipped = _intersection(upper, rectangle)
            if clipped is None:
                continue
            xs.update((clipped[0], clipped[2]))
            ys.update((clipped[1], clipped[3]))
    contact_cells: list[_Rect] = []
    supporting_ids: set[str] = set()
    ordered_x = sorted(xs)
    ordered_y = sorted(ys)
    for x0, x1 in zip(ordered_x, ordered_x[1:]):
        if x1 <= x0 + _EPSILON:
            continue
        for y0, y1 in zip(ordered_y, ordered_y[1:]):
            if y1 <= y0 + _EPSILON:
                continue
            point = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
            cell_supporters = {
                surface.placement_id
                for surface in clipped_surfaces
                if _point_in_rect(point, surface.outer)
                and not any(_point_in_rect(point, opening) for opening in surface.openings)
            }
            if cell_supporters:
                contact_cells.append((x0, y0, x1, y1))
                supporting_ids.update(cell_supporters)
    area = sum(
        (rectangle[2] - rectangle[0]) * (rectangle[3] - rectangle[1]) for rectangle in contact_cells
    )
    ratio = min(1.0, area / footprint)
    fall_through = area <= _EPSILON and _opening_union_contains(
        upper,
        tuple(opening for surface in clipped_surfaces for opening in surface.openings),
        xy_clearance,
    )
    center = ((upper[0] + upper[2]) / 2.0, (upper[1] + upper[3]) / 2.0)
    hull = _convex_hull(
        [
            point
            for rectangle in contact_cells
            for point in (
                (rectangle[0], rectangle[1]),
                (rectangle[0], rectangle[3]),
                (rectangle[2], rectangle[1]),
                (rectangle[2], rectangle[3]),
            )
        ]
    )
    stable = _point_in_convex_polygon(center, hull)
    if fall_through:
        status = FALLS_THROUGH_OPENING
    elif ratio + _EPSILON < MIN_SUPPORT_RATIO:
        status = INSUFFICIENT_MATERIAL_SUPPORT
    elif not stable:
        status = UNSTABLE_SUPPORT_POLYGON
    elif ratio < 1.0 - _EPSILON or len(supporting_ids) > 1:
        status = BRIDGED_ON_MATERIAL
    else:
        status = SUPPORTED_ON_MATERIAL
    return MaterialSupportEvaluation(
        status=status,
        supporting_ids=tuple(sorted(supporting_ids)),
        coverage_ratio=_round(ratio),
        material_contact_area_mm2=_round(area),
        stable_support_polygon=stable,
        falls_through_opening=fall_through,
    )


def _search_surface(
    placement: object,
    participant: Mapping[str, object],
) -> _Surface:
    placement_id = str(getattr(placement, "participant_id"))
    origin = tuple(float(value) for value in getattr(placement, "origin_mm"))
    world_size = tuple(float(value) for value in getattr(placement, "world_size_mm"))
    local_size = tuple(float(value) for value in getattr(placement, "local_size_mm"))
    rotation = int(getattr(placement, "rotation_deg_z"))
    cavities, minimum = _participant_cavities(
        participant,
        str(getattr(placement, "container_variant_id", "")),
    )
    offsets = tuple(max(0.0, local_size[index] - minimum[index]) / 2.0 for index in range(3))
    openings: list[_Rect] = []
    for cavity in cavities:
        cavity_origin = _vector(cavity.get("local_origin_mm"))
        cavity_size = _vector(cavity.get("inner_dimensions_mm"))
        local_origin = tuple(offsets[index] + cavity_origin[index] for index in range(3))
        if local_origin[2] + cavity_size[2] < local_size[2] - _EPSILON:
            continue
        openings.append(
            _local_rect_to_world(
                origin,
                local_size,
                rotation,
                local_origin[0],
                local_origin[1],
                cavity_size[0],
                cavity_size[1],
            )
        )
    return _Surface(
        placement_id=placement_id,
        outer=(
            origin[0],
            origin[1],
            origin[0] + world_size[0],
            origin[1] + world_size[1],
        ),
        openings=tuple(openings),
    )


def _plan_surface(placement: Mapping[str, object]) -> _Surface:
    placement_id = str(placement.get("id") or placement.get("placement_id"))
    origin = _vector(placement.get("origin_mm"))
    world_size = _vector(placement.get("world_size_mm"))
    final_local = _vector(
        placement.get("final_outer_dimensions_mm") or placement.get("world_size_mm")
    )
    minimum_offset = _vector(placement.get("minimum_envelope_origin_in_final_mm"))
    rotation = int(placement.get("rotation_deg_z", 0))
    openings: list[_Rect] = []
    cavities = placement.get("cavity_layout")
    if isinstance(cavities, list):
        for cavity in cavities:
            if not isinstance(cavity, Mapping):
                continue
            cavity_origin = _vector(cavity.get("local_origin_mm"))
            cavity_size = _vector(cavity.get("inner_dimensions_mm"))
            local_origin = tuple(minimum_offset[index] + cavity_origin[index] for index in range(3))
            if local_origin[2] + cavity_size[2] < final_local[2] - _EPSILON:
                continue
            openings.append(
                _local_rect_to_world(
                    origin,
                    final_local,
                    rotation,
                    local_origin[0],
                    local_origin[1],
                    cavity_size[0],
                    cavity_size[1],
                )
            )
    return _Surface(
        placement_id=placement_id,
        outer=(
            origin[0],
            origin[1],
            origin[0] + world_size[0],
            origin[1] + world_size[1],
        ),
        openings=tuple(openings),
    )


def _participant_cavities(
    participant: Mapping[str, object],
    selected_variant_id: str,
) -> tuple[list[Mapping[str, object]], tuple[float, float, float]]:
    selected = participant.get("selected_container_variant_v1")
    option: Mapping[str, object] | None = selected if isinstance(selected, Mapping) else None
    options = participant.get("container_internal_variant_options_v1")
    if option is None and selected_variant_id and isinstance(options, list):
        option = next(
            (
                value
                for value in options
                if isinstance(value, Mapping)
                and str(value.get("variant_id")) == selected_variant_id
            ),
            None,
        )
    minimum_source = (
        option.get("minimum_outer_envelope_mm")
        if option is not None
        else participant.get("minimum_local_mm")
    )
    minimum = _vector(minimum_source)
    cavity_values = option.get("cavities") if option is not None else None
    if not isinstance(cavity_values, list):
        hint = participant.get("top_inset_search_hint_v1")
        cavity_values = hint.get("cavities") if isinstance(hint, Mapping) else []
    return (
        [value for value in cavity_values if isinstance(value, Mapping)],
        minimum,
    )


def _local_rect_to_world(
    body_origin: tuple[float, float, float],
    final_local_size: tuple[float, float, float],
    rotation_deg_z: int,
    local_x: float,
    local_y: float,
    size_x: float,
    size_y: float,
) -> _Rect:
    if rotation_deg_z == 90:
        x0 = body_origin[0] + final_local_size[1] - local_y - size_y
        y0 = body_origin[1] + local_x
        return (x0, y0, x0 + size_y, y0 + size_x)
    x0 = body_origin[0] + local_x
    y0 = body_origin[1] + local_y
    return (x0, y0, x0 + size_x, y0 + size_y)


def _participant_clearance(
    participant: Mapping[str, object],
    axis: str,
    fallback: float,
) -> float:
    policy = participant.get("external_clearance_effective_v1")
    between = policy.get("between_mm") if isinstance(policy, Mapping) else None
    value = between.get(axis) if isinstance(between, Mapping) else None
    return (
        float(value)
        if isinstance(value, (int, float)) and not isinstance(value, bool)
        else fallback
    )


def _plan_clearance(
    placement: Mapping[str, object],
    axis: str,
    fallback: float,
) -> float:
    policy = placement.get("external_clearance_effective_v1")
    between = policy.get("between_mm") if isinstance(policy, Mapping) else None
    local_axis = axis
    if axis in {"x", "y"} and int(placement.get("rotation_deg_z", 0)) == 90:
        local_axis = "y" if axis == "x" else "x"
    value = between.get(local_axis) if isinstance(between, Mapping) else None
    return (
        float(value)
        if isinstance(value, (int, float)) and not isinstance(value, bool)
        else fallback
    )


def _vector(value: object) -> tuple[float, float, float]:
    if not isinstance(value, Mapping):
        return (0.0, 0.0, 0.0)
    return tuple(float(value.get(axis, 0.0)) for axis in _AXES)  # type: ignore[return-value]


def _intersection(left: _Rect, right: _Rect) -> _Rect | None:
    result = (
        max(left[0], right[0]),
        max(left[1], right[1]),
        min(left[2], right[2]),
        min(left[3], right[3]),
    )
    return result if result[2] > result[0] + _EPSILON and result[3] > result[1] + _EPSILON else None


def _rectangles_overlap(left: _Rect, right: _Rect) -> bool:
    return _intersection(left, right) is not None


def _point_in_rect(point: tuple[float, float], rectangle: _Rect) -> bool:
    return (
        rectangle[0] - _EPSILON <= point[0] <= rectangle[2] + _EPSILON
        and rectangle[1] - _EPSILON <= point[1] <= rectangle[3] + _EPSILON
    )


def _opening_union_contains(
    inner: _Rect,
    openings: tuple[_Rect, ...],
    clearance: float,
) -> bool:
    usable = tuple(
        (
            opening[0] + clearance,
            opening[1] + clearance,
            opening[2] - clearance,
            opening[3] - clearance,
        )
        for opening in openings
        if opening[2] - opening[0] > 2.0 * clearance + _EPSILON
        and opening[3] - opening[1] > 2.0 * clearance + _EPSILON
    )
    if not usable:
        return False
    xs = sorted(
        {inner[0], inner[2]}
        | {
            boundary
            for opening in usable
            for boundary in (
                max(inner[0], opening[0]),
                min(inner[2], opening[2]),
            )
            if inner[0] <= boundary <= inner[2]
        }
    )
    ys = sorted(
        {inner[1], inner[3]}
        | {
            boundary
            for opening in usable
            for boundary in (
                max(inner[1], opening[1]),
                min(inner[3], opening[3]),
            )
            if inner[1] <= boundary <= inner[3]
        }
    )
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            if x1 <= x0 + _EPSILON or y1 <= y0 + _EPSILON:
                continue
            point = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
            if not any(_point_in_rect(point, opening) for opening in usable):
                return False
    return True


def _convex_hull(
    points: list[tuple[float, float]],
) -> tuple[tuple[float, float], ...]:
    values = sorted(set(points))
    if len(values) <= 1:
        return tuple(values)

    def cross(
        origin: tuple[float, float],
        left: tuple[float, float],
        right: tuple[float, float],
    ) -> float:
        return (left[0] - origin[0]) * (right[1] - origin[1]) - (left[1] - origin[1]) * (
            right[0] - origin[0]
        )

    lower: list[tuple[float, float]] = []
    for point in values:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= _EPSILON:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(values):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= _EPSILON:
            upper.pop()
        upper.append(point)
    return tuple(lower[:-1] + upper[:-1])


def _point_in_convex_polygon(
    point: tuple[float, float],
    polygon: tuple[tuple[float, float], ...],
) -> bool:
    if len(polygon) < 3:
        return False
    sign = 0
    for left, right in zip(polygon, polygon[1:] + polygon[:1]):
        cross = (right[0] - left[0]) * (point[1] - left[1]) - (right[1] - left[1]) * (
            point[0] - left[0]
        )
        if abs(cross) <= _EPSILON:
            continue
        current = 1 if cross > 0.0 else -1
        if sign and current != sign:
            return False
        sign = current
    return True


def _round(value: float) -> float:
    return round(float(value), 6)
