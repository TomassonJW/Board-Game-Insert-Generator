"""Comparateurs offline et petit oracle exact interne pour P64-L06C.

Ce module ne route pas le solveur produit. Il normalise deux candidats de
benchmark au maximum et repasse toute solution par le certificat BGIG commun.
L'oracle exact reste volontairement limité à de petits placements rectangulaires
sur le fond de la boîte, sans dépendance externe.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping

from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.free_3d_plan_adapter import (
    Free3DPreparedProblem,
    certify_minimal_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_contract import (
    PlacementSnapshot,
    SolverBudget,
    SolverCandidate,
    SolverStrategy,
    ValidationCertificate,
    certify_minimal_layout_candidate,
)
from board_game_insert_generator.solver_outcome import SOLUTION_FOUND


ADAPTER_RESULT_SCHEMA_V1 = "bgig.solver_benchmark_adapter_result.v1"
ADAPTER_PROTOCOL_SCHEMA_V1 = "bgig.solver_benchmark_adapter_protocol.v1"
CURRENT_BGIG_ADAPTER_ID = "current_bgig_minimal_layout"
INTERNAL_EXACT_ADAPTER_ID = "internal_exact_floor"
INTERNAL_EXACT_FAMILY_ID = "benchmark_internal_exact_floor"
INTERNAL_EXACT_VERSION = "1"
EXACT_MODEL_ID = "canonical_minimum_envelopes_single_floor_v1"
STATUS_PROVEN_IMPOSSIBLE = "proven_impossible"
STATUS_BOUNDED_UNKNOWN = "bounded_unknown"
STATUS_UNSUPPORTED = "unsupported"
STATUS_CERTIFICATE_REJECTED = "certificate_rejected"
STATUS_INVALID_INPUT = "invalid_input"
_EPSILON = 0.0001
_AXES = ("x", "y", "z")


class SolverBenchmarkAdapterError(ValueError):
    """Entrée ou identifiant d'adapter invalide."""


@dataclass(frozen=True)
class ExactOracleCaps:
    """Plafonds explicites du petit oracle, sans limite temporelle cachée."""

    max_participants: int = 4
    max_search_states: int = 250_000
    max_placement_trials: int = 1_000_000

    def __post_init__(self) -> None:
        for name, value in self.to_dict().items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"Exact oracle cap {name} must be a positive integer.")

    def to_dict(self) -> dict[str, int]:
        return {
            "max_participants": self.max_participants,
            "max_placement_trials": self.max_placement_trials,
            "max_search_states": self.max_search_states,
        }


@dataclass(frozen=True)
class BenchmarkAdapterExecution:
    """Rapport sérialisable et éventuel plan certifié gardé hors du rapport."""

    report: dict[str, object]
    certified_plan: dict[str, object] | None


@dataclass(frozen=True)
class _FloorBody:
    participant_id: str
    role: str
    name: str
    local_size_mm: tuple[float, float, float]


@dataclass(frozen=True)
class _FloorPlacement:
    body: _FloorBody
    origin_x_mm: float
    origin_y_mm: float
    world_x_mm: float
    world_y_mm: float
    rotation_deg_z: int


@dataclass
class _ExactCounters:
    search_states: int = 0
    placement_trials: int = 0
    feasible_placements: int = 0
    complete_geometries: int = 0
    duplicate_states: int = 0
    recertification_attempts: int = 0
    cap_reached: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "cap_reached": self.cap_reached,
            "complete_geometries": self.complete_geometries,
            "duplicate_states": self.duplicate_states,
            "feasible_placements": self.feasible_placements,
            "placement_trials": self.placement_trials,
            "recertification_attempts": self.recertification_attempts,
            "search_states": self.search_states,
        }


