"""Insertion incrémentale bornée d'un nouveau conteneur dans le vide global.

Le producteur conserve tous les placements certifiés existants, énumère des
positions de contact déterministes pour un seul nouveau conteneur, puis soumet
le plan complet au certificat minimal commun. Il n'appelle jamais le
portefeuille de solveurs globaux et ne matérialise rien.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from itertools import product
from typing import Mapping, Sequence

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.container_internal_variants import (
    ContainerInternalVariant,
    ContainerVariantFrontier,
)
from board_game_insert_generator.container_variant_global_search import (
    _participants_with_variant_options,
)
from board_game_insert_generator.free_3d_beam_solver import VariantFree3DPlacement
from board_game_insert_generator.free_3d_plan_adapter import (
    certify_minimal_free_3d_plan,
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_layout_reuse import (
    LocalReuseBudget,
    _fixed_envelope_variant,
    _previous_plan_is_certified,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import (
    MINIMAL_LAYOUT_FAMILY_ID,
    MINIMAL_LAYOUT_SOLVER_VERSION,
    _minimal_budget,
    _placements_from_certified_plan,
    _rebuild_empty_spaces,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_contract import (
    SolverStrategy,
    _placement_clearance,
    validate_placement_geometry,
)


GLOBAL_VOID_REUSE_SCHEMA_V1 = "bgig.incremental_global_void_container_reuse.v1"
GLOBAL_VOID_REUSE_FAMILY_ID = "incremental_global_void_container_reuse"
GLOBAL_VOID_REUSE_VERSION = "p64-l05a-v1"
GLOBAL_VOID_PRODUCER_ID = "fixed_world_contact_insertion_v1"
GLOBAL_VOID_PRODUCER_VERSION = "1"

STATUS_NOT_ATTEMPTED = "not_attempted"
STATUS_CONTAINER_PLACED = "container_placed_in_global_void"
STATUS_GLOBAL_SOLVE_REQUIRED = "global_solve_required"

_AXES = ("x", "y", "z")
_EPSILON = 0.0001


@dataclass(frozen=True)
class GlobalVoidReuseBudget:
    """Caps déterministes de l'insertion d'un seul conteneur."""

    max_new_container_groups: int = 1
    max_variant_options: int = 12
    max_position_trials: int = 16_384
    max_global_recertifications: int = 64

    def __post_init__(self) -> None:
        if any(value <= 0 for value in self.to_dict().values()):
            raise ValueError("Global void reuse budget caps must be positive.")

    def to_dict(self) -> dict[str, int]:
        return {
            "max_new_container_groups": self.max_new_container_groups,
            "max_variant_options": self.max_variant_options,
            "max_position_trials": self.max_position_trials,
            "max_global_recertifications": self.max_global_recertifications,
        }


@dataclass(frozen=True)
class IncrementalGlobalVoidReuseAttempt:
    """Rapport observable et éventuel plan entièrement recertifié."""

    partition: dict[str, object] | None
    report: dict[str, object]


def empty_global_void_reuse_report(
    *,
    status: str = STATUS_NOT_ATTEMPTED,
    stop_reason: str = "no_eligible_new_container",
    budget: GlobalVoidReuseBudget | None = None,
) -> dict[str, object]:
    selected = budget or GlobalVoidReuseBudget()
    return {
        "schema_version": GLOBAL_VOID_REUSE_SCHEMA_V1,
        "status": status,
        "existing_placements_reused": False,
        "existing_world_placements_changed": False,
        "new_world_placement_added": False,
        "global_solver_invocation_count": 0,
        "finalization_invocation_count": 0,
        "fusion_materialization_invocation_count": 0,
        "new_container_group_id": "",
        "new_placement_id": "",
        "producer_id": GLOBAL_VOID_PRODUCER_ID,
        "producer_version": GLOBAL_VOID_PRODUCER_VERSION,
        "budget": selected.to_dict(),
        "counters": {
            "variant_options_considered": 0,
            "position_trials": 0,
            "geometry_admissions": 0,
            "global_recertification_count": 0,
            "existing_variants_reconstructed": 0,
        },
        "stop_reason": stop_reason,
        "source_plan_digest": "",
        "result_plan_digest": "",
        "rejection_codes": [],
    }


def attempt_incremental_global_void_container_reuse(
    previous_project: object,
    current_project: object,
    previous_plan: Mapping[str, object],
    *,
    container_frontiers: Sequence[ContainerVariantFrontier],
    effort_profile: str,
    budget: GlobalVoidReuseBudget | None = None,
) -> IncrementalGlobalVoidReuseAttempt:
    """Insérer un seul nouveau conteneur sans déplacer les voisins existants."""

    selected_budget = budget or GlobalVoidReuseBudget()
    report = empty_global_void_reuse_report(budget=selected_budget)
    report["source_plan_digest"] = str(previous_plan.get("plan_digest", ""))

    previous = normalize_project_draft(previous_project).project
    current = normalize_project_draft(current_project).project
    if canonical_digest(previous) == canonical_digest(current):
        return _failed(report, STATUS_NOT_ATTEMPTED, "project_unchanged")
    if not _same_global_dependencies(previous, current):
        return _failed(report, STATUS_NOT_ATTEMPTED, "global_dependency_changed")

    previous_groups = _by_id(previous.get("container_groups"))
    current_groups = _by_id(current.get("container_groups"))
    new_group_ids = tuple(sorted(set(current_groups) - set(previous_groups)))
    if (
        set(previous_groups) - set(current_groups)
        or len(new_group_ids) != 1
        or len(new_group_ids) > selected_budget.max_new_container_groups
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "new_container_group_set_not_eligible",
        )
    new_group_id = new_group_ids[0]
    report["new_container_group_id"] = new_group_id
    if any(previous_groups[key] != current_groups[key] for key in previous_groups):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "existing_container_contract_changed",
        )
    if previous.get("fill_elements") != current.get("fill_elements"):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "fill_element_set_changed",
        )

    previous_contents = _by_id(previous.get("contents"))
    current_contents = _by_id(current.get("contents"))
    if set(previous_contents) - set(current_contents) or any(
        previous_contents[key] != current_contents[key] for key in previous_contents
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "existing_content_changed",
        )
    inserted_content_ids = set(current_contents) - set(previous_contents)
    if not inserted_content_ids or any(
        str(current_contents[key].get("container_group_id", "")) != new_group_id
        for key in inserted_content_ids
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "new_contents_not_exclusive_to_new_container",
        )
    if any(
        str(value.get("container_group_id", "")) == new_group_id
        for key, value in current_contents.items()
        if key not in inserted_content_ids
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "existing_content_reassigned_to_new_container",
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
    frontiers = tuple(
        sorted(container_frontiers, key=lambda value: value.container_group_id)
    )
    frontier_by_group = {value.container_group_id: value for value in frontiers}
    if (
        set(frontier_by_group) != set(current_groups)
        or len(frontier_by_group) != len(frontiers)
        or any(
            value.budget.effort_profile != effort_profile
            or not value.variants
            or any(not variant.local_certificate.certified for variant in value.variants)
            for value in frontiers
        )
    ):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "frontier_contract_rejected",
        )

    restored = _restore_existing_variants(
        current,
        previous_groups,
        previous_plan,
        frontiers,
        base_problem.storage_height_mm,
        report,
    )
    if restored is None:
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "existing_variant_could_not_be_reconstructed",
        )
    frontiers, reconstructed_by_group = restored
    frontier_by_group = {
        value.container_group_id: value for value in frontiers
    }
    participants = _participants_with_variant_options(
        base_problem.participants,
        frontiers,
    )
    problem = replace(
        base_problem,
        participants=participants,
        container_variant_frontiers=frontiers,
    )
    new_participants = tuple(
        value
        for value in participants
        if str(value.get("container_group_id", "")) == new_group_id
    )
    if len(new_participants) != 1 or str(new_participants[0].get("role")) != "container":
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "new_container_participant_not_unique",
        )
    new_participant = new_participants[0]
    new_placement_id = str(new_participant["id"])
    report["new_placement_id"] = new_placement_id

    old_placements = _placements_from_certified_plan(previous_plan)
    participant_groups = {
        str(value["id"]): str(value.get("container_group_id", ""))
        for value in participants
    }
    old_placements = tuple(
        replace(
            value,
            container_variant_id=reconstructed_by_group[
                participant_groups[value.participant_id]
            ].variant_id,
            container_variant_digest=reconstructed_by_group[
                participant_groups[value.participant_id]
            ].geometry_digest,
            container_variant_canonical=reconstructed_by_group[
                participant_groups[value.participant_id]
            ].canonical,
        )
        if isinstance(value, VariantFree3DPlacement)
        and participant_groups.get(value.participant_id)
        in reconstructed_by_group
        else value
        for value in old_placements
    )
    old_ids = {value.participant_id for value in old_placements}
    expected_old_ids = {
        str(value["id"])
        for value in participants
        if str(value["id"]) != new_placement_id
    }
    if old_ids != expected_old_ids:
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "existing_world_body_set_changed",
        )
    if not _existing_variants_are_available(old_placements, frontier_by_group):
        return _failed(
            report,
            STATUS_GLOBAL_SOLVE_REQUIRED,
            "existing_variant_not_available",
        )

    variants = tuple(
        sorted(
            frontier_by_group[new_group_id].variants,
            key=_variant_rank,
        )[: selected_budget.max_variant_options]
    )
    counters = report["counters"]
    assert isinstance(counters, dict)
    previous_raw_placements = [
        deepcopy(dict(value))
        for value in previous_plan.get("placements", [])
        if isinstance(value, Mapping)
    ]
    source_signature = _placement_signature(previous_raw_placements, old_ids)
    last_rejections: tuple[str, ...] = ()

    for variant in variants:
        counters["variant_options_considered"] = (
            int(counters["variant_options_considered"]) + 1
        )
        local_size = variant.draft.minimum_outer_envelope_mm
        for rotation in _rotations(local_size):
            world_size = (
                (local_size[1], local_size[0], local_size[2])
                if rotation == 90
                else local_size
            )
            raw_template = _candidate_raw_placement(
                new_participant,
                new_placement_id,
                world_size,
                rotation,
                (0.0, 0.0, 0.0),
            )
            origins = _candidate_origins(
                previous_raw_placements,
                raw_template,
                problem.box,
                problem.storage_height_mm,
                problem.xy_clearance_mm,
                problem.box_xy_clearance_mm,
                problem.z_clearance_mm,
            )
            for origin in origins:
                if int(counters["position_trials"]) >= selected_budget.max_position_trials:
                    return _failed(
                        report,
                        STATUS_GLOBAL_SOLVE_REQUIRED,
                        "position_trial_budget_exhausted",
                    )
                counters["position_trials"] = int(counters["position_trials"]) + 1
                raw_candidate = _candidate_raw_placement(
                    new_participant,
                    new_placement_id,
                    world_size,
                    rotation,
                    origin,
                )
                geometry = validate_placement_geometry(
                    [*previous_raw_placements, raw_candidate],
                    problem.box,
                    problem.storage_height_mm,
                    problem.xy_clearance_mm,
                    problem.box_xy_clearance_mm,
                    problem.z_clearance_mm,
                )
                if not all(
                    bool(geometry[key])
                    for key in (
                        "inside_box",
                        "box_xy_clearance_respected",
                        "no_collisions",
                        "clearances_respected",
                    )
                ):
                    continue
                counters["geometry_admissions"] = int(counters["geometry_admissions"]) + 1
                if (
                    int(counters["global_recertification_count"])
                    >= selected_budget.max_global_recertifications
                ):
                    return _failed(
                        report,
                        STATUS_GLOBAL_SOLVE_REQUIRED,
                        "global_recertification_budget_exhausted",
                    )
                candidate = VariantFree3DPlacement(
                    participant_id=new_placement_id,
                    role="container",
                    name=str(new_participant.get("name", new_placement_id)),
                    origin_mm=origin,
                    world_size_mm=world_size,
                    local_size_mm=local_size,
                    rotation_deg_z=rotation,
                    supporting_ids=(),
                    support_coverage_ratio=1.0,
                    container_variant_id=variant.variant_id,
                    container_variant_digest=variant.geometry_digest,
                    container_variant_canonical=variant.canonical,
                )
                placements = (*old_placements, candidate)
                solver_budget = _minimal_budget(effort_profile)
                spaces = _rebuild_empty_spaces(placements, problem, solver_budget)
                counters["global_recertification_count"] = (
                    int(counters["global_recertification_count"]) + 1
                )
                provenance = {
                    "schema_version": GLOBAL_VOID_REUSE_SCHEMA_V1,
                    "family_id": GLOBAL_VOID_REUSE_FAMILY_ID,
                    "family_version": GLOBAL_VOID_REUSE_VERSION,
                    "producer_id": GLOBAL_VOID_PRODUCER_ID,
                    "producer_version": GLOBAL_VOID_PRODUCER_VERSION,
                    "effort_profile": effort_profile,
                    "source_plan_digest": report["source_plan_digest"],
                    "source_project_digest": canonical_digest(previous),
                    "result_project_digest": canonical_digest(current),
                    "new_container_group_id": new_group_id,
                    "new_placement_id": new_placement_id,
                    "selected_variant_id": variant.variant_id,
                    "selected_variant_digest": variant.geometry_digest,
                    "selected_origin_mm": list(origin),
                    "selected_rotation_deg_z": rotation,
                    "budget": selected_budget.to_dict(),
                    "counters": deepcopy(counters),
                    "global_solver_invocation_count": 0,
                    "finalization_invocation_count": 0,
                    "fusion_materialization_invocation_count": 0,
                    "existing_world_placements_changed": False,
                }
                candidate_id = "global-void-reuse-" + canonical_digest(provenance)[:16]
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
                last_rejections = rejection_codes
                if certified is None:
                    continue
                partition = certified.plan
                result_raw = [
                    dict(value)
                    for value in partition.get("placements", [])
                    if isinstance(value, Mapping)
                ]
                if _placement_signature(result_raw, old_ids) != source_signature:
                    report["rejection_codes"] = ["EXISTING_WORLD_PLACEMENTS_CHANGED"]
                    return _failed(
                        report,
                        STATUS_GLOBAL_SOLVE_REQUIRED,
                        "existing_world_placements_changed",
                    )
                report.update(
                    {
                        "status": STATUS_CONTAINER_PLACED,
                        "existing_placements_reused": True,
                        "existing_world_placements_changed": False,
                        "new_world_placement_added": True,
                        "stop_reason": "new_container_inserted_and_plan_recertified",
                        "selected_variant_id": variant.variant_id,
                        "selected_variant_digest": variant.geometry_digest,
                        "selected_origin_mm": list(origin),
                        "selected_rotation_deg_z": rotation,
                        "result_plan_digest": str(partition["plan_digest"]),
                        "rejection_codes": [],
                    }
                )
                return IncrementalGlobalVoidReuseAttempt(
                    deepcopy(partition),
                    deepcopy(report),
                )

    report["rejection_codes"] = list(last_rejections)
    return _failed(
        report,
        STATUS_GLOBAL_SOLVE_REQUIRED,
        "no_certified_global_void_position",
    )


def _restore_existing_variants(
    current: Mapping[str, object],
    previous_groups: Mapping[str, Mapping[str, object]],
    previous_plan: Mapping[str, object],
    frontiers: tuple[ContainerVariantFrontier, ...],
    storage_height_mm: float,
    report: dict[str, object],
) -> tuple[
    tuple[ContainerVariantFrontier, ...],
    dict[str, ContainerInternalVariant],
] | None:
    placements = {
        str(value.get("container_group_id", "")): dict(value)
        for value in previous_plan.get("placements", [])
        if isinstance(value, Mapping)
        and str(value.get("role", "")) == "container"
    }
    derived = derive_container_plan(
        current,
        max_container_height_mm=storage_height_mm,
    )
    containers = {
        str(value["container_group_id"]): dict(value)
        for value in derived.get("containers", [])
        if isinstance(value, Mapping)
    }
    counters = report["counters"]
    assert isinstance(counters, dict)
    reconstructed: dict[str, ContainerInternalVariant] = {}
    updated: list[ContainerVariantFrontier] = []
    for frontier in frontiers:
        group_id = frontier.container_group_id
        if group_id not in previous_groups:
            updated.append(frontier)
            continue
        placement = placements.get(group_id)
        container = containers.get(group_id)
        if placement is None or container is None:
            return None
        old_variant = placement.get("container_internal_variant_v1")
        old_digest = (
            str(old_variant.get("geometry_digest", ""))
            if isinstance(old_variant, Mapping)
            else ""
        )
        if any(
            value.geometry_digest == old_digest
            for value in frontier.variants
        ):
            updated.append(frontier)
            continue
        local_counters: dict[str, object] = {
            "search_states": 0,
            "positions_tested": 0,
            "budget_exhausted": False,
        }
        variant = _fixed_envelope_variant(
            container,
            previous_groups[group_id],
            placement,
            LocalReuseBudget(),
            local_counters,
        )
        if variant is None:
            return None
        variants = tuple(
            sorted(
                {
                    value.geometry_digest: value
                    for value in (*frontier.variants, variant)
                }.values(),
                key=lambda value: (value.variant_id, value.geometry_digest),
            )
        )
        updated.append(replace(frontier, variants=variants))

        reconstructed[group_id] = variant
        counters["existing_variants_reconstructed"] = (
            int(counters["existing_variants_reconstructed"]) + 1
        )
    return (
        tuple(sorted(updated, key=lambda value: value.container_group_id)),
        reconstructed,
    )


def _same_global_dependencies(
    previous: Mapping[str, object],
    current: Mapping[str, object],
) -> bool:
    mutable_keys = {"container_groups", "contents"}
    keys = (set(previous) | set(current)) - mutable_keys
    return all(previous.get(key) == current.get(key) for key in keys)


def _by_id(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, list):
        return {}
    return {
        str(item["id"]): deepcopy(dict(item))
        for item in value
        if isinstance(item, Mapping) and "id" in item
    }


def _existing_variants_are_available(
    placements: Sequence[object],
    frontier_by_group: Mapping[str, ContainerVariantFrontier],
) -> bool:
    by_digest = {
        digest
        for frontier in frontier_by_group.values()
        for value in frontier.variants
        for digest in (value.geometry_digest,)
    }
    return all(
        not isinstance(value, VariantFree3DPlacement)
        or value.container_variant_digest in by_digest
        for value in placements
    )


def _variant_rank(
    variant: ContainerInternalVariant,
) -> tuple[float, float, float, str]:
    x, y, z = variant.draft.minimum_outer_envelope_mm
    return (x * y * z, z, x * y, variant.geometry_digest)


def _rotations(
    local_size: tuple[float, float, float],
) -> tuple[int, ...]:
    return (0,) if abs(local_size[0] - local_size[1]) <= _EPSILON else (0, 90)


def _candidate_raw_placement(
    participant: Mapping[str, object],
    participant_id: str,
    world_size: tuple[float, float, float],
    rotation: int,
    origin: tuple[float, float, float],
) -> dict[str, object]:
    value: dict[str, object] = {
        "id": participant_id,
        "role": "container",
        "name": str(participant.get("name", participant_id)),
        "origin_mm": dict(zip(_AXES, origin)),
        "world_size_mm": dict(zip(_AXES, world_size)),
        "rotation_deg_z": rotation,
    }
    if "external_clearance_effective_v1" in participant:
        value["external_clearance_effective_v1"] = deepcopy(
            participant["external_clearance_effective_v1"]
        )
    return value


def _candidate_origins(
    existing: Sequence[Mapping[str, object]],
    candidate: Mapping[str, object],
    box: Mapping[str, float],
    storage_height_mm: float,
    xy_clearance_mm: float,
    box_xy_clearance_mm: float,
    z_clearance_mm: float,
) -> tuple[tuple[float, float, float], ...]:
    size = _dimensions(candidate["world_size_mm"])
    x_box = _placement_clearance(
        candidate,
        "box_per_side_xy_mm",
        "x",
        box_xy_clearance_mm,
    )
    y_box = _placement_clearance(
        candidate,
        "box_per_side_xy_mm",
        "y",
        box_xy_clearance_mm,
    )
    xs = {x_box, float(box["x"]) - x_box - size[0]}
    ys = {y_box, float(box["y"]) - y_box - size[1]}
    zs = {0.0, storage_height_mm - size[2]}
    for other in existing:
        origin = _dimensions(other.get("origin_mm"))
        other_size = _dimensions(other.get("world_size_mm"))
        gap_x = max(
            _placement_clearance(other, "between_mm", "x", xy_clearance_mm),
            _placement_clearance(candidate, "between_mm", "x", xy_clearance_mm),
        )
        gap_y = max(
            _placement_clearance(other, "between_mm", "y", xy_clearance_mm),
            _placement_clearance(candidate, "between_mm", "y", xy_clearance_mm),
        )
        gap_z = max(
            _placement_clearance(other, "between_mm", "z", z_clearance_mm),
            _placement_clearance(candidate, "between_mm", "z", z_clearance_mm),
        )
        xs.update((origin[0] + other_size[0] + gap_x, origin[0] - gap_x - size[0]))
        ys.update((origin[1] + other_size[1] + gap_y, origin[1] - gap_y - size[1]))
        zs.update((origin[2] + other_size[2] + gap_z, origin[2] - gap_z - size[2]))
    candidates = {
        (_round_mm(x), _round_mm(y), _round_mm(z))
        for x, y, z in product(xs, ys, zs)
        if x >= -_EPSILON
        and y >= -_EPSILON
        and z >= -_EPSILON
        and x + size[0] <= float(box["x"]) + _EPSILON
        and y + size[1] <= float(box["y"]) + _EPSILON
        and z + size[2] <= storage_height_mm + _EPSILON
    }
    return tuple(sorted(candidates, key=lambda value: (value[2], value[1], value[0])))


def _placement_signature(
    placements: Sequence[Mapping[str, object]],
    participant_ids: set[str],
) -> str:
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
        for value in sorted(placements, key=lambda item: str(item["id"]))
        if str(value["id"]) in participant_ids
    ]
    return canonical_digest(payload)


def _dimensions(value: object) -> tuple[float, float, float]:
    if not isinstance(value, Mapping):
        raise TypeError("Expected a three-axis mapping.")
    return tuple(float(value[axis]) for axis in _AXES)


def _round_mm(value: float) -> float:
    return round(float(value), 4)


def _failed(
    report: Mapping[str, object],
    status: str,
    stop_reason: str,
) -> IncrementalGlobalVoidReuseAttempt:
    value = deepcopy(dict(report))
    value.update(
        {
            "status": status,
            "existing_placements_reused": False,
            "existing_world_placements_changed": False,
            "new_world_placement_added": False,
            "stop_reason": stop_reason,
            "result_plan_digest": "",
        }
    )
    return IncrementalGlobalVoidReuseAttempt(None, value)
