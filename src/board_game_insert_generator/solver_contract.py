"""Internal multi-solver contract used by the P64 portfolio.

The public partition-plan schema deliberately remains unchanged in P64-H05.
This module is the narrow internal boundary that later strategy families must
use: an immutable candidate snapshot, a monotone budget snapshot and one
authoritative certificate for a complete placement.

``stage_stack`` is the only adapter in this lot.  It still owns its existing
search and selection logic, but it cannot expose a materializable proposal
until this module certifies it.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable, Mapping


STAGE_STACK_FAMILY_ID = "stage_stack"
COMMON_VALIDATOR_SCHEMA_V1 = "bgig.solver_candidate_certificate.v1"
_EPSILON = 0.0001
_AXES = ("x", "y", "z")


class SolverContractViolation(RuntimeError):
    """Raised when a strategy tries to expose an uncertified solution."""


@dataclass(frozen=True)
class SolverStrategy:
    """Stable identity of one internal strategy family."""

    family_id: str
    version: str


@dataclass(frozen=True)
class SolverBudget:
    """Immutable, comparable search-budget snapshot.

    ``limits`` is sorted by construction so it has a deterministic digest and
    can later be compared across effort profiles without exposing new UI here.
    """

    family_id: str
    effort_profile: str
    limits: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        if tuple(sorted(name for name, _ in self.limits)) != tuple(name for name, _ in self.limits):
            raise ValueError("Solver budget limits must be sorted by name.")
        if any(value < 0 for _, value in self.limits):
            raise ValueError("Solver budget limits must be non-negative.")

    def is_at_least_as_permissive_as(self, other: "SolverBudget") -> bool:
        """Return whether this snapshot never tightens a shared budget limit."""

        if self.family_id != other.family_id:
            return False
        current = dict(self.limits)
        baseline = dict(other.limits)
        return all(current.get(name, -1) >= value for name, value in baseline.items())


@dataclass(frozen=True)
class PlacementSnapshot:
    """Immutable geometry view of one proposed body."""

    placement_id: str
    role: str
    origin_mm: tuple[float, float, float]
    size_mm: tuple[float, float, float]
    rotation_deg_z: int


@dataclass(frozen=True)
class SolverCandidate:
    """One immutable candidate exposed by a strategy before certification."""

    strategy: SolverStrategy
    candidate_id: str
    plan_digest: str
    placements: tuple[PlacementSnapshot, ...]
    score_breakdown: tuple[tuple[str, float], ...]
    automatic_body_count: int

    @property
    def digest(self) -> str:
        payload = {
            "strategy": {"family_id": self.strategy.family_id, "version": self.strategy.version},
            "candidate_id": self.candidate_id,
            "plan_digest": self.plan_digest,
            "placements": [
                {
                    "placement_id": item.placement_id,
                    "role": item.role,
                    "origin_mm": item.origin_mm,
                    "size_mm": item.size_mm,
                    "rotation_deg_z": item.rotation_deg_z,
                }
                for item in self.placements
            ],
            "score_breakdown": self.score_breakdown,
            "automatic_body_count": self.automatic_body_count,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ValidationCheck:
    """One named invariant evaluated by the common validator."""

    name: str
    passed: bool
    rejection_code: str | None = None


@dataclass(frozen=True)
class ValidationCertificate:
    """Immutable result of the only admission check for a full proposal."""

    schema_version: str
    candidate_digest: str
    certified: bool
    checks: tuple[ValidationCheck, ...]

    @property
    def rejection_codes(self) -> tuple[str, ...]:
        return tuple(
            check.rejection_code
            for check in self.checks
            if not check.passed and check.rejection_code is not None
        )


@dataclass(frozen=True)
class StrategyRun:
    """Immutable internal result shared by future solver families."""

    strategy: SolverStrategy
    budget: SolverBudget
    candidates: tuple[SolverCandidate, ...]
    certificates: tuple[ValidationCertificate, ...]


def run_stage_stack_adapter(
    legacy_solver: Callable[..., dict[str, object]],
    raw_project: object,
    *,
    request_id: str | None = None,
    request_revision: int | None = None,
) -> dict[str, object]:
    """Run the preserved baseline and fail closed for an uncertified solution.

    The adapter intentionally returns the legacy plan byte-for-byte.  P64-H05
    therefore adds no project schema or public-plan field; the contract is an
    internal safety boundary until the portfolio has a public configuration.
    """

    plan = legacy_solver(
        raw_project,
        request_id=request_id,
        request_revision=request_revision,
    )
    run = inspect_stage_stack_plan(plan)
    if _solution_found(plan) and (len(run.certificates) != 1 or not run.certificates[0].certified):
        raise SolverContractViolation(
            "stage_stack attempted to expose a materializable proposal without a common certificate."
        )
    return plan


def inspect_stage_stack_plan(plan: Mapping[str, object]) -> StrategyRun:
    """Adapt one legacy plan to immutable common-contract values.

    Non-solutions deliberately expose zero candidates: an incomplete or failed
    search cannot accidentally become materializable through this boundary.
    """

    solver = _mapping(plan.get("solver"))
    strategy = SolverStrategy(
        family_id=STAGE_STACK_FAMILY_ID,
        version=_text(solver.get("schema_version")) or "not_applicable",
    )
    budget = _budget_from_legacy(strategy, _mapping(solver.get("budgets")))
    if not _solution_found(plan):
        return StrategyRun(strategy=strategy, budget=budget, candidates=(), certificates=())

    candidate = _candidate_from_plan(plan, strategy)
    certificate = certify_partition_candidate(plan, candidate)
    return StrategyRun(
        strategy=strategy,
        budget=budget,
        candidates=(candidate,),
        certificates=(certificate,),
    )


def certify_partition_candidate(
    plan: Mapping[str, object],
    candidate: SolverCandidate,
) -> ValidationCertificate:
    """Revalidate a complete candidate against the common P64 invariants."""

    placements = _mappings(plan.get("placements"))
    box = _mapping(_mapping(plan.get("box")).get("inner_dimensions_mm"))
    policy = _mapping(plan.get("clearance_policy"))
    geometry = validate_placement_geometry(
        placements,
        _dimension(box),
        _number(_mapping(plan.get("box")).get("storage_height_mm")),
        _number(policy.get("between_bodies_xy_mm")),
        _number(policy.get("box_perimeter_xy_mm")),
        _number(policy.get("between_bodies_z_mm")),
    )
    summary = _mapping(plan.get("summary"))
    envelope_contract = _mapping(plan.get("envelope_contract"))
    top_insets = _mapping(plan.get("top_inset_reservations"))
    stage_support = _mapping(plan.get("stage_support"))
    top_support = _mapping(plan.get("support"))
    container_placements = [item for item in placements if _text(item.get("role")) == "container"]
    expected_containers = _integer(summary.get("requested_container_count"))
    envelope_containers = _mappings(envelope_contract.get("containers"))
    envelope_ready = (
        _text(_mapping(envelope_contract.get("summary")).get("status")) == "ready_for_p56"
        and len(envelope_containers) == expected_containers
        and all(_text(item.get("status")) == "ready" for item in envelope_containers)
    )
    cavities_walls_floors = (
        len(container_placements) == expected_containers
        and all(_container_preserves_cavity_wall_and_floor(item) for item in container_placements)
        and all(_contract_preserves_cavity_wall_and_floor(item) for item in envelope_containers)
    )
    reservations_and_support = (
        _text(top_insets.get("status")) in {"applied", "not_required"}
        and not _mappings(top_insets.get("blockers"))
        and _text(stage_support.get("status")) == "supported"
        and _text(top_support.get("status")) in {"supported_by_requested_bodies", "not_required"}
    )
    removal = _removal_sequence_is_complete(plan, placements)
    conservation = _conservation_is_complete(summary, _mapping(plan.get("validation")))
    requested_bodies_only = (
        candidate.automatic_body_count == 0
        and _integer(summary.get("automatic_body_count")) == 0
        and _integer(_mapping(plan.get("invariants")).get("automatic_body_count")) == 0
        and bool(_mapping(plan.get("invariants")).get("requested_bodies_only"))
    )
    checks = (
        ValidationCheck("inside_box", bool(geometry["inside_box"]), "OUTSIDE_USEFUL_BOX"),
        ValidationCheck("box_xy_clearance", bool(geometry["box_xy_clearance_respected"]), "BOX_XY_CLEARANCE"),
        ValidationCheck("no_collisions", bool(geometry["no_collisions"]), "BODY_COLLISION"),
        ValidationCheck("between_body_clearance", bool(geometry["clearances_respected"]), "BODY_CLEARANCE"),
        ValidationCheck("envelope_contract", envelope_ready, "ENVELOPE_CONTRACT"),
        ValidationCheck("cavities_walls_floors", cavities_walls_floors, "CAVITY_WALL_FLOOR_CONTRACT"),
        ValidationCheck("reservations_and_support", reservations_and_support, "RESERVATION_OR_SUPPORT_CONTRACT"),
        ValidationCheck("removal_sequence", removal, "REMOVAL_SEQUENCE_CONTRACT"),
        ValidationCheck("volume_conservation", conservation, "VOLUME_CONSERVATION"),
        ValidationCheck("requested_bodies_only", requested_bodies_only, "AUTOMATIC_BODY_FORBIDDEN"),
    )
    return ValidationCertificate(
        schema_version=COMMON_VALIDATOR_SCHEMA_V1,
        candidate_digest=candidate.digest,
        certified=all(check.passed for check in checks),
        checks=checks,
    )


def validate_placement_geometry(
    placements: list[dict[str, object]],
    box: dict[str, float],
    storage_height: float,
    xy_clearance: float,
    box_xy_clearance: float,
    z_clearance: float,
) -> dict[str, object]:
    """Authoritative common geometric validation for every strategy family."""

    inside = all(
        all(_number(_mapping(item.get("origin_mm")).get(axis)) >= -_EPSILON for axis in _AXES)
        and _number(_mapping(item.get("origin_mm")).get("x")) + _number(_mapping(item.get("world_size_mm")).get("x")) <= box["x"] + _EPSILON
        and _number(_mapping(item.get("origin_mm")).get("y")) + _number(_mapping(item.get("world_size_mm")).get("y")) <= box["y"] + _EPSILON
        and _number(_mapping(item.get("origin_mm")).get("z")) + _number(_mapping(item.get("world_size_mm")).get("z")) <= storage_height + _EPSILON
        for item in placements
    )
    box_xy_clearance_respected = all(
        _number(_mapping(item.get("origin_mm")).get("x")) >= _placement_clearance(item, "box_per_side_xy_mm", "x", box_xy_clearance) - _EPSILON
        and _number(_mapping(item.get("origin_mm")).get("y")) >= _placement_clearance(item, "box_per_side_xy_mm", "y", box_xy_clearance) - _EPSILON
        and _number(_mapping(item.get("origin_mm")).get("x")) + _number(_mapping(item.get("world_size_mm")).get("x"))
        <= box["x"] - _placement_clearance(item, "box_per_side_xy_mm", "x", box_xy_clearance) + _EPSILON
        and _number(_mapping(item.get("origin_mm")).get("y")) + _number(_mapping(item.get("world_size_mm")).get("y"))
        <= box["y"] - _placement_clearance(item, "box_per_side_xy_mm", "y", box_xy_clearance) + _EPSILON
        for item in placements
    )
    no_collisions = all(
        not _intersects(left, right)
        for index, left in enumerate(placements)
        for right in placements[index + 1 :]
    )
    clearances = all(
        _separated_with_clearance(left, right, xy_clearance, z_clearance)
        for index, left in enumerate(placements)
        for right in placements[index + 1 :]
    )
    body_volume = sum(_volume(_mapping(item.get("world_size_mm"))) for item in placements)
    storage_volume = box["x"] * box["y"] * storage_height
    return {
        "inside_box": inside,
        "box_xy_clearance_respected": box_xy_clearance_respected,
        "no_collisions": no_collisions,
        "clearances_respected": clearances,
        "body_volume_mm3": _round(body_volume),
        "storage_volume_mm3": _round(storage_volume),
        "technical_void_volume_mm3": _round(max(0.0, storage_volume - body_volume)),
        "unassigned_printable_volume_mm3": 0.0,
    }


def _budget_from_legacy(strategy: SolverStrategy, budgets: Mapping[str, object]) -> SolverBudget:
    limits = tuple(
        sorted(
            (str(name), int(value))
            for name, value in budgets.items()
            if isinstance(value, int) and not isinstance(value, bool)
        )
    )
    return SolverBudget(family_id=strategy.family_id, effort_profile="baseline", limits=limits)


def _candidate_from_plan(plan: Mapping[str, object], strategy: SolverStrategy) -> SolverCandidate:
    solver = _mapping(plan.get("solver"))
    summary = _mapping(plan.get("summary"))
    score = _mapping(summary.get("score_breakdown"))
    placements = tuple(
        PlacementSnapshot(
            placement_id=_text(item.get("id")) or _text(item.get("placement_id")),
            role=_text(item.get("role")),
            origin_mm=_dimension_tuple(_mapping(item.get("origin_mm"))),
            size_mm=_dimension_tuple(_mapping(item.get("world_size_mm"))),
            rotation_deg_z=_integer(item.get("rotation_deg_z")),
        )
        for item in _mappings(plan.get("placements"))
    )
    return SolverCandidate(
        strategy=strategy,
        candidate_id=_text(solver.get("candidate_id")) or "stage_stack:complete",
        plan_digest=_text(plan.get("plan_digest")),
        placements=placements,
        score_breakdown=tuple(
            sorted((str(name), _number(value)) for name, value in score.items() if isinstance(value, (int, float)))
        ),
        automatic_body_count=_integer(summary.get("automatic_body_count")),
    )


def _solution_found(plan: Mapping[str, object]) -> bool:
    return (
        _text(_mapping(_mapping(plan.get("solver")).get("result")).get("status")) == "solution_found"
        and bool(_mapping(plan.get("summary")).get("materializable"))
    )


def _container_preserves_cavity_wall_and_floor(placement: Mapping[str, object]) -> bool:
    return (
        bool(_mappings(placement.get("cavity_layout")))
        and _dimension_is_non_negative(_mapping(placement.get("minimum_outer_envelope_mm")))
        and _dimension_is_non_negative(_mapping(placement.get("surplus_distribution_mm")))
        and _dimension_is_non_negative(_mapping(placement.get("minimum_envelope_origin_in_final_mm")))
    )


def _contract_preserves_cavity_wall_and_floor(contract: Mapping[str, object]) -> bool:
    constraints = _mapping(contract.get("constraints"))
    return (
        bool(_mappings(contract.get("cavity_layout")))
        and _dimension_is_non_negative(_mapping(contract.get("minimum_outer_envelope_mm")))
        and _number(constraints.get("minimum_wall_thickness_mm")) > 0.0
        and _number(constraints.get("minimum_floor_thickness_mm")) > 0.0
    )


def _removal_sequence_is_complete(plan: Mapping[str, object], placements: list[dict[str, object]]) -> bool:
    sequence = _mappings(plan.get("removal_sequence"))
    placement_ids = {_text(item.get("id")) or _text(item.get("placement_id")) for item in placements}
    removal_ids = {_text(item.get("target_id")) for item in sequence}
    orders = [_integer(item.get("order")) for item in sequence]
    return bool(sequence) and placement_ids.issubset(removal_ids) and len(orders) == len(set(orders))


def _conservation_is_complete(summary: Mapping[str, object], validation: Mapping[str, object]) -> bool:
    storage = _number(validation.get("storage_volume_mm3"))
    body = _number(validation.get("body_volume_mm3"))
    technical = _number(validation.get("technical_void_volume_mm3"))
    return (
        bool(summary.get("complete_printable_partition"))
        and bool(summary.get("technical_voids_are_clearances_only"))
        and abs(_number(summary.get("residual_volume_mm3"))) <= _EPSILON
        and abs(_number(validation.get("unassigned_printable_volume_mm3"))) <= _EPSILON
        and abs((body + technical) - storage) <= 0.01
    )


def _intersects(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    left_origin, left_size = _mapping(left.get("origin_mm")), _mapping(left.get("world_size_mm"))
    right_origin, right_size = _mapping(right.get("origin_mm")), _mapping(right.get("world_size_mm"))
    return all(
        _number(left_origin.get(axis)) < _number(right_origin.get(axis)) + _number(right_size.get(axis)) - _EPSILON
        and _number(right_origin.get(axis)) < _number(left_origin.get(axis)) + _number(left_size.get(axis)) - _EPSILON
        for axis in _AXES
    )


def _placement_clearance(placement: Mapping[str, object], vector: str, axis: str, fallback: float) -> float:
    policy = _mapping(placement.get("external_clearance_effective_v1"))
    values = _mapping(policy.get(vector))
    local_axis = axis
    if axis in {"x", "y"} and _integer(placement.get("rotation_deg_z")) == 90:
        local_axis = "y" if axis == "x" else "x"
    value = values.get(local_axis)
    return fallback if value is None else _number(value)


def _separated_with_clearance(
    left: Mapping[str, object],
    right: Mapping[str, object],
    xy_clearance: float,
    z_clearance: float,
) -> bool:
    left_origin, left_size = _mapping(left.get("origin_mm")), _mapping(left.get("world_size_mm"))
    right_origin, right_size = _mapping(right.get("origin_mm")), _mapping(right.get("world_size_mm"))
    return any(
        _number(left_origin.get(axis)) + _number(left_size.get(axis)) + clearance <= _number(right_origin.get(axis)) + 0.001
        or _number(right_origin.get(axis)) + _number(right_size.get(axis)) + clearance <= _number(left_origin.get(axis)) + 0.001
        for axis, clearance in (
            ("x", max(_placement_clearance(left, "between_mm", "x", xy_clearance), _placement_clearance(right, "between_mm", "x", xy_clearance))),
            ("y", max(_placement_clearance(left, "between_mm", "y", xy_clearance), _placement_clearance(right, "between_mm", "y", xy_clearance))),
            ("z", max(_placement_clearance(left, "between_mm", "z", z_clearance), _placement_clearance(right, "between_mm", "z", z_clearance))),
        )
    )


def _dimension(value: Mapping[str, object]) -> dict[str, float]:
    return {axis: _number(value.get(axis)) for axis in _AXES}


def _dimension_tuple(value: Mapping[str, object]) -> tuple[float, float, float]:
    return tuple(_number(value.get(axis)) for axis in _AXES)  # type: ignore[return-value]


def _dimension_is_non_negative(value: Mapping[str, object]) -> bool:
    return bool(value) and all(_number(value.get(axis)) >= 0.0 for axis in _AXES)


def _volume(value: Mapping[str, object]) -> float:
    return _number(value.get("x")) * _number(value.get("y")) * _number(value.get("z"))


def _round(value: float) -> float:
    return round(float(value), 4)


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _mappings(value: object) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _number(value: object) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def _integer(value: object) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0