def available_benchmark_adapters() -> tuple[dict[str, object], ...]:
    """Décrit exactement les deux candidats autorisés dans ce premier Goal."""

    return (
        {
            "adapter_id": CURRENT_BGIG_ADAPTER_ID,
            "adapter_kind": "bounded_product_solver",
            "external_dependency_count": 0,
            "protocol_schema_version": ADAPTER_PROTOCOL_SCHEMA_V1,
            "version": "current_runtime",
        },
        {
            "adapter_id": INTERNAL_EXACT_ADAPTER_ID,
            "adapter_kind": "small_exact_reference",
            "exact_model": EXACT_MODEL_ID,
            "external_dependency_count": 0,
            "protocol_schema_version": ADAPTER_PROTOCOL_SCHEMA_V1,
            "version": INTERNAL_EXACT_VERSION,
        },
    )


def run_benchmark_adapter(
    case: object,
    adapter_id: str,
    *,
    exact_caps: ExactOracleCaps | None = None,
    initial_incumbent: Mapping[str, object] | None = None,
    current_solver: Callable[..., dict[str, object]] | None = None,
) -> BenchmarkAdapterExecution:
    """Exécute un adapter connu et retourne la même forme de rapport."""

    normalized = _normalize_case(case)
    known = {item["adapter_id"] for item in available_benchmark_adapters()}
    if adapter_id not in known:
        raise SolverBenchmarkAdapterError(
            f"Unknown benchmark adapter {adapter_id!r}; expected one of {sorted(known)}."
        )
    if adapter_id == CURRENT_BGIG_ADAPTER_ID:
        return _run_current_bgig(
            normalized,
            initial_incumbent=initial_incumbent,
            solver_callable=current_solver or solve_minimal_layout,
        )
    return _run_internal_exact(normalized, exact_caps or ExactOracleCaps())


def recertify_minimal_layout_plan(plan: object) -> ValidationCertificate:
    """Reconstruit un candidat depuis le plan puis relance le certificat commun."""

    value = _mapping(plan, "plan")
    placements = _mapping_list(value.get("placements"), "plan.placements")
    solver = _mapping(value.get("solver"), "plan.solver")
    minimal = _mapping(value.get("minimal_layout"), "plan.minimal_layout")
    metrics = _mapping(minimal.get("metrics"), "plan.minimal_layout.metrics")
    digest = str(minimal.get("certifiable_payload_digest", ""))
    if not _is_digest(digest):
        raise SolverBenchmarkAdapterError(
            "A solved minimal layout must expose its certifiable payload digest."
        )
    candidate = SolverCandidate(
        strategy=SolverStrategy(
            family_id=str(solver.get("family_id", "")),
            version=str(solver.get("schema_version", "")),
        ),
        candidate_id=str(solver.get("candidate_id", "benchmark-recertification")),
        plan_digest=digest,
        placements=tuple(
            PlacementSnapshot(
                placement_id=str(item.get("id") or item.get("placement_id") or ""),
                role=str(item.get("role", "")),
                origin_mm=_dimension_tuple(item.get("origin_mm"), "placement.origin_mm"),
                size_mm=_dimension_tuple(item.get("world_size_mm"), "placement.world_size_mm"),
                rotation_deg_z=int(item.get("rotation_deg_z", 0)),
            )
            for item in placements
        ),
        score_breakdown=tuple(
            sorted(
                (str(name), float(number))
                for name, number in metrics.items()
                if isinstance(number, (int, float)) and not isinstance(number, bool)
            )
        ),
        automatic_body_count=int(
            _mapping(value.get("summary"), "plan.summary").get(
                "automatic_body_count", 0
            )
        ),
    )
    return certify_minimal_layout_candidate(value, candidate)


