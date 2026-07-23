"""Corpus T0/T1 déterministe pour la campagne autonome P64-L06.

Le manifest conserve les anciens corpus sans changer leurs digests et décrit les
cas générés par des recettes compactes. Le holdout est fermé par défaut : son
ouverture exige la trace d'un unique candidat sélectionné avant consultation.
"""

from __future__ import annotations

from copy import deepcopy
from math import ceil, isclose, sqrt
from random import Random
from typing import Mapping, Sequence

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft
from board_game_insert_generator.solver_case_corpus import validate_solver_case_corpus


SOLVER_BENCHMARK_MANIFEST_SCHEMA_V1 = "bgig.solver_benchmark_manifest.v1"
SOLVER_BENCHMARK_RECIPE_SCHEMA_V1 = "bgig.solver_benchmark_recipe.v1"
SOLVER_BENCHMARK_HOLDOUT_SELECTION_SCHEMA_V1 = (
    "bgig.solver_benchmark_holdout_selection.v1"
)
SOLVER_BENCHMARK_PRODUCER_ID = "p64_l06_t0_t1_generator"
SOLVER_BENCHMARK_PRODUCER_VERSION = "1"
GENERATED_SPLITS = ("discovery", "tuning", "holdout")
GENERATED_CASES_PER_SPLIT = 64

FAMILY_MANY_ONE = "many_containers_one_content"
FAMILY_FEW_MANY = "few_containers_many_contents"
FAMILY_MANY_MANY = "many_containers_many_contents"
FAMILY_MIXED = "mixed_dense_simple_heterogeneous"
FAMILY_INCREMENTAL_COLD = "incremental_then_cold"
FAMILIES = (
    FAMILY_MANY_ONE,
    FAMILY_FEW_MANY,
    FAMILY_MANY_MANY,
    FAMILY_MIXED,
    FAMILY_INCREMENTAL_COLD,
)

FEASIBLE_BY_CONSTRUCTION = "feasible_by_construction"
PROVEN_IMPOSSIBLE_SMALL_EXACT = "proven_impossible_small_exact"
_ALLOWED_ORACLES = (FEASIBLE_BY_CONSTRUCTION, PROVEN_IMPOSSIBLE_SMALL_EXACT)
_ALLOWED_DENSITIES = ("ample", "dense", "nearly_saturated")
_ALLOWED_CONTENT_PROFILES = ("homogeneous", "heterogeneous", "nearly_equal")
_ALLOWED_ARRANGEMENTS = ("obvious", "multiple_competing")
_ALLOWED_RESERVATIONS = ("absent", "constraining")
_ALLOWED_ROTATION_WITNESSES = ("fixed_zero_witness", "uses_z_rotation")
_ALLOWED_ROTATION_POLICIES = ("permitted", "forbidden_by_benchmark")
_ALLOWED_ORDERINGS = ("natural", "reversed", "volume_ascending", "seeded_shuffle")
_ALLOWED_EXECUTION_MODES = ("cold", "incremental")
_ALLOWED_CHANGE_KINDS = ("none", "internal_modification", "new_container", "full_rebuild")
_SECRET_KEY_FRAGMENTS = ("api_key", "authorization", "password", "secret", "token")
_EPSILON = 0.0001

_SPLIT_SEED_BASE = {"discovery": 640_610_000, "tuning": 640_620_000, "holdout": 640_630_000}
_SPLIT_OFFSET = {"discovery": 0, "tuning": 1, "holdout": 2}
_GROUP_CHOICES = {
    FAMILY_MANY_ONE: (8, 12, 18, 30, 50),
    FAMILY_FEW_MANY: (2, 4),
    FAMILY_MANY_MANY: (8, 12, 18),
    FAMILY_MIXED: (4, 8, 12, 18),
    FAMILY_INCREMENTAL_COLD: (2, 4, 8, 12),
}


class SolverBenchmarkCorpusError(ValueError):
    """Erreur fermée du manifest, d'une recette ou de son oracle."""


def build_solver_benchmark_manifest(
    regression_corpora: Mapping[str, object],
) -> dict[str, object]:
    """Construit le manifest canonique L06 en préservant chaque corpus source."""

    if not isinstance(regression_corpora, Mapping) or not regression_corpora:
        raise SolverBenchmarkCorpusError("At least one regression corpus is required.")
    regression: list[dict[str, object]] = []
    for source_id, raw_corpus in sorted(regression_corpora.items(), key=lambda item: str(item[0])):
        identifier = _identifier(str(source_id), "regression source id")
        corpus = validate_solver_case_corpus(raw_corpus)
        regression.append({"source_id": identifier, "corpus": corpus})

    generated = [
        _build_generated_case_record(split, index)
        for split in GENERATED_SPLITS
        for index in range(GENERATED_CASES_PER_SPLIT)
    ]
    holdout_records = [case for case in generated if case["split"] == "holdout"]
    manifest: dict[str, object] = {
        "schema_version": SOLVER_BENCHMARK_MANIFEST_SCHEMA_V1,
        "producer": {
            "id": SOLVER_BENCHMARK_PRODUCER_ID,
            "version": SOLVER_BENCHMARK_PRODUCER_VERSION,
        },
        "regression_corpora": regression,
        "generated_cases": generated,
        "matrix": {
            "contents_per_container_targets": [1, 2, 4, 8, 16, 32],
            "retained_variant_targets": [1, 2, 4, 8],
            "container_group_targets": [2, 4, 8, 12, 18, 30, 50],
            "layer_targets": [1, 2, 3],
            "content_profiles": list(_ALLOWED_CONTENT_PROFILES),
            "density_targets": list(_ALLOWED_DENSITIES),
            "arrangement_targets": list(_ALLOWED_ARRANGEMENTS),
            "rotation_policy_targets": list(_ALLOWED_ROTATION_POLICIES),
            "families": list(FAMILIES),
        },
        "holdout_policy": {
            "status": "sealed",
            "case_count": len(holdout_records),
            "case_commitment_digest": canonical_digest(holdout_records),
            "single_hypothesis_required": True,
            "post_open_tuning_allowed": False,
            "new_iteration_requires_new_manifest": True,
        },
        "summary": {
            "regression_corpus_count": len(regression),
            "regression_case_count": sum(
                int(item["corpus"]["summary"]["case_count"]) for item in regression
            ),
            "generated_case_count": len(generated),
            "discovery_case_count": GENERATED_CASES_PER_SPLIT,
            "tuning_case_count": GENERATED_CASES_PER_SPLIT,
            "holdout_case_count": GENERATED_CASES_PER_SPLIT,
        },
        "invariants": {
            "historical_corpus_digests_preserved": True,
            "pairwise_matrix_not_cartesian_product": True,
            "t0_t1_only": True,
            "external_dependency_count": 0,
            "solver_modification_count": 0,
            "holdout_closed_by_default": True,
            "rotation_disable_control_exposed_by_project_v1": False,
            "finalization_invocation_count": 0,
            "cad_build_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
            "personal_project_paths_embedded": False,
        },
    }
    _reject_secret_keys(manifest)
    manifest["manifest_digest"] = canonical_digest(manifest)
    return manifest


