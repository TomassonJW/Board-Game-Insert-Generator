"""Corpus V2 du tournoi externe P64-L07.

Le module conserve les régressions L06, crée une campagne BGIG fraîche et
décrit deux sources publiques verrouillées. Les cas publics restent des
contrôles de méthode : seules les entrées BGIG entièrement recertifiables
participent au classement produit.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO, Mapping, Sequence
from zipfile import BadZipFile, ZipFile

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.solver_benchmark_corpus import (
    FAMILIES,
    FEASIBLE_BY_CONSTRUCTION,
    GENERATED_CASES_PER_SPLIT,
    GENERATED_SPLITS,
    PROVEN_IMPOSSIBLE_SMALL_EXACT,
    SOLVER_BENCHMARK_MANIFEST_SCHEMA_V1,
    SolverBenchmarkCorpusError,
    build_generated_benchmark_case_records,
    build_holdout_selection,
    materialize_generated_benchmark_case,
    validate_solver_benchmark_manifest,
)
from board_game_insert_generator.solver_case_corpus import validate_solver_case_corpus


EXTERNAL_SOLVER_BENCHMARK_MANIFEST_SCHEMA_V2 = (
    "bgig.solver_benchmark_manifest.v2"
)
EXTERNAL_SOLVER_HOLDOUT_SELECTION_SCHEMA_V2 = (
    "bgig.external_solver_holdout_selection.v2"
)
EXTERNAL_SOLVER_SEALED_HOLDOUT_SCHEMA_V2 = (
    "bgig.external_solver_sealed_holdout.v2"
)
EXTERNAL_SOLVER_HOLDOUT_RECEIPT_SCHEMA_V2 = (
    "bgig.external_solver_holdout_receipt.v2"
)
EXTERNAL_SOLVER_BENCHMARK_PRODUCER_ID = "p64_l07_t0_t1_generator"
EXTERNAL_SOLVER_BENCHMARK_PRODUCER_VERSION = "2"
EXTERNAL_CASE_ID_PREFIX = "l07-v2-"
EXTERNAL_OPEN_SPLITS = ("discovery", "tuning")
EXTERNAL_SPLIT_SEED_BASES = {
    "discovery": 640_710_000,
    "tuning": 640_720_000,
}
EXTERNAL_SPLIT_OFFSETS = {"discovery": 3, "tuning": 7}
MAX_PUBLIC_SOURCE_BYTES = 64 * 1024 * 1024
_SECRET_KEY_FRAGMENTS = ("api_key", "authorization", "password", "secret", "token")

_Q4_ROOT = "Benchmark dataset and instance generator for Real-World 3dBPP"
_Q4_SELECTED_MEMBERS = (
    {
        "path": f"{_Q4_ROOT}/Input/3dBPP_1.txt",
        "byte_count": 837,
        "sha256": "97d62d38f65dc23729cca2904232170f2c641150044974df244f27f5b77bee0e",
    },
    {
        "path": f"{_Q4_ROOT}/Input/3dBPP_3.txt",
        "byte_count": 837,
        "sha256": "c723c24d530ca61d9d0d67fff0ad8423761b66cfc071efb28ff8d487b6647034",
    },
    {
        "path": f"{_Q4_ROOT}/Input/3dBPP_5.txt",
        "byte_count": 838,
        "sha256": "78dfddd4f5370c753cb247d799b3ab66eb927a1788098ca15a6883024c330d3f",
    },
    {
        "path": f"{_Q4_ROOT}/Input/3dBPP_7.txt",
        "byte_count": 838,
        "sha256": "6e06fd72a8459c6a27706ec062cbd20556e2fff1b71e0f8e58c0ba1209564fac",
    },
)


class ExternalSolverBenchmarkCorpusError(SolverBenchmarkCorpusError):
    """Erreur fermée du manifest externe, de sa sélection ou de ses sources."""


def build_external_sealed_holdout(
    *,
    seed_base: int,
    split_offset: int,
    campaign_nonce: str,
) -> dict[str, object]:
    """Construit les recettes privées du holdout dans un sidecar non versionné."""

    if isinstance(seed_base, bool) or not isinstance(seed_base, int) or seed_base < 0:
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout seed base must be a non-negative integer."
        )
    if (
        isinstance(split_offset, bool)
        or not isinstance(split_offset, int)
        or split_offset < 0
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout split offset must be a non-negative integer."
        )
    if not _is_digest(campaign_nonce):
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout campaign nonce must contain 256 random bits."
        )
    records = build_generated_benchmark_case_records(
        case_id_prefix=EXTERNAL_CASE_ID_PREFIX,
        split_seed_bases={"holdout": seed_base},
        split_offsets={"holdout": split_offset},
        splits=("holdout",),
    )
    payload: dict[str, object] = {
        "schema_version": EXTERNAL_SOLVER_SEALED_HOLDOUT_SCHEMA_V2,
        "producer": {
            "id": EXTERNAL_SOLVER_BENCHMARK_PRODUCER_ID,
            "version": EXTERNAL_SOLVER_BENCHMARK_PRODUCER_VERSION,
        },
        "campaign_nonce": campaign_nonce,
        "seed_base": seed_base,
        "split_offset": split_offset,
        "case_records": records,
        "invariants": {
            "private_until_selection": True,
            "versioned_in_repository": False,
            "solver_invocation_count_at_build": 0,
        },
    }
    payload["sealed_holdout_digest"] = canonical_digest(payload)
    return _validate_external_sealed_holdout(payload)


def public_source_catalog() -> list[dict[str, object]]:
    """Retourne les deux sources publiques autorisées et leurs empreintes."""

    definitions: list[dict[str, object]] = [
        {
            "source_id": "orlib-thpack9",
            "authority": "OR-Library, J E Beasley",
            "dataset_title": "THPACK9 multiple-container loading instances",
            "dataset_page_url": (
                "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/thpackinfo.html"
            ),
            "download_url": (
                "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/"
                "thpack9.txt"
            ),
            "primary_publication": {
                "title": (
                    "An integer-programming based heuristic approach to the "
                    "three-dimensional packing problem"
                ),
                "authors": "Ivancic, Mathur and Mohanty",
                "year": 1989,
                "source_url": (
                    "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/"
                    "thpackinfo.html"
                ),
            },
            "license": {
                "spdx": "MIT",
                "scope": "all material available from OR-Library",
                "url": (
                    "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/legal.html"
                ),
                "redistribution": "allowed_with_notice",
            },
            "artifact": {
                "kind": "text",
                "byte_count": 3818,
                "sha256": (
                    "a4f5e3a748709217cdc749f7d27940f15b9f2a31b3e840e"
                    "725642237036f82cc"
                ),
                "selected_members": [],
            },
            "objective_mapping": {
                "original_objective": (
                    "minimize_identical_container_count_for_full_consignment"
                ),
                "bgig_projection": (
                    "fixed_container_count_all_items_feasibility_decision"
                ),
                "objective_correspondence": "exact_decision_reduction",
                "preserved_constraints": [
                    "all_items_required",
                    "container_dimensions",
                    "axis_aligned_cuboids",
                    "orientation_permissions",
                    "non_overlap",
                ],
                "constraints_absent_from_source": [
                    "bgig_full_support",
                    "bgig_removal_order",
                    "bgig_reservations",
                    "p45_local_variant_generation",
                ],
                "benchmark_role": "public_method_control_only",
                "product_ranking_eligible": False,
            },
            "verified_on": "2026-07-23",
        },
        {
            "source_id": "q4realbpp-v1",
            "authority": "Mendeley Data / Tecnalia",
            "dataset_title": (
                "Benchmark dataset and instance generator for Real-World 3dBPP"
            ),
            "dataset_page_url": "https://data.mendeley.com/datasets/y258s6d939/1",
            "download_url": (
                "https://data.mendeley.com/public-api/zip/"
                "y258s6d939/download/1"
            ),
            "primary_publication": {
                "title": (
                    "Benchmark dataset and instance generator for real-world "
                    "three-dimensional bin packing problems"
                ),
                "authors": "Osaba, Villar-Rodriguez and Romero",
                "year": 2023,
                "source_url": "https://doi.org/10.17632/y258s6d939.1",
            },
            "license": {
                "spdx": "GPL-3.0-only",
                "scope": "dataset version 1 and generator",
                "url": "https://www.gnu.org/licenses/gpl-3.0.html",
                "redistribution": "not_embedded_fetch_by_digest",
            },
            "artifact": {
                "kind": "zip",
                "byte_count": 12_201_414,
                "sha256": (
                    "dd3825b8abac54e04e748777d654065e176bb6ddf5e479c"
                    "beb638630fdb22fb4"
                ),
                "selected_members": list(_Q4_SELECTED_MEMBERS),
            },
            "objective_mapping": {
                "original_objective": (
                    "single_bin_all_items_feasibility_for_dimension_only_cases"
                ),
                "bgig_projection": "single_box_all_items_feasibility",
                "objective_correspondence": "exact_for_cases_1_3_5_7",
                "preserved_constraints": [
                    "all_items_required",
                    "single_bin_dimensions",
                    "axis_aligned_cuboids",
                    "six_axis_orientations",
                    "non_overlap",
                ],
                "constraints_absent_from_source": [
                    "bgig_full_support",
                    "bgig_removal_order",
                    "bgig_reservations",
                    "p45_local_variant_generation",
                ],
                "benchmark_role": "public_method_control_only",
                "product_ranking_eligible": False,
            },
            "verified_on": "2026-07-23",
        },
    ]
    result: list[dict[str, object]] = []
    for definition in definitions:
        item = deepcopy(definition)
        item["source_digest"] = canonical_digest(item)
        result.append(_validate_public_source_record(item))
    return result


def build_external_solver_benchmark_manifest(
    historical_l06_manifest: object,
    sealed_holdout: object,
) -> dict[str, object]:
    """Construit le manifest V2 sans exposer les recettes du holdout."""

    historical = validate_solver_benchmark_manifest(historical_l06_manifest)
    accepted_holdout = _validate_external_sealed_holdout(sealed_holdout)
    regression_sources = {
        str(item["source_id"]): item["corpus"]
        for item in historical["regression_corpora"]
    }
    baseline = {
        "source_manifest_schema": SOLVER_BENCHMARK_MANIFEST_SCHEMA_V1,
        "source_manifest_digest": historical["manifest_digest"],
        "source_holdout_commitment_digest": historical["holdout_policy"][
            "case_commitment_digest"
        ],
        "source_holdout_case_count": historical["holdout_policy"]["case_count"],
        "l06_holdout_status_for_l07": "consumed_open_regression_archive_only",
        "eligible_as_final_arbitrator": False,
        "answers_reused_for_l07_selection": False,
        "regression_corpus_digests": [
            item["corpus"]["corpus_digest"]
            for item in historical["regression_corpora"]
        ],
    }
    open_records = _build_open_generated_records()
    _validate_generated_partitions(
        [*open_records, *accepted_holdout["case_records"]]
    )
    return _build_external_solver_benchmark_manifest(
        regression_sources=regression_sources,
        historical_baseline=baseline,
        sealed_holdout_receipt=_build_sealed_holdout_receipt(accepted_holdout),
    )


def validate_external_solver_benchmark_manifest(
    manifest: object,
) -> dict[str, object]:
    """Valide le digest puis reconstruit tout le manifest V2."""

    payload = _mapping(manifest, "external solver benchmark manifest")
    if payload.get("schema_version") != EXTERNAL_SOLVER_BENCHMARK_MANIFEST_SCHEMA_V2:
        raise ExternalSolverBenchmarkCorpusError(
            "Unsupported external solver benchmark manifest schema."
        )
    supplied_digest = payload.pop("manifest_digest", None)
    if not _is_digest(supplied_digest):
        raise ExternalSolverBenchmarkCorpusError(
            "External solver benchmark manifest digest is missing."
        )
    if canonical_digest(payload) != supplied_digest:
        raise ExternalSolverBenchmarkCorpusError(
            "External solver benchmark manifest digest mismatch."
        )
    raw_regression = payload.get("regression_corpora")
    if not isinstance(raw_regression, list) or not raw_regression:
        raise ExternalSolverBenchmarkCorpusError(
            "External regression corpora must be a non-empty list."
        )
    regression_sources: dict[str, object] = {}
    for raw_item in raw_regression:
        item = _mapping(raw_item, "manifest.regression_corpora[]")
        source_id = _identifier(
            str(item.get("source_id", "")), "regression source id"
        )
        if source_id in regression_sources:
            raise ExternalSolverBenchmarkCorpusError(
                "Regression source identifiers must be unique."
            )
        regression_sources[source_id] = item.get("corpus")
    baseline = _validate_historical_baseline(payload.get("historical_baseline"))
    receipt = _validate_sealed_holdout_receipt(
        payload.get("sealed_holdout_receipt")
    )
    rebuilt = _build_external_solver_benchmark_manifest(
        regression_sources=regression_sources,
        historical_baseline=baseline,
        sealed_holdout_receipt=receipt,
    )
    candidate = deepcopy(dict(manifest))
    if rebuilt != candidate:
        raise ExternalSolverBenchmarkCorpusError(
            "External solver benchmark manifest is not canonical."
        )
    return rebuilt


def build_external_holdout_selection(
    *,
    primary_candidate_id: str,
    complementary_candidate_ids: Sequence[str],
    router_digest: str,
    candidate_bundle_digest: str,
    open_corpus_digest: str,
    settings_digest: str,
    total_budget_seconds: int,
) -> dict[str, object]:
    """Scelle un candidat seul ou un portefeuille avant le holdout L07."""

    if not isinstance(primary_candidate_id, str):
        raise ExternalSolverBenchmarkCorpusError(
            "Primary candidate id must be a string."
        )
    primary = _identifier(primary_candidate_id, "primary candidate id")
    if isinstance(complementary_candidate_ids, (str, bytes)):
        raise ExternalSolverBenchmarkCorpusError(
            "Complementary candidate ids must be a sequence."
        )
    complements: list[str] = []
    for value in complementary_candidate_ids:
        if not isinstance(value, str):
            raise ExternalSolverBenchmarkCorpusError(
                "Complementary candidate ids must be strings."
            )
        complements.append(_identifier(value, "complementary candidate id"))
    selected = [primary, *complements]
    if len(selected) > 3 or len(set(selected)) != len(selected):
        raise ExternalSolverBenchmarkCorpusError(
            "Holdout selection requires one to three distinct candidates."
        )
    digests = {
        "router_digest": router_digest,
        "candidate_bundle_digest": candidate_bundle_digest,
        "open_corpus_digest": open_corpus_digest,
        "settings_digest": settings_digest,
    }
    if any(not _is_digest(value) for value in digests.values()):
        raise ExternalSolverBenchmarkCorpusError(
            "Holdout selection digests must be SHA-256 values."
        )
    if (
        isinstance(total_budget_seconds, bool)
        or not isinstance(total_budget_seconds, int)
        or not 1 <= total_budget_seconds <= 36 * 60 * 60
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Holdout total budget must stay within 1 second and 36 hours."
        )
    selection: dict[str, object] = {
        "schema_version": EXTERNAL_SOLVER_HOLDOUT_SELECTION_SCHEMA_V2,
        "primary_candidate_id": primary,
        "complementary_candidate_ids": complements,
        "selected_candidate_ids": selected,
        "selected_candidate_count": len(selected),
        **digests,
        "total_budget_seconds": total_budget_seconds,
        "selected_before_holdout": True,
        "post_open_tuning_allowed": False,
    }
    selection["selection_digest"] = canonical_digest(selection)
    return selection


def materialize_external_benchmark_split(
    manifest: object,
    split: str,
    *,
    holdout_selection: object | None = None,
    sealed_holdout: object | None = None,
) -> list[dict[str, object]]:
    """Matérialise un split sans rendre le holdout reconstructible du manifest."""

    validated = validate_external_solver_benchmark_manifest(manifest)
    if split == "regression":
        return [
            deepcopy(case)
            for source in validated["regression_corpora"]
            for case in source["corpus"]["cases"]
        ]
    if split not in GENERATED_SPLITS:
        raise ExternalSolverBenchmarkCorpusError(
            "Unknown external benchmark split."
        )
    accepted_selection: dict[str, object] | None = None
    records = validated["bgig_generated_cases"]
    if split == "holdout":
        accepted_selection = _validate_external_holdout_selection(holdout_selection)
        _validate_selection_for_manifest(validated, accepted_selection)
        accepted_holdout = _validate_external_sealed_holdout(sealed_holdout)
        verify_external_sealed_holdout(validated, accepted_holdout)
        records = accepted_holdout["case_records"]
    return [
        _materialize_v2_case(record, accepted_selection=accepted_selection)
        for record in records
        if record["split"] == split
    ]


def open_external_holdout_cases(
    manifest: object,
    selection: object,
    sealed_holdout: object,
) -> dict[str, object]:
    """Ouvre le sidecar privé après une sélection complète et liée au manifest."""

    validated = validate_external_solver_benchmark_manifest(manifest)
    accepted = _validate_external_holdout_selection(selection)
    _validate_selection_for_manifest(validated, accepted)
    accepted_holdout = _validate_external_sealed_holdout(sealed_holdout)
    verify_external_sealed_holdout(validated, accepted_holdout)
    cases = [
        _materialize_v2_case(record, accepted_selection=accepted)
        for record in accepted_holdout["case_records"]
    ]
    return {
        "selection": accepted,
        "manifest_digest": validated["manifest_digest"],
        "sealed_holdout_digest": accepted_holdout["sealed_holdout_digest"],
        "holdout_commitment_digest": validated["holdout_policy"][
            "case_commitment_digest"
        ],
        "cases": cases,
        "opening_digest": canonical_digest(
            {
                "selection_digest": accepted["selection_digest"],
                "manifest_digest": validated["manifest_digest"],
                "case_ids": [case["case_id"] for case in cases],
            }
        ),
        "invariants": {"post_open_tuning_allowed": False},
    }


def verify_external_sealed_holdout(
    manifest: object,
    sealed_holdout: object,
) -> dict[str, object]:
    """Vérifie le sidecar contre le reçu public sans exposer ses recettes."""

    validated = validate_external_solver_benchmark_manifest(manifest)
    accepted = _validate_external_sealed_holdout(sealed_holdout)
    receipt = _build_sealed_holdout_receipt(accepted)
    if receipt != validated["sealed_holdout_receipt"]:
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout does not match the public manifest receipt."
        )
    _validate_generated_partitions(
        [*validated["bgig_generated_cases"], *accepted["case_records"]]
    )
    return {
        "status": "verified",
        "sealed_holdout_digest": accepted["sealed_holdout_digest"],
        "case_commitment_digest": receipt["case_commitment_digest"],
        "case_count": receipt["case_count"],
        "private_recipe_count": receipt["case_count"],
        "solver_invocation_count": 0,
    }


def verify_downloaded_public_source(
    source: object,
    artifact_path: Path,
) -> dict[str, object]:
    """Vérifie taille, empreinte et membres sélectionnés d'une source."""

    validated = _validate_public_source_record(source)
    path = Path(artifact_path)
    if not path.is_file():
        raise ExternalSolverBenchmarkCorpusError(
            "Downloaded public source artifact is missing."
        )
    artifact = _mapping(validated["artifact"], "public source artifact")
    size = path.stat().st_size
    if size != artifact["byte_count"]:
        raise ExternalSolverBenchmarkCorpusError(
            "Downloaded public source byte count mismatch."
        )
    digest = _sha256_path(path)
    if digest != artifact["sha256"]:
        raise ExternalSolverBenchmarkCorpusError(
            "Downloaded public source digest mismatch."
        )
    verified_members: list[dict[str, object]] = []
    if artifact["kind"] == "zip":
        try:
            with ZipFile(path) as archive:
                for raw_member in artifact["selected_members"]:
                    member = _mapping(raw_member, "public source selected member")
                    try:
                        info = archive.getinfo(str(member["path"]))
                    except KeyError as error:
                        raise ExternalSolverBenchmarkCorpusError(
                            "Downloaded public source member is missing."
                        ) from error
                    if info.file_size != member["byte_count"]:
                        raise ExternalSolverBenchmarkCorpusError(
                            "Downloaded public source member byte count mismatch."
                        )
                    with archive.open(info) as stream:
                        member_digest = _sha256_stream(stream)
                    if member_digest != member["sha256"]:
                        raise ExternalSolverBenchmarkCorpusError(
                            "Downloaded public source member digest mismatch."
                        )
                    verified_members.append(
                        {
                            "path": member["path"],
                            "byte_count": info.file_size,
                            "sha256": member_digest,
                        }
                    )
        except BadZipFile as error:
            raise ExternalSolverBenchmarkCorpusError(
                "Downloaded public source is not a valid ZIP archive."
            ) from error
    return {
        "status": "verified",
        "source_id": validated["source_id"],
        "artifact_byte_count": size,
        "artifact_sha256": digest,
        "selected_members": verified_members,
        "source_digest": validated["source_digest"],
    }