def _run_current_bgig(
    case: dict[str, object],
    *,
    initial_incumbent: Mapping[str, object] | None,
    solver_callable: Callable[..., dict[str, object]],
) -> BenchmarkAdapterExecution:
    features = _mapping_or_empty(case.get("features"))
    rotation_policy = str(features.get("rotation_policy_target", "permitted"))
    execution_mode = str(features.get("execution_mode", "cold"))
    unsupported: list[str] = []
    if rotation_policy == "forbidden_by_benchmark":
        unsupported.append("rotation_disable_control_not_exposed_by_project_v1")
    if execution_mode == "incremental" and initial_incumbent is None:
        unsupported.append("incremental_incumbent_not_supplied")
    if unsupported:
        report = _base_report(
            case,
            CURRENT_BGIG_ADAPTER_ID,
            "current_runtime",
            "bounded_product_solver",
            status=STATUS_UNSUPPORTED,
            stop_reason="unsupported_benchmark_constraint",
            unsupported_constraints=unsupported,
            exact_model=None,
            exact_complete=False,
            recertification=_not_attempted_certificate(),
            solution=None,
            counters={},
        )
        return BenchmarkAdapterExecution(report, None)

    settings = _mapping(case.get("solver_settings"), "case.solver_settings")
    effort = str(settings.get("effort", "quick"))
    plan = solver_callable(
        case["project"],
        effort_profile=effort,
        initial_incumbent=initial_incumbent,
    )
    solver = _mapping(plan.get("solver"), "solver result.solver")
    outcome = _mapping(solver.get("result"), "solver result.solver.result")
    telemetry = _mapping_or_empty(solver.get("telemetry"))
    counters = deepcopy(_mapping_or_empty(telemetry.get("counters")))
    status = str(outcome.get("status", STATUS_INVALID_INPUT))
    stop_reason = str(
        telemetry.get("stop_reason")
        or _mapping_or_empty(solver.get("search")).get("stop_reason")
        or "not_reported"
    )
    if status != SOLUTION_FOUND:
        report = _base_report(
            case,
            CURRENT_BGIG_ADAPTER_ID,
            str(solver.get("schema_version", "current_runtime")),
            "bounded_product_solver",
            status=status,
            stop_reason=stop_reason,
            unsupported_constraints=(),
            exact_model=None,
            exact_complete=False,
            recertification=_not_attempted_certificate(),
            solution=None,
            counters=counters,
        )
        return BenchmarkAdapterExecution(report, None)

    certificate = recertify_minimal_layout_plan(plan)
    certificate_payload = _certificate_payload(certificate, attempted=True)
    if not certificate.certified:
        report = _base_report(
            case,
            CURRENT_BGIG_ADAPTER_ID,
            str(solver.get("schema_version", "current_runtime")),
            "bounded_product_solver",
            status=STATUS_CERTIFICATE_REJECTED,
            stop_reason="fresh_common_recertification_rejected",
            unsupported_constraints=(),
            exact_model=None,
            exact_complete=False,
            recertification=certificate_payload,
            solution=None,
            counters=counters,
        )
        return BenchmarkAdapterExecution(report, None)

    solution = _solution_payload(plan, certificate)
    report = _base_report(
        case,
        CURRENT_BGIG_ADAPTER_ID,
        str(solver.get("schema_version", "current_runtime")),
        "bounded_product_solver",
        status=SOLUTION_FOUND,
        stop_reason=stop_reason,
        unsupported_constraints=(),
        exact_model=None,
        exact_complete=False,
        recertification=certificate_payload,
        solution=solution,
        counters=counters,
    )
    return BenchmarkAdapterExecution(report, deepcopy(plan))


