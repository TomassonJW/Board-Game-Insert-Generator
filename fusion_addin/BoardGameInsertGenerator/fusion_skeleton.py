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
DEFAULT_CAD_IR_INPUT_FILENAME = "cad_ir_input.json"
CAD_IR_PATH_OVERRIDE_FILENAME = "cad_ir_path.txt"

DOCUMENT_STATUS_READY = "ready"
DOCUMENT_STATUS_ZERO_DOC = "zero_doc"

PLAN_STATUS_PLANNED_ONLY = "planned_only"
FUSION_MANUAL_VALIDATION_REQUIRED = "manual_validation_required"


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


@dataclass(frozen=True)
class FusionVectorMm:
    """3D vector stored in millimeters, matching the CAD IR contract."""

    x: float
    y: float
    z: float

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass(frozen=True)
class FusionSolidPlan:
    """One rectangular solid or reference outline to create in Fusion."""

    cad_id: str
    component_name: str
    body_name: str
    origin_mm: FusionVectorMm
    size_mm: FusionVectorMm
    role: str
    printable: bool
    operation_kind: str
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED

    def to_dict(self) -> dict[str, Any]:
        return {
            "cad_id": self.cad_id,
            "component_name": self.component_name,
            "body_name": self.body_name,
            "origin_mm": self.origin_mm.to_dict(),
            "size_mm": self.size_mm.to_dict(),
            "role": self.role,
            "printable": self.printable,
            "operation_kind": self.operation_kind,
            "validation_status": self.validation_status,
        }


@dataclass(frozen=True)
class FusionGenerationPlan:
    """Pure-Python plan consumed by the Fusion API entry point."""

    project_name: str
    reference_box: FusionSolidPlan
    blanks: tuple[FusionSolidPlan, ...]
    validation_status: str = FUSION_MANUAL_VALIDATION_REQUIRED

    @property
    def created_object_count(self) -> int:
        return 1 + len(self.blanks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "reference_box": self.reference_box.to_dict(),
            "blanks": [blank.to_dict() for blank in self.blanks],
            "validation_status": self.validation_status,
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
            "Active Fusion document detected. Fusion generation still requires "
            "manual validation."
        ),
        document_name=document_name,
    )


def resolve_cad_ir_input_path(
    addin_dir: str | Path,
    default_filename: str = DEFAULT_CAD_IR_INPUT_FILENAME,
    override_filename: str = CAD_IR_PATH_OVERRIDE_FILENAME,
) -> Path:
    """Resolve the CAD IR JSON file consumed by the add-in.

    By default the add-in loads ``cad_ir_input.json`` from its own folder. If a
    ``cad_ir_path.txt`` file exists next to the add-in, the first non-empty,
    non-comment line becomes the input path. Relative override paths are resolved
    from the add-in folder.
    """

    root = Path(addin_dir)
    override_path = root / override_filename
    default_path = root / default_filename

    if not override_path.is_file():
        return default_path

    configured_value = _first_path_value(override_path)
    if configured_value is None:
        raise FusionSkeletonError(
            f"CAD IR path override file is empty: {override_path}. "
            f"Delete it to use {default_filename!r}, or write a CAD IR JSON path."
        )

    configured_path = Path(configured_value).expanduser()
    if not configured_path.is_absolute():
        configured_path = root / configured_path
    configured_path = configured_path.resolve()

    if configured_path.is_dir():
        raise FusionSkeletonError(
            f"Configured CAD IR path points to a directory, not a JSON file: {configured_path}. "
            f"Check {override_path}."
        )
    if not configured_path.is_file():
        raise FusionSkeletonError(
            f"Configured CAD IR JSON file not found: {configured_path}. "
            f"Check {override_path}, or generate one with export-cad-ir."
        )

    return configured_path


def cad_ir_input_guidance(addin_dir: str | Path) -> str:
    """Return short user-facing guidance for Fusion CAD IR loading errors."""

    root = Path(addin_dir)
    return "\n".join(
        [
            "CAD IR input guidance:",
            f"- Default input: {root / DEFAULT_CAD_IR_INPUT_FILENAME}",
            f"- Optional path override: {root / CAD_IR_PATH_OVERRIDE_FILENAME}",
            (
                "- Override format: first non-empty line is an absolute path "
                "or a path relative to the add-in folder."
            ),
            (
                "- Generate from BGIG: python -m board_game_insert_generator "
                "export-cad-ir <config.json> --output <cad_ir_input.json>"
            ),
        ]
    )


def load_cad_ir_json(path: str | Path) -> dict[str, Any]:
    """Load and validate a serialized CAD IR payload from JSON."""

    source_path = Path(path)
    if not source_path.is_file():
        raise FusionSkeletonError(f"CAD IR JSON file not found: {source_path}.")

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

    reference_payload = payload.get("box_reference")
    if not isinstance(reference_payload, dict):
        raise FusionSkeletonError("CAD IR payload must contain a box_reference object.")

    components = payload.get("components")
    if not isinstance(components, list):
        raise FusionSkeletonError("CAD IR payload must contain a components list.")
    if not components:
        raise FusionSkeletonError("CAD IR components list must contain at least one component.")
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise FusionSkeletonError(f"CAD IR components[{index}] must be an object.")

    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise FusionSkeletonError("CAD IR metadata must be an object when present.")

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


