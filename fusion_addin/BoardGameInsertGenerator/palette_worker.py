"""Bounded pure worker queue for long palette calculations.

The worker receives only copied JSON data and string paths.  Fusion polls the
registry from its authorised callback thread and remains the sole publisher of
HTML or CAD side effects.
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ASYNC_PROJECT_ACTIONS = frozenset({"solve_project", "finalize_project"})
POLL_PROJECT_OPERATION_ACTION = "poll_project_operation"
ASYNC_EXECUTION_SCHEMA = "bgig.palette.async_execution.v1"
_MAX_RETAINED_JOBS = 16

PaletteHandler = Callable[[object, str | Path, str | Path | None], dict[str, object]]


@dataclass
class _ProjectJob:
    operation_id: str
    action: str
    source_revision: int | None
    input_digest: str
    request: dict[str, object]
    addin_dir: str
    project_root: str | None
    handler: PaletteHandler | None
    response: dict[str, object] | None = None
    done: bool = False


_LOCK = threading.Lock()
_JOBS: OrderedDict[str, _ProjectJob] = OrderedDict()
_ACTIVE_ACTIONS: dict[str, str] = {}
_ASYNC_LANE = "pure_calculation_core"


def is_async_project_action(action: object) -> bool:
    """Return whether this pure bridge action belongs on the worker."""

    return isinstance(action, str) and action in ASYNC_PROJECT_ACTIONS


def submit_project_operation(
    raw_request: object,
    addin_dir: str | Path,
    project_root: str | Path | None,
    *,
    handler: PaletteHandler | None = None,
) -> dict[str, object] | None:
    """Start one bounded worker job or return an immediate fail-closed response."""

    request = _request_mapping(raw_request)
    operation_id = _required_text(request.get("request_id"), "request_id")
    action = _required_text(request.get("action"), "action")
    if action not in ASYNC_PROJECT_ACTIONS:
        raise ValueError(f"Action asynchrone non prise en charge : {action}.")
    revision = _revision(request.get("source_revision"))
    job = _ProjectJob(
        operation_id=operation_id,
        action=action,
        source_revision=revision,
        input_digest=_request_input_digest(request),
        request=deepcopy(request),
        addin_dir=str(Path(addin_dir)),
        project_root=None if project_root is None else str(Path(project_root)),
        handler=handler,
    )
    with _LOCK:
        existing = _JOBS.get(operation_id)
        if existing is not None:
            return None
        active_id = _ACTIVE_ACTIONS.get(_ASYNC_LANE)
        if active_id is not None:
            return _busy_response(operation_id, action, active_id)
        _evict_completed_jobs_locked()
        _JOBS[operation_id] = job
        _ACTIVE_ACTIONS[_ASYNC_LANE] = operation_id
    worker = threading.Thread(
        target=_run_project_job,
        args=(job,),
        name=f"bgig-{action}-{operation_id[-12:]}",
        daemon=True,
    )
    worker.start()
    return None


def busy_response_while_project_operation_active(raw_request: object) -> dict[str, object] | None:
    """Reject a concurrent pure bridge mutation instead of racing shared state."""

    request = _request_mapping(raw_request)
    operation_id = _required_text(request.get("request_id"), "request_id")
    action = _required_text(request.get("action"), "action")
    with _LOCK:
        active_id = _ACTIVE_ACTIONS.get(_ASYNC_LANE)
    if active_id is None:
        return None
    return _busy_response(operation_id, action, active_id)

def poll_project_operation(raw_request: object) -> dict[str, object] | None:
    """Return a completed response once, rejecting an outdated input identity."""

    request = _request_mapping(raw_request)
    operation_id = _required_text(request.get("operation_id"), "operation_id")
    with _LOCK:
        job = _JOBS.get(operation_id)
        if job is None:
            return _missing_response(operation_id)
        if not job.done:
            return None
        _JOBS.pop(operation_id, None)
        if _ACTIVE_ACTIONS.get(_ASYNC_LANE) == operation_id:
            _ACTIVE_ACTIONS.pop(_ASYNC_LANE, None)
        response = deepcopy(job.response) if job.response is not None else _worker_failure_response(job)
    current_revision = _revision(request.get("source_revision"))
    current_digest = _request_input_digest(request)
    if current_revision != job.source_revision or current_digest != job.input_digest:
        return _stale_response(job, response, current_revision, current_digest)
    response["async_execution"] = _execution_identity(job, stale=False)
    return response


def _run_project_job(job: _ProjectJob) -> None:
    try:
        handler = job.handler or _pure_palette_handler()
        response = handler(
            deepcopy(job.request),
            job.addin_dir,
            job.project_root,
        )
        if not isinstance(response, dict):
            raise TypeError("Le worker palette doit retourner un objet JSON.")
        completed = deepcopy(response)
        completed["async_execution"] = _execution_identity(job, stale=False)
    except Exception as exc:  # pragma: no cover - boundary defended by focused tests.
        completed = _worker_failure_response(job, exc)
    with _LOCK:
        current = _JOBS.get(job.operation_id)
        if current is job:
            job.response = completed
            job.done = True
            if _ACTIVE_ACTIONS.get(_ASYNC_LANE) == job.operation_id:
                _ACTIVE_ACTIONS.pop(_ASYNC_LANE, None)


def _pure_palette_handler() -> PaletteHandler:
    try:
        from .palette_project import handle_palette_request
    except ImportError:  # pragma: no cover - Fusion may load the add-in as a script.
        from palette_project import handle_palette_request  # type: ignore[no-redef]
    return handle_palette_request


def _execution_identity(job: _ProjectJob, *, stale: bool) -> dict[str, object]:
    return {
        "schema_version": ASYNC_EXECUTION_SCHEMA,
        "operation_id": job.operation_id,
        "action": job.action,
        "source_revision": job.source_revision,
        "input_digest": job.input_digest,
        "worker_pure_data_only": True,
        "fusion_side_effects_in_worker": False,
        "stale": stale,
    }


def _stale_response(
    job: _ProjectJob,
    response: dict[str, object],
    current_revision: int | None,
    current_digest: str,
) -> dict[str, object]:
    stale = dict(response)
    stale["status"] = "stale"
    stale["errors"] = [
        "Le resultat asynchrone a ete rejete : la source courante ne correspond plus a son entree."
    ]
    solver_result = dict(stale.get("solver_result") or {})
    solver_result.update(
        {
            "status": "stale_or_cancelled",
            "stop_reason": "source_identity_changed",
            "request_id": job.operation_id,
            "request_revision": job.source_revision,
        }
    )
    stale["solver_result"] = solver_result
    activity = dict(stale.get("operation_activity") or {})
    if activity:
        activity["status"] = "rejected"
        activity["stop_reason"] = "source_identity_changed"
        stale["operation_activity"] = activity
    identity = _execution_identity(job, stale=True)
    identity["current_source_revision"] = current_revision
    identity["current_input_digest"] = current_digest
    stale["async_execution"] = identity
    return stale


def _busy_response(operation_id: str, action: str, active_id: str) -> dict[str, object]:
    return {
        "schema": "bgig.palette.response.v1",
        "request_id": operation_id,
        "status": "busy",
        "errors": ["Cette operation est deja en cours. BGIG conserve la premiere identite."],
        "async_execution": {
            "schema_version": ASYNC_EXECUTION_SCHEMA,
            "operation_id": operation_id,
            "action": action,
            "conflicting_operation_id": active_id,
            "accepted": False,
        },
    }


def _missing_response(operation_id: str) -> dict[str, object]:
    return {
        "schema": "bgig.palette.response.v1",
        "request_id": operation_id,
        "status": "stale",
        "errors": ["Cette operation asynchrone n est plus disponible."],
        "solver_result": {
            "status": "stale_or_cancelled",
            "stop_reason": "async_operation_missing",
            "request_id": operation_id,
        },
    }


def _worker_failure_response(job: _ProjectJob, exc: Exception | None = None) -> dict[str, object]:
    detail = "Le worker de calcul n a pas produit de reponse."
    if exc is not None:
        detail = f"Le worker de calcul a echoue : {exc}."
    return {
        "schema": "bgig.palette.response.v1",
        "request_id": job.operation_id,
        "status": "bridge_error",
        "errors": [detail],
        "async_execution": _execution_identity(job, stale=False),
    }


def _request_mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("La demande asynchrone doit etre un objet JSON.")
    return value


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} doit etre renseigne.")
    return value.strip()


def _revision(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _request_input_digest(request: dict[str, object]) -> str:
    return _input_digest(
        {
            "project": request.get("project"),
            "solver_settings": request.get("solver_settings"),
            "finishing_effort": request.get("finishing_effort"),
        }
    )

def _input_digest(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _evict_completed_jobs_locked() -> None:
    completed = [operation_id for operation_id, job in _JOBS.items() if job.done]
    while len(_JOBS) >= _MAX_RETAINED_JOBS and completed:
        _JOBS.pop(completed.pop(0), None)