def build_generated_benchmark_case_records(
    *,
    case_id_prefix: str,
    split_seed_bases: Mapping[str, int],
    split_offsets: Mapping[str, int],
    splits: Sequence[str] = GENERATED_SPLITS,
) -> list[dict[str, object]]:
    """Construit une campagne fraîche avec les recettes T0/T1 certifiées.

    Cette entrée publique permet à une nouvelle campagne de réutiliser le
    générateur sans réutiliser les identifiants ni les graines du holdout L06.
    Un appel peut produire un sous-ensemble explicite de splits afin de garder
    les recettes d'un nouveau holdout hors du manifest ouvert.
    """

    prefix = _identifier(case_id_prefix, "generated case id prefix")
    if isinstance(splits, (str, bytes)):
        raise SolverBenchmarkCorpusError(
            "Generated campaign splits must be a sequence."
        )
    selected_splits = tuple(splits)
    if (
        not selected_splits
        or len(set(selected_splits)) != len(selected_splits)
        or any(split not in GENERATED_SPLITS for split in selected_splits)
    ):
        raise SolverBenchmarkCorpusError(
            "Generated campaign splits must be distinct known splits."
        )
    expected_splits = set(selected_splits)
    if set(split_seed_bases) != expected_splits:
        raise SolverBenchmarkCorpusError(
            "Generated campaign seed bases must cover selected splits exactly."
        )
    if set(split_offsets) != expected_splits:
        raise SolverBenchmarkCorpusError(
            "Generated campaign offsets must cover selected splits exactly."
        )
    bases: dict[str, int] = {}
    offsets: dict[str, int] = {}
    for split in selected_splits:
        seed_base = split_seed_bases[split]
        offset = split_offsets[split]
        if (
            isinstance(seed_base, bool)
            or not isinstance(seed_base, int)
            or seed_base < 0
        ):
            raise SolverBenchmarkCorpusError(
                "Generated campaign seed bases must be non-negative integers."
            )
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise SolverBenchmarkCorpusError(
                "Generated campaign offsets must be non-negative integers."
            )
        bases[split] = seed_base
        offsets[split] = offset
    if len(set(bases.values())) != len(selected_splits):
        raise SolverBenchmarkCorpusError(
            "Generated campaign seed bases must be distinct between splits."
        )
    return [
        _build_generated_case_record(
            split,
            index,
            case_id_prefix=prefix,
            seed_base=bases[split],
            split_offset=offsets[split],
        )
        for split in selected_splits
        for index in range(GENERATED_CASES_PER_SPLIT)
    ]


def validate_solver_benchmark_manifest(manifest: object) -> dict[str, object]:
    """Valide le digest puis reconstruit entièrement le manifest canonique."""

    if not isinstance(manifest, Mapping):
        raise SolverBenchmarkCorpusError("Solver benchmark manifest must be an object.")
    payload = deepcopy(dict(manifest))
    if payload.get("schema_version") != SOLVER_BENCHMARK_MANIFEST_SCHEMA_V1:
        raise SolverBenchmarkCorpusError("Unsupported solver benchmark manifest schema.")
    supplied_digest = payload.pop("manifest_digest", None)
    if not _is_digest(supplied_digest):
        raise SolverBenchmarkCorpusError("Solver benchmark manifest digest is missing.")
    if canonical_digest(payload) != supplied_digest:
        raise SolverBenchmarkCorpusError("Solver benchmark manifest digest mismatch.")
    raw_regression = payload.get("regression_corpora")
    if not isinstance(raw_regression, list) or not raw_regression:
        raise SolverBenchmarkCorpusError("Regression corpora must be a non-empty list.")
    sources: dict[str, object] = {}
    for raw in raw_regression:
        item = _mapping(raw, "manifest.regression_corpora[]")
        source_id = _identifier(str(item.get("source_id", "")), "regression source id")
        if source_id in sources:
            raise SolverBenchmarkCorpusError("Regression source identifiers must be unique.")
        sources[source_id] = item.get("corpus")
    rebuilt = build_solver_benchmark_manifest(sources)
    if rebuilt != dict(manifest):
        raise SolverBenchmarkCorpusError("Solver benchmark manifest is not canonical.")
    return deepcopy(rebuilt)


def build_holdout_selection(
    hypothesis_id: str,
    candidate_digest: str,
) -> dict[str, object]:
    """Scelle la sélection unique faite avant toute consultation du holdout."""

    identifier = _identifier(hypothesis_id, "hypothesis_id")
    if not _is_digest(candidate_digest):
        raise SolverBenchmarkCorpusError("Candidate digest must be a SHA-256 digest.")
    selection: dict[str, object] = {
        "schema_version": SOLVER_BENCHMARK_HOLDOUT_SELECTION_SCHEMA_V1,
        "hypothesis_id": identifier,
        "candidate_digest": candidate_digest,
        "selected_candidate_count": 1,
        "selected_before_holdout": True,
    }
    selection["selection_digest"] = canonical_digest(selection)
    return selection


def open_holdout_cases(
    manifest: object,
    selection: object,
) -> dict[str, object]:
    """Ouvre une seule fois logiquement le holdout après sélection unique."""

    validated = validate_solver_benchmark_manifest(manifest)
    accepted_selection = _validate_holdout_selection(selection)
    cases = [
        _materialize_generated_case(record, allow_holdout=True)
        for record in validated["generated_cases"]
        if record["split"] == "holdout"
    ]
    return {
        "selection": accepted_selection,
        "manifest_digest": validated["manifest_digest"],
        "holdout_commitment_digest": validated["holdout_policy"][
            "case_commitment_digest"
        ],
        "cases": cases,
        "opening_digest": canonical_digest(
            {
                "selection_digest": accepted_selection["selection_digest"],
                "manifest_digest": validated["manifest_digest"],
                "case_ids": [case["case_id"] for case in cases],
            }
        ),
        "invariants": {"post_open_tuning_allowed": False},
    }


def materialize_benchmark_split(
    manifest: object,
    split: str,
    *,
    holdout_selection: object | None = None,
) -> list[dict[str, object]]:
    """Matérialise un split ; le holdout refuse tout accès implicite."""

    validated = validate_solver_benchmark_manifest(manifest)
    if split == "regression":
        return [
            deepcopy(case)
            for source in validated["regression_corpora"]
            for case in source["corpus"]["cases"]
        ]
    if split not in GENERATED_SPLITS:
        raise SolverBenchmarkCorpusError("Unknown benchmark split.")
    if split == "holdout":
        _validate_holdout_selection(holdout_selection)
    return [
        _materialize_generated_case(record, allow_holdout=split == "holdout")
        for record in validated["generated_cases"]
        if record["split"] == split
    ]

def materialize_generated_benchmark_case(
    case_record: object,
    *,
    holdout_selection: object | None = None,
) -> dict[str, object]:
    """Matérialise un cas isolé avec la même fermeture du holdout."""

    record = _mapping(case_record, "generated case")
    split = str(record.get("split", ""))
    if split == "holdout":
        _validate_holdout_selection(holdout_selection)
    return _materialize_generated_case(record, allow_holdout=split == "holdout")


def validate_materialized_benchmark_case(case: object) -> dict[str, object]:
    """Vérifie le projet, le témoin construit ou la preuve négative exacte."""

    value = _mapping(case, "materialized benchmark case")
    project = normalize_project_draft(value.get("project")).project
    if canonical_digest(project) != value.get("project_digest"):
        raise SolverBenchmarkCorpusError("Materialized project digest mismatch.")
    previous = value.get("previous_project")
    if previous is not None:
        previous_project = normalize_project_draft(previous).project
        if canonical_digest(previous_project) != value.get("previous_project_digest"):
            raise SolverBenchmarkCorpusError("Previous project digest mismatch.")
    oracle = _mapping(value.get("oracle"), "materialized benchmark case.oracle")
    if canonical_digest(oracle) != value.get("oracle_digest"):
        raise SolverBenchmarkCorpusError("Materialized oracle digest mismatch.")
    _validate_local_witness(project, oracle)
    kind = str(oracle.get("kind", ""))
    if kind == FEASIBLE_BY_CONSTRUCTION:
        _validate_global_witness(project, oracle)
    elif kind == PROVEN_IMPOSSIBLE_SMALL_EXACT:
        _validate_impossibility_proof(project, oracle)
    else:
        raise SolverBenchmarkCorpusError("Unsupported benchmark oracle kind.")
    return deepcopy(value)


