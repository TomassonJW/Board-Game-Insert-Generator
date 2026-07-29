"""Corpus produit P64-L09W-B et vérités indépendantes du solveur.

Les cas positifs sont construits dans l'espace ``project.v1``. Leur placement
témoin est produit avant tout appel au solveur évalué, puis recertifié par le
certificat commun BGIG. Le holdout conserve ses recettes dans un sidecar privé ;
le manifest versionné n'en publie que l'engagement et les agrégats préenregistrés.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from math import ceil, isclose, sqrt
import secrets
from typing import Iterable, Mapping, Sequence

from .expandable_envelope import derive_expandable_envelope_contract
from .free_3d_greedy_solver import Free3DPlacement
from .free_3d_plan_adapter import (
    CertifiedFree3DPlan,
    Free3DPreparedProblem,
    certify_free_3d_plan,
    prepare_free_3d_problem,
)
from .incremental_project_state import canonical_digest
from .project_v1 import blank_project_v1, normalize_project_draft
from .solver_contract import SolverStrategy
from .solver_portfolio import portfolio_effort_profiles
from .top_inset_reservation import resolve_top_inset_reservations


MANIFEST_SCHEMA = "bgig.product_solver_robustness_corpus.v1"
SEALED_HOLDOUT_SCHEMA = "bgig.product_solver_robustness_holdout.v1"
HOLDOUT_RECEIPT_SCHEMA = "bgig.product_solver_robustness_holdout_receipt.v1"
POSITIVE_CASE_SCHEMA = "bgig.product_solver_robustness_positive_case.v1"
NEGATIVE_CASE_SCHEMA = "bgig.product_solver_robustness_negative_control.v1"
ORACLE_RECEIPT_SCHEMA = "bgig.product_solver_robustness_oracle_receipt.v1"
WITNESS_SCHEMA = "bgig.product_solver_robustness_witness.v1"
EDIT_SEQUENCE_SCHEMA = "bgig.product_solver_robustness_edit_sequence.v1"
NEGATIVE_PROOF_SCHEMA = "bgig.product_solver_robustness_negative_proof.v1"
SOAK_PLAN_SCHEMA = "bgig.product_solver_robustness_soak_plan.v1"
GENERATOR_VERSION = "p64-l09w-product-pairwise-v2"
REGRESSION_BASELINE_SCHEMA = "bgig.p64_l09w_a_solver_robustness_evidence.v1"
REGRESSION_BASELINE_ARTIFACT = (
    "tests/fixtures/p64_l09w_a_solver_robustness_baseline.v1.json"
)
REGRESSION_BASELINE_REPORT_DIGEST = (
    "26aed0b36c47396ed54291193e89913c680f603c02090936fc4932e311987105"
)

OPEN_POSITIVE_COUNT = 400
DISCOVERY_COUNT = 240
TUNING_COUNT = 160
HOLDOUT_POSITIVE_COUNT = 400
NEGATIVE_CONTROL_COUNT = 40
SOAK_RECIPE_COUNT = 2_000

CONTENTS_PER_CONTAINER_VALUES = (1, 2, 4, 8, 16, 32, 64)
CONTAINER_COUNT_VALUES = (1, 2, 4, 8, 12, 18, 30, 50, 64)
DENSITY_VALUES = (30, 65, 85, 95)
FLAT_COUNT_VALUES = (0, 1, 2, 3, 4, 5, 6, 10)
BOX_SIZE_VALUES = ("small", "medium", "large")
EXECUTION_VALUES = (
    "cold",
    "add",
    "remove",
    "local_parameter",
    "global_parameter",
)

_LAYOUT_CLEARANCE_MM = 0.6
_BOX_XY_CLEARANCE_MM = 0.6
_Z_CLEARANCE_MM = 0.6
_WALL_MM = 1.2
_FLOOR_MM = 1.2
_CONTENT_CLEARANCE_MM = 0.6
_GRID_EPSILON_MM = 0.0001
_SIZE_ANCHORS_MM = {"small": 120.0, "medium": 220.0, "large": 360.0}
_ASPECT_FACTORS = (
    (1.0, 1.0, 0.72, "balanced"),
    (1.75, 0.72, 0.62, "wide"),
    (0.72, 1.75, 0.88, "deep"),
    (1.03, 0.97, 1.18, "near-equal-xy"),
    (1.35, 0.86, 1.42, "tall"),
)


class ProductRobustnessCorpusError(ValueError):
    """Le corpus ou l'une de ses preuves ne respecte pas son contrat."""


def build_open_recipe_plan() -> list[dict[str, object]]:
    """Construire les 400 recettes positives ouvertes sans lancer le solveur."""

    return [
        _design_positive_recipe(
            ordinal,
            namespace="open-p64-l09w-b-v1",
            phase=0,
        )
        for ordinal in range(OPEN_POSITIVE_COUNT)
    ]


def build_holdout_recipe_plan(
    *,
    campaign_nonce: str,
) -> list[dict[str, object]]:
    """Construire les recettes privées distinctes du holdout fermé."""

    _require_nonce(campaign_nonce)
    phase = int(campaign_nonce[:8], 16)
    namespace = f"holdout-{canonical_digest({'nonce': campaign_nonce})[:20]}"
    return [
        _design_positive_recipe(
            ordinal,
            namespace=namespace,
            phase=phase,
        )
        for ordinal in range(HOLDOUT_POSITIVE_COUNT)
    ]


def build_positive_case_record(
    recipe: Mapping[str, object],
) -> dict[str, object]:
    """Engager et recertifier un cas positif sans appeler le solveur évalué."""

    accepted_recipe = validate_positive_recipe(recipe)
    bundle = materialize_positive_case_bundle(accepted_recipe)
    oracle = certify_independent_witness(
        bundle["after_project"],
        bundle["witness"],
        case_id=str(accepted_recipe["case_id"]),
    )
    payload: dict[str, object] = {
        "schema_version": POSITIVE_CASE_SCHEMA,
        "case_id": accepted_recipe["case_id"],
        "split": accepted_recipe["split"],
        "stratum": accepted_recipe["stratum"],
        "expected": "feasible",
        "axes": deepcopy(accepted_recipe["axes"]),
        "recipe": accepted_recipe,
        "recipe_digest": canonical_digest(accepted_recipe),
        "seed_digest": canonical_digest({"seed": accepted_recipe["seed"]}),
        "project_digest": canonical_digest(bundle["after_project"]),
        "before_project_digest": (
            None
            if bundle["before_project"] is None
            else canonical_digest(bundle["before_project"])
        ),
        "edit_sequence_digest": canonical_digest(bundle["edit_sequence"]),
        "witness_digest": canonical_digest(bundle["witness"]),
        "oracle_receipt": oracle,
        "solver_invocation_count": 0,
    }
    payload["case_digest"] = canonical_digest(payload)
    return validate_positive_case_record(payload)


