"""Pure local-variant boundary for P64-V2H03B.

This module deliberately does not participate in public partition selection.
It reads the established container derivation, builds immutable local geometry
variants, certifies them fail-closed, and returns a bounded Pareto frontier for
future P64-V2H03C consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from math import isfinite, log
from typing import Mapping, Sequence

from board_game_insert_generator.container_derivation import (
    _best_fit_rows,
    _bounded_target_widths,
    _compartment_orderings,
    _next_fit_rows,
    _register_arrangement_candidate,
    derive_container_plan,
)
from board_game_insert_generator.project_v1 import normalize_project_draft


INTERNAL_VARIANT_SCHEMA_V1 = "bgig.container_internal_variants.v1"
LOCAL_CERTIFICATE_SCHEMA_V1 = "bgig.container_local_variant_certificate.v1"
LOCAL_GEOMETRY_CONTRACT_V1 = "container_internal_geometry.v1"
CANONICAL_PRODUCER_ID = "canonical_v1"
RECTANGULAR_RELAYOUT_PRODUCER_ID = "bounded_rectangular_relayout_v1"
PRODUCER_VERSION_V1 = "1"
EFFORT_QUICK = "quick"
EFFORT_NORMAL = "normal"
EFFORT_DEEP = "deep"
_AXES = ("x", "y", "z")
_EPSILON = 0.0001


@dataclass(frozen=True, order=True)
class VariantProvenance:
    """Stable producer identity plus one deterministic generation path."""

    producer_id: str
    producer_version: str
    generation_path: str


@dataclass(frozen=True)
class CavitySnapshot:
    """Immutable local cavity geometry and resolved content semantics."""

    cavity_id: str
    content_id: str
    shape_kind: str
    footprint_policy: str
    local_origin_mm: tuple[float, float, float]
    inner_dimensions_mm: tuple[float, float, float]
    base_dimensions_mm: tuple[float, float, float]
    resolved_dimensions_mm: tuple[float, float, float]
    clearance_values_mm: tuple[float, float, float]
    clearance_sources: tuple[str, str, str]
    quantity_payload: str
    storage_orientation: str
    resolved_orientation: str

    def geometry_payload(self) -> dict[str, object]:
        return {
            "cavity_id": self.cavity_id,
            "content_id": self.content_id,
            "shape_kind": self.shape_kind,
            "footprint_policy": self.footprint_policy,
            "local_origin_mm": self.local_origin_mm,
            "inner_dimensions_mm": self.inner_dimensions_mm,
            "base_dimensions_mm": self.base_dimensions_mm,
            "resolved_dimensions_mm": self.resolved_dimensions_mm,
            "clearance_values_mm": self.clearance_values_mm,
            "clearance_sources": self.clearance_sources,
            "quantity": json.loads(self.quantity_payload),
            "storage_orientation": self.storage_orientation,
            "resolved_orientation": self.resolved_orientation,
        }

    def content_invariant(self) -> tuple[object, ...]:
        """Return every field a relayout producer is forbidden to change."""

        return (
            self.cavity_id,
            self.content_id,
            self.shape_kind,
            self.footprint_policy,
            self.inner_dimensions_mm,
            self.base_dimensions_mm,
            self.resolved_dimensions_mm,
            self.clearance_values_mm,
            self.clearance_sources,
            self.quantity_payload,
            self.storage_orientation,
            self.resolved_orientation,
        )


@dataclass(frozen=True)
class ContainerVariantBudget:
    """Finite observable caps shared by the local and future global lanes."""

    effort_profile: str
    max_generated_variants_per_container: int
    max_certified_variants_per_container: int
    max_retained_variants_per_container: int
    max_variant_options_per_expansion: int
    max_variant_assignment_states: int
    max_variant_placement_trials: int

    def __post_init__(self) -> None:
        values = self.limit_items()
        if any(value < 0 for _, value in values):
            raise ValueError("Container variant budget limits must be non-negative.")
        if any(value == 0 for _, value in values[:3]):
            raise ValueError("Local variant generation, certification and retention need positive caps.")

    def limit_items(self) -> tuple[tuple[str, int], ...]:
        return (
            ("max_generated_variants_per_container", self.max_generated_variants_per_container),
            ("max_certified_variants_per_container", self.max_certified_variants_per_container),
            ("max_retained_variants_per_container", self.max_retained_variants_per_container),
            ("max_variant_options_per_expansion", self.max_variant_options_per_expansion),
            ("max_variant_assignment_states", self.max_variant_assignment_states),
            ("max_variant_placement_trials", self.max_variant_placement_trials),
        )

    def is_at_least_as_permissive_as(self, other: "ContainerVariantBudget") -> bool:
        current = dict(self.limit_items())
        return all(current[name] >= value for name, value in other.limit_items())

    def to_dict(self) -> dict[str, object]:
        return {"effort_profile": self.effort_profile, **dict(self.limit_items())}


@dataclass(frozen=True)
class ContainerInternalVariantDraft:
    """One immutable producer output before admission to the local frontier."""

    container_group_id: str
    variant_id: str
    geometry_digest: str
    canonical: bool
    provenance: tuple[VariantProvenance, ...]
    minimum_outer_envelope_mm: tuple[float, float, float]
    cavities: tuple[CavitySnapshot, ...]
    wall_thickness_mm: float
    floor_thickness_mm: float
    cavity_layout_frame: str
    row_count: int
    internal_separator_count: int
    automatic_body_count: int
    generation_index: int


@dataclass(frozen=True)
class LocalVariantCheck:
    name: str
    passed: bool
    rejection_code: str | None = None


@dataclass(frozen=True)
class LocalVariantCertificate:
    schema_version: str
    geometry_digest: str
    certified: bool
    checks: tuple[LocalVariantCheck, ...]

    @property
    def rejection_codes(self) -> tuple[str, ...]:
        return tuple(
            check.rejection_code
            for check in self.checks
            if not check.passed and check.rejection_code is not None
        )


@dataclass(frozen=True)
class LocalVariantCost:
    canonical_priority: int
    envelope_x_mm: float
    envelope_y_mm: float
    envelope_z_mm: float
    volume_mm3: float
    area_mm2: float
    aspect_penalty: float
    layout_complexity: int

    def dominance_axes(self) -> tuple[float, ...]:
        return (
            self.envelope_x_mm,
            self.envelope_y_mm,
            self.envelope_z_mm,
            self.volume_mm3,
            self.aspect_penalty,
            float(self.layout_complexity),
        )


@dataclass(frozen=True)
class ContainerInternalVariant:
    """Certified local variant admitted or rejected by one authoritative check."""

    draft: ContainerInternalVariantDraft
    provenance: tuple[VariantProvenance, ...]
    local_cost: LocalVariantCost
    local_certificate: LocalVariantCertificate

    @property
    def container_group_id(self) -> str:
        return self.draft.container_group_id

    @property
    def variant_id(self) -> str:
        return self.draft.variant_id

    @property
    def geometry_digest(self) -> str:
        return self.draft.geometry_digest

    @property
    def canonical(self) -> bool:
        return self.draft.canonical


@dataclass(frozen=True)
class RejectedContainerVariant:
    variant: ContainerInternalVariant
    rejection_codes: tuple[str, ...]


@dataclass(frozen=True)
class ContainerVariantFrontier:
    container_group_id: str
    budget: ContainerVariantBudget
    variants: tuple[ContainerInternalVariant, ...]
    rejected: tuple[RejectedContainerVariant, ...]
    generated_count: int
    raw_layout_count: int
    certified_count: int
    duplicate_count: int
    dominated_count: int
    generation_limit_reached: bool
    certification_limit_reached: bool
    retention_limit_reached: bool
    generated_digests: tuple[str, ...]
    certified_digests: tuple[str, ...]


@dataclass(frozen=True)
class InternalVariantRun:
    schema_version: str
    budget: ContainerVariantBudget
    frontiers: tuple[ContainerVariantFrontier, ...]
    skipped_container_group_ids: tuple[str, ...]


def standard_variant_budgets() -> tuple[ContainerVariantBudget, ...]:
    """Return the bounded H03B caps measured against the deterministic corpus."""

    return (
        ContainerVariantBudget(EFFORT_QUICK, 24, 24, 4, 2, 32, 128),
        ContainerVariantBudget(EFFORT_NORMAL, 48, 48, 8, 4, 384, 3_072),
        ContainerVariantBudget(EFFORT_DEEP, 96, 96, 12, 6, 3_072, 36_864),
    )


def variant_budget_for_effort(effort_profile: str) -> ContainerVariantBudget:
    for budget in standard_variant_budgets():
        if budget.effort_profile == effort_profile:
            return budget
    raise ValueError(
        f"Unknown container variant effort profile {effort_profile!r}; expected quick, normal or deep."
    )


def derive_container_internal_variant_frontiers(
    raw_project: object,
    *,
    effort_profile: str = EFFORT_NORMAL,
    max_container_height_mm: float | None = None,
) -> InternalVariantRun:
    """Build internal frontiers without changing the public derivation result."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    plan = derive_container_plan(project, max_container_height_mm=max_container_height_mm)
    groups = {str(value["id"]): value for value in _mappings(project["container_groups"])}
    budget = variant_budget_for_effort(effort_profile)
    frontiers: list[ContainerVariantFrontier] = []
    skipped: list[str] = []
    for container in _mappings(plan["containers"]):
        group_id = str(container["container_group_id"])
        if container.get("outer_dimensions_mm") is None or not _mappings(container["compartments"]):
            skipped.append(group_id)
            continue
        frontiers.append(build_container_variant_frontier(container, groups[group_id], budget))
    return InternalVariantRun(
        schema_version=INTERNAL_VARIANT_SCHEMA_V1,
        budget=budget,
        frontiers=tuple(frontiers),
        skipped_container_group_ids=tuple(skipped),
    )


