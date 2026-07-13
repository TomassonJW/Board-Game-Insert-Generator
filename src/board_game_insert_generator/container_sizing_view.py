"""Read-only presentation contract for P65 container sizing cards.

The palette must never infer a physical minimum or a proposed envelope itself.
This module combines the normalized project, P55 envelope report and optional
P64 partition into an additive, stable-id keyed view for Conteneurs.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


CONTAINER_SIZING_VIEW_SCHEMA_V1 = "bgig.container_sizing_view.v1"
_AXES = ("x", "y", "z")


class ContainerSizingViewError(ValueError):
    """Raised when a sizing projection would hide an invalid source contract."""


def build_container_sizing_view(
    project: object,
    envelopes: object,
    partition: object | None = None,
) -> dict[str, object]:
    """Project minimum, request and calculated sizes without changing a plan."""

    source = _mapping(project, "project")
    envelope_report = _mapping(envelopes, "envelopes")
    groups = _mappings(source.get("container_groups"), "project.container_groups")
    contents = _mappings(source.get("contents"), "project.contents")
    envelope_by_group = {
        str(item["container_group_id"]): item
        for item in _mappings(envelope_report.get("containers"), "envelopes.containers")
    }
    plan_status, placements, diagnostics, stage_support = _partition_context(partition)
    placement_by_group = {
        str(item["container_group_id"]): item
        for item in placements
        if item.get("role") == "container" and item.get("container_group_id") is not None
    }
    contents_by_group: dict[str, list[dict[str, Any]]] = {}
    for content in contents:
        group_id = str(content.get("container_group_id", ""))
        contents_by_group.setdefault(group_id, []).append(content)

    containers = [
        _container_projection(
            group,
            envelope_by_group.get(str(group["id"])),
            placement_by_group.get(str(group["id"])),
            contents_by_group.get(str(group["id"]), []),
            plan_status,
            diagnostics,
            stage_support,
        )
        for group in groups
    ]
    return {
        "schema_version": CONTAINER_SIZING_VIEW_SCHEMA_V1,
        "project_name": str(source.get("project_name", "")),
        "proposal_status": plan_status,
        "containers": containers,
        "summary": {
            "container_count": len(containers),
            "ready_minimum_count": sum(item["minimum_status"] == "ready" for item in containers),
            "calculated_count": sum(item["calculated_outer_dimensions_mm"] is not None for item in containers),
            "estimation_available": bool(containers) and all(
                item["minimum_status"] == "ready" for item in containers
            ),
            "mutation": "none",
        },
        "invariants": {
            "minimum_owned_by_python": True,
            "calculated_size_owned_by_partition": True,
            "stable_group_ids": True,
            "does_not_mutate_project": True,
            "does_not_materialize_fusion": True,
        },
    }


def _container_projection(
    group: dict[str, Any],
    envelope: dict[str, Any] | None,
    placement: dict[str, Any] | None,
    contents: list[dict[str, Any]],
    plan_status: str,
    diagnostics: list[dict[str, Any]],
    stage_support: dict[str, Any],
) -> dict[str, object]:
    group_id = str(group["id"])
    minimum = deepcopy(envelope.get("minimum_outer_envelope_mm")) if envelope else None
    constraints = _mapping_or_empty(envelope.get("constraints") if envelope else None)
    modes = _mapping_or_empty(constraints.get("dimension_modes"))
    targets = _mapping_or_empty(constraints.get("target_outer_dimensions_mm"))
    locked = _mapping_or_empty(constraints.get("locked_outer_dimensions_mm"))
    dimension_contract = _mapping_or_empty(placement.get("dimension_contract") if placement else None)
    contract_axes = _mapping_or_empty(dimension_contract.get("axes"))
    calculated = deepcopy(placement.get("final_outer_dimensions_mm")) if placement else None
    axis_contracts: dict[str, dict[str, object]] = {}
    for axis in _AXES:
        mode = str(modes.get(axis, _mode_from_group(group, axis)))
        requested = locked.get(axis) if mode == "fixed" else targets.get(axis)
        solved_axis = _mapping_or_empty(contract_axes.get(axis))
        axis_contracts[axis] = {
            "mode": mode,
            "requested_mm": _number_or_none(requested),
            "minimum_mm": _dimension_value(minimum, axis),
            "calculated_mm": _dimension_value(calculated, axis),
            "status": str(solved_axis.get("status", "not_computed")),
            "reason": str(solved_axis.get("reason", _fallback_axis_reason(envelope, plan_status))),
        }

    envelope_status = str(envelope.get("status", "blocked")) if envelope else "blocked"
    blockers = list(envelope.get("blockers", [])) if envelope else ["Conteneur introuvable dans les derives."]
    if placement is not None:
        proposal_status = plan_status
    elif plan_status in {"impossible", "incomplete"}:
        proposal_status = plan_status
    elif envelope_status == "blocked":
        proposal_status = "blocked"
    else:
        proposal_status = "not_computed"
    local_diagnostics = [
        _user_diagnostic(item)
        for item in diagnostics
        if str(item.get("reference_id", "")) == group_id
    ]
    return {
        "container_group_id": group_id,
        "label": str(group.get("name", "Conteneur")),
        "minimum_status": "ready" if envelope_status == "ready" else "blocked",
        "minimum_outer_dimensions_mm": minimum,
        "axis_contracts": axis_contracts,
        "calculated_outer_dimensions_mm": calculated,
        "proposal_status": proposal_status,
        "surplus_distribution_mm": deepcopy(placement.get("surplus_distribution_mm")) if placement else None,
        "stage": {
            "index": int(placement.get("stage_index", 0)) if placement else None,
            "id": str(placement.get("stage_id", "")) if placement else "",
            "bottom_z_mm": _number_or_none(placement.get("stage_bottom_z_mm")) if placement else None,
            "top_z_mm": _number_or_none(placement.get("stage_top_z_mm")) if placement else None,
            "support_status": str(stage_support.get("status", "not_computed")) if placement else "not_computed",
        },
        "content_count": len(contents),
        "content_names": [str(item.get("name", "Element")) for item in contents],
        "cavity_count": len(envelope.get("cavity_layout", [])) if envelope else 0,
        "minimum_wall_thickness_mm": _number_or_none(constraints.get("minimum_wall_thickness_mm")),
        "minimum_floor_thickness_mm": _number_or_none(constraints.get("minimum_floor_thickness_mm")),
        "minimum_message": (
            "Le minimum de ce conteneur doit etre corrige avant estimation."
            if envelope_status != "ready"
            else ""
        ),
        "blockers": [str(item) for item in blockers],
        "diagnostics": local_diagnostics,
    }


def _partition_context(
    partition: object | None,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if partition is None:
        return "not_computed", [], [], {}
    plan = _mapping(partition, "partition")
    summary = _mapping(plan.get("summary"), "partition.summary")
    raw_status = str(summary.get("status", "impossible"))
    status = {
        "constructed": "complete",
        "proposal_with_residuals": "partial",
    }.get(raw_status, raw_status)
    return (
        status,
        _mappings(plan.get("placements"), "partition.placements"),
        _mappings(plan.get("diagnostics"), "partition.diagnostics"),
        _mapping_or_empty(plan.get("stage_support")),
    )


def _mode_from_group(group: dict[str, Any], axis: str) -> str:
    locked = _mapping_or_empty(group.get("locked_outer_dimensions_mm"))
    targets = _mapping_or_empty(group.get("target_outer_dimensions_mm"))
    if locked.get(axis) is not None:
        return "fixed"
    if targets.get(axis) is not None:
        return "target"
    return "auto"


def _fallback_axis_reason(envelope: dict[str, Any] | None, plan_status: str) -> str:
    if plan_status in {"impossible", "incomplete"}:
        return "Le projet ne permet pas encore de calculer cette taille."
    return "Estime les tailles pour obtenir une proposition." if envelope and envelope.get("status") == "ready" else "Corrige le minimum avant estimation."


def _user_diagnostic(value: dict[str, Any]) -> dict[str, str]:
    return {
        "message": str(value.get("message", "Calcul impossible pour ce conteneur.")),
        "action": str(value.get("action", "Corrige les contraintes puis reessaie.")),
    }


def _dimension_value(value: object, axis: str) -> float | None:
    return _number_or_none(_mapping_or_empty(value).get(axis))


def _number_or_none(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContainerSizingViewError("Une dimension de presentation doit etre numerique ou absente.")
    return float(value)


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContainerSizingViewError(f"{field} doit etre un objet.")
    return value


def _mapping_or_empty(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _mappings(value: object, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ContainerSizingViewError(f"{field} doit etre une liste.")
    return [_mapping(item, f"{field}[{index}]") for index, item in enumerate(value)]