def _build_external_solver_benchmark_manifest(
    *,
    regression_sources: Mapping[str, object],
    historical_baseline: object,
    sealed_holdout_receipt: object,
) -> dict[str, object]:
    if not regression_sources:
        raise ExternalSolverBenchmarkCorpusError(
            "At least one external regression corpus is required."
        )
    baseline = _validate_historical_baseline(historical_baseline)
    regression: list[dict[str, object]] = []
    for source_id, raw_corpus in sorted(
        regression_sources.items(), key=lambda item: str(item[0])
    ):
        identifier = _identifier(str(source_id), "regression source id")
        corpus = validate_solver_case_corpus(raw_corpus)
        regression.append({"source_id": identifier, "corpus": corpus})
    regression_digests = [
        item["corpus"]["corpus_digest"] for item in regression
    ]
    if regression_digests != baseline["regression_corpus_digests"]:
        raise ExternalSolverBenchmarkCorpusError(
            "L07 regression corpora must match the preserved L06 sources."
        )

    generated = _build_open_generated_records()
    _validate_open_generated_partitions(generated)
    receipt = _validate_sealed_holdout_receipt(sealed_holdout_receipt)
    exact_controls = _build_small_exact_controls(generated)
    sources = public_source_catalog()
    public_controls = _build_public_method_controls(sources)
    open_corpus_digest = canonical_digest(
        {
            "regression_corpus_digests": regression_digests,
            "bgig_generated_cases": generated,
            "public_method_controls": public_controls,
            "small_exact_controls": exact_controls,
        }
    )
    manifest: dict[str, object] = {
        "schema_version": EXTERNAL_SOLVER_BENCHMARK_MANIFEST_SCHEMA_V2,
        "producer": {
            "id": EXTERNAL_SOLVER_BENCHMARK_PRODUCER_ID,
            "version": EXTERNAL_SOLVER_BENCHMARK_PRODUCER_VERSION,
        },
        "historical_baseline": baseline,
        "regression_corpora": regression,
        "bgig_generated_cases": generated,
        "sealed_holdout_receipt": receipt,
        "open_corpus_digest": open_corpus_digest,
        "public_sources": sources,
        "public_method_controls": public_controls,
        "small_exact_controls": exact_controls,
        "matrix": {
            "contents_per_container_targets": [1, 2, 4, 8, 16, 32],
            "retained_variant_targets": [1, 2, 4, 8],
            "container_group_targets": [2, 4, 8, 12, 18, 30, 50],
            "layer_targets": [1, 2, 3],
            "density_targets": ["ample", "dense", "nearly_saturated"],
            "reservation_targets": ["absent", "constraining"],
            "rotation_policy_targets": [
                "forbidden_by_benchmark",
                "permitted",
            ],
            "execution_modes": ["cold", "incremental"],
            "families": list(FAMILIES),
        },
        "split_policy": {
            "splits": ["regression", *GENERATED_SPLITS],
            "generated_seed_bases": deepcopy(EXTERNAL_SPLIT_SEED_BASES),
            "generated_split_offsets": deepcopy(EXTERNAL_SPLIT_OFFSETS),
            "cross_split_case_id_overlap_count": 0,
            "cross_split_seed_overlap_count": 0,
            "cross_split_project_digest_overlap_count": 0,
            "cross_split_previous_project_digest_overlap_count": 0,
            "permutation_derivative_cross_split_count": 0,
            "public_holdout_case_count": 0,
            "public_cases_with_lost_constraints_product_ranked": 0,
        },
        "holdout_policy": {
            "status": "sealed_private_sidecar",
            "case_count": receipt["case_count"],
            "case_commitment_digest": receipt["case_commitment_digest"],
            "sealed_holdout_digest": receipt["sealed_holdout_digest"],
            "recipes_embedded_in_manifest": False,
            "seed_material_embedded_in_manifest": False,
            "independent_from_l06": True,
            "single_opening_after_selection": True,
            "selected_candidate_minimum": 1,
            "selected_candidate_maximum": 3,
            "post_open_tuning_allowed": False,
            "new_iteration_requires_new_manifest": True,
            "solver_invocation_count_at_build": 0,
        },
        "summary": {
            "regression_corpus_count": len(regression),
            "regression_case_count": sum(
                int(item["corpus"]["summary"]["case_count"])
                for item in regression
            ),
            "bgig_generated_case_count": (
                len(generated) + int(receipt["case_count"])
            ),
            "open_bgig_generated_case_count": len(generated),
            "discovery_case_count": GENERATED_CASES_PER_SPLIT,
            "tuning_case_count": GENERATED_CASES_PER_SPLIT,
            "holdout_case_count": receipt["case_count"],
            "public_source_count": len(sources),
            "public_method_control_count": len(public_controls),
            "small_exact_control_count": len(exact_controls),
        },
        "invariants": {
            "historical_regression_digests_preserved": True,
            "l06_holdout_not_final_arbitrator": True,
            "new_holdout_closed_by_default": True,
            "new_holdout_solver_invocation_count": 0,
            "holdout_recipe_records_embedded": False,
            "holdout_seed_material_embedded": False,
            "public_source_artifacts_embedded": False,
            "public_cases_product_ranking_eligible": False,
            "product_ranking_requires_bgig_recertification": True,
            "t0_t1_only": True,
            "t2_t4_case_count": 0,
            "external_dependency_count_at_build": 0,
            "finalization_invocation_count": 0,
            "cad_build_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
            "personal_project_paths_embedded": False,
        },
    }
    _reject_secret_keys(manifest)
    manifest["manifest_digest"] = canonical_digest(manifest)
    return manifest