def generation_plan_from_cad_ir(payload: Any) -> FusionGenerationPlan:
    """Build the first executable Fusion generation plan from CAD IR.

    The plan only copies resolved CAD IR dimensions. It never computes layout,
    offsets, or tolerances.
    """

    validated_payload = validate_cad_ir_payload(payload)
    metadata = validated_payload.get("metadata", {})
    project_name = (
        metadata.get("project_name")
        if isinstance(metadata, dict) and isinstance(metadata.get("project_name"), str)
        else "BGIG CAD IR scene"
    )
    reference_payload = validated_payload.get("box_reference")
    if not isinstance(reference_payload, dict):
        raise FusionSkeletonError("CAD IR payload must contain a box_reference object.")

    reference_box = FusionSolidPlan(
        cad_id=_required_text(reference_payload, "id", "box_reference"),
        component_name=_fusion_name(
            _optional_text(reference_payload, "name")
            or "BGIG Box Reference - not printable"
        ),
        body_name=_fusion_name(
            f"{_required_text(reference_payload, 'id', 'box_reference')} outline"
        ),
        origin_mm=_vector_from_payload(reference_payload, "origin_mm", "box_reference origin"),
        size_mm=_vector_from_payload(reference_payload, "size_mm", "box_reference size"),
        role="reference_box",
        printable=False,
        operation_kind="create_reference_outline",
    )

    blanks: list[FusionSolidPlan] = []
    for component in validated_payload["components"]:
        if not isinstance(component, dict):
            raise FusionSkeletonError("Each CAD IR component must be an object.")

        component_id = _required_text(component, "id", "component")
        component_name = _fusion_name(
            _optional_text(component, "name") or component_id
        )
        body = component.get("body")
        if not isinstance(body, dict):
            raise FusionSkeletonError(
                f"CAD IR component {component_id!r} must contain a body object."
            )

        body_kind = _required_text(body, "kind", f"component {component_id} body")
        if body_kind != "rectangular_blank":
            raise FusionSkeletonError(
                f"CAD IR body kind {body_kind!r} is not supported by P4-M003."
            )

        operations = body.get("operations")
        if not isinstance(operations, list) or not operations:
            raise FusionSkeletonError(
                f"CAD IR body for component {component_id!r} must contain operations."
            )
        operation = _single_rectangular_prism_operation(operations, component_id)
        body_id = _required_text(body, "id", f"component {component_id} body")
        blanks.append(
            FusionSolidPlan(
                cad_id=body_id,
                component_name=component_name,
                body_name=_fusion_name(_optional_text(body, "name") or body_id),
                origin_mm=_vector_from_payload(
                    body,
                    "printable_origin_mm",
                    f"component {component_id} printable origin",
                ),
                size_mm=_vector_from_payload(
                    body,
                    "printable_size_mm",
                    f"component {component_id} printable size",
                ),
                role="rectangular_blank",
                printable=True,
                operation_kind=_required_text(
                    operation,
                    "kind",
                    f"component {component_id} operation",
                ),
            )
        )

    return FusionGenerationPlan(
        project_name=project_name,
        reference_box=reference_box,
        blanks=tuple(blanks),
    )


def mm_to_cm(value_mm: float) -> float:
    """Convert CAD IR millimeters to Fusion API internal centimeters."""

    return value_mm / 10.0


def _single_rectangular_prism_operation(
    operations: list[Any],
    component_id: str,
) -> dict[str, Any]:
    rectangular_operations = [
        operation
        for operation in operations
        if isinstance(operation, dict)
        and operation.get("kind") == "create_rectangular_prism"
    ]
    if len(rectangular_operations) != 1:
        raise FusionSkeletonError(
            "P4-M003 expects exactly one create_rectangular_prism operation "
            f"for component {component_id!r}."
        )
    return rectangular_operations[0]


def _vector_from_payload(
    source: dict[str, Any],
    key: str,
    label: str,
) -> FusionVectorMm:
    value = source.get(key)
    if not isinstance(value, dict):
        raise FusionSkeletonError(f"CAD IR {label} must be an object.")

    return FusionVectorMm(
        x=_required_number(value, "x", label),
        y=_required_number(value, "y", label),
        z=_required_number(value, "z", label),
    )


def _first_path_value(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            return value.strip('"')
    return None


def _required_number(source: dict[str, Any], key: str, label: str) -> float:
    value = source.get(key)
    if not isinstance(value, (int, float)):
        raise FusionSkeletonError(f"CAD IR {label} must contain numeric {key}.")
    number = float(value)
    if number < 0:
        raise FusionSkeletonError(f"CAD IR {label} {key} must be non-negative.")
    return number


def _optional_text(source: dict[str, Any], key: str) -> str | None:
    value = source.get(key)
    return value if isinstance(value, str) and value else None


def _fusion_name(value: str) -> str:
    return " ".join(value.replace(":", " - ").split())


def _required_text(source: dict[str, Any], key: str, label: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise FusionSkeletonError(f"CAD IR {label} must contain a non-empty {key}.")
    return value