def build_container_variant_frontier(
    container: Mapping[str, object],
    group: Mapping[str, object],
    budget: ContainerVariantBudget,
) -> ContainerVariantFrontier:
    """Generate, certify, deduplicate and prune one local frontier."""

    canonical = _canonical_draft(container)
    relayouts, raw_layout_count = _rectangular_relayout_drafts(container, budget)
    drafts = (canonical, *relayouts)
    certified: list[ContainerInternalVariant] = []
    rejected: list[RejectedContainerVariant] = []
    certification_limit_reached = False
    for draft in drafts:
        variant = certify_container_variant_draft(draft, container, group)
        if not variant.local_certificate.certified:
            rejected.append(
                RejectedContainerVariant(variant, variant.local_certificate.rejection_codes)
            )
            continue
        if len(certified) >= budget.max_certified_variants_per_container:
            certification_limit_reached = True
            break
        certified.append(variant)

    unique, duplicate_count = _deduplicate_variants(certified)
    pareto = _pareto_frontier(unique)
    retained = _retain_variants(pareto, budget.max_retained_variants_per_container)
    return ContainerVariantFrontier(
        container_group_id=str(container["container_group_id"]),
        budget=budget,
        variants=tuple(retained),
        rejected=tuple(rejected),
        generated_count=len(drafts),
        raw_layout_count=raw_layout_count,
        certified_count=len(certified),
        duplicate_count=duplicate_count,
        dominated_count=len(unique) - len(pareto),
        generation_limit_reached=(1 + raw_layout_count) > budget.max_generated_variants_per_container,
        certification_limit_reached=certification_limit_reached,
        retention_limit_reached=len(pareto) > budget.max_retained_variants_per_container,
        generated_digests=tuple(draft.geometry_digest for draft in drafts),
        certified_digests=tuple(sorted({variant.geometry_digest for variant in certified})),
    )