def _run_internal_exact(
    case: dict[str, object],
    caps: ExactOracleCaps,
) -> BenchmarkAdapterExecution:
    features = _mapping_or_empty(case.get("features"))
    unsupported: list[str] = []
    if not bool(case.get("generated_case")):
        unsupported.append("generated_exact_case_features_missing")
    if int(features.get("layer_target", 0)) != 1:
        unsupported.append("exact_model_supports_one_floor_layer_only")
    if str(features.get("reservation_mode", "unknown")) != "absent":
        unsupported.append("exact_model_does_not_cover_top_reservations")
    if int(features.get("retained_variant_target", 0)) != 1:
        unsupported.append("exact_model_requires_one_retained_local_variant")
    rotation_policy = str(features.get("rotation_policy_target", ""))
    if rotation_policy not in {"permitted", "forbidden_by_benchmark"}:
        unsupported.append("rotation_policy_is_not_explicit")
    if unsupported:
        report = _base_report(
            case,
            INTERNAL_EXACT_ADAPTER_ID,
            INTERNAL_EXACT_VERSION,
            "small_exact_reference",
            status=STATUS_UNSUPPORTED,
            stop_reason="outside_exact_model",
            unsupported_constraints=unsupported,
            exact_model=EXACT_MODEL_ID,
            exact_complete=False,
            recertification=_not_attempted_certificate(),
            solution=None,
            counters={},
            exact_caps=caps,
        )
        return BenchmarkAdapterExecution(report, None)

    lower_bound = _fixed_project_lower_bound(case["project"], rotation_policy)
    if lower_bound is not None:
        report = _base_report(
            case,
            INTERNAL_EXACT_ADAPTER_ID,
            INTERNAL_EXACT_VERSION,
            "small_exact_reference",
            status=STATUS_PROVEN_IMPOSSIBLE,
            stop_reason="exact_fixed_dimension_lower_bound",
            unsupported_constraints=(),
            exact_model=EXACT_MODEL_ID,
            exact_complete=True,
            recertification=_not_attempted_certificate(),
            solution=None,
            counters={"cap_reached": False, "proof": lower_bound},
            exact_caps=caps,
        )
        return BenchmarkAdapterExecution(report, None)
    preparation = prepare_free_3d_problem(case["project"])
    if preparation.problem is None:
        report = _base_report(
            case,
            INTERNAL_EXACT_ADAPTER_ID,
            INTERNAL_EXACT_VERSION,
            "small_exact_reference",
            status=STATUS_INVALID_INPUT,
            stop_reason="product_input_validation_failed",
            unsupported_constraints=preparation.rejection_codes,
            exact_model=EXACT_MODEL_ID,
            exact_complete=True,
            recertification=_not_attempted_certificate(),
            solution=None,
            counters={},
            exact_caps=caps,
        )
        return BenchmarkAdapterExecution(report, None)
    problem = preparation.problem
    if problem.top_inset_zones:
        unsupported.append("resolved_top_reservation_present")
    if any(str(item.get("role", "")) != "container" for item in problem.participants):
        unsupported.append("exact_model_supports_container_bodies_only")
    if len(problem.participants) > caps.max_participants:
        unsupported.append("participant_count_exceeds_exact_scope")
    if unsupported:
        report = _base_report(
            case,
            INTERNAL_EXACT_ADAPTER_ID,
            INTERNAL_EXACT_VERSION,
            "small_exact_reference",
            status=STATUS_UNSUPPORTED,
            stop_reason="outside_exact_model",
            unsupported_constraints=unsupported,
            exact_model=EXACT_MODEL_ID,
            exact_complete=False,
            recertification=_not_attempted_certificate(),
            solution=None,
            counters={},
            exact_caps=caps,
        )
        return BenchmarkAdapterExecution(report, None)

    bodies = tuple(
        _FloorBody(
            participant_id=str(item["id"]),
            role=str(item["role"]),
            name=str(item["name"]),
            local_size_mm=_dimension_tuple(
                item["minimum_local_mm"], "participant.minimum_local_mm"
            ),
        )
        for item in problem.participants
    )
    counters = _ExactCounters()
    certified, rejection_codes = _search_exact_floor(
        problem,
        bodies,
        rotation_policy=rotation_policy,
        caps=caps,
        counters=counters,
    )
    if certified is not None:
        report = _base_report(
            case,
            INTERNAL_EXACT_ADAPTER_ID,
            INTERNAL_EXACT_VERSION,
            "small_exact_reference",
            status=SOLUTION_FOUND,
            stop_reason="certified_feasibility_witness_found",
            unsupported_constraints=(),
            exact_model=EXACT_MODEL_ID,
            exact_complete=True,
            recertification=_certificate_payload(certified.certificate, attempted=True),
            solution=_solution_payload(certified.plan, certified.certificate),
            counters=counters.to_dict(),
            exact_caps=caps,
        )
        return BenchmarkAdapterExecution(report, deepcopy(certified.plan))

    if counters.cap_reached:
        status = STATUS_BOUNDED_UNKNOWN
        stop_reason = "exact_cap_reached_before_exhaustion"
        exact_complete = False
    elif rejection_codes:
        status = STATUS_BOUNDED_UNKNOWN
        stop_reason = "geometric_completions_rejected_by_common_certificate"
        exact_complete = False
    else:
        status = STATUS_PROVEN_IMPOSSIBLE
        stop_reason = "exact_floor_model_exhausted"
        exact_complete = True
    report = _base_report(
        case,
        INTERNAL_EXACT_ADAPTER_ID,
        INTERNAL_EXACT_VERSION,
        "small_exact_reference",
        status=status,
        stop_reason=stop_reason,
        unsupported_constraints=(),
        exact_model=EXACT_MODEL_ID,
        exact_complete=exact_complete,
        recertification=(
            {
                "attempted": counters.recertification_attempts > 0,
                "candidate_digest": None,
                "certified": False,
                "rejection_codes": sorted(rejection_codes),
                "schema_version": None,
            }
            if rejection_codes
            else _not_attempted_certificate()
        ),
        solution=None,
        counters=counters.to_dict(),
        exact_caps=caps,
    )
    return BenchmarkAdapterExecution(report, None)


