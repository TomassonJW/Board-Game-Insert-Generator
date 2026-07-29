"""Pure, strictly subtractive plan for removable flat-item insets.

The finalized-container geometry is an immutable input.  This module derives
only negative rectangular volumes.  It never creates, joins, grows or rewrites
positive geometry.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping, Sequence

from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)
from board_game_insert_generator.product_grid import (
    PRODUCT_GRID_STEP_MM,
    is_on_product_grid,
    nearest_ticks,
)


FLAT_INSET_SUBTRACTION_PLAN_SCHEMA_V1 = (
    "bgig.flat_inset_subtraction_plan.v1"
)
FLAT_INSET_SUBTRACTION_OPERATION_SCHEMA_V1 = (
    "bgig.flat_inset_subtraction_operation.v1"
)
SUBTRACTIVE_FLAT_INSET_CERTIFICATE_SCHEMA_V1 = (
    "bgig.subtractive_flat_inset_certificate.v1"
)
FINALIZED_CONTAINER_GEOMETRY_SCHEMA_V1 = (
    "bgig.finalized_container_geometry.v1"
)
XY_COMPOSITE_CONTAINER_BODY_SCHEMA_V3 = (
    "bgig.xy_composite_container_body.v3"
)

TOP_INSET_KIND = "top_inset"
TOP_INSET_GRIP_KIND = "top_inset_grip"
FLAT_INSET_ATTRIBUTION = "flat_inset"
FLAT_GRIP_ATTRIBUTION = "flat_grip"
BOOLEAN_DIFFERENCE = "difference"

_NUMERIC_EPSILON_MM = 0.0001
_AXES = ("x", "y", "z")


class FlatInsetSubtractionError(ValueError):
    """Fail-closed rejection of a non-subtractive or ambiguous plan."""


def build_flat_inset_subtraction_plan(
    placements: Sequence[Mapping[str, object]],
    reservations: Sequence[Mapping[str, object]],
    *,
    design_top_z_mm: float,
    positive_geometry_certificate: Mapping[str, object],
    require_complete_reservation_coverage: bool = True,
) -> dict[str, object]:
    """Return the canonical negative-only plan for every finalized owner."""

    positive_digest, body_records = _validated_positive_certificate(
        positive_geometry_certificate
    )
    placement_values = tuple(
        sorted(
            (value for value in placements if isinstance(value, Mapping)),
            key=lambda value: str(value.get("id", "")),
        )
    )
    reservation_values = tuple(
        sorted(
            (value for value in reservations if isinstance(value, Mapping)),
            key=lambda value: str(value.get("id", "")),
        )
    )
    placement_ids = {str(value.get("id", "")) for value in placement_values}
    if not placement_ids or "" in placement_ids:
        raise FlatInsetSubtractionError(
            "La passe soustractive exige des proprietaires finalises identifies."
        )
    if placement_ids != set(body_records):
        raise FlatInsetSubtractionError(
            "Les proprietaires du certificat positif et du plan divergent."
        )
    if not is_on_product_grid(float(design_top_z_mm)):
        raise FlatInsetSubtractionError(
            "Le sommet de conception doit rester sur la grille produit."
        )

    operations: list[dict[str, object]] = []
    depth_witnesses: list[dict[str, object]] = []
    owner_target_ids: dict[str, tuple[str, ...]] = {}
    for placement in placement_values:
        owner_id = str(placement["id"])
        targets = _positive_targets(
            placement,
            body_records[owner_id],
        )
        owner_target_ids[owner_id] = tuple(
            str(value["target_prism_id"]) for value in targets
        )
        component_origin = {
            axis: min(
                float(_mapping(target["final_origin_mm"])[axis])
                for target in targets
            )
            for axis in _AXES
        }
        for target in targets:
            target_operations, target_witnesses = (
                _target_subtraction_operations(
                    owner_id,
                    target,
                    component_origin=component_origin,
                    reservations=reservation_values,
                    design_top_z_mm=float(design_top_z_mm),
                    owner_positive_geometry_digest=str(
                        body_records[owner_id][
                            "positive_geometry_digest"
                        ]
                    ),
                    aggregate_positive_geometry_digest=positive_digest,
                )
            )
            operations.extend(target_operations)
            depth_witnesses.extend(target_witnesses)

    operations.sort(key=_operation_sort_key)
    depth_witnesses.sort(key=_witness_sort_key)
    certificate = _subtractive_certificate(
        operations,
        depth_witnesses,
        placements=placement_values,
        reservations=reservation_values,
        positive_geometry_digest=positive_digest,
        require_complete_reservation_coverage=(
            require_complete_reservation_coverage
        ),
    )
    if certificate["certified"] is not True:
        codes = ", ".join(certificate["rejection_codes"])
        raise FlatInsetSubtractionError(
            "Le plan d encastrement soustractif est invalide"
            + (f" : {codes}." if codes else ".")
        )
    plan: dict[str, object] = {
        "schema_version": FLAT_INSET_SUBTRACTION_PLAN_SCHEMA_V1,
        "status": "certified",
        "boolean_contract": BOOLEAN_DIFFERENCE,
        "positive_geometry_schema_version": (
            FINALIZED_CONTAINER_GEOMETRY_SCHEMA_V1
        ),
        "positive_geometry_digest_before": positive_digest,
        "positive_geometry_digest_after": positive_digest,
        "product_grid_step_mm": PRODUCT_GRID_STEP_MM,
        "numeric_epsilon_mm": _NUMERIC_EPSILON_MM,
        "complete_reservation_coverage_required": (
            require_complete_reservation_coverage
        ),
        "operations": operations,
        "local_depth_witnesses": depth_witnesses,
        "owners": [
            {
                "owner_id": owner_id,
                "target_prism_ids": list(owner_target_ids[owner_id]),
                "operation_ids": [
                    str(value["id"])
                    for value in operations
                    if str(value["placement_id"]) == owner_id
                ],
            }
            for owner_id in sorted(owner_target_ids)
        ],
        "certificate": certificate,
    }
    plan["deterministic_digest"] = canonical_digest(plan)
    return plan


def assert_flat_inset_subtraction_plan(
    plan: Mapping[str, object],
    placements: Sequence[Mapping[str, object]],
    reservations: Sequence[Mapping[str, object]],
    *,
    design_top_z_mm: float,
    positive_geometry_certificate: Mapping[str, object],
) -> None:
    """Rebuild the pure artifact and reject any downstream divergence."""

    if (
        plan.get("schema_version")
        != FLAT_INSET_SUBTRACTION_PLAN_SCHEMA_V1
        or plan.get("status") != "certified"
    ):
        raise FlatInsetSubtractionError(
            "Le plan d encastrement soustractif v1 est absent ou invalide."
        )
    supplied = deepcopy(dict(plan))
    supplied_digest = str(supplied.pop("deterministic_digest", ""))
    if not supplied_digest or supplied_digest != canonical_digest(supplied):
        raise FlatInsetSubtractionError(
            "Le digest du plan d encastrement soustractif diverge."
        )
    expected = build_flat_inset_subtraction_plan(
        placements,
        reservations,
        design_top_z_mm=design_top_z_mm,
        positive_geometry_certificate=positive_geometry_certificate,
    )
    if supplied_digest != expected["deterministic_digest"] or dict(plan) != expected:
        raise FlatInsetSubtractionError(
            "Le plan d encastrement soustractif ne correspond plus "
            "a la geometrie positive figee."
        )


def operations_for_owner(
    plan: Mapping[str, object],
    owner_id: str,
) -> tuple[dict[str, object], ...]:
    """Return detached executable operations for one finalized body."""

    raw_operations = plan.get("operations", ())
    if not isinstance(raw_operations, (list, tuple)):
        raise FlatInsetSubtractionError(
            "Les operations soustractives doivent former une liste."
        )
    return tuple(
        deepcopy(dict(value))
        for value in raw_operations
        if isinstance(value, Mapping)
        and str(value.get("placement_id", "")) == owner_id
    )


def _validated_positive_certificate(
    certificate: Mapping[str, object],
) -> tuple[str, dict[str, Mapping[str, object]]]:
    raw_bodies = certificate.get("bodies", ())
    bodies = (
        tuple(value for value in raw_bodies if isinstance(value, Mapping))
        if isinstance(raw_bodies, (list, tuple))
        else ()
    )
    body_records = {
        str(value.get("owner_id", "")): value
        for value in bodies
        if str(value.get("owner_id", ""))
    }
    digest = str(certificate.get("positive_geometry_digest", ""))
    expected_digest = canonical_digest(
        {
            "schema_version": FINALIZED_CONTAINER_GEOMETRY_SCHEMA_V1,
            "body_positive_geometry_digests": [
                {
                    "owner_id": owner_id,
                    "positive_geometry_digest": str(
                        body_records[owner_id].get(
                            "positive_geometry_digest",
                            "",
                        )
                    ),
                }
                for owner_id in sorted(body_records)
            ],
        }
    )
    if (
        certificate.get("schema_version")
        != FINALIZED_CONTAINER_GEOMETRY_SCHEMA_V1
        or certificate.get("certified") is not True
        or not body_records
        or len(body_records) != len(bodies)
        or digest != expected_digest
        or int(certificate.get("flat_positive_body_count", -1)) != 0
        or int(certificate.get("flat_positive_union_count", -1)) != 0
        or int(certificate.get("flat_positive_operation_count", -1)) != 0
        or abs(float(certificate.get("flat_positive_volume_mm3", -1.0)))
        > _NUMERIC_EPSILON_MM
    ):
        raise FlatInsetSubtractionError(
            "La geometrie positive des conteneurs doit etre certifiee "
            "et figee avant la passe plate."
        )
    return digest, body_records


def _positive_targets(
    placement: Mapping[str, object],
    body_record: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    owner_id = str(placement["id"])
    composite = placement.get("composite_body")
    if isinstance(composite, Mapping):
        raw_prisms = composite.get("prisms", ())
        prisms = (
            tuple(value for value in raw_prisms if isinstance(value, Mapping))
            if isinstance(raw_prisms, (list, tuple))
            else ()
        )
        if (
            composite.get("schema_version")
            != XY_COMPOSITE_CONTAINER_BODY_SCHEMA_V3
            or str(composite.get("owner_id", "")) != owner_id
            or str(composite.get("positive_geometry_digest", ""))
            != str(body_record.get("positive_geometry_digest", ""))
            or not prisms
        ):
            raise FlatInsetSubtractionError(
                f"La geometrie positive composite de {owner_id!r} diverge."
            )
        targets: list[dict[str, object]] = []
        for prism in prisms:
            if (
                str(prism.get("owner_id", "")) != owner_id
                or prism.get("geometry_role") != "finalized_container"
                or prism.get("positive_geometry_source")
                != "container_finalization"
                or bool(prism.get("flat_item_id"))
                or "cad_origin_mm" in prism
                or "cad_size_mm" in prism
            ):
                raise FlatInsetSubtractionError(
                    f"Le prisme positif de {owner_id!r} porte une attribution interdite."
                )
            targets.append(
                {
                    "target_prism_id": str(prism["prism_id"]),
                    "final_origin_mm": deepcopy(prism["final_origin_mm"]),
                    "final_size_mm": deepcopy(prism["final_size_mm"]),
                }
            )
        return tuple(
            sorted(
                targets,
                key=lambda value: str(value["target_prism_id"]),
            )
        )
    origin = placement.get("origin_mm")
    size = placement.get("world_size_mm")
    if not isinstance(origin, Mapping) or not isinstance(size, Mapping):
        raise FlatInsetSubtractionError(
            f"Le conteneur finalise {owner_id!r} n a pas de volume positif."
        )
    return (
        {
            "target_prism_id": f"{owner_id}:finalized-container",
            "final_origin_mm": deepcopy(dict(origin)),
            "final_size_mm": deepcopy(dict(size)),
        },
    )


def _target_subtraction_operations(
    owner_id: str,
    target: Mapping[str, object],
    *,
    component_origin: Mapping[str, float],
    reservations: Sequence[Mapping[str, object]],
    design_top_z_mm: float,
    owner_positive_geometry_digest: str,
    aggregate_positive_geometry_digest: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    origin = _dimension(target["final_origin_mm"], "final_origin_mm")
    size = _dimension(target["final_size_mm"], "final_size_mm")
    target_id = str(target["target_prism_id"])
    target_top = origin["z"] + size["z"]
    operations: list[dict[str, object]] = []
    witnesses: list[dict[str, object]] = []
    for cell in _atomic_xy_cells(origin, size, reservations):
        center = (
            cell["x"] + cell["width"] / 2.0,
            cell["y"] + cell["height"] / 2.0,
        )
        footprint_matches = _footprint_matches(center, reservations)
        if footprint_matches:
            cell_operations: list[dict[str, object]] = []
            requested_intervals: list[tuple[float, float]] = []
            for reservation, region in footprint_matches:
                bottom = float(region["layer_bottom_z_mm"])
                top = float(region["layer_top_z_mm"])
                if top <= origin["z"] + _NUMERIC_EPSILON_MM:
                    continue
                if bottom >= target_top - _NUMERIC_EPSILON_MM:
                    continue
                if (
                    bottom < origin["z"] - _NUMERIC_EPSILON_MM
                    or top > target_top + _NUMERIC_EPSILON_MM
                ):
                    raise FlatInsetSubtractionError(
                        f"L intervalle plat [{bottom}; {top}] traverse "
                        f"partiellement le prisme {target_id!r}."
                    )
                requested_intervals.append((bottom, top))
                cell_operations.append(
                    _operation(
                        owner_id,
                        target_id,
                        cell,
                        component_origin=component_origin,
                        interval=(bottom, top),
                        kind=TOP_INSET_KIND,
                        attribution=FLAT_INSET_ATTRIBUTION,
                        reservation=reservation,
                        local_region_id=str(region["id"]),
                        overlapping_reservation_ids=_text_tuple(
                            region.get("overlapping_reservation_ids", ())
                        ),
                        owner_positive_geometry_digest=(
                            owner_positive_geometry_digest
                        ),
                        aggregate_positive_geometry_digest=(
                            aggregate_positive_geometry_digest
                        ),
                    )
                )
            if cell_operations:
                ordered_intervals = sorted(requested_intervals)
                contiguous = all(
                    abs(left[1] - right[0]) <= _NUMERIC_EPSILON_MM
                    for left, right in zip(
                        ordered_intervals,
                        ordered_intervals[1:],
                    )
                )
                non_overlapping = all(
                    left[1] <= right[0] + _NUMERIC_EPSILON_MM
                    for left, right in zip(
                        ordered_intervals,
                        ordered_intervals[1:],
                    )
                )
                combined_depth = sum(
                    top - bottom for bottom, top in ordered_intervals
                )
                span_depth = (
                    ordered_intervals[-1][1]
                    - ordered_intervals[0][0]
                )
                matched_reservation_ids = tuple(
                    sorted(
                        str(reservation["id"])
                        for reservation, _ in footprint_matches
                    )
                )
                declared_overlap_sets = {
                    tuple(
                        sorted(
                            _text_tuple(
                                region.get(
                                    "overlapping_reservation_ids",
                                    (),
                                )
                            )
                        )
                    )
                    for _, region in footprint_matches
                }
                witness = {
                    "owner_id": owner_id,
                    "target_prism_id": target_id,
                    "world_origin_xy_mm": {
                        "x": _mm(cell["x"]),
                        "y": _mm(cell["y"]),
                    },
                    "size_xy_mm": {
                        "x": _mm(cell["width"]),
                        "y": _mm(cell["height"]),
                    },
                    "covering_reservation_ids": list(
                        matched_reservation_ids
                    ),
                    "covering_flat_item_ids": [
                        str(reservation["flat_item_id"])
                        for reservation, _ in footprint_matches
                    ],
                    "operation_ids": [
                        str(value["id"]) for value in cell_operations
                    ],
                    "intervals_z_mm": [
                        {"bottom": _mm(bottom), "top": _mm(top)}
                        for bottom, top in ordered_intervals
                    ],
                    "combined_depth_mm": _mm(combined_depth),
                    "interval_span_depth_mm": _mm(span_depth),
                    "stack_contiguous": contiguous,
                    "stack_non_overlapping": non_overlapping,
                    "declared_covering_set_exact": (
                        declared_overlap_sets
                        == {matched_reservation_ids}
                    ),
                }
                witnesses.append(witness)
                operations.extend(cell_operations)
            continue

        grip_matches = [
            value
            for value in reservations
            if _point_in_rectangle(
                center,
                _reservation_rectangle(value, kind="grip"),
            )
        ]
        if not grip_matches:
            continue
        reservation = min(
            grip_matches,
            key=lambda value: (
                float(value["support_plane_z_mm"]),
                str(value["id"]),
            ),
        )
        interval = (
            design_top_z_mm - float(reservation["total_thickness_mm"]),
            design_top_z_mm,
        )
        if interval[1] <= origin["z"] + _NUMERIC_EPSILON_MM:
            continue
        if interval[0] >= target_top - _NUMERIC_EPSILON_MM:
            continue
        if (
            interval[0] < origin["z"] - _NUMERIC_EPSILON_MM
            or interval[1] > target_top + _NUMERIC_EPSILON_MM
        ):
            raise FlatInsetSubtractionError(
                f"La prise plate traverse partiellement le prisme {target_id!r}."
            )
        operations.append(
            _operation(
                owner_id,
                target_id,
                cell,
                component_origin=component_origin,
                interval=interval,
                kind=TOP_INSET_GRIP_KIND,
                attribution=FLAT_GRIP_ATTRIBUTION,
                reservation=reservation,
                local_region_id=f"{reservation['id']}:grip-region",
                overlapping_reservation_ids=(str(reservation["id"]),),
                owner_positive_geometry_digest=(
                    owner_positive_geometry_digest
                ),
                aggregate_positive_geometry_digest=(
                    aggregate_positive_geometry_digest
                ),
            )
        )
    return operations, witnesses


def _operation(
    owner_id: str,
    target_id: str,
    cell: Mapping[str, float],
    *,
    component_origin: Mapping[str, float],
    interval: tuple[float, float],
    kind: str,
    attribution: str,
    reservation: Mapping[str, object],
    local_region_id: str,
    overlapping_reservation_ids: tuple[str, ...],
    owner_positive_geometry_digest: str,
    aggregate_positive_geometry_digest: str,
) -> dict[str, object]:
    bottom, top = interval
    cell_id = ":".join(
        str(nearest_ticks(value))
        for value in (
            cell["x"],
            cell["y"],
            cell["width"],
            cell["height"],
        )
    )
    operation_id = (
        f"{reservation['id']}:{owner_id}:{target_id}:{kind}:{cell_id}"
    )
    world_origin = {
        "x": _mm(cell["x"]),
        "y": _mm(cell["y"]),
        "z": _mm(bottom),
    }
    size = {
        "x": _mm(cell["width"]),
        "y": _mm(cell["height"]),
        "z": _mm(top - bottom),
    }
    return {
        "schema_version": FLAT_INSET_SUBTRACTION_OPERATION_SCHEMA_V1,
        "id": operation_id,
        "kind": kind,
        "boolean_operation": BOOLEAN_DIFFERENCE,
        "geometry_role": "negative_volume",
        "geometry_attribution": attribution,
        "creates_positive_geometry": False,
        "creates_printable_body": False,
        "creates_union": False,
        "reservation_id": str(reservation["id"]),
        "flat_item_id": str(reservation["flat_item_id"]),
        "placement_id": owner_id,
        "target_prism_id": target_id,
        "local_region_id": local_region_id,
        "overlapping_reservation_ids": list(
            sorted(overlapping_reservation_ids)
        ),
        "removal_order": int(reservation["removal_order"]),
        "world_origin_mm": world_origin,
        "local_origin_mm": {
            axis: _mm(
                world_origin[axis] - float(component_origin[axis])
            )
            for axis in _AXES
        },
        "size_mm": size,
        "cut_plane_world_z_mm": _mm(top),
        "retained_body_below_mm": _mm(
            bottom - float(component_origin["z"])
        ),
        "minimum_floor_mm": 0.0,
        "cavity_overlap_area_mm2": 0.0,
        "local_interval_z_mm": {
            "bottom": _mm(bottom),
            "top": _mm(top),
        },
        "non_perforating": True,
        "owner_positive_geometry_digest": (
            owner_positive_geometry_digest
        ),
        "positive_geometry_digest": (
            aggregate_positive_geometry_digest
        ),
    }


def _subtractive_certificate(
    operations: Sequence[Mapping[str, object]],
    depth_witnesses: Sequence[Mapping[str, object]],
    *,
    placements: Sequence[Mapping[str, object]],
    reservations: Sequence[Mapping[str, object]],
    positive_geometry_digest: str,
    require_complete_reservation_coverage: bool,
) -> dict[str, object]:
    rejection_codes: list[str] = []
    operation_ids = [str(value.get("id", "")) for value in operations]
    if (
        len(operation_ids) != len(set(operation_ids))
        or any(not value for value in operation_ids)
    ):
        rejection_codes.append("FLAT_SUBTRACTION_OPERATION_ID_INVALID")
    allowed_attributions = {
        TOP_INSET_KIND: FLAT_INSET_ATTRIBUTION,
        TOP_INSET_GRIP_KIND: FLAT_GRIP_ATTRIBUTION,
    }
    exact_operations = True
    on_grid = True
    for operation in operations:
        kind = str(operation.get("kind", ""))
        origin = _mapping(operation.get("world_origin_mm"))
        local_origin = _mapping(operation.get("local_origin_mm"))
        size = _mapping(operation.get("size_mm"))
        interval = _mapping(operation.get("local_interval_z_mm"))
        values = [
            float(origin[axis]) for axis in _AXES
        ] + [
            float(local_origin[axis]) for axis in _AXES
        ] + [
            float(size[axis]) for axis in _AXES
        ] + [
            float(interval["bottom"]),
            float(interval["top"]),
            float(operation.get("cut_plane_world_z_mm", -1.0)),
        ]
        on_grid = on_grid and all(is_on_product_grid(value) for value in values)
        exact_operations = bool(
            exact_operations
            and operation.get("schema_version")
            == FLAT_INSET_SUBTRACTION_OPERATION_SCHEMA_V1
            and operation.get("boolean_operation") == BOOLEAN_DIFFERENCE
            and operation.get("geometry_role") == "negative_volume"
            and operation.get("geometry_attribution")
            == allowed_attributions.get(kind)
            and operation.get("creates_positive_geometry") is False
            and operation.get("creates_printable_body") is False
            and operation.get("creates_union") is False
            and bool(operation.get("flat_item_id"))
            and bool(operation.get("placement_id"))
            and bool(operation.get("target_prism_id"))
            and min(float(size[axis]) for axis in _AXES) > 0.0
            and abs(float(origin["z"]) - float(interval["bottom"]))
            <= _NUMERIC_EPSILON_MM
            and abs(
                float(size["z"])
                - (
                    float(interval["top"])
                    - float(interval["bottom"])
                )
            )
            <= _NUMERIC_EPSILON_MM
            and abs(
                float(operation.get("cut_plane_world_z_mm", -1.0))
                - float(interval["top"])
            )
            <= _NUMERIC_EPSILON_MM
            and str(operation.get("positive_geometry_digest", ""))
            == positive_geometry_digest
        )
    if not exact_operations:
        rejection_codes.append("FLAT_SUBTRACTION_OPERATION_NOT_EXACT")
    if not on_grid:
        rejection_codes.append("FLAT_SUBTRACTION_OFF_PRODUCT_GRID")
    overlapping_pairs = _overlapping_operation_pairs(operations)
    if overlapping_pairs:
        rejection_codes.append("FLAT_SUBTRACTION_VOLUMES_OVERLAP")
    witnesses_exact = all(
        value.get("stack_contiguous") is True
        and value.get("stack_non_overlapping") is True
        and value.get("declared_covering_set_exact") is True
        and abs(
            float(value.get("combined_depth_mm", -1.0))
            - float(value.get("interval_span_depth_mm", -2.0))
        )
        <= _NUMERIC_EPSILON_MM
        for value in depth_witnesses
    )
    if not witnesses_exact:
        rejection_codes.append("FLAT_LOCAL_DEPTH_STACK_INVALID")
    requested_flat_ids = {
        str(value.get("flat_item_id", ""))
        for value in reservations
        if str(value.get("flat_item_id", ""))
    }
    footprint_flat_ids = {
        str(value.get("flat_item_id", ""))
        for value in operations
        if value.get("kind") == TOP_INSET_KIND
    }
    if (
        require_complete_reservation_coverage
        and requested_flat_ids != footprint_flat_ids
    ):
        rejection_codes.append("FLAT_INSET_FOOTPRINT_NOT_FULLY_ATTRIBUTED")
    owner_ids = {str(value.get("id", "")) for value in placements}
    if any(
        str(value.get("placement_id", "")) not in owner_ids
        for value in operations
    ):
        rejection_codes.append("FLAT_SUBTRACTION_OWNER_UNKNOWN")

    operation_volume = sum(_operation_volume_mm3(value) for value in operations)
    certified = not rejection_codes
    observed_depths = sorted(
        {
            _mm(float(value["combined_depth_mm"]))
            for value in depth_witnesses
        }
    )
    return {
        "schema_version": SUBTRACTIVE_FLAT_INSET_CERTIFICATE_SCHEMA_V1,
        "certified": certified,
        "boolean_operation": BOOLEAN_DIFFERENCE,
        "operation_count": len(operations),
        "flat_inset_operation_count": sum(
            int(value.get("kind") == TOP_INSET_KIND)
            for value in operations
        ),
        "flat_grip_operation_count": sum(
            int(value.get("kind") == TOP_INSET_GRIP_KIND)
            for value in operations
        ),
        "negative_volume_sum_mm3": _mm3(operation_volume),
        "negative_union_volume_mm3": _mm3(operation_volume),
        "negative_union_is_exact": not overlapping_pairs,
        "operation_attribution_complete": exact_operations,
        "all_coordinates_on_product_grid": on_grid,
        "local_depth_stack_exact": witnesses_exact,
        "complete_reservation_coverage_required": (
            require_complete_reservation_coverage
        ),
        "requested_flat_item_ids": sorted(requested_flat_ids),
        "covered_flat_item_ids": sorted(footprint_flat_ids),
        "observed_combined_local_depths_mm": observed_depths,
        "flat_positive_volume_mm3": 0.0,
        "flat_positive_body_count": 0,
        "flat_positive_union_count": 0,
        "flat_positive_operation_count": 0,
        "new_printable_body_count_attributed_to_flat_items": 0,
        "positive_geometry_digest_before": positive_geometry_digest,
        "positive_geometry_digest_after": positive_geometry_digest,
        "positive_geometry_unchanged": True,
        "positive_operations_after_subtraction_start": 0,
        "rejection_codes": rejection_codes,
        "stop_reason": (
            "strictly_subtractive_flat_insets_certified"
            if certified
            else "strictly_subtractive_flat_insets_rejected"
        ),
    }


def _atomic_xy_cells(
    origin: Mapping[str, float],
    size: Mapping[str, float],
    reservations: Sequence[Mapping[str, object]],
) -> tuple[dict[str, float], ...]:
    x0 = float(origin["x"])
    y0 = float(origin["y"])
    x1 = x0 + float(size["x"])
    y1 = y0 + float(size["y"])
    xs = {x0, x1}
    ys = {y0, y1}
    rectangles: list[tuple[float, float, float, float]] = []
    for reservation in reservations:
        raw_regions = reservation.get("local_depth_regions", ())
        if isinstance(raw_regions, (list, tuple)):
            for region in raw_regions:
                if not isinstance(region, Mapping):
                    continue
                rectangles.append(
                    _rectangle(
                        region.get("cut_origin_mm"),
                        region.get("cut_size_mm"),
                    )
                )
        rectangles.append(_reservation_rectangle(reservation, kind="grip"))
    for rectangle in rectangles:
        intersection = _rectangle_intersection(
            (x0, y0, x1, y1),
            rectangle,
        )
        if intersection is None:
            continue
        xs.update((intersection[0], intersection[2]))
        ys.update((intersection[1], intersection[3]))
    cells = []
    ordered_x = sorted(xs)
    ordered_y = sorted(ys)
    for x_index in range(len(ordered_x) - 1):
        for y_index in range(len(ordered_y) - 1):
            width = ordered_x[x_index + 1] - ordered_x[x_index]
            height = ordered_y[y_index + 1] - ordered_y[y_index]
            if (
                width <= _NUMERIC_EPSILON_MM
                or height <= _NUMERIC_EPSILON_MM
            ):
                continue
            cells.append(
                {
                    "x": _mm(ordered_x[x_index]),
                    "y": _mm(ordered_y[y_index]),
                    "width": _mm(width),
                    "height": _mm(height),
                }
            )
    return tuple(cells)


def _footprint_matches(
    point: tuple[float, float],
    reservations: Sequence[Mapping[str, object]],
) -> tuple[tuple[Mapping[str, object], Mapping[str, object]], ...]:
    matches: list[
        tuple[Mapping[str, object], Mapping[str, object]]
    ] = []
    for reservation in reservations:
        raw_regions = reservation.get("local_depth_regions", ())
        if not isinstance(raw_regions, (list, tuple)):
            continue
        for region in raw_regions:
            if not isinstance(region, Mapping):
                continue
            if _point_in_rectangle(
                point,
                _rectangle(
                    region.get("cut_origin_mm"),
                    region.get("cut_size_mm"),
                ),
            ):
                matches.append((reservation, region))
                break
    return tuple(
        sorted(
            matches,
            key=lambda value: (
                float(value[1]["layer_bottom_z_mm"]),
                str(value[0]["id"]),
            ),
        )
    )


def _reservation_rectangle(
    reservation: Mapping[str, object],
    *,
    kind: str,
) -> tuple[float, float, float, float]:
    if kind != "grip":
        raise FlatInsetSubtractionError(
            f"Type de rectangle plat inconnu : {kind!r}."
        )
    grip = reservation.get("grip_zone")
    if not isinstance(grip, Mapping):
        return (0.0, 0.0, 0.0, 0.0)
    return _rectangle(grip.get("origin_mm"), grip.get("size_mm"))


def _rectangle(
    raw_origin: object,
    raw_size: object,
) -> tuple[float, float, float, float]:
    origin = _mapping(raw_origin)
    size = _mapping(raw_size)
    x0 = float(origin["x"])
    y0 = float(origin["y"])
    return (
        x0,
        y0,
        x0 + float(size["x"]),
        y0 + float(size["y"]),
    )


def _rectangle_intersection(
    left: Sequence[float],
    right: Sequence[float],
) -> tuple[float, float, float, float] | None:
    intersection = (
        max(float(left[0]), float(right[0])),
        max(float(left[1]), float(right[1])),
        min(float(left[2]), float(right[2])),
        min(float(left[3]), float(right[3])),
    )
    if (
        intersection[2] - intersection[0] <= _NUMERIC_EPSILON_MM
        or intersection[3] - intersection[1] <= _NUMERIC_EPSILON_MM
    ):
        return None
    return intersection


def _point_in_rectangle(
    point: Sequence[float],
    rectangle: Sequence[float],
) -> bool:
    return bool(
        rectangle[0] - _NUMERIC_EPSILON_MM
        <= point[0]
        <= rectangle[2] + _NUMERIC_EPSILON_MM
        and rectangle[1] - _NUMERIC_EPSILON_MM
        <= point[1]
        <= rectangle[3] + _NUMERIC_EPSILON_MM
    )


def _overlapping_operation_pairs(
    operations: Sequence[Mapping[str, object]],
) -> list[tuple[str, str]]:
    boxes = [
        (
            str(value.get("id", "")),
            str(value.get("placement_id", "")),
            _operation_box_ticks(value),
        )
        for value in operations
    ]
    overlaps: list[tuple[str, str]] = []
    for left_index, left in enumerate(boxes):
        for right in boxes[left_index + 1 :]:
            if left[1] != right[1]:
                continue
            if all(
                min(left[2][axis][1], right[2][axis][1])
                > max(left[2][axis][0], right[2][axis][0])
                for axis in range(3)
            ):
                overlaps.append((left[0], right[0]))
    return overlaps


def _operation_box_ticks(
    operation: Mapping[str, object],
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    origin = _mapping(operation["world_origin_mm"])
    size = _mapping(operation["size_mm"])
    return tuple(
        (
            nearest_ticks(float(origin[axis])),
            nearest_ticks(float(origin[axis]) + float(size[axis])),
        )
        for axis in _AXES
    )  # type: ignore[return-value]


def _operation_volume_mm3(operation: Mapping[str, object]) -> float:
    box = _operation_box_ticks(operation)
    tick_volume = 1
    for lower, upper in box:
        tick_volume *= upper - lower
    return tick_volume / 1000.0


def _operation_sort_key(
    operation: Mapping[str, object],
) -> tuple[object, ...]:
    origin = _mapping(operation["world_origin_mm"])
    size = _mapping(operation["size_mm"])
    return (
        str(operation["placement_id"]),
        str(operation["target_prism_id"]),
        float(origin["z"]),
        float(origin["x"]),
        float(origin["y"]),
        float(size["z"]),
        str(operation["kind"]),
        str(operation["flat_item_id"]),
        str(operation["id"]),
    )


def _witness_sort_key(
    witness: Mapping[str, object],
) -> tuple[object, ...]:
    origin = _mapping(witness["world_origin_xy_mm"])
    return (
        str(witness["owner_id"]),
        str(witness["target_prism_id"]),
        float(origin["x"]),
        float(origin["y"]),
    )


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise FlatInsetSubtractionError(
            "Une structure geometrique attendue est absente."
        )
    return value


def _dimension(value: object, label: str) -> dict[str, float]:
    mapping = _mapping(value)
    result = {axis: float(mapping[axis]) for axis in _AXES}
    if not all(is_on_product_grid(number) for number in result.values()):
        raise FlatInsetSubtractionError(
            f"{label} doit rester sur la grille produit de 0,1 mm."
        )
    if label.endswith("size_mm") and min(result.values()) <= 0.0:
        raise FlatInsetSubtractionError(
            f"{label} doit etre strictement positif."
        )
    return result


def _text_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise FlatInsetSubtractionError(
            "La liste des reservations couvrantes est invalide."
        )
    result = tuple(str(item) for item in value if str(item))
    if len(result) != len(value):
        raise FlatInsetSubtractionError(
            "Une reservation couvrante n est pas identifiee."
        )
    return result


def _mm(value: float) -> float:
    rounded = round(float(value), 6)
    if not is_on_product_grid(rounded):
        raise FlatInsetSubtractionError(
            f"La valeur {rounded} mm sort de la grille produit de 0,1 mm."
        )
    return rounded


def _mm3(value: float) -> float:
    return round(float(value), 6)
