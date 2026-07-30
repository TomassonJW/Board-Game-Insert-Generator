"""Stable identity of the selected offline product result.

The complete plan digest deliberately covers search provenance and telemetry.
Those fields may vary when a wall-clock-limited portfolio completes a different
amount of non-selected work. Performance validation needs a second identity
that covers the selected geometry and its downstream product contracts only.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)


SELECTED_PRODUCT_IDENTITY_SCHEMA_V2 = (
    "bgig.selected_product_identity.v2"
)

_PLAN_FIELDS = (
    "schema_version",
    "box",
    "clearance_policy",
    "envelope_contract",
    "flat_stack",
    "invariants",
    "placements",
    "removal_sequence",
    "residuals",
    "source",
    "stage_support",
    "stages",
    "suggestions",
    "support",
    "top_inset_reservations",
    "validation",
)

_MINIMAL_LAYOUT_FIELDS = (
    "schema_version",
    "artifact_kind",
    "geometry_statement",
    "best_candidate_statement",
    "metrics",
    "residual",
    "finalization_applied",
    "automatic_body_count",
    "flat_geometry_certificate",
    "container_variant_certificate",
)


def selected_product_identity(
    plan: Mapping[str, object],
) -> dict[str, object]:
    """Return the stable, allow-listed product projection of a plan."""

    projection: dict[str, object] = {
        "schema_version": SELECTED_PRODUCT_IDENTITY_SCHEMA_V2,
        "plan": {
            field: deepcopy(plan[field])
            for field in _PLAN_FIELDS
            if field in plan
        },
    }
    minimal = plan.get("minimal_layout")
    if isinstance(minimal, Mapping):
        projection["minimal_layout"] = {
            field: deepcopy(minimal[field])
            for field in _MINIMAL_LAYOUT_FIELDS
            if field in minimal
        }
        global_certificate = minimal.get("global_certificate")
        if isinstance(global_certificate, Mapping):
            projection["minimal_layout"]["global_certificate"] = {
                field: deepcopy(value)
                for field, value in global_certificate.items()
                if field != "candidate_digest"
            }
    return projection


def selected_product_digest(plan: Mapping[str, object]) -> str:
    """Hash the selected product projection independently of search progress."""

    return canonical_digest(selected_product_identity(plan))