def certify_container_variant_draft(
    draft: ContainerInternalVariantDraft,
    source_container: Mapping[str, object],
    group: Mapping[str, object],
) -> ContainerInternalVariant:
    """Apply the only local admission certificate; invalid data fails closed."""

    source_cavities = {
        str(value["id"]): _cavity_snapshot(value)
        for value in _mappings(source_container["compartments"])
    }
    candidate_cavities = {value.cavity_id: value for value in draft.cavities}
    source_ids = tuple(sorted(source_cavities))
    candidate_ids = tuple(sorted(candidate_cavities))
    coverage_ok = source_ids == candidate_ids and len(candidate_ids) == len(draft.cavities)
    contents_unchanged = coverage_ok and all(
        candidate_cavities[cavity_id].content_invariant()
        == source_cavities[cavity_id].content_invariant()
        for cavity_id in source_ids
    )
    source_wall = _number(source_container["wall_thickness_mm"])
    source_floor = _number(source_container["floor_thickness_mm"])
    physical_values_ok = (
        _same(draft.wall_thickness_mm, source_wall)
        and _same(draft.floor_thickness_mm, source_floor)
    )
    finite_positive = _finite_positive_geometry(draft)
    origins_ok = _origins_match_local_frame(draft)
    contained = origins_ok and _cavities_are_contained(draft)
    separated = contained and _cavities_are_separated(draft)
    tight_envelope = contained and _envelope_is_tight(draft)
    fixed_axes_ok = _fixed_axes_accept(draft, group)
    digest_ok = draft.geometry_digest == compute_variant_geometry_digest(draft)
    checks = (
        _check("container_group", draft.container_group_id == str(source_container["container_group_id"]), "LOCAL_CONTAINER_GROUP_MISMATCH"),
        _check("coverage", coverage_ok, "LOCAL_CONTENT_COVERAGE_MISMATCH"),
        _check("content_invariants", contents_unchanged, "LOCAL_CONTENT_GEOMETRY_CHANGED"),
        _check("physical_values", physical_values_ok, "LOCAL_PHYSICAL_VALUE_CHANGED"),
        _check("finite_positive_geometry", finite_positive, "LOCAL_INVALID_GEOMETRY"),
        _check("local_frame", origins_ok, "LOCAL_FRAME_INVALID"),
        _check("contained_cavities", contained, "LOCAL_CAVITY_OUT_OF_BOUNDS"),
        _check("separated_cavities", separated, "LOCAL_CAVITY_OVERLAP_OR_WALL_MISSING"),
        _check("tight_minimum_envelope", tight_envelope, "LOCAL_MINIMUM_ENVELOPE_MISMATCH"),
        _check("automatic_body_count", draft.automatic_body_count == 0, "LOCAL_AUTOMATIC_BODY_FORBIDDEN"),
        _check("fixed_axes", fixed_axes_ok, "LOCAL_FIXED_AXIS_EXCEEDED"),
        _check("geometry_digest", digest_ok, "LOCAL_GEOMETRY_DIGEST_MISMATCH"),
    )
    certificate = LocalVariantCertificate(
        schema_version=LOCAL_CERTIFICATE_SCHEMA_V1,
        geometry_digest=draft.geometry_digest,
        certified=all(check.passed for check in checks),
        checks=checks,
    )
    return ContainerInternalVariant(
        draft=draft,
        provenance=tuple(sorted(set(draft.provenance))),
        local_cost=_local_cost(draft),
        local_certificate=certificate,
    )