def _fixed_project_lower_bound(
    project: object,
    rotation_policy: str,
) -> dict[str, object] | None:
    """Prouve certains rejets fixes avec une boîte volontairement généreuse."""

    value = _mapping(project, "case.project")
    box_contract = _mapping(value.get("box"), "case.project.box")
    box = _mapping(
        box_contract.get("inner_dimensions_mm"),
        "case.project.box.inner_dimensions_mm",
    )
    available_x = float(box["x"])
    available_y = float(box["y"])
    available_z = float(box_contract.get("usable_height_mm", box["z"]))
    groups = _mapping_list(
        value.get("container_groups"), "case.project.container_groups"
    )
    fixed: list[tuple[str, tuple[float, float, float]]] = []
    for group in groups:
        modes = _mapping_or_empty(group.get("dimension_modes"))
        locked = _mapping_or_empty(group.get("locked_outer_dimensions_mm"))
        if any(str(modes.get(axis)) != "fixed" for axis in _AXES):
            return None
        if any(
            isinstance(locked.get(axis), bool)
            or not isinstance(locked.get(axis), (int, float))
            for axis in _AXES
        ):
            return None
        fixed.append(
            (
                str(group.get("id", "")),
                tuple(float(locked[axis]) for axis in _AXES),
            )
        )
    for group_id, (size_x, size_y, size_z) in fixed:
        if size_z > available_z + _EPSILON:
            return {
                "available_height_mm": available_z,
                "container_group_id": group_id,
                "kind": "fixed_body_height_bound",
                "required_height_mm": size_z,
            }
        orientations = [(size_x, size_y)]
        if rotation_policy == "permitted":
            orientations.append((size_y, size_x))
        if not any(
            width <= available_x + _EPSILON and depth <= available_y + _EPSILON
            for width, depth in orientations
        ):
            return {
                "available_footprint_mm": {"x": available_x, "y": available_y},
                "container_group_id": group_id,
                "kind": "fixed_body_footprint_bound",
                "required_footprint_mm": {"x": size_x, "y": size_y},
            }
    required_volume = sum(x * y * z for _group_id, (x, y, z) in fixed)
    available_volume = available_x * available_y * available_z
    if required_volume > available_volume + _EPSILON:
        return {
            "available_volume_mm3": round(available_volume, 6),
            "kind": "fixed_volume_bound",
            "required_volume_mm3": round(required_volume, 6),
        }
    required_floor_area = sum(x * y for _group_id, (x, y, _z) in fixed)
    available_floor_area = available_x * available_y
    if required_floor_area > available_floor_area + _EPSILON:
        return {
            "available_floor_area_mm2": round(available_floor_area, 6),
            "kind": "fixed_single_floor_area_bound",
            "required_floor_area_mm2": round(required_floor_area, 6),
        }
    return None