def _build_generated_case_record(
    split: str,
    index: int,
    *,
    case_id_prefix: str = "",
    seed_base: int | None = None,
    split_offset: int | None = None,
) -> dict[str, object]:
    if split not in GENERATED_SPLITS:
        raise SolverBenchmarkCorpusError("Unknown generated split.")
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < 64:
        raise SolverBenchmarkCorpusError("Generated case index must stay within 0..63.")
    family = FAMILIES[index % 5] if index < 60 else FAMILIES[index - 60]
    family_ordinal = index // 5
    if family == FAMILY_INCREMENTAL_COLD:
        axis_ordinal = family_ordinal // 2
        seed_ordinal = axis_ordinal * 5 + 4
    else:
        axis_ordinal = family_ordinal
        seed_ordinal = index
    offset = _SPLIT_OFFSET[split] if split_offset is None else split_offset
    seed = (
        _SPLIT_SEED_BASE[split] if seed_base is None else seed_base
    ) + seed_ordinal
    groups = _GROUP_CHOICES[family]
    group_count = groups[(axis_ordinal + offset) % len(groups)]
    layer_count = (1, 2, 3)[(axis_ordinal * 2 + offset) % 3]
    content_profile = _ALLOWED_CONTENT_PROFILES[(axis_ordinal + offset) % 3]
    density = _ALLOWED_DENSITIES[(axis_ordinal * 2 + offset) % 3]
    arrangement = _ALLOWED_ARRANGEMENTS[(axis_ordinal + offset) % 2]
    reservation = _ALLOWED_RESERVATIONS[(axis_ordinal * 3 + offset) % 2]
    rotation = _ALLOWED_ROTATION_WITNESSES[(axis_ordinal + offset) % 2]
    rotation_policy = (
        "permitted" if rotation == "uses_z_rotation" else "forbidden_by_benchmark"
    )
    ordering = _ALLOWED_ORDERINGS[(axis_ordinal * 3 + offset) % 4]
    variant_target = (1, 2, 4, 8)[(axis_ordinal + 2 * offset) % 4]
    contents_per_group = _content_counts(family, group_count, axis_ordinal, offset)
    oracle_kind = (
        FEASIBLE_BY_CONSTRUCTION
        if family == FAMILY_INCREMENTAL_COLD or (index + offset) % 3 != 1
        else PROVEN_IMPOSSIBLE_SMALL_EXACT
    )
    proof_kind = (
        "none"
        if oracle_kind == FEASIBLE_BY_CONSTRUCTION
        else ("fixed_volume_bound" if (axis_ordinal + offset) % 2 == 0 else "body_height_bound")
    )
    if family == FAMILY_INCREMENTAL_COLD:
        pair_ordinal = family_ordinal // 2
        sequence_id = f"{split}-sequence-{pair_ordinal + 1:02d}"
        execution_mode = "incremental" if family_ordinal % 2 == 0 else "cold"
        change_kind = ("internal_modification", "new_container", "full_rebuild")[
            (pair_ordinal + offset) % 3
        ]
    else:
        sequence_id = "none"
        execution_mode = "cold"
        change_kind = "none"
    recipe: dict[str, object] = {
        "schema_version": SOLVER_BENCHMARK_RECIPE_SCHEMA_V1,
        "group_count": group_count,
        "contents_per_group": contents_per_group,
        "layer_count": layer_count,
        "content_profile": content_profile,
        "density_target": density,
        "arrangement_target": arrangement,
        "retained_variant_target": variant_target,
        "reservation_mode": reservation,
        "rotation_witness": rotation,
        "rotation_policy_target": rotation_policy,
        "ordering": ordering,
        "oracle_kind": oracle_kind,
        "proof_kind": proof_kind,
        "sequence_id": sequence_id,
        "execution_mode": execution_mode,
        "change_kind": change_kind,
    }
    case_id = (
        f"{case_id_prefix}{split}-{chr(97 + FAMILIES.index(family))}"
        f"-{index + 1:03d}"
    )
    core = _materialize_recipe(
        case_id=case_id,
        split=split,
        family=family,
        seed=seed,
        recipe=recipe,
    )
    return {
        "case_id": case_id,
        "split": split,
        "family": family,
        "seed": seed,
        "recipe": recipe,
        "project_digest": core["project_digest"],
        "previous_project_digest": core.get("previous_project_digest"),
        "oracle_digest": core["oracle_digest"],
        "solver_settings": {
            "method": "auto",
            "effort": "quick" if group_count <= 12 else "normal",
        },
        "features": core["features"],
    }


def _content_counts(
    family: str,
    group_count: int,
    ordinal: int,
    offset: int,
) -> list[int]:
    if family == FAMILY_MANY_ONE:
        return [1] * group_count
    if family == FAMILY_FEW_MANY:
        count = (8, 16, 32)[(ordinal + offset) % 3]
        return [count] * group_count
    if family == FAMILY_MANY_MANY:
        count = (2, 4, 8)[(ordinal * 2 + offset) % 3]
        return [count] * group_count
    if family == FAMILY_MIXED:
        targets = (1, 2, 4, 8, 16, 32)
        return [targets[(index + ordinal + offset) % len(targets)] for index in range(group_count)]
    count = (1, 2, 4)[(ordinal + offset) % 3]
    return [count] * group_count


def _materialize_generated_case(
    record: Mapping[str, object],
    *,
    allow_holdout: bool,
) -> dict[str, object]:
    split = str(record.get("split", ""))
    if split not in GENERATED_SPLITS:
        raise SolverBenchmarkCorpusError("Generated case split is unsupported.")
    if split == "holdout" and not allow_holdout:
        raise SolverBenchmarkCorpusError(
            "Holdout is sealed until one hypothesis has been selected."
        )
    case_id = _identifier(str(record.get("case_id", "")), "generated case id")
    family = str(record.get("family", ""))
    if family not in FAMILIES:
        raise SolverBenchmarkCorpusError("Generated case family is unsupported.")
    seed = record.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise SolverBenchmarkCorpusError("Generated case seed must be a non-negative integer.")
    recipe = _validate_recipe(record.get("recipe"))
    core = _materialize_recipe(
        case_id=case_id,
        split=split,
        family=family,
        seed=seed,
        recipe=recipe,
    )
    for field in ("project_digest", "previous_project_digest", "oracle_digest", "features"):
        if core.get(field) != record.get(field):
            raise SolverBenchmarkCorpusError(f"Generated case {field} mismatch.")
    settings = _mapping(record.get("solver_settings"), "generated case.solver_settings")
    if settings.get("method") != "auto" or settings.get("effort") not in {"quick", "normal"}:
        raise SolverBenchmarkCorpusError("Generated case solver settings are unsupported.")
    materialized = {
        "case_id": case_id,
        "split": split,
        "family": family,
        "seed": seed,
        "recipe": recipe,
        "solver_settings": deepcopy(settings),
        **core,
    }
    return validate_materialized_benchmark_case(materialized)