def _build_open_generated_records() -> list[dict[str, object]]:
    return build_generated_benchmark_case_records(
        case_id_prefix=EXTERNAL_CASE_ID_PREFIX,
        split_seed_bases=EXTERNAL_SPLIT_SEED_BASES,
        split_offsets=EXTERNAL_SPLIT_OFFSETS,
        splits=EXTERNAL_OPEN_SPLITS,
    )


def _build_small_exact_controls(
    generated: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    controls: list[dict[str, object]] = []
    for split in ("discovery", "tuning"):
        records = [record for record in generated if record["split"] == split]
        for oracle_kind in (
            FEASIBLE_BY_CONSTRUCTION,
            PROVEN_IMPOSSIBLE_SMALL_EXACT,
        ):
            selected = next(
                (
                    record
                    for record in records
                    if record["recipe"]["oracle_kind"] == oracle_kind
                    and int(record["features"]["container_group_count"]) <= 4
                ),
                None,
            )
            if selected is None:
                raise ExternalSolverBenchmarkCorpusError(
                    "Each open split needs small positive and negative controls."
                )
            case = materialize_generated_benchmark_case(selected)
            controls.append(
                {
                    "case_id": case["case_id"],
                    "split": split,
                    "family": case["family"],
                    "project_digest": case["project_digest"],
                    "oracle_digest": case["oracle_digest"],
                    "oracle_kind": oracle_kind,
                    "expected_truth": case["oracle"]["expected_truth"],
                    "container_group_count": case["features"][
                        "container_group_count"
                    ],
                    "verification": (
                        "constructed_positive_witness"
                        if oracle_kind == FEASIBLE_BY_CONSTRUCTION
                        else str(case["oracle"]["proof"]["kind"])
                    ),
                    "supplied_to_tested_solver": False,
                }
            )
    return controls


def _build_public_method_controls(
    sources: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    source_digests = {
        str(source["source_id"]): str(source["source_digest"])
        for source in sources
    }
    controls = [
        ("orlib-thpack9-001", "orlib-thpack9", "instance-001", "discovery"),
        ("orlib-thpack9-002", "orlib-thpack9", "instance-002", "tuning"),
        ("orlib-thpack9-003", "orlib-thpack9", "instance-003", "discovery"),
        ("orlib-thpack9-004", "orlib-thpack9", "instance-004", "tuning"),
        ("q4realbpp-1", "q4realbpp-v1", "Input/3dBPP_1.txt", "discovery"),
        ("q4realbpp-3", "q4realbpp-v1", "Input/3dBPP_3.txt", "tuning"),
        ("q4realbpp-5", "q4realbpp-v1", "Input/3dBPP_5.txt", "discovery"),
        ("q4realbpp-7", "q4realbpp-v1", "Input/3dBPP_7.txt", "tuning"),
    ]
    return [
        {
            "case_id": case_id,
            "source_id": source_id,
            "source_case_id": source_case_id,
            "split": split,
            "source_digest": source_digests[source_id],
            "objective_correspondence": (
                "exact_decision_reduction"
                if source_id == "orlib-thpack9"
                else "exact_single_bin_feasibility"
            ),
            "benchmark_role": "public_method_control_only",
            "product_ranking_eligible": False,
            "holdout_eligible": False,
            "requires_source_fetch_and_digest_verification": True,
        }
        for case_id, source_id, source_case_id, split in controls
    ]


def _validate_generated_partitions(
    generated: Sequence[Mapping[str, object]],
) -> None:
    _validate_partition_set(generated, GENERATED_SPLITS)


def _validate_open_generated_partitions(
    generated: Sequence[Mapping[str, object]],
) -> None:
    _validate_partition_set(generated, EXTERNAL_OPEN_SPLITS)


def _validate_partition_set(
    generated: Sequence[Mapping[str, object]],
    expected_splits: Sequence[str],
) -> None:
    if len(generated) != len(expected_splits) * GENERATED_CASES_PER_SPLIT:
        raise ExternalSolverBenchmarkCorpusError(
            "Generated V2 campaign has the wrong case count."
        )
    by_split = {
        split: [record for record in generated if record["split"] == split]
        for split in expected_splits
    }
    if any(
        len(records) != GENERATED_CASES_PER_SPLIT
        for records in by_split.values()
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Every V2 generated split must contain 64 cases."
        )
    for split, records in by_split.items():
        if {record["family"] for record in records} != set(FAMILIES):
            raise ExternalSolverBenchmarkCorpusError(
                f"Generated V2 split {split} misses a required family."
            )
    fields = ("case_id", "seed", "project_digest", "previous_project_digest")
    for field in fields:
        split_values = {
            split: {
                record[field]
                for record in records
                if record.get(field) is not None
            }
            for split, records in by_split.items()
        }
        for index, first in enumerate(expected_splits):
            for second in expected_splits[index + 1 :]:
                if split_values[first] & split_values[second]:
                    raise ExternalSolverBenchmarkCorpusError(
                        f"Generated V2 {field} leaks between splits."
                    )


def _validate_historical_baseline(value: object) -> dict[str, object]:
    baseline = _mapping(value, "historical baseline")
    if baseline.get("source_manifest_schema") != SOLVER_BENCHMARK_MANIFEST_SCHEMA_V1:
        raise ExternalSolverBenchmarkCorpusError(
            "Historical baseline must reference the L06 V1 schema."
        )
    for field in (
        "source_manifest_digest",
        "source_holdout_commitment_digest",
    ):
        if not _is_digest(baseline.get(field)):
            raise ExternalSolverBenchmarkCorpusError(
                f"Historical baseline {field} is invalid."
            )
    if baseline.get("source_holdout_case_count") != GENERATED_CASES_PER_SPLIT:
        raise ExternalSolverBenchmarkCorpusError(
            "Historical L06 holdout case count mismatch."
        )
    if (
        baseline.get("l06_holdout_status_for_l07")
        != "consumed_open_regression_archive_only"
        or baseline.get("eligible_as_final_arbitrator") is not False
        or baseline.get("answers_reused_for_l07_selection") is not False
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Historical L06 holdout must remain excluded from L07 selection."
        )
    digests = baseline.get("regression_corpus_digests")
    if (
        not isinstance(digests, list)
        or not digests
        or any(not _is_digest(digest) for digest in digests)
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Historical regression corpus digests are invalid."
        )
    return deepcopy(baseline)


def _build_sealed_holdout_receipt(
    sealed_holdout: Mapping[str, object],
) -> dict[str, object]:
    records = sealed_holdout["case_records"]
    return {
        "schema_version": EXTERNAL_SOLVER_HOLDOUT_RECEIPT_SCHEMA_V2,
        "sealed_holdout_schema": EXTERNAL_SOLVER_SEALED_HOLDOUT_SCHEMA_V2,
        "sealed_holdout_digest": sealed_holdout["sealed_holdout_digest"],
        "case_commitment_digest": canonical_digest(records),
        "case_count": len(records),
        "family_count": len({record["family"] for record in records}),
        "private_recipe_count": len(records),
        "solver_invocation_count_at_seal": 0,
    }


def _validate_sealed_holdout_receipt(value: object) -> dict[str, object]:
    receipt = _mapping(value, "sealed holdout receipt")
    if (
        receipt.get("schema_version")
        != EXTERNAL_SOLVER_HOLDOUT_RECEIPT_SCHEMA_V2
        or receipt.get("sealed_holdout_schema")
        != EXTERNAL_SOLVER_SEALED_HOLDOUT_SCHEMA_V2
        or not _is_digest(receipt.get("sealed_holdout_digest"))
        or not _is_digest(receipt.get("case_commitment_digest"))
        or receipt.get("case_count") != GENERATED_CASES_PER_SPLIT
        or receipt.get("family_count") != len(FAMILIES)
        or receipt.get("private_recipe_count") != GENERATED_CASES_PER_SPLIT
        or receipt.get("solver_invocation_count_at_seal") != 0
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout receipt is invalid."
        )
    return receipt


def _validate_external_sealed_holdout(value: object) -> dict[str, object]:
    sealed = _mapping(value, "sealed holdout sidecar")
    supplied_digest = sealed.pop("sealed_holdout_digest", None)
    if (
        sealed.get("schema_version") != EXTERNAL_SOLVER_SEALED_HOLDOUT_SCHEMA_V2
        or not _is_digest(supplied_digest)
        or canonical_digest(sealed) != supplied_digest
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout sidecar digest or schema is invalid."
        )
    producer = _mapping(sealed.get("producer"), "sealed holdout producer")
    if producer != {
        "id": EXTERNAL_SOLVER_BENCHMARK_PRODUCER_ID,
        "version": EXTERNAL_SOLVER_BENCHMARK_PRODUCER_VERSION,
    }:
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout producer is invalid."
        )
    seed_base = sealed.get("seed_base")
    split_offset = sealed.get("split_offset")
    if (
        isinstance(seed_base, bool)
        or not isinstance(seed_base, int)
        or seed_base < 0
        or isinstance(split_offset, bool)
        or not isinstance(split_offset, int)
        or split_offset < 0
        or not _is_digest(sealed.get("campaign_nonce"))
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout private recipe is invalid."
        )
    rebuilt = build_generated_benchmark_case_records(
        case_id_prefix=EXTERNAL_CASE_ID_PREFIX,
        split_seed_bases={"holdout": seed_base},
        split_offsets={"holdout": split_offset},
        splits=("holdout",),
    )
    if sealed.get("case_records") != rebuilt:
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout case records are not canonical."
        )
    invariants = _mapping(
        sealed.get("invariants"), "sealed holdout invariants"
    )
    if invariants != {
        "private_until_selection": True,
        "versioned_in_repository": False,
        "solver_invocation_count_at_build": 0,
    }:
        raise ExternalSolverBenchmarkCorpusError(
            "Sealed holdout invariants are invalid."
        )
    sealed["sealed_holdout_digest"] = supplied_digest
    _reject_secret_keys(sealed, "sealed_holdout")
    return sealed