def _search_exact_floor(
    problem: Free3DPreparedProblem,
    bodies: tuple[_FloorBody, ...],
    *,
    rotation_policy: str,
    caps: ExactOracleCaps,
    counters: _ExactCounters,
):
    min_x = _round_mm(problem.box_xy_clearance_mm)
    min_y = _round_mm(problem.box_xy_clearance_mm)
    max_x = _round_mm(problem.box["x"] - problem.box_xy_clearance_mm)
    max_y = _round_mm(problem.box["y"] - problem.box_xy_clearance_mm)
    if max_x <= min_x + _EPSILON or max_y <= min_y + _EPSILON:
        return None, set()
    if any(body.local_size_mm[2] > problem.storage_height_mm + _EPSILON for body in bodies):
        return None, set()
    usable_area = (max_x - min_x) * (max_y - min_y)
    if sum(body.local_size_mm[0] * body.local_size_mm[1] for body in bodies) > usable_area + _EPSILON:
        return None, set()

    seen: set[tuple[object, ...]] = set()
    certificate_rejections: set[str] = set()

    def visit(
        remaining: tuple[_FloorBody, ...],
        placed: tuple[_FloorPlacement, ...],
    ):
        if counters.cap_reached:
            return None
        state_key = (
            tuple(sorted(body.participant_id for body in remaining)),
            tuple(
                sorted(
                    (
                        item.body.participant_id,
                        item.origin_x_mm,
                        item.origin_y_mm,
                        item.world_x_mm,
                        item.world_y_mm,
                        item.rotation_deg_z,
                    )
                    for item in placed
                )
            ),
        )
        if state_key in seen:
            counters.duplicate_states += 1
            return None
        if counters.search_states >= caps.max_search_states:
            counters.cap_reached = True
            return None
        seen.add(state_key)
        counters.search_states += 1
        if not remaining:
            counters.complete_geometries += 1
            counters.recertification_attempts += 1
            candidate_placements = tuple(
                Free3DPlacement(
                    participant_id=item.body.participant_id,
                    role=item.body.role,
                    name=item.body.name,
                    origin_mm=(item.origin_x_mm, item.origin_y_mm, 0.0),
                    world_size_mm=(
                        item.world_x_mm,
                        item.world_y_mm,
                        item.body.local_size_mm[2],
                    ),
                    local_size_mm=item.body.local_size_mm,
                    rotation_deg_z=item.rotation_deg_z,
                    supporting_ids=(),
                    support_coverage_ratio=1.0,
                )
                for item in sorted(placed, key=lambda value: value.body.participant_id)
            )
            strategy = SolverStrategy(INTERNAL_EXACT_FAMILY_ID, INTERNAL_EXACT_VERSION)
            budget = SolverBudget(
                INTERNAL_EXACT_FAMILY_ID,
                "exact-small",
                tuple(sorted(caps.to_dict().items())),
            )
            certified, rejections = certify_minimal_free_3d_plan(
                problem,
                strategy=strategy,
                budget=budget,
                candidate_id=(
                    "exact-floor-"
                    + str(counters.complete_geometries).zfill(6)
                ),
                placements=candidate_placements,
                empty_spaces=(),
                search_telemetry=counters.to_dict(),
                search_provenance={
                    "exact_model": EXACT_MODEL_ID,
                    "stop_reason": "candidate_common_recertification",
                    "wall_clock_limited": False,
                },
            )
            if certified is not None:
                return certified
            certificate_rejections.update(rejections)
            return None

        ordered = tuple(
            sorted(
                remaining,
                key=lambda body: (
                    -(body.local_size_mm[0] * body.local_size_mm[1]),
                    -body.local_size_mm[2],
                    body.participant_id,
                ),
            )
        )
        duplicate_geometry: set[tuple[float, float, float]] = set()
        for body in ordered:
            if body.local_size_mm in duplicate_geometry:
                continue
            duplicate_geometry.add(body.local_size_mm)
            next_remaining = tuple(
                value for value in remaining if value.participant_id != body.participant_id
            )
            for rotation, width, depth in _orientations(body, rotation_policy):
                x_candidates = {min_x}
                y_candidates = {min_y}
                for item in placed:
                    x_candidates.add(
                        _round_mm(
                            item.origin_x_mm
                            + item.world_x_mm
                            + problem.xy_clearance_mm
                        )
                    )
                    y_candidates.add(
                        _round_mm(
                            item.origin_y_mm
                            + item.world_y_mm
                            + problem.xy_clearance_mm
                        )
                    )
                for y in sorted(y_candidates):
                    for x in sorted(x_candidates):
                        if counters.placement_trials >= caps.max_placement_trials:
                            counters.cap_reached = True
                            return None
                        counters.placement_trials += 1
                        if x + width > max_x + _EPSILON or y + depth > max_y + _EPSILON:
                            continue
                        proposal = _FloorPlacement(body, x, y, width, depth, rotation)
                        if not _floor_separated(
                            proposal,
                            placed,
                            problem.xy_clearance_mm,
                        ):
                            continue
                        counters.feasible_placements += 1
                        result = visit(next_remaining, placed + (proposal,))
                        if result is not None:
                            return result
                        if counters.cap_reached:
                            return None
        return None

    return visit(bodies, ()), certificate_rejections