def _validate_recipe(value: object) -> dict[str, object]:
    recipe = _mapping(value, "generated case.recipe")
    if recipe.get("schema_version") != SOLVER_BENCHMARK_RECIPE_SCHEMA_V1:
        raise SolverBenchmarkCorpusError("Unsupported benchmark recipe schema.")
    count = recipe.get("group_count")
    if isinstance(count, bool) or not isinstance(count, int) or not 2 <= count <= 50:
        raise SolverBenchmarkCorpusError("Recipe group_count must stay within 2..50.")
    contents = recipe.get("contents_per_group")
    if not isinstance(contents, list) or len(contents) != count:
        raise SolverBenchmarkCorpusError("Recipe contents_per_group must match group_count.")
    if any(isinstance(item, bool) or not isinstance(item, int) or item not in {1, 2, 4, 8, 16, 32} for item in contents):
        raise SolverBenchmarkCorpusError("Recipe content counts use unsupported targets.")
    checks = (
        ("layer_count", {1, 2, 3}),
        ("retained_variant_target", {1, 2, 4, 8}),
        ("content_profile", set(_ALLOWED_CONTENT_PROFILES)),
        ("density_target", set(_ALLOWED_DENSITIES)),
        ("arrangement_target", set(_ALLOWED_ARRANGEMENTS)),
        ("reservation_mode", set(_ALLOWED_RESERVATIONS)),
        ("rotation_witness", set(_ALLOWED_ROTATION_WITNESSES)),
        ("rotation_policy_target", set(_ALLOWED_ROTATION_POLICIES)),
        ("ordering", set(_ALLOWED_ORDERINGS)),
        ("oracle_kind", set(_ALLOWED_ORACLES)),
        ("execution_mode", set(_ALLOWED_EXECUTION_MODES)),
        ("change_kind", set(_ALLOWED_CHANGE_KINDS)),
    )
    for field, allowed in checks:
        if recipe.get(field) not in allowed:
            raise SolverBenchmarkCorpusError(f"Recipe {field} is unsupported.")
    if (
        recipe["rotation_policy_target"] == "forbidden_by_benchmark"
        and recipe["rotation_witness"] != "fixed_zero_witness"
    ):
        raise SolverBenchmarkCorpusError("Forbidden rotation requires a zero-rotation witness.")
    if recipe.get("proof_kind") not in {"none", "fixed_volume_bound", "body_height_bound"}:
        raise SolverBenchmarkCorpusError("Recipe proof_kind is unsupported.")
    sequence_id = str(recipe.get("sequence_id", ""))
    if sequence_id != "none":
        _identifier(sequence_id, "recipe sequence_id")
    return deepcopy(recipe)

def _materialize_recipe(
    *,
    case_id: str,
    split: str,
    family: str,
    seed: int,
    recipe: Mapping[str, object],
) -> dict[str, object]:
    project_key = (
        str(recipe["sequence_id"])
        if family == FAMILY_INCREMENTAL_COLD
        else case_id
    )
    project, oracle = _build_project_and_oracle(
        project_key=project_key,
        seed=seed,
        recipe=recipe,
    )
    normalized = normalize_project_draft(project).project
    previous_project: dict[str, object] | None = None
    previous_digest: str | None = None
    if family == FAMILY_INCREMENTAL_COLD:
        previous_raw = _build_previous_project(
            project_key=project_key,
            seed=seed,
            recipe=recipe,
        )
        previous_project = normalize_project_draft(previous_raw).project
        previous_digest = canonical_digest(previous_project)
        if previous_digest == canonical_digest(normalized):
            raise SolverBenchmarkCorpusError("Incremental sequence must change the project.")
    group_count = len(normalized["container_groups"])
    content_counts = [
        sum(
            content["container_group_id"] == group["id"]
            for content in normalized["contents"]
        )
        for group in normalized["container_groups"]
    ]
    oracle_outer_volume = sum(
        _volume(_mapping(witness["outer_dimensions_mm"], "oracle outer dimensions"))
        for witness in oracle["local_content_witnesses"]
    )
    box = _mapping(normalized["box"], "project.box")
    dimensions = _mapping(box["inner_dimensions_mm"], "project.box.inner_dimensions_mm")
    box_volume = float(dimensions["x"]) * float(dimensions["y"]) * float(
        box["usable_height_mm"]
    )
    features = {
        "container_group_count": group_count,
        "content_count": len(normalized["contents"]),
        "contents_per_container_minimum": min(content_counts),
        "contents_per_container_maximum": max(content_counts),
        "retained_variant_target": recipe["retained_variant_target"],
        "layer_target": min(int(recipe["layer_count"]), group_count),
        "content_profile": recipe["content_profile"],
        "density_target": recipe["density_target"],
        "arrangement_target": recipe["arrangement_target"],
        "reservation_mode": recipe["reservation_mode"],
        "rotation_witness": recipe["rotation_witness"],
        "rotation_policy_target": recipe["rotation_policy_target"],
        "rotation_disable_control": "not_exposed_by_project_v1",
        "ordering": recipe["ordering"],
        "execution_mode": recipe["execution_mode"],
        "change_kind": recipe["change_kind"],
        "oracle_outer_load_ratio": round(oracle_outer_volume / box_volume, 8),
        "oracle_kind": recipe["oracle_kind"],
    }
    result: dict[str, object] = {
        "project": normalized,
        "project_digest": canonical_digest(normalized),
        "previous_project": previous_project,
        "previous_project_digest": previous_digest,
        "oracle": oracle,
        "oracle_digest": canonical_digest(oracle),
        "features": features,
        "invariants": {
            "t0_t1_only": True,
            "oracle_not_supplied_as_warm_start": True,
            "solver_invocation_count": 0,
            "external_dependency_count": 0,
        },
    }
    return result


