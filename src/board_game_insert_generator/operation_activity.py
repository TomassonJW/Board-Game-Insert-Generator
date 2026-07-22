"""Pure, deterministic activity state for explicit long-running operations.

The producer deliberately does not measure time itself. Callers provide the
start and observation timestamps so the same inputs always produce the same
state. Activity is derived runtime state: it is never persisted in the project
and it never starts a solver, finalizer, CAD build, or Fusion mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


OPERATION_ACTIVITY_SCHEMA_V1 = "bgig.operation_activity.v1"
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_REJECTED = "rejected"

_ACTION_CONTRACTS: dict[str, tuple[str, str, str]] = {
    "validate_project": (
        "local_analysis",
        "Analyse locale",
        "D\u00e9rivation et certification locales",
    ),
    "solve_project": (
        "minimal_layout_calculation",
        "Calcul de l\u2019agencement minimal",
        "Recherche et certification du plan minimal",
    ),
    "finalize_project": (
        "volume_finalization",
        "Finalisation du volume",
        "Application et certification de la politique de finition",
    ),
    "materialize_project": (
        "fusion_materialization",
        "Mat\u00e9rialisation Fusion",
        "Pr\u00e9paration CAD et synchronisation de la sc\u00e8ne",
    ),
    "regenerate_project": (
        "fusion_materialization",
        "Mise \u00e0 jour de la sc\u00e8ne Fusion",
        "Pr\u00e9paration CAD et remplacement s\u00fbr de la sc\u00e8ne",
    ),
}


class OperationActivityError(ValueError):
    """Raised when an activity identity or lifecycle transition is invalid."""


@dataclass(frozen=True)
class OperationActivityDecision:
    """Result of a pure begin decision against already-active operations."""

    accepted: bool
    activity: dict[str, object]
    stop_reason: str


def supports_operation_activity(action: str) -> bool:
    """Return whether an existing explicit action has an activity contract."""

    return action in _ACTION_CONTRACTS


def begin_operation_activity(
    *,
    action: str,
    operation_id: str,
    source_revision: int | None,
    started_at_ms: int,
    active_activities: Sequence[Mapping[str, object]] = (),
) -> OperationActivityDecision:
    """Create one active state or reject the same semantic operation twice.

    Different operation kinds are intentionally not blocked here. Their own
    domain preconditions remain authoritative in the staged orchestrator.
    """

    operation_kind, label, step_label = _contract(action)
    identifier = _required_text(operation_id, "operation_id")
    started = _non_negative_int(started_at_ms, "started_at_ms")
    revision: int | str = (
        _non_negative_int(source_revision, "source_revision")
        if source_revision is not None
        else "not_applicable"
    )
    conflicting = next(
        (
            value
            for value in active_activities
            if value.get("status") == STATUS_ACTIVE
            and value.get("operation_kind") == operation_kind
        ),
        None,
    )
    if conflicting is not None:
        existing_id = str(conflicting.get("operation_id", ""))
        return OperationActivityDecision(
            accepted=False,
            activity={
                **_base_payload(
                    action=action,
                    operation_id=identifier,
                    operation_kind=operation_kind,
                    label=label,
                    step_label=step_label,
                    source_revision=revision,
                    started_at_ms=started,
                ),
                "status": STATUS_REJECTED,
                "elapsed_ms": 0,
                "stop_reason": "same_operation_already_active",
                "conflicting_operation_id": existing_id,
            },
            stop_reason="same_operation_already_active",
        )
    return OperationActivityDecision(
        accepted=True,
        activity={
            **_base_payload(
                action=action,
                operation_id=identifier,
                operation_kind=operation_kind,
                label=label,
                step_label=step_label,
                source_revision=revision,
                started_at_ms=started,
            ),
            "status": STATUS_ACTIVE,
            "elapsed_ms": 0,
            "stop_reason": "operation_started",
            "conflicting_operation_id": "",
        },
        stop_reason="operation_started",
    )


def observe_operation_activity(
    activity: Mapping[str, object],
    *,
    observed_at_ms: int,
) -> dict[str, object]:
    """Update elapsed time without changing identity, step, or terminality."""

    current = _validated_activity(activity)
    if current["status"] != STATUS_ACTIVE:
        return current
    observed = _non_negative_int(observed_at_ms, "observed_at_ms")
    return {
        **current,
        "elapsed_ms": max(0, observed - int(current["started_at_ms"])),
    }


def finish_operation_activity(
    activity: Mapping[str, object],
    *,
    finished_at_ms: int,
    succeeded: bool,
    stop_reason: str,
) -> dict[str, object]:
    """Produce one terminal state while preserving the exact operation identity."""

    current = _validated_activity(activity)
    if current["status"] != STATUS_ACTIVE:
        raise OperationActivityError("Only an active operation can be finished.")
    finished = _non_negative_int(finished_at_ms, "finished_at_ms")
    reason = _required_text(stop_reason, "stop_reason")
    return {
        **current,
        "status": STATUS_COMPLETED if succeeded else STATUS_FAILED,
        "elapsed_ms": max(0, finished - int(current["started_at_ms"])),
        "stop_reason": reason,
    }


def refresh_terminal_operation_activity(
    activity: Mapping[str, object],
    *,
    observed_at_ms: int,
    stop_reason: str | None = None,
    succeeded: bool | None = None,
) -> dict[str, object]:
    """Refresh elapsed time after adapter work without reopening the lifecycle."""

    current = _validated_activity(activity)
    if current["status"] not in {STATUS_COMPLETED, STATUS_FAILED}:
        raise OperationActivityError("Only a terminal operation can be refreshed.")
    observed = _non_negative_int(observed_at_ms, "observed_at_ms")
    refreshed = {
        **current,
        "elapsed_ms": max(
            int(current.get("elapsed_ms", 0)),
            observed - int(current["started_at_ms"]),
        ),
    }
    if stop_reason is not None:
        refreshed["stop_reason"] = _required_text(stop_reason, "stop_reason")
    if succeeded is not None:
        if not isinstance(succeeded, bool):
            raise OperationActivityError("succeeded must be a boolean or None.")
        refreshed["status"] = STATUS_COMPLETED if succeeded else STATUS_FAILED
    return refreshed


def _base_payload(
    *,
    action: str,
    operation_id: str,
    operation_kind: str,
    label: str,
    step_label: str,
    source_revision: int | str,
    started_at_ms: int,
) -> dict[str, object]:
    return {
        "schema_version": OPERATION_ACTIVITY_SCHEMA_V1,
        "operation_id": operation_id,
        "operation_kind": operation_kind,
        "action": action,
        "label": label,
        "current_step": step_label,
        "source_revision": source_revision,
        "started_at_ms": started_at_ms,
        "cancel_supported": False,
        "invariants": {
            "fake_percentage_exposed": False,
            "eta_claimed": False,
            "same_operation_double_launch_blocked": True,
            "different_operation_kinds_blocked": False,
            "user_cancellation_supported": False,
            "stale_or_cancelled_is_user_cancellation": False,
            "starts_domain_operation": False,
            "persisted_in_project": False,
        },
    }


def _validated_activity(activity: Mapping[str, object]) -> dict[str, object]:
    value = dict(activity)
    if value.get("schema_version") != OPERATION_ACTIVITY_SCHEMA_V1:
        raise OperationActivityError("Unsupported operation activity schema.")
    _required_text(value.get("operation_id"), "operation_id")
    _required_text(value.get("operation_kind"), "operation_kind")
    _required_text(value.get("action"), "action")
    _non_negative_int(value.get("started_at_ms"), "started_at_ms")
    if value.get("status") not in {
        STATUS_ACTIVE,
        STATUS_COMPLETED,
        STATUS_FAILED,
        STATUS_REJECTED,
    }:
        raise OperationActivityError("Unknown operation activity status.")
    return value


def _contract(action: str) -> tuple[str, str, str]:
    try:
        return _ACTION_CONTRACTS[action]
    except KeyError as exc:
        raise OperationActivityError(
            f"Action {action!r} has no operation activity contract."
        ) from exc


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperationActivityError(f"{field} must be a non-empty string.")
    return value.strip()


def _non_negative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise OperationActivityError(f"{field} must be a non-negative integer.")
    return value
