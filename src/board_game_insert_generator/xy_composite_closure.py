"""Bounded XY-composite fallback for top-reservation finishing."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Mapping, Sequence

from board_game_insert_generator.free_3d_continuous_closure import (
    Free3DClosureResult,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    EmptySpace,
    Free3DPlacement,
    TopInsetZone,
)
from board_game_insert_generator.global_rectangular_closure import (
    GlobalRectangularClosureResult,
    close_global_rectangular_partition,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_contract import SolverBudget


XY_COMPOSITE_CLOSURE_VERSION = "bgig.xy_composite_closure.v3"
XY_COMPOSITE_CERTIFICATE_SCHEMA_V1 = (
    "bgig.xy_composite_partition_certificate.v1"
)
XY_COMPOSITE_CERTIFICATE_SCHEMA_V2 = (
    "bgig.xy_composite_partition_certificate.v2"
)
_EPSILON = 0.0001
# Above this bounded branching point, try the already-certified rectangular
# partition before assigning residual cells owner by owner. Reservations remain
# deferred CAD cuts and the residual strategy keeps the unused wall-clock budget.
_RESERVATION_DEFERRED_FIRST_OWNER_COUNT = 12


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


@dataclass(frozen=True)
class _AttachmentOption:
    residual_index: int
    owner_id: str
    parent_index: int
    axis: str
    annex: _RawPrism
    seam_area_mm2: float
    internal_gap_mm: float
    external_corridors: tuple[_RawPrism, ...] = ()


@dataclass(frozen=True)
class _VerticalExtensionOption:
    residual_index: int
    owner_id: str
    parent_index: int
    replacement: tuple[_RawPrism, ...]
    vertical_gap_mm: float


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
    rectangular_attempt: GlobalRectangularClosureResult | None = None,
    continuous_prefill: Free3DClosureResult | None = None,
) -> XYCompositeClosureResult:
    """Build connected XY annexes after rectangular extensions."""

    if (
        continuous_prefill is not None
        and continuous_prefill.empty_spaces
        and top_inset_zones
        and len(placements) >= _RESERVATION_DEFERRED_FIRST_OWNER_COUNT
    ):
        started_at = perf_counter()
        reservation_deferred = close_xy_composite_partition(
            participants,
            placements,
            box,
            storage_height_mm,
            xy_clearance_mm,
            box_perimeter_xy_mm=box_perimeter_xy_mm,
            between_bodies_z_mm=between_bodies_z_mm,
            budget=budget,
            top_inset_zones=top_inset_zones,
            rectangular_attempt=None,
            continuous_prefill=None,
        )
        if reservation_deferred.status == "closed":
            return reservation_deferred
        limits = dict(budget.limits)
        remaining_elapsed_ms = max(
            0,
            int(limits.get("max_closure_elapsed_ms", 1_000))
            - int((perf_counter() - started_at) * 1_000.0),
        )
        if remaining_elapsed_ms <= 0:
            return reservation_deferred
        limits["max_closure_elapsed_ms"] = remaining_elapsed_ms
        residual_budget = SolverBudget(
            budget.family_id,
            budget.effort_profile,
            tuple(sorted(limits.items())),
        )
        gross_attempt = rectangular_attempt or close_global_rectangular_partition(
            participants,
            placements,
            box,
            storage_height_mm,
            xy_clearance_mm,
            box_perimeter_xy_mm=box_perimeter_xy_mm,
            between_bodies_z_mm=between_bodies_z_mm,
            budget=residual_budget,
            top_inset_zones=top_inset_zones,
        )
        return _close_hybrid_residual(
            placements,
            continuous_prefill,
            gross_attempt,
            box,
            storage_height_mm,
            xy_clearance_mm,
            box_perimeter_xy_mm=box_perimeter_xy_mm,
            between_bodies_z_mm=between_bodies_z_mm,
            budget=residual_budget,
            top_inset_zones=top_inset_zones,
        )

    if continuous_prefill is not None and continuous_prefill.empty_spaces:
        gross_attempt = rectangular_attempt or close_global_rectangular_partition(
            participants,
            placements,
            box,
            storage_height_mm,
            xy_clearance_mm,
            box_perimeter_xy_mm=box_perimeter_xy_mm,
            between_bodies_z_mm=between_bodies_z_mm,
            budget=budget,
            top_inset_zones=top_inset_zones,
        )
        return _close_hybrid_residual(
            placements,
            continuous_prefill,
            gross_attempt,
            box,
            storage_height_mm,
            xy_clearance_mm,
            box_perimeter_xy_mm=box_perimeter_xy_mm,
            between_bodies_z_mm=between_bodies_z_mm,
            budget=budget,
            top_inset_zones=top_inset_zones,
        )

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


def _close_hybrid_residual(
    source_placements: Sequence[Free3DPlacement],
    prefill: Free3DClosureResult,
    gross_attempt: GlobalRectangularClosureResult,
    box: Mapping[str, object],
    storage_height_mm: float,
    xy_clearance_mm: float,
    *,
    box_perimeter_xy_mm: float,
    between_bodies_z_mm: float,
    budget: SolverBudget,
    top_inset_zones: Sequence[TopInsetZone],
) -> XYCompositeClosureResult:
    deadline_at = perf_counter() + max(
        0.001,
        float(
            dict(budget.limits).get(
                "max_closure_elapsed_ms",
                1_000,
            )
        )
        / 1_000.0,
    )
    max_cells = max(
        1,
        int(dict(budget.limits).get("max_closure_candidates", 10_000)),
    )
    all_residual_cells, cell_rejection = _disjoint_residual_cells(
        prefill.empty_spaces,
        prefill.placements,
        top_inset_zones,
        max_cells=max_cells,
        deadline_at=deadline_at,
    )
    if cell_rejection:
        return _failure(cell_rejection, gross_attempt)
    source_by_id = {
        value.participant_id: value for value in source_placements
    }
    prefill_by_id = {
        value.participant_id: value for value in prefill.placements
    }
    if set(source_by_id) != set(prefill_by_id):
        return _failure(
            "xy_composite_prefill_owner_set_mismatch",
            gross_attempt,
        )
    raw_by_owner: dict[str, list[_RawPrism]] = {
        owner_id: [
            _RawPrism(
                tuple(prefill_by_id[owner_id].origin_mm),
                tuple(prefill_by_id[owner_id].world_size_mm),
            )
        ]
        for owner_id in sorted(prefill_by_id)
    }
    technical_corridors = list(
        value
        for value in all_residual_cells
        if _is_external_clearance_corridor(
            value,
            raw_by_owner,
            float(xy_clearance_mm),
            float(between_bodies_z_mm),
        )
    )
    residual_cells = tuple(
        value
        for value in all_residual_cells
        if value not in technical_corridors
    )
    pending = list(residual_cells)
    printable_residual_cell_count = len(residual_cells)
    initial_residual_volume = sum(value.volume() for value in pending)
    assigned_residual_volume = 0.0
    removed_internal_clearance_volume = 0.0
    assignment_trace: list[dict[str, object]] = []

    while pending:
        if perf_counter() >= deadline_at:
            return _failure(
                "xy_composite_deadline_reached",
                gross_attempt,
                certificate={
                    "residual_cell_count": len(residual_cells),
                    "unassigned_residual_cell_count": len(pending),
                    "source_minimum_envelopes_frozen": True,
                    "continuous_prefill_digest": prefill.deterministic_digest,
                    "assignment_trace": assignment_trace,
                    "unassigned_residual_signatures": [
                        list(_raw_signature(value)) for value in pending
                    ],
                },
            )
        vertical_options: list[
            tuple[tuple[object, ...], _VerticalExtensionOption]
        ] = []
        for residual_index, residual in enumerate(pending):
            for option in _vertical_extension_options(
                residual_index,
                residual,
                raw_by_owner,
                float(xy_clearance_mm),
                float(between_bodies_z_mm),
                top_inset_zones,
            ):
                current = raw_by_owner[option.owner_id]
                projected = _merge_prisms(
                    (
                        *current[: option.parent_index],
                        *option.replacement,
                        *current[option.parent_index + 1 :],
                    )
                )
                vertical_options.append(
                    (
                        (
                            round(option.vertical_gap_mm, 6),
                            max(0, len(projected) - 1),
                            option.owner_id,
                            _raw_signature(residual),
                            option.parent_index,
                        ),
                        option,
                    )
                )
        if vertical_options:
            _, selected_vertical = min(
                vertical_options,
                key=lambda value: value[0],
            )
            residual = pending[selected_vertical.residual_index]
            current = raw_by_owner[selected_vertical.owner_id]
            previous_volume = sum(value.volume() for value in current)
            projected = _merge_prisms(
                (
                    *current[: selected_vertical.parent_index],
                    *selected_vertical.replacement,
                    *current[selected_vertical.parent_index + 1 :],
                )
            )
            covered_indexes, partial_coverage = (
                _covered_residual_indexes(
                    pending,
                    selected_vertical.replacement,
                )
            )
            if (
                partial_coverage
                or selected_vertical.residual_index
                not in covered_indexes
            ):
                return _failure(
                    "xy_composite_partial_residual_consumption",
                    gross_attempt,
                )
            covered_residuals = [
                value
                for index, value in enumerate(pending)
                if index in covered_indexes
            ]
            pending = [
                value
                for index, value in enumerate(pending)
                if index not in covered_indexes
            ]
            raw_by_owner[selected_vertical.owner_id] = list(projected)
            added_volume = (
                sum(value.volume() for value in projected)
                - previous_volume
            )
            covered_volume = sum(
                value.volume() for value in covered_residuals
            )
            bridge_volume = max(0.0, added_volume - covered_volume)
            assigned_residual_volume += covered_volume
            removed_internal_clearance_volume += bridge_volume
            assignment_trace.append(
                {
                    "residual_signature": list(_raw_signature(residual)),
                    "owner_id": selected_vertical.owner_id,
                    "attachment_axis": "rectangular_z_extension",
                    "seam_area_mm2": 0.0,
                    "internal_gap_removed_mm": round(
                        selected_vertical.vertical_gap_mm,
                        6,
                    ),
                    "internal_gap_removed_volume_mm3": round(
                        bridge_volume,
                        6,
                    ),
                    "covered_residual_cell_count": len(
                        covered_residuals
                    ),
                    "covered_residual_volume_mm3": round(
                        covered_volume,
                        6,
                    ),
                }
            )
            if (
                sum(len(values) for values in raw_by_owner.values())
                > max_cells
            ):
                return _failure(
                    "xy_composite_prism_budget_exhausted",
                    gross_attempt,
                )
            continue
        options: list[
            tuple[
                tuple[object, ...],
                _AttachmentOption,
            ]
        ] = []
        options_by_residual: dict[int, int] = {}
        for residual_index, residual in enumerate(pending):
            residual_options = _attachment_options(
                residual_index,
                residual,
                raw_by_owner,
                float(xy_clearance_mm),
                float(between_bodies_z_mm),
                top_inset_zones,
            )
            options_by_residual[residual_index] = len(residual_options)
            for option in residual_options:
                current = raw_by_owner[option.owner_id]
                projected = _merge_prisms((*current, option.annex))
                added_by_owner = {
                    owner_id: sum(value.volume() for value in values)
                    - _volume(prefill_by_id[owner_id].world_size_mm)
                    for owner_id, values in raw_by_owner.items()
                }
                projected_added = (
                    sum(value.volume() for value in projected)
                    - _volume(
                        prefill_by_id[option.owner_id].world_size_mm
                    )
                )
                added_by_owner[option.owner_id] = projected_added
                added_values = tuple(added_by_owner.values())
                imbalance = (
                    max(added_values) - min(added_values)
                    if added_values
                    else 0.0
                )
                annex_count = max(0, len(projected) - 1)
                corner_proxy = annex_count * 8
                longest_face = max(
                    option.annex.size[0],
                    option.annex.size[1],
                )
                rank = (
                    options_by_residual[residual_index],
                    annex_count,
                    corner_proxy,
                    round(option.seam_area_mm2, 6),
                    round(imbalance, 6),
                    -round(longest_face, 6),
                    option.owner_id,
                    _raw_signature(residual),
                    option.parent_index,
                    option.axis,
                )
                options.append((rank, option))
        if not options:
            emergent_corridors = [
                value
                for value in pending
                if _is_external_clearance_corridor(
                    value,
                    raw_by_owner,
                    float(xy_clearance_mm),
                    float(between_bodies_z_mm),
                )
                or _is_clearance_corridor_junction(
                    value,
                    technical_corridors,
                    float(xy_clearance_mm),
                )
                or _is_xy_clearance_cross_junction(
                    value,
                    raw_by_owner,
                    float(xy_clearance_mm),
                )
                or _is_union_z_clearance_corridor(
                    value,
                    raw_by_owner,
                    float(between_bodies_z_mm),
                )
            ]
            if emergent_corridors:
                emergent_volume = sum(
                    value.volume() for value in emergent_corridors
                )
                pending = [
                    value
                    for value in pending
                    if value not in emergent_corridors
                ]
                technical_corridors.extend(emergent_corridors)
                printable_residual_cell_count -= len(
                    emergent_corridors
                )
                initial_residual_volume -= emergent_volume
                continue
            split_corridor = next(
                (
                    (
                        residual_index,
                        pieces,
                    )
                    for residual_index, residual in enumerate(pending)
                    if (
                        pieces := _split_certified_external_corridor(
                            residual,
                            raw_by_owner,
                            float(xy_clearance_mm),
                            float(between_bodies_z_mm),
                            technical_corridors,
                        )
                    )
                ),
                None,
            )
            if split_corridor is not None:
                residual_index, pieces = split_corridor
                corridor = pending.pop(residual_index)
                technical_corridors.extend(pieces)
                printable_residual_cell_count -= 1
                initial_residual_volume -= corridor.volume()
                continue
            trimmed_options: list[
                tuple[tuple[object, ...], _AttachmentOption]
            ] = []
            for residual_index, residual in enumerate(pending):
                for option in _trimmed_attachment_options(
                    residual_index,
                    residual,
                    raw_by_owner,
                    float(xy_clearance_mm),
                    float(between_bodies_z_mm),
                    top_inset_zones,
                    technical_corridors,
                ):
                    corridor_volume = sum(
                        value.volume()
                        for value in option.external_corridors
                    )
                    trimmed_options.append(
                        (
                            (
                                round(corridor_volume, 6),
                                len(option.external_corridors),
                                option.owner_id,
                                _raw_signature(residual),
                                option.parent_index,
                                option.axis,
                            ),
                            option,
                        )
                    )
            if trimmed_options:
                _, selected_trimmed = min(
                    trimmed_options,
                    key=lambda value: value[0],
                )
                options.append(
                    (
                        (
                            0,
                            0,
                            0,
                            0.0,
                            0.0,
                            0.0,
                            selected_trimmed.owner_id,
                            _raw_signature(
                                pending[
                                    selected_trimmed.residual_index
                                ]
                            ),
                            selected_trimmed.parent_index,
                            selected_trimmed.axis,
                        ),
                        selected_trimmed,
                    )
                )
        if not options:
            boundary_split = next(
                (
                    (residual_index, pieces)
                    for residual_index, residual in enumerate(pending)
                    if (
                        pieces := _partition_residual_by_owner_faces(
                            residual,
                            raw_by_owner,
                            top_inset_zones,
                            max_cells=max_cells - len(pending) + 1,
                        )
                    )
                    and any(
                        _vertical_extension_options(
                            0,
                            piece,
                            raw_by_owner,
                            float(xy_clearance_mm),
                            float(between_bodies_z_mm),
                            top_inset_zones,
                        )
                        or _attachment_options(
                            0,
                            piece,
                            raw_by_owner,
                            float(xy_clearance_mm),
                            float(between_bodies_z_mm),
                            top_inset_zones,
                        )
                        for piece in pieces
                    )
                ),
                None,
            )
            if boundary_split is not None:
                residual_index, pieces = boundary_split
                pending = [
                    *pending[:residual_index],
                    *pieces,
                    *pending[residual_index + 1 :],
                ]
                continue
        if not options:
            unassigned_volume = sum(value.volume() for value in pending)
            return _failure(
                "xy_composite_residual_owner_not_found",
                gross_attempt,
                certificate={
                    "residual_cell_count": len(residual_cells),
                    "unassigned_residual_cell_count": len(pending),
                    "printable_residual_volume_mm3": round(
                        unassigned_volume,
                        6,
                    ),
                    "source_minimum_envelopes_frozen": True,
                    "continuous_prefill_digest": prefill.deterministic_digest,
                    "assignment_trace": assignment_trace,
                    "unassigned_residual_signatures": [
                        list(_raw_signature(value)) for value in pending
                    ],
                },
            )
        _, selected = min(options, key=lambda value: value[0])
        residual = pending[selected.residual_index]
        consumed_shapes = (
            selected.annex,
            *selected.external_corridors,
        )
        (
            remaining_residuals,
            consumed_residuals,
            fully_consumed_indexes,
            split_residual_count,
        ) = _consume_pending_residuals(pending, consumed_shapes)
        if selected.residual_index not in fully_consumed_indexes:
            return _failure(
                "xy_composite_partial_residual_consumption",
                gross_attempt,
            )
        pending = list(remaining_residuals)
        owner_prisms = raw_by_owner[selected.owner_id]
        owner_prisms.append(selected.annex)
        raw_by_owner[selected.owner_id] = list(
            _merge_prisms(owner_prisms)
        )
        assigned_volume = sum(
            _raw_intersection_volume(value, selected.annex)
            for value in consumed_residuals
        )
        corridor_volume = sum(
            _raw_intersection_volume(value, corridor)
            for value in consumed_residuals
            for corridor in selected.external_corridors
        )
        assigned_residual_volume += assigned_volume
        initial_residual_volume -= corridor_volume
        technical_corridors.extend(selected.external_corridors)
        printable_residual_cell_count -= sum(
            1
            for value in consumed_residuals
            if _raw_intersection_volume(value, selected.annex)
            <= _EPSILON
        )
        bridge_volume = max(
            0.0,
            selected.annex.volume() - assigned_volume,
        )
        removed_internal_clearance_volume += bridge_volume
        assignment_trace.append(
            {
                "residual_signature": list(_raw_signature(residual)),
                "owner_id": selected.owner_id,
                "attachment_axis": selected.axis,
                "seam_area_mm2": round(selected.seam_area_mm2, 6),
                "internal_gap_removed_mm": round(
                    selected.internal_gap_mm,
                    6,
                ),
                "internal_gap_removed_volume_mm3": round(
                    bridge_volume,
                    6,
                ),
                "covered_residual_cell_count": len(
                    consumed_residuals
                ),
                "split_residual_cell_count": split_residual_count,
                "covered_residual_volume_mm3": round(
                    assigned_volume,
                    6,
                ),
                "external_clearance_split_volume_mm3": round(
                    corridor_volume,
                    6,
                ),
            }
        )
        if sum(len(values) for values in raw_by_owner.values()) > max_cells:
            return _failure(
                "xy_composite_prism_budget_exhausted",
                gross_attempt,
            )

    owners: list[CompositeOwnerBody] = []
    for owner_id in sorted(raw_by_owner):
        raw = tuple(raw_by_owner[owner_id])
        owner = _owner_contract(
            source_by_id[owner_id],
            prefill_by_id[owner_id],
            raw,
            0.0,
            expected_composite_volume=sum(
                value.volume() for value in raw
            ),
        )
        if owner.certificate.get("certified") is not True:
            return _failure(
                str(
                    owner.certificate.get(
                        "stop_reason",
                        "xy_composite_owner_certificate_rejected",
                    )
                ),
                gross_attempt,
                certificate=owner.certificate,
            )
        owners.append(owner)
    certificate = _hybrid_certificate(
        owners,
        source_placements,
        prefill.placements,
        box,
        storage_height_mm,
        box_perimeter_xy_mm,
        xy_clearance_mm,
        between_bodies_z_mm,
        top_inset_zones,
        residual_cell_count=printable_residual_cell_count,
        initial_residual_volume=initial_residual_volume,
        assigned_residual_volume=assigned_residual_volume,
        internal_clearance_removed_volume=(
            removed_internal_clearance_volume
        ),
        external_corridor_count=len(technical_corridors),
        external_corridor_volume=sum(
            value.volume() for value in technical_corridors
        ),
        assignment_trace=assignment_trace,
    )
    if certificate.get("certified") is not True:
        return _failure(
            str(
                certificate.get(
                    "stop_reason",
                    "xy_composite_hybrid_certificate_rejected",
                )
            ),
            gross_attempt,
            certificate=certificate,
        )
    digest = canonical_digest(
        {
            "schema_version": XY_COMPOSITE_CLOSURE_VERSION,
            "source_mode": "continuous_prefill_residual_cells",
            "continuous_prefill_digest": prefill.deterministic_digest,
            "owners": [_owner_payload(value) for value in owners],
            "certificate": certificate,
        }
    )
    return XYCompositeClosureResult(
        status="closed",
        owner_bodies=tuple(owners),
        gross_closure=gross_attempt,
        certificate=certificate,
        deterministic_digest=digest,
        stop_reason="xy_composite_residual_partition_complete",
    )


def _disjoint_residual_cells(
    spaces: Sequence[EmptySpace],
    placements: Sequence[Free3DPlacement],
    zones: Sequence[TopInsetZone],
    *,
    max_cells: int,
    deadline_at: float,
) -> tuple[tuple[_RawPrism, ...], str]:
    if not spaces:
        return (), ""
    x_values: set[float] = set()
    y_values: set[float] = set()
    z_values: set[float] = set()
    for space in spaces:
        for axis, values in enumerate((x_values, y_values, z_values)):
            values.add(_coordinate(space.origin_mm[axis]))
            values.add(
                _coordinate(
                    space.origin_mm[axis] + space.size_mm[axis]
                )
            )
    for placement in placements:
        for axis, values in enumerate((x_values, y_values, z_values)):
            values.add(_coordinate(placement.origin_mm[axis]))
            values.add(
                _coordinate(
                    placement.origin_mm[axis]
                    + placement.world_size_mm[axis]
                )
            )
    for zone in zones:
        x_values.update(
            {
                _coordinate(zone.origin_xy_mm[0]),
                _coordinate(
                    zone.origin_xy_mm[0] + zone.size_xy_mm[0]
                ),
            }
        )
        y_values.update(
            {
                _coordinate(zone.origin_xy_mm[1]),
                _coordinate(
                    zone.origin_xy_mm[1] + zone.size_xy_mm[1]
                ),
            }
        )
        z_values.update(
            {
                _coordinate(zone.support_plane_z_mm),
                _coordinate(
                    zone.support_plane_z_mm + zone.inset_depth_mm
                ),
            }
        )
    axes = (
        tuple(sorted(x_values)),
        tuple(sorted(y_values)),
        tuple(sorted(z_values)),
    )
    indexes = [
        {value: index for index, value in enumerate(axis_values)}
        for axis_values in axes
    ]
    occupied: set[tuple[int, int, int]] = set()
    for space in spaces:
        if perf_counter() >= deadline_at:
            return (), "xy_composite_deadline_reached"
        lower = tuple(
            indexes[axis][_coordinate(space.origin_mm[axis])]
            for axis in range(3)
        )
        upper = tuple(
            indexes[axis][
                _coordinate(
                    space.origin_mm[axis] + space.size_mm[axis]
                )
            ]
            for axis in range(3)
        )
        for x_index in range(lower[0], upper[0]):
            for y_index in range(lower[1], upper[1]):
                for z_index in range(lower[2], upper[2]):
                    if perf_counter() >= deadline_at:
                        return (), "xy_composite_deadline_reached"
                    occupied.add((x_index, y_index, z_index))
                    if len(occupied) > max_cells:
                        return (), "xy_composite_residual_cell_budget_exhausted"
    raw = [
        _RawPrism(
            (
                axes[0][index[0]],
                axes[1][index[1]],
                axes[2][index[2]],
            ),
            (
                axes[0][index[0] + 1] - axes[0][index[0]],
                axes[1][index[1] + 1] - axes[1][index[1]],
                axes[2][index[2] + 1] - axes[2][index[2]],
            ),
        )
        for index in sorted(occupied)
        if all(
            axes[axis][index[axis] + 1]
            - axes[axis][index[axis]]
            > _EPSILON
            for axis in range(3)
        )
    ]
    return tuple(sorted(raw, key=_raw_signature)), ""


def _covered_residual_indexes(
    pending: Sequence[_RawPrism],
    added_prisms: Sequence[_RawPrism],
) -> tuple[set[int], bool]:
    """Identify every residual cell entirely consumed by new owner material."""

    covered: set[int] = set()
    partial_coverage = False
    for index, residual in enumerate(pending):
        residual_volume = residual.volume()
        covered_volume = sum(
            _raw_intersection_volume(residual, prism)
            for prism in added_prisms
        )
        tolerance = max(_EPSILON, residual_volume * 1e-9)
        if covered_volume >= residual_volume - tolerance:
            covered.add(index)
        elif covered_volume > tolerance:
            partial_coverage = True
    return covered, partial_coverage


def _consume_pending_residuals(
    pending: Sequence[_RawPrism],
    added_prisms: Sequence[_RawPrism],
) -> tuple[
    tuple[_RawPrism, ...],
    tuple[_RawPrism, ...],
    set[int],
    int,
]:
    """Consume added material while keeping exact leftover residual pieces."""

    remaining: list[_RawPrism] = []
    consumed: list[_RawPrism] = []
    fully_consumed: set[int] = set()
    split_count = 0
    for index, residual in enumerate(pending):
        pieces = (residual,)
        for added in added_prisms:
            next_pieces: list[_RawPrism] = []
            for piece in pieces:
                intersection = _raw_intersection_prism(piece, added)
                if intersection is None:
                    next_pieces.append(piece)
                    continue
                next_pieces.extend(
                    _subtract_raw_prism(piece, intersection)
                )
            pieces = tuple(next_pieces)
        remaining_volume = sum(value.volume() for value in pieces)
        tolerance = max(_EPSILON, residual.volume() * 1e-9)
        consumed_volume = residual.volume() - remaining_volume
        if consumed_volume <= tolerance:
            remaining.append(residual)
            continue
        consumed.append(residual)
        if remaining_volume <= tolerance:
            fully_consumed.add(index)
            continue
        split_count += 1
        remaining.extend(pieces)
    return (
        _merge_prisms(remaining),
        tuple(consumed),
        fully_consumed,
        split_count,
    )


def _partition_residual_by_owner_faces(
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    zones: Sequence[TopInsetZone] = (),
    *,
    max_cells: int,
) -> tuple[_RawPrism, ...]:
    """Restore certified XY boundaries erased by residual merging."""

    lower = residual.origin
    upper = tuple(
        residual.origin[axis] + residual.size[axis]
        for axis in range(3)
    )
    axes: list[set[float]] = [
        {lower[0], upper[0]},
        {lower[1], upper[1]},
    ]
    for values in raw_by_owner.values():
        for value in values:
            for axis in (0, 1):
                for boundary in (
                    value.origin[axis],
                    value.origin[axis] + value.size[axis],
                ):
                    if (
                        lower[axis] + _EPSILON
                        < boundary
                        < upper[axis] - _EPSILON
                    ):
                        axes[axis].add(boundary)
    for zone in zones:
        for axis in (0, 1):
            for boundary in (
                zone.origin_xy_mm[axis],
                zone.origin_xy_mm[axis] + zone.size_xy_mm[axis],
            ):
                if (
                    lower[axis] + _EPSILON
                    < boundary
                    < upper[axis] - _EPSILON
                ):
                    axes[axis].add(boundary)
    x_values = sorted(axes[0])
    y_values = sorted(axes[1])
    cell_count = (len(x_values) - 1) * (len(y_values) - 1)
    if cell_count <= 1 or cell_count > max_cells:
        return ()
    return tuple(
        sorted(
            (
                _RawPrism(
                    (x0, y0, residual.origin[2]),
                    (
                        x1 - x0,
                        y1 - y0,
                        residual.size[2],
                    ),
                )
                for x0, x1 in zip(x_values, x_values[1:])
                for y0, y1 in zip(y_values, y_values[1:])
                if x1 - x0 > _EPSILON and y1 - y0 > _EPSILON
            ),
            key=_raw_signature,
        )
    )


def _vertical_extension_options(
    residual_index: int,
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
    z_clearance_mm: float,
    zones: Sequence[TopInsetZone],
) -> tuple[_VerticalExtensionOption, ...]:
    options: list[_VerticalExtensionOption] = []
    residual_upper_z = residual.origin[2] + residual.size[2]
    for owner_id in sorted(raw_by_owner):
        owner_prisms = raw_by_owner[owner_id]
        for parent_index, parent in enumerate(owner_prisms):
            parent_upper_z = parent.origin[2] + parent.size[2]
            gap = residual.origin[2] - parent_upper_z
            if gap < -_EPSILON or gap > z_clearance_mm + _EPSILON:
                continue
            if not _contains_xy(parent, residual):
                continue
            replacement = _split_and_raise(
                parent,
                residual,
                residual_upper_z,
            )
            projected = (
                *owner_prisms[:parent_index],
                *replacement,
                *owner_prisms[parent_index + 1 :],
            )
            if any(
                _raw_intersection_volume(left, right) > _EPSILON
                for left_index, left in enumerate(projected)
                for right in projected[left_index + 1 :]
            ):
                continue
            if any(
                _raw_intersects_zone(value, zone)
                for value in replacement
                for zone in zones
            ):
                continue
            if any(
                not _raw_prisms_separated(
                    value,
                    other,
                    xy_clearance_mm,
                    z_clearance_mm,
                )
                for value in replacement
                for other_owner, other_values in raw_by_owner.items()
                if other_owner != owner_id
                for other in other_values
            ):
                continue
            options.append(
                _VerticalExtensionOption(
                    residual_index,
                    owner_id,
                    parent_index,
                    replacement,
                    max(0.0, gap),
                )
            )
    return tuple(options)


def _is_external_clearance_corridor(
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
    z_clearance_mm: float,
) -> bool:
    clearances = (
        float(xy_clearance_mm),
        float(xy_clearance_mm),
        float(z_clearance_mm),
    )
    if all(value <= _EPSILON for value in clearances):
        return False
    for axis, clearance in enumerate(clearances):
        if (
            clearance <= _EPSILON
            or abs(residual.size[axis] - clearance) > _EPSILON
        ):
            continue
        orthogonal_axes = tuple(
            candidate for candidate in range(3) if candidate != axis
        )
        lower_owners: set[str] = set()
        upper_owners: set[str] = set()
        residual_lower = residual.origin[axis]
        residual_upper = residual_lower + residual.size[axis]
        for owner_id, values in raw_by_owner.items():
            for value in values:
                covers_orthogonal = all(
                    value.origin[orthogonal]
                    <= residual.origin[orthogonal] + _EPSILON
                    and value.origin[orthogonal]
                    + value.size[orthogonal]
                    >= residual.origin[orthogonal]
                    + residual.size[orthogonal]
                    - _EPSILON
                    for orthogonal in orthogonal_axes
                )
                if not covers_orthogonal:
                    continue
                value_lower = value.origin[axis]
                value_upper = value_lower + value.size[axis]
                if abs(value_upper - residual_lower) <= _EPSILON:
                    lower_owners.add(owner_id)
                if abs(value_lower - residual_upper) <= _EPSILON:
                    upper_owners.add(owner_id)
        if any(
            lower_owner != upper_owner
            for lower_owner in lower_owners
            for upper_owner in upper_owners
        ):
            return True
    return False


def _is_clearance_corridor_junction(
    residual: _RawPrism,
    corridors: Sequence[_RawPrism],
    xy_clearance_mm: float,
) -> bool:
    """Preserve XY clearance intersections once an adjacent corridor is known."""

    if xy_clearance_mm <= _EPSILON or not any(
        abs(residual.size[axis] - xy_clearance_mm) <= _EPSILON
        for axis in (0, 1)
    ):
        return False
    return any(
        _raw_vertical_face_axis(residual, corridor)
        for corridor in corridors
    )


def _is_xy_clearance_cross_junction(
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
) -> bool:
    """Keep the square where two certified XY clearance lanes cross.

    At a four-way junction no single neighbouring owner spans the whole
    opposite face, so the ordinary corridor test cannot identify either
    lane.  The cell is technical when both XY dimensions equal the configured
    clearance and the XY projections of material touch all four sides.  The
    projection is intentional: an external XY lane stays void above a lower
    neighbouring body as well.
    """

    if (
        xy_clearance_mm <= _EPSILON
        or abs(residual.size[0] - xy_clearance_mm) > _EPSILON
        or abs(residual.size[1] - xy_clearance_mm) > _EPSILON
    ):
        return False
    lower = residual.origin
    upper = tuple(
        residual.origin[axis] + residual.size[axis]
        for axis in range(3)
    )
    touching: dict[str, set[str]] = {
        "left": set(),
        "right": set(),
        "bottom": set(),
        "top": set(),
    }
    for owner_id, values in raw_by_owner.items():
        for value in values:
            value_upper = tuple(
                value.origin[axis] + value.size[axis]
                for axis in range(3)
            )
            y_touches = bool(
                value.origin[1] <= upper[1] + _EPSILON
                and value_upper[1] >= lower[1] - _EPSILON
            )
            x_touches = bool(
                value.origin[0] <= upper[0] + _EPSILON
                and value_upper[0] >= lower[0] - _EPSILON
            )
            if (
                y_touches
                and abs(value_upper[0] - lower[0]) <= _EPSILON
            ):
                touching["left"].add(owner_id)
            if (
                y_touches
                and abs(value.origin[0] - upper[0]) <= _EPSILON
            ):
                touching["right"].add(owner_id)
            if (
                x_touches
                and abs(value_upper[1] - lower[1]) <= _EPSILON
            ):
                touching["bottom"].add(owner_id)
            if (
                x_touches
                and abs(value.origin[1] - upper[1]) <= _EPSILON
            ):
                touching["top"].add(owner_id)
    return bool(
        all(touching.values())
        and len(set().union(*touching.values())) >= 2
    )


def _is_union_z_clearance_corridor(
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    z_clearance_mm: float,
) -> bool:
    """Certify a Z gap whose two faces are mosaics of several owners."""

    if (
        z_clearance_mm <= _EPSILON
        or abs(residual.size[2] - z_clearance_mm) > _EPSILON
    ):
        return False
    lower_z = residual.origin[2]
    upper_z = lower_z + residual.size[2]
    below: list[tuple[str, _RawPrism]] = []
    above: list[tuple[str, _RawPrism]] = []
    for owner_id, values in raw_by_owner.items():
        for value in values:
            value_upper_z = value.origin[2] + value.size[2]
            if abs(value_upper_z - lower_z) <= _EPSILON:
                below.append((owner_id, value))
            if abs(value.origin[2] - upper_z) <= _EPSILON:
                above.append((owner_id, value))
    if not below or not above:
        return False
    x0, y0 = residual.origin[:2]
    x1 = x0 + residual.size[0]
    y1 = y0 + residual.size[1]
    xs = {x0, x1}
    ys = {y0, y1}
    for _, value in (*below, *above):
        vx0, vy0 = value.origin[:2]
        vx1 = vx0 + value.size[0]
        vy1 = vy0 + value.size[1]
        if vx0 < x1 - _EPSILON and x0 < vx1 - _EPSILON:
            xs.update({max(x0, vx0), min(x1, vx1)})
        if vy0 < y1 - _EPSILON and y0 < vy1 - _EPSILON:
            ys.update({max(y0, vy0), min(y1, vy1)})
    ordered_x = sorted(xs)
    ordered_y = sorted(ys)
    for x_index in range(len(ordered_x) - 1):
        for y_index in range(len(ordered_y) - 1):
            cell_x0, cell_x1 = (
                ordered_x[x_index],
                ordered_x[x_index + 1],
            )
            cell_y0, cell_y1 = (
                ordered_y[y_index],
                ordered_y[y_index + 1],
            )
            if (
                cell_x1 - cell_x0 <= _EPSILON
                or cell_y1 - cell_y0 <= _EPSILON
            ):
                continue
            center = (
                (cell_x0 + cell_x1) / 2.0,
                (cell_y0 + cell_y1) / 2.0,
            )
            lower_owners = {
                owner_id
                for owner_id, value in below
                if _point_in_raw_xy(center, value)
            }
            upper_owners = {
                owner_id
                for owner_id, value in above
                if _point_in_raw_xy(center, value)
            }
            if (
                not lower_owners
                or not upper_owners
                or not any(
                    lower_owner != upper_owner
                    for lower_owner in lower_owners
                    for upper_owner in upper_owners
                )
            ):
                return False
    return True


def _point_in_raw_xy(
    point: Sequence[float],
    prism: _RawPrism,
) -> bool:
    return bool(
        prism.origin[0] - _EPSILON
        <= point[0]
        <= prism.origin[0] + prism.size[0] + _EPSILON
        and prism.origin[1] - _EPSILON
        <= point[1]
        <= prism.origin[1] + prism.size[1] + _EPSILON
    )


def _raw_vertical_face_axis(
    left: _RawPrism,
    right: _RawPrism,
) -> str:
    left_upper = tuple(
        left.origin[axis] + left.size[axis] for axis in range(3)
    )
    right_upper = tuple(
        right.origin[axis] + right.size[axis] for axis in range(3)
    )
    overlap_z = min(left_upper[2], right_upper[2]) - max(
        left.origin[2],
        right.origin[2],
    )
    if overlap_z <= _EPSILON:
        return ""
    overlap_y = min(left_upper[1], right_upper[1]) - max(
        left.origin[1],
        right.origin[1],
    )
    if overlap_y > _EPSILON and (
        abs(left_upper[0] - right.origin[0]) <= _EPSILON
        or abs(right_upper[0] - left.origin[0]) <= _EPSILON
    ):
        return "x"
    overlap_x = min(left_upper[0], right_upper[0]) - max(
        left.origin[0],
        right.origin[0],
    )
    if overlap_x > _EPSILON and (
        abs(left_upper[1] - right.origin[1]) <= _EPSILON
        or abs(right_upper[1] - left.origin[1]) <= _EPSILON
    ):
        return "y"
    return ""


def _contains_xy(parent: _RawPrism, child: _RawPrism) -> bool:
    return bool(
        parent.origin[0] <= child.origin[0] + _EPSILON
        and parent.origin[1] <= child.origin[1] + _EPSILON
        and parent.origin[0] + parent.size[0]
        >= child.origin[0] + child.size[0] - _EPSILON
        and parent.origin[1] + parent.size[1]
        >= child.origin[1] + child.size[1] - _EPSILON
    )


def _split_and_raise(
    parent: _RawPrism,
    residual: _RawPrism,
    target_upper_z: float,
) -> tuple[_RawPrism, ...]:
    x_values = sorted(
        {
            parent.origin[0],
            residual.origin[0],
            residual.origin[0] + residual.size[0],
            parent.origin[0] + parent.size[0],
        }
    )
    y_values = sorted(
        {
            parent.origin[1],
            residual.origin[1],
            residual.origin[1] + residual.size[1],
            parent.origin[1] + parent.size[1],
        }
    )
    values: list[_RawPrism] = []
    for x_index in range(len(x_values) - 1):
        for y_index in range(len(y_values) - 1):
            x0, x1 = x_values[x_index], x_values[x_index + 1]
            y0, y1 = y_values[y_index], y_values[y_index + 1]
            if x1 - x0 <= _EPSILON or y1 - y0 <= _EPSILON:
                continue
            inside_residual_xy = bool(
                x0 >= residual.origin[0] - _EPSILON
                and x1
                <= residual.origin[0] + residual.size[0] + _EPSILON
                and y0 >= residual.origin[1] - _EPSILON
                and y1
                <= residual.origin[1] + residual.size[1] + _EPSILON
            )
            upper_z = (
                target_upper_z
                if inside_residual_xy
                else parent.origin[2] + parent.size[2]
            )
            values.append(
                _RawPrism(
                    (x0, y0, parent.origin[2]),
                    (
                        x1 - x0,
                        y1 - y0,
                        upper_z - parent.origin[2],
                    ),
                )
            )
    return _merge_prisms(values)


def _attachment_options(
    residual_index: int,
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
    z_clearance_mm: float,
    zones: Sequence[TopInsetZone],
) -> tuple[_AttachmentOption, ...]:
    options: list[_AttachmentOption] = []
    for owner_id in sorted(raw_by_owner):
        owner_prisms = raw_by_owner[owner_id]
        if not owner_prisms:
            continue
        owner_base = owner_prisms[0].origin[2]
        residual_upper_z = residual.origin[2] + residual.size[2]
        if residual_upper_z <= owner_base + _EPSILON:
            continue
        lowered_residual = _RawPrism(
            (
                residual.origin[0],
                residual.origin[1],
                owner_base,
            ),
            (
                residual.size[0],
                residual.size[1],
                residual_upper_z - owner_base,
            ),
        )
        for parent_index, parent in enumerate(owner_prisms):
            for axis, annex, seam_area, gap in _bridge_options(
                parent,
                lowered_residual,
                xy_clearance_mm,
            ):
                if any(
                    _raw_intersection_volume(annex, value) > _EPSILON
                    for index, value in enumerate(owner_prisms)
                    if index != parent_index
                ):
                    continue
                if any(_raw_intersects_zone(annex, zone) for zone in zones):
                    continue
                if any(
                    not _raw_prisms_separated(
                        annex,
                        other,
                        xy_clearance_mm,
                        z_clearance_mm,
                    )
                    for other_owner, other_values in raw_by_owner.items()
                    if other_owner != owner_id
                    for other in other_values
                ):
                    continue
                options.append(
                    _AttachmentOption(
                        residual_index,
                        owner_id,
                        parent_index,
                        axis,
                        annex,
                        seam_area,
                        gap,
                    )
                )
    return tuple(options)


def _trimmed_attachment_options(
    residual_index: int,
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
    z_clearance_mm: float,
    zones: Sequence[TopInsetZone],
    known_corridors: Sequence[_RawPrism],
) -> tuple[_AttachmentOption, ...]:
    """Split a residual cell only to preserve a certified external gap."""

    options: list[_AttachmentOption] = []
    for owner_id in sorted(raw_by_owner):
        owner_prisms = raw_by_owner[owner_id]
        if not owner_prisms:
            continue
        owner_base = owner_prisms[0].origin[2]
        residual_upper_z = residual.origin[2] + residual.size[2]
        if residual_upper_z <= owner_base + _EPSILON:
            continue
        lowered_residual = _RawPrism(
            (residual.origin[0], residual.origin[1], owner_base),
            (
                residual.size[0],
                residual.size[1],
                residual_upper_z - owner_base,
            ),
        )
        other_prisms = tuple(
            value
            for other_owner, values in raw_by_owner.items()
            if other_owner != owner_id
            for value in values
        )
        for parent_index, parent in enumerate(owner_prisms):
            for axis, annex, seam_area, gap in _bridge_options(
                parent,
                lowered_residual,
                xy_clearance_mm,
            ):
                for trimmed in _externally_separated_xy_trims(
                    annex,
                    other_prisms,
                    xy_clearance_mm,
                    z_clearance_mm,
                ):
                    if _raw_signature(trimmed) == _raw_signature(annex):
                        continue
                    if not _raw_vertical_face_axis(parent, trimmed):
                        continue
                    if any(
                        _raw_intersection_volume(trimmed, value) > _EPSILON
                        for index, value in enumerate(owner_prisms)
                        if index != parent_index
                    ):
                        continue
                    if any(
                        _raw_intersects_zone(trimmed, zone)
                        for zone in zones
                    ):
                        continue
                    assigned = _raw_intersection_prism(
                        residual,
                        trimmed,
                    )
                    if assigned is None:
                        continue
                    corridors = _subtract_raw_prism(residual, assigned)
                    if not corridors:
                        continue
                    prospective = {
                        candidate_owner: tuple(values)
                        for candidate_owner, values in raw_by_owner.items()
                    }
                    prospective[owner_id] = _merge_prisms(
                        (*owner_prisms, trimmed)
                    )
                    if not _technical_corridors_certified(
                        corridors,
                        prospective,
                        xy_clearance_mm,
                        z_clearance_mm,
                        known_corridors,
                    ):
                        continue
                    options.append(
                        _AttachmentOption(
                            residual_index,
                            owner_id,
                            parent_index,
                            axis,
                            trimmed,
                            seam_area,
                            gap,
                            corridors,
                        )
                    )
    return tuple(
        sorted(
            options,
            key=lambda value: (
                round(
                    sum(
                        corridor.volume()
                        for corridor in value.external_corridors
                    ),
                    6,
                ),
                value.owner_id,
                value.parent_index,
                value.axis,
                _raw_signature(value.annex),
            ),
        )
    )


def _externally_separated_xy_trims(
    annex: _RawPrism,
    other_prisms: Sequence[_RawPrism],
    xy_clearance_mm: float,
    z_clearance_mm: float,
) -> tuple[_RawPrism, ...]:
    candidates = (annex,)
    for other in other_prisms:
        next_candidates: dict[
            tuple[float, float, float, float, float, float],
            _RawPrism,
        ] = {}
        for candidate in candidates:
            if _raw_prisms_separated(
                candidate,
                other,
                xy_clearance_mm,
                z_clearance_mm,
            ):
                next_candidates[_raw_signature(candidate)] = candidate
                continue
            for trimmed in _xy_clearance_trims(
                candidate,
                other,
                xy_clearance_mm,
            ):
                next_candidates[_raw_signature(trimmed)] = trimmed
        if not next_candidates:
            return ()
        candidates = tuple(
            sorted(
                next_candidates.values(),
                key=lambda value: (
                    -round(value.volume(), 6),
                    _raw_signature(value),
                ),
            )[:64]
        )
    return tuple(
        value
        for value in candidates
        if all(
            _raw_prisms_separated(
                value,
                other,
                xy_clearance_mm,
                z_clearance_mm,
            )
            for other in other_prisms
        )
    )


def _xy_clearance_trims(
    prism: _RawPrism,
    obstacle: _RawPrism,
    clearance_mm: float,
) -> tuple[_RawPrism, ...]:
    lower = prism.origin
    upper = tuple(
        prism.origin[axis] + prism.size[axis] for axis in range(3)
    )
    obstacle_upper = tuple(
        obstacle.origin[axis] + obstacle.size[axis]
        for axis in range(3)
    )
    candidates: list[_RawPrism] = []
    for axis in (0, 1):
        positive_upper = obstacle.origin[axis] - clearance_mm
        if lower[axis] + _EPSILON < positive_upper < upper[axis] - _EPSILON:
            size = list(prism.size)
            size[axis] = positive_upper - lower[axis]
            candidates.append(_RawPrism(prism.origin, tuple(size)))
        negative_lower = obstacle_upper[axis] + clearance_mm
        if lower[axis] + _EPSILON < negative_lower < upper[axis] - _EPSILON:
            origin = list(prism.origin)
            size = list(prism.size)
            origin[axis] = negative_lower
            size[axis] = upper[axis] - negative_lower
            candidates.append(_RawPrism(tuple(origin), tuple(size)))
    return tuple(candidates)


def _raw_intersection_prism(
    left: _RawPrism,
    right: _RawPrism,
) -> _RawPrism | None:
    lower = tuple(
        max(left.origin[axis], right.origin[axis])
        for axis in range(3)
    )
    upper = tuple(
        min(
            left.origin[axis] + left.size[axis],
            right.origin[axis] + right.size[axis],
        )
        for axis in range(3)
    )
    if any(
        upper[axis] - lower[axis] <= _EPSILON
        for axis in range(3)
    ):
        return None
    return _RawPrism(
        lower,
        tuple(upper[axis] - lower[axis] for axis in range(3)),
    )


def _subtract_raw_prism(
    source: _RawPrism,
    removed: _RawPrism,
) -> tuple[_RawPrism, ...]:
    axes = tuple(
        tuple(
            sorted(
                {
                    source.origin[axis],
                    removed.origin[axis],
                    removed.origin[axis] + removed.size[axis],
                    source.origin[axis] + source.size[axis],
                }
            )
        )
        for axis in range(3)
    )
    values: list[_RawPrism] = []
    for x_index in range(len(axes[0]) - 1):
        for y_index in range(len(axes[1]) - 1):
            for z_index in range(len(axes[2]) - 1):
                lower = (
                    axes[0][x_index],
                    axes[1][y_index],
                    axes[2][z_index],
                )
                upper = (
                    axes[0][x_index + 1],
                    axes[1][y_index + 1],
                    axes[2][z_index + 1],
                )
                cell = _RawPrism(
                    lower,
                    tuple(
                        upper[axis] - lower[axis]
                        for axis in range(3)
                    ),
                )
                if cell.volume() <= _EPSILON:
                    continue
                if _raw_intersection_volume(cell, removed) > _EPSILON:
                    continue
                values.append(cell)
    return _merge_prisms(values)


def _technical_corridors_certified(
    corridors: Sequence[_RawPrism],
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
    z_clearance_mm: float,
    known_corridors: Sequence[_RawPrism],
) -> bool:
    pending = list(corridors)
    accepted = list(known_corridors)
    while pending:
        selected_index = next(
            (
                index
                for index, corridor in enumerate(pending)
                if _is_external_clearance_corridor(
                    corridor,
                    raw_by_owner,
                    xy_clearance_mm,
                    z_clearance_mm,
                )
                or _is_clearance_corridor_junction(
                    corridor,
                    accepted,
                    xy_clearance_mm,
                )
                or _is_xy_clearance_cross_junction(
                    corridor,
                    raw_by_owner,
                    xy_clearance_mm,
                )
                or _is_union_z_clearance_corridor(
                    corridor,
                    raw_by_owner,
                    z_clearance_mm,
                )
            ),
            None,
        )
        if selected_index is None:
            return False
        accepted.append(pending.pop(selected_index))
    return True


def _split_certified_external_corridor(
    residual: _RawPrism,
    raw_by_owner: Mapping[str, Sequence[_RawPrism]],
    xy_clearance_mm: float,
    z_clearance_mm: float,
    known_corridors: Sequence[_RawPrism],
) -> tuple[_RawPrism, ...]:
    """Split a mixed XY/Z clearance junction into certified void cells."""

    clearances = (
        float(xy_clearance_mm),
        float(xy_clearance_mm),
        float(z_clearance_mm),
    )
    axes: list[tuple[float, ...]] = []
    for axis, clearance in enumerate(clearances):
        lower = residual.origin[axis]
        upper = lower + residual.size[axis]
        coordinates = {lower, upper}
        if clearance > _EPSILON:
            for values in raw_by_owner.values():
                for value in values:
                    value_upper = value.origin[axis] + value.size[axis]
                    for candidate in (
                        value.origin[axis] - clearance,
                        value_upper + clearance,
                    ):
                        if lower + _EPSILON < candidate < upper - _EPSILON:
                            coordinates.add(candidate)
        axes.append(tuple(sorted(coordinates)))
    cell_count = (
        (len(axes[0]) - 1)
        * (len(axes[1]) - 1)
        * (len(axes[2]) - 1)
    )
    if cell_count <= 1 or cell_count > 4096:
        return ()
    pieces = tuple(
        _RawPrism(
            (
                axes[0][x_index],
                axes[1][y_index],
                axes[2][z_index],
            ),
            (
                axes[0][x_index + 1] - axes[0][x_index],
                axes[1][y_index + 1] - axes[1][y_index],
                axes[2][z_index + 1] - axes[2][z_index],
            ),
        )
        for x_index in range(len(axes[0]) - 1)
        for y_index in range(len(axes[1]) - 1)
        for z_index in range(len(axes[2]) - 1)
    )
    if not _technical_corridors_certified(
        pieces,
        raw_by_owner,
        xy_clearance_mm,
        z_clearance_mm,
        known_corridors,
    ):
        return ()
    return pieces


def _bridge_options(
    parent: _RawPrism,
    residual: _RawPrism,
    maximum_gap: float,
) -> tuple[tuple[str, _RawPrism, float, float], ...]:
    parent_upper = tuple(
        parent.origin[axis] + parent.size[axis] for axis in range(3)
    )
    residual_upper = tuple(
        residual.origin[axis] + residual.size[axis] for axis in range(3)
    )
    overlap_z = min(parent_upper[2], residual_upper[2]) - max(
        parent.origin[2],
        residual.origin[2],
    )
    if overlap_z <= _EPSILON:
        return ()
    options: list[tuple[str, _RawPrism, float, float]] = []
    overlap_y = min(parent_upper[1], residual_upper[1]) - max(
        parent.origin[1],
        residual.origin[1],
    )
    if overlap_y > _EPSILON:
        if parent_upper[0] <= residual.origin[0] + _EPSILON:
            gap = residual.origin[0] - parent_upper[0]
            if -_EPSILON <= gap <= maximum_gap + _EPSILON:
                options.append(
                    (
                        "x",
                        _RawPrism(
                            (
                                parent_upper[0],
                                residual.origin[1],
                                residual.origin[2],
                            ),
                            (
                                residual_upper[0] - parent_upper[0],
                                residual.size[1],
                                residual.size[2],
                            ),
                        ),
                        overlap_y * overlap_z,
                        max(0.0, gap),
                    )
                )
        if residual_upper[0] <= parent.origin[0] + _EPSILON:
            gap = parent.origin[0] - residual_upper[0]
            if -_EPSILON <= gap <= maximum_gap + _EPSILON:
                options.append(
                    (
                        "x",
                        _RawPrism(
                            residual.origin,
                            (
                                parent.origin[0] - residual.origin[0],
                                residual.size[1],
                                residual.size[2],
                            ),
                        ),
                        overlap_y * overlap_z,
                        max(0.0, gap),
                    )
                )
    overlap_x = min(parent_upper[0], residual_upper[0]) - max(
        parent.origin[0],
        residual.origin[0],
    )
    if overlap_x > _EPSILON:
        if parent_upper[1] <= residual.origin[1] + _EPSILON:
            gap = residual.origin[1] - parent_upper[1]
            if -_EPSILON <= gap <= maximum_gap + _EPSILON:
                options.append(
                    (
                        "y",
                        _RawPrism(
                            (
                                residual.origin[0],
                                parent_upper[1],
                                residual.origin[2],
                            ),
                            (
                                residual.size[0],
                                residual_upper[1] - parent_upper[1],
                                residual.size[2],
                            ),
                        ),
                        overlap_x * overlap_z,
                        max(0.0, gap),
                    )
                )
        if residual_upper[1] <= parent.origin[1] + _EPSILON:
            gap = parent.origin[1] - residual_upper[1]
            if -_EPSILON <= gap <= maximum_gap + _EPSILON:
                options.append(
                    (
                        "y",
                        _RawPrism(
                            residual.origin,
                            (
                                residual.size[0],
                                parent.origin[1] - residual.origin[1],
                                residual.size[2],
                            ),
                        ),
                        overlap_x * overlap_z,
                        max(0.0, gap),
                    )
                )
    return tuple(
        sorted(
            options,
            key=lambda value: (
                round(value[2], 6),
                value[0],
                _raw_signature(value[1]),
            ),
        )
    )


def _hybrid_certificate(
    owners: Sequence[CompositeOwnerBody],
    source_placements: Sequence[Free3DPlacement],
    prefill_placements: Sequence[Free3DPlacement],
    box: Mapping[str, object],
    storage_height_mm: float,
    box_perimeter_xy_mm: float,
    xy_clearance_mm: float,
    z_clearance_mm: float,
    zones: Sequence[TopInsetZone],
    *,
    residual_cell_count: int,
    initial_residual_volume: float,
    assigned_residual_volume: float,
    internal_clearance_removed_volume: float,
    external_corridor_count: int,
    external_corridor_volume: float,
    assignment_trace: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    owner_prisms = {
        owner.owner_id: tuple(
            _RawPrism(value.origin_mm, value.size_mm)
            for value in owner.prisms
        )
        for owner in owners
    }
    external_clearances = all(
        _raw_prisms_separated(
            left,
            right,
            xy_clearance_mm,
            z_clearance_mm,
        )
        for left_index, left_owner in enumerate(sorted(owner_prisms))
        for right_owner in sorted(owner_prisms)[left_index + 1 :]
        for left in owner_prisms[left_owner]
        for right in owner_prisms[right_owner]
    )
    reservations_excluded = all(
        not _raw_intersects_zone(prism, zone)
        for values in owner_prisms.values()
        for prism in values
        for zone in zones
    )
    sources_frozen = all(
        owner.certificate.get("minimum_envelope_contained_by_union") is True
        and owner.source_placement == next(
            value
            for value in source_placements
            if value.participant_id == owner.owner_id
        )
        for owner in owners
    )
    owner_connections = all(
        owner.certificate.get(
            "all_annexes_connected_by_vertical_xy_faces"
        )
        is True
        for owner in owners
    )
    support_certified = all(
        value.origin_mm[2] <= _EPSILON
        or value.support_coverage_ratio + _EPSILON >= 0.25
        for value in prefill_placements
    )
    residual = max(
        0.0,
        initial_residual_volume - assigned_residual_volume,
    )
    composite_volume = sum(
        _volume(prism.size_mm)
        for owner in owners
        for prism in owner.prisms
    )
    root_volume = max(
        0.0,
        (float(box["x"]) - 2.0 * box_perimeter_xy_mm)
        * (float(box["y"]) - 2.0 * box_perimeter_xy_mm)
        * float(storage_height_mm),
    )
    reservation_volume = _reservation_union_volume(
        zones,
        box,
        storage_height_mm,
        box_perimeter_xy_mm,
    )
    technical_void_volume = max(
        0.0,
        root_volume - reservation_volume - composite_volume,
    )
    certified = bool(
        owners
        and all(
            owner.certificate.get("certified") is True for owner in owners
        )
        and external_clearances
        and reservations_excluded
        and sources_frozen
        and owner_connections
        and support_certified
        and residual <= _EPSILON
    )
    return {
        "schema_version": XY_COMPOSITE_CERTIFICATE_SCHEMA_V2,
        "certified": certified,
        "source_mode": "continuous_prefill_residual_cells",
        "owner_count": len(owners),
        "residual_cell_count": residual_cell_count,
        "assigned_residual_cell_count": sum(
            int(value.get("covered_residual_cell_count", 1))
            for value in assignment_trace
        ),
        "initial_printable_residual_volume_mm3": round(
            initial_residual_volume,
            6,
        ),
        "assigned_residual_volume_mm3": round(
            assigned_residual_volume,
            6,
        ),
        "printable_residual_volume_mm3": (
            0.0 if residual <= _EPSILON else round(residual, 6)
        ),
        "internal_clearance_removed_volume_mm3": round(
            internal_clearance_removed_volume,
            6,
        ),
        "preserved_external_corridor_count": external_corridor_count,
        "preserved_external_corridor_volume_mm3": round(
            external_corridor_volume,
            6,
        ),
        "composite_body_volume_mm3": round(composite_volume, 6),
        "reserved_subtraction_volume_mm3": round(
            reservation_volume,
            6,
        ),
        "technical_void_volume_mm3": round(
            technical_void_volume,
            6,
        ),
        "source_minimum_envelopes_frozen": sources_frozen,
        "cavity_world_poses_unchanged": sources_frozen,
        "external_clearances_certified": external_clearances,
        "top_reservations_excluded": reservations_excluded,
        "owner_unions_connected": owner_connections,
        "annex_support_certified": support_certified,
        "internal_owner_annex_clearance_mm": 0.0,
        "unions_before_cavities_and_reservation_cuts": True,
        "partition_complete_by_construction": certified,
        "assignment_policy": [
            "fewest_owner_options",
            "fewest_annexes",
            "fewest_corner_proxy",
            "smallest_seam_area",
            "lowest_added_volume_imbalance",
            "longest_common_face",
            "stable_owner_and_cell_identity",
        ],
        "assignment_trace": [dict(value) for value in assignment_trace],
        "stop_reason": (
            "xy_composite_hybrid_certificate_accepted"
            if certified
            else "xy_composite_hybrid_certificate_rejected"
        ),
    }


def _raw_prisms_separated(
    left: _RawPrism,
    right: _RawPrism,
    xy_clearance_mm: float,
    z_clearance_mm: float,
) -> bool:
    gaps = []
    for axis in range(3):
        left_upper = left.origin[axis] + left.size[axis]
        right_upper = right.origin[axis] + right.size[axis]
        if left_upper <= right.origin[axis] + _EPSILON:
            gaps.append(max(0.0, right.origin[axis] - left_upper))
        elif right_upper <= left.origin[axis] + _EPSILON:
            gaps.append(max(0.0, left.origin[axis] - right_upper))
        else:
            gaps.append(-1.0)
    return bool(
        gaps[0] + _EPSILON >= xy_clearance_mm
        or gaps[1] + _EPSILON >= xy_clearance_mm
        or gaps[2] + _EPSILON >= z_clearance_mm
    )


def _raw_intersects_zone(
    prism: _RawPrism,
    zone: TopInsetZone,
) -> bool:
    zone_origin = (
        float(zone.origin_xy_mm[0]),
        float(zone.origin_xy_mm[1]),
        float(zone.support_plane_z_mm),
    )
    zone_size = (
        float(zone.size_xy_mm[0]),
        float(zone.size_xy_mm[1]),
        float(zone.inset_depth_mm),
    )
    return all(
        prism.origin[axis]
        < zone_origin[axis] + zone_size[axis] - _EPSILON
        and zone_origin[axis]
        < prism.origin[axis] + prism.size[axis] - _EPSILON
        for axis in range(3)
    )


def _raw_intersection_volume(
    left: _RawPrism,
    right: _RawPrism,
) -> float:
    volume = 1.0
    for axis in range(3):
        lower = max(left.origin[axis], right.origin[axis])
        upper = min(
            left.origin[axis] + left.size[axis],
            right.origin[axis] + right.size[axis],
        )
        volume *= max(0.0, upper - lower)
    return volume


def _reservation_union_volume(
    zones: Sequence[TopInsetZone],
    box: Mapping[str, object],
    storage_height_mm: float,
    perimeter: float,
) -> float:
    prisms: list[_RawPrism] = []
    for zone in zones:
        lower = (
            max(perimeter, float(zone.origin_xy_mm[0])),
            max(perimeter, float(zone.origin_xy_mm[1])),
            max(0.0, float(zone.support_plane_z_mm)),
        )
        upper = (
            min(
                float(box["x"]) - perimeter,
                float(zone.origin_xy_mm[0] + zone.size_xy_mm[0]),
            ),
            min(
                float(box["y"]) - perimeter,
                float(zone.origin_xy_mm[1] + zone.size_xy_mm[1]),
            ),
            min(
                float(storage_height_mm),
                float(zone.support_plane_z_mm + zone.inset_depth_mm),
            ),
        )
        if all(upper[axis] > lower[axis] + _EPSILON for axis in range(3)):
            prisms.append(
                _RawPrism(
                    lower,
                    tuple(
                        upper[axis] - lower[axis] for axis in range(3)
                    ),
                )
            )
    return _orthogonal_union_volume(prisms)


def _orthogonal_union_volume(prisms: Sequence[_RawPrism]) -> float:
    if not prisms:
        return 0.0
    axes = tuple(
        sorted(
            {
                _coordinate(value.origin[axis])
                for value in prisms
            }
            | {
                _coordinate(value.origin[axis] + value.size[axis])
                for value in prisms
            }
        )
        for axis in range(3)
    )
    volume = 0.0
    for x_index in range(len(axes[0]) - 1):
        for y_index in range(len(axes[1]) - 1):
            for z_index in range(len(axes[2]) - 1):
                center = (
                    (axes[0][x_index] + axes[0][x_index + 1]) / 2.0,
                    (axes[1][y_index] + axes[1][y_index + 1]) / 2.0,
                    (axes[2][z_index] + axes[2][z_index + 1]) / 2.0,
                )
                if not any(
                    all(
                        value.origin[axis] - _EPSILON
                        <= center[axis]
                        <= value.origin[axis]
                        + value.size[axis]
                        + _EPSILON
                        for axis in range(3)
                    )
                    for value in prisms
                ):
                    continue
                volume += (
                    (axes[0][x_index + 1] - axes[0][x_index])
                    * (axes[1][y_index + 1] - axes[1][y_index])
                    * (axes[2][z_index + 1] - axes[2][z_index])
                )
    return volume


def _raw_signature(value: _RawPrism) -> tuple[float, ...]:
    return tuple(
        _coordinate(number) for number in value.origin + value.size
    )


def _coordinate(value: float) -> float:
    return round(float(value), 6)


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
    *,
    expected_composite_volume: float | None = None,
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
    gross_volume = (
        float(expected_composite_volume)
        if expected_composite_volume is not None
        else _volume(gross.world_size_mm)
    )
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
