"""Bounded, explainable portfolios built from deterministic P20 solves.

P21 compares a handful of stable candidate-order policies. It is not a global
optimiser, a backtracking solver, or a persistent editor. The result remains
pure Python and CAD-agnostic so a later UI or CAD adapter can consume an
explicit human selection without recalculating the layout.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import sha256
from html import escape
import json
from typing import Iterable

from board_game_insert_generator.box_fill import box_fill_plan_to_dict
from board_game_insert_generator.box_fill_solver import (
    BoxFillCandidate,
    BoxFillSolveRequest,
    BoxFillSolveResult,
    render_box_fill_solution_svg,
    solve_box_fill_greedy,
)


BOX_FILL_VARIANTS_SCHEMA_V0 = "box_fill_variants.v0"
MAX_POLICIES_V0 = 8
SUPPORTED_POLICY_IDS = (
    "compact_origin",
    "preserve_large_free_region",
    "accessibility_front",
    "minimal_rotation",
    "balanced_footprint",
)


@dataclass(frozen=True)
class VariantPreferenceProfile:
    """A preference only ranks stable raw subscores; it never changes them."""

    id: str = "balanced"
    weights: dict[str, float] = field(
        default_factory=lambda: {
            "compactness": 0.25,
            "free_space": 0.20,
            "accessibility": 0.20,
            "printability": 0.15,
            "simplicity": 0.10,
            "coverage": 0.10,
        }
    )


@dataclass(frozen=True)
class BoxFillVariantRequest:
    solve_request: BoxFillSolveRequest
    preference: VariantPreferenceProfile = field(default_factory=VariantPreferenceProfile)
    policies: tuple[str, ...] = SUPPORTED_POLICY_IDS
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


def standard_preference_profile(profile_id: str) -> VariantPreferenceProfile:
    """Return a named V0 preference profile with transparent fixed weights."""

    profiles = {
        "balanced": VariantPreferenceProfile(),
        "compact": VariantPreferenceProfile(
            "compact",
            {
                "compactness": 0.45,
                "free_space": 0.15,
                "accessibility": 0.10,
                "printability": 0.10,
                "simplicity": 0.10,
                "coverage": 0.10,
            },
        ),
        "accessible": VariantPreferenceProfile(
            "accessible",
            {
                "compactness": 0.15,
                "free_space": 0.15,
                "accessibility": 0.45,
                "printability": 0.10,
                "simplicity": 0.05,
                "coverage": 0.10,
            },
        ),
        "print_simple": VariantPreferenceProfile(
            "print_simple",
            {
                "compactness": 0.10,
                "free_space": 0.10,
                "accessibility": 0.10,
                "printability": 0.40,
                "simplicity": 0.20,
                "coverage": 0.10,
            },
        ),
    }
    try:
        return profiles[profile_id]
    except KeyError as exc:
        raise ValueError(
            f"Unknown P21 preference {profile_id!r}; expected one of: "
            + ", ".join(sorted(profiles))
        ) from exc


def generate_box_fill_variants(request: BoxFillVariantRequest) -> VariantPortfolio:
    """Generate a small deterministic portfolio without mutating its source plan."""

    _validate_request(request)
    unique: dict[str, LayoutVariant] = {}
    duplicates: dict[str, list[str]] = {}
    for policy_id in request.policies:
        candidates = _policy_candidates(request.solve_request.candidates, policy_id)
        result = solve_box_fill_greedy(replace(request.solve_request, candidates=candidates))
        layout_digest = _layout_digest(result)
        scores = _scores(result)
        existing = unique.get(layout_digest)
        if existing is not None:
            duplicates.setdefault(existing.id, []).append(policy_id)
            continue
        variant = LayoutVariant(
            id=f"variant:{policy_id}:{layout_digest[:12]}",
            policy_id=policy_id,
            result=result,
            scores=scores,
            layout_digest=layout_digest,
            reasons=_policy_reasons(policy_id),
        )
        unique[layout_digest] = variant

    ordered = tuple(
        sorted(
            unique.values(),
            key=lambda item: (-_weighted(item.scores, request.preference), item.id),
        )[: request.max_variants]
    )
    viable = tuple(item for item in ordered if item.result.status == "solved")
    recommended_variant_id = viable[0].id if viable else None
    return VariantPortfolio(
        schema_version=BOX_FILL_VARIANTS_SCHEMA_V0,
        request=request,
        variants=ordered,
        duplicate_policy_ids={key: tuple(value) for key, value in duplicates.items()},
        pareto_variant_ids=_pareto_variant_ids(viable),
        recommended_variant_id=recommended_variant_id,
        digest=_portfolio_digest(ordered, request.preference),
    )


def select_box_fill_variant(
    portfolio: VariantPortfolio,
    variant_id: str | None = None,
) -> LayoutVariant:
    """Select an explicit variant, defaulting only to the proven recommendation."""

    selected_id = portfolio.recommended_variant_id if variant_id in (None, "recommended") else variant_id
    if selected_id is None:
        raise ValueError("No solved P21 variant is available to select.")
    for variant in portfolio.variants:
        if variant.id == selected_id:
            if variant.result.status != "solved":
                raise ValueError(f"Variant {selected_id!r} is not solved and cannot be selected.")
            return variant
    raise ValueError(f"Unknown P21 variant {selected_id!r}.")


def variant_portfolio_to_dict(portfolio: VariantPortfolio) -> dict[str, object]:
    """Serialize the portfolio with full plans for reports and future adapters."""

    return {
        "schema_version": portfolio.schema_version,
        "source_plan_id": portfolio.request.solve_request.source_plan.id,
        "preference": {
            "id": portfolio.request.preference.id,
            "weights": dict(sorted(portfolio.request.preference.weights.items())),
        },
        "requested_policy_ids": list(portfolio.request.policies),
        "duplicate_policy_ids": {
            key: list(value) for key, value in sorted(portfolio.duplicate_policy_ids.items())
        },
        "pareto_variant_ids": list(portfolio.pareto_variant_ids),
        "recommended_variant_id": portfolio.recommended_variant_id,
        "portfolio_digest": portfolio.digest,
        "variants": [
            _variant_to_dict(
                variant,
                portfolio.request.preference,
                recommended=variant.id == portfolio.recommended_variant_id,
                pareto=variant.id in portfolio.pareto_variant_ids,
            )
            for variant in portfolio.variants
        ],
        "limits": list(_portfolio_limits()),
    }


def selected_variant_to_dict(
    portfolio: VariantPortfolio,
    variant_id: str | None = None,
) -> dict[str, object]:
    """Return a portable explicit selection; no UI state or source mutation occurs."""

    selected = select_box_fill_variant(portfolio, variant_id)
    return {
        "schema_version": "box_fill_variant_selection.v0",
        "portfolio_schema_version": portfolio.schema_version,
        "portfolio_digest": portfolio.digest,
        "selected_variant_id": selected.id,
        "selected_by": "recommendation" if variant_id in (None, "recommended") else "explicit_variant_id",
        "variant": _variant_to_dict(
            selected,
            portfolio.request.preference,
            recommended=selected.id == portfolio.recommended_variant_id,
            pareto=selected.id in portfolio.pareto_variant_ids,
        ),
        "limits": list(_portfolio_limits()),
    }


def format_variant_portfolio_markdown(portfolio: VariantPortfolio) -> str:
    """Produce an operational comparison a human can audit before selecting."""

    lines = [
        "# BoxFill variant portfolio",
        "",
        f"- Source plan: `{portfolio.request.solve_request.source_plan.id}`",
        f"- Portfolio schema: `{portfolio.schema_version}`",
        f"- Preference: `{portfolio.request.preference.id}`",
        f"- Deterministic digest: `{portfolio.digest}`",
        f"- Recommended variant: `{portfolio.recommended_variant_id or 'none'}`",
        f"- Pareto variants: {', '.join(portfolio.pareto_variant_ids) or 'none'}",
        "",
        "## Variants",
        "",
        "| Variant | Policy | Status | Weighted score | Compactness | Free space | Access | Print | Simplicity | Coverage |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant in portfolio.variants:
        scores = variant.scores
        marker = " recommended" if variant.id == portfolio.recommended_variant_id else ""
        lines.append(
            "| `{id}`{marker} | `{policy}` | `{status}` | {weighted:.3f} | {compactness:.3f} | "
            "{free_space:.3f} | {accessibility:.3f} | {printability:.3f} | "
            "{simplicity:.3f} | {coverage:.3f} |".format(
                id=variant.id,
                marker=marker,
                policy=variant.policy_id,
                status=variant.result.status,
                weighted=_weighted(variant.scores, portfolio.request.preference),
                **scores,
            )
        )
    if not portfolio.variants:
        lines.append("| none | - | `blocked` | - | - | - | - | - | - | - |")
    lines.extend(["", "## Duplicate policies", ""])
    if portfolio.duplicate_policy_ids:
        for canonical, duplicates in sorted(portfolio.duplicate_policy_ids.items()):
            lines.append(f"- `{', '.join(duplicates)}` produced the same geometry as `{canonical}`.")
    else:
        lines.append("- None.")
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {limit}" for limit in _portfolio_limits())
    lines.append("")
    return "\n".join(lines)


def render_variant_portfolio_html(portfolio: VariantPortfolio, layer_id: str | None = None) -> str:
    """Render a self-contained static comparison dashboard (not a persistent app)."""

    cards = "".join(_variant_card_html(portfolio, variant, layer_id) for variant in portfolio.variants)
    recommendation = portfolio.recommended_variant_id or "No solved variant is available."
    duplicate_summary = "; ".join(
        f"{', '.join(values)} -> {key}" for key, values in sorted(portfolio.duplicate_policy_ids.items())
    ) or "None"
    limits = "".join(f"<li>{escape(limit)}</li>" for limit in _portfolio_limits())
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>BGIG BoxFill variant portfolio</title>
<style>
:root {{ color-scheme: light; font-family: Inter, Segoe UI, system-ui, sans-serif; color: #172033; background: #f4f7fb; }}
body {{ margin: 0; }} main {{ max-width: 1200px; margin: auto; padding: 28px; }} h1, h2, h3, p {{ margin-top: 0; }}
.eyebrow {{ color: #51617a; font-size: .85rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }}
.summary {{ background: #172033; color: #f7f9fc; border-radius: 16px; padding: 20px; margin-bottom: 24px; }} .summary code {{ color: #c7d9ff; overflow-wrap: anywhere; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 18px; }}
.card {{ background: #fff; border: 1px solid #dbe3ef; border-radius: 16px; padding: 18px; box-shadow: 0 6px 20px rgba(32, 52, 84, .08); }}
.card.recommended {{ border: 2px solid #2c67d7; box-shadow: 0 8px 24px rgba(44, 103, 215, .18); }}
.badge {{ display: inline-block; padding: 4px 8px; border-radius: 999px; background: #e7eefc; color: #1645a0; font-size: .78rem; font-weight: 700; }}
.status {{ color: #19703d; font-weight: 700; }} .scores {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 12px; font-size: .9rem; }} .scores strong {{ float: right; }}
.preview {{ background: #f8fafc; border: 1px solid #e1e8f2; border-radius: 10px; padding: 8px; margin-top: 14px; overflow: auto; }} .preview svg {{ display: block; min-width: 280px; width: 100%; max-height: 220px; }}
.limits {{ color: #51617a; font-size: .92rem; }} code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
</style>
</head>
<body><main>
<p class=\"eyebrow\">BGIG â€¢ static P21 comparison</p><h1>Choose a BoxFill layout with evidence</h1>
<section class=\"summary\"><p>Recommended selection</p><h2><code>{escape(recommendation)}</code></h2>
<p>Preference: <code>{escape(portfolio.request.preference.id)}</code> Â· portfolio digest: <code>{escape(portfolio.digest)}</code></p><p>Duplicate policies: {escape(duplicate_summary)}</p></section>
<section class=\"cards\">{cards}</section><section class=\"limits\"><h2>What this page does not claim</h2><ul>{limits}</ul></section>
</main></body></html>
"""


