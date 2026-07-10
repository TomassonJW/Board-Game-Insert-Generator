"""Pure validation and analysis for the manual BoxFillPlan V0 contract."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from board_game_insert_generator.models import (
    AssetAllocation,
    BoxFillBox,
    BoxFillLayer,
    BoxFillModule,
    BoxFillPlan,
    Dimension3D,
    Point3D,
)


@dataclass(frozen=True)
class BoxFillIssue:
    code: str
    field: str
    message: str
    severity: str = "blocker"
    category: str = "validation"
    entity_id: str | None = None
    constraint_ref: str = "box_fill_plan.v0"
    corrective_action: str = "Correct the referenced field and validate the plan again."

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "field": self.field,
            "entity_id": self.entity_id,
            "constraint_ref": self.constraint_ref,
            "corrective_action": self.corrective_action,
        }


@dataclass(frozen=True)
class AssetCoverage:
    asset_id: str
    declared_quantity: int
    allocated_quantity: int
    unallocated_quantity: int
    over_allocated_quantity: int
    status: str
    module_ids: tuple[str, ...] = ()
    compartment_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "declared_quantity": self.declared_quantity,
            "allocated_quantity": self.allocated_quantity,
            "unallocated_quantity": self.unallocated_quantity,
            "over_allocated_quantity": self.over_allocated_quantity,
            "status": self.status,
            "module_ids": list(self.module_ids),
            "compartment_ids": list(self.compartment_ids),
        }


@dataclass(frozen=True)
class FreeRegion:
    id: str
    origin: Point3D
    size: Dimension3D
    volume_mm3: float
    layer_id: str | None
    usable_for_module: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "origin_mm": _point_to_dict(self.origin),
            "size_mm": _dimension_to_dict(self.size),
            "volume_mm3": self.volume_mm3,
            "layer_id": self.layer_id,
            "usable_for_module": self.usable_for_module,
            "reason": self.reason,
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
    regions: tuple[FreeRegion, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "total_box_volume_mm3": self.total_box_volume_mm3,
            "occupied_module_volume_mm3": self.occupied_module_volume_mm3,
            "occupied_reservation_volume_mm3": self.occupied_reservation_volume_mm3,
            "total_free_volume_mm3": self.total_free_volume_mm3,
            "regions": [region.to_dict() for region in self.regions],
            "qualification": self.qualification,
            "layer_id": self.layer_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class BoxFillAnalysis:
    coverage: tuple[AssetCoverage, ...]
    free_volume: FreeVolume
    issues: tuple[BoxFillIssue, ...]
    metrics: dict[str, object]

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "blocker" for issue in self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "coverage": [entry.to_dict() for entry in self.coverage],
            "free_volume": self.free_volume.to_dict(),
            "validation": {
                "status": "valid" if self.valid else "invalid",
                "issue_count": len(self.issues),
                "issues": [issue.to_dict() for issue in self.issues],
            },
            "warnings": [issue.to_dict() for issue in self.issues if issue.severity == "warning"],
            "metrics": self.metrics,
        }


def analyze_box_fill_plan(plan: BoxFillPlan) -> BoxFillAnalysis:
    issues = tuple(validate_box_fill_plan(plan))
    coverage = _asset_coverage(plan)
    total_box_volume = plan.box.inner_dimensions.x * plan.box.inner_dimensions.y * plan.box.usable_height_mm
    regions, occupied_module_volume, occupied_reservation_volume = _decompose_free_regions(plan)
    total_free_volume = sum(region.volume_mm3 for region in regions)
    free_volume = FreeVolume(
        total_box_volume_mm3=total_box_volume,
        occupied_module_volume_mm3=occupied_module_volume,
        occupied_reservation_volume_mm3=occupied_reservation_volume,
        total_free_volume_mm3=total_free_volume,
        qualification="exact_aabb_cells_v0",
        layer_id=None,
        reason=(
            "Exact orthogonal free cells are derived from box, module, reservation and layer faces; "
            "they are not an automatic placement proposal."
        ),
        regions=tuple(regions),
    )
    covered_items = sum(min(entry.allocated_quantity, entry.declared_quantity) for entry in coverage)
    total_items = sum(entry.declared_quantity for entry in coverage)
    metrics = {
        "asset_types_count": len(plan.assets),
        "total_item_count": total_items,
        "covered_item_count": covered_items,
        "uncovered_item_count": sum(entry.unallocated_quantity for entry in coverage),
        "coverage_ratio": (covered_items / total_items) if total_items else 1.0,
        "modules_count": len(plan.modules),
        "reservations_count": len(plan.reservations),
        "layers_count": len(plan.layers),
        "total_box_volume_mm3": total_box_volume,
        "occupied_module_volume_mm3": occupied_module_volume,
        "occupied_reservation_volume_mm3": occupied_reservation_volume,
        "occupied_total_volume_mm3": occupied_module_volume + occupied_reservation_volume,
        "total_free_volume_mm3": total_free_volume,
        "occupancy_ratio": ((occupied_module_volume + occupied_reservation_volume) / total_box_volume) if total_box_volume else 0.0,
        "reservation_ratio": (occupied_reservation_volume / total_box_volume) if total_box_volume else 0.0,
        "volumes_by_layer": _volumes_by_layer(plan, regions),
    }
    return BoxFillAnalysis(coverage=coverage, free_volume=free_volume, issues=issues, metrics=metrics)


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
    for family, entries in (
        ("layers", plan.layers),
        ("reservations", plan.reservations),
        ("modules", plan.modules),
        ("compartments", plan.compartments),
        ("access_features", plan.access_features),
    ):
        for index, entry in enumerate(entries):
            field = f"{family}[{index}].id"
            if not entry.id:
                issues.append(_issue("BOX_FILL_EMPTY_ID", field, "BoxFillPlan ids cannot be empty."))
            elif entry.id in seen:
                issues.append(_issue("BOX_FILL_DUPLICATE_ID", field, f"Id '{entry.id}' is already used by {seen[entry.id]}; ids must be unique across the plan.", entity_id=entry.id))
            else:
                seen[entry.id] = family


def _validate_layers(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    reservation_ids = {reservation.id for reservation in plan.reservations}
    module_ids = {module.id for module in plan.modules}
    for index, layer in enumerate(plan.layers):
        prefix = f"layers[{index}]"
        if layer.origin_z_mm < 0.0 or layer.height_mm <= 0.0:
            issues.append(_issue("BOX_FILL_LAYER_DIMENSIONS_INVALID", prefix, "Layer origin_z_mm must be non-negative and height_mm must be positive.", entity_id=layer.id))
        elif layer.origin_z_mm + layer.height_mm > plan.box.usable_height_mm:
            issues.append(_issue("BOX_FILL_LAYER_OUTSIDE_BOX", prefix, "Layer must stay inside the usable box height.", entity_id=layer.id))
        for reservation_id in layer.support_reservation_ids:
            if reservation_id not in reservation_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_RESERVATION", f"{prefix}.support_reservation_ids", f"Layer references unknown reservation '{reservation_id}'.", entity_id=layer.id))
        for module_id in layer.module_ids:
            if module_id not in module_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_MODULE", f"{prefix}.module_ids", f"Layer references unknown module '{module_id}'.", entity_id=layer.id))


def _validate_volumes(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    layer_ids = {layer.id for layer in plan.layers}
    layers = {layer.id: layer for layer in plan.layers}
    for family, entries in (("modules", plan.modules), ("reservations", plan.reservations)):
        for index, entry in enumerate(entries):
            prefix = f"{family}[{index}]"
            if not _positive(entry.size):
                issues.append(_issue("BOX_FILL_VOLUME_DIMENSIONS_INVALID", prefix, "Volume size must be strictly positive on X, Y and Z.", entity_id=entry.id))
                continue
            if not _fits_box(entry.origin, entry.size, plan):
                issues.append(_issue("BOX_FILL_VOLUME_OUTSIDE_BOX", prefix, "Volume must stay entirely inside the usable BoxFillPlan volume.", entity_id=entry.id))
            if entry.layer_id is not None and entry.layer_id not in layer_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_LAYER", f"{prefix}.layer_id", f"Volume references unknown layer '{entry.layer_id}'.", entity_id=entry.id))
            elif entry.layer_id is not None:
                layer = layers[entry.layer_id]
                if entry.origin.z < layer.origin_z_mm or entry.origin.z + entry.size.z > layer.origin_z_mm + layer.height_mm:
                    issues.append(_issue("BOX_FILL_VOLUME_OUTSIDE_LAYER", f"{prefix}.layer_id", f"Volume '{entry.id}' must stay inside layer '{layer.id}'.", entity_id=entry.id))


def _validate_collisions(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    for left, right in combinations(plan.modules, 2):
        if _intersects(left.origin, left.size, right.origin, right.size):
            issues.append(_issue("BOX_FILL_MODULE_COLLISION", "modules", f"Modules '{left.id}' and '{right.id}' overlap.", entity_id=left.id))
    for module in plan.modules:
        for reservation in plan.reservations:
            if _intersects(module.origin, module.size, reservation.origin, reservation.size):
                issues.append(_issue("BOX_FILL_MODULE_RESERVATION_COLLISION", "modules", f"Module '{module.id}' overlaps reservation '{reservation.id}'.", entity_id=module.id))
    for left, right in combinations(plan.reservations, 2):
        if _intersects(left.origin, left.size, right.origin, right.size) and not (left.allow_overlap and right.allow_overlap):
            issues.append(_issue("BOX_FILL_RESERVATION_COLLISION", "reservations", f"Reservations '{left.id}' and '{right.id}' overlap without mutual allow_overlap.", entity_id=left.id))


def _validate_references(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    asset_ids = {asset.id for asset in plan.assets}
    modules = {module.id: module for module in plan.modules}
    compartment_ids = {compartment.id for compartment in plan.compartments}
    feature_ids = {feature.id for feature in plan.access_features}
    for index, module in enumerate(plan.modules):
        prefix = f"modules[{index}]"
        for compartment_id in module.compartment_ids:
            if compartment_id not in compartment_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_COMPARTMENT", f"{prefix}.compartment_ids", f"Module references unknown compartment '{compartment_id}'.", entity_id=module.id))
        for feature_id in module.access_feature_ids:
            if feature_id not in feature_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_ACCESS_FEATURE", f"{prefix}.access_feature_ids", f"Module references unknown access feature '{feature_id}'.", entity_id=module.id))
    for index, allocation in enumerate(plan.allocations):
        prefix = f"allocations[{index}]"
        if allocation.asset_id not in asset_ids:
            issues.append(_issue("BOX_FILL_UNKNOWN_ASSET", f"{prefix}.asset_id", f"Allocation references unknown asset '{allocation.asset_id}'.", entity_id=allocation.asset_id))
        if allocation.module_id not in modules:
            issues.append(_issue("BOX_FILL_UNKNOWN_MODULE", f"{prefix}.module_id", f"Allocation references unknown module '{allocation.module_id}'.", entity_id=allocation.module_id))
        if allocation.quantity <= 0:
            issues.append(_issue("BOX_FILL_ALLOCATION_QUANTITY_INVALID", f"{prefix}.quantity", "Allocation quantity must be a positive integer.", entity_id=allocation.asset_id))
        if allocation.compartment_id is not None:
            if allocation.compartment_id not in compartment_ids:
                issues.append(_issue("BOX_FILL_UNKNOWN_COMPARTMENT", f"{prefix}.compartment_id", f"Allocation references unknown compartment '{allocation.compartment_id}'.", entity_id=allocation.compartment_id))
            elif allocation.module_id in modules and allocation.compartment_id not in modules[allocation.module_id].compartment_ids:
                issues.append(_issue("BOX_FILL_COMPARTMENT_NOT_IN_MODULE", f"{prefix}.compartment_id", f"Compartment '{allocation.compartment_id}' is not attached to module '{allocation.module_id}'.", entity_id=allocation.compartment_id))


def _validate_coverage(plan: BoxFillPlan, issues: list[BoxFillIssue]) -> None:
    for coverage in _asset_coverage(plan):
        if coverage.over_allocated_quantity:
            issues.append(_issue("BOX_FILL_ALLOCATION_OVER_CAPACITY", f"assets.{coverage.asset_id}", f"Asset '{coverage.asset_id}' is over-allocated by {coverage.over_allocated_quantity}.", entity_id=coverage.asset_id))
        elif coverage.unallocated_quantity:
            issues.append(_issue("BOX_FILL_ASSET_UNCOVERED", f"assets.{coverage.asset_id}", f"Asset '{coverage.asset_id}' has {coverage.unallocated_quantity} unallocated item(s).", severity="warning", category="coverage", entity_id=coverage.asset_id, corrective_action="Allocate the remaining asset quantity to an existing module."))


def _asset_coverage(plan: BoxFillPlan) -> tuple[AssetCoverage, ...]:
    allocated = {asset.id: 0 for asset in plan.assets}
    modules = {asset.id: [] for asset in plan.assets}
    compartments = {asset.id: [] for asset in plan.assets}
    for allocation in plan.allocations:
        if allocation.asset_id in allocated:
            allocated[allocation.asset_id] += allocation.quantity
            modules[allocation.asset_id].append(allocation.module_id)
            if allocation.compartment_id is not None:
                compartments[allocation.asset_id].append(allocation.compartment_id)
    result: list[AssetCoverage] = []
    for asset in plan.assets:
        actual = allocated[asset.id]
        declared = asset.quantity.count
        status = "over_allocated" if actual > declared else "covered" if actual == declared else "uncovered" if actual == 0 else "partial"
        result.append(AssetCoverage(asset.id, declared, actual, max(0, declared - actual), max(0, actual - declared), status, tuple(sorted(set(modules[asset.id]))), tuple(sorted(set(compartments[asset.id])))))
    return tuple(result)


def box_fill_plan_to_dict(plan: BoxFillPlan) -> dict[str, object]:
    analysis = analyze_box_fill_plan(plan).to_dict()
    return {
        "schema_version": plan.schema_version,
        "id": plan.id,
        "box": {"id": plan.box.id, "inner_dimensions_mm": _dimension_to_dict(plan.box.inner_dimensions), "origin_mm": _point_to_dict(plan.box.origin), "usable_height_mm": plan.box.usable_height_mm, "lid_clearance_mm": plan.box.lid_clearance_mm, "units": plan.box.units, "orientation": plan.box.orientation},
        "assets": [{"id": asset.id, "name": asset.name, "kind": asset.kind.value, "quantity": asset.quantity.count, "dimensions_mm": _dimension_to_dict(asset.dimensions)} for asset in plan.assets],
        "layers": [{"id": layer.id, "origin_z_mm": layer.origin_z_mm, "height_mm": layer.height_mm, "role": layer.role, "removal_order": layer.removal_order, "support_reservation_ids": list(layer.support_reservation_ids), "module_ids": list(layer.module_ids), "comment": layer.comment, "metadata": layer.metadata} for layer in plan.layers],
        "reservations": [{"id": reservation.id, "kind": reservation.kind.value, "origin_mm": _point_to_dict(reservation.origin), "size_mm": _dimension_to_dict(reservation.size), "layer_id": reservation.layer_id, "removal_order": reservation.removal_order, "allow_overlap": reservation.allow_overlap, "printable": False, "source": reservation.source, "comment": reservation.comment, "metadata": reservation.metadata} for reservation in plan.reservations],
        "modules": [{"id": module.id, "name": module.name, "origin_mm": _point_to_dict(module.origin), "size_mm": _dimension_to_dict(module.size), "orientation": module.orientation, "locked": module.locked, "manual": module.manual, "printable": module.printable, "layer_id": module.layer_id, "source": module.source, "compartment_ids": list(module.compartment_ids), "access_feature_ids": list(module.access_feature_ids), "comment": module.comment, "metadata": module.metadata} for module in plan.modules],
        "allocations": [{"asset_id": allocation.asset_id, "quantity": allocation.quantity, "module_id": allocation.module_id, "compartment_id": allocation.compartment_id, "source": allocation.source, "intent": allocation.intent, "coverage_status": allocation.coverage_status} for allocation in plan.allocations],
        "compartments": [{"id": compartment.id, "functional_type": compartment.functional_type.value, "origin_mm": _point_to_dict(compartment.origin), "size_mm": _dimension_to_dict(compartment.size), "clearance_mm": compartment.clearance_mm, "clearance_source": compartment.clearance_source, "comment": compartment.comment} for compartment in plan.compartments],
        "access_features": [{"id": feature.id, "kind": feature.kind.value, "placement": feature.placement, "position_mm": _point_to_dict(feature.position), "size_mm": _dimension_to_dict(feature.size) if feature.size is not None else None, "radius_mm": feature.radius_mm, "taxonomy": feature.taxonomy.value if feature.taxonomy is not None else None, "comment": feature.comment} for feature in plan.access_features],
        "coverage": analysis["coverage"],
        "free_volumes": [analysis["free_volume"]],
        "validation": analysis["validation"],
        "warnings": analysis["warnings"],
        "metrics": analysis["metrics"],
        "metadata": plan.metadata,
    }


def derive_box_fill_plan_from_executable_asset_plan(config: Any, executable_plan: dict[str, object] | None = None) -> BoxFillPlan:
    """Bridge existing asset-first placements without inventing missing product data."""
    if executable_plan is None:
        from board_game_insert_generator.asset_candidates import build_executable_asset_module_plan
        executable_plan = build_executable_asset_module_plan(config)
    generated_by_id = {entry.get("module_id"): entry for entry in executable_plan.get("generated_modules", [])}
    modules: list[BoxFillModule] = []
    allocations: list[AssetAllocation] = []
    assigned = {asset.id: 0 for asset in config.assets}
    for placement in executable_plan.get("placements", []):
        module_id = str(placement["module_id"])
        modules.append(BoxFillModule(module_id, module_id, Point3D(**placement["origin_mm"]), Dimension3D(**placement["size_mm"]), manual=False, source="derived_from_executable_asset_plan", metadata={"candidate_id": placement.get("candidate_id"), "placement_source": placement.get("placement_source")}))
        generated = generated_by_id.get(module_id, {})
        for asset_id in generated.get("source_asset_ids", placement.get("source_asset_ids", [])):
            asset = next((item for item in config.assets if item.id == asset_id), None)
            remaining = 0 if asset is None else asset.quantity.count - assigned[asset_id]
            if remaining > 0:
                allocations.append(AssetAllocation(asset_id, remaining, module_id, source="derived_from_executable_asset_plan"))
                assigned[asset_id] += remaining
    layer = BoxFillLayer("derived-base-layer", 0.0, config.box.usable_height_mm, "derived", module_ids=tuple(module.id for module in modules), comment="Derived from executable_asset_plan placements; reservations were not inferred.")
    return BoxFillPlan(
        "box_fill_plan.v0",
        f"derived:{executable_plan.get('plan_id', 'executable_asset_plan')}",
        BoxFillBox("derived-game-box", config.box.inner_dimensions, Point3D(0.0, 0.0, 0.0), config.box.usable_height_mm, config.box.lid_clearance_mm, config.units),
        config.assets,
        layers=(layer,),
        modules=tuple(modules),
        allocations=tuple(allocations),
        metadata={"source": "derived_from_executable_asset_plan", "bridge_warnings": ["Reservations, manual locks, compartments and access features were not inferred.", "Only placed executable modules were converted; rejected modules remain uncovered."]},
    )


def _volumes_by_layer(plan: BoxFillPlan, regions: list[FreeRegion]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {
        layer.id: {"module_volume_mm3": 0.0, "reservation_volume_mm3": 0.0, "free_volume_mm3": 0.0}
        for layer in plan.layers
    }
    result["unassigned"] = {"module_volume_mm3": 0.0, "reservation_volume_mm3": 0.0, "free_volume_mm3": 0.0}
    for module in plan.modules:
        result.get(module.layer_id or "unassigned", result["unassigned"])["module_volume_mm3"] += _volume(module.size)
    for reservation in plan.reservations:
        result.get(reservation.layer_id or "unassigned", result["unassigned"])["reservation_volume_mm3"] += _volume(reservation.size)
    for region in regions:
        result.get(region.layer_id or "unassigned", result["unassigned"])["free_volume_mm3"] += region.volume_mm3
    return {key: value for key, value in result.items() if key != "unassigned" or any(value.values())}

def _decompose_free_regions(plan: BoxFillPlan) -> tuple[list[FreeRegion], float, float]:
    x_cuts = {plan.box.origin.x, plan.box.origin.x + plan.box.inner_dimensions.x}
    y_cuts = {plan.box.origin.y, plan.box.origin.y + plan.box.inner_dimensions.y}
    z_cuts = {plan.box.origin.z, plan.box.origin.z + plan.box.usable_height_mm}
    for volume in (*plan.modules, *plan.reservations):
        x_cuts.update((_clip(volume.origin.x, plan.box.origin.x, plan.box.origin.x + plan.box.inner_dimensions.x), _clip(volume.origin.x + volume.size.x, plan.box.origin.x, plan.box.origin.x + plan.box.inner_dimensions.x)))
        y_cuts.update((_clip(volume.origin.y, plan.box.origin.y, plan.box.origin.y + plan.box.inner_dimensions.y), _clip(volume.origin.y + volume.size.y, plan.box.origin.y, plan.box.origin.y + plan.box.inner_dimensions.y)))
        z_cuts.update((_clip(volume.origin.z, plan.box.origin.z, plan.box.origin.z + plan.box.usable_height_mm), _clip(volume.origin.z + volume.size.z, plan.box.origin.z, plan.box.origin.z + plan.box.usable_height_mm)))
    for layer in plan.layers:
        z_cuts.update((_clip(layer.origin_z_mm, plan.box.origin.z, plan.box.origin.z + plan.box.usable_height_mm), _clip(layer.origin_z_mm + layer.height_mm, plan.box.origin.z, plan.box.origin.z + plan.box.usable_height_mm)))
    regions: list[FreeRegion] = []
    module_volume = 0.0
    reservation_volume = 0.0
    for xi, x in enumerate(sorted(x_cuts)[:-1]):
        xs = sorted(x_cuts)
        for yi, y in enumerate(sorted(y_cuts)[:-1]):
            ys = sorted(y_cuts)
            for zi, z in enumerate(sorted(z_cuts)[:-1]):
                zs = sorted(z_cuts)
                origin = Point3D(x, y, z)
                size = Dimension3D(xs[xi + 1] - x, ys[yi + 1] - y, zs[zi + 1] - z)
                if not _positive(size):
                    continue
                volume = _volume(size)
                if any(_contains(item.origin, item.size, origin, size) for item in plan.modules):
                    module_volume += volume
                elif any(_contains(item.origin, item.size, origin, size) for item in plan.reservations):
                    reservation_volume += volume
                else:
                    regions.append(FreeRegion(f"free:{xi}:{yi}:{zi}", origin, size, volume, _layer_for_region(plan, origin, size), True, "Exact AABB free cell; no automatic placement decision is implied."))
    return regions, module_volume, reservation_volume


def _clip(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))

def _contains(container_origin: Point3D, container_size: Dimension3D, origin: Point3D, size: Dimension3D) -> bool:
    return origin.x >= container_origin.x and origin.y >= container_origin.y and origin.z >= container_origin.z and origin.x + size.x <= container_origin.x + container_size.x and origin.y + size.y <= container_origin.y + container_size.y and origin.z + size.z <= container_origin.z + container_size.z


def _layer_for_region(plan: BoxFillPlan, origin: Point3D, size: Dimension3D) -> str | None:
    for layer in plan.layers:
        if origin.z >= layer.origin_z_mm and origin.z + size.z <= layer.origin_z_mm + layer.height_mm:
            return layer.id
    return None


def _positive(size: Dimension3D) -> bool:
    return size.x > 0.0 and size.y > 0.0 and size.z > 0.0


def _fits_box(origin: Point3D, size: Dimension3D, plan: BoxFillPlan) -> bool:
    box = plan.box
    return origin.x >= box.origin.x and origin.y >= box.origin.y and origin.z >= box.origin.z and origin.x + size.x <= box.origin.x + box.inner_dimensions.x and origin.y + size.y <= box.origin.y + box.inner_dimensions.y and origin.z + size.z <= box.origin.z + box.usable_height_mm


def _intersects(left_origin: Point3D, left_size: Dimension3D, right_origin: Point3D, right_size: Dimension3D) -> bool:
    return left_origin.x < right_origin.x + right_size.x and right_origin.x < left_origin.x + left_size.x and left_origin.y < right_origin.y + right_size.y and right_origin.y < left_origin.y + left_size.y and left_origin.z < right_origin.z + right_size.z and right_origin.z < left_origin.z + left_size.z


def _volume(size: Dimension3D) -> float:
    return size.x * size.y * size.z


def _point_to_dict(point: Point3D) -> dict[str, float]:
    return {"x": point.x, "y": point.y, "z": point.z}


def _dimension_to_dict(dimension: Dimension3D | None) -> dict[str, float] | None:
    return None if dimension is None else {"x": dimension.x, "y": dimension.y, "z": dimension.z}


def _issue(code: str, field: str, message: str, severity: str = "blocker", category: str = "validation", entity_id: str | None = None, constraint_ref: str = "box_fill_plan.v0", corrective_action: str = "Correct the referenced field and validate the plan again.") -> BoxFillIssue:
    return BoxFillIssue(code, field, message, severity, category, entity_id, constraint_ref, corrective_action)