def compute_variant_geometry_digest(draft: ContainerInternalVariantDraft) -> str:
    payload = {
        "contract_version": LOCAL_GEOMETRY_CONTRACT_V1,
        "container_group_id": draft.container_group_id,
        "minimum_outer_envelope_mm": draft.minimum_outer_envelope_mm,
        "wall_thickness_mm": _round(draft.wall_thickness_mm),
        "floor_thickness_mm": _round(draft.floor_thickness_mm),
        "cavity_layout_frame": draft.cavity_layout_frame,
        "automatic_body_count": draft.automatic_body_count,
        "cavities": [
            cavity.geometry_payload()
            for cavity in sorted(draft.cavities, key=lambda value: value.cavity_id)
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def container_internal_variant_to_dict(variant: ContainerInternalVariant) -> dict[str, object]:
    draft = variant.draft
    primary = draft.provenance[0]
    return {
        "container_group_id": draft.container_group_id,
        "variant_id": draft.variant_id,
        "geometry_digest": draft.geometry_digest,
        "canonical": draft.canonical,
        "producer_id": primary.producer_id,
        "producer_version": primary.producer_version,
        "provenance": [
            {
                "producer_id": value.producer_id,
                "producer_version": value.producer_version,
                "generation_path": value.generation_path,
            }
            for value in variant.provenance
        ],
        "minimum_outer_envelope_mm": _dimension_dict(draft.minimum_outer_envelope_mm),
        "wall_thickness_mm": draft.wall_thickness_mm,
        "floor_thickness_mm": draft.floor_thickness_mm,
        "cavity_layout_frame": draft.cavity_layout_frame,
        "cavity_layout": [
            {
                **cavity.geometry_payload(),
                "local_origin_mm": _dimension_dict(cavity.local_origin_mm),
                "inner_dimensions_mm": _dimension_dict(cavity.inner_dimensions_mm),
                "base_dimensions_mm": _dimension_dict(cavity.base_dimensions_mm),
                "resolved_dimensions_mm": _dimension_dict(cavity.resolved_dimensions_mm),
                "clearance_values_mm": _dimension_dict(cavity.clearance_values_mm),
            }
            for cavity in draft.cavities
        ],
        "local_cost_breakdown": {
            "canonical_priority": variant.local_cost.canonical_priority,
            "envelope_x_mm": variant.local_cost.envelope_x_mm,
            "envelope_y_mm": variant.local_cost.envelope_y_mm,
            "envelope_z_mm": variant.local_cost.envelope_z_mm,
            "volume_mm3": variant.local_cost.volume_mm3,
            "area_mm2": variant.local_cost.area_mm2,
            "aspect_penalty": variant.local_cost.aspect_penalty,
            "layout_complexity": variant.local_cost.layout_complexity,
        },
        "local_certificate": {
            "schema_version": variant.local_certificate.schema_version,
            "certified": variant.local_certificate.certified,
            "rejection_codes": list(variant.local_certificate.rejection_codes),
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "rejection_code": check.rejection_code,
                }
                for check in variant.local_certificate.checks
            ],
        },
    }