def _validate_request(request: BoxFillVariantRequest) -> None:
    if not request.policies:
        raise ValueError("P21 requires at least one deterministic policy.")
    if len(request.policies) > MAX_POLICIES_V0:
        raise ValueError(f"P21 supports at most {MAX_POLICIES_V0} policies per portfolio.")
    unknown = sorted(set(request.policies) - set(SUPPORTED_POLICY_IDS))
    if unknown:
        raise ValueError("Unsupported P21 policy ids: " + ", ".join(unknown))
    if request.max_variants < 1:
        raise ValueError("P21 max_variants must be at least 1.")
    if any(weight < 0.0 for weight in request.preference.weights.values()):
        raise ValueError("P21 preference weights cannot be negative.")


def _policy_candidates(candidates: tuple[BoxFillCandidate, ...], policy_id: str) -> tuple[BoxFillCandidate, ...]:
    """Encode a policy as a stable rank while retaining user priority precedence."""

    if policy_id == "preserve_large_free_region":
        ordered = sorted(candidates, key=lambda item: (item.size.x * item.size.y, item.module_id))
    elif policy_id == "accessibility_front":
        ordered = sorted(candidates, key=lambda item: (-item.priority, item.size.y, item.size.x, item.module_id))
    elif policy_id == "balanced_footprint":
        ordered = sorted(candidates, key=lambda item: (abs(item.size.x - item.size.y), -(item.size.x * item.size.y), item.module_id))
    else:
        ordered = sorted(candidates, key=lambda item: (-(item.size.x * item.size.y), -max(item.size.x, item.size.y), item.module_id))

    rank_span = len(ordered) + 1
    return tuple(
        replace(
            candidate,
            priority=(candidate.priority * rank_span) + (len(ordered) - index),
            preferred_orientation="native" if policy_id == "minimal_rotation" else candidate.preferred_orientation,
        )
        for index, candidate in enumerate(ordered)
    )


