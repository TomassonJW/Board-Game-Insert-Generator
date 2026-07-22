"""Persistent certified minimal-plan witness for P64-L05C.

A witness is not a cache hit and never bypasses certification. It preserves one
already-certified partition under exact project and P45 frontier dependencies so
the solver can recertify it as an incumbent while continuing its normal lanes.
"""

from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Mapping, Sequence

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_outcome import SOLUTION_FOUND


CERTIFIED_PLAN_WITNESS_SCHEMA_V1 = "bgig.certified_plan_witness.v1"
CERTIFIED_PLAN_WITNESS_PRODUCER_ID = "certified_minimal_plan_witness_v1"
CERTIFIED_PLAN_WITNESS_PRODUCER_VERSION = "1"
WITNESS_ACCEPTED = "accepted"
WITNESS_REJECTED = "rejected"
WITNESS_NOT_AVAILABLE = "not_available"


def certified_plan_witness_identity(
    raw_project: object,
    frontier_digests: Sequence[tuple[str, str]],
) -> dict[str, object]:
    """Build the effort-agnostic exact dependency identity for a witness."""

    project = normalize_project_draft(raw_project).project
    ordered = _ordered_frontier_digests(frontier_digests)
    frontier_payload = [
        {"container_group_id": group_id, "digest": digest} for group_id, digest in ordered
    ]
    project_digest = canonical_digest(project)
    frontier_set_digest = canonical_digest(frontier_payload)
    return {
        "project_digest": project_digest,
        "frontier_set_digest": frontier_set_digest,
        "frontier_digests": frontier_payload,
        "compatibility_digest": canonical_digest(
            {
                "project_digest": project_digest,
                "frontier_set_digest": frontier_set_digest,
            }
        ),
    }


def build_certified_plan_witness(
    raw_project: object,
    partition: Mapping[str, object],
    *,
    frontier_digests: Sequence[tuple[str, str]],
) -> dict[str, object]:
    """Freeze one certified partition without trusting it as future proof."""

    plan = deepcopy(dict(partition))
    if not is_certified_minimal_partition(plan):
        raise ValueError("A witness requires a certified minimal partition.")
    plan_digest = _required_digest(plan.get("plan_digest"), "partition.plan_digest")
    placement_geometry_digest = canonical_digest(plan.get("placements", []))
    identity = certified_plan_witness_identity(raw_project, frontier_digests)
    solver = _mapping(plan.get("solver"))
    strategy = _mapping(solver.get("strategy"))
    minimal = _mapping(plan.get("minimal_layout"))
    provenance = _mapping(minimal.get("search_provenance"))
    witness: dict[str, object] = {
        "schema_version": CERTIFIED_PLAN_WITNESS_SCHEMA_V1,
        "producer": {
            "id": CERTIFIED_PLAN_WITNESS_PRODUCER_ID,
            "version": CERTIFIED_PLAN_WITNESS_PRODUCER_VERSION,
        },
        "identity": identity,
        "source": {
            "plan_digest": plan_digest,
            "placement_geometry_digest": placement_geometry_digest,
            "rank_axes": list(certified_plan_witness_rank_axes(plan)),
            "solver_family_id": str(strategy.get("family_id", "")),
            "solver_version": str(strategy.get("version", "")),
            "effort_profile": str(provenance.get("effort_profile", "")),
            "placement_certificate_schema": str(
                _mapping(minimal.get("global_certificate")).get("schema_version", "")
            ),
        },
        "partition": plan,
        "invariants": {
            "source_partition_certified": True,
            "effort_profile_is_not_a_compatibility_key": True,
            "solver_method_is_not_a_compatibility_key": True,
            "future_recertification_required": True,
            "search_must_continue": True,
            "cache_hit_claimed": False,
            "finalization_invocation_count": 0,
            "cad_build_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
        },
    }
    witness["witness_digest"] = canonical_digest(witness)
    return witness


def validate_certified_plan_witness(
    witness: object,
    raw_project: object,
    *,
    frontier_digests: Sequence[tuple[str, str]],
) -> dict[str, object]:
    """Validate stored identity and flags; the solver must still recertify."""

    current_identity = certified_plan_witness_identity(
        raw_project,
        frontier_digests,
    )
    if not isinstance(witness, Mapping):
        return _rejection("witness_is_not_an_object", current_identity)
    payload = deepcopy(dict(witness))
    if payload.get("schema_version") != CERTIFIED_PLAN_WITNESS_SCHEMA_V1:
        return _rejection("unsupported_witness_schema", current_identity)
    supplied_digest = payload.pop("witness_digest", None)
    if not isinstance(supplied_digest, str) or len(supplied_digest) != 64:
        return _rejection("missing_witness_digest", current_identity)
    if canonical_digest(payload) != supplied_digest:
        return _rejection("witness_digest_mismatch", current_identity)
    identity = _mapping(payload.get("identity"))
    if identity != current_identity:
        return _rejection("witness_dependencies_changed", current_identity)
    partition = payload.get("partition")
    if not isinstance(partition, Mapping):
        return _rejection("witness_partition_missing", current_identity)
    plan = deepcopy(dict(partition))
    if not is_certified_minimal_partition(plan):
        return _rejection("witness_partition_not_certified", current_identity)
    source = _mapping(payload.get("source"))
    if source.get("plan_digest") != plan.get("plan_digest"):
        return _rejection("witness_plan_digest_mismatch", current_identity)
    if source.get("placement_geometry_digest") != canonical_digest(plan.get("placements", [])):
        return _rejection("witness_placement_digest_mismatch", current_identity)
    if source.get("rank_axes") != list(certified_plan_witness_rank_axes(plan)):
        return _rejection("witness_rank_axes_mismatch", current_identity)
    return {
        "schema_version": CERTIFIED_PLAN_WITNESS_SCHEMA_V1,
        "status": WITNESS_ACCEPTED,
        "stop_reason": "exact_dependencies_and_certificate_flags_match",
        "witness_digest": supplied_digest,
        "compatibility_digest": str(current_identity["compatibility_digest"]),
        "plan_digest": str(plan["plan_digest"]),
        "partition": plan,
        "invariants": {
            "future_recertification_required": True,
            "search_must_continue": True,
            "cache_hit_claimed": False,
        },
    }