def internal_variant_run_to_dict(run: InternalVariantRun) -> dict[str, object]:
    return {
        "schema_version": run.schema_version,
        "budget": run.budget.to_dict(),
        "skipped_container_group_ids": list(run.skipped_container_group_ids),
        "frontiers": [
            {
                "container_group_id": frontier.container_group_id,
                "generated_count": frontier.generated_count,
                "raw_layout_count": frontier.raw_layout_count,
                "certified_count": frontier.certified_count,
                "duplicate_count": frontier.duplicate_count,
                "dominated_count": frontier.dominated_count,
                "generation_limit_reached": frontier.generation_limit_reached,
                "certification_limit_reached": frontier.certification_limit_reached,
                "retention_limit_reached": frontier.retention_limit_reached,
                "variants": [container_internal_variant_to_dict(value) for value in frontier.variants],
                "rejected": [
                    {
                        "variant_id": value.variant.variant_id,
                        "geometry_digest": value.variant.geometry_digest,
                        "rejection_codes": list(value.rejection_codes),
                    }
                    for value in frontier.rejected
                ],
            }
            for frontier in run.frontiers
        ],
    }


def _canonical_draft(container: Mapping[str, object]) -> ContainerInternalVariantDraft:
    group_id = str(container["container_group_id"])
    cavities = tuple(_cavity_snapshot(value) for value in _mappings(container["compartments"]))
    draft = ContainerInternalVariantDraft(
        container_group_id=group_id,
        variant_id=f"{group_id}:canonical_v1",
        geometry_digest="",
        canonical=True,
        provenance=(VariantProvenance(CANONICAL_PRODUCER_ID, PRODUCER_VERSION_V1, "current_container_derivation"),),
        minimum_outer_envelope_mm=_dimension_tuple(container["outer_dimensions_mm"]),
        cavities=cavities,
        wall_thickness_mm=_number(container["wall_thickness_mm"]),
        floor_thickness_mm=_number(container["floor_thickness_mm"]),
        cavity_layout_frame="minimum_outer_envelope.local",
        row_count=int(_mapping(container["compartment_layout"])["rows"]),
        internal_separator_count=max(0, len(cavities) - 1),
        automatic_body_count=0,
        generation_index=0,
    )
    return replace(draft, geometry_digest=compute_variant_geometry_digest(draft))


