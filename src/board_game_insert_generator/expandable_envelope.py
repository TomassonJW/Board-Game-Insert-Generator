"""Executable P55 contract for fixed cavities and expandable container envelopes.

This pure module does not solve the box partition. It freezes the calibrated
cavity layout produced by P39, exposes the minimum printable envelope, and
validates a proposed final envelope against additive per-container constraints.
"""

from __future__ import annotations

from copy import deepcopy
from math import isfinite

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.project_v1 import normalize_project_draft


EXPANDABLE_ENVELOPE_SCHEMA_V1 = "bgig.expandable_envelope_contract.v1"
_AXES = ("x", "y", "z")
_EPSILON = 0.0001


class ExpandableEnvelopeError(ValueError):
    """Raised when proposed final envelopes do not match the P55 contract."""


def derive_expandable_envelope_contract(
    raw_project: object,
    *,
    final_outer_dimensions_by_group: object | None = None,
    available_outer_dimensions_by_group: object | None = None,
    max_container_height_mm: float | None = None,
) -> dict[str, object]:
    """Return fixed cavity layouts plus minimum/final outer envelopes."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    derived = derive_container_plan(project, max_container_height_mm=max_container_height_mm)
    groups = {str(value["id"]): value for value in _mappings(project["container_groups"])}
    proposals = _proposal_mapping(final_outer_dimensions_by_group)
    available_by_group = _proposal_mapping(available_outer_dimensions_by_group)
    unknown = sorted((set(proposals) | set(available_by_group)) - set(groups))
    if unknown:
        raise ExpandableEnvelopeError(
            "Final envelope proposals reference unknown container groups: " + ", ".join(unknown) + "."
        )

    contracts: list[dict[str, object]] = []
    for container in _mappings(derived["containers"]):
        group_id = str(container["container_group_id"])
        contracts.append(
            _contract_for_container(
                container,
                groups[group_id],
                proposals.get(group_id),
                derived,
                available_by_group.get(group_id),
            )
        )

    blocked = [item for item in contracts if item["status"] == "blocked"]
    ready = [item for item in contracts if item["status"] == "ready"]
    return {
        "schema_version": EXPANDABLE_ENVELOPE_SCHEMA_V1,
        "source": deepcopy(derived["source"]),
        "project_name": project["project_name"],
        "box_limits_mm": deepcopy(derived["box_limits_mm"]),
        "containers": contracts,
        "summary": {
            "status": "blocked" if blocked else "ready_for_p56",
            "requested_container_count": len(contracts),
            "ready_container_count": len(ready),
            "blocked_container_count": len(blocked),
            "fixed_cavity_count": sum(len(_values(item["cavity_layout"])) for item in contracts),
            "automatic_body_count": 0,
            "invariant": "fixed_cavity_layout__expandable_outer_envelope",
            "next_step": "P56 may edit and persist this contract; P57 will solve final envelopes jointly.",
        },
        "blockers": [
            {
                "container_group_id": item["container_group_id"],
                "container_name": item["container_name"],
                "message": message,
            }
            for item in blocked
            for message in _values(item["blockers"])
        ],
        "limitations": [
            "This contract validates one container envelope at a time; it does not partition the box.",
            "Final envelope placement and shared external clearances belong to P57.",
            "No CAD, Fusion or print validation is claimed.",
        ],
    }


def _contract_for_container(
    container: dict[str, object],
    group: dict[str, object],
    proposal: object | None,
    derived: dict[str, object],
    available_outer_dimensions: object | None,
) -> dict[str, object]:
    group_id = str(container["container_group_id"])
    expansion_axes = {axis: bool(_mapping(group["expansion_axes"])[axis]) for axis in _AXES}
    locked = _nullable_dimension(group["locked_outer_dimensions_mm"])
    dimension_modes = {axis: str(_mapping(group["dimension_modes"])[axis]) for axis in _AXES}
    target_dimensions = _nullable_dimension(group["target_outer_dimensions_mm"])
    constraints = {
        "expansion_axes": expansion_axes,
        "locked_outer_dimensions_mm": locked,
        "dimension_modes": dimension_modes,
        "target_outer_dimensions_mm": target_dimensions,
        "surplus_preference": group["surplus_preference"],
        "minimum_wall_thickness_mm": container["wall_thickness_mm"],
        "minimum_floor_thickness_mm": container["floor_thickness_mm"],
    }
    base_blockers = [str(value) for value in _values(container["blockers"])]
    if container["outer_dimensions_mm"] is None:
        return {
            "container_group_id": group_id,
            "container_name": container["container_name"],
            "status": "blocked",
            "cavity_layout": [],
            "minimum_outer_envelope_mm": None,
            "final_outer_envelope_mm": None,
            "minimum_envelope_origin_in_final_mm": None,
            "surplus_distribution_mm": None,
            "constraints": constraints,
            "blockers": base_blockers + [
                "A container without calibrated contents has no expandable minimum envelope."
            ],
            "warnings": deepcopy(container["warnings"]),
        }

    minimum = _dimension(container["outer_dimensions_mm"])
    final = _resolve_final(minimum, locked, proposal, group_id)
    blockers = list(base_blockers)
    limits = _dimension(_mapping(derived["box_limits_mm"])["inner_dimensions_mm"])
    limits["z"] = float(_mapping(derived["box_limits_mm"])["usable_height_mm"])
    if available_outer_dimensions is not None:
        limits = _dimension(available_outer_dimensions)
    for axis in _AXES:
        if locked[axis] is not None and locked[axis] + _EPSILON < minimum[axis]:
            blockers.append(
                f"Locked outer {axis.upper()} dimension {locked[axis]} mm is below the minimum "
                f"{minimum[axis]} mm."
            )
        if final[axis] + _EPSILON < minimum[axis]:
            blockers.append(
                f"Final outer {axis.upper()} dimension {final[axis]} mm is below the minimum "
                f"{minimum[axis]} mm."
            )
        if not expansion_axes[axis] and locked[axis] is None and abs(final[axis] - minimum[axis]) > _EPSILON:
            blockers.append(
                f"Axis {axis.upper()} cannot expand; final dimension must remain {minimum[axis]} mm."
            )
        if locked[axis] is not None and abs(final[axis] - locked[axis]) > _EPSILON:
            blockers.append(
                f"Axis {axis.upper()} is locked to {locked[axis]} mm, not {final[axis]} mm."
            )
        if final[axis] > limits[axis] + _EPSILON:
            blockers.append(
                f"Final outer {axis.upper()} dimension {final[axis]} mm exceeds the available "
                f"{limits[axis]} mm."
            )

    surplus = {axis: _round(max(0.0, final[axis] - minimum[axis])) for axis in _AXES}
    distribution = _surplus_distribution(surplus)
    cavity_layout = [
        {
            "cavity_id": compartment["id"],
            "content_id": compartment["content_id"],
            "shape_kind": compartment["shape_kind"],
            "local_origin_mm": deepcopy(compartment["local_origin_mm"]),
            "inner_dimensions_mm": deepcopy(compartment["inner_dimensions_mm"]),
            "content_clearance_mm": compartment["content_clearance_mm"],
            "quantity": deepcopy(compartment["quantity"]),
        }
        for compartment in _mappings(container["compartments"])
    ]
    return {
        "container_group_id": group_id,
        "container_name": container["container_name"],
        "status": "blocked" if blockers else "ready",
        "cavity_layout": cavity_layout,
        "cavity_layout_frame": "minimum_outer_envelope.local",
        "minimum_outer_envelope_mm": minimum,
        "final_outer_envelope_mm": final,
        "minimum_envelope_origin_in_final_mm": {
            "x": distribution["left"],
            "y": distribution["front"],
            "z": distribution["below"],
        },
        "surplus_distribution_mm": distribution,
        "dimension_resolution": {
            axis: {
                "mode": dimension_modes[axis],
                "minimum_mm": minimum[axis],
                "target_mm": target_dimensions[axis],
                "calculated_mm": final[axis],
                "target_deviation_mm": (
                    _round(final[axis] - float(target_dimensions[axis]))
                    if target_dimensions[axis] is not None else None
                ),
            }
            for axis in _AXES
        },
        "constraints": constraints,
        "invariants": {
            "cavity_dimensions_fixed": True,
            "cavity_local_origins_fixed": True,
            "external_envelope_expansion_only": True,
            "automatic_body_created": False,
        },
        "blockers": blockers,
        "warnings": deepcopy(container["warnings"]),
    }


def _resolve_final(
    minimum: dict[str, float],
    locked: dict[str, float | None],
    proposal: object | None,
    group_id: str,
) -> dict[str, float]:
    if proposal is None:
        return {
            axis: _round(minimum[axis] if locked[axis] is None else float(locked[axis]))
            for axis in _AXES
        }
    raw = _mapping(proposal)
    unknown = sorted(set(raw) - set(_AXES))
    if unknown:
        raise ExpandableEnvelopeError(
            f"Final envelope for '{group_id}' has unknown axes: {', '.join(unknown)}."
        )
    result: dict[str, float] = {}
    for axis in _AXES:
        value = raw.get(axis, locked[axis] if locked[axis] is not None else minimum[axis])
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
            raise ExpandableEnvelopeError(
                f"Final envelope {group_id}.{axis} must be a finite positive number."
            )
        if float(value) <= 0:
            raise ExpandableEnvelopeError(
                f"Final envelope {group_id}.{axis} must be a finite positive number."
            )
        result[axis] = _round(float(value))
    return result


def _proposal_mapping(value: object | None) -> dict[str, object]:
    if value is None:
        return {}
    raw = _mapping(value)
    return {str(key): proposal for key, proposal in raw.items()}


def _surplus_distribution(surplus: dict[str, float]) -> dict[str, float]:
    # The minimum-envelope frame and all cavity-local coordinates stay frozen.
    # XY surplus is balanced around that frame; Z surplus becomes material below it.
    left = _round(surplus["x"] / 2.0)
    front = _round(surplus["y"] / 2.0)
    return {
        "left": left,
        "right": _round(surplus["x"] - left),
        "front": front,
        "back": _round(surplus["y"] - front),
        "below": surplus["z"],
        "above": 0.0,
    }


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ExpandableEnvelopeError("Envelope contract values must be objects.")
    return value


def _mappings(value: object) -> list[dict[str, object]]:
    return [_mapping(item) for item in _values(value)]


def _values(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ExpandableEnvelopeError("Envelope contract collections must be lists.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: _round(float(raw[axis])) for axis in _AXES}


def _nullable_dimension(value: object) -> dict[str, float | None]:
    raw = _mapping(value)
    return {
        axis: None if raw[axis] is None else _round(float(raw[axis]))
        for axis in _AXES
    }


def _round(value: float) -> float:
    return round(float(value), 4)