def _scores(result: BoxFillSolveResult) -> dict[str, float]:
    metrics = result.metrics
    candidates_count = max(int(metrics["candidates_count"]), 1)
    refused_ratio = int(metrics["auto_refused_count"]) / candidates_count
    return {
        "compactness": _layout_compactness(result),
        "free_space": float(metrics["largest_free_region_mm3"]) / max(float(metrics["total_box_volume_mm3"]), 1.0),
        "accessibility": 1.0 / (1.0 + float(metrics["rotation_count"])),
        "printability": 1.0 - refused_ratio,
        "simplicity": 1.0 / (1.0 + float(metrics["modules_count"])),
        "coverage": float(metrics["coverage_ratio"]),
    }


def _layout_compactness(result: BoxFillSolveResult) -> float:
    """Measure how densely module footprints occupy their own per-layer envelope."""

    densities: list[float] = []
    for layer in result.solved_plan.layers:
        modules = [module for module in result.solved_plan.modules if module.layer_id == layer.id]
        if not modules:
            continue
        occupied_area = sum(module.size.x * module.size.y for module in modules)
        min_x = min(module.origin.x for module in modules)
        max_x = max(module.origin.x + module.size.x for module in modules)
        min_y = min(module.origin.y for module in modules)
        max_y = max(module.origin.y + module.size.y for module in modules)
        envelope_area = max((max_x - min_x) * (max_y - min_y), 1.0)
        densities.append(occupied_area / envelope_area)
    return sum(densities) / len(densities) if densities else 0.0


