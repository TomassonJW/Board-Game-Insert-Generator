"""Réutilisation locale pré-finalisation d'un agencement minimal P64-L04A.

Ce module ne lance jamais le solveur global. Il tente de reconstruire une
variante locale certifiée dans l'enveloppe déjà placée, puis repasse le plan
monde inchangé par le certificat minimal commun.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.container_internal_variants import (
    CavitySnapshot,
    ContainerInternalVariant,
    ContainerInternalVariantDraft,
    ContainerVariantFrontier,
    VariantProvenance,
    _cavity_snapshot,
    certify_container_variant_draft,
    compute_variant_geometry_digest,
)
from board_game_insert_generator.container_variant_global_search import (
    _participants_with_variant_options,
)
from board_game_insert_generator.free_3d_beam_solver import VariantFree3DPlacement
from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.free_3d_plan_adapter import (
    certify_minimal_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_project_state import (
    STAGE_CONTAINER_FRONTIER,
    build_project_dependency_snapshot,
    canonical_digest,
)
from board_game_insert_generator.minimal_layout_solver import (
    MINIMAL_LAYOUT_FAMILY_ID,
    MINIMAL_LAYOUT_SOLVER_VERSION,
    _minimal_budget,
    _rebuild_empty_spaces,
)
from board_game_insert_generator.partition_solver import _digest as _partition_digest
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_contract import SolverStrategy


LOCAL_LAYOUT_REUSE_SCHEMA_V1 = "bgig.incremental_local_layout_reuse.v1"
LOCAL_LAYOUT_REUSE_FAMILY_ID = "incremental_local_layout_reuse"
LOCAL_LAYOUT_REUSE_VERSION = "p64-l04a-v1"
INCREMENTAL_FIXED_ENVELOPE_PRODUCER_ID = "incremental_fixed_envelope_v1"
INCREMENTAL_FIXED_ENVELOPE_PRODUCER_VERSION = "1"

STATUS_NOT_ATTEMPTED = "not_attempted"
STATUS_PLACEMENT_REUSED = "placement_reused"
STATUS_GLOBAL_SOLVE_REQUIRED = "global_solve_required"
STATUS_STALE_OR_CANCELLED = "stale_or_cancelled"

_AXES = ("x", "y", "z")
_EPSILON = 0.0001


@dataclass(frozen=True)
class LocalReuseBudget:
    """Caps déterministes de la seule recherche locale."""

    max_changed_containers: int = 4
    max_inserted_cavities_per_container: int = 8
    max_positions_per_cavity: int = 128
    max_search_states_per_container: int = 1024

    def __post_init__(self) -> None:
        if any(value <= 0 for value in self.to_dict().values()):
            raise ValueError("Local reuse budget caps must be positive.")

    def to_dict(self) -> dict[str, int]:
        return {
            "max_changed_containers": self.max_changed_containers,
            "max_inserted_cavities_per_container": (
                self.max_inserted_cavities_per_container
            ),
            "max_positions_per_cavity": self.max_positions_per_cavity,
            "max_search_states_per_container": self.max_search_states_per_container,
        }


@dataclass(frozen=True)
class IncrementalLayoutReuseAttempt:
    """Résultat public compact et éventuel plan recertifié."""

    partition: dict[str, object] | None
    report: dict[str, object]


def empty_local_reuse_report(
    *,
    status: str = STATUS_NOT_ATTEMPTED,
    stop_reason: str = "no_eligible_local_edit",
    budget: LocalReuseBudget | None = None,
) -> dict[str, object]:
    selected_budget = budget or LocalReuseBudget()
    return {
        "schema_version": LOCAL_LAYOUT_REUSE_SCHEMA_V1,
        "status": status,
        "placement_reused": False,
        "world_placements_changed": False,
        "global_solver_invocation_count": 0,
        "local_recertification_attempt_count": 0,
        "changed_container_group_ids": [],
        "producer_id": INCREMENTAL_FIXED_ENVELOPE_PRODUCER_ID,
        "producer_version": INCREMENTAL_FIXED_ENVELOPE_PRODUCER_VERSION,
        "budget": selected_budget.to_dict(),
        "counters": {
            "search_states": 0,
            "positions_tested": 0,
            "fixed_envelope_variants_certified": 0,
            "same_envelope_frontier_fallbacks": 0,
            "global_recertification_count": 0,
        },
        "stop_reason": stop_reason,
        "source_plan_digest": "",
        "result_plan_digest": "",
    }


def attempt_incremental_minimal_layout_reuse(
    previous_project: object,
    current_project: object,
    previous_plan: Mapping[str, object],
    *,
    container_frontiers: Sequence[ContainerVariantFrontier],
    effort_profile: str,
    budget: LocalReuseBudget | None = None,
) -> IncrementalLayoutReuseAttempt:
    """Recertifier localement un plan sans appeler la recherche globale."""

    selected_budget = budget or LocalReuseBudget()
    report = empty_local_reuse_report(budget=selected_budget)
    previous = normalize_project_draft(previous_project).project
    current = normalize_project_draft(current_project).project
    previous_snapshot = build_project_dependency_snapshot(previous)
    current_snapshot = build_project_dependency_snapshot(current)
    same_group_ids = (
        previous_snapshot.container_group_ids
        == current_snapshot.container_group_ids
    )
    changed_groups = (
        tuple(
            group_id
            for group_id in current_snapshot.container_group_ids
            if canonical_digest(
                dict(
                    previous_snapshot.local_dependencies(
                        STAGE_CONTAINER_FRONTIER,
                        group_id,
                    )
                )
            )
            != canonical_digest(
                dict(
                    current_snapshot.local_dependencies(
                        STAGE_CONTAINER_FRONTIER,
                        group_id,
                    )
                )
            )
        )
        if same_group_ids
        else ()
    )
    report["changed_container_group_ids"] = list(changed_groups)
    report["source_plan_digest"] = str(previous_plan.get("plan_digest", ""))

    if previous_snapshot.project_digest == current_snapshot.project_digest:
        return _failed(report, STATUS_NOT_ATTEMPTED, "project_unchanged")
    if (
        previous_snapshot.box_context_digest != current_snapshot.box_context_digest
        or previous_snapshot.top_reservation_digest
        != current_snapshot.top_reservation_digest
        or previous_snapshot.solver_settings_digest
        != current_snapshot.solver_settings_digest
    ):
        return _failed(report, STATUS_NOT_ATTEMPTED, "global_dependency_changed")
    if (
        not same_group_ids
        or [dict(value) for value in previous["container_groups"]]
        != [dict(value) for value in current["container_groups"]]
        or [dict(value) for value in previous["fill_elements"]]
        != [dict(value) for value in current["fill_elements"]]
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "container_set_or_contract_changed",
        )
    if not changed_groups:
        return _failed(report, STATUS_NOT_ATTEMPTED, "no_changed_container")
    if len(changed_groups) > selected_budget.max_changed_containers:
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "changed_container_cap_reached",
        )
    if not _previous_plan_is_certified(previous_plan):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "source_plan_not_certified",
        )

    preparation = prepare_free_3d_problem(current)
    if preparation.problem is None:
        report["rejection_codes"] = list(preparation.rejection_codes)
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "current_problem_rejected",
        )
    base_problem = preparation.problem
    frontier_by_group = {
        frontier.container_group_id: frontier for frontier in container_frontiers
    }
    expected_groups = set(current_snapshot.container_group_ids)
    if set(frontier_by_group) != expected_groups or len(frontier_by_group) != len(
        container_frontiers
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "frontier_set_incomplete",
        )
    if any(
        frontier.budget.effort_profile != effort_profile
        or not frontier.variants
        or any(
            not variant.local_certificate.certified
            for variant in frontier.variants
        )
        for frontier in container_frontiers
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "frontier_contract_rejected",
        )

    derived = derive_container_plan(
        current,
        max_container_height_mm=base_problem.storage_height_mm,
    )
    containers = {
        str(value["container_group_id"]): dict(value)
        for value in _mappings(derived["containers"])
    }
    groups = {
        str(value["id"]): dict(value) for value in current["container_groups"]
    }
    previous_placements = {
        str(value["id"]): dict(value)
        for value in _mappings(previous_plan["placements"])
    }
    participant_ids = {str(value["id"]) for value in base_problem.participants}
    if set(previous_placements) != participant_ids:
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "world_body_set_changed",
        )

    counters = report["counters"]
    assert isinstance(counters, dict)
    selected_variants: dict[str, ContainerInternalVariant] = {}
    updated_frontiers: list[ContainerVariantFrontier] = []
    for group_id in sorted(expected_groups):
        placement = next(
            (
                value
                for value in previous_placements.values()
                if str(value.get("container_group_id", "")) == group_id
            ),
            None,
        )
        if placement is None:
            return _failed(
                report,
                STATUS_GLOBAL_SOLVE_REQUIRED,
                "source_container_placement_missing",
            )
        frontier = frontier_by_group[group_id]
        old_variant = _mapping(
            placement.get("container_internal_variant_v1", {})
        )
        exact = next(
            (
                value
                for value in frontier.variants
                if value.geometry_digest
                == str(old_variant.get("geometry_digest", ""))
            ),
            None,
        )
        if exact is not None:
            selected = exact
        else:
            selected = _fixed_envelope_variant(
                containers[group_id],
                groups[group_id],
                placement,
                selected_budget,
                counters,
            )
            if selected is not None:
                counters["fixed_envelope_variants_certified"] += 1
            else:
                selected = _same_envelope_frontier_variant(
                    frontier,
                    placement,
                )
                if selected is not None:
                    counters["same_envelope_frontier_fallbacks"] += 1
        if selected is None:
            return _failed(
                report,
                STATUS_GLOBAL_SOLVE_REQUIRED,
                "fixed_envelope_rejected",
            )
        selected_variants[group_id] = selected
        variants = tuple(
            sorted(
                {
                    value.geometry_digest: value
                    for value in (*frontier.variants, selected)
                }.values(),
                key=lambda value: (value.variant_id, value.geometry_digest),
            )
        )
        updated_frontiers.append(replace(frontier, variants=variants))

    frontiers = tuple(
        sorted(updated_frontiers, key=lambda value: value.container_group_id)
    )
    participants = _participants_with_variant_options(
        base_problem.participants,
        frontiers,
    )
    problem = replace(
        base_problem,
        participants=participants,
        container_variant_frontiers=frontiers,
    )
    placements = _reused_world_placements(
        problem.participants,
        previous_placements,
        selected_variants,
    )
    if placements is None:
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "world_placement_contract_changed",
        )

    solver_budget = _minimal_budget(effort_profile)
    spaces = _rebuild_empty_spaces(placements, problem, solver_budget)
    counters["global_recertification_count"] = 1
    report["local_recertification_attempt_count"] = 1
    provenance = {
        "schema_version": LOCAL_LAYOUT_REUSE_SCHEMA_V1,
        "family_id": LOCAL_LAYOUT_REUSE_FAMILY_ID,
        "family_version": LOCAL_LAYOUT_REUSE_VERSION,
        "producer_id": INCREMENTAL_FIXED_ENVELOPE_PRODUCER_ID,
        "producer_version": INCREMENTAL_FIXED_ENVELOPE_PRODUCER_VERSION,
        "effort_profile": effort_profile,
        "source_plan_digest": report["source_plan_digest"],
        "source_project_digest": previous_snapshot.project_digest,
        "result_project_digest": current_snapshot.project_digest,
        "changed_container_group_ids": list(changed_groups),
        "budget": selected_budget.to_dict(),
        "counters": deepcopy(counters),
        "global_solver_invocation_count": 0,
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
        "world_placements_changed": False,
    }
    selection_mode = (
        "same_envelope_frontier_fallback"
        if int(counters["same_envelope_frontier_fallbacks"]) > 0
        else "fixed_envelope"
    )
    provenance["selection_mode"] = selection_mode
    candidate_id = "local-reuse-" + canonical_digest(provenance)[:16]
    certified, rejection_codes = certify_minimal_free_3d_plan(
        problem,
        strategy=SolverStrategy(
            MINIMAL_LAYOUT_FAMILY_ID,
            MINIMAL_LAYOUT_SOLVER_VERSION,
        ),
        budget=solver_budget,
        candidate_id=candidate_id,
        placements=placements,
        empty_spaces=spaces,
        search_telemetry=deepcopy(counters),
        search_provenance=provenance,
    )
    if certified is None:
        report["rejection_codes"] = list(rejection_codes)
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "global_recertification_rejected",
        )

    partition = certified.plan
    if _world_signature(previous_plan) != _world_signature(partition):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "world_placements_changed",
        )
    report.update(
        {
            "status": STATUS_PLACEMENT_REUSED,
            "placement_reused": True,
            "world_placements_changed": False,
            "stop_reason": f"{selection_mode}_plan_recertified",
            "selection_mode": selection_mode,
            "result_plan_digest": str(partition["plan_digest"]),
        }
    )
    return IncrementalLayoutReuseAttempt(
        deepcopy(partition),
        deepcopy(report),
    )



def _fixed_envelope_variant(
    source_container: Mapping[str, object],
    group: Mapping[str, object],
    previous_placement: Mapping[str, object],
    budget: LocalReuseBudget,
    counters: dict[str, object],
) -> ContainerInternalVariant | None:
    if str(source_container.get("status", "")) != "ready":
        return None
    outer = _dimension_tuple(previous_placement.get("final_outer_dimensions_mm"))
    wall = float(source_container["wall_thickness_mm"])
    floor = float(source_container["floor_thickness_mm"])
    old_origins = {
        str(value.get("cavity_id", value.get("id", ""))): _dimension_tuple(
            value.get("local_origin_mm")
        )
        for value in _mappings(previous_placement.get("cavity_layout", []))
    }
    placed: list[CavitySnapshot] = []
    pending: list[CavitySnapshot] = []
    for compartment in _mappings(source_container["compartments"]):
        cavity_id = str(compartment["id"])
        if cavity_id in old_origins:
            placed.append(
                _cavity_snapshot(
                    compartment,
                    origin=old_origins[cavity_id],
                )
            )
        else:
            pending.append(_cavity_snapshot(compartment))

    if len(pending) > budget.max_inserted_cavities_per_container:
        return None
    if any(not _cavity_fits(value, placed[:index] + placed[index + 1 :], outer, wall) for index, value in enumerate(placed)):
        return None
    ordered_pending = sorted(
        pending,
        key=lambda value: (
            -max(value.inner_dimensions_mm),
            -(value.inner_dimensions_mm[0] * value.inner_dimensions_mm[1]),
            -value.inner_dimensions_mm[2],
            value.cavity_id,
        ),
    )
    state_start = int(counters["search_states"])

    def search(
        index: int,
        current: list[CavitySnapshot],
    ) -> ContainerInternalVariant | None:
        if (
            int(counters["search_states"]) - state_start
            >= budget.max_search_states_per_container
        ):
            counters["budget_exhausted"] = True
            return None
        counters["search_states"] = int(counters["search_states"]) + 1
        if index == len(ordered_pending):
            return _certified_fixed_draft(
                source_container,
                group,
                outer,
                tuple(sorted(current, key=lambda value: value.cavity_id)),
                wall,
                floor,
            )
        cavity = ordered_pending[index]
        origins = _candidate_origins(cavity, current, outer, wall, floor)
        for origin in origins[: budget.max_positions_per_cavity]:
            counters["positions_tested"] = int(counters["positions_tested"]) + 1
            candidate = replace(cavity, local_origin_mm=origin)
            if not _cavity_fits(candidate, current, outer, wall):
                continue
            result = search(index + 1, [*current, candidate])
            if result is not None:
                return result
        return None

    return search(0, placed)


def _certified_fixed_draft(
    source_container: Mapping[str, object],
    group: Mapping[str, object],
    outer: tuple[float, float, float],
    cavities: tuple[CavitySnapshot, ...],
    wall: float,
    floor: float,
) -> ContainerInternalVariant | None:
    group_id = str(source_container["container_group_id"])
    provenance = (
        VariantProvenance(
            INCREMENTAL_FIXED_ENVELOPE_PRODUCER_ID,
            INCREMENTAL_FIXED_ENVELOPE_PRODUCER_VERSION,
            "preserve_existing_origins_then_contact_positions",
        ),
    )
    draft = ContainerInternalVariantDraft(
        container_group_id=group_id,
        variant_id="pending_digest",
        geometry_digest="",
        canonical=False,
        provenance=provenance,
        minimum_outer_envelope_mm=outer,
        cavities=cavities,
        wall_thickness_mm=wall,
        floor_thickness_mm=floor,
        cavity_layout_frame="minimum_outer_envelope.local",
        row_count=len({value.local_origin_mm[1] for value in cavities}),
        internal_separator_count=max(0, len(cavities) - 1),
        automatic_body_count=0,
        generation_index=0,
    )
    digest = compute_variant_geometry_digest(draft)
    draft = replace(
        draft,
        variant_id=f"{group_id}:incremental:{digest[:16]}",
        geometry_digest=digest,
    )
    variant = certify_container_variant_draft(draft, source_container, group)
    return variant if variant.local_certificate.certified else None


def _candidate_origins(
    cavity: CavitySnapshot,
    placed: Sequence[CavitySnapshot],
    outer: tuple[float, float, float],
    wall: float,
    floor: float,
) -> tuple[tuple[float, float, float], ...]:
    width, depth, _ = cavity.inner_dimensions_mm
    xs = {wall, outer[0] - wall - width}
    ys = {wall, outer[1] - wall - depth}
    for value in placed:
        x, y, _ = value.local_origin_mm
        size_x, size_y, _ = value.inner_dimensions_mm
        xs.update((x + size_x + wall, x - width - wall))
        ys.update((y + size_y + wall, y - depth - wall))
    candidates = {
        (_round_mm(x), _round_mm(y), _round_mm(floor))
        for x in xs
        for y in ys
        if x + _EPSILON >= wall
        and y + _EPSILON >= wall
        and x + width + wall <= outer[0] + _EPSILON
        and y + depth + wall <= outer[1] + _EPSILON
    }
    return tuple(
        sorted(
            candidates,
            key=lambda value: (
                value[1],
                value[0],
                value[2],
            ),
        )
    )


def _cavity_fits(
    candidate: CavitySnapshot,
    placed: Sequence[CavitySnapshot],
    outer: tuple[float, float, float],
    wall: float,
) -> bool:
    x, y, z = candidate.local_origin_mm
    width, depth, height = candidate.inner_dimensions_mm
    if (
        x + _EPSILON < wall
        or y + _EPSILON < wall
        or x + width + wall > outer[0] + _EPSILON
        or y + depth + wall > outer[1] + _EPSILON
        or z + height > outer[2] + _EPSILON
    ):
        return False
    for other in placed:
        other_x, other_y, _ = other.local_origin_mm
        other_width, other_depth, _ = other.inner_dimensions_mm
        gap_x = max(
            other_x - (x + width),
            x - (other_x + other_width),
        )
        gap_y = max(
            other_y - (y + depth),
            y - (other_y + other_depth),
        )
        if gap_x < -_EPSILON and gap_y < -_EPSILON:
            return False
        if max(gap_x, gap_y) + _EPSILON < wall:
            return False
    return True


def _same_envelope_frontier_variant(
    frontier: ContainerVariantFrontier,
    previous_placement: Mapping[str, object],
) -> ContainerInternalVariant | None:
    outer = _dimension_tuple(previous_placement.get("final_outer_dimensions_mm"))
    candidates = [
        value
        for value in frontier.variants
        if _same_dimensions(value.draft.minimum_outer_envelope_mm, outer)
    ]
    return min(
        candidates,
        key=lambda value: (value.variant_id, value.geometry_digest),
        default=None,
    )


def _reused_world_placements(
    participants: Sequence[Mapping[str, object]],
    previous_placements: Mapping[str, Mapping[str, object]],
    selected_variants: Mapping[str, ContainerInternalVariant],
) -> tuple[Free3DPlacement, ...] | None:
    result: list[Free3DPlacement] = []
    for participant in sorted(participants, key=lambda value: str(value["id"])):
        participant_id = str(participant["id"])
        previous = previous_placements.get(participant_id)
        if previous is None:
            return None
        origin = _dimension_tuple(previous.get("origin_mm"))
        world = _dimension_tuple(previous.get("world_size_mm"))
        local = _dimension_tuple(previous.get("final_outer_dimensions_mm"))
        rotation = int(previous.get("rotation_deg_z", 0))
        expected_world = (
            (local[1], local[0], local[2])
            if rotation == 90
            else local
        )
        if not _same_dimensions(world, expected_world):
            return None
        base = {
            "participant_id": participant_id,
            "role": str(participant["role"]),
            "name": str(previous.get("name", participant.get("name", participant_id))),
            "origin_mm": origin,
            "world_size_mm": world,
            "local_size_mm": local,
            "rotation_deg_z": rotation,
            "supporting_ids": (),
            "support_coverage_ratio": 1.0,
        }
        if str(participant["role"]) == "container":
            group_id = str(participant["container_group_id"])
            variant = selected_variants.get(group_id)
            if variant is None or not _same_dimensions(
                variant.draft.minimum_outer_envelope_mm,
                local,
            ):
                return None
            result.append(
                VariantFree3DPlacement(
                    **base,
                    container_variant_id=variant.variant_id,
                    container_variant_digest=variant.geometry_digest,
                    container_variant_canonical=variant.canonical,
                )
            )
        else:
            minimum = _dimension_tuple(participant.get("minimum_local_mm"))
            if not _same_dimensions(local, minimum):
                return None
            result.append(Free3DPlacement(**base))
    return tuple(result)


def _world_signature(plan: Mapping[str, object]) -> str:
    payload = [
        {
            "id": str(value["id"]),
            "role": str(value["role"]),
            "origin_mm": deepcopy(value["origin_mm"]),
            "world_size_mm": deepcopy(value["world_size_mm"]),
            "final_outer_dimensions_mm": deepcopy(
                value["final_outer_dimensions_mm"]
            ),
            "rotation_deg_z": int(value["rotation_deg_z"]),
        }
        for value in sorted(
            _mappings(plan.get("placements", [])),
            key=lambda item: str(item["id"]),
        )
    ]
    return canonical_digest(payload)


def _previous_plan_is_certified(plan: Mapping[str, object]) -> bool:
    digest_payload = deepcopy(dict(plan))
    recorded_plan_digest = str(digest_payload.pop("plan_digest", ""))
    if (
        not recorded_plan_digest
        or _partition_digest(digest_payload) != recorded_plan_digest
    ):
        return False
    summary = _mapping(plan.get("summary", {}))
    minimal = _mapping(plan.get("minimal_layout", {}))
    certificate = _mapping(minimal.get("global_certificate", {}))
    variant_certificate = _mapping(
        minimal.get("container_variant_certificate", {})
    )
    placements = plan.get("placements")
    return bool(
        summary.get("status") == "constructed"
        and summary.get("placement_certified") is True
        and minimal.get("artifact_kind") == "minimal_layout"
        and minimal.get("finalization_applied") is False
        and certificate.get("certified") is True
        and (
            not variant_certificate
            or variant_certificate.get("certified") is True
        )
        and isinstance(placements, Sequence)
        and not isinstance(placements, (str, bytes))
    )


def _failed(
    report: Mapping[str, object],
    status: str,
    stop_reason: str,
) -> IncrementalLayoutReuseAttempt:
    payload = deepcopy(dict(report))
    payload.update(
        {
            "status": status,
            "placement_reused": False,
            "world_placements_changed": False,
            "stop_reason": stop_reason,
            "result_plan_digest": "",
        }
    )
    return IncrementalLayoutReuseAttempt(None, payload)


def _dimension_tuple(value: object) -> tuple[float, float, float]:
    raw = _mapping(value)
    return tuple(_round_mm(float(raw[axis])) for axis in _AXES)


def _same_dimensions(
    left: Sequence[float],
    right: Sequence[float],
) -> bool:
    return all(
        abs(float(left[index]) - float(right[index])) <= _EPSILON
        for index in range(3)
    )


def _round_mm(value: float) -> float:
    return round(float(value), 4)


def _mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]