def _rectangular_relayout_drafts(
    container: Mapping[str, object],
    budget: ContainerVariantBudget,
) -> tuple[tuple[ContainerInternalVariantDraft, ...], int]:
    compartments = _mappings(container["compartments"])
    wall = _number(container["wall_thickness_mm"])
    floor = _number(container["floor_thickness_mm"])
    candidates: dict[tuple[tuple[str, ...], ...], dict[str, object]] = {}
    paths: dict[tuple[tuple[str, ...], ...], set[str]] = {}
    span = _total_candidate_span(compartments, wall)
    local_box = {"x": span, "y": span, "z": span}

    def register(rows: list[list[dict[str, object]]], order: str, path: str) -> None:
        signature = tuple(tuple(str(value["id"]) for value in row) for row in rows)
        paths.setdefault(signature, set()).add(path)
        _register_arrangement_candidate(candidates, rows, wall, local_box, order)

    for order, ordered in _compartment_orderings(compartments):
        for columns in range(1, len(ordered) + 1):
            rows = [ordered[index : index + columns] for index in range(0, len(ordered), columns)]
            register(rows, order, f"{order}:columns:{columns}")
        widths = _bounded_target_widths(ordered, wall, span, span)
        for width in widths:
            register(
                _next_fit_rows(ordered, width, wall),
                order,
                f"{order}:next_fit:{_round(width)}",
            )
            register(
                _best_fit_rows(ordered, width, wall),
                order,
                f"{order}:best_fit:{_round(width)}",
            )

    raw_layout_count = len(candidates)
    maximum_relayouts = max(0, budget.max_generated_variants_per_container - 1)
    selected = list(candidates.items())[:maximum_relayouts]
    result: list[ContainerInternalVariantDraft] = []
    for generation_index, (signature, candidate) in enumerate(selected, start=1):
        cavities = _candidate_cavities(candidate, wall, floor)
        outer = (
            _round(_number(_mapping(candidate["size_mm"])["x"]) + wall * 2.0),
            _round(_number(_mapping(candidate["size_mm"])["y"]) + wall * 2.0),
            _dimension_tuple(container["outer_dimensions_mm"])[2],
        )
        provenance = tuple(
            VariantProvenance(RECTANGULAR_RELAYOUT_PRODUCER_ID, PRODUCER_VERSION_V1, path)
            for path in sorted(paths[signature])
        )
        draft = ContainerInternalVariantDraft(
            container_group_id=str(container["container_group_id"]),
            variant_id="pending_digest",
            geometry_digest="",
            canonical=False,
            provenance=provenance,
            minimum_outer_envelope_mm=outer,
            cavities=cavities,
            wall_thickness_mm=wall,
            floor_thickness_mm=floor,
            cavity_layout_frame="minimum_outer_envelope.local",
            row_count=int(candidate["rows"]),
            internal_separator_count=max(0, len(cavities) - 1),
            automatic_body_count=0,
            generation_index=generation_index,
        )
        digest = compute_variant_geometry_digest(draft)
        result.append(
            replace(
                draft,
                variant_id=f"{draft.container_group_id}:relayout:{digest[:16]}",
                geometry_digest=digest,
            )
        )
    return tuple(result), raw_layout_count


def _candidate_cavities(
    candidate: Mapping[str, object], wall: float, floor: float
) -> tuple[CavitySnapshot, ...]:
    snapshots: list[CavitySnapshot] = []
    y = 0.0
    rows = _values(candidate["row_values"])
    row_heights = _values(candidate["row_heights"])
    for raw_row, raw_height in zip(rows, row_heights):
        x = 0.0
        for compartment in _mappings(raw_row):
            snapshots.append(
                _cavity_snapshot(
                    compartment,
                    origin=(wall + x, wall + y, floor),
                )
            )
            x += _number(_mapping(compartment["inner_dimensions_mm"])["x"]) + wall
        y += _number(raw_height) + wall
    return tuple(sorted(snapshots, key=lambda value: value.cavity_id))


def _cavity_snapshot(
    compartment: Mapping[str, object],
    *,
    origin: tuple[float, float, float] | None = None,
) -> CavitySnapshot:
    local_origin = _dimension_tuple(compartment["local_origin_mm"]) if origin is None else tuple(_round(value) for value in origin)
    clearance = _mapping(compartment["clearance_effective_v1"])
    values = _mapping(clearance["values_mm"])
    sources = _mapping(clearance["source_by_axis"])
    footprint = _mapping(compartment["footprint_profile"])
    return CavitySnapshot(
        cavity_id=str(compartment["id"]),
        content_id=str(compartment["content_id"]),
        shape_kind=str(compartment["shape_kind"]),
        footprint_policy=str(footprint["policy"]),
        local_origin_mm=local_origin,
        inner_dimensions_mm=_dimension_tuple(compartment["inner_dimensions_mm"]),
        base_dimensions_mm=_dimension_tuple(compartment["base_dimensions_mm"]),
        resolved_dimensions_mm=_dimension_tuple(compartment["resolved_dimensions_mm"]),
        clearance_values_mm=tuple(_round(_number(values[axis])) for axis in _AXES),
        clearance_sources=tuple(str(sources[axis]) for axis in _AXES),
        quantity_payload=json.dumps(
            _mapping(compartment["quantity"]),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ),
        storage_orientation=str(compartment["storage_orientation"]),
        resolved_orientation=str(compartment["resolved_orientation"]),
    )