def _build_previous_project(
    *,
    project_key: str,
    seed: int,
    recipe: Mapping[str, object],
) -> dict[str, object]:
    change_kind = str(recipe["change_kind"])
    previous_recipe = deepcopy(dict(recipe))
    counts = list(previous_recipe["contents_per_group"])
    previous_seed = seed
    if change_kind == "internal_modification":
        counts[0] = max(1, counts[0] // 2)
    elif change_kind == "new_container":
        previous_recipe["group_count"] = int(previous_recipe["group_count"]) - 1
        counts = counts[:-1]
    elif change_kind == "full_rebuild":
        previous_seed = seed + 100_003
        previous_recipe["content_profile"] = {
            "homogeneous": "heterogeneous",
            "heterogeneous": "nearly_equal",
            "nearly_equal": "homogeneous",
        }[str(previous_recipe["content_profile"])]
    else:
        raise SolverBenchmarkCorpusError("Incremental family requires a real change kind.")
    previous_recipe["contents_per_group"] = counts
    previous_recipe["execution_mode"] = "cold"
    project, _oracle = _build_project_and_oracle(
        project_key=f"{project_key}-before",
        seed=previous_seed,
        recipe=previous_recipe,
    )
    return project


def _build_project_and_oracle(
    *,
    project_key: str,
    seed: int,
    recipe: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    group_count = int(recipe["group_count"])
    counts = [int(value) for value in recipe["contents_per_group"]]
    layers = min(int(recipe["layer_count"]), group_count)
    stack_count = int(ceil(group_count / layers))
    locals_by_id: dict[str, dict[str, object]] = {}
    for index in range(group_count):
        level = index // stack_count
        scale = 1.0 - 0.06 * level
        group_id = f"container-{index + 1:03d}"
        locals_by_id[group_id] = _build_local_container(
            seed=seed,
            group_index=index,
            group_id=group_id,
            content_count=counts[index],
            profile=str(recipe["content_profile"]),
            variant_target=int(recipe["retained_variant_target"]),
            arrangement=str(recipe["arrangement_target"]),
            scale=scale,
        )

    locals_by_id = _canonical_local_geometry(locals_by_id)

    stacks: list[list[str]] = [[] for _ in range(stack_count)]
    for index in range(group_count):
        stacks[index % stack_count].append(f"container-{index + 1:03d}")
    for members in stacks:
        maximum_x = max(float(locals_by_id[group_id]["outer_dimensions_mm"]["x"]) for group_id in members)
        maximum_y = max(float(locals_by_id[group_id]["outer_dimensions_mm"]["y"]) for group_id in members)
        for group_id in members:
            locals_by_id[group_id]["outer_dimensions_mm"]["x"] = round(maximum_x, 3)
            locals_by_id[group_id]["outer_dimensions_mm"]["y"] = round(maximum_y, 3)

    rotations = {
        stack_index: (
            90
            if recipe["rotation_witness"] == "uses_z_rotation" and stack_index % 2 == 1
            else 0
        )
        for stack_index in range(stack_count)
    }
    stack_world_sizes: list[dict[str, float]] = []
    for stack_index, members in enumerate(stacks):
        first = locals_by_id[members[0]]["outer_dimensions_mm"]
        rotation = rotations[stack_index]
        stack_world_sizes.append(
            {
                "x": float(first["y"] if rotation == 90 else first["x"]),
                "y": float(first["x"] if rotation == 90 else first["y"]),
                "z": sum(
                    float(locals_by_id[group_id]["outer_dimensions_mm"]["z"])
                    for group_id in members
                ),
            }
        )
    columns = max(1, int(ceil(sqrt(stack_count))))
    rows = int(ceil(stack_count / columns))
    column_widths = [0.0] * columns
    row_depths = [0.0] * rows
    for stack_index, size in enumerate(stack_world_sizes):
        column = stack_index % columns
        row = stack_index // columns
        column_widths[column] = max(column_widths[column], size["x"])
        row_depths[row] = max(row_depths[row], size["y"])
    gap = 0.8
    reservation_strip = 12.0 if recipe["reservation_mode"] == "constraining" else 0.0
    base_margin = {"nearly_saturated": 0.4, "dense": 2.0, "ample": 12.0}[
        str(recipe["density_target"])
    ]
    x_offsets = [reservation_strip + base_margin]
    for width in column_widths[:-1]:
        x_offsets.append(x_offsets[-1] + width + gap)
    y_offsets = [base_margin]
    for depth in row_depths[:-1]:
        y_offsets.append(y_offsets[-1] + depth + gap)
    placements: list[dict[str, object]] = []
    for stack_index, members in enumerate(stacks):
        column = stack_index % columns
        row = stack_index // columns
        z = 0.0
        for level, group_id in enumerate(members):
            local_size = locals_by_id[group_id]["outer_dimensions_mm"]
            rotation = rotations[stack_index]
            world_size = {
                "x": float(local_size["y"] if rotation == 90 else local_size["x"]),
                "y": float(local_size["x"] if rotation == 90 else local_size["y"]),
                "z": float(local_size["z"]),
            }
            placements.append(
                {
                    "container_group_id": group_id,
                    "origin_mm": {
                        "x": round(x_offsets[column], 3),
                        "y": round(y_offsets[row], 3),
                        "z": round(z, 3),
                    },
                    "world_size_mm": {axis: round(value, 3) for axis, value in world_size.items()},
                    "rotation_deg_z": rotation,
                    "stack_index": stack_index,
                    "layer_index": level,
                }
            )
            z += world_size["z"]
    extent_x = max(float(p["origin_mm"]["x"]) + float(p["world_size_mm"]["x"]) for p in placements)
    extent_y = max(float(p["origin_mm"]["y"]) + float(p["world_size_mm"]["y"]) for p in placements)
    extent_z = max(float(p["origin_mm"]["z"]) + float(p["world_size_mm"]["z"]) for p in placements)
    box_dimensions = {
        "x": round(extent_x + base_margin, 3),
        "y": round(extent_y + base_margin, 3),
        "z": round(extent_z + 0.4, 3),
    }
    proof: dict[str, object] | None = None
    if recipe["oracle_kind"] == PROVEN_IMPOSSIBLE_SMALL_EXACT:
        locked_volume = sum(
            _volume(_mapping(value["outer_dimensions_mm"], "outer dimensions"))
            for value in locals_by_id.values()
        )
        maximum_z = max(float(value["outer_dimensions_mm"]["z"]) for value in locals_by_id.values())
        if recipe["proof_kind"] == "fixed_volume_bound":
            longest_xy = max(
                max(
                    float(value["outer_dimensions_mm"]["x"]),
                    float(value["outer_dimensions_mm"]["y"]),
                )
                for value in locals_by_id.values()
            )
            shortest_xy = max(
                min(
                    float(value["outer_dimensions_mm"]["x"]),
                    float(value["outer_dimensions_mm"]["y"]),
                )
                for value in locals_by_id.values()
            )
            box_dimensions["x"] = round(longest_xy + 0.4, 3)
            box_dimensions["y"] = round(shortest_xy + 0.4, 3)
            box_dimensions["z"] = round(maximum_z + 0.4, 3)
            available_volume = (
                box_dimensions["x"] * box_dimensions["y"] * box_dimensions["z"]
            )
            if locked_volume <= available_volume + _EPSILON:
                raise SolverBenchmarkCorpusError(
                    "Generated fixed-volume proof lacks a strict lower-bound conflict."
                )
            proof = {
                "kind": "fixed_volume_bound",
                "required_volume_mm3": round(locked_volume, 6),
                "available_volume_mm3": round(
                    box_dimensions["x"] * box_dimensions["y"] * box_dimensions["z"], 6
                ),
            }
        else:
            box_dimensions["z"] = round(max(0.1, maximum_z - 0.1), 3)
            proof = {
                "kind": "body_height_bound",
                "minimum_required_height_mm": round(maximum_z, 6),
                "available_height_mm": box_dimensions["z"],
            }

    project = blank_project_v1()
    project["project_name"] = f"Benchmark {project_key}"
    project["box"] = {
        "inner_dimensions_mm": deepcopy(box_dimensions),
        "usable_height_mm": box_dimensions["z"],
        "lid_clearance_mm": 0.0,
    }
    project["layout"] = {
        "layout_clearance_mm": 0.2,
        "container_box_xy_clearance_mm": 0.2,
        "container_z_clearance_mm": 0.0,
        "default_wall_thickness_mm": 1.2,
        "default_floor_thickness_mm": 1.2,
        "default_content_clearance_mm": 0.0,
    }
    groups: list[dict[str, object]] = []
    contents: list[dict[str, object]] = []
    local_witnesses: list[dict[str, object]] = []
    for group_id, local in locals_by_id.items():
        outer = deepcopy(local["outer_dimensions_mm"])
        group: dict[str, object] = {
            "id": group_id,
            "name": f"Conteneur {group_id}",
            "wall_thickness_mm": 1.2,
            "floor_thickness_mm": 1.2,
        }
        if recipe["oracle_kind"] == PROVEN_IMPOSSIBLE_SMALL_EXACT:
            group.update(
                {
                    "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
                    "locked_outer_dimensions_mm": deepcopy(outer),
                    "target_outer_dimensions_mm": deepcopy(outer),
                }
            )
        else:
            group.update(
                {
                    "dimension_modes": {"x": "auto", "y": "auto", "z": "auto"},
                    "locked_outer_dimensions_mm": {"x": None, "y": None, "z": None},
                    "target_outer_dimensions_mm": {"x": None, "y": None, "z": None},
                }
            )
        groups.append(group)
        contents.extend(deepcopy(local["contents"]))
        local_witnesses.append(
            {
                "container_group_id": group_id,
                "outer_dimensions_mm": deepcopy(outer),
                "content_placements": deepcopy(local["content_placements"]),
            }
        )
    groups, contents = _ordered_project_items(
        groups,
        contents,
        ordering=str(recipe["ordering"]),
        seed=seed,
        outer_by_group={
            group_id: local["outer_dimensions_mm"]
            for group_id, local in locals_by_id.items()
        },
    )
    project["container_groups"] = groups
    project["contents"] = contents
    if recipe["reservation_mode"] == "constraining":
        project["flat_items"] = [
            {
                "id": "reserved-strip",
                "name": "Réservation témoin",
                "kind": "board",
                "dimensions_mm": {
                    "x": round(min(10.0, box_dimensions["x"] / 3.0), 3),
                    "y": round(max(0.1, box_dimensions["y"] - 0.8), 3),
                    "z": round(min(2.0, box_dimensions["z"] / 3.0), 3),
                },
                "quantity": 1,
                "stack_order": 0,
                "origin_mm": {"x": 0.2, "y": 0.2},
                "rotation_deg_z": 0,
            }
        ]
    oracle = {
        "kind": recipe["oracle_kind"],
        "rotation_policy_target": recipe["rotation_policy_target"],
        "expected_truth": (
            "feasible"
            if recipe["oracle_kind"] == FEASIBLE_BY_CONSTRUCTION
            else "impossible"
        ),
        "local_content_witnesses": sorted(
            local_witnesses, key=lambda item: str(item["container_group_id"])
        ),
        "global_container_placements": (
            sorted(placements, key=lambda item: str(item["container_group_id"]))
            if recipe["oracle_kind"] == FEASIBLE_BY_CONSTRUCTION
            else []
        ),
        "removal_sequence": (
            [
                item["container_group_id"]
                for item in sorted(
                    placements,
                    key=lambda item: (
                        -float(item["origin_mm"]["z"]),
                        int(item["stack_index"]),
                    ),
                )
            ]
            if recipe["oracle_kind"] == FEASIBLE_BY_CONSTRUCTION
            else []
        ),
        "proof": proof,
        "certificate_scope": "independent_aabb_construction_or_exact_lower_bound",
        "supplied_to_tested_solver": False,
    }
    return project, oracle

def _canonical_local_geometry(
    locals_by_id: Mapping[str, Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    """Use the certified P45 canonical draft as the constructed local witness."""

    project = blank_project_v1()
    project["project_name"] = "Benchmark local construction"
    project["box"] = {
        "inner_dimensions_mm": {"x": 5000.0, "y": 5000.0, "z": 1000.0},
        "usable_height_mm": 1000.0,
        "lid_clearance_mm": 0.0,
    }
    project["layout"] = {
        "layout_clearance_mm": 0.2,
        "container_box_xy_clearance_mm": 0.2,
        "container_z_clearance_mm": 0.0,
        "default_wall_thickness_mm": 1.2,
        "default_floor_thickness_mm": 1.2,
        "default_content_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {
            "id": group_id,
            "name": f"Conteneur {group_id}",
            "wall_thickness_mm": 1.2,
            "floor_thickness_mm": 1.2,
        }
        for group_id in locals_by_id
    ]
    project["contents"] = [
        deepcopy(content)
        for local in locals_by_id.values()
        for content in local["contents"]
    ]
    plan = derive_container_plan(project)
    result = {group_id: deepcopy(dict(local)) for group_id, local in locals_by_id.items()}
    for raw_container in plan["containers"]:
        container = _mapping(raw_container, "derived local container")
        group_id = str(container["container_group_id"])
        if container.get("status") != "ready":
            raise SolverBenchmarkCorpusError(
                f"P45 canonical construction is blocked for {group_id}."
            )
        result[group_id]["outer_dimensions_mm"] = deepcopy(
            _mapping(container["outer_dimensions_mm"], "derived outer dimensions")
        )
        result[group_id]["content_placements"] = [
            {
                "content_id": compartment["content_id"],
                "origin_mm": deepcopy(compartment["local_origin_mm"]),
                "size_mm": deepcopy(compartment["inner_dimensions_mm"]),
            }
            for compartment in container["compartments"]
        ]
    return result

def _build_local_container(
    *,
    seed: int,
    group_index: int,
    group_id: str,
    content_count: int,
    profile: str,
    variant_target: int,
    arrangement: str,
    scale: float,
) -> dict[str, object]:
    rng = Random(seed + group_index * 7_919)
    base_x = (7.0 + rng.randrange(0, 7)) * scale
    base_y = (6.0 + rng.randrange(0, 8)) * scale
    base_z = (3.0 + rng.randrange(0, 5)) * scale
    sizes: list[dict[str, float]] = []
    for index in range(content_count):
        if profile == "homogeneous":
            x, y, z = base_x, base_y, base_z
        elif profile == "nearly_equal":
            delta = (-0.25, 0.0, 0.25)[index % 3] * scale
            x, y, z = base_x + delta, base_y - delta, base_z + delta / 2.0
        else:
            x = base_x * (0.72 + 0.14 * (index % 4))
            y = base_y * (0.78 + 0.12 * ((index * 3) % 4))
            z = base_z * (0.82 + 0.09 * ((index * 5) % 4))
        sizes.append({"x": round(x, 3), "y": round(y, 3), "z": round(z, 3)})
    if arrangement == "obvious":
        columns = min(content_count, max(1, 2 * variant_target))
    else:
        columns = min(content_count, max(1, int(ceil(sqrt(content_count)))))
    rows = int(ceil(content_count / columns))
    column_widths = [0.0] * columns
    row_depths = [0.0] * rows
    for index, size in enumerate(sizes):
        column_widths[index % columns] = max(column_widths[index % columns], size["x"])
        row_depths[index // columns] = max(row_depths[index // columns], size["y"])
    gap = 1.2
    wall = 1.2
    x_offsets = [wall]
    for width in column_widths[:-1]:
        x_offsets.append(x_offsets[-1] + width + gap)
    y_offsets = [wall]
    for depth in row_depths[:-1]:
        y_offsets.append(y_offsets[-1] + depth + gap)
    contents: list[dict[str, object]] = []
    placements: list[dict[str, object]] = []
    for index, size in enumerate(sizes):
        content_id = f"{group_id}-content-{index + 1:03d}"
        contents.append(
            {
                "id": content_id,
                "name": f"Contenu {content_id}",
                "shape_kind": "rectangle",
                "dimensions_mm": deepcopy(size),
                "quantity": 1,
                "container_group_id": group_id,
                "content_clearance_mm": 0.0,
                "measurement_confidence": "exact",
            }
        )
        placements.append(
            {
                "content_id": content_id,
                "origin_mm": {
                    "x": round(x_offsets[index % columns], 3),
                    "y": round(y_offsets[index // columns], 3),
                    "z": wall,
                },
                "size_mm": deepcopy(size),
            }
        )
    outer = {
        "x": round(2.0 * wall + sum(column_widths) + gap * max(0, columns - 1), 3),
        "y": round(2.0 * wall + sum(row_depths) + gap * max(0, rows - 1), 3),
        "z": round(wall + max(size["z"] for size in sizes) + 0.2, 3),
    }
    return {
        "outer_dimensions_mm": outer,
        "contents": contents,
        "content_placements": placements,
    }


def _ordered_project_items(
    groups: list[dict[str, object]],
    contents: list[dict[str, object]],
    *,
    ordering: str,
    seed: int,
    outer_by_group: Mapping[str, Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if ordering == "natural":
        return groups, contents
    if ordering == "reversed":
        return list(reversed(groups)), list(reversed(contents))
    if ordering == "volume_ascending":
        groups = sorted(
            groups,
            key=lambda group: _volume(
                outer_by_group[str(group["id"])]
            ),
        )
        contents = sorted(
            contents,
            key=lambda content: _volume(
                _mapping(content["dimensions_mm"], "content dimensions")
            ),
        )
        return groups, contents
    rng = Random(seed + 97_531)
    rng.shuffle(groups)
    rng.shuffle(contents)
    return groups, contents


def _validate_local_witness(
    project: Mapping[str, object],
    oracle: Mapping[str, object],
) -> None:
    groups = {str(item["id"]): item for item in project["container_groups"]}
    contents = {str(item["id"]): item for item in project["contents"]}
    raw_witnesses = oracle.get("local_content_witnesses")
    if not isinstance(raw_witnesses, list) or len(raw_witnesses) != len(groups):
        raise SolverBenchmarkCorpusError("Local witness must cover every container group.")
    seen_contents: set[str] = set()
    seen_groups: set[str] = set()
    for raw in raw_witnesses:
        witness = _mapping(raw, "oracle.local_content_witnesses[]")
        group_id = str(witness.get("container_group_id", ""))
        if group_id not in groups or group_id in seen_groups:
            raise SolverBenchmarkCorpusError("Local witness group coverage is invalid.")
        seen_groups.add(group_id)
        group = groups[group_id]
        outer = _mapping(witness.get("outer_dimensions_mm"), "witness outer dimensions")
        modes = _mapping(group["dimension_modes"], "group dimension modes")
        locked = _mapping(group["locked_outer_dimensions_mm"], "locked dimensions")
        for axis in "xyz":
            if modes[axis] == "fixed":
                if not isclose(float(locked[axis]), float(outer[axis]), abs_tol=_EPSILON):
                    raise SolverBenchmarkCorpusError("Fixed local witness dimensions mismatch.")
            elif locked[axis] is not None:
                raise SolverBenchmarkCorpusError("Automatic local witness carries a fixed dimension.")
        raw_placements = witness.get("content_placements")
        if not isinstance(raw_placements, list):
            raise SolverBenchmarkCorpusError("Local content placements must be a list.")
        boxes: list[tuple[dict[str, float], dict[str, float]]] = []
        for raw_placement in raw_placements:
            placement = _mapping(raw_placement, "oracle.content_placements[]")
            content_id = str(placement.get("content_id", ""))
            if content_id not in contents or content_id in seen_contents:
                raise SolverBenchmarkCorpusError("Local witness content coverage is invalid.")
            content = contents[content_id]
            if content["container_group_id"] != group_id:
                raise SolverBenchmarkCorpusError("Local witness content uses the wrong group.")
            origin = _float_dimension(placement.get("origin_mm"), "content origin")
            size = _float_dimension(placement.get("size_mm"), "content size")
            expected = _float_dimension(content["dimensions_mm"], "content dimensions")
            if any(not isclose(size[axis], expected[axis], abs_tol=_EPSILON) for axis in "xyz"):
                raise SolverBenchmarkCorpusError("Local witness content size mismatch.")
            wall = float(group["wall_thickness_mm"])
            floor = float(group["floor_thickness_mm"])
            if (
                origin["x"] < wall - _EPSILON
                or origin["y"] < wall - _EPSILON
                or origin["z"] < floor - _EPSILON
                or origin["x"] + size["x"] > float(outer["x"]) - wall + _EPSILON
                or origin["y"] + size["y"] > float(outer["y"]) - wall + _EPSILON
                or origin["z"] + size["z"] > float(outer["z"]) + _EPSILON
            ):
                raise SolverBenchmarkCorpusError("Local witness violates wall or floor bounds.")
            for other_origin, other_size in boxes:
                if _boxes_overlap(origin, size, other_origin, other_size):
                    raise SolverBenchmarkCorpusError("Local witness content placements overlap.")
                if _xy_separation(origin, size, other_origin, other_size) < wall - _EPSILON:
                    raise SolverBenchmarkCorpusError("Local witness lacks a separating wall.")
            boxes.append((origin, size))
            seen_contents.add(content_id)
    if seen_contents != set(contents):
        raise SolverBenchmarkCorpusError("Local witness does not cover every content.")


def _validate_global_witness(
    project: Mapping[str, object],
    oracle: Mapping[str, object],
) -> None:
    groups = {str(item["id"]): item for item in project["container_groups"]}
    oracle_outer = {
        str(item["container_group_id"]): _float_dimension(
            item["outer_dimensions_mm"], "oracle outer dimensions"
        )
        for item in oracle["local_content_witnesses"]
    }
    raw_placements = oracle.get("global_container_placements")
    if not isinstance(raw_placements, list) or len(raw_placements) != len(groups):
        raise SolverBenchmarkCorpusError("Global witness must cover every container.")
    box = _mapping(project["box"], "project.box")
    box_xy = _mapping(box["inner_dimensions_mm"], "project.box.inner_dimensions_mm")
    bounds = {"x": float(box_xy["x"]), "y": float(box_xy["y"]), "z": float(box["usable_height_mm"])}
    placed: list[tuple[str, dict[str, float], dict[str, float], int]] = []
    seen: set[str] = set()
    for raw in raw_placements:
        placement = _mapping(raw, "oracle.global_container_placements[]")
        group_id = str(placement.get("container_group_id", ""))
        if group_id not in groups or group_id in seen:
            raise SolverBenchmarkCorpusError("Global witness group coverage is invalid.")
        seen.add(group_id)
        origin = _float_dimension(placement.get("origin_mm"), "container origin")
        size = _float_dimension(placement.get("world_size_mm"), "container world size")
        rotation = int(placement.get("rotation_deg_z", -1))
        if oracle.get("rotation_policy_target") == "forbidden_by_benchmark" and rotation != 0:
            raise SolverBenchmarkCorpusError("Forbidden-rotation witness must stay at zero degrees.")
        if rotation not in {0, 90}:
            raise SolverBenchmarkCorpusError("Global witness rotation must be 0 or 90 degrees.")
        local = oracle_outer[group_id]
        expected = {"x": local["y"] if rotation == 90 else local["x"], "y": local["x"] if rotation == 90 else local["y"], "z": local["z"]}
        if any(not isclose(size[axis], expected[axis], abs_tol=_EPSILON) for axis in "xyz"):
            raise SolverBenchmarkCorpusError("Global witness size or rotation mismatch.")
        if any(origin[axis] < -_EPSILON or origin[axis] + size[axis] > bounds[axis] + _EPSILON for axis in "xyz"):
            raise SolverBenchmarkCorpusError("Global witness exceeds the game box.")
        if any(_boxes_overlap(origin, size, other_origin, other_size) for _id, other_origin, other_size, _level in placed):
            raise SolverBenchmarkCorpusError("Global witness container placements overlap.")
        level = int(placement.get("layer_index", -1))
        placed.append((group_id, origin, size, level))
    _validate_reservation_projection(project, placed)
    for group_id, origin, size, level in placed:
        if level <= 0:
            if not isclose(origin["z"], 0.0, abs_tol=_EPSILON):
                raise SolverBenchmarkCorpusError("Base-layer witness must start at z=0.")
            continue
        supported = any(
            isclose(other_origin["z"] + other_size["z"], origin["z"], abs_tol=_EPSILON)
            and other_origin["x"] <= origin["x"] + _EPSILON
            and other_origin["y"] <= origin["y"] + _EPSILON
            and other_origin["x"] + other_size["x"] >= origin["x"] + size["x"] - _EPSILON
            and other_origin["y"] + other_size["y"] >= origin["y"] + size["y"] - _EPSILON
            for other_id, other_origin, other_size, _other_level in placed
            if other_id != group_id
        )
        if not supported:
            raise SolverBenchmarkCorpusError("Upper-layer witness lacks full support.")
    sequence = oracle.get("removal_sequence")
    if not isinstance(sequence, list) or set(str(value) for value in sequence) != set(groups):
        raise SolverBenchmarkCorpusError("Removal sequence must cover every container.")
    positions = {str(group_id): index for index, group_id in enumerate(sequence)}
    for upper_id, upper_origin, _upper_size, _level in placed:
        for lower_id, lower_origin, lower_size, _other_level in placed:
            if (
                isclose(
                    lower_origin["z"] + lower_size["z"],
                    upper_origin["z"],
                    abs_tol=_EPSILON,
                )
                and _rectangles_overlap_xy(lower_origin, lower_size, upper_origin, _upper_size)
                and positions[upper_id] > positions[lower_id]
            ):
                raise SolverBenchmarkCorpusError("Removal sequence must remove upper containers first.")


def _validate_reservation_projection(
    project: Mapping[str, object],
    placed: Sequence[tuple[str, dict[str, float], dict[str, float], int]],
) -> None:
    for raw in project["flat_items"]:
        item = _mapping(raw, "project.flat_items[]")
        origin = _mapping(item["origin_mm"], "flat item origin")
        dimensions = _mapping(item["dimensions_mm"], "flat item dimensions")
        reservation_origin = {"x": float(origin["x"]), "y": float(origin["y"]), "z": 0.0}
        reservation_size = {"x": float(dimensions["x"]), "y": float(dimensions["y"]), "z": float("inf")}
        for _group_id, placed_origin, placed_size, _level in placed:
            if _boxes_overlap(reservation_origin, reservation_size, placed_origin, placed_size):
                raise SolverBenchmarkCorpusError("Global witness intersects a reservation projection.")


def _validate_impossibility_proof(
    project: Mapping[str, object],
    oracle: Mapping[str, object],
) -> None:
    proof = _mapping(oracle.get("proof"), "oracle.proof")
    groups = list(project["container_groups"])
    box = _mapping(project["box"], "project.box")
    dimensions = _mapping(box["inner_dimensions_mm"], "project.box.inner_dimensions_mm")
    if proof.get("kind") == "fixed_volume_bound":
        required = sum(
            _volume(_mapping(group["locked_outer_dimensions_mm"], "locked dimensions"))
            for group in groups
        )
        available = float(dimensions["x"]) * float(dimensions["y"]) * float(box["usable_height_mm"])
        if required <= available + _EPSILON:
            raise SolverBenchmarkCorpusError("Fixed-volume impossibility proof is false.")
        if not isclose(float(proof.get("required_volume_mm3", -1.0)), required, abs_tol=0.01) or not isclose(float(proof.get("available_volume_mm3", -1.0)), available, abs_tol=0.01):
            raise SolverBenchmarkCorpusError("Fixed-volume proof facts mismatch.")
    elif proof.get("kind") == "body_height_bound":
        required = max(float(group["locked_outer_dimensions_mm"]["z"]) for group in groups)
        available = float(box["usable_height_mm"])
        if required <= available + _EPSILON:
            raise SolverBenchmarkCorpusError("Body-height impossibility proof is false.")
        if not isclose(float(proof.get("minimum_required_height_mm", -1.0)), required, abs_tol=0.01) or not isclose(float(proof.get("available_height_mm", -1.0)), available, abs_tol=0.01):
            raise SolverBenchmarkCorpusError("Body-height proof facts mismatch.")
    else:
        raise SolverBenchmarkCorpusError("Unsupported impossibility proof.")

def _validate_holdout_selection(value: object) -> dict[str, object]:
    selection = _mapping(value, "holdout selection")
    supplied = selection.pop("selection_digest", None)
    if selection.get("schema_version") != SOLVER_BENCHMARK_HOLDOUT_SELECTION_SCHEMA_V1:
        raise SolverBenchmarkCorpusError("Unsupported holdout selection schema.")
    _identifier(str(selection.get("hypothesis_id", "")), "hypothesis_id")
    if not _is_digest(selection.get("candidate_digest")):
        raise SolverBenchmarkCorpusError("Holdout candidate digest is invalid.")
    if selection.get("selected_candidate_count") != 1:
        raise SolverBenchmarkCorpusError("Holdout requires exactly one selected candidate.")
    if selection.get("selected_before_holdout") is not True:
        raise SolverBenchmarkCorpusError("Candidate must be selected before holdout opens.")
    if not _is_digest(supplied) or canonical_digest(selection) != supplied:
        raise SolverBenchmarkCorpusError("Holdout selection digest mismatch.")
    selection["selection_digest"] = supplied
    return selection


def _rectangles_overlap_xy(
    first_origin: Mapping[str, float],
    first_size: Mapping[str, float],
    second_origin: Mapping[str, float],
    second_size: Mapping[str, float],
) -> bool:
    return all(
        float(first_origin[axis])
        < float(second_origin[axis]) + float(second_size[axis]) - _EPSILON
        and float(second_origin[axis])
        < float(first_origin[axis]) + float(first_size[axis]) - _EPSILON
        for axis in "xy"
    )

def _xy_separation(
    first_origin: Mapping[str, float],
    first_size: Mapping[str, float],
    second_origin: Mapping[str, float],
    second_size: Mapping[str, float],
) -> float:
    gaps = []
    for axis in "xy":
        gaps.append(
            max(
                0.0,
                float(second_origin[axis])
                - (float(first_origin[axis]) + float(first_size[axis])),
                float(first_origin[axis])
                - (float(second_origin[axis]) + float(second_size[axis])),
            )
        )
    return max(gaps)

def _boxes_overlap(
    first_origin: Mapping[str, float],
    first_size: Mapping[str, float],
    second_origin: Mapping[str, float],
    second_size: Mapping[str, float],
) -> bool:
    return all(
        float(first_origin[axis]) < float(second_origin[axis]) + float(second_size[axis]) - _EPSILON
        and float(second_origin[axis]) < float(first_origin[axis]) + float(first_size[axis]) - _EPSILON
        for axis in "xyz"
    )


def _volume(value: Mapping[str, object]) -> float:
    return float(value["x"]) * float(value["y"]) * float(value["z"])


def _float_dimension(value: object, field: str) -> dict[str, float]:
    raw = _mapping(value, field)
    if set(raw) != {"x", "y", "z"}:
        raise SolverBenchmarkCorpusError(f"{field} must contain x, y and z.")
    result: dict[str, float] = {}
    for axis in "xyz":
        item = raw[axis]
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise SolverBenchmarkCorpusError(f"{field}.{axis} must be numeric.")
        result[axis] = float(item)
    return result


def _identifier(value: str, field: str) -> str:
    result = str(value).strip()
    if not result or len(result) > 128 or any(separator in result for separator in ("/", "\\")):
        raise SolverBenchmarkCorpusError(f"{field} must be a portable identifier.")
    return result


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise SolverBenchmarkCorpusError(f"{field} must be an object.")
    return dict(value)


def _is_digest(value: object) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _reject_secret_keys(value: object, path: str = "manifest") -> None:
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key).lower()
            if any(fragment in key for fragment in _SECRET_KEY_FRAGMENTS):
                raise SolverBenchmarkCorpusError(
                    f"Secret-like key is forbidden in benchmark manifest: {path}.{raw_key}."
                )
            _reject_secret_keys(item, f"{path}.{raw_key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_secret_keys(item, f"{path}[{index}]")
