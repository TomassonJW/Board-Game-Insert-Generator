"""Bounded XY-composite fallback for top-reservation finishing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
    TopInsetZone,
)
from board_game_insert_generator.global_rectangular_closure import (
    GlobalRectangularClosureResult,
    close_global_rectangular_partition,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_contract import SolverBudget


XY_COMPOSITE_CLOSURE_VERSION = "bgig.xy_composite_closure.v1"
XY_COMPOSITE_CERTIFICATE_SCHEMA_V1 = (
    "bgig.xy_composite_partition_certificate.v1"
)
_EPSILON = 0.0001


@dataclass(frozen=True)
class CompositePrism:
    prism_id: str
    owner_id: str
    kind: str
    origin_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]
    attached_to_prism_id: str
    attachment_axis: str


@dataclass(frozen=True)
class CompositeOwnerBody:
    owner_id: str
    source_placement: Free3DPlacement
    base_z_mm: float
    core_prism_id: str
    prisms: tuple[CompositePrism, ...]
    certificate: dict[str, object]


@dataclass(frozen=True)
class XYCompositeClosureResult:
    status: str
    owner_bodies: tuple[CompositeOwnerBody, ...]
    gross_closure: GlobalRectangularClosureResult
    certificate: dict[str, object]
    deterministic_digest: str
    stop_reason: str


@dataclass(frozen=True)
class _RawPrism:
    origin: tuple[float, float, float]
    size: tuple[float, float, float]

    def volume(self) -> float:
        return self.size[0] * self.size[1] * self.size[2]


def close_xy_composite_partition(
    participants: Sequence[Mapping[str, object]],
    placements: Sequence[Free3DPlacement],
    box: Mapping[str, object],
    storage_height_mm: float,
    xy_clearance_mm: float,
    *,
    box_perimeter_xy_mm: float,
    between_bodies_z_mm: float,
    budget: SolverBudget,
    top_inset_zones: Sequence[TopInsetZone] = (),
) -> XYCompositeClosureResult:
    """Build connected same-base XY prisms after one gross rectangular solve."""

    gross = close_global_rectangular_partition(
        participants,
        placements,
        box,
        storage_height_mm,
        xy_clearance_mm,
        box_perimeter_xy_mm=box_perimeter_xy_mm,
        between_bodies_z_mm=between_bodies_z_mm,
        budget=budget,
        top_inset_zones=(),
    )
    if gross.empty_spaces:
        return _failure(
            "xy_composite_gross_partition_not_found",
            gross,
        )
    max_prisms = max(
        1,
        int(dict(budget.limits).get("max_closure_candidates", 10_000)),
    )
    owners: list[CompositeOwnerBody] = []
    total_subtracted = 0.0
    total_prisms = 0
    for gross_placement in gross.placements:
        source = next(
            (
                value
                for value in placements
                if value.participant_id == gross_placement.participant_id
            ),
            None,
        )
        if source is None:
            return _failure("xy_composite_source_owner_missing", gross)
        raw, subtracted, rejection = _decompose_owner(
            gross_placement,
            source,
            top_inset_zones,
        )
        if rejection:
            return _failure(rejection, gross)
        merged = _merge_prisms(raw)
        total_prisms += len(merged)
        if total_prisms > max_prisms:
            return _failure("xy_composite_prism_budget_exhausted", gross)
        owner = _owner_contract(source, gross_placement, merged, subtracted)
        if owner.certificate.get("certified") is not True:
            return _failure(
                str(
                    owner.certificate.get(
                        "stop_reason",
                        "xy_composite_owner_certificate_rejected",
                    )
                ),
                gross,
            )
        owners.append(owner)
        total_subtracted += subtracted
    certificate = _global_certificate(
        gross,
        owners,
        total_subtracted,
    )
    if certificate["certified"] is not True:
        return _failure(
            "xy_composite_global_certificate_rejected",
            gross,
            certificate=certificate,
        )
    digest = canonical_digest(
        {
            "schema_version": XY_COMPOSITE_CLOSURE_VERSION,
            "owners": [_owner_payload(value) for value in owners],
            "certificate": certificate,
        }
    )
    return XYCompositeClosureResult(
        status="closed",
        owner_bodies=tuple(sorted(owners, key=lambda value: value.owner_id)),
        gross_closure=gross,
        certificate=certificate,
        deterministic_digest=digest,
        stop_reason="xy_composite_partition_complete",
    )


def xy_composite_closure_to_dict(
    result: XYCompositeClosureResult,
) -> dict[str, object]:
    return {
        "schema_version": XY_COMPOSITE_CLOSURE_VERSION,
        "status": result.status,
        "stop_reason": result.stop_reason,
        "deterministic_digest": result.deterministic_digest,
        "certificate": dict(result.certificate),
        "owners": [_owner_payload(value) for value in result.owner_bodies],
        "gross_partition_certificate": dict(
            result.gross_closure.partition_certificate
        ),
    }


def _decompose_owner(
    gross: Free3DPlacement,
    source: Free3DPlacement,
    zones: Sequence[TopInsetZone],
) -> tuple[tuple[_RawPrism, ...], float, str]:
    lower_x, lower_y, lower_z = gross.origin_mm
    upper_x = lower_x + gross.world_size_mm[0]
    upper_y = lower_y + gross.world_size_mm[1]
    upper_z = lower_z + gross.world_size_mm[2]
    relevant: list[TopInsetZone] = []
    x_values = {lower_x, upper_x}
    y_values = {lower_y, upper_y}
    for zone in zones:
        zone_x0 = float(zone.origin_xy_mm[0])
        zone_y0 = float(zone.origin_xy_mm[1])
        zone_x1 = zone_x0 + float(zone.size_xy_mm[0])
        zone_y1 = zone_y0 + float(zone.size_xy_mm[1])
        if (
            zone_x0 >= upper_x - _EPSILON
            or zone_x1 <= lower_x + _EPSILON
            or zone_y0 >= upper_y - _EPSILON
            or zone_y1 <= lower_y + _EPSILON
            or float(zone.support_plane_z_mm) >= upper_z - _EPSILON
        ):
            continue
        zone_upper = float(zone.support_plane_z_mm + zone.inset_depth_mm)
        if zone_upper < upper_z - _EPSILON:
            return (), 0.0, "xy_composite_reservation_not_top_open"
        relevant.append(zone)
        x_values.update(
            {max(lower_x, zone_x0), min(upper_x, zone_x1)}
        )
        y_values.update(
            {max(lower_y, zone_y0), min(upper_y, zone_y1)}
        )
    xs = sorted(x_values)
    ys = sorted(y_values)
    raw: list[_RawPrism] = []
    subtracted = 0.0
    for x_index in range(len(xs) - 1):
        for y_index in range(len(ys) - 1):
            x0, x1 = xs[x_index], xs[x_index + 1]
            y0, y1 = ys[y_index], ys[y_index + 1]
            if x1 - x0 <= _EPSILON or y1 - y0 <= _EPSILON:
                continue
            top = upper_z
            for zone in relevant:
                if _cell_overlaps_zone(x0, x1, y0, y1, zone):
                    top = min(top, float(zone.support_plane_z_mm))
            if top <= lower_z + _EPSILON:
                subtracted += (x1 - x0) * (y1 - y0) * (upper_z - lower_z)
                continue
            raw.append(
                _RawPrism(
                    (x0, y0, lower_z),
                    (x1 - x0, y1 - y0, top - lower_z),
                )
            )
            subtracted += (x1 - x0) * (y1 - y0) * (upper_z - top)
    source_volume = _volume(source.world_size_mm)
    covered_source = sum(_intersection_volume(value, source) for value in raw)
    if abs(covered_source - source_volume) > max(_EPSILON, source_volume * 1e-9):
        return (), subtracted, "xy_composite_minimum_envelope_not_preserved"
    return tuple(raw), subtracted, ""


def _merge_prisms(values: Sequence[_RawPrism]) -> tuple[_RawPrism, ...]:
    current = list(values)
    changed = True
    while changed:
        changed = False
        current.sort(
            key=lambda value: (
                value.origin[2],
                value.size[2],
                value.origin[1],
                value.origin[0],
                value.size[1],
                value.size[0],
            )
        )
        for left_index, left in enumerate(current):
            for right_index in range(left_index + 1, len(current)):
                merged = _merge_pair(left, current[right_index])
                if merged is None:
                    continue
                current = [
                    value
                    for index, value in enumerate(current)
                    if index not in {left_index, right_index}
                ]
                current.append(merged)
                changed = True
                break
            if changed:
                break
    return tuple(current)


def _merge_pair(left: _RawPrism, right: _RawPrism) -> _RawPrism | None:
    if (
        abs(left.origin[2] - right.origin[2]) > _EPSILON
        or abs(left.size[2] - right.size[2]) > _EPSILON
    ):
        return None
    lx0, ly0, lz = left.origin
    rx0, ry0, _ = right.origin
    lx1, ly1 = lx0 + left.size[0], ly0 + left.size[1]
    rx1, ry1 = rx0 + right.size[0], ry0 + right.size[1]
    if (
        abs(ly0 - ry0) <= _EPSILON
        and abs(ly1 - ry1) <= _EPSILON
        and (abs(lx1 - rx0) <= _EPSILON or abs(rx1 - lx0) <= _EPSILON)
    ):
        x0, x1 = min(lx0, rx0), max(lx1, rx1)
        return _RawPrism((x0, ly0, lz), (x1 - x0, left.size[1], left.size[2]))
    if (
        abs(lx0 - rx0) <= _EPSILON
        and abs(lx1 - rx1) <= _EPSILON
        and (abs(ly1 - ry0) <= _EPSILON or abs(ry1 - ly0) <= _EPSILON)
    ):
        y0, y1 = min(ly0, ry0), max(ly1, ry1)
        return _RawPrism((lx0, y0, lz), (left.size[0], y1 - y0, left.size[2]))
    return None


def _owner_contract(
    source: Free3DPlacement,
    gross: Free3DPlacement,
    raw: Sequence[_RawPrism],
    subtracted_volume: float,
) -> CompositeOwnerBody:
    if not raw:
        certificate = {
            "schema_version": "bgig.xy_composite_owner_certificate.v1",
            "certified": False,
            "stop_reason": "xy_composite_owner_has_no_printable_prism",
        }
        return CompositeOwnerBody(
            source.participant_id, source, source.origin_mm[2], "", (), certificate
        )
    source_center = tuple(
        source.origin_mm[axis] + source.world_size_mm[axis] / 2.0
        for axis in range(3)
    )
    core_index = max(
        range(len(raw)),
        key=lambda index: (
            _contains_point_xy(raw[index], source_center),
            _intersection_volume(raw[index], source),
            raw[index].volume(),
            tuple(-value for value in raw[index].origin),
        ),
    )
    ordered = [raw[core_index]] + [
        value for index, value in enumerate(raw) if index != core_index
    ]
    temporary = [
        CompositePrism(
            prism_id=f"{source.participant_id}:prism:{index:04d}",
            owner_id=source.participant_id,
            kind="core" if index == 0 else "annex",
            origin_mm=value.origin,
            size_mm=value.size,
            attached_to_prism_id="",
            attachment_axis="",
        )
        for index, value in enumerate(ordered)
    ]
    connected: set[int] = {0}
    pending = set(range(1, len(temporary)))
    resolved = [temporary[0]]
    while pending:
        options: list[tuple[int, int, str]] = []
        for annex_index in sorted(pending):
            for parent_index in sorted(connected):
                axis = _vertical_face_axis(
                    temporary[parent_index], temporary[annex_index]
                )
                if axis:
                    options.append((annex_index, parent_index, axis))
        if not options:
            break
        annex_index, parent_index, axis = min(options)
        annex = temporary[annex_index]
        temporary[annex_index] = CompositePrism(
            annex.prism_id,
            annex.owner_id,
            annex.kind,
            annex.origin_mm,
            annex.size_mm,
            temporary[parent_index].prism_id,
            axis,
        )
        connected.add(annex_index)
        pending.remove(annex_index)
        resolved.append(temporary[annex_index])
    common_bottom = all(
        abs(value.origin_mm[2] - source.origin_mm[2]) <= _EPSILON
        for value in temporary
    )
    union_contains_minimum = abs(
        sum(_intersection_volume_raw(value, source) for value in raw)
        - _volume(source.world_size_mm)
    ) <= max(_EPSILON, _volume(source.world_size_mm) * 1e-9)
    gross_volume = _volume(gross.world_size_mm)
    composite_volume = sum(value.volume() for value in raw)
    volume_error = abs(gross_volume - subtracted_volume - composite_volume)
    certified = bool(
        not pending
        and common_bottom
        and union_contains_minimum
        and volume_error <= max(_EPSILON, gross_volume * 1e-9)
    )
    certificate = {
        "schema_version": "bgig.xy_composite_owner_certificate.v1",
        "certified": certified,
        "owner_id": source.participant_id,
        "core_prism_id": temporary[0].prism_id,
        "prism_count": len(temporary),
        "annex_count": max(0, len(temporary) - 1),
        "unique_owner": all(
            value.owner_id == source.participant_id for value in temporary
        ),
        "common_lower_z": common_bottom,
        "minimum_envelope_contained_by_union": union_contains_minimum,
        "all_annexes_connected_by_vertical_xy_faces": not pending,
        "z_only_attachment_count": 0,
        "edge_or_point_attachment_count": 0,
        "gross_volume_mm3": round(gross_volume, 6),
        "reserved_subtraction_volume_mm3": round(subtracted_volume, 6),
        "composite_volume_mm3": round(composite_volume, 6),
        "coverage_error_mm3": round(volume_error, 9),
        "stop_reason": (
            "xy_composite_owner_certified"
            if certified
            else "xy_composite_owner_connectivity_rejected"
        ),
    }
    return CompositeOwnerBody(
        source.participant_id,
        source,
        source.origin_mm[2],
        temporary[0].prism_id,
        tuple(sorted(temporary, key=lambda value: value.prism_id)),
        certificate,
    )


def _global_certificate(
    gross: GlobalRectangularClosureResult,
    owners: Sequence[CompositeOwnerBody],
    subtracted_volume: float,
) -> dict[str, object]:
    gross_certificate = gross.partition_certificate
    gross_body_volume = float(gross_certificate["body_volume_mm3"])
    composite_volume = sum(
        sum(_volume(value.size_mm) for value in owner.prisms)
        for owner in owners
    )
    error = abs(gross_body_volume - subtracted_volume - composite_volume)
    certified = bool(
        all(owner.certificate.get("certified") is True for owner in owners)
        and len({owner.owner_id for owner in owners}) == len(owners)
        and error <= max(_EPSILON, gross_body_volume * 1e-9)
    )
    return {
        "schema_version": XY_COMPOSITE_CERTIFICATE_SCHEMA_V1,
        "certified": certified,
        "owner_count": len(owners),
        "every_owner_unique": len({owner.owner_id for owner in owners}) == len(owners),
        "gross_body_volume_mm3": round(gross_body_volume, 6),
        "reserved_subtraction_volume_mm3": round(subtracted_volume, 6),
        "composite_body_volume_mm3": round(composite_volume, 6),
        "technical_void_volume_mm3": gross_certificate[
            "technical_void_volume_mm3"
        ],
        "printable_residual_volume_mm3": 0.0 if certified else round(error, 6),
        "coverage_error_mm3": round(error, 9),
        "unique_owner_per_prism": all(
            prism.owner_id == owner.owner_id
            for owner in owners
            for prism in owner.prisms
        ),
        "all_prisms_share_owner_lower_z": all(
            owner.certificate.get("common_lower_z") is True for owner in owners
        ),
        "all_annexes_use_true_vertical_xy_faces": all(
            owner.certificate.get(
                "all_annexes_connected_by_vertical_xy_faces"
            ) is True
            for owner in owners
        ),
        "z_only_attachment_count": 0,
        "edge_or_point_attachment_count": 0,
        "reservation_subtractions_deferred_to_cad_ir": True,
        "partition_complete_by_construction": certified,
    }


def _failure(
    reason: str,
    gross: GlobalRectangularClosureResult,
    *,
    certificate: Mapping[str, object] | None = None,
) -> XYCompositeClosureResult:
    rejected = dict(certificate or {})
    rejected.update(
        {
            "schema_version": XY_COMPOSITE_CERTIFICATE_SCHEMA_V1,
            "certified": False,
            "stop_reason": reason,
        }
    )
    digest = canonical_digest(
        {
            "schema_version": XY_COMPOSITE_CLOSURE_VERSION,
            "reason": reason,
            "gross_digest": gross.deterministic_digest,
        }
    )
    return XYCompositeClosureResult(
        status="not_closed",
        owner_bodies=(),
        gross_closure=gross,
        certificate=rejected,
        deterministic_digest=digest,
        stop_reason=reason,
    )


def _owner_payload(owner: CompositeOwnerBody) -> dict[str, object]:
    source = owner.source_placement
    return {
        "owner_id": owner.owner_id,
        "base_z_mm": owner.base_z_mm,
        "core_prism_id": owner.core_prism_id,
        "source_minimum_placement": {
            "origin_mm": list(source.origin_mm),
            "world_size_mm": list(source.world_size_mm),
            "local_size_mm": list(source.local_size_mm),
            "rotation_deg_z": source.rotation_deg_z,
            "container_variant_id": str(
                getattr(source, "container_variant_id", "")
            ),
            "container_variant_digest": str(
                getattr(source, "container_variant_digest", "")
            ),
            "container_variant_canonical": bool(
                getattr(source, "container_variant_canonical", False)
            ),
        },
        "prisms": [
            {
                "prism_id": value.prism_id,
                "owner_id": value.owner_id,
                "kind": value.kind,
                "origin_mm": list(value.origin_mm),
                "size_mm": list(value.size_mm),
                "attached_to_prism_id": value.attached_to_prism_id,
                "attachment_axis": value.attachment_axis,
            }
            for value in owner.prisms
        ],
        "certificate": dict(owner.certificate),
    }


def _cell_overlaps_zone(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    zone: TopInsetZone,
) -> bool:
    zx0, zy0 = float(zone.origin_xy_mm[0]), float(zone.origin_xy_mm[1])
    zx1 = zx0 + float(zone.size_xy_mm[0])
    zy1 = zy0 + float(zone.size_xy_mm[1])
    return (
        x0 < zx1 - _EPSILON
        and zx0 < x1 - _EPSILON
        and y0 < zy1 - _EPSILON
        and zy0 < y1 - _EPSILON
    )


def _vertical_face_axis(left: CompositePrism, right: CompositePrism) -> str:
    lx0, ly0, lz0 = left.origin_mm
    rx0, ry0, rz0 = right.origin_mm
    lx1, ly1, lz1 = tuple(
        left.origin_mm[index] + left.size_mm[index] for index in range(3)
    )
    rx1, ry1, rz1 = tuple(
        right.origin_mm[index] + right.size_mm[index] for index in range(3)
    )
    overlap_z = min(lz1, rz1) - max(lz0, rz0)
    if overlap_z <= _EPSILON:
        return ""
    overlap_y = min(ly1, ry1) - max(ly0, ry0)
    if (
        overlap_y > _EPSILON
        and (abs(lx1 - rx0) <= _EPSILON or abs(rx1 - lx0) <= _EPSILON)
    ):
        return "x"
    overlap_x = min(lx1, rx1) - max(lx0, rx0)
    if (
        overlap_x > _EPSILON
        and (abs(ly1 - ry0) <= _EPSILON or abs(ry1 - ly0) <= _EPSILON)
    ):
        return "y"
    return ""


def _contains_point_xy(prism: _RawPrism, point: Sequence[float]) -> int:
    return int(
        prism.origin[0] - _EPSILON <= point[0] <= prism.origin[0] + prism.size[0] + _EPSILON
        and prism.origin[1] - _EPSILON <= point[1] <= prism.origin[1] + prism.size[1] + _EPSILON
    )


def _intersection_volume(prism: _RawPrism, placement: Free3DPlacement) -> float:
    return _intersection_volume_raw(prism, placement)


def _intersection_volume_raw(
    prism: _RawPrism,
    placement: Free3DPlacement,
) -> float:
    volume = 1.0
    for axis in range(3):
        lower = max(prism.origin[axis], placement.origin_mm[axis])
        upper = min(
            prism.origin[axis] + prism.size[axis],
            placement.origin_mm[axis] + placement.world_size_mm[axis],
        )
        volume *= max(0.0, upper - lower)
    return volume


def _volume(size: Sequence[float]) -> float:
    return float(size[0]) * float(size[1]) * float(size[2])
