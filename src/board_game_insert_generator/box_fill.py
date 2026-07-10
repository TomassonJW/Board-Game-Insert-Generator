"""Pure validation and analysis for the manual BoxFillPlan V0 contract."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from board_game_insert_generator.models import BoxFillPlan, Dimension3D, Point3D


@dataclass(frozen=True)
class BoxFillIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class AssetCoverage:
    asset_id: str
    declared_quantity: int
    allocated_quantity: int
    unallocated_quantity: int
    over_allocated_quantity: int
    status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "declared_quantity": self.declared_quantity,
            "allocated_quantity": self.allocated_quantity,
            "unallocated_quantity": self.unallocated_quantity,
            "over_allocated_quantity": self.over_allocated_quantity,
            "status": self.status,
        }


@dataclass(frozen=True)
class FreeVolume:
    total_box_volume_mm3: float
    occupied_module_volume_mm3: float
    occupied_reservation_volume_mm3: float
    total_free_volume_mm3: float
    qualification: str
    layer_id: str | None
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "total_box_volume_mm3": self.total_box_volume_mm3,
            "occupied_module_volume_mm3": self.occupied_module_volume_mm3,
            "occupied_reservation_volume_mm3": self.occupied_reservation_volume_mm3,
            "total_free_volume_mm3": self.total_free_volume_mm3,
            "regions": [],
            "qualification": self.qualification,
            "layer_id": self.layer_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class BoxFillAnalysis:
    coverage: tuple[AssetCoverage, ...]
    free_volume: FreeVolume
    issues: tuple[BoxFillIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "coverage": [entry.to_dict() for entry in self.coverage],
            "free_volume": self.free_volume.to_dict(),
            "validation": {
                "status": "valid" if self.valid else "invalid",
                "issue_count": len(self.issues),
                "issues": [
                    {"code": issue.code, "field": issue.field, "message": issue.message}
                    for issue in self.issues
                ],
            },
            "warnings": [],
        }


def analyze_box_fill_plan(plan: BoxFillPlan) -> BoxFillAnalysis:
    issues = tuple(validate_box_fill_plan(plan))
    coverage = _asset_coverage(plan)
    module_volume = sum(_volume(module.size) for module in plan.modules)
    reservation_volume = sum(_volume(reservation.size) for reservation in plan.reservations)
    total_box_volume = (
        plan.box.inner_dimensions.x
        * plan.box.inner_dimensions.y
        * plan.box.usable_height_mm
    )
    free_volume = FreeVolume(
        total_box_volume_mm3=total_box_volume,
        occupied_module_volume_mm3=module_volume,
        occupied_reservation_volume_mm3=reservation_volume,
        total_free_volume_mm3=max(0.0, total_box_volume - module_volume - reservation_volume),
        qualification="aggregate_only",
        layer_id=None,
        reason=(
            "P19 V0 subtracts declared module and reservation volumes only; "
            "it does not yet solve disconnected free regions or usability."
        ),
    )
    return BoxFillAnalysis(coverage=coverage, free_volume=free_volume, issues=issues)


def validate_box_fill_plan(plan: BoxFillPlan) -> list[BoxFillIssue]:
    issues: list[BoxFillIssue] = []
    _validate_ids(plan, issues)
    _validate_layers(plan, issues)
    _validate_volumes(plan, issues)
    _validate_collisions(plan, issues)
    _validate_references(plan, issues)
    _validate_coverage(plan, issues)
    return issues


def _validate_ids(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    seen: dict[str, str] = {}
    families = (
        ("layers", plan.layers),
        ("reservations", plan.reservations),
        ("modules", plan.modules),
        ("compartments", plan.compartments),
        ("access_features", plan.access_features),
    )
    for family, entries in families:
        for index, entry in enumerate(entries):
            field = f"{family}[{index}].id"
            identifier = entry.id
            if not identifier:
                issues.append(_issue("BOX_FILL_EMPTY_ID", field, "BoxFillPlan ids cannot be empty."))
                continue
            previous = seen.get(identifier)
            if previous is not None:
                issues.append(
                    _issue(
                        "BOX_FILL_DUPLICATE_ID",
                        field,
                        f"Id '{identifier}' is already used by {previous}; ids must be unique across the plan.",
                    )
                )
            else:
                seen[identifier] = family


def _validate_layers(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    reservation_ids = {reservation.id for reservation in plan.reservations}
    module_ids = {module.id for module in plan.modules}
    for index, layer in enumerate(plan.layers):
        prefix = f"layers[{index}]"
        if layer.origin_z_mm < 0.0 or layer.height_mm <= 0.0:
            issues.append(_issue("BOX_FILL_LAYER_DIMENSIONS_INVALID", prefix, "Layer origin_z_mm must be non-negative and height_mm must be positive."))
        elif layer.origin_z_mm + layer.height_mm > plan.box.usable_height_mm:
            issues.append(_issue("BOX_FILL_LAYER_OUTSIDE_BOX", prefix, "Layer must stay inside the usable box height."))
        for reservation_id in layer.support_reservation_ids:
            if reservation_id not in reservation_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_RESERVATION", f"{prefix}.support_reservation_ids", f"Layer references unknown reservation '{reservation_id}'."))
        for module_id in layer.module_ids:
            if module_id not in module_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_MODULE", f"{prefix}.module_ids", f"Layer references unknown module '{module_id}'."))


def _validate_volumes(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    for family, entries in (("modules", plan.modules), ("reservations", plan.reservations)):
        for index, entry in enumerate(entries):
            prefix = f"{family}[{index}]"
            if not _positive(entry.size):
                issues.append(_issue("BOX_FILL_VOLUME_DIMENSIONS_INVALID", prefix, "Volume size must be strictly positive on X, Y and Z."))
                continue
            if not _fits_box(entry.origin, entry.size, plan):
                issues.append(_issue("BOX_FILL_VOLUME_OUTSIDE_BOX", prefix, "Volume must stay entirely inside the usable BoxFillPlan volume."))
    layer_ids = {layer.id for layer in plan.layers}
    for family, entries in (("modules", plan.modules), ("reservations", plan.reservations)):
        for index, entry in enumerate(entries):
            if entry.layer_id is not None and entry.layer_id not in layer_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_LAYER", f"{family}[{index}].layer_id", f"Volume references unknown layer '{entry.layer_id}'."))


def _validate_collisions(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    for left, right in combinations(plan.modules, 2):
        if _intersects(left.origin, left.size, right.origin, right.size):
            issues.append(_issue("BOX_FILL_MODULE_COLLISION", "modules", f"Modules '{left.id}' and '{right.id}' overlap."))
    for module in plan.modules:
        for reservation in plan.reservations:
            if _intersects(module.origin, module.size, reservation.origin, reservation.size):
                issues.append(_issue("BOX_FILL_MODULE_RESERVATION_COLLISION", "modules", f"Module '{module.id}' overlaps reservation '{reservation.id}'."))
    for left, right in combinations(plan.reservations, 2):
        if _intersects(left.origin, left.size, right.origin, right.size) and not (left.allow_overlap and right.allow_overlap):
            issues.append(_issue("BOX_FILL_RESERVATION_COLLISION", "reservations", f"Reservations '{left.id}' and '{right.id}' overlap without mutual allow_overlap."))


def _validate_references(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    asset_ids = {asset.id for asset in plan.assets}
    modules = {module.id: module for module in plan.modules}
    compartment_ids = {compartment.id for compartment in plan.compartments}
    feature_ids = {feature.id for feature in plan.access_features}
    for index, module in enumerate(plan.modules):
        prefix = f"modules[{index}]"
        for compartment_id in module.compartment_ids:
            if compartment_id not in compartment_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_COMPARTMENT", f"{prefix}.compartment_ids", f"Module references unknown compartment '{compartment_id}'."))
        for feature_id in module.access_feature_ids:
            if feature_id not in feature_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_ACCESS_FEATURE", f"{prefix}.access_feature_ids", f"Module references unknown access feature '{feature_id}'."))
    for index, allocation in enumerate(plan.allocations):
        prefix = f"allocations[{index}]"
        if allocation.asset_id not in asset_ids:
            issues.append(_issue("BOX_FILL_UNKNOWN_ASSET", f"{prefix}.asset_id", f"Allocation references unknown asset '{allocation.asset_id}'."))
        if allocation.module_id not in modules:
            issues.append(_issue("BOX_FILL_UNKNOWN_MODULE", f"{prefix}.module_id", f"Allocation references unknown module '{allocation.module_id}'."))
        if allocation.quantity <= 0:
            issues.append(_issue("BOX_FILL_ALLOCATION_QUANTITY_INVALID", f"{prefix}.quantity", "Allocation quantity must be a positive integer."))
        if allocation.compartment_id is not None:
            if allocation.compartment_id not in compartment_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_COMPARTMENT", f"{prefix}.compartment_id", f"Allocation references unknown compartment '{allocation.compartment_id}'."))
            elif allocation.module_id in modules and allocation.compartment_id not in modules[allocation.module_id].compartment_ids:
                issues.append(_issue("BOX_FILL_COMPARTMENT_NOT_IN_MODULE", f"{prefix}.compartment_id", f"Compartment '{allocation.compartment_id}' is not attached to module '{allocation.module_id}'."))


def _validate_coverage(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    for coverage in _asset_coverage(plan):
        if coverage.over_allocated_quantity:
            issues.append(_issue("BOX_FILL_ALLOCATION_OVER_CAPACITY", f"assets.{coverage.asset_id}", f"Asset '{coverage.asset_id}' is over-allocated by {coverage.over_allocated_quantity}."))
        elif coverage.unallocated_quantity:
            issues.append(_issue("BOX_FILL_ASSET_UNCOVERED", f"assets.{coverage.asset_id}", f"Asset '{coverage.asset_id}' has {coverage.unallocated_quantity} unallocated item(s)."))


def _asset_coverage(plan: BoxFillPlan) -> tuple[AssetCoverage, ...]:
    allocated: dict[str, int] = {asset.id: 0 for asset in plan.assets}
    for allocation in plan.allocations:
        if allocation.asset_id in allocated:
            allocated[allocation.asset_id] += allocation.quantity
    result: list[AssetCoverage] = []
    for asset in plan.assets:
        declared = asset.quantity.count
        actual = allocated[asset.id]
        if actual > declared:
            status = "over_allocated"
        elif actual == declared:
            status = "covered"
        elif actual == 0:
            status = "uncovered"
        else:
            status = "partial"
        result.append(
            AssetCoverage(
                asset_id=asset.id,
                declared_quantity=declared,
                allocated_quantity=actual,
                unallocated_quantity=max(0, declared - actual),
                over_allocated_quantity=max(0, actual - declared),
                status=status,
            )
        )
    return tuple(result)


def box_fill_plan_to_dict(plan: BoxFillPlan) -> dict[str, object]:
    analysis = analyze_box_fill_plan(plan).to_dict()
    return {
        "schema_version": plan.schema_version,
        "id": plan.id,
        "box": {
            "id": plan.box.id,
            "inner_dimensions_mm": _dimension_to_dict(plan.box.inner_dimensions),
            "origin_mm": _point_to_dict(plan.box.origin),
            "usable_height_mm": plan.box.usable_height_mm,
            "lid_clearance_mm": plan.box.lid_clearance_mm,
            "units": plan.box.units,
            "orientation": plan.box.orientation,
        },
        "assets": [
            {
                "id": asset.id,
                "name": asset.name,
                "kind": asset.kind.value,
                "quantity": asset.quantity.count,
                "dimensions_mm": _dimension_to_dict(asset.dimensions),
            }
            for asset in plan.assets
        ],
        "layers": [
            {
                "id": layer.id,
                "origin_z_mm": layer.origin_z_mm,
                "height_mm": layer.height_mm,
                "role": layer.role,
                "removal_order": layer.removal_order,
                "support_reservation_ids": list(layer.support_reservation_ids),
                "module_ids": list(layer.module_ids),
                "comment": layer.comment,
                "metadata": layer.metadata,
            }
            for layer in plan.layers
        ],
        "reservations": [
            {
                "id": reservation.id,
                "kind": reservation.kind.value,
                "origin_mm": _point_to_dict(reservation.origin),
                "size_mm": _dimension_to_dict(reservation.size),
                "layer_id": reservation.layer_id,
                "removal_order": reservation.removal_order,
                "allow_overlap": reservation.allow_overlap,
                "printable": False,
                "source": reservation.source,
                "comment": reservation.comment,
                "metadata": reservation.metadata,
            }
            for reservation in plan.reservations
        ],
        "modules": [
            {
                "id": module.id,
                "name": module.name,
                "origin_mm": _point_to_dict(module.origin),
                "size_mm": _dimension_to_dict(module.size),
                "orientation": module.orientation,
                "locked": module.locked,
                "manual": module.manual,
                "printable": module.printable,
                "layer_id": module.layer_id,
                "source": module.source,
                "compartment_ids": list(module.compartment_ids),
                "access_feature_ids": list(module.access_feature_ids),
                "comment": module.comment,
                "metadata": module.metadata,
            }
            for module in plan.modules
        ],
        "allocations": [
            {
                "asset_id": allocation.asset_id,
                "quantity": allocation.quantity,
                "module_id": allocation.module_id,
                "compartment_id": allocation.compartment_id,
                "source": allocation.source,
                "intent": allocation.intent,
                "coverage_status": allocation.coverage_status,
            }
            for allocation in plan.allocations
        ],
        "compartments": [
            {
                "id": compartment.id,
                "functional_type": compartment.functional_type.value,
                "origin_mm": _point_to_dict(compartment.origin),
                "size_mm": _dimension_to_dict(compartment.size),
                "clearance_mm": compartment.clearance_mm,
                "clearance_source": compartment.clearance_source,
                "comment": compartment.comment,
            }
            for compartment in plan.compartments
        ],
        "access_features": [
            {
                "id": feature.id,
                "kind": feature.kind.value,
                "placement": feature.placement,
                "position_mm": _point_to_dict(feature.position),
                "size_mm": _dimension_to_dict(feature.size) if feature.size is not None else None,
                "radius_mm": feature.radius_mm,
                "taxonomy": feature.taxonomy.value if feature.taxonomy is not None else None,
                "comment": feature.comment,
            }
            for feature in plan.access_features
        ],
        "coverage": analysis["coverage"],
        "free_volumes": [analysis["free_volume"]],
        "validation": analysis["validation"],
        "warnings": analysis["warnings"],
        "metadata": plan.metadata,
    }


def _point_to_dict(point: Point3D) -> dict[str, float]:
    return {"x": point.x, "y": point.y, "z": point.z}


def _dimension_to_dict(dimension: Dimension3D | None) -> dict[str, float] | None:
    if dimension is None:
        return None
    return {"x": dimension.x, "y": dimension.y, "z": dimension.z}
def _positive(size: Dimension3D) -> bool:
    return size.x > 0.0 and size.y > 0.0 and size.z > 0.0


def _fits_box(origin: Point3D, size: Dimension3D, plan: BoxFillPlan) -> bool:
    box = plan.box
    return (
        origin.x >= box.origin.x
        and origin.y >= box.origin.y
        and origin.z >= box.origin.z
        and origin.x + size.x <= box.origin.x + box.inner_dimensions.x
        and origin.y + size.y <= box.origin.y + box.inner_dimensions.y
        and origin.z + size.z <= box.origin.z + box.usable_height_mm
    )


def _intersects(left_origin: Point3D, left_size: Dimension3D, right_origin: Point3D, right_size: Dimension3D) -> bool:
    return (
        left_origin.x < right_origin.x + right_size.x
        and right_origin.x < left_origin.x + left_size.x
        and left_origin.y < right_origin.y + right_size.y
        and right_origin.y < left_origin.y + left_size.y
        and left_origin.z < right_origin.z + right_size.z
        and right_origin.z < left_origin.z + left_size.z
    )


def _volume(size: Dimension3D) -> float:
    return size.x * size.y * size.z


def _issue(code: str, field: str, message: str) -> BoxFillIssue:
    return BoxFillIssue(code=code, field=field, message=message)