def _validate_selection_for_manifest(
    manifest: Mapping[str, object],
    selection: Mapping[str, object],
) -> None:
    if selection["open_corpus_digest"] != manifest["open_corpus_digest"]:
        raise ExternalSolverBenchmarkCorpusError(
            "Holdout selection is not bound to this open corpus."
        )


def _validate_public_source_record(value: object) -> dict[str, object]:
    source = _mapping(value, "public source")
    supplied_digest = source.pop("source_digest", None)
    if not _is_digest(supplied_digest) or canonical_digest(source) != supplied_digest:
        raise ExternalSolverBenchmarkCorpusError("Public source digest mismatch.")
    _identifier(str(source.get("source_id", "")), "public source id")
    license_record = _mapping(source.get("license"), "public source license")
    if license_record.get("spdx") not in {"MIT", "GPL-3.0-only"}:
        raise ExternalSolverBenchmarkCorpusError(
            "Public source license is unsupported."
        )
    artifact = _mapping(source.get("artifact"), "public source artifact")
    if artifact.get("kind") not in {"text", "zip"}:
        raise ExternalSolverBenchmarkCorpusError(
            "Public source artifact kind is unsupported."
        )
    if (
        isinstance(artifact.get("byte_count"), bool)
        or not isinstance(artifact.get("byte_count"), int)
        or not 1 <= artifact["byte_count"] <= MAX_PUBLIC_SOURCE_BYTES
        or not _is_digest(artifact.get("sha256"))
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Public source artifact size or digest is invalid."
        )
    members = artifact.get("selected_members")
    if not isinstance(members, list):
        raise ExternalSolverBenchmarkCorpusError(
            "Public source selected members must be a list."
        )
    for raw_member in members:
        member = _mapping(raw_member, "public source selected member")
        _identifier(str(member.get("path", "")).replace("/", "-"), "member path")
        if (
            isinstance(member.get("byte_count"), bool)
            or not isinstance(member.get("byte_count"), int)
            or member["byte_count"] < 1
            or not _is_digest(member.get("sha256"))
        ):
            raise ExternalSolverBenchmarkCorpusError(
                "Public source selected member metadata is invalid."
            )
    objective = _mapping(
        source.get("objective_mapping"), "public source objective mapping"
    )
    if (
        objective.get("benchmark_role") != "public_method_control_only"
        or objective.get("product_ranking_eligible") is not False
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Public sources cannot enter the BGIG product ranking."
        )
    source["source_digest"] = supplied_digest
    return deepcopy(source)