def _weighted(scores: dict[str, float], profile: VariantPreferenceProfile) -> float:
    return sum(scores.get(key, 0.0) * weight for key, weight in profile.weights.items())


def _layout_digest(result: BoxFillSolveResult) -> str:
    layout = [(item.module_id, item.origin.x, item.origin.y, item.origin.z, item.orientation) for item in result.placements]
    return sha256(json.dumps(layout, sort_keys=True).encode("utf-8")).hexdigest()


def _portfolio_digest(variants: Iterable[LayoutVariant], preference: VariantPreferenceProfile) -> str:
    payload = [(item.id, item.layout_digest, sorted(item.scores.items())) for item in variants]
    return sha256(json.dumps({"variants": payload, "preference": [preference.id, sorted(preference.weights.items())]}, sort_keys=True).encode("utf-8")).hexdigest()


def _pareto_variant_ids(variants: tuple[LayoutVariant, ...]) -> tuple[str, ...]:
    front: list[str] = []
    for candidate in variants:
        dominated = any(
            other.id != candidate.id
            and all(other.scores[key] >= candidate.scores[key] for key in candidate.scores)
            and any(other.scores[key] > candidate.scores[key] for key in candidate.scores)
            for other in variants
        )
        if not dominated:
            front.append(candidate.id)
    return tuple(sorted(front))