def _orientations(
    body: _FloorBody,
    rotation_policy: str,
) -> tuple[tuple[int, float, float], ...]:
    x, y, _z = body.local_size_mm
    result = [(0, x, y)]
    if rotation_policy == "permitted" and abs(x - y) > _EPSILON:
        result.append((90, y, x))
    return tuple(result)


def _floor_separated(
    candidate: _FloorPlacement,
    placed: tuple[_FloorPlacement, ...],
    clearance_mm: float,
) -> bool:
    for other in placed:
        separated = (
            candidate.origin_x_mm + candidate.world_x_mm + clearance_mm
            <= other.origin_x_mm + _EPSILON
            or other.origin_x_mm + other.world_x_mm + clearance_mm
            <= candidate.origin_x_mm + _EPSILON
            or candidate.origin_y_mm + candidate.world_y_mm + clearance_mm
            <= other.origin_y_mm + _EPSILON
            or other.origin_y_mm + other.world_y_mm + clearance_mm
            <= candidate.origin_y_mm + _EPSILON
        )
        if not separated:
            return False
    return True


def _normalize_case(case: object) -> dict[str, object]:
    value = deepcopy(_mapping(case, "case"))
    case_id = str(value.get("case_id", ""))
    if not case_id:
        raise SolverBenchmarkAdapterError("Benchmark case_id is required.")
    normalized = normalize_project_draft(value.get("project")).project
    digest = str(value.get("project_digest", ""))
    if canonical_digest(normalized) != digest:
        raise SolverBenchmarkAdapterError("Benchmark project digest mismatch.")
    settings = _mapping(value.get("solver_settings"), "case.solver_settings")
    if str(settings.get("method", "auto")) != "auto":
        raise SolverBenchmarkAdapterError("Only the auto benchmark method is supported.")
    effort = str(settings.get("effort", ""))
    if effort not in {"quick", "normal", "deep"}:
        raise SolverBenchmarkAdapterError("Unsupported benchmark effort profile.")
    generated = isinstance(value.get("features"), Mapping) and isinstance(
        value.get("recipe"), Mapping
    )
    value["project"] = normalized
    value["generated_case"] = generated
    value["split"] = str(value.get("split", "regression"))
    value["family"] = str(value.get("family", "regression"))
    value["features"] = deepcopy(_mapping_or_empty(value.get("features")))
    value["solver_settings"] = deepcopy(settings)
    return value