def _validate_external_holdout_selection(value: object) -> dict[str, object]:
    selection = _mapping(value, "external holdout selection")
    supplied_digest = selection.pop("selection_digest", None)
    if (
        selection.get("schema_version")
        != EXTERNAL_SOLVER_HOLDOUT_SELECTION_SCHEMA_V2
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "Unsupported external holdout selection schema."
        )
    if not _is_digest(supplied_digest) or canonical_digest(selection) != supplied_digest:
        raise ExternalSolverBenchmarkCorpusError(
            "External holdout selection digest mismatch."
        )
    selected = selection.get("selected_candidate_ids")
    complements = selection.get("complementary_candidate_ids")
    primary = selection.get("primary_candidate_id")
    if (
        not isinstance(selected, list)
        or not isinstance(complements, list)
        or not isinstance(primary, str)
        or any(not isinstance(value, str) for value in selected)
        or any(not isinstance(value, str) for value in complements)
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "External holdout candidate lists are invalid."
        )
    if (
        not 1 <= len(selected) <= 3
        or len(set(str(value) for value in selected)) != len(selected)
        or selection.get("selected_candidate_count") != len(selected)
        or selected[0] != selection.get("primary_candidate_id")
        or selected[1:] != complements
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "External holdout candidate selection is inconsistent."
        )
    for candidate_id in selected:
        _identifier(str(candidate_id), "selected candidate id")
    for field in (
        "router_digest",
        "candidate_bundle_digest",
        "open_corpus_digest",
        "settings_digest",
    ):
        if not _is_digest(selection.get(field)):
            raise ExternalSolverBenchmarkCorpusError(
                f"External holdout selection {field} is invalid."
            )
    budget = selection.get("total_budget_seconds")
    if (
        isinstance(budget, bool)
        or not isinstance(budget, int)
        or not 1 <= budget <= 36 * 60 * 60
        or selection.get("selected_before_holdout") is not True
        or selection.get("post_open_tuning_allowed") is not False
    ):
        raise ExternalSolverBenchmarkCorpusError(
            "External holdout timing or sealing policy is invalid."
        )
    selection["selection_digest"] = supplied_digest
    return deepcopy(selection)