def _variant_to_dict(variant: LayoutVariant, preference: VariantPreferenceProfile, *, recommended: bool, pareto: bool) -> dict[str, object]:
    return {
        "id": variant.id,
        "policy_id": variant.policy_id,
        "status": variant.result.status,
        "layout_digest": variant.layout_digest,
        "weighted_score": _weighted(variant.scores, preference),
        "subscores": dict(sorted(variant.scores.items())),
        "reasons": list(variant.reasons),
        "recommended": recommended,
        "pareto": pareto,
        "solution": {**variant.result.to_dict(), "solved_plan": box_fill_plan_to_dict(variant.result.solved_plan)},
    }


def _policy_reasons(policy_id: str) -> tuple[str, ...]:
    messages = {
        "compact_origin": "Larger footprints are considered first to make the origin compact under the bounded greedy rule.",
        "preserve_large_free_region": "Smaller footprints are considered first; this is only an ordering heuristic, not a guarantee about usable free space.",
        "accessibility_front": "Candidates are ordered for a front-oriented comparison; physical reachability still needs human validation.",
        "minimal_rotation": "Native orientation is preferred whenever P20 can choose it; no print or ergonomic claim is implied.",
        "balanced_footprint": "Near-square footprints are considered first to compare a balanced 2D packing order.",
    }
    return (messages[policy_id], "Executed through bounded deterministic P20 greedy placement without backtracking.")


def _portfolio_limits() -> tuple[str, ...]:
    return (
        "No backtracking, exhaustive search, global optimisation or learned scoring is performed.",
        "Scores compare declared geometric proxies; they do not validate physical ergonomics or printability.",
        "This static dashboard stores no persistent UI state and does not edit the source plan.",
        "Fusion is not recalculated or materialised from this portfolio; a later adapter must consume an explicit selection.",
        "No 3D print, slicer or physical tolerance validation is claimed.",
    )


def _variant_card_html(portfolio: VariantPortfolio, variant: LayoutVariant, layer_id: str | None) -> str:
    scores = variant.scores
    layers = (layer_id,) if layer_id else tuple(layer.id for layer in variant.result.solved_plan.layers)
    previews = "".join(
        f'<div class="preview"><strong>Layer {escape(current_layer_id)}</strong>{render_box_fill_solution_svg(variant.result, current_layer_id)}</div>'
        for current_layer_id in layers
    )
    badge = '<span class="badge">Recommended</span>' if variant.id == portfolio.recommended_variant_id else ""
    return f'''<article class="card{' recommended' if badge else ''}">
<p>{badge}</p><h2><code>{escape(variant.id)}</code></h2>
<p>Policy <code>{escape(variant.policy_id)}</code> Â· <span class="status">{escape(variant.result.status)}</span></p>
<p>Weighted score <strong>{_weighted(scores, portfolio.request.preference):.3f}</strong></p>
<div class="scores"><span>Compactness <strong>{scores['compactness']:.3f}</strong></span><span>Free space <strong>{scores['free_space']:.3f}</strong></span><span>Access proxy <strong>{scores['accessibility']:.3f}</strong></span><span>Print proxy <strong>{scores['printability']:.3f}</strong></span><span>Simplicity <strong>{scores['simplicity']:.3f}</strong></span><span>Coverage <strong>{scores['coverage']:.3f}</strong></span></div>{previews}</article>'''
