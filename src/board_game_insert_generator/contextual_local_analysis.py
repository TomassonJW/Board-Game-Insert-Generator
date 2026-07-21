"""Incremental contextual local analysis for P64-L02.

The module enriches certified container frontiers with explicit metrics and
fail-closed box/reservation annotations. It never invokes a global solver,
performs a placement, finalizes a plan or materializes Fusion geometry.
"""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from typing import Mapping, Sequence

from board_game_insert_generator.container_internal_variants import (
    CANONICAL_PRODUCER_ID,
    RECTANGULAR_RELAYOUT_PRODUCER_ID,
    ContainerInternalVariant,
    ContainerVariantFrontier,
    container_internal_variant_to_dict,
    derive_container_internal_variant_frontiers,
    internal_variant_run_to_dict,
)
from board_game_insert_generator.incremental_project_state import (
    STAGE_CONTAINER_FRONTIER,
    STAGE_CONTEXT_ANNOTATION,
    BoundedArtifactCache,
    ContextAnnotationKey,
    IncrementalProjectState,
    canonical_digest,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.top_inset_reservation import derive_top_inset_reservations


LOCAL_ANALYSIS_SCHEMA_V1 = "bgig.contextual_local_analysis.v1"
LOCAL_SCORE_SCHEMA_V1 = "bgig.local_variant_scores.v1"
CONTEXT_ANNOTATION_SCHEMA_V1 = "bgig.local_context_annotation.v1"
GLOBAL_BOUNDS_SCHEMA_V1 = "bgig.reactive_global_bounds.v1"
ANNOTATOR_ID = "box_and_top_reservation_context"
ANNOTATOR_VERSION = "1"
PRODUCER_SET_VERSION = "p64_l02_v1"

COMPATIBLE = "compatible"
CONDITIONAL = "conditional"
INCOMPATIBLE = "incompatible"
UNKNOWN = "unknown"
_COMPATIBILITY_ORDER = {
    COMPATIBLE: 0,
    CONDITIONAL: 1,
    UNKNOWN: 2,
    INCOMPATIBLE: 3,
}
_EPSILON = 0.0001


class IncrementalLocalAnalysisEngine:
    """Consume P64-L01 state/cache primitives for bounded local analysis."""

    def __init__(
        self,
        raw_project: object,
        *,
        effort_profile: str = "normal",
        cache_entries: int = 256,
    ) -> None:
        self.effort_profile = effort_profile
        self.state = IncrementalProjectState(raw_project)
        self.cache = BoundedArtifactCache(cache_entries)
        self._project = normalize_project_draft(raw_project).project
        self._frontiers: dict[str, ContainerVariantFrontier] = {}
        self._analyses: dict[str, dict[str, object]] = {}
        self._frontier_digests: dict[str, str] = {}
        self._context_digests: dict[str, str] = {}
        self._last_recomputed_frontiers: tuple[str, ...] = ()
        self._last_recomputed_contexts: tuple[str, ...] = ()
        self._last_reused_frontiers: tuple[str, ...] = ()
        self._last_reused_contexts: tuple[str, ...] = ()
        self._analyze(
            frontier_group_ids=self.state.snapshot.container_group_ids,
            context_group_ids=self.state.snapshot.container_group_ids,
        )

    def update_project(self, raw_project: object) -> dict[str, object]:
        """Refresh only invalidated local stages and return an observable snapshot."""

        normalized = normalize_project_draft(raw_project).project
        delta = self.state.update_project(normalized)
        self._project = normalized
        current_ids = set(self.state.snapshot.container_group_ids)
        for group_id in tuple(self._frontiers):
            if group_id not in current_ids:
                self._frontiers.pop(group_id, None)
                self._analyses.pop(group_id, None)
                self._frontier_digests.pop(group_id, None)
                self._context_digests.pop(group_id, None)

        if not delta.changed:
            self._last_recomputed_frontiers = ()
            self._last_recomputed_contexts = ()
            self._last_reused_frontiers = tuple(sorted(current_ids))
            self._last_reused_contexts = tuple(sorted(current_ids))
            return self.snapshot()

        frontier_targets = set(delta.invalidated_container_group_ids)
        frontier_targets.update(current_ids - set(self._frontiers))
        context_targets = set(delta.invalidated_context_group_ids)
        context_targets.update(frontier_targets)
        context_targets.update(current_ids - set(self._analyses))
        self._analyze(
            frontier_group_ids=tuple(sorted(frontier_targets)),
            context_group_ids=tuple(sorted(context_targets)),
        )
        return self.snapshot()

    def snapshot(self) -> dict[str, object]:
        """Return the current local result without persisting cache artifacts."""

        events = [
            {
                "scope": event.scope,
                "owner_id": event.owner_id,
                "reason": event.reason,
            }
            for event in self.state.last_invalidation.events
        ]
        return {
            "schema_version": LOCAL_ANALYSIS_SCHEMA_V1,
            "source_revision": self.state.source_revision,
            "effort_profile": self.effort_profile,
            "containers": [
                deepcopy(self._analyses[group_id])
                for group_id in sorted(self._analyses)
            ],
            "reactive_global_bounds": _reactive_global_bounds(
                self._project, self._analyses
            ),
            "incremental": {
                "recomputed_frontier_group_ids": list(
                    self._last_recomputed_frontiers
                ),
                "recomputed_context_group_ids": list(
                    self._last_recomputed_contexts
                ),
                "reused_frontier_group_ids": list(self._last_reused_frontiers),
                "reused_context_group_ids": list(self._last_reused_contexts),
                "invalidation_events": events,
                "cache": self.cache.telemetry(),
            },
            "invariants": {
                "global_solver_invocation_count": 0,
                "global_placement_performed": False,
                "finalization_performed": False,
                "fusion_materialization_performed": False,
                "unknown_promoted_to_compatible": False,
                "ui_shortlist_limits_engine_frontier": False,
                "project_schema_mutated": False,
            },
        }

    def _analyze(
        self,
        *,
        frontier_group_ids: Sequence[str],
        context_group_ids: Sequence[str],
    ) -> None:
        known_ids = set(self.state.snapshot.container_group_ids)
        frontier_targets = tuple(
            value for value in sorted(set(frontier_group_ids)) if value in known_ids
        )
        context_targets = tuple(
            value for value in sorted(set(context_group_ids)) if value in known_ids
        )
        recomputed_frontiers: list[str] = []
        reused_frontiers: list[str] = []
        recomputed_contexts: list[str] = []
        reused_contexts: list[str] = []

        for group_id in frontier_targets:
            frontier, frontier_digest, cache_status = self._frontier(group_id)
            if frontier is None:
                self._frontiers.pop(group_id, None)
                self._frontier_digests.pop(group_id, None)
            else:
                self._frontiers[group_id] = frontier
                self._frontier_digests[group_id] = frontier_digest
            if cache_status == "hit":
                reused_frontiers.append(group_id)
            else:
                recomputed_frontiers.append(group_id)

        top_insets = derive_top_inset_reservations(self._project)
        for group_id in context_targets:
            frontier = self._frontiers.get(group_id)
            if frontier is None:
                self._analyses[group_id] = _empty_container_analysis(
                    group_id,
                    self.effort_profile,
                    reason="no_certified_local_frontier",
                )
                self._context_digests[group_id] = canonical_digest(
                    self._analyses[group_id]
                )
                recomputed_contexts.append(group_id)
                continue
            analysis, digest, cache_status = self._context(
                group_id,
                frontier,
                self._frontier_digests[group_id],
                top_insets,
            )
            self._analyses[group_id] = analysis
            self._context_digests[group_id] = digest
            if cache_status == "hit":
                reused_contexts.append(group_id)
            else:
                recomputed_contexts.append(group_id)

        untouched = known_ids - set(frontier_targets)
        reused_frontiers.extend(
            group_id for group_id in sorted(untouched) if group_id in self._frontiers
        )
        untouched_contexts = known_ids - set(context_targets)
        reused_contexts.extend(
            group_id
            for group_id in sorted(untouched_contexts)
            if group_id in self._analyses
        )
        self._last_recomputed_frontiers = tuple(sorted(set(recomputed_frontiers)))
        self._last_recomputed_contexts = tuple(sorted(set(recomputed_contexts)))
        self._last_reused_frontiers = tuple(sorted(set(reused_frontiers)))
        self._last_reused_contexts = tuple(sorted(set(reused_contexts)))

    def _frontier(
        self, group_id: str
    ) -> tuple[ContainerVariantFrontier | None, str, str]:
        member_digests: dict[str, str] = {}
        for asset_id in self.state.snapshot.members_for(group_id):
            key = self.state.snapshot.asset_resolution_key(
                asset_id,
                resolver_id="project_v1_normalized_asset",
                resolver_version="1",
            )
            member_digests[asset_id] = canonical_digest(
                {
                    "schema_version": "bgig.local_asset_resolution_identity.v1",
                    "complete_key_digest": key.digest,
                }
            )
        producer_set_digest = canonical_digest(
            {
                "producer_set_version": PRODUCER_SET_VERSION,
                "producer_ids": [
                    CANONICAL_PRODUCER_ID,
                    RECTANGULAR_RELAYOUT_PRODUCER_ID,
                ],
            }
        )
        key = self.state.snapshot.container_frontier_key(
            group_id,
            asset_resolution_digests=member_digests,
            producer_set_digest=producer_set_digest,
            effort_profile=self.effort_profile,
        )
        token = self.state.begin_local_request(STAGE_CONTAINER_FRONTIER, group_id)
        lookup = self.cache.lookup(key)
        if lookup.status == "hit":
            frontier = lookup.value
            if not isinstance(frontier, ContainerVariantFrontier):
                raise TypeError("Cached local frontier has an unexpected type.")
            accepted = self.state.accept_local_result(
                token, lookup.artifact_digest or ""
            )
            if not accepted.accepted:
                raise RuntimeError(
                    f"Cached local frontier rejected: {accepted.reason}."
                )
            return frontier, lookup.artifact_digest or "", "hit"

        run = derive_container_internal_variant_frontiers(
            self._project,
            effort_profile=self.effort_profile,
            container_group_ids=(group_id,),
        )
        frontier = run.frontiers[0] if run.frontiers else None
        frontier_digest = canonical_digest(internal_variant_run_to_dict(run))
        if frontier is not None:
            self.cache.put(key, frontier_digest, frontier)
        accepted = self.state.accept_local_result(token, frontier_digest)
        if not accepted.accepted:
            raise RuntimeError(
                f"Fresh local frontier rejected: {accepted.reason}."
            )
        return frontier, frontier_digest, "miss"

    def _context(
        self,
        group_id: str,
        frontier: ContainerVariantFrontier,
        frontier_digest: str,
        top_insets: Mapping[str, object],
    ) -> tuple[dict[str, object], str, str]:
        key = ContextAnnotationKey(
            container_group_id=group_id,
            container_frontier_digest=frontier_digest,
            box_context_digest=self.state.snapshot.box_context_digest,
            top_reservation_digest=self.state.snapshot.top_reservation_digest,
            annotator_id=ANNOTATOR_ID,
            annotator_version=ANNOTATOR_VERSION,
        )
        token = self.state.begin_local_request(STAGE_CONTEXT_ANNOTATION, group_id)
        lookup = self.cache.lookup(key)
        if lookup.status == "hit":
            if not isinstance(lookup.value, dict):
                raise TypeError("Cached context analysis has an unexpected type.")
            accepted = self.state.accept_local_result(
                token, lookup.artifact_digest or ""
            )
            if not accepted.accepted:
                raise RuntimeError(
                    f"Cached context analysis rejected: {accepted.reason}."
                )
            return deepcopy(lookup.value), lookup.artifact_digest or "", "hit"

        analysis = _analyze_frontier(
            self._project,
            frontier,
            top_insets,
            frontier_digest=frontier_digest,
        )
        digest = canonical_digest(analysis)
        self.cache.put(key, digest, analysis)
        accepted = self.state.accept_local_result(token, digest)
        if not accepted.accepted:
            raise RuntimeError(
                f"Fresh context analysis rejected: {accepted.reason}."
            )
        return analysis, digest, "miss"


def build_contextual_local_analysis(
    raw_project: object,
    *,
    effort_profile: str = "normal",
) -> dict[str, object]:
    """Build one reconstructible complete local-analysis snapshot."""

    return IncrementalLocalAnalysisEngine(
        raw_project,
        effort_profile=effort_profile,
    ).snapshot()


def _analyze_frontier(
    project: Mapping[str, object],
    frontier: ContainerVariantFrontier,
    top_insets: Mapping[str, object],
    *,
    frontier_digest: str,
) -> dict[str, object]:
    variants = [
        _analyze_variant(project, variant, top_insets)
        for variant in frontier.variants
    ]
    pareto = _contextual_pareto(variants)
    representatives = _representatives(pareto)
    return {
        "container_group_id": frontier.container_group_id,
        "frontier_digest": frontier_digest,
        "effort_profile": frontier.budget.effort_profile,
        "budget": frontier.budget.to_dict(),
        "engine_frontier_count": len(variants),
        "engine_frontier_variant_digests": [
            value["geometry_digest"] for value in variants
        ],
        "pareto_variant_digests": [
            value["geometry_digest"] for value in pareto
        ],
        "visible_representatives": representatives,
        "variants": variants,
        "generation": {
            "generated_count": frontier.generated_count,
            "raw_layout_count": frontier.raw_layout_count,
            "certified_count": frontier.certified_count,
            "duplicate_count": frontier.duplicate_count,
            "dominated_count": frontier.dominated_count,
            "generation_limit_reached": frontier.generation_limit_reached,
            "certification_limit_reached": frontier.certification_limit_reached,
            "retention_limit_reached": frontier.retention_limit_reached,
        },
        "summary": {
            "status": "possibilities_current",
            "variant_count": len(variants),
            "pareto_count": len(pareto),
            "representative_count": len(representatives),
            "representative_labels": [
                label
                for value in representatives
                for label in value["labels"]
            ],
        },
        "invariants": {
            "local_certificate_required": True,
            "shortlist_is_non_normative": True,
            "shortlist_maximum": 3,
            "engine_frontier_not_truncated_to_shortlist": True,
            "geometry_digest_unchanged_by_context": True,
            "opaque_total_score_present": False,
        },
    }


def _analyze_variant(
    project: Mapping[str, object],
    variant: ContainerInternalVariant,
    top_insets: Mapping[str, object],
) -> dict[str, object]:
    base = container_internal_variant_to_dict(variant)
    scores = _variant_scores(variant)
    box = _box_compatibility(project, variant)
    reservations = [
        _reservation_compatibility(variant, reservation, top_insets)
        for reservation in _mappings(top_insets.get("reservations", []))
    ]
    if reservations:
        top_status = max(
            (str(value["status"]) for value in reservations),
            key=lambda value: _COMPATIBILITY_ORDER[value],
        )
        top_reason = "worst_explicit_reservation_annotation"
    elif _mappings(top_insets.get("blockers", [])):
        top_status = UNKNOWN
        top_reason = "reservation_contract_blocked"
    else:
        top_status = COMPATIBLE
        top_reason = "no_top_reservation"
    context = {
        "schema_version": CONTEXT_ANNOTATION_SCHEMA_V1,
        "box": box,
        "top_context": {
            "status": top_status,
            "reason": top_reason,
        },
        "reservations": reservations,
        "overall_status": max(
            (str(box["status"]), top_status),
            key=lambda value: _COMPATIBILITY_ORDER[value],
        ),
        "unknown_is_compatible": False,
    }
    return {
        **base,
        "scores": scores,
        "context_compatibility": context,
    }


def _variant_scores(variant: ContainerInternalVariant) -> dict[str, object]:
    x, y, z = variant.draft.minimum_outer_envelope_mm
    cavity_volume = sum(
        cavity.inner_dimensions_mm[0]
        * cavity.inner_dimensions_mm[1]
        * cavity.inner_dimensions_mm[2]
        for cavity in variant.draft.cavities
    )
    volume = x * y * z
    return {
        "schema_version": LOCAL_SCORE_SCHEMA_V1,
        "envelope_efficiency": {
            "value": _round(cavity_volume / volume) if volume > 0.0 else None,
            "numerator_cavity_volume_mm3": _round(cavity_volume),
            "denominator_outer_volume_mm3": _round(volume),
        },
        "volume_mm3": _round(volume),
        "footprint_area_mm2": _round(x * y),
        "aspect_penalty": _round(variant.local_cost.aspect_penalty),
        "height_mm": _round(z),
        "layout_complexity": {
            "value": variant.local_cost.layout_complexity,
            "row_count": variant.draft.row_count,
            "internal_separator_count": variant.draft.internal_separator_count,
            "cut_change_count": 0,
        },
        "compatibility_is_separate": True,
        "opaque_total": None,
    }


def _box_compatibility(
    project: Mapping[str, object],
    variant: ContainerInternalVariant,
) -> dict[str, object]:
    box_payload = _mapping(project["box"])
    inner = _dimension(box_payload["inner_dimensions_mm"])
    usable_z = min(inner["z"], float(box_payload["usable_height_mm"]))
    x, y, z = variant.draft.minimum_outer_envelope_mm
    orientations = [
        {
            "rotation_deg_z": 0,
            "fits_x": x <= inner["x"] + _EPSILON,
            "fits_y": y <= inner["y"] + _EPSILON,
            "fits_z": z <= usable_z + _EPSILON,
        },
        {
            "rotation_deg_z": 90,
            "fits_x": y <= inner["x"] + _EPSILON,
            "fits_y": x <= inner["y"] + _EPSILON,
            "fits_z": z <= usable_z + _EPSILON,
        },
    ]
    for value in orientations:
        value["fits_all_axes"] = bool(
            value["fits_x"] and value["fits_y"] and value["fits_z"]
        )
    compatible_orientations = [
        int(value["rotation_deg_z"])
        for value in orientations
        if value["fits_all_axes"]
    ]
    return {
        "status": COMPATIBLE if compatible_orientations else INCOMPATIBLE,
        "reason": (
            "at_least_one_xy_orientation_fits_all_box_axes"
            if compatible_orientations
            else "no_xy_orientation_fits_all_box_axes"
        ),
        "box_inner_dimensions_mm": {
            "x": inner["x"],
            "y": inner["y"],
            "z": usable_z,
        },
        "orientations": orientations,
        "compatible_rotation_deg_z": compatible_orientations,
        "does_not_certify_global_placement": True,
    }


def _reservation_compatibility(
    variant: ContainerInternalVariant,
    reservation: Mapping[str, object],
    top_insets: Mapping[str, object],
) -> dict[str, object]:
    reservation_id = str(reservation.get("id", "unknown"))
    support_plane = reservation.get("support_plane_z_mm")
    design_top = top_insets.get("design_top_z_mm")
    if (
        not isinstance(support_plane, (int, float))
        or isinstance(support_plane, bool)
    ):
        return {
            "reservation_id": reservation_id,
            "status": UNKNOWN,
            "reason": "support_plane_missing",
        }
    if not isinstance(design_top, (int, float)) or isinstance(design_top, bool):
        return {
            "reservation_id": reservation_id,
            "status": UNKNOWN,
            "reason": "design_top_missing",
        }
    height = variant.draft.minimum_outer_envelope_mm[2]
    if height <= float(support_plane) + _EPSILON:
        status = COMPATIBLE
        reason = "variant_remains_below_support_plane"
    elif height > float(design_top) + _EPSILON:
        status = INCOMPATIBLE
        reason = "variant_exceeds_design_top"
    else:
        status = CONDITIONAL
        reason = "localized_position_rotation_or_cut_requires_global_validation"
    return {
        "reservation_id": reservation_id,
        "flat_item_id": reservation.get("flat_item_id"),
        "status": status,
        "reason": reason,
        "variant_height_mm": _round(height),
        "support_plane_z_mm": _round(float(support_plane)),
        "cut_origin_mm": deepcopy(reservation.get("cut_origin_mm")),
        "cut_size_mm": deepcopy(reservation.get("cut_size_mm")),
        "does_not_certify_final_position": True,
    }


def _contextual_pareto(
    variants: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for candidate in variants:
        if any(
            other["geometry_digest"] != candidate["geometry_digest"]
            and _dominates(_pareto_axes(other), _pareto_axes(candidate))
            for other in variants
        ):
            continue
        result.append(candidate)
    return sorted(result, key=_stable_variant_key)


def _pareto_axes(variant: Mapping[str, object]) -> tuple[float, ...]:
    scores = _mapping(variant["scores"])
    efficiency = _mapping(scores["envelope_efficiency"]).get("value")
    complexity = _mapping(scores["layout_complexity"])["value"]
    context = _mapping(variant["context_compatibility"])
    return (
        1.0 - float(efficiency)
        if isinstance(efficiency, (int, float))
        else 1.0,
        float(scores["volume_mm3"]),
        float(scores["footprint_area_mm2"]),
        float(scores["aspect_penalty"]),
        float(scores["height_mm"]),
        float(complexity),
        float(_COMPATIBILITY_ORDER[str(context["overall_status"])]),
    )


def _dominates(left: Sequence[float], right: Sequence[float]) -> bool:
    return all(a <= b + _EPSILON for a, b in zip(left, right)) and any(
        a < b - _EPSILON for a, b in zip(left, right)
    )


def _stable_variant_key(
    variant: Mapping[str, object],
) -> tuple[object, ...]:
    scores = _mapping(variant["scores"])
    context = _mapping(variant["context_compatibility"])
    return (
        float(scores["volume_mm3"]),
        float(scores["footprint_area_mm2"]),
        float(scores["aspect_penalty"]),
        float(scores["height_mm"]),
        _COMPATIBILITY_ORDER[str(context["overall_status"])],
        str(variant["geometry_digest"]),
    )


def _representatives(
    pareto: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    if not pareto:
        return []
    selectors = (
        (
            "Compact",
            lambda value: (
                float(_mapping(value["scores"])["volume_mm3"]),
                float(_mapping(value["scores"])["footprint_area_mm2"]),
                float(_mapping(value["scores"])["height_mm"]),
                str(value["geometry_digest"]),
            ),
        ),
        (
            "\u00c9quilibr\u00e9",
            lambda value: (
                float(_mapping(value["scores"])["aspect_penalty"]),
                float(
                    _mapping(
                        _mapping(value["scores"])["layout_complexity"]
                    )["value"]
                ),
                float(_mapping(value["scores"])["volume_mm3"]),
                str(value["geometry_digest"]),
            ),
        ),
        (
            "Bas",
            lambda value: (
                float(_mapping(value["scores"])["height_mm"]),
                _COMPATIBILITY_ORDER[
                    str(
                        _mapping(value["context_compatibility"])[
                            "overall_status"
                        ]
                    )
                ],
                float(_mapping(value["scores"])["volume_mm3"]),
                str(value["geometry_digest"]),
            ),
        ),
    )
    selected: OrderedDict[str, dict[str, object]] = OrderedDict()
    for label, key in selectors:
        candidate = min(pareto, key=key)
        digest = str(candidate["geometry_digest"])
        entry = selected.setdefault(
            digest,
            {
                "geometry_digest": digest,
                "variant_id": candidate["variant_id"],
                "labels": [],
                "minimum_outer_envelope_mm": deepcopy(
                    candidate["minimum_outer_envelope_mm"]
                ),
                "scores": deepcopy(candidate["scores"]),
                "context_compatibility": deepcopy(
                    candidate["context_compatibility"]
                ),
            },
        )
        entry["labels"].append(label)
    return list(selected.values())


def _reactive_global_bounds(
    project: Mapping[str, object],
    analyses: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    box_payload = _mapping(project["box"])
    inner = _dimension(box_payload["inner_dimensions_mm"])
    usable_z = min(inner["z"], float(box_payload["usable_height_mm"]))
    usable_volume = inner["x"] * inner["y"] * usable_z
    minimum_volumes: list[float] = []
    without_frontier: list[str] = []
    without_box_fit: list[str] = []
    minimum_heights: list[float] = []
    group_ids = sorted(
        str(value["id"]) for value in _mappings(project["container_groups"])
    )
    for group_id in group_ids:
        analysis = analyses.get(group_id)
        variants = (
            _mappings(analysis.get("variants", [])) if analysis else []
        )
        if not variants:
            without_frontier.append(group_id)
            continue
        volumes = [
            float(_mapping(value["scores"])["volume_mm3"])
            for value in variants
        ]
        heights = [
            float(_mapping(value["scores"])["height_mm"])
            for value in variants
        ]
        minimum_volumes.append(min(volumes))
        minimum_heights.append(min(heights))
        if not any(
            _mapping(
                _mapping(value["context_compatibility"])["box"]
            )["status"]
            == COMPATIBLE
            for value in variants
        ):
            without_box_fit.append(group_id)
    minimum_total = sum(minimum_volumes)
    contradictions: list[str] = []
    if minimum_total > usable_volume + _EPSILON:
        contradictions.append(
            "minimum_envelope_volume_exceeds_usable_box_volume"
        )
    contradictions.extend(
        f"container_without_box_axis_fit:{group_id}"
        for group_id in without_box_fit
    )
    status = (
        "necessary_contradiction"
        if contradictions
        else "incomplete"
        if without_frontier
        else "necessary_bounds_satisfied"
    )
    return {
        "schema_version": GLOBAL_BOUNDS_SCHEMA_V1,
        "status": status,
        "usable_box_volume_upper_bound_mm3": _round(usable_volume),
        "minimum_envelope_volume_sum_mm3": (
            None if without_frontier else _round(minimum_total)
        ),
        "signed_volume_balance_mm3": (
            None
            if without_frontier
            else _round(usable_volume - minimum_total)
        ),
        "maximum_minimum_height_mm": (
            None
            if not minimum_heights
            else _round(max(minimum_heights))
        ),
        "container_count": len(group_ids),
        "container_without_certified_frontier_ids": without_frontier,
        "container_without_box_axis_fit_ids": without_box_fit,
        "formal_contradictions": contradictions,
        "placement_performed": False,
        "proves_global_solution": False,
        "proves_impossible_only_when_formal_contradiction_listed": True,
    }


def _empty_container_analysis(
    group_id: str,
    effort_profile: str,
    *,
    reason: str,
) -> dict[str, object]:
    return {
        "container_group_id": group_id,
        "frontier_digest": "",
        "effort_profile": effort_profile,
        "budget": None,
        "engine_frontier_count": 0,
        "engine_frontier_variant_digests": [],
        "pareto_variant_digests": [],
        "visible_representatives": [],
        "variants": [],
        "generation": {},
        "summary": {
            "status": UNKNOWN,
            "reason": reason,
            "variant_count": 0,
            "pareto_count": 0,
            "representative_count": 0,
            "representative_labels": [],
        },
        "invariants": {
            "shortlist_is_non_normative": True,
            "opaque_total_score_present": False,
        },
    }


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Local analysis value must be a mapping.")
    return dict(value)


def _mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError("Local analysis collection must be a sequence.")
    return [_mapping(item) for item in value]


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _round(value: float) -> float:
    return round(float(value), 4)