def _deduplicate_variants(
    variants: Sequence[ContainerInternalVariant],
) -> tuple[list[ContainerInternalVariant], int]:
    unique: dict[str, ContainerInternalVariant] = {}
    duplicates = 0
    for variant in variants:
        existing = unique.get(variant.geometry_digest)
        if existing is None:
            unique[variant.geometry_digest] = variant
            continue
        duplicates += 1
        provenance = tuple(sorted(set((*existing.provenance, *variant.provenance))))
        unique[variant.geometry_digest] = replace(existing, provenance=provenance)
    return list(unique.values()), duplicates


def _pareto_frontier(
    variants: Sequence[ContainerInternalVariant],
) -> list[ContainerInternalVariant]:
    result: list[ContainerInternalVariant] = []
    for variant in variants:
        if variant.canonical:
            result.append(variant)
            continue
        if any(
            other.geometry_digest != variant.geometry_digest
            and _dominates(other.local_cost, variant.local_cost)
            for other in variants
        ):
            continue
        result.append(variant)
    return result


def _retain_variants(
    variants: Sequence[ContainerInternalVariant], maximum: int
) -> list[ContainerInternalVariant]:
    ordered = sorted(variants, key=_variant_sort_key)
    canonical = [variant for variant in ordered if variant.canonical]
    others = [variant for variant in ordered if not variant.canonical]
    return (canonical[:1] + others)[:maximum]


def _variant_sort_key(variant: ContainerInternalVariant) -> tuple[object, ...]:
    cost = variant.local_cost
    primary = variant.provenance[0]
    return (
        cost.canonical_priority,
        max(cost.envelope_x_mm, cost.envelope_y_mm),
        cost.envelope_x_mm,
        cost.envelope_y_mm,
        cost.envelope_z_mm,
        cost.volume_mm3,
        cost.area_mm2,
        cost.aspect_penalty,
        cost.layout_complexity,
        primary.producer_id,
        variant.geometry_digest,
    )


def _dominates(left: LocalVariantCost, right: LocalVariantCost) -> bool:
    left_axes = left.dominance_axes()
    right_axes = right.dominance_axes()
    return all(a <= b + _EPSILON for a, b in zip(left_axes, right_axes)) and any(
        a < b - _EPSILON for a, b in zip(left_axes, right_axes)
    )


def _local_cost(draft: ContainerInternalVariantDraft) -> LocalVariantCost:
    x, y, z = draft.minimum_outer_envelope_mm
    aspect = abs(log(max(x, y) / min(x, y))) if min(x, y) > 0.0 else 0.0
    return LocalVariantCost(
        canonical_priority=0 if draft.canonical else 1,
        envelope_x_mm=_round(x),
        envelope_y_mm=_round(y),
        envelope_z_mm=_round(z),
        volume_mm3=_round(x * y * z),
        area_mm2=_round(x * y),
        aspect_penalty=_round(aspect),
        layout_complexity=draft.row_count + draft.internal_separator_count,
    )


def _finite_positive_geometry(draft: ContainerInternalVariantDraft) -> bool:
    numbers = [
        *draft.minimum_outer_envelope_mm,
        draft.wall_thickness_mm,
        draft.floor_thickness_mm,
    ]
    for cavity in draft.cavities:
        numbers.extend(cavity.local_origin_mm)
        numbers.extend(cavity.inner_dimensions_mm)
    return all(isfinite(value) for value in numbers) and all(
        value > 0.0
        for value in (
            *draft.minimum_outer_envelope_mm,
            draft.wall_thickness_mm,
            draft.floor_thickness_mm,
            *(axis for cavity in draft.cavities for axis in cavity.inner_dimensions_mm),
        )
    )


def _origins_match_local_frame(draft: ContainerInternalVariantDraft) -> bool:
    if draft.cavity_layout_frame != "minimum_outer_envelope.local":
        return False
    return all(
        cavity.local_origin_mm[0] + _EPSILON >= draft.wall_thickness_mm
        and cavity.local_origin_mm[1] + _EPSILON >= draft.wall_thickness_mm
        and _same(cavity.local_origin_mm[2], draft.floor_thickness_mm)
        for cavity in draft.cavities
    )