def _materialize_v2_case(
    record: Mapping[str, object],
    *,
    accepted_selection: Mapping[str, object] | None,
) -> dict[str, object]:
    if record["split"] != "holdout":
        return materialize_generated_benchmark_case(record)
    if accepted_selection is None:
        raise ExternalSolverBenchmarkCorpusError(
            "External holdout selection is required."
        )
    bridge = build_holdout_selection(
        "p64-l07-v2-selection",
        str(accepted_selection["selection_digest"]),
    )
    return materialize_generated_benchmark_case(
        record,
        holdout_selection=bridge,
    )


def _sha256_path(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_stream(stream: BinaryIO) -> str:
    digest = sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _identifier(value: str, field: str) -> str:
    result = str(value).strip()
    if (
        not result
        or len(result) > 256
        or any(separator in result for separator in ("/", "\\"))
    ):
        raise ExternalSolverBenchmarkCorpusError(
            f"{field} must be a portable identifier."
        )
    return result


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ExternalSolverBenchmarkCorpusError(f"{field} must be an object.")
    return deepcopy(dict(value))


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
                raise ExternalSolverBenchmarkCorpusError(
                    f"Secret-like key is forbidden in benchmark manifest: "
                    f"{path}.{raw_key}."
                )
            _reject_secret_keys(item, f"{path}.{raw_key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_secret_keys(item, f"{path}[{index}]")
