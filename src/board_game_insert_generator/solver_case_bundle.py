"""Capture pure et versionnée d'un cas solveur P64-L05B.

Le bundle est un artefact local de diagnostic. Sa construction ne lance aucune
analyse, recherche, finalisation, CAD ou matérialisation.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Mapping, Sequence

from board_game_insert_generator.container_internal_variants import (
    ContainerInternalVariant,
    ContainerVariantFrontier,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import normalize_project_draft


SOLVER_CASE_BUNDLE_SCHEMA_V1 = "bgig.solver_case_bundle.v1"
SOLVER_CASE_EVENT_TRACE_SCHEMA_V1 = "bgig.solver_case_event_trace.v1"
SOLVER_CASE_PRODUCER_ID = "solver_case_capture_v1"
SOLVER_CASE_PRODUCER_VERSION = "1"
MAX_INTERACTION_EVENTS = 256
_MAX_TEXT_LENGTH = 256
_SECRET_KEY_FRAGMENTS = (
    "api_key",
    "authorization",
    "password",
    "secret",
    "token",
)
_EVENT_TEXT_FIELDS = ("event_type", "action", "ui_field", "object_id")
_EVENT_INT_FIELDS = ("sequence", "source_revision", "elapsed_ms")
_SCENE_IDENTITY_FIELDS = (
    "schema_version",
    "artifact_kind",
    "artifact_digest",
    "partition_plan_digest",
    "cad_ir_digest",
    "source_revision",
)


def build_solver_case_bundle(
    raw_project: object,
    *,
    solver_settings: Mapping[str, object],
    solver_case_state: Mapping[str, object],
    local_analysis: Mapping[str, object],
    container_frontiers: Sequence[ContainerVariantFrontier],
    interaction_events: object,
    client_context: Mapping[str, object] | None,
    capture_id: str,
    captured_at_ms: int,
    source_revision: int,
) -> dict[str, object]:
    """Construire un bundle déterministe pour des entrées déjà observées."""

    identifier = _bounded_text(capture_id, "capture_id")
    capture_time = _non_negative_int(captured_at_ms, "captured_at_ms")
    revision = _non_negative_int(source_revision, "source_revision")
    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    events, discarded = _interaction_events(interaction_events)
    frontiers = tuple(
        sorted(container_frontiers, key=lambda value: value.container_group_id)
    )
    frontier_payload = [_frontier_payload(value) for value in frontiers]
    state_payload = deepcopy(dict(solver_case_state))
    analysis_payload = deepcopy(dict(local_analysis))
    context_payload = _client_context(client_context or {})
    settings_payload = {
        "method": _bounded_text(
            solver_settings.get("method", "auto"),
            "solver_settings.method",
        ),
        "effort": _bounded_text(
            solver_settings.get("effort", "normal"),
            "solver_settings.effort",
        ),
    }
    project_digest = canonical_digest(project)
    state_digest = canonical_digest(state_payload)
    analysis_digest = canonical_digest(analysis_payload)
    frontier_digest = canonical_digest(frontier_payload)
    trace_payload = {
        "schema_version": SOLVER_CASE_EVENT_TRACE_SCHEMA_V1,
        "event_count": len(events),
        "discarded_event_count": discarded,
        "events": events,
    }
    trace_digest = canonical_digest(trace_payload)
    observed_partition = state_payload.get("observed_partition")
    has_observed_partition = isinstance(observed_partition, Mapping)
    has_certified_plan = bool(
        isinstance(observed_partition, Mapping)
        and isinstance(observed_partition.get("minimal_layout"), Mapping)
        and observed_partition["minimal_layout"]
        .get("global_certificate", {})
        .get("certified")
        is True
    )
    bundle: dict[str, object] = {
        "schema_version": SOLVER_CASE_BUNDLE_SCHEMA_V1,
        "capture": {
            "capture_id": identifier,
            "captured_at_ms": capture_time,
            "source_revision": revision,
            "producer_id": SOLVER_CASE_PRODUCER_ID,
            "producer_version": SOLVER_CASE_PRODUCER_VERSION,
        },
        "project": deepcopy(project),
        "project_normalization": {
            "source_schema": normalization.source_schema,
            "migrated": normalization.migrated,
        },
        "solver_settings": settings_payload,
        "solver_case_state": state_payload,
        "local_analysis": analysis_payload,
        "container_variant_frontiers": frontier_payload,
        "interaction_trace": trace_payload,
        "client_context": context_payload,
        "digests": {
            "project_digest": project_digest,
            "solver_case_state_digest": state_digest,
            "local_analysis_digest": analysis_digest,
            "container_frontiers_digest": frontier_digest,
            "interaction_trace_digest": trace_digest,
        },
        "summary": {
            "container_group_count": len(project["container_groups"]),
            "content_count": len(project["contents"]),
            "frontier_count": len(frontier_payload),
            "event_count": len(events),
            "has_observed_partition": has_observed_partition,
            "has_certified_plan": has_certified_plan,
            "solver_result_status": _nested_text(
                state_payload,
                ("staged_calculation", "minimal_layout", "solver_result_status"),
            ),
            "stop_reason": _nested_text(
                state_payload,
                ("staged_calculation", "minimal_layout", "stop_reason"),
            ),
        },
        "invariants": {
            "capture_is_explicit": True,
            "global_solver_invocation_count": 0,
            "finalization_invocation_count": 0,
            "cad_build_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
            "interaction_values_captured": False,
            "document_paths_captured": False,
            "automatic_solver_modification": False,
        },
    }
    _reject_secret_keys(bundle)
    bundle["bundle_digest"] = canonical_digest(bundle)
    return bundle


def solver_case_capture_summary(
    bundle: Mapping[str, object],
) -> dict[str, object]:
    """Retour bridge compact ; le bundle complet reste dans le fichier local."""

    capture = bundle.get("capture")
    summary = bundle.get("summary")
    if not isinstance(capture, Mapping) or not isinstance(summary, Mapping):
        raise TypeError("Solver case bundle summary requires a valid bundle.")
    return {
        "schema_version": SOLVER_CASE_BUNDLE_SCHEMA_V1,
        "capture_id": str(capture.get("capture_id", "")),
        "bundle_digest": str(bundle.get("bundle_digest", "")),
        "event_count": int(summary.get("event_count", 0)),
        "has_observed_partition": bool(
            summary.get("has_observed_partition", False)
        ),
        "has_certified_plan": bool(summary.get("has_certified_plan", False)),
        "solver_result_status": str(summary.get("solver_result_status", "")),
        "stop_reason": str(summary.get("stop_reason", "")),
        "automatic_solver_modification": False,
    }


def _frontier_payload(
    frontier: ContainerVariantFrontier,
) -> dict[str, object]:
    return {
        "container_group_id": frontier.container_group_id,
        "budget": frontier.budget.to_dict(),
        "counts": {
            "generated": frontier.generated_count,
            "raw_layout": frontier.raw_layout_count,
            "certified": frontier.certified_count,
            "duplicates": frontier.duplicate_count,
            "dominated": frontier.dominated_count,
            "retained": len(frontier.variants),
        },
        "limits": {
            "generation_limit_reached": frontier.generation_limit_reached,
            "certification_limit_reached": frontier.certification_limit_reached,
            "retention_limit_reached": frontier.retention_limit_reached,
        },
        "generated_digests": list(frontier.generated_digests),
        "certified_digests": list(frontier.certified_digests),
        "variants": [
            _variant_payload(value)
            for value in sorted(
                frontier.variants,
                key=lambda value: (value.variant_id, value.geometry_digest),
            )
        ],
        "rejected": [
            {
                "variant_id": value.variant.variant_id,
                "geometry_digest": value.variant.geometry_digest,
                "rejection_codes": list(value.rejection_codes),
            }
            for value in frontier.rejected
        ],
    }


def _variant_payload(
    variant: ContainerInternalVariant,
) -> dict[str, object]:
    draft = variant.draft
    return {
        "variant_id": variant.variant_id,
        "geometry_digest": variant.geometry_digest,
        "canonical": variant.canonical,
        "minimum_outer_envelope_mm": list(draft.minimum_outer_envelope_mm),
        "wall_thickness_mm": draft.wall_thickness_mm,
        "floor_thickness_mm": draft.floor_thickness_mm,
        "cavity_layout_frame": draft.cavity_layout_frame,
        "row_count": draft.row_count,
        "internal_separator_count": draft.internal_separator_count,
        "generation_index": draft.generation_index,
        "provenance": [
            {
                "producer_id": value.producer_id,
                "producer_version": value.producer_version,
                "generation_path": value.generation_path,
            }
            for value in variant.provenance
        ],
        "cavities": [value.geometry_payload() for value in draft.cavities],
        "local_cost": asdict(variant.local_cost),
        "local_certificate": {
            "schema_version": variant.local_certificate.schema_version,
            "geometry_digest": variant.local_certificate.geometry_digest,
            "certified": variant.local_certificate.certified,
            "checks": [
                {
                    "name": value.name,
                    "passed": value.passed,
                    "rejection_code": value.rejection_code,
                }
                for value in variant.local_certificate.checks
            ],
        },
    }


def _interaction_events(
    value: object,
) -> tuple[list[dict[str, object]], int]:
    if value is None:
        return [], 0
    if not isinstance(value, list):
        raise TypeError("interaction_events must be a list.")
    discarded = max(0, len(value) - MAX_INTERACTION_EVENTS)
    selected = value[-MAX_INTERACTION_EVENTS:]
    events: list[dict[str, object]] = []
    for index, raw in enumerate(selected):
        if not isinstance(raw, Mapping):
            raise TypeError(f"interaction_events[{index}] must be an object.")
        event: dict[str, object] = {}
        for field in _EVENT_TEXT_FIELDS:
            if field in raw and raw[field] not in (None, ""):
                event[field] = _bounded_text(
                    raw[field],
                    f"interaction_events[{index}].{field}",
                )
        for field in _EVENT_INT_FIELDS:
            if field in raw:
                event[field] = _non_negative_int(
                    raw[field],
                    f"interaction_events[{index}].{field}",
                )
        if "event_type" not in event:
            raise ValueError(
                f"interaction_events[{index}].event_type is required."
            )
        events.append(event)
    return events, discarded


def _client_context(
    value: Mapping[str, object],
) -> dict[str, object]:
    result: dict[str, object] = {
        "scene_present": bool(value.get("scene_present", False)),
        "dirty": bool(value.get("dirty", False)),
        "solved_stale": bool(value.get("solved_stale", False)),
    }
    identity = value.get("scene_artifact_identity")
    if isinstance(identity, Mapping):
        result["scene_artifact_identity"] = {
            key: deepcopy(identity[key])
            for key in _SCENE_IDENTITY_FIELDS
            if key in identity
            and isinstance(identity[key], (str, int, float, bool))
        }
    else:
        result["scene_artifact_identity"] = None
    return result


def _nested_text(
    value: Mapping[str, object],
    path: tuple[str, ...],
) -> str:
    current: object = value
    for key in path:
        if not isinstance(current, Mapping):
            return ""
        current = current.get(key)
    return str(current) if current not in (None, "") else ""


def _reject_secret_keys(value: object, path: str = "bundle") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(fragment in normalized for fragment in _SECRET_KEY_FRAGMENTS):
                raise ValueError(f"Secret-like field rejected at {path}.{key}.")
            _reject_secret_keys(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_secret_keys(item, f"{path}[{index}]")


def _bounded_text(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be text.")
    text = value.strip()
    if not text:
        raise ValueError(f"{field} must not be empty.")
    if len(text) > _MAX_TEXT_LENGTH:
        raise ValueError(f"{field} exceeds {_MAX_TEXT_LENGTH} characters.")
    return text


def _non_negative_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise TypeError(f"{field} must be a non-negative integer.")
    return value