def _cavities_are_contained(draft: ContainerInternalVariantDraft) -> bool:
    outer = draft.minimum_outer_envelope_mm
    wall = draft.wall_thickness_mm
    return all(
        cavity.local_origin_mm[0] + cavity.inner_dimensions_mm[0] + wall <= outer[0] + _EPSILON
        and cavity.local_origin_mm[1] + cavity.inner_dimensions_mm[1] + wall <= outer[1] + _EPSILON
        and cavity.local_origin_mm[2] + cavity.inner_dimensions_mm[2] <= outer[2] + _EPSILON
        for cavity in draft.cavities
    )


def _cavities_are_separated(draft: ContainerInternalVariantDraft) -> bool:
    cavities = draft.cavities
    for index, left in enumerate(cavities):
        for right in cavities[index + 1 :]:
            gap_x = max(
                right.local_origin_mm[0] - (left.local_origin_mm[0] + left.inner_dimensions_mm[0]),
                left.local_origin_mm[0] - (right.local_origin_mm[0] + right.inner_dimensions_mm[0]),
            )
            gap_y = max(
                right.local_origin_mm[1] - (left.local_origin_mm[1] + left.inner_dimensions_mm[1]),
                left.local_origin_mm[1] - (right.local_origin_mm[1] + right.inner_dimensions_mm[1]),
            )
            if gap_x < -_EPSILON and gap_y < -_EPSILON:
                return False
            if max(gap_x, gap_y) + _EPSILON < draft.wall_thickness_mm:
                return False
    return True


def _envelope_is_tight(draft: ContainerInternalVariantDraft) -> bool:
    if not draft.cavities:
        return False
    expected = (
        _round(max(value.local_origin_mm[0] + value.inner_dimensions_mm[0] for value in draft.cavities) + draft.wall_thickness_mm),
        _round(max(value.local_origin_mm[1] + value.inner_dimensions_mm[1] for value in draft.cavities) + draft.wall_thickness_mm),
        _round(max(value.local_origin_mm[2] + value.inner_dimensions_mm[2] for value in draft.cavities)),
    )
    return all(_same(value, expected[index]) for index, value in enumerate(draft.minimum_outer_envelope_mm))


def _fixed_axes_accept(
    draft: ContainerInternalVariantDraft, group: Mapping[str, object]
) -> bool:
    modes = _mapping(group["dimension_modes"])
    locked = _mapping(group["locked_outer_dimensions_mm"])
    targets = _mapping(group["target_outer_dimensions_mm"])
    for index, axis in enumerate(_AXES):
        if str(modes[axis]) != "fixed":
            continue
        limit = locked[axis] if locked[axis] is not None else targets[axis]
        if limit is None or draft.minimum_outer_envelope_mm[index] > _number(limit) + _EPSILON:
            return False
    return True


def _total_candidate_span(compartments: Sequence[Mapping[str, object]], wall: float) -> float:
    width = sum(_number(_mapping(value["inner_dimensions_mm"])["x"]) for value in compartments)
    height = sum(_number(_mapping(value["inner_dimensions_mm"])["y"]) for value in compartments)
    separators = wall * max(0, len(compartments) - 1)
    return _round(max(width, height) + separators + wall * 2.0)


def _check(name: str, passed: bool, code: str) -> LocalVariantCheck:
    return LocalVariantCheck(name, passed, None if passed else code)


def _dimension_tuple(value: object) -> tuple[float, float, float]:
    raw = _mapping(value)
    return tuple(_round(_number(raw[axis])) for axis in _AXES)


def _dimension_dict(value: tuple[float, float, float]) -> dict[str, float]:
    return {axis: value[index] for index, axis in enumerate(_AXES)}


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Internal container variant values must be mappings.")
    return value


def _mappings(value: object) -> list[Mapping[str, object]]:
    return [_mapping(item) for item in _values(value)]


def _values(value: object) -> list[object]:
    if not isinstance(value, list):
        raise TypeError("Internal container variant collections must be lists.")
    return value


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("Internal container variant dimensions must be numbers.")
    return float(value)


def _same(left: float, right: float) -> bool:
    return abs(float(left) - float(right)) <= _EPSILON


def _round(value: float) -> float:
    return round(float(value), 4)
