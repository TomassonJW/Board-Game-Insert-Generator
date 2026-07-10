"""Deterministic bounded 2D greedy placement for BoxFillPlan."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import sha256
import json

from board_game_insert_generator.box_fill import analyze_box_fill_plan
from board_game_insert_generator.models import AssetAllocation, BoxFillModule, BoxFillPlan, Dimension3D, Point3D

BOX_FILL_GREEDY_POLICY_V0 = "box_fill_greedy_2d.v0"


@dataclass(frozen=True)
class BoxFillCandidate:
    module_id: str
    name: str
    size: Dimension3D
    allocations: tuple[AssetAllocation, ...] = ()
    allowed_layer_ids: tuple[str, ...] = ()
    allow_xy_rotation: bool = False
    preferred_orientation: str = "native"
    priority: int = 0
    source: str = "manual"
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class BoxFillSolveRequest:
    source_plan: BoxFillPlan
    candidates: tuple[BoxFillCandidate, ...]
    policy: str = BOX_FILL_GREEDY_POLICY_V0
    solver_version: str = "v0"


@dataclass(frozen=True)
class BoxFillSolveDiagnostic:
    module_id: str
    code: str
    category: str
    severity: str
    message: str
    attempted_layer_ids: tuple[str, ...]
    attempted_orientations: tuple[str, ...]
    corrective_action: str

    def to_dict(self) -> dict[str, object]:
        return {"module_id": self.module_id, "code": self.code, "category": self.category, "severity": self.severity, "message": self.message, "attempted_layer_ids": list(self.attempted_layer_ids), "attempted_orientations": list(self.attempted_orientations), "corrective_action": self.corrective_action}


@dataclass(frozen=True)
class BoxFillPlacement:
    module_id: str
    origin: Point3D
    size: Dimension3D
    layer_id: str
    orientation: str

    def to_dict(self) -> dict[str, object]:
        return {"module_id": self.module_id, "origin_mm": _point(self.origin), "size_mm": _size(self.size), "layer_id": self.layer_id, "orientation": self.orientation}


@dataclass(frozen=True)
class BoxFillSolveResult:
    source_plan_id: str
    policy: str
    solver_version: str
    status: str
    solved_plan: BoxFillPlan
    candidate_order: tuple[str, ...]
    placements: tuple[BoxFillPlacement, ...]
    diagnostics: tuple[BoxFillSolveDiagnostic, ...]
    metrics: dict[str, object]
    solver_result_digest: str

    def to_dict(self) -> dict[str, object]:
        return {"source_plan_id": self.source_plan_id, "solver_policy": self.policy, "solver_version": self.solver_version, "status": self.status, "candidate_order": list(self.candidate_order), "placements": [item.to_dict() for item in self.placements], "refusals": [item.to_dict() for item in self.diagnostics], "metrics": self.metrics, "solver_result_digest": self.solver_result_digest}


def solve_box_fill_greedy(request: BoxFillSolveRequest) -> BoxFillSolveResult:
    if request.policy != BOX_FILL_GREEDY_POLICY_V0:
        raise ValueError(f"Unsupported BoxFill solver policy: {request.policy!r}")
    plan = request.source_plan
    ordered = tuple(sorted(request.candidates, key=lambda item: (-item.priority, -(item.size.x * item.size.y), -max(item.size.x, item.size.y), -item.size.z, item.module_id)))
    placed_modules = list(plan.modules)
    allocations = list(plan.allocations)
    placements: list[BoxFillPlacement] = []
    diagnostics: list[BoxFillSolveDiagnostic] = []
    existing_ids = {module.id for module in plan.modules}
    for candidate in ordered:
        layers = _candidate_layers(plan, candidate)
        orientations = _orientations(candidate)
        if candidate.module_id in existing_ids or candidate.size.x <= 0 or candidate.size.y <= 0 or candidate.size.z <= 0:
            diagnostics.append(_diagnostic(candidate, "invalid_candidate_dimensions", "validation", "Candidate id conflicts with an existing module or dimensions are not strictly positive.", layers, tuple(name for name, _ in orientations), "Use a unique module id and strictly positive X/Y/Z dimensions."))
            continue
        placement = _first_placement(plan, placed_modules, candidate, layers, orientations)
        if placement is None:
            code = "no_layer_with_sufficient_height" if not any(candidate.size.z <= layer.height_mm for layer in plan.layers if layer.id in layers) else "no_free_rectangle_fits"
            diagnostics.append(_diagnostic(candidate, code, "placement", "No valid deterministic AABB position was found without moving locked/manual modules or reservations.", layers, tuple(name for name, _ in orientations), "Choose a compatible layer, reduce the candidate footprint, allow XY rotation, or free space."))
            continue
        placed_modules.append(BoxFillModule(candidate.module_id, candidate.name, placement.origin, placement.size, orientation=placement.orientation, locked=False, manual=False, printable=True, layer_id=placement.layer_id, source=candidate.source, metadata={**candidate.metadata, "solver_policy": request.policy, "auto_placed": True}))
        allocations.extend(replace(item, module_id=candidate.module_id) for item in candidate.allocations)
        existing_ids.add(candidate.module_id)
        placements.append(placement)
    solved = replace(plan, id=f"{plan.id}:greedy-2d", modules=tuple(placed_modules), allocations=tuple(allocations), metadata={**plan.metadata, "solver_policy": request.policy, "solver_version": request.solver_version, "source_plan_id": plan.id})
    analysis = analyze_box_fill_plan(solved)
    status = "solved" if not diagnostics and analysis.valid else "partial" if placements else "blocked"
    metrics = {**analysis.metrics, "candidates_count": len(ordered), "locked_modules_count": sum(1 for module in plan.modules if module.locked), "manual_modules_count": sum(1 for module in plan.modules if module.manual), "auto_placed_count": len(placements), "auto_refused_count": len(diagnostics), "rotation_count": sum(1 for placement in placements if placement.orientation == "rotated_90_z"), "layers_used": sorted({placement.layer_id for placement in placements}), "free_regions_count": len(analysis.free_volume.regions), "largest_free_region_mm3": max((item.volume_mm3 for item in analysis.free_volume.regions), default=0.0)}
    digest_payload = {"policy": request.policy, "order": [candidate.module_id for candidate in ordered], "placements": [placement.to_dict() for placement in placements], "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics]}
    digest = sha256(json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return BoxFillSolveResult(plan.id, request.policy, request.solver_version, status, solved, tuple(candidate.module_id for candidate in ordered), tuple(placements), tuple(diagnostics), metrics, digest)


def _candidate_layers(plan: BoxFillPlan, candidate: BoxFillCandidate) -> tuple[str, ...]:
    known = {layer.id for layer in plan.layers}
    return tuple(layer_id for layer_id in candidate.allowed_layer_ids if layer_id in known) if candidate.allowed_layer_ids else tuple(layer.id for layer in sorted(plan.layers, key=lambda item: (item.removal_order if item.removal_order is not None else 9999, item.origin_z_mm, item.id)))


def _orientations(candidate: BoxFillCandidate) -> tuple[tuple[str, Dimension3D], ...]:
    native = ("native", candidate.size)
    rotated = ("rotated_90_z", Dimension3D(candidate.size.y, candidate.size.x, candidate.size.z))
    return (rotated, native) if candidate.allow_xy_rotation and candidate.preferred_orientation == "rotated_90_z" else (native, rotated) if candidate.allow_xy_rotation else (native,)


def _first_placement(plan: BoxFillPlan, modules: list[BoxFillModule], candidate: BoxFillCandidate, layer_ids: tuple[str, ...], orientations: tuple[tuple[str, Dimension3D], ...]) -> BoxFillPlacement | None:
    layers = {layer.id: layer for layer in plan.layers}
    for layer_id in layer_ids:
        layer = layers[layer_id]
        for orientation, size in orientations:
            if size.z > layer.height_mm:
                continue
            obstacles = [*plan.reservations, *modules]
            xs = sorted({plan.box.origin.x, *(item.origin.x + item.size.x for item in obstacles), *(item.origin.x for item in obstacles)})
            ys = sorted({plan.box.origin.y, *(item.origin.y + item.size.y for item in obstacles), *(item.origin.y for item in obstacles)})
            for y in ys:
                for x in xs:
                    origin = Point3D(x, y, layer.origin_z_mm)
                    probe = BoxFillModule(candidate.module_id, candidate.name, origin, size, layer_id=layer_id)
                    if _fits(plan, probe) and not any(_intersects(probe, item) for item in obstacles):
                        return BoxFillPlacement(candidate.module_id, origin, size, layer_id, orientation)
    return None


def _fits(plan: BoxFillPlan, module: BoxFillModule) -> bool:
    return module.origin.x >= plan.box.origin.x and module.origin.y >= plan.box.origin.y and module.origin.x + module.size.x <= plan.box.origin.x + plan.box.inner_dimensions.x and module.origin.y + module.size.y <= plan.box.origin.y + plan.box.inner_dimensions.y and module.origin.z >= plan.box.origin.z and module.origin.z + module.size.z <= plan.box.origin.z + plan.box.usable_height_mm


def _intersects(left, right) -> bool:
    return left.origin.x < right.origin.x + right.size.x and right.origin.x < left.origin.x + left.size.x and left.origin.y < right.origin.y + right.size.y and right.origin.y < left.origin.y + left.size.y and left.origin.z < right.origin.z + right.size.z and right.origin.z < left.origin.z + left.size.z


def _diagnostic(candidate, code, category, message, layers, orientations, action):
    return BoxFillSolveDiagnostic(candidate.module_id, code, category, "blocker", message, layers, orientations, action)


def _point(point: Point3D) -> dict[str, float]: return {"x": point.x, "y": point.y, "z": point.z}
def _size(size: Dimension3D) -> dict[str, float]: return {"x": size.x, "y": size.y, "z": size.z}