def build_open_case_records(
    recipes: Sequence[Mapping[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Recertifier les 400 cas ouverts discovery puis tuning."""

    selected = list(recipes) if recipes is not None else build_open_recipe_plan()
    if len(selected) != OPEN_POSITIVE_COUNT:
        raise ProductRobustnessCorpusError(
            f"Open corpus needs {OPEN_POSITIVE_COUNT} positive recipes."
        )
    records = [build_positive_case_record(recipe) for recipe in selected]
    validate_positive_distribution(records, expected_count=OPEN_POSITIVE_COUNT)
    return records


def build_sealed_holdout(
    *,
    campaign_nonce: str | None = None,
    recipes: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Créer le sidecar privé et fermé des 400 cas positifs."""

    nonce = campaign_nonce or secrets.token_hex(32)
    _require_nonce(nonce)
    selected = (
        list(recipes)
        if recipes is not None
        else build_holdout_recipe_plan(campaign_nonce=nonce)
    )
    if len(selected) != HOLDOUT_POSITIVE_COUNT:
        raise ProductRobustnessCorpusError(
            f"Holdout needs {HOLDOUT_POSITIVE_COUNT} positive recipes."
        )
    records = [build_positive_case_record(recipe) for recipe in selected]
    return seal_holdout_records(
        campaign_nonce=nonce,
        records=records,
    )


def seal_holdout_records(
    *,
    campaign_nonce: str,
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Assembler un sidecar depuis des cas déjà recertifiés et checkpointés."""

    _require_nonce(campaign_nonce)
    accepted_records = [
        validate_positive_case_record(record, reconstruct=False)
        for record in records
    ]
    coverage = validate_positive_distribution(
        accepted_records,
        expected_count=HOLDOUT_POSITIVE_COUNT,
    )
    payload: dict[str, object] = {
        "schema_version": SEALED_HOLDOUT_SCHEMA,
        "campaign_nonce": campaign_nonce,
        "generator_version": GENERATOR_VERSION,
        "case_records": accepted_records,
        "coverage": coverage,
        "opened": False,
        "opening_count": 0,
        "solver_invocation_count": 0,
    }
    payload["sealed_holdout_digest"] = canonical_digest(payload)
    return validate_sealed_holdout(payload)


def materialize_positive_case_bundle(
    recipe: Mapping[str, object],
) -> dict[str, object]:
    """Reconstruire projet avant/après, édition et témoin indépendant."""

    accepted = validate_positive_recipe(recipe)
    after = _materialize_project(accepted, phase="after")
    execution = str(_mapping(accepted["axes"])["execution"])
    before = None if execution == "cold" else _materialize_project(accepted, phase="before")
    edit_sequence = _materialize_edit_sequence(accepted)
    witness = materialize_positive_witness(accepted)
    return {
        "after_project": after,
        "before_project": before,
        "edit_sequence": edit_sequence,
        "witness": witness,
    }


def materialize_positive_witness(
    recipe: Mapping[str, object],
) -> dict[str, object]:
    """Construire le placement sans consulter un résultat du solveur."""

    accepted = validate_positive_recipe(recipe)
    axes = _mapping(accepted["axes"])
    body = _dimension(accepted["body_size_mm"])
    box = _dimension(accepted["box_inner_dimensions_mm"])
    grid = _mapping(accepted["placement_grid"])
    group_count = int(axes["container_count"])
    layers = int(axes["layer_count"])
    columns = int(grid["columns"])
    bottom_margin = float(grid["bottom_margin_mm"])
    placements: list[dict[str, object]] = []
    for group_index in range(group_count):
        stack_index = group_index // layers
        layer_index = group_index % layers
        column = stack_index % columns
        row = stack_index // columns
        origin = {
            "x": _nearest_tenth(
                _BOX_XY_CLEARANCE_MM
                + column * (body["x"] + _LAYOUT_CLEARANCE_MM)
            ),
            "y": _nearest_tenth(
                _BOX_XY_CLEARANCE_MM
                + row * (body["y"] + _LAYOUT_CLEARANCE_MM)
            ),
            "z": _nearest_tenth(
                bottom_margin
                + layer_index * (body["z"] + _Z_CLEARANCE_MM)
            ),
        }
        support_group_ids = (
            []
            if layer_index == 0
            else [f"group-{group_index - 1:03d}"]
        )
        placements.append(
            {
                "container_group_id": f"group-{group_index:03d}",
                "origin_mm": origin,
                "world_size_mm": deepcopy(body),
                "rotation_deg_z": 0,
                "support_group_ids": support_group_ids,
                "support_coverage_ratio": 1.0,
            }
        )
    highest = max(
        placement["origin_mm"]["z"] + placement["world_size_mm"]["z"]
        for placement in placements
    )
    if not isclose(highest, box["z"], abs_tol=0.001):
        raise ProductRobustnessCorpusError(
            "Constructed witness does not reach the design top."
        )
    return {
        "schema_version": WITNESS_SCHEMA,
        "case_id": accepted["case_id"],
        "constructed_without_solver": True,
        "solver_invocation_count": 0,
        "placements": placements,
        "constructive_metrics": deepcopy(accepted["constructive_metrics"]),
    }


def certify_independent_witness(
    raw_project: Mapping[str, object],
    witness: Mapping[str, object],
    *,
    case_id: str,
) -> dict[str, object]:
    """Recertifier le témoin par la chaîne produit, jamais par le solveur testé."""

    project = deepcopy(dict(raw_project))
    flat_items = list(project.get("flat_items", []))
    if flat_items:
        scaffold_project = deepcopy(project)
        scaffold_project["flat_items"] = []
        scaffold_preparation = prepare_free_3d_problem(scaffold_project)
        scaffold_problem = _require_prepared_problem(
            scaffold_preparation.status,
            scaffold_preparation.problem,
            scaffold_preparation.rejection_codes,
            context="scaffold",
        )
        placements = _free_3d_placements(scaffold_problem, witness)
        scaffold = _certify_constructed_placements(
            scaffold_problem,
            placements,
            candidate_id=f"{case_id}:scaffold",
        )
        top_inset_plan = resolve_top_inset_reservations(
            project,
            scaffold.plan["placements"],
            require_reserved_prisms=False,
        )
        if top_inset_plan.get("status") == "blocked":
            raise ProductRobustnessCorpusError(
                "Independent top-inset oracle is blocked: "
                + ",".join(
                    str(value.get("code"))
                    for value in _mappings(top_inset_plan.get("blockers"))
                )
            )
        preparation = prepare_free_3d_problem(
            project,
            top_inset_plan=top_inset_plan,
        )
        problem = _require_prepared_problem(
            preparation.status,
            preparation.problem,
            preparation.rejection_codes,
            context="full-project",
        )
        certified = _certify_constructed_placements(
            problem,
            _free_3d_placements(problem, witness),
            candidate_id=f"{case_id}:full",
        )
        scaffold_digest = _validation_certificate_digest(scaffold)
        top_inset_plan_digest = canonical_digest(top_inset_plan)
    else:
        preparation = prepare_free_3d_problem(project)
        problem = _require_prepared_problem(
            preparation.status,
            preparation.problem,
            preparation.rejection_codes,
            context="full-project",
        )
        certified = _certify_constructed_placements(
            problem,
            _free_3d_placements(problem, witness),
            candidate_id=f"{case_id}:full",
        )
        scaffold_digest = None
        top_inset_plan_digest = canonical_digest(problem.top_inset_plan)

    payload: dict[str, object] = {
        "schema_version": ORACLE_RECEIPT_SCHEMA,
        "validator_schema": certified.certificate.schema_version,
        "certified": certified.certificate.certified,
        "candidate_digest": certified.certificate.candidate_digest,
        "certificate_digest": _validation_certificate_digest(certified),
        "placement_digest": certified.placement_digest,
        "scaffold_certificate_digest": scaffold_digest,
        "top_inset_plan_digest": top_inset_plan_digest,
        "container_variant_selection_count": len(
            certified.selected_container_variants
        ),
        "strictly_subtractive_top_insets": bool(flat_items),
        "solver_invocation_count": 0,
    }
    payload["oracle_digest"] = canonical_digest(payload)
    return payload


def validate_positive_recipe(
    value: Mapping[str, object],
) -> dict[str, object]:
    recipe = deepcopy(dict(value))
    if recipe.get("generator_version") != GENERATOR_VERSION:
        raise ProductRobustnessCorpusError("Unknown positive recipe version.")
    case_id = recipe.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise ProductRobustnessCorpusError("Positive recipe case id is missing.")
    if recipe.get("split") not in {"discovery", "tuning", "holdout", "soak"}:
        raise ProductRobustnessCorpusError("Positive recipe split is invalid.")
    axes = recipe.get("axes")
    if not isinstance(axes, dict):
        raise ProductRobustnessCorpusError("Positive recipe axes are missing.")
    group_count = int(axes.get("container_count", 0))
    content_count = int(axes.get("contents_per_container", 0))
    flat_count = int(axes.get("flat_count", -1))
    layer_count = int(axes.get("layer_count", 0))
    density = int(axes.get("target_density_pct", 0))
    if group_count not in CONTAINER_COUNT_VALUES:
        raise ProductRobustnessCorpusError("Container-count axis is outside the gate.")
    if content_count not in CONTENTS_PER_CONTAINER_VALUES:
        raise ProductRobustnessCorpusError(
            "Contents-per-container axis is outside the gate."
        )
    if group_count * content_count > 512:
        raise ProductRobustnessCorpusError("Positive recipe exceeds 512 content records.")
    if flat_count not in FLAT_COUNT_VALUES:
        raise ProductRobustnessCorpusError("Flat-count axis is outside the gate.")
    if density not in DENSITY_VALUES:
        raise ProductRobustnessCorpusError("Density axis is outside the gate.")
    if layer_count < 1 or group_count % layer_count:
        raise ProductRobustnessCorpusError(
            "Layer count must divide the container count."
        )
    if axes.get("box_size") not in BOX_SIZE_VALUES:
        raise ProductRobustnessCorpusError("Box-size axis is invalid.")
    if axes.get("execution") not in EXECUTION_VALUES:
        raise ProductRobustnessCorpusError("Execution axis is invalid.")
    quantity = int(recipe.get("quantity_per_record", 0))
    developed = group_count * content_count * quantity
    if quantity < 1 or developed > 4_096:
        raise ProductRobustnessCorpusError("Developed content count is outside the gate.")
    body = _dimension(recipe.get("body_size_mm"))
    box = _dimension(recipe.get("box_inner_dimensions_mm"))
    if min(body.values()) <= 0.0 or min(box.values()) <= 0.0:
        raise ProductRobustnessCorpusError("Recipe dimensions must be positive.")
    size = _classify_box(box)
    if size != axes["box_size"]:
        raise ProductRobustnessCorpusError(
            f"Box-size commitment says {axes['box_size']} but reconstructs {size}."
        )
    metrics = recipe.get("constructive_metrics")
    if not isinstance(metrics, dict):
        raise ProductRobustnessCorpusError("Constructive metrics are missing.")
    actual_density = float(metrics.get("useful_density_pct", -1.0))
    if abs(actual_density - density) > 0.35:
        raise ProductRobustnessCorpusError(
            "Constructive density is not close to its preregistered target."
        )
    expected_stratum = _classify_stratum(axes, metrics)
    if recipe.get("stratum") != expected_stratum:
        raise ProductRobustnessCorpusError("Positive stratum is misclassified.")
    expected_pose_mode = (
        "automatic" if expected_stratum == "common" else "explicit-stacked"
    )
    if recipe.get("flat_pose_mode") != expected_pose_mode:
        raise ProductRobustnessCorpusError("Flat pose mode is misclassified.")
    if recipe.get("split") == "discovery" and recipe.get("stratum") != "common":
        raise ProductRobustnessCorpusError("Discovery must contain the common 240.")
    if recipe.get("split") == "tuning" and recipe.get("stratum") != "stress":
        raise ProductRobustnessCorpusError("Tuning must contain the stress 160.")
    return recipe


def _design_positive_recipe(
    ordinal: int,
    *,
    namespace: str,
    phase: int,
) -> dict[str, object]:
    if ordinal < 0 or ordinal >= OPEN_POSITIVE_COUNT:
        raise ProductRobustnessCorpusError("Positive recipe ordinal is out of range.")
    axes = _scheduled_axes(ordinal, phase=phase)
    split = (
        "holdout"
        if namespace.startswith("holdout-")
        else "discovery"
        if ordinal < DISCOVERY_COUNT
        else "tuning"
    )
    case_seed = _seed_for(namespace, ordinal)
    case_id = (
        f"p64-l09w-{split}-{ordinal:03d}-"
        f"{canonical_digest({'namespace': namespace, 'seed': case_seed})[:10]}"
    )
    quantity = _quantity_per_record(
        int(axes["container_count"]),
        int(axes["contents_per_container"]),
        seed=case_seed,
        execution=str(axes["execution"]),
    )
    sizing_extra = 1 if axes["execution"] in {"add", "remove"} else 0
    minimum = _minimum_body_size(
        int(axes["contents_per_container"]),
        quantity,
        sizing_extra,
    )
    flat_thicknesses = [
        _nearest_tenth(0.3 + 0.1 * ((case_seed + index) % 3))
        for index in range(int(axes["flat_count"]))
    ]
    flat_total = sum(flat_thicknesses)
    aspect = _ASPECT_FACTORS[(ordinal + phase) % len(_ASPECT_FACTORS)]
    requested_size = str(axes["box_size"])
    geometry = None
    for size_class in BOX_SIZE_VALUES[BOX_SIZE_VALUES.index(requested_size) :]:
        try:
            geometry = _design_geometry(
                group_count=int(axes["container_count"]),
                layer_count=int(axes["layer_count"]),
                density_pct=int(axes["target_density_pct"]),
                size_class=size_class,
                stratum=str(axes["stratum"]),
                minimum_body=minimum,
                flat_total_height_mm=flat_total,
                aspect_factors=aspect[:3],
            )
        except ProductRobustnessCorpusError:
            continue
        axes["box_size"] = size_class
        break
    if geometry is None:
        raise ProductRobustnessCorpusError(
            f"No supported box size can realize positive recipe {case_id}."
        )
    metrics = _constructive_metrics(
        axes,
        geometry,
        flat_count=int(axes["flat_count"]),
    )
    recipe: dict[str, object] = {
        "generator_version": GENERATOR_VERSION,
        "case_id": case_id,
        "seed": case_seed,
        "ordinal": ordinal,
        "split": split,
        "stratum": axes["stratum"],
        "axes": axes,
        "quantity_per_record": quantity,
        "content_pattern": "compact-orthogonal-assets-v1",
        "aspect_profile": aspect[3],
        "body_size_mm": geometry["body"],
        "box_inner_dimensions_mm": geometry["box"],
        "placement_grid": geometry["grid"],
        "flat_thicknesses_mm": flat_thicknesses,
        "flat_pose_mode": (
            "automatic"
            if axes["stratum"] == "common"
            else "explicit-stacked"
        ),
        "constructive_metrics": metrics,
        "product_constants": {
            "layout_clearance_mm": _LAYOUT_CLEARANCE_MM,
            "container_box_xy_clearance_mm": _BOX_XY_CLEARANCE_MM,
            "container_z_clearance_mm": _Z_CLEARANCE_MM,
            "default_wall_thickness_mm": _WALL_MM,
            "default_floor_thickness_mm": _FLOOR_MM,
            "default_content_clearance_mm": _CONTENT_CLEARANCE_MM,
            "product_grid_mm": 0.1,
            "geometry_epsilon_mm": _GRID_EPSILON_MM,
        },
    }
    return validate_positive_recipe(recipe)


def _scheduled_axes(ordinal: int, *, phase: int) -> dict[str, object]:
    if ordinal < DISCOVERY_COUNT:
        local = ordinal
        groups = (1, 2, 4, 8, 12, 18)[(local + phase) % 6]
        contents = (1, 2, 4, 8, 16)[(local * 2 + local // 5 + phase) % 5]
        density = (30, 65, 85)[(local + local // 7 + phase) % 3]
        flats = (0, 1, 2)[(local * 2 + local // 11 + phase) % 3]
        if groups in {12, 18}:
            layers = 3
        else:
            allowed_layers = [
                value for value in (1, 2) if groups % value == 0
            ]
            layers = allowed_layers[
                (local + local // 13 + phase) % len(allowed_layers)
            ]
        size = BOX_SIZE_VALUES[(local * 2 + local // 17 + phase) % 3]
        execution = EXECUTION_VALUES[(local * 3 + local // 19 + phase) % 5]
        stratum = "common"
    else:
        local = ordinal - DISCOVERY_COUNT
        if local < 80:
            groups = (30, 50, 64, 30, 50, 64, 30, 50)[
                (local + phase) % 8
            ]
            contents = (1, 2, 4, 8)[(local * 3 + phase) % 4]
            layer_options = {
                30: (5, 6),
                50: (5, 10),
                64: (4, 8),
            }[groups]
            layers = layer_options[(local + phase) % len(layer_options)]
            density = 95
            size = ("medium", "large")[(local + phase) % 2]
        else:
            high_local = local - 80
            groups = (1, 2, 4, 8)[(high_local + phase) % 4]
            contents = (32, 64)[(high_local * 3 + phase) % 2]
            layers = {
                1: 1,
                2: 2,
                4: 4,
                8: (4, 8)[(high_local + phase) % 2],
            }[groups]
            density = (30, 65, 85, 95)[(high_local + phase) % 4]
            size = BOX_SIZE_VALUES[(high_local * 2 + phase) % 3]
        flats = (3, 4, 5, 6, 10)[(local * 3 + phase) % 5]
        execution = EXECUTION_VALUES[(local * 2 + local // 7 + phase) % 5]
        stratum = "stress"
    return {
        "container_count": groups,
        "contents_per_container": contents,
        "target_density_pct": density,
        "flat_count": flats,
        "layer_count": layers,
        "layer_bucket": "4+" if layers >= 4 else str(layers),
        "box_size": size,
        "execution": execution,
        "stratum": stratum,
    }


def _design_geometry(
    *,
    group_count: int,
    layer_count: int,
    density_pct: int,
    size_class: str,
    stratum: str,
    minimum_body: Mapping[str, object],
    flat_total_height_mm: float,
    aspect_factors: Sequence[float],
) -> dict[str, object]:
    target_largest = _SIZE_ANCHORS_MM[size_class]
    minimum = _dimension(minimum_body)

    def candidate(scale: float) -> dict[str, object] | None:
        minimum_required = {
            "x": minimum["x"] + 0.2,
            "y": minimum["y"] + 0.2,
            "z": minimum["z"] + flat_total_height_mm + _FLOOR_MM + 0.2,
        }
        required = (
            {
                axis: value / 0.96
                for axis, value in minimum_required.items()
            }
            if stratum == "common"
            else minimum_required
        )
        body = {
            "x": _ceil_tenth(max(required["x"], scale * aspect_factors[0])),
            "y": _ceil_tenth(max(required["y"], scale * aspect_factors[1])),
            "z": _ceil_tenth(max(required["z"], scale * aspect_factors[2])),
        }
        stacks = group_count // layer_count
        columns, rows = _factor_grid(stacks, body["x"], body["y"])
        stack_height = (
            layer_count * body["z"]
            + (layer_count - 1) * _Z_CLEARANCE_MM
        )
        bottom_margin = 0.0
        base_box = {
            "x": _ceil_tenth(
                2.0 * _BOX_XY_CLEARANCE_MM
                + columns * body["x"]
                + (columns - 1) * _LAYOUT_CLEARANCE_MM
            ),
            "y": _ceil_tenth(
                2.0 * _BOX_XY_CLEARANCE_MM
                + rows * body["y"]
                + (rows - 1) * _LAYOUT_CLEARANCE_MM
            ),
            "z": _ceil_tenth(stack_height + bottom_margin),
        }
        if stratum == "common":
            occupied_x = (
                columns * body["x"]
                + (columns - 1) * _LAYOUT_CLEARANCE_MM
            )
            occupied_y = (
                rows * body["y"]
                + (rows - 1) * _LAYOUT_CLEARANCE_MM
            )
            base_box["x"] = max(
                base_box["x"],
                _ceil_tenth(occupied_x / 0.969),
            )
            base_box["y"] = max(
                base_box["y"],
                _ceil_tenth(occupied_y / 0.969),
            )
        occupied_volume = group_count * body["x"] * body["y"] * body["z"]
        base_density = occupied_volume / _volume(base_box)
        target_density = density_pct / 100.0
        if base_density + 1e-12 < target_density:
            return None
        xy_expansion = sqrt(base_density / target_density)
        box = {
            "x": _ceil_tenth(base_box["x"] * xy_expansion),
            "y": _ceil_tenth(base_box["y"] * xy_expansion),
            "z": base_box["z"],
        }
        return {
            "body": body,
            "box": box,
            "minimum_required_body_mm": minimum_required,
            "grid": {
                "columns": columns,
                "rows": rows,
                "stack_count": stacks,
                "layers": layer_count,
                "bottom_margin_mm": bottom_margin,
            },
        }

    low = 0.0
    high = 600.0
    high_candidate = candidate(high)
    if (
        high_candidate is None
        or max(_dimension(high_candidate["box"]).values()) < target_largest
    ):
        raise ProductRobustnessCorpusError("Unable to reach the requested box size.")
    for _ in range(55):
        middle = (low + high) / 2.0
        geometry = candidate(middle)
        if (
            geometry is None
            or max(_dimension(geometry["box"]).values()) < target_largest
        ):
            low = middle
        else:
            high = middle
    result = candidate(high)
    if result is None:
        raise ProductRobustnessCorpusError("Unable to construct target density.")
    actual_class = _classify_box(_dimension(result["box"]))
    if actual_class != size_class:
        raise ProductRobustnessCorpusError(
            f"Requested {size_class} box reconstructs as {actual_class}."
        )
    return result


def _constructive_metrics(
    axes: Mapping[str, object],
    geometry: Mapping[str, object],
    *,
    flat_count: int,
) -> dict[str, object]:
    body = _dimension(geometry["body"])
    box = _dimension(geometry["box"])
    grid = _mapping(geometry["grid"])
    group_count = int(axes["container_count"])
    occupied = group_count * _volume(body)
    density = 100.0 * occupied / _volume(box)
    occupied_span = {
        "x": (
            int(grid["columns"]) * body["x"]
            + (int(grid["columns"]) - 1) * _LAYOUT_CLEARANCE_MM
        ),
        "y": (
            int(grid["rows"]) * body["y"]
            + (int(grid["rows"]) - 1) * _LAYOUT_CLEARANCE_MM
        ),
        "z": (
            int(grid["layers"]) * body["z"]
            + (int(grid["layers"]) - 1) * _Z_CLEARANCE_MM
        ),
    }
    box_slack_by_axis = {
        axis: round(
            100.0 * max(0.0, box[axis] - occupied_span[axis]) / box[axis],
            4,
        )
        for axis in ("x", "y", "z")
    }
    required = _dimension(geometry["minimum_required_body_mm"])
    margin_by_axis = {
        axis: round(
            100.0 * max(0.0, body[axis] - required[axis]) / body[axis],
            4,
        )
        for axis in ("x", "y", "z")
    }
    return {
        "useful_density_pct": round(density, 4),
        "minimum_axis_margin_pct": min(margin_by_axis.values()),
        "constructive_axis_margin_pct": margin_by_axis,
        "box_slack_pct": box_slack_by_axis,
        "occupied_container_volume_mm3": round(occupied, 4),
        "box_volume_mm3": round(_volume(box), 4),
        "free_region_lower_bound": 1,
        "fragmentation_class": (
            "reserved-top"
            if flat_count
            else "layered"
            if int(axes["layer_count"]) > 1
            else "single-layer"
        ),
        "support_edge_count": group_count - int(grid["stack_count"]),
        "maximum_aspect_ratio": round(
            max(body.values()) / min(body.values()),
            4,
        ),
        "near_equal_xy_delta_mm": round(abs(body["x"] - body["y"]), 4),
    }


@lru_cache(maxsize=None)
def _minimum_body_size(
    contents_per_container: int,
    quantity_per_record: int,
    first_quantity_extra: int,
) -> dict[str, float]:
    project = blank_project_v1()
    project["project_name"] = "P64-L09W sizing oracle"
    project["box"] = {
        "inner_dimensions_mm": {"x": 2_000.0, "y": 2_000.0, "z": 2_000.0},
        "usable_height_mm": 2_000.0,
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [_group_payload(0, target=None)]
    project["contents"] = [
        _content_payload(
            0,
            content_index,
            quantity=(
                quantity_per_record + first_quantity_extra
                if content_index == 0
                else quantity_per_record
            ),
        )
        for content_index in range(contents_per_container)
    ]
    report = derive_expandable_envelope_contract(project)
    containers = _mappings(report.get("containers"))
    if (
        _mapping(report.get("summary")).get("status") != "ready_for_p56"
        or len(containers) != 1
    ):
        raise ProductRobustnessCorpusError(
            "Product sizing oracle cannot derive a minimum container."
        )
    return _dimension(containers[0]["minimum_outer_envelope_mm"])


def _materialize_project(
    recipe: Mapping[str, object],
    *,
    phase: str,
) -> dict[str, object]:
    axes = _mapping(recipe["axes"])
    group_count = int(axes["container_count"])
    contents_per_group = int(axes["contents_per_container"])
    quantity = int(recipe["quantity_per_record"])
    target = _dimension(recipe["body_size_mm"])
    box = _dimension(recipe["box_inner_dimensions_mm"])
    execution = str(axes["execution"])
    project = blank_project_v1()
    project["project_name"] = str(recipe["case_id"])
    project["box"] = {
        "inner_dimensions_mm": deepcopy(box),
        "usable_height_mm": box["z"],
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        _group_payload(group_index, target=target)
        for group_index in range(group_count)
    ]
    project["contents"] = []
    for group_index in range(group_count):
        for content_index in range(contents_per_group):
            current_quantity = quantity
            if group_index == 0 and content_index == 0:
                if execution == "add" and phase == "after":
                    current_quantity += 1
                elif execution == "remove" and phase == "before":
                    current_quantity += 1
            content = _content_payload(
                group_index,
                content_index,
                quantity=current_quantity,
            )
            if (
                execution == "local_parameter"
                and phase == "before"
                and group_index == 0
                and content_index == 0
            ):
                dimensions = _dimension(content["dimensions_mm"])
                dimensions["x"] = _nearest_tenth(max(0.1, dimensions["x"] - 0.1))
                content["dimensions_mm"] = dimensions
            project["contents"].append(content)
    project["flat_items"] = _flat_items(recipe)
    if execution == "global_parameter" and phase == "before":
        project["layout"]["layout_clearance_mm"] = 0.5
    return normalize_project_draft(project).project


def _materialize_edit_sequence(
    recipe: Mapping[str, object],
) -> dict[str, object]:
    axes = _mapping(recipe["axes"])
    execution = str(axes["execution"])
    operation: dict[str, object] | None
    if execution == "cold":
        operation = None
    elif execution == "add":
        operation = {
            "op": "increment_quantity",
            "content_id": "content-000-000",
            "delta": 1,
        }
    elif execution == "remove":
        operation = {
            "op": "decrement_quantity",
            "content_id": "content-000-000",
            "delta": -1,
        }
    elif execution == "local_parameter":
        operation = {
            "op": "replace_content_dimension",
            "content_id": "content-000-000",
            "axis": "x",
            "delta_mm": 0.1,
        }
    else:
        operation = {
            "op": "replace_global_layout_clearance",
            "before_mm": 0.5,
            "after_mm": _LAYOUT_CLEARANCE_MM,
        }
    return {
        "schema_version": EDIT_SEQUENCE_SCHEMA,
        "case_id": recipe["case_id"],
        "execution": execution,
        "operations": [] if operation is None else [operation],
    }


def _group_payload(
    group_index: int,
    *,
    target: Mapping[str, object] | None,
) -> dict[str, object]:
    if target is None:
        modes = {"x": "auto", "y": "auto", "z": "auto"}
        targets = {"x": None, "y": None, "z": None}
    else:
        modes = {"x": "fixed", "y": "fixed", "z": "fixed"}
        targets = _dimension(target)
    return {
        "id": f"group-{group_index:03d}",
        "name": f"Bac {group_index:03d}",
        "wall_thickness_mm": None,
        "floor_thickness_mm": None,
        "dimension_modes": modes,
        "target_outer_dimensions_mm": targets,
    }


def _content_payload(
    group_index: int,
    content_index: int,
    *,
    quantity: int,
) -> dict[str, object]:
    return {
        "id": f"content-{group_index:03d}-{content_index:03d}",
        "name": f"Contenu {group_index:03d}-{content_index:03d}",
        "shape_kind": "custom",
        "dimensions_mm": {
            "x": _nearest_tenth(0.8 + 0.2 * (content_index % 7)),
            "y": _nearest_tenth(0.9 + 0.2 * ((content_index * 3 + 1) % 7)),
            "z": _nearest_tenth(0.7 + 0.1 * ((content_index * 5 + 2) % 7)),
        },
        "quantity": quantity,
        "container_group_id": f"group-{group_index:03d}",
        "content_clearance_mm": None,
        "measurement_confidence": "exact",
    }


def _flat_items(recipe: Mapping[str, object]) -> list[dict[str, object]]:
    axes = _mapping(recipe["axes"])
    body = _dimension(recipe["body_size_mm"])
    thicknesses = list(recipe["flat_thicknesses_mm"])
    result = []
    explicit = recipe.get("flat_pose_mode") == "explicit-stacked"
    for index in range(int(axes["flat_count"])):
        width_ratio = 0.24 if explicit else 0.22 + 0.02 * (index % 4)
        depth_ratio = 0.225 if explicit else 0.20 + 0.025 * ((index * 3) % 4)
        flat_x = _nearest_tenth(max(1.0, body["x"] * width_ratio))
        flat_y = _nearest_tenth(max(1.0, body["y"] * depth_ratio))
        result.append(
            {
                "id": f"flat-{index:03d}",
                "name": f"Élément plat {index:03d}",
                "kind": "board" if index % 2 == 0 else "rulebook",
                "dimensions_mm": {
                    "x": flat_x,
                    "y": flat_y,
                    "z": float(thicknesses[index]),
                },
                "quantity": 1,
                "stack_order": index,
                "origin_mm": (
                    {
                        "x": _nearest_tenth(
                            _BOX_XY_CLEARANCE_MM
                            + (body["x"] - flat_x) / 2.0
                        ),
                        "y": _nearest_tenth(
                            _BOX_XY_CLEARANCE_MM
                            + (body["y"] - flat_y) / 2.0
                        ),
                    }
                    if explicit
                    else None
                ),
                "rotation_deg_z": 0 if explicit else None,
            }
        )
    return result


def _quantity_per_record(
    group_count: int,
    contents_per_group: int,
    *,
    seed: int,
    execution: str,
) -> int:
    capacity = 4_096 // (group_count * contents_per_group)
    if execution == "add":
        capacity = max(1, capacity - 1)
    choices = [value for value in (1, 2, 4, 8) if value <= capacity]
    return choices[seed % len(choices)]


def _free_3d_placements(
    problem: Free3DPreparedProblem,
    witness: Mapping[str, object],
) -> tuple[Free3DPlacement, ...]:
    geometry_by_group = {
        str(item["container_group_id"]): item
        for item in _mappings(witness.get("placements"))
    }
    participant_by_group = {
        str(item["container_group_id"]): item
        for item in problem.participants
        if "container_group_id" in item
    }
    result: list[Free3DPlacement] = []
    for participant in problem.participants:
        group_id = str(participant.get("container_group_id", ""))
        geometry = geometry_by_group.get(group_id)
        if geometry is None:
            raise ProductRobustnessCorpusError(
                f"Independent witness misses {group_id}."
            )
        support_ids = tuple(
            str(participant_by_group[str(value)]["id"])
            for value in geometry["support_group_ids"]
        )
        size = _dimension_tuple(geometry["world_size_mm"])
        result.append(
            Free3DPlacement(
                participant_id=str(participant["id"]),
                role=str(participant["role"]),
                name=str(participant["name"]),
                origin_mm=_dimension_tuple(geometry["origin_mm"]),
                world_size_mm=size,
                local_size_mm=size,
                rotation_deg_z=int(geometry["rotation_deg_z"]),
                supporting_ids=support_ids,
                support_coverage_ratio=float(
                    geometry["support_coverage_ratio"]
                ),
            )
        )
    if len(result) != len(geometry_by_group):
        raise ProductRobustnessCorpusError(
            "Independent witness participant count mismatch."
        )
    return tuple(result)


def _certify_constructed_placements(
    problem: Free3DPreparedProblem,
    placements: tuple[Free3DPlacement, ...],
    *,
    candidate_id: str,
) -> CertifiedFree3DPlan:
    profile = next(
        value
        for value in portfolio_effort_profiles()
        if value.profile_id == "normal"
    )
    certified, rejections = certify_free_3d_plan(
        problem,
        strategy=SolverStrategy(
            profile.beam_budget.family_id,
            "p64-l09w-independent-witness-v1",
        ),
        budget=profile.beam_budget,
        candidate_id=candidate_id,
        placements=placements,
        search_telemetry={
            "independent_witness": True,
            "solver_invocation_count": 0,
            "witness_disclosed_to_evaluated_solver": False,
        },
    )
    if certified is None:
        raise ProductRobustnessCorpusError(
            "Independent witness failed current certification: "
            + ",".join(rejections)
        )
    if not certified.certificate.certified:
        raise ProductRobustnessCorpusError(
            "Independent witness returned a non-certified plan."
        )
    return certified


def _validation_certificate_digest(certified: CertifiedFree3DPlan) -> str:
    return canonical_digest(
        {
            "schema_version": certified.certificate.schema_version,
            "candidate_digest": certified.certificate.candidate_digest,
            "certified": certified.certificate.certified,
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "rejection_code": check.rejection_code,
                }
                for check in certified.certificate.checks
            ],
        }
    )


def _require_prepared_problem(
    status: str,
    problem: Free3DPreparedProblem | None,
    rejection_codes: Sequence[str],
    *,
    context: str,
) -> Free3DPreparedProblem:
    if status != "ready" or problem is None:
        raise ProductRobustnessCorpusError(
            f"Independent {context} preparation failed: "
            + ",".join(rejection_codes)
        )
    return problem


def _factor_grid(
    stack_count: int,
    body_x: float,
    body_y: float,
) -> tuple[int, int]:
    candidates = [
        (columns, stack_count // columns)
        for columns in range(1, stack_count + 1)
        if stack_count % columns == 0
    ]
    return min(
        candidates,
        key=lambda value: (
            abs(value[0] * body_x - value[1] * body_y),
            value[0] * body_x + value[1] * body_y,
            value[0],
        ),
    )


def _classify_box(box: Mapping[str, object]) -> str:
    largest = max(_dimension(box).values())
    if largest <= 150.0:
        return "small"
    if largest <= 300.0:
        return "medium"
    return "large"


def _classify_stratum(
    axes: Mapping[str, object],
    metrics: Mapping[str, object],
) -> str:
    common = (
        int(axes["target_density_pct"]) in {30, 65, 85}
        and int(axes["container_count"]) <= 18
        and int(axes["contents_per_container"]) <= 16
        and int(axes["flat_count"]) <= 2
        and int(axes["layer_count"]) <= 3
        and float(metrics["minimum_axis_margin_pct"]) >= 3.0
    )
    return "common" if common else "stress"


def _seed_for(namespace: str, ordinal: int) -> int:
    return int(
        canonical_digest(
            {
                "generator_version": GENERATOR_VERSION,
                "namespace": namespace,
                "ordinal": ordinal,
            }
        )[:16],
        16,
    )


def _require_nonce(value: str) -> None:
    if (
        len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ProductRobustnessCorpusError(
            "Holdout nonce must contain 256 lowercase hexadecimal bits."
        )


def _dimension(value: object) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise ProductRobustnessCorpusError("Dimension payload is missing.")
    try:
        return {axis: float(value[axis]) for axis in ("x", "y", "z")}
    except (KeyError, TypeError, ValueError) as error:
        raise ProductRobustnessCorpusError("Dimension payload is invalid.") from error


def _dimension_tuple(value: object) -> tuple[float, float, float]:
    dimension = _dimension(value)
    return dimension["x"], dimension["y"], dimension["z"]


def _mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, Mapping)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _volume(value: Mapping[str, object]) -> float:
    dimension = _dimension(value)
    return dimension["x"] * dimension["y"] * dimension["z"]


def _nearest_tenth(value: float) -> float:
    return round(float(value) + 1e-12, 1)


def _ceil_tenth(value: float) -> float:
    return ceil((float(value) - 1e-12) * 10.0) / 10.0


def validate_positive_case_record(
    value: Mapping[str, object],
    *,
    reconstruct: bool = True,
    recertify: bool = False,
) -> dict[str, object]:
    """Vérifier les engagements d'un cas, avec recertification optionnelle."""

    record = deepcopy(dict(value))
    supplied = record.pop("case_digest", None)
    if (
        record.get("schema_version") != POSITIVE_CASE_SCHEMA
        or supplied != canonical_digest(record)
    ):
        raise ProductRobustnessCorpusError(
            "Positive case schema or digest is invalid."
        )
    recipe = record.get("recipe")
    if not isinstance(recipe, Mapping):
        raise ProductRobustnessCorpusError("Positive case recipe is missing.")
    accepted_recipe = validate_positive_recipe(recipe)
    if record.get("recipe_digest") != canonical_digest(accepted_recipe):
        raise ProductRobustnessCorpusError("Positive recipe commitment mismatch.")
    if record.get("seed_digest") != canonical_digest(
        {"seed": accepted_recipe["seed"]}
    ):
        raise ProductRobustnessCorpusError("Positive seed commitment mismatch.")
    for key in ("case_id", "split", "stratum", "axes"):
        if record.get(key) != accepted_recipe.get(key):
            raise ProductRobustnessCorpusError(
                f"Positive case field {key} differs from its recipe."
            )
    if record.get("expected") != "feasible":
        raise ProductRobustnessCorpusError("Positive case expectation is invalid.")
    if record.get("solver_invocation_count") != 0:
        raise ProductRobustnessCorpusError(
            "Corpus construction must not invoke the evaluated solver."
        )
    oracle = _validate_oracle_receipt(record.get("oracle_receipt"))
    if reconstruct:
        bundle = materialize_positive_case_bundle(accepted_recipe)
        expected_commitments = {
            "project_digest": canonical_digest(bundle["after_project"]),
            "before_project_digest": (
                None
                if bundle["before_project"] is None
                else canonical_digest(bundle["before_project"])
            ),
            "edit_sequence_digest": canonical_digest(bundle["edit_sequence"]),
            "witness_digest": canonical_digest(bundle["witness"]),
        }
        for key, expected in expected_commitments.items():
            if record.get(key) != expected:
                raise ProductRobustnessCorpusError(
                    f"Positive {key} commitment mismatch."
                )
        if recertify:
            current = certify_independent_witness(
                bundle["after_project"],
                bundle["witness"],
                case_id=str(record["case_id"]),
            )
            if current != oracle:
                raise ProductRobustnessCorpusError(
                    "Positive oracle receipt no longer recertifies identically."
                )
    elif recertify:
        raise ProductRobustnessCorpusError(
            "Recertification requires project reconstruction."
        )
    record["case_digest"] = supplied
    return record


def validate_positive_distribution(
    records: Sequence[Mapping[str, object]],
    *,
    expected_count: int,
) -> dict[str, object]:
    """Appliquer les minima gelés du plan pairwise."""

    accepted = [
        validate_positive_case_record(record, reconstruct=False)
        for record in records
    ]
    if len(accepted) != expected_count:
        raise ProductRobustnessCorpusError(
            f"Positive distribution needs {expected_count} cases."
        )
    counts = {
        "stratum": _axis_counts(accepted, "stratum"),
        "contents_per_container": _axis_counts(
            accepted, "contents_per_container"
        ),
        "container_count": _axis_counts(accepted, "container_count"),
        "target_density_pct": _axis_counts(accepted, "target_density_pct"),
        "flat_count": _axis_counts(accepted, "flat_count"),
        "layer_bucket": _axis_counts(accepted, "layer_bucket"),
        "box_size": _axis_counts(accepted, "box_size"),
        "execution": _axis_counts(accepted, "execution"),
    }
    expected_strata = {"common": 240, "stress": 160}
    if counts["stratum"] != expected_strata:
        raise ProductRobustnessCorpusError(
            f"Positive strata differ from {expected_strata}: {counts['stratum']}."
        )
    minima: tuple[tuple[str, Sequence[object], int], ...] = (
        ("contents_per_container", CONTENTS_PER_CONTAINER_VALUES, 20),
        ("container_count", CONTAINER_COUNT_VALUES, 20),
        ("target_density_pct", DENSITY_VALUES, 60),
        ("flat_count", FLAT_COUNT_VALUES, 20),
        ("layer_bucket", ("1", "2", "3", "4+"), 40),
        ("box_size", BOX_SIZE_VALUES, 60),
        ("execution", EXECUTION_VALUES, 40),
    )
    for axis, required_values, minimum in minima:
        for axis_value in required_values:
            observed = int(counts[axis].get(str(axis_value), 0))
            if observed < minimum:
                raise ProductRobustnessCorpusError(
                    f"Pairwise minimum missing for {axis}={axis_value}: "
                    f"{observed} < {minimum}."
                )
    digests = {
        key: [str(record[key]) for record in accepted]
        for key in (
            "recipe_digest",
            "project_digest",
            "witness_digest",
            "edit_sequence_digest",
        )
    }
    for key, values in digests.items():
        if len(values) != len(set(values)):
            raise ProductRobustnessCorpusError(
                f"Positive distribution duplicates {key}."
            )
    return {
        "case_count": len(accepted),
        "counts": counts,
        "minimums_satisfied": True,
        "solver_invocation_count": 0,
    }


def build_negative_control_records() -> list[dict[str, object]]:
    """Construire 40 impossibilités à borne formelle, hors taux positif."""

    records = [
        _build_negative_control_record(ordinal)
        for ordinal in range(NEGATIVE_CONTROL_COUNT)
    ]
    families = _axis_counts(records, "proof_family")
    if families != {
        "axis": 10,
        "reservation": 10,
        "stacking_z": 10,
        "volume": 10,
    }:
        raise ProductRobustnessCorpusError(
            f"Negative proof families are incomplete: {families}."
        )
    return records


def materialize_negative_project(
    recipe: Mapping[str, object],
) -> dict[str, object]:
    family = str(recipe.get("proof_family"))
    ordinal = int(recipe.get("ordinal", -1))
    if family not in {"volume", "axis", "stacking_z", "reservation"}:
        raise ProductRobustnessCorpusError("Negative proof family is invalid.")
    if ordinal < 0 or ordinal >= NEGATIVE_CONTROL_COUNT:
        raise ProductRobustnessCorpusError("Negative ordinal is invalid.")
    variation = (ordinal % 10) * 0.1
    project = blank_project_v1()
    project["project_name"] = f"p64-l09w-negative-{family}-{ordinal:02d}"
    if family == "volume":
        group_count = 2
        body = {"x": 20.0 + variation, "y": 20.0, "z": 20.0}
        box = {"x": 21.2 + variation, "y": 21.2, "z": 20.0}
    elif family == "axis":
        group_count = 1
        body = {"x": 30.0 + variation, "y": 10.0, "z": 10.0}
        box = {"x": 20.0 + variation, "y": 30.0, "z": 20.0}
    elif family == "stacking_z":
        group_count = 2
        body = {"x": 20.0, "y": 20.0, "z": 15.0 + variation}
        box = {"x": 21.2, "y": 21.2, "z": 25.0 + variation}
    else:
        group_count = 1
        body = {"x": 20.0, "y": 20.0, "z": 20.0}
        box = {"x": 21.2, "y": 21.2, "z": 20.0}
    project["box"] = {
        "inner_dimensions_mm": box,
        "usable_height_mm": box["z"],
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        _group_payload(index, target=body)
        for index in range(group_count)
    ]
    project["contents"] = [
        _content_payload(index, 0, quantity=1)
        for index in range(group_count)
    ]
    if family == "reservation":
        project["flat_items"] = [
            {
                "id": "flat-oversized",
                "name": "Plateau hors borne",
                "kind": "board",
                "dimensions_mm": {
                    "x": 30.0 + variation,
                    "y": 10.0,
                    "z": 1.0,
                },
                "quantity": 1,
                "stack_order": 0,
                "origin_mm": None,
                "rotation_deg_z": None,
            }
        ]
    return normalize_project_draft(project).project


def validate_negative_case_record(
    value: Mapping[str, object],
    *,
    reconstruct: bool = True,
) -> dict[str, object]:
    record = deepcopy(dict(value))
    supplied = record.pop("case_digest", None)
    if (
        record.get("schema_version") != NEGATIVE_CASE_SCHEMA
        or supplied != canonical_digest(record)
    ):
        raise ProductRobustnessCorpusError(
            "Negative case schema or digest is invalid."
        )
    if (
        record.get("split") != "negative-control"
        or record.get("expected") != "proven_impossible"
        or record.get("solver_invocation_count") != 0
    ):
        raise ProductRobustnessCorpusError("Negative control metadata is invalid.")
    recipe = record.get("recipe")
    proof = record.get("proof")
    if not isinstance(recipe, Mapping) or not isinstance(proof, Mapping):
        raise ProductRobustnessCorpusError(
            "Negative recipe or proof is missing."
        )
    family = str(recipe.get("proof_family"))
    if record.get("proof_family") != family:
        raise ProductRobustnessCorpusError("Negative proof family mismatch.")
    if proof.get("schema_version") != NEGATIVE_PROOF_SCHEMA:
        raise ProductRobustnessCorpusError("Negative proof schema is invalid.")
    if record.get("recipe_digest") != canonical_digest(dict(recipe)):
        raise ProductRobustnessCorpusError("Negative recipe digest mismatch.")
    if record.get("proof_digest") != canonical_digest(dict(proof)):
        raise ProductRobustnessCorpusError("Negative proof digest mismatch.")
    if reconstruct:
        project = materialize_negative_project(recipe)
        expected_proof = _formal_negative_proof(project, family)
        if record.get("project_digest") != canonical_digest(project):
            raise ProductRobustnessCorpusError("Negative project digest mismatch.")
        if dict(proof) != expected_proof:
            raise ProductRobustnessCorpusError(
                "Negative formal bound no longer reconstructs."
            )
    record["case_digest"] = supplied
    return record


def build_public_manifest(
    open_positive_records: Sequence[Mapping[str, object]],
    negative_records: Sequence[Mapping[str, object]],
    sealed_holdout: Mapping[str, object],
) -> dict[str, object]:
    """Publier les cas ouverts et le seul reçu agrégé du holdout."""

    positives = [
        validate_positive_case_record(record, reconstruct=False)
        for record in open_positive_records
    ]
    negatives = [
        validate_negative_case_record(record, reconstruct=False)
        for record in negative_records
    ]
    open_coverage = validate_positive_distribution(
        positives,
        expected_count=OPEN_POSITIVE_COUNT,
    )
    sealed = validate_sealed_holdout(sealed_holdout)
    if len(negatives) != NEGATIVE_CONTROL_COUNT:
        raise ProductRobustnessCorpusError(
            f"Manifest needs {NEGATIVE_CONTROL_COUNT} negative controls."
        )
    _require_cross_split_disjointness(positives, sealed["case_records"])
    holdout_coverage = _mapping(sealed["coverage"])
    receipt = {
        "schema_version": HOLDOUT_RECEIPT_SCHEMA,
        "sealed_holdout_digest": sealed["sealed_holdout_digest"],
        "positive_case_count": HOLDOUT_POSITIVE_COUNT,
        "stratum_counts": deepcopy(
            _mapping(holdout_coverage["counts"])["stratum"]
        ),
        "pairwise_minimums_satisfied": bool(
            holdout_coverage["minimums_satisfied"]
        ),
        "opened": False,
        "opening_count": 0,
        "solver_invocation_count": 0,
    }
    soak_plan = {
        "schema_version": SOAK_PLAN_SCHEMA,
        "generator_version": GENERATOR_VERSION,
        "recipe_count": SOAK_RECIPE_COUNT,
        "namespace_digest": canonical_digest(
            {"namespace": "p64-l09w-soak-v1"}
        ),
        "deterministic": True,
        "resume_key": "soak_ordinal",
        "oracle_required_before_measurement": True,
        "solver_invocation_count": 0,
    }
    payload: dict[str, object] = {
        "schema_version": MANIFEST_SCHEMA,
        "generator_version": GENERATOR_VERSION,
        "regression_source": _regression_source(),
        "open_positive_case_records": positives,
        "negative_control_records": negatives,
        "open_coverage": open_coverage,
        "sealed_holdout_receipt": receipt,
        "soak_plan": soak_plan,
        "invariants": {
            "project_schema": "bgig.project.v1",
            "positive_truth": "constructed_then_currently_recertified",
            "negative_truth": "formal_bound",
            "witness_disclosed_to_evaluated_solver": False,
            "strictly_subtractive_top_insets": True,
            "product_grid_mm": 0.1,
            "geometry_epsilon_mm": 0.0001,
            "holdout_recipes_embedded": False,
            "holdout_opened": False,
            "legacy_holdout_reused": False,
            "solver_invocation_count": 0,
        },
    }
    payload["manifest_digest"] = canonical_digest(payload)
    return validate_public_manifest(payload)


def validate_public_manifest(
    value: Mapping[str, object],
) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop("manifest_digest", None)
    if (
        payload.get("schema_version") != MANIFEST_SCHEMA
        or payload.get("generator_version") != GENERATOR_VERSION
        or supplied != canonical_digest(payload)
    ):
        raise ProductRobustnessCorpusError(
            "Public corpus manifest schema or digest is invalid."
        )
    positives_raw = payload.get("open_positive_case_records")
    negatives_raw = payload.get("negative_control_records")
    if payload.get("regression_source") != _regression_source():
        raise ProductRobustnessCorpusError(
            "Public regression source commitment is invalid."
        )
    if not isinstance(positives_raw, list) or not isinstance(negatives_raw, list):
        raise ProductRobustnessCorpusError("Public corpus records are missing.")
    positives = [
        validate_positive_case_record(record, reconstruct=False)
        for record in positives_raw
    ]
    negatives = [
        validate_negative_case_record(record, reconstruct=False)
        for record in negatives_raw
    ]
    coverage = validate_positive_distribution(
        positives,
        expected_count=OPEN_POSITIVE_COUNT,
    )
    if payload.get("open_coverage") != coverage:
        raise ProductRobustnessCorpusError("Open coverage summary mismatch.")
    if len(negatives) != NEGATIVE_CONTROL_COUNT:
        raise ProductRobustnessCorpusError("Negative control count mismatch.")
    receipt = payload.get("sealed_holdout_receipt")
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema_version") != HOLDOUT_RECEIPT_SCHEMA
        or not _is_digest(receipt.get("sealed_holdout_digest"))
        or receipt.get("positive_case_count") != HOLDOUT_POSITIVE_COUNT
        or receipt.get("stratum_counts") != {"common": 240, "stress": 160}
        or receipt.get("pairwise_minimums_satisfied") is not True
        or receipt.get("opened") is not False
        or receipt.get("opening_count") != 0
        or receipt.get("solver_invocation_count") != 0
    ):
        raise ProductRobustnessCorpusError(
            "Public sealed-holdout receipt is invalid."
        )
    if "case_records" in receipt or "campaign_nonce" in receipt:
        raise ProductRobustnessCorpusError(
            "Public manifest leaks private holdout recipes."
        )
    soak = payload.get("soak_plan")
    if (
        not isinstance(soak, dict)
        or soak.get("schema_version") != SOAK_PLAN_SCHEMA
        or soak.get("recipe_count") != SOAK_RECIPE_COUNT
        or soak.get("deterministic") is not True
        or soak.get("solver_invocation_count") != 0
    ):
        raise ProductRobustnessCorpusError("Soak plan is invalid.")
    payload["manifest_digest"] = supplied
    return payload


def validate_sealed_holdout(
    value: Mapping[str, object],
) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop("sealed_holdout_digest", None)
    if (
        payload.get("schema_version") != SEALED_HOLDOUT_SCHEMA
        or payload.get("generator_version") != GENERATOR_VERSION
        or supplied != canonical_digest(payload)
    ):
        raise ProductRobustnessCorpusError(
            "Sealed holdout schema or digest is invalid."
        )
    _require_nonce(str(payload.get("campaign_nonce", "")))
    records_raw = payload.get("case_records")
    if not isinstance(records_raw, list):
        raise ProductRobustnessCorpusError("Sealed holdout records are missing.")
    records = [
        validate_positive_case_record(record, reconstruct=False)
        for record in records_raw
    ]
    if any(record["split"] != "holdout" for record in records):
        raise ProductRobustnessCorpusError(
            "Sealed holdout contains a non-holdout case."
        )
    coverage = validate_positive_distribution(
        records,
        expected_count=HOLDOUT_POSITIVE_COUNT,
    )
    if payload.get("coverage") != coverage:
        raise ProductRobustnessCorpusError("Sealed holdout coverage mismatch.")
    if (
        payload.get("opened") is not False
        or payload.get("opening_count") != 0
        or payload.get("solver_invocation_count") != 0
    ):
        raise ProductRobustnessCorpusError(
            "New holdout must remain closed and unused."
        )
    payload["case_records"] = records
    payload["sealed_holdout_digest"] = supplied
    return payload


def verify_sealed_holdout(
    manifest: Mapping[str, object],
    sealed_holdout: Mapping[str, object],
) -> dict[str, object]:
    accepted_manifest = validate_public_manifest(manifest)
    accepted_holdout = validate_sealed_holdout(sealed_holdout)
    receipt = accepted_manifest["sealed_holdout_receipt"]
    if (
        receipt["sealed_holdout_digest"]
        != accepted_holdout["sealed_holdout_digest"]
    ):
        raise ProductRobustnessCorpusError(
            "Private holdout does not match its public receipt."
        )
    _require_cross_split_disjointness(
        accepted_manifest["open_positive_case_records"],
        accepted_holdout["case_records"],
    )
    return {
        "status": "verified_closed",
        "positive_case_count": HOLDOUT_POSITIVE_COUNT,
        "sealed_holdout_digest": accepted_holdout["sealed_holdout_digest"],
        "opening_count": 0,
        "solver_invocation_count": 0,
    }


def build_soak_recipe(soak_ordinal: int) -> dict[str, object]:
    """Reconstruire une recette soak stable et reprenable par ordinal."""

    if soak_ordinal < 0 or soak_ordinal >= SOAK_RECIPE_COUNT:
        raise ProductRobustnessCorpusError("Soak ordinal is out of range.")
    cycle, base_ordinal = divmod(soak_ordinal, OPEN_POSITIVE_COUNT)
    recipe = _design_positive_recipe(
        base_ordinal,
        namespace=f"soak-p64-l09w-v1-cycle-{cycle}",
        phase=cycle + 1,
    )
    recipe["split"] = "soak"
    recipe["case_id"] = (
        f"p64-l09w-soak-{soak_ordinal:04d}-"
        f"{canonical_digest({'soak_ordinal': soak_ordinal})[:10]}"
    )
    recipe["ordinal"] = soak_ordinal
    recipe["soak_cycle"] = cycle
    return validate_positive_recipe(recipe)


def _build_negative_control_record(ordinal: int) -> dict[str, object]:
    family = ("volume", "axis", "stacking_z", "reservation")[ordinal // 10]
    recipe = {
        "generator_version": GENERATOR_VERSION,
        "case_id": f"p64-l09w-negative-{family}-{ordinal:02d}",
        "ordinal": ordinal,
        "proof_family": family,
    }
    project = materialize_negative_project(recipe)
    proof = _formal_negative_proof(project, family)
    payload: dict[str, object] = {
        "schema_version": NEGATIVE_CASE_SCHEMA,
        "case_id": recipe["case_id"],
        "split": "negative-control",
        "expected": "proven_impossible",
        "proof_family": family,
        "recipe": recipe,
        "recipe_digest": canonical_digest(recipe),
        "project_digest": canonical_digest(project),
        "proof": proof,
        "proof_digest": canonical_digest(proof),
        "solver_invocation_count": 0,
    }
    payload["case_digest"] = canonical_digest(payload)
    return validate_negative_case_record(payload)


def _regression_source() -> dict[str, object]:
    return {
        "split": "regression",
        "kind": "p64-l09w-a-current-reconstructible",
        "artifact": REGRESSION_BASELINE_ARTIFACT,
        "schema_version": REGRESSION_BASELINE_SCHEMA,
        "baseline_report_digest": REGRESSION_BASELINE_REPORT_DIGEST,
        "case_records_embedded": False,
        "legacy_holdouts_consumed": True,
    }


def _formal_negative_proof(
    project: Mapping[str, object],
    family: str,
) -> dict[str, object]:
    box = _dimension(_mapping(project["box"])["inner_dimensions_mm"])
    groups = _mappings(project["container_groups"])
    targets = [
        _dimension(group["target_outer_dimensions_mm"])
        for group in groups
    ]
    if family == "volume":
        required = sum(_volume(value) for value in targets)
        available = _volume(box)
        inequality = required > available + _GRID_EPSILON_MM
        facts = {
            "required_container_volume_mm3": round(required, 4),
            "available_box_volume_mm3": round(available, 4),
        }
    elif family == "axis":
        required = targets[0]["x"] + 2.0 * _BOX_XY_CLEARANCE_MM
        available = box["x"]
        inequality = required > available + _GRID_EPSILON_MM
        facts = {
            "required_x_with_clearance_mm": round(required, 4),
            "available_x_mm": round(available, 4),
        }
    elif family == "stacking_z":
        required = (
            sum(value["z"] for value in targets)
            + (len(targets) - 1) * _Z_CLEARANCE_MM
        )
        available = box["z"]
        one_per_xy_layer = all(
            2.0 * value["x"] + _LAYOUT_CLEARANCE_MM
            + 2.0 * _BOX_XY_CLEARANCE_MM
            > box["x"]
            and 2.0 * value["y"] + _LAYOUT_CLEARANCE_MM
            + 2.0 * _BOX_XY_CLEARANCE_MM
            > box["y"]
            for value in targets
        )
        inequality = one_per_xy_layer and required > available + _GRID_EPSILON_MM
        facts = {
            "maximum_containers_per_xy_layer": 1,
            "required_stack_z_mm": round(required, 4),
            "available_z_mm": round(available, 4),
        }
    else:
        flat = _dimension(
            _mappings(project.get("flat_items"))[0]["dimensions_mm"]
        )
        required = flat["x"] + 2.0 * _LAYOUT_CLEARANCE_MM
        available = box["x"]
        inequality = required > available + _GRID_EPSILON_MM
        facts = {
            "required_reserved_x_mm": round(required, 4),
            "available_x_mm": round(available, 4),
        }
    if not inequality:
        raise ProductRobustnessCorpusError(
            f"Formal negative bound {family} is not strict."
        )
    return {
        "schema_version": NEGATIVE_PROOF_SCHEMA,
        "kind": family,
        "strict_inequality": True,
        "facts": facts,
        "solver_invocation_count": 0,
    }


def _validate_oracle_receipt(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ProductRobustnessCorpusError("Positive oracle receipt is missing.")
    receipt = deepcopy(dict(value))
    supplied = receipt.pop("oracle_digest", None)
    if (
        receipt.get("schema_version") != ORACLE_RECEIPT_SCHEMA
        or receipt.get("certified") is not True
        or receipt.get("solver_invocation_count") != 0
        or not _is_digest(receipt.get("candidate_digest"))
        or not _is_digest(receipt.get("certificate_digest"))
        or not _is_digest(receipt.get("placement_digest"))
        or not _is_digest(receipt.get("top_inset_plan_digest"))
        or supplied != canonical_digest(receipt)
    ):
        raise ProductRobustnessCorpusError("Positive oracle receipt is invalid.")
    scaffold = receipt.get("scaffold_certificate_digest")
    if scaffold is not None and not _is_digest(scaffold):
        raise ProductRobustnessCorpusError(
            "Positive scaffold certificate digest is invalid."
        )
    receipt["oracle_digest"] = supplied
    return receipt


def _require_cross_split_disjointness(
    open_records: Sequence[Mapping[str, object]],
    holdout_records: Sequence[Mapping[str, object]],
) -> None:
    for key in (
        "recipe_digest",
        "project_digest",
        "witness_digest",
        "edit_sequence_digest",
    ):
        open_values = {str(record[key]) for record in open_records}
        holdout_values = {str(record[key]) for record in holdout_records}
        overlap = open_values.intersection(holdout_values)
        if overlap:
            raise ProductRobustnessCorpusError(
                f"Open/holdout split leaks duplicate {key}."
            )


def _axis_counts(
    records: Sequence[Mapping[str, object]],
    axis: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        if axis in {"stratum", "proof_family"}:
            value = record[axis]
        else:
            value = _mapping(record["axes"])[axis]
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