def _base_report(
    case: Mapping[str, object],
    adapter_id: str,
    adapter_version: str,
    adapter_kind: str,
    *,
    status: str,
    stop_reason: str,
    unsupported_constraints,
    exact_model: str | None,
    exact_complete: bool,
    recertification: Mapping[str, object],
    solution: Mapping[str, object] | None,
    counters: Mapping[str, object],
    exact_caps: ExactOracleCaps | None = None,
) -> dict[str, object]:
    report: dict[str, object] = {
        "schema_version": ADAPTER_RESULT_SCHEMA_V1,
        "adapter": {
            "adapter_id": adapter_id,
            "adapter_kind": adapter_kind,
            "external_dependency_count": 0,
            "protocol_schema_version": ADAPTER_PROTOCOL_SCHEMA_V1,
            "version": adapter_version,
        },
        "case": {
            "case_id": case["case_id"],
            "family": case["family"],
            "project_digest": case["project_digest"],
            "split": case["split"],
        },
        "status": status,
        "stop_reason": stop_reason,
        "unsupported_constraints": sorted(str(value) for value in unsupported_constraints),
        "exact": {
            "caps": exact_caps.to_dict() if exact_caps is not None else None,
            "complete_for_declared_model": exact_complete,
            "model": exact_model,
        },
        "recertification": deepcopy(dict(recertification)),
        "solution": deepcopy(dict(solution)) if solution is not None else None,
        "counters": deepcopy(dict(counters)),
        "invariants": {
            "candidate_count_at_most_two": True,
            "external_dependency_count": 0,
            "fusion_runtime_invocation_count": 0,
            "oracle_payload_consumed_by_adapter": False,
            "product_solver_routing_changed": False,
            "solution_requires_fresh_bgig_certificate": True,
        },
    }
    report["deterministic_digest"] = canonical_digest(report)
    return report


def _solution_payload(
    plan: Mapping[str, object],
    certificate: ValidationCertificate,
) -> dict[str, object]:
    placements = _mapping_list(plan.get("placements"), "plan.placements")
    minimal = _mapping(plan.get("minimal_layout"), "plan.minimal_layout")
    return {
        "candidate_digest": certificate.candidate_digest,
        "certificate_schema_version": certificate.schema_version,
        "certified": certificate.certified,
        "metrics": deepcopy(_mapping_or_empty(minimal.get("metrics"))),
        "placement_count": len(placements),
        "placement_digest": canonical_digest(
            [
                {
                    "id": item.get("id") or item.get("placement_id"),
                    "origin_mm": item.get("origin_mm"),
                    "rotation_deg_z": item.get("rotation_deg_z"),
                    "world_size_mm": item.get("world_size_mm"),
                }
                for item in sorted(
                    placements,
                    key=lambda value: str(value.get("id") or value.get("placement_id")),
                )
            ]
        ),
        "plan_digest": plan.get("plan_digest"),
        "rotation_count": sum(
            int(int(item.get("rotation_deg_z", 0)) != 0) for item in placements
        ),
    }


def _certificate_payload(
    certificate: ValidationCertificate,
    *,
    attempted: bool,
) -> dict[str, object]:
    return {
        "attempted": attempted,
        "candidate_digest": certificate.candidate_digest,
        "certified": certificate.certified,
        "rejection_codes": list(certificate.rejection_codes),
        "schema_version": certificate.schema_version,
    }


def _not_attempted_certificate() -> dict[str, object]:
    return {
        "attempted": False,
        "candidate_digest": None,
        "certified": False,
        "rejection_codes": [],
        "schema_version": None,
    }


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise SolverBenchmarkAdapterError(f"{field} must be an object.")
    return dict(value)


def _mapping_or_empty(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _mapping_list(value: object, field: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise SolverBenchmarkAdapterError(f"{field} must be a list of objects.")
    return [dict(item) for item in value]


def _dimension_tuple(value: object, field: str) -> tuple[float, float, float]:
    dimensions = _mapping(value, field)
    result = tuple(float(dimensions[axis]) for axis in _AXES)
    if any(number < 0.0 for number in result):
        raise SolverBenchmarkAdapterError(f"{field} must be non-negative.")
    return result


def _is_digest(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _round_mm(value: float) -> float:
    return round(float(value), 6)
