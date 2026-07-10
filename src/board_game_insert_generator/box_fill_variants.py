"""Bounded deterministic portfolios built from P20 greedy solves."""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from hashlib import sha256
import json
from board_game_insert_generator.box_fill_solver import BoxFillCandidate, BoxFillSolveRequest, BoxFillSolveResult, solve_box_fill_greedy

BOX_FILL_VARIANTS_SCHEMA_V0 = "box_fill_variants.v0"

@dataclass(frozen=True)
class VariantPreferenceProfile:
    id: str = "balanced"
    weights: dict[str, float] = field(default_factory=lambda: {"compactness": .25, "free_space": .2, "accessibility": .2, "printability": .15, "simplicity": .1, "coverage": .1})

@dataclass(frozen=True)
class BoxFillVariantRequest:
    solve_request: BoxFillSolveRequest
    preference: VariantPreferenceProfile = field(default_factory=VariantPreferenceProfile)
    policies: tuple[str, ...] = ("compact_origin", "preserve_large_free_region", "accessibility_front", "minimal_rotation", "balanced_footprint")
    max_variants: int = 5

@dataclass(frozen=True)
class LayoutVariant:
    id: str
    policy_id: str
    result: BoxFillSolveResult
    scores: dict[str, float]
    layout_digest: str
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class VariantPortfolio:
    schema_version: str
    request: BoxFillVariantRequest
    variants: tuple[LayoutVariant, ...]
    duplicate_policy_ids: dict[str, tuple[str, ...]]
    pareto_variant_ids: tuple[str, ...]
    recommended_variant_id: str | None
    digest: str

def generate_box_fill_variants(request: BoxFillVariantRequest) -> VariantPortfolio:
    unique: dict[str, LayoutVariant] = {}
    duplicates: dict[str, list[str]] = {}
    for policy in request.policies[:8]:
        candidates = _policy_candidates(request.solve_request.candidates, policy)
        result = solve_box_fill_greedy(replace(request.solve_request, candidates=candidates))
        layout = [(item.module_id, item.origin.x, item.origin.y, item.origin.z, item.orientation) for item in result.placements]
        digest = sha256(json.dumps(layout, sort_keys=True).encode()).hexdigest()
        scores = _scores(result)
        if digest in unique:
            duplicates.setdefault(unique[digest].id, []).append(policy)
            continue
        variant = LayoutVariant(f"variant:{policy}:{digest[:12]}", policy, result, scores, digest, (f"Policy {policy} ran bounded P20 greedy placement.",))
        unique[digest] = variant
    variants = tuple(sorted(unique.values(), key=lambda item: (-_weighted(item.scores, request.preference), item.id))[:request.max_variants])
    valid = [item for item in variants if item.result.status == "solved"]
    recommended = valid[0].id if valid else None
    pareto = tuple(item.id for item in valid)
    digest = sha256(json.dumps([(item.id, item.layout_digest, item.scores) for item in variants], sort_keys=True).encode()).hexdigest()
    return VariantPortfolio(BOX_FILL_VARIANTS_SCHEMA_V0, request, variants, {key: tuple(value) for key, value in duplicates.items()}, pareto, recommended, digest)

def _policy_candidates(candidates, policy):
    if policy == "accessibility_front": return tuple(sorted(candidates, key=lambda item: (-item.priority, item.module_id)))
    if policy == "minimal_rotation": return tuple(replace(item, preferred_orientation="native") for item in candidates)
    if policy == "preserve_large_free_region": return tuple(sorted(candidates, key=lambda item: (item.size.x * item.size.y, item.module_id)))
    if policy == "balanced_footprint": return tuple(sorted(candidates, key=lambda item: (abs(item.size.x-item.size.y), -item.size.x*item.size.y, item.module_id)))
    return tuple(sorted(candidates, key=lambda item: (-item.size.x*item.size.y, item.module_id)))
def _scores(result):
    m=result.metrics; return {"compactness": m["occupancy_ratio"], "free_space": m["largest_free_region_mm3"] / max(m["total_box_volume_mm3"],1), "accessibility": 1/(1+m["rotation_count"]), "printability": 1/(1+m["auto_placed_count"]), "simplicity": 1/(1+m["modules_count"]), "coverage": m["coverage_ratio"]}
def _weighted(scores, profile): return sum(scores.get(key,0)*weight for key,weight in profile.weights.items())
