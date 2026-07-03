"""Testable helpers for the Fusion 360 adapter skeleton.

This module intentionally imports no Fusion 360 API. The add-in entry point can
use these helpers from inside Fusion, while unit tests can exercise the same
boundary checks in normal Python.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_CAD_IR_SCHEMA_VERSION = "cad_ir.v0"
SUPPORTED_UNITS = "mm"

DOCUMENT_STATUS_READY = "ready"
DOCUMENT_STATUS_ZERO_DOC = "zero_doc"

PLAN_STATUS_PLANNED_ONLY = "planned_only"


class FusionSkeletonError(ValueError):
    """Raised when a CAD IR payload cannot be consumed by the skeleton."""


@dataclass(frozen=True)
class FusionDocumentState:
    """Small document-state record independent from Fusion API classes."""

    status: str
    message: str
    document_name: str | None = None


@dataclass(frozen=True)
class FusionOperationPlan:
    """Non-executable plan item derived from one CAD IR operation."""

    component_id: str
    body_id: str
    operation_id: str
    operation_kind: str
    execution_status: str = PLAN_STATUS_PLANNED_ONLY
    reason: str = (
        "P4-M002 records the future Fusion operation intent only; "
        "no geometry is created."
    )

    def to_dict(self) -> dict[str, str]:
        return {
            "component_id": self.component_id,
            "body_id": self.body_id,
            "operation_id": self.operation_id,
            "operation_kind": self.operation_kind,
            "execution_status": self.execution_status,
            "reason": self.reason,
        }


def describe_document_state(application: Any) -> FusionDocumentState:
    """Return a serializable status for Fusion's active document state.

    ``application`` is duck-typed so tests can pass small fake objects. In
    Fusion's "Zero Doc" state, ``activeDocument`` is absent or ``None``.
    """

    if application is None:
        return FusionDocumentState(
            status=DOCUMENT_STATUS_ZERO_DOC,
            message=(
                "Fusion application is unavailable. Open Fusion 360 with a "
                "design document before future generation."
            ),
        )

    active_document = getattr(application, "activeDocument", None)
    if active_document is None:
        return FusionDocumentState(
            status=DOCUMENT_STATUS_ZERO_DOC,
            message=(
                "No active Fusion document. Create or open a design document "
                "before future geometry generation."
            ),
        )

    document_name = (
        getattr(active_document, "name", None)
        or getattr(active_document, "title", None)
        or None
    )
    return FusionDocumentState(
        status=DOCUMENT_STATUS_READY,
        message=(
            "Active Fusion document detected. P4-M002 still does not create "
            "geometry."
        ),
        document_name=document_name,
    )


def load_cad_ir_json(path: str | Path) -> dict[str, Any]:
    """Load and validate a serialized CAD IR payload from JSON."""

    source_path = Path(path)
    try:
        raw_payload = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FusionSkeletonError(
            f"Invalid CAD IR JSON in {source_path}: {exc.msg}."
        ) from exc

    return validate_cad_ir_payload(raw_payload)


def validate_cad_ir_payload(payload: Any) -> dict[str, Any]:
    """Validate the minimum CAD IR contract consumed by the skeleton."""

    if not isinstance(payload, dict):
        raise FusionSkeletonError("CAD IR payload must be a JSON object.")

    schema_version = payload.get("schema_version")
    if schema_version != SUPPORTED_CAD_IR_SCHEMA_VERSION:
        raise FusionSkeletonError(
            "Unsupported CAD IR schema_version "
            f"{schema_version!r}; expected {SUPPORTED_CAD_IR_SCHEMA_VERSION!r}."
        )

    units = payload.get("units")
    if units != SUPPORTED_UNITS:
        raise FusionSkeletonError(
            f"Unsupported CAD IR units {units!r}; expected {SUPPORTED_UNITS!r}."
        )

    components = payload.get("components")
    if not isinstance(components, list):
        raise FusionSkeletonError("CAD IR payload must contain a components list.")

    return payload


def planned_operations_from_cad_ir(payload: Any) -> tuple[FusionOperationPlan, ...]:
    """Convert CAD IR operations into a non-executable Fusion plan.

    This is deliberately a planning layer only. P4-M002 must not create
    components, bodies, sketches, extrusions, or exports.
    """

    validated_payload = validate_cad_ir_payload(payload)
    planned_operations: list[FusionOperationPlan] = []

    for component in validated_payload["components"]:
        if not isinstance(component, dict):
            raise FusionSkeletonError("Each CAD IR component must be an object.")

        component_id = _required_text(component, "id", "component")
        body = component.get("body")
        if not isinstance(body, dict):
            raise FusionSkeletonError(
                f"CAD IR component {component_id!r} must contain a body object."
            )

        body_id = _required_text(body, "id", f"component {component_id} body")
        operations = body.get("operations", [])
        if not isinstance(operations, list):
            raise FusionSkeletonError(
                f"CAD IR body {body_id!r} operations must be a list."
            )

        for operation in operations:
            if not isinstance(operation, dict):
                raise FusionSkeletonError(
                    f"CAD IR body {body_id!r} operation must be an object."
                )
            planned_operations.append(
                FusionOperationPlan(
                    component_id=component_id,
                    body_id=body_id,
                    operation_id=_required_text(
                        operation,
                        "id",
                        f"body {body_id} operation",
                    ),
                    operation_kind=_required_text(
                        operation,
                        "kind",
                        f"body {body_id} operation",
                    ),
                )
            )

    return tuple(planned_operations)


def _required_text(source: dict[str, Any], key: str, label: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise FusionSkeletonError(f"CAD IR {label} must contain a non-empty {key}.")
    return value