def certified_plan_witness_summary(
    result: Mapping[str, object],
) -> dict[str, object]:
    """Return a compact bridge-safe summary without the embedded partition."""

    return {
        "schema_version": CERTIFIED_PLAN_WITNESS_SCHEMA_V1,
        "status": str(result.get("status", WITNESS_NOT_AVAILABLE)),
        "stop_reason": str(result.get("stop_reason", "not_loaded")),
        "witness_digest": str(result.get("witness_digest", "")),
        "compatibility_digest": str(result.get("compatibility_digest", "")),
        "plan_digest": str(result.get("plan_digest", "")),
        "future_recertification_required": True,
        "search_must_continue": True,
        "cache_hit_claimed": False,
    }


def certified_plan_witness_rank_axes(
    partition: Mapping[str, object],
) -> tuple[float, ...]:
    """Return the shared lexicographic minimal-layout ranking axes."""

    metrics = _mapping(_mapping(partition.get("minimal_layout")).get("metrics"))
    try:
        axes = (
            float(metrics["cluster_volume_mm3"]),
            float(metrics["internal_gap_mm3"]),
            float(metrics["cluster_height_mm"]),
            float(metrics["cluster_footprint_mm2"]),
            float(metrics["residual_fragmentation"]),
            -float(metrics["contact_count"]),
            -float(metrics["minimum_support_ratio"]),
        )
        if not all(isfinite(value) for value in axes):
            raise ValueError("Witness ranking axes must be finite.")
        return axes
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("A witness requires complete finite ranking axes.") from exc


def is_certified_minimal_partition(partition: Mapping[str, object]) -> bool:
    """Recognize the shared minimal-layout certificate contract."""

    summary = _mapping(partition.get("summary"))
    minimal = _mapping(partition.get("minimal_layout"))
    certificate = _mapping(minimal.get("global_certificate"))
    variant_value = minimal.get("container_variant_certificate")
    variant_certified = True
    if isinstance(variant_value, Mapping):
        variant_certified = bool(variant_value.get("certified"))
    solver = _mapping(partition.get("solver"))
    result = _mapping(solver.get("result"))
    plan_digest = partition.get("plan_digest")
    return bool(
        result.get("status") == SOLUTION_FOUND
        and summary.get("status") == "constructed"
        and summary.get("placement_certified") is True
        and minimal.get("artifact_kind") == "minimal_layout"
        and minimal.get("finalization_applied") is False
        and certificate.get("certified") is True
        and variant_certified
        and isinstance(plan_digest, str)
        and len(plan_digest) == 64
    )


def _rejection(
    stop_reason: str,
    current_identity: Mapping[str, object],
) -> dict[str, object]:
    return {
        "schema_version": CERTIFIED_PLAN_WITNESS_SCHEMA_V1,
        "status": WITNESS_REJECTED,
        "stop_reason": stop_reason,
        "witness_digest": "",
        "compatibility_digest": str(current_identity.get("compatibility_digest", "")),
        "plan_digest": "",
        "partition": None,
        "invariants": {
            "future_recertification_required": True,
            "search_must_continue": True,
            "cache_hit_claimed": False,
        },
    }


def _ordered_frontier_digests(
    value: Sequence[tuple[str, str]],
) -> tuple[tuple[str, str], ...]:
    ordered = tuple(sorted((str(group_id), str(digest)) for group_id, digest in value))
    if not ordered:
        raise ValueError("A witness requires current P45 frontier digests.")
    group_ids = [group_id for group_id, _digest in ordered]
    if len(group_ids) != len(set(group_ids)):
        raise ValueError("Witness frontier group ids must be unique.")
    for group_id, digest in ordered:
        if not group_id.strip():
            raise ValueError("Witness frontier group ids must not be empty.")
        _required_digest(digest, f"frontier_digests[{group_id}]")
    return ordered


def _required_digest(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character digest.")
    return value


def _mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}
