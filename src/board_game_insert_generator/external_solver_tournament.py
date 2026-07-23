"""Contrat reproductible du tournoi externe P64-L07D.

Le module ne lance aucun binaire. Il valide la configuration, résume les
rapports déjà recertifiés par BGIG, compare les candidats sur une portée
commune et construit la sélection immuable exigée avant le holdout.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from math import ceil, isfinite
from pathlib import Path
import re
from typing import Mapping, Sequence
from zipfile import ZipFile

from .external_solver_artifacts import (
    external_solver_candidate_catalog,
    validate_external_solver_artifact_lock,
)
from .external_solver_benchmark_corpus import (
    build_external_holdout_selection,
    validate_external_solver_benchmark_manifest,
    verify_downloaded_public_source,
)
from .incremental_project_state import canonical_digest


EXTERNAL_TOURNAMENT_CONFIG_SCHEMA_V1 = (
    "bgig.external_solver_tournament_config.v1"
)
EXTERNAL_TOURNAMENT_STAGE_SUMMARY_SCHEMA_V1 = (
    "bgig.external_solver_tournament_stage_summary.v1"
)
EXTERNAL_TOURNAMENT_TUNING_SUMMARY_SCHEMA_V1 = (
    "bgig.external_solver_tournament_tuning_summary.v1"
)
EXTERNAL_TOURNAMENT_SELECTION_EVIDENCE_SCHEMA_V1 = (
    "bgig.external_solver_tournament_selection_evidence.v1"
)
EXTERNAL_TOURNAMENT_PUBLIC_EVIDENCE_SCHEMA_V1 = (
    "bgig.external_solver_public_method_evidence.v1"
)

_QUALITY_FIELDS = (
    "cluster_volume_mm3",
    "internal_gap_mm3",
    "cluster_height_mm",
    "cluster_footprint_mm2",
    "residual_fragmentation",
    "contact_count",
    "minimum_support_ratio",
)
_CANDIDATE_FAILURE_STATUSES = {
    "certificate_rejected",
    "external_error",
}
_EXPECTED_TRUTHS = {"feasible", "impossible", "regression_open"}
_Q4_BIN_PATTERN = re.compile(
    r"Bin dimensions \(L \* W \* H\): "
    r"\((\d+),\s*(\d+),\s*(\d+)\)"
)


class ExternalSolverTournamentError(ValueError):
    """Configuration ou preuve L07D incohérente."""


def validate_external_tournament_config(
    value: object,
) -> dict[str, object]:
    """Valide la règle de tournoi annoncée avant la première mesure."""

    config = _mapping(value, "external tournament config")
    supplied_digest = config.pop("config_digest", None)
    if (
        config.get("schema_version")
        != EXTERNAL_TOURNAMENT_CONFIG_SCHEMA_V1
        or not _is_digest(supplied_digest)
        or canonical_digest(config) != supplied_digest
    ):
        raise ExternalSolverTournamentError(
            "External tournament config schema or digest mismatch."
        )
    candidate_ids = config.get("candidate_ids")
    if (
        not isinstance(candidate_ids, list)
        or len(candidate_ids) < 3
        or len(candidate_ids) != len(set(candidate_ids))
        or any(not isinstance(item, str) or not item for item in candidate_ids)
    ):
        raise ExternalSolverTournamentError(
            "External tournament needs at least three distinct candidates."
        )
    stages = _mapping(config.get("stages"), "external tournament stages")
    for stage in ("exact_controls", "regression", "discovery", "holdout"):
        _validate_limits(
            _mapping(stages.get(stage), f"external tournament stage {stage}")
        )
    tuning_trials = stages.get("tuning_trials")
    if (
        not isinstance(tuning_trials, list)
        or not 2 <= len(tuning_trials) <= 4
    ):
        raise ExternalSolverTournamentError(
            "External tournament tuning must announce two to four trials."
        )
    trial_ids: set[str] = set()
    for raw_trial in tuning_trials:
        trial = _mapping(raw_trial, "external tournament tuning trial")
        trial_id = trial.get("trial_id")
        if (
            not isinstance(trial_id, str)
            or not trial_id
            or trial_id in trial_ids
        ):
            raise ExternalSolverTournamentError(
                "External tournament tuning trial ids must be distinct."
            )
        trial_ids.add(trial_id)
        _validate_limits(trial)
    ranking = _mapping(config.get("ranking"), "external tournament ranking")
    if (
        ranking.get("quality_contract")
        != "bgig.minimal_layout_lexicographic.v1"
        or ranking.get("invalid_output_policy") != "fail_closed"
        or ranking.get("unsupported_policy")
        != "excluded_from_quality_but_counted_in_coverage"
        or ranking.get("public_method_controls_product_ranked") is not False
    ):
        raise ExternalSolverTournamentError(
            "External tournament ranking contract changed."
        )
    portfolio = _mapping(
        config.get("portfolio_policy"), "external tournament portfolio policy"
    )
    if (
        portfolio.get("maximum_candidate_count") != 3
        or portfolio.get("one_engine_invocation_per_case") is not True
        or portfolio.get("distinct_family_gain_required") is not True
        or portfolio.get("must_beat_best_single") is not True
    ):
        raise ExternalSolverTournamentError(
            "External tournament portfolio policy changed."
        )
    config["config_digest"] = supplied_digest
    return deepcopy(config)


def summarize_external_tournament_stage(
    stage: str,
    rows: Sequence[Mapping[str, object]],
    *,
    artifact_lock: object,
    candidate_ids: Sequence[str],
) -> dict[str, object]:
    """Agrège une étape sans croire les sorties positives sur parole."""

    lock = validate_external_solver_artifact_lock(artifact_lock)
    catalog = {
        str(item["candidate_id"]): item
        for item in external_solver_candidate_catalog(lock)
    }
    expected_ids = tuple(str(item) for item in candidate_ids)
    if (
        len(expected_ids) < 3
        or len(expected_ids) != len(set(expected_ids))
        or any(candidate_id not in catalog for candidate_id in expected_ids)
    ):
        raise ExternalSolverTournamentError(
            "External tournament candidate set does not match the lock."
        )
    normalized = [
        _validate_result_row(row, expected_ids) for row in rows
    ]
    if not normalized:
        raise ExternalSolverTournamentError(
            "External tournament stage cannot be empty."
        )
    result_keys = [
        (
            str(row["candidate_id"]),
            str(row["case_id"]),
            str(row["trial_id"]),
        )
        for row in normalized
    ]
    if len(result_keys) != len(set(result_keys)):
        raise ExternalSolverTournamentError(
            "External tournament stage contains duplicate executions."
        )
    by_candidate: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_case_trial: dict[
        tuple[str, str], dict[str, dict[str, object]]
    ] = defaultdict(dict)
    for row in normalized:
        candidate_id = str(row["candidate_id"])
        by_candidate[candidate_id].append(row)
        by_case_trial[
            (str(row["case_id"]), str(row["trial_id"]))
        ][candidate_id] = row
    expected_case_trials = {
        (str(row["case_id"]), str(row["trial_id"])) for row in normalized
    }
    for candidate_id in expected_ids:
        observed = {
            (str(row["case_id"]), str(row["trial_id"]))
            for row in by_candidate[candidate_id]
        }
        if observed != expected_case_trials:
            raise ExternalSolverTournamentError(
                "Candidates did not receive the same stage inputs."
            )

    quality_counts = {
        candidate_id: {"wins": 0, "losses": 0, "ties": 0}
        for candidate_id in expected_ids
    }
    for candidates in by_case_trial.values():
        for first_index, first_id in enumerate(expected_ids):
            for second_id in expected_ids[first_index + 1 :]:
                first_axes = _quality_axes(candidates[first_id]["report"])
                second_axes = _quality_axes(candidates[second_id]["report"])
                if first_axes is None or second_axes is None:
                    continue
                if first_axes < second_axes:
                    quality_counts[first_id]["wins"] += 1
                    quality_counts[second_id]["losses"] += 1
                elif second_axes < first_axes:
                    quality_counts[second_id]["wins"] += 1
                    quality_counts[first_id]["losses"] += 1
                else:
                    quality_counts[first_id]["ties"] += 1
                    quality_counts[second_id]["ties"] += 1

    summaries = []
    for candidate_id in expected_ids:
        candidate_rows = by_candidate[candidate_id]
        statuses: dict[str, int] = defaultdict(int)
        family_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        total_wall = 0.0
        total_cpu = 0.0
        peak_bytes = 0
        worker_invocations = 0
        oracle_count = 0
        oracle_passes = 0
        certified = 0
        representable = 0
        for row in candidate_rows:
            report = _mapping(row["report"], "external tournament report")
            status = str(report.get("status", ""))
            family = str(row["family"])
            statuses[status] += 1
            family_counts[family][status] += 1
            if report.get("model") is not None:
                representable += 1
            recertification = _mapping_or_empty(report.get("recertification"))
            if (
                status == "solution_found"
                and recertification.get("certified") is True
            ):
                certified += 1
            expected_truth = str(row["expected_truth"])
            if (
                expected_truth != "regression_open"
                and report.get("model") is not None
            ):
                oracle_count += 1
                if _truth_matches(expected_truth, status):
                    oracle_passes += 1
            timing = _mapping_or_empty(report.get("timing"))
            resources = _mapping_or_empty(report.get("resources"))
            total_wall += _finite_non_negative(
                timing.get("total_wall_seconds")
            )
            total_cpu += _finite_non_negative(resources.get("cpu_seconds"))
            peak_bytes = max(
                peak_bytes,
                int(resources.get("peak_working_set_bytes") or 0),
            )
            invariants = _mapping_or_empty(report.get("invariants"))
            worker_invocations += int(
                invariants.get(
                    "external_worker_invocation_count",
                    invariants.get("worker_invocation_count", 0),
                )
                or 0
            )
        failure_count = sum(
            statuses.get(status, 0)
            for status in _CANDIDATE_FAILURE_STATUSES
        )
        quality = quality_counts[candidate_id]
        candidate = catalog[candidate_id]
        bundle_byte_count = sum(
            int(artifact["byte_count"])
            for artifact in lock["artifacts"]
            if artifact["candidate_id"] == candidate_id
        )
        summary = {
            "candidate_id": candidate_id,
            "family": candidate["family"],
            "version": candidate["version"],
            "product_gate": candidate["product_gate"],
            "result_count": len(candidate_rows),
            "case_count": len(
                {str(row["case_id"]) for row in candidate_rows}
            ),
            "trial_count": len(
                {str(row["trial_id"]) for row in candidate_rows}
            ),
            "representable_count": representable,
            "worker_invocation_count": worker_invocations,
            "certified_solution_count": certified,
            "oracle_evaluable_count": oracle_count,
            "oracle_pass_count": oracle_passes,
            "oracle_miss_count": oracle_count - oracle_passes,
            "candidate_failure_count": failure_count,
            "statuses": dict(sorted(statuses.items())),
            "families": {
                family: dict(sorted(counts.items()))
                for family, counts in sorted(family_counts.items())
            },
            "quality_pairwise": deepcopy(quality),
            "resources": {
                "total_wall_seconds": round(total_wall, 6),
                "total_cpu_seconds": round(total_cpu, 6),
                "peak_working_set_bytes": peak_bytes or None,
                "bundle_byte_count": bundle_byte_count,
            },
        }
        summary["rank_key"] = _candidate_rank_key(summary)
        summaries.append(summary)
    summaries.sort(key=lambda item: tuple(item["rank_key"]))
    payload: dict[str, object] = {
        "schema_version": EXTERNAL_TOURNAMENT_STAGE_SUMMARY_SCHEMA_V1,
        "stage": stage,
        "artifact_lock_digest": lock["lock_digest"],
        "candidate_count": len(expected_ids),
        "external_family_count": len(
            {str(catalog[item]["family"]) for item in expected_ids}
        ),
        "case_trial_count": len(expected_case_trials),
        "result_count": len(normalized),
        "ranking": [item["candidate_id"] for item in summaries],
        "candidates": summaries,
        "invariants": {
            "same_input_set_for_every_candidate": True,
            "positive_results_require_bgig_certificate": True,
            "invalid_output_fails_closed": True,
            "unsupported_cases_counted_but_not_quality_ranked": True,
        },
    }
    payload["summary_digest"] = canonical_digest(payload)
    return payload


def summarize_external_tournament_tuning(
    rows: Sequence[Mapping[str, object]],
    *,
    artifact_lock: object,
    candidate_ids: Sequence[str],
    trial_ids: Sequence[str],
) -> dict[str, object]:
    """Choisit un réglage par candidat parmi les essais annoncés."""

    trials = []
    for trial_id in trial_ids:
        trial_rows = [
            row for row in rows if str(row.get("trial_id")) == trial_id
        ]
        trials.append(
            summarize_external_tournament_stage(
                f"tuning:{trial_id}",
                trial_rows,
                artifact_lock=artifact_lock,
                candidate_ids=candidate_ids,
            )
        )
    selected: dict[str, str] = {}
    for candidate_id in candidate_ids:
        options = []
        for trial in trials:
            candidate = _candidate_summary(trial, candidate_id)
            options.append(
                (
                    tuple(candidate["rank_key"]),
                    str(trial["stage"]).split(":", 1)[1],
                )
            )
        options.sort()
        selected[str(candidate_id)] = options[0][1]
    payload: dict[str, object] = {
        "schema_version": EXTERNAL_TOURNAMENT_TUNING_SUMMARY_SCHEMA_V1,
        "trial_count": len(trials),
        "trials": trials,
        "selected_trial_by_candidate": selected,
        "invariants": {
            "trial_count_identical_for_every_candidate": True,
            "trial_choice_precedes_holdout": True,
            "post_open_tuning_allowed": False,
        },
    }
    payload["summary_digest"] = canonical_digest(payload)
    return payload


def build_external_tournament_selection_evidence(
    *,
    config: object,
    manifest: object,
    artifact_lock: object,
    code_bundle_digest: str,
    public_evidence: object,
    exact_control_summary: object,
    regression_summary: object,
    discovery_summary: object,
    tuning_summary: object,
    tuning_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Sélectionne un candidat ou un routeur avant toute ouverture du holdout."""

    accepted_config = validate_external_tournament_config(config)
    accepted_manifest = validate_external_solver_benchmark_manifest(manifest)
    lock = validate_external_solver_artifact_lock(artifact_lock)
    if not _is_digest(code_bundle_digest):
        raise ExternalSolverTournamentError(
            "External tournament code bundle digest is invalid."
        )
    candidate_ids = [
        str(item) for item in accepted_config["candidate_ids"]
    ]
    summaries = {
        "exact_controls": _validate_summary(
            exact_control_summary, "exact_controls"
        ),
        "regression": _validate_summary(regression_summary, "regression"),
        "discovery": _validate_summary(discovery_summary, "discovery"),
    }
    tuning = _mapping(tuning_summary, "external tournament tuning summary")
    supplied_tuning_digest = tuning.get("summary_digest")
    if (
        tuning.get("schema_version")
        != EXTERNAL_TOURNAMENT_TUNING_SUMMARY_SCHEMA_V1
        or not _is_digest(supplied_tuning_digest)
        or canonical_digest(
            {
                key: value
                for key, value in tuning.items()
                if key != "summary_digest"
            }
        )
        != supplied_tuning_digest
    ):
        raise ExternalSolverTournamentError(
            "External tournament tuning summary is invalid."
        )
    public = _mapping(public_evidence, "external public method evidence")
    if (
        public.get("schema_version")
        != EXTERNAL_TOURNAMENT_PUBLIC_EVIDENCE_SCHEMA_V1
        or not _is_digest(public.get("evidence_digest"))
    ):
        raise ExternalSolverTournamentError(
            "External public method evidence is invalid."
        )
    catalog = {
        str(item["candidate_id"]): item
        for item in external_solver_candidate_catalog(lock)
    }
    selected_trials = {
        str(key): str(value)
        for key, value in _mapping(
            tuning.get("selected_trial_by_candidate"),
            "selected tuning trials",
        ).items()
    }
    candidate_decisions = []
    eligible = []
    for candidate_id in candidate_ids:
        reasons = []
        candidate = catalog[candidate_id]
        if candidate["product_gate"] != "candidate":
            reasons.append(str(candidate["product_gate"]))
        for stage, summary in summaries.items():
            record = _candidate_summary(summary, candidate_id)
            if int(record["candidate_failure_count"]) != 0:
                reasons.append(f"{stage}_candidate_failure")
        trial_summary = _trial_candidate_summary(
            tuning, candidate_id, selected_trials[candidate_id]
        )
        if int(trial_summary["candidate_failure_count"]) != 0:
            reasons.append("tuning_candidate_failure")
        decision = {
            "candidate_id": candidate_id,
            "family": candidate["family"],
            "product_gate": candidate["product_gate"],
            "selected_tuning_trial": selected_trials[candidate_id],
            "selection_eligible": not reasons,
            "rejection_reasons": reasons,
            "selection_rank_key": _selection_rank_key(
                summaries["discovery"], trial_summary, candidate_id
            ),
        }
        candidate_decisions.append(decision)
        if not reasons:
            eligible.append(decision)
    if not eligible:
        raise ExternalSolverTournamentError(
            "No product-eligible external candidate passed the open gates."
        )
    eligible.sort(
        key=lambda item: (
            tuple(item["selection_rank_key"]),
            str(item["candidate_id"]),
        )
    )
    primary = str(eligible[0]["candidate_id"])
    portfolio = _analyze_portfolio(
        primary,
        [str(item["candidate_id"]) for item in eligible],
        tuning_rows,
        selected_trials,
    )
    complementary = [
        str(item) for item in portfolio["complementary_candidate_ids"]
    ]
    selected_ids = [primary, *complementary]
    trial_config = {
        str(item["trial_id"]): item
        for item in accepted_config["stages"]["tuning_trials"]
    }
    selected_tuning_settings = {
        candidate_id: deepcopy(trial_config[selected_trials[candidate_id]])
        for candidate_id in selected_ids
    }
    holdout_limit = _mapping(
        accepted_config["stages"]["holdout"],
        "external tournament holdout limits",
    )
    selected_settings = {
        "tuning_by_candidate": selected_tuning_settings,
        "holdout": deepcopy(holdout_limit),
    }
    router = deepcopy(portfolio["router"])
    router_digest = canonical_digest(router)
    settings_digest = canonical_digest(selected_settings)
    candidate_bundle_digest = canonical_digest(
        {
            "artifact_lock_digest": lock["lock_digest"],
            "code_bundle_digest": code_bundle_digest,
            "selected_candidate_ids": selected_ids,
        }
    )
    holdout_selection = build_external_holdout_selection(
        primary_candidate_id=primary,
        complementary_candidate_ids=complementary,
        router_digest=router_digest,
        candidate_bundle_digest=candidate_bundle_digest,
        open_corpus_digest=str(accepted_manifest["open_corpus_digest"]),
        settings_digest=settings_digest,
        total_budget_seconds=int(ceil(float(holdout_limit["wall_seconds"]))),
    )
    evidence: dict[str, object] = {
        "schema_version": (
            EXTERNAL_TOURNAMENT_SELECTION_EVIDENCE_SCHEMA_V1
        ),
        "config_digest": accepted_config["config_digest"],
        "manifest_digest": accepted_manifest["manifest_digest"],
        "open_corpus_digest": accepted_manifest["open_corpus_digest"],
        "artifact_lock_digest": lock["lock_digest"],
        "code_bundle_digest": code_bundle_digest,
        "candidate_bundle_digest": candidate_bundle_digest,
        "public_method_evidence_digest": public["evidence_digest"],
        "open_stage_summary_digests": {
            stage: summary["summary_digest"]
            for stage, summary in summaries.items()
        },
        "tuning_summary_digest": tuning["summary_digest"],
        "primary_candidate_id": primary,
        "complementary_candidate_ids": complementary,
        "selected_candidate_ids": selected_ids,
        "selected_settings": selected_settings,
        "settings_digest": settings_digest,
        "router": router,
        "router_digest": router_digest,
        "portfolio_analysis": portfolio,
        "candidate_decisions": candidate_decisions,
        "holdout_limits": deepcopy(holdout_limit),
        "holdout_selection": holdout_selection,
        "invariants": {
            "external_candidate_count": len(candidate_ids),
            "external_family_count": len(
                {str(catalog[item]["family"]) for item in candidate_ids}
            ),
            "selected_before_holdout": True,
            "holdout_case_count_seen": 0,
            "post_open_tuning_allowed": False,
            "one_engine_invocation_per_case": True,
            "product_solver_routing_changed": False,
        },
    }
    evidence["selection_evidence_digest"] = canonical_digest(evidence)
    return validate_external_tournament_selection_evidence(evidence)


def validate_external_tournament_selection_evidence(
    value: object,
) -> dict[str, object]:
    """Refuse toute sélection modifiée après son scellement."""

    evidence = _mapping(value, "external tournament selection evidence")
    supplied_digest = evidence.pop("selection_evidence_digest", None)
    if (
        evidence.get("schema_version")
        != EXTERNAL_TOURNAMENT_SELECTION_EVIDENCE_SCHEMA_V1
        or not _is_digest(supplied_digest)
        or canonical_digest(evidence) != supplied_digest
    ):
        raise ExternalSolverTournamentError(
            "External tournament selection evidence digest mismatch."
        )
    selected = evidence.get("selected_candidate_ids")
    primary = evidence.get("primary_candidate_id")
    complementary = evidence.get("complementary_candidate_ids")
    if (
        not isinstance(selected, list)
        or not isinstance(complementary, list)
        or not 1 <= len(selected) <= 3
        or selected != [primary, *complementary]
        or len(selected) != len(set(selected))
        or canonical_digest(evidence.get("router"))
        != evidence.get("router_digest")
        or canonical_digest(evidence.get("selected_settings"))
        != evidence.get("settings_digest")
    ):
        raise ExternalSolverTournamentError(
            "External tournament selected candidates or bindings changed."
        )
    stored_holdout = _mapping(
        evidence.get("holdout_selection"), "external holdout selection"
    )
    rebuilt = build_external_holdout_selection(
        primary_candidate_id=str(primary),
        complementary_candidate_ids=[
            str(item) for item in complementary
        ],
        router_digest=str(evidence["router_digest"]),
        candidate_bundle_digest=str(evidence["candidate_bundle_digest"]),
        open_corpus_digest=str(evidence["open_corpus_digest"]),
        settings_digest=str(evidence["settings_digest"]),
        total_budget_seconds=int(
            _mapping(
                evidence.get("holdout_limits"), "holdout limits"
            )["wall_seconds"]
        ),
    )
    if rebuilt != stored_holdout:
        raise ExternalSolverTournamentError(
            "External tournament holdout selection binding changed."
        )
    invariants = _mapping(
        evidence.get("invariants"), "selection invariants"
    )
    if (
        int(invariants.get("external_candidate_count", 0)) < 3
        or int(invariants.get("external_family_count", 0)) < 3
        or invariants.get("selected_before_holdout") is not True
        or invariants.get("holdout_case_count_seen") != 0
        or invariants.get("post_open_tuning_allowed") is not False
        or invariants.get("one_engine_invocation_per_case") is not True
    ):
        raise ExternalSolverTournamentError(
            "External tournament selection invariants changed."
        )
    evidence["selection_evidence_digest"] = supplied_digest
    return deepcopy(evidence)


def build_external_public_method_evidence(
    *,
    manifest: object,
    downloaded_sources: Mapping[str, Path],
) -> dict[str, object]:
    """Vérifie et décrit les huit contrôles publics sans les classer produit."""

    accepted = validate_external_solver_benchmark_manifest(manifest)
    source_by_id = {
        str(item["source_id"]): item for item in accepted["public_sources"]
    }
    if set(downloaded_sources) != set(source_by_id):
        raise ExternalSolverTournamentError(
            "External public source paths do not match the manifest."
        )
    receipts = {}
    for source_id, path in downloaded_sources.items():
        receipts[source_id] = verify_downloaded_public_source(
            source_by_id[source_id], path
        )
    orlib_path = downloaded_sources["orlib-thpack9"]
    orlib_cases = _parse_orlib_controls(
        orlib_path.read_text(encoding="ascii")
    )
    q4_cases = _parse_q4_controls(downloaded_sources["q4realbpp-v1"])
    controls_by_id = {
        item["case_id"]: item
        for item in [*orlib_cases, *q4_cases]
    }
    expected_ids = {
        str(item["case_id"])
        for item in accepted["public_method_controls"]
    }
    if set(controls_by_id) != expected_ids:
        raise ExternalSolverTournamentError(
            "External public method controls do not match the manifest."
        )
    payload: dict[str, object] = {
        "schema_version": EXTERNAL_TOURNAMENT_PUBLIC_EVIDENCE_SCHEMA_V1,
        "manifest_digest": accepted["manifest_digest"],
        "source_count": len(receipts),
        "control_count": len(controls_by_id),
        "source_receipts": {
            key: receipts[key] for key in sorted(receipts)
        },
        "controls": [
            controls_by_id[key] for key in sorted(controls_by_id)
        ],
        "invariants": {
            "all_sources_verified_by_size_and_sha256": True,
            "objective_mapping_copied_from_manifest": True,
            "candidate_invocation_count": 0,
            "product_ranking_eligible": False,
            "holdout_eligible": False,
        },
    }
    payload["evidence_digest"] = canonical_digest(payload)
    return payload


def quality_axes_from_report(
    report: Mapping[str, object],
) -> tuple[float, ...] | None:
    """Expose les axes BGIG partagés pour les tests et rapports."""

    return _quality_axes(report)


def _validate_result_row(
    value: Mapping[str, object],
    candidate_ids: Sequence[str],
) -> dict[str, object]:
    row = _mapping(value, "external tournament result row")
    candidate_id = row.get("candidate_id")
    if (
        candidate_id not in candidate_ids
        or not isinstance(row.get("case_id"), str)
        or not row["case_id"]
        or not isinstance(row.get("family"), str)
        or not row["family"]
        or row.get("expected_truth") not in _EXPECTED_TRUTHS
        or not isinstance(row.get("trial_id"), str)
        or not row["trial_id"]
    ):
        raise ExternalSolverTournamentError(
            "External tournament result row metadata is invalid."
        )
    report = _mapping(row.get("report"), "external tournament report")
    report_case = _mapping_or_empty(report.get("case"))
    report_candidate = _mapping_or_empty(report.get("candidate"))
    if (
        report_case.get("case_id") != row["case_id"]
        or report_candidate.get("candidate_id") != candidate_id
        or not _is_digest(report.get("report_digest"))
        or canonical_digest(
            {
                key: item
                for key, item in report.items()
                if key != "report_digest"
            }
        )
        != report["report_digest"]
    ):
        raise ExternalSolverTournamentError(
            "External tournament result report binding is invalid."
        )
    row["report"] = report
    return row


def _quality_axes(report: Mapping[str, object]) -> tuple[float, ...] | None:
    if report.get("status") != "solution_found":
        return None
    recertification = _mapping_or_empty(report.get("recertification"))
    solution = _mapping_or_empty(report.get("solution"))
    metrics = _mapping_or_empty(solution.get("metrics"))
    if recertification.get("certified") is not True:
        return None
    try:
        values = tuple(float(metrics[field]) for field in _QUALITY_FIELDS)
    except (KeyError, TypeError, ValueError) as exc:
        raise ExternalSolverTournamentError(
            "Certified external solution misses BGIG quality metrics."
        ) from exc
    if not all(isfinite(item) for item in values):
        raise ExternalSolverTournamentError(
            "Certified external solution quality metrics are not finite."
        )
    return (
        values[0],
        values[1],
        values[2],
        values[3],
        values[4],
        -values[5],
        -values[6],
    )


def _truth_matches(expected_truth: str, status: str) -> bool:
    return (
        expected_truth == "feasible" and status == "solution_found"
    ) or (
        expected_truth == "impossible"
        and status == "infeasible_proven"
    )


def _candidate_rank_key(summary: Mapping[str, object]) -> list[object]:
    quality = _mapping(summary.get("quality_pairwise"), "quality summary")
    resources = _mapping(summary.get("resources"), "resource summary")
    return [
        int(summary["candidate_failure_count"]),
        int(summary["oracle_miss_count"]),
        -int(summary["oracle_pass_count"]),
        -int(summary["certified_solution_count"]),
        -int(quality["wins"]),
        int(quality["losses"]),
        float(resources["total_wall_seconds"]),
        int(resources["bundle_byte_count"]),
        str(summary["candidate_id"]),
    ]


def _selection_rank_key(
    discovery: Mapping[str, object],
    tuning_candidate: Mapping[str, object],
    candidate_id: str,
) -> list[object]:
    discovered = _candidate_summary(discovery, candidate_id)
    discovery_quality = _mapping(
        discovered["quality_pairwise"], "discovery quality"
    )
    tuning_quality = _mapping(
        tuning_candidate["quality_pairwise"], "tuning quality"
    )
    discovery_resources = _mapping(
        discovered["resources"], "discovery resources"
    )
    tuning_resources = _mapping(
        tuning_candidate["resources"], "tuning resources"
    )
    return [
        int(discovered["candidate_failure_count"])
        + int(tuning_candidate["candidate_failure_count"]),
        int(discovered["oracle_miss_count"])
        + int(tuning_candidate["oracle_miss_count"]),
        -(
            int(discovered["oracle_pass_count"])
            + int(tuning_candidate["oracle_pass_count"])
        ),
        -(
            int(discovered["certified_solution_count"])
            + int(tuning_candidate["certified_solution_count"])
        ),
        -(
            int(discovery_quality["wins"])
            + int(tuning_quality["wins"])
        ),
        int(discovery_quality["losses"])
        + int(tuning_quality["losses"]),
        round(
            float(discovery_resources["total_wall_seconds"])
            + float(tuning_resources["total_wall_seconds"]),
            6,
        ),
        int(tuning_resources["bundle_byte_count"]),
        candidate_id,
    ]


def _analyze_portfolio(
    primary: str,
    eligible_ids: Sequence[str],
    rows: Sequence[Mapping[str, object]],
    selected_trials: Mapping[str, str],
) -> dict[str, object]:
    by_candidate_family: dict[
        str, dict[str, dict[str, dict[str, object]]]
    ] = defaultdict(lambda: defaultdict(dict))
    for raw_row in rows:
        row = dict(raw_row)
        candidate_id = str(row.get("candidate_id"))
        if (
            candidate_id not in eligible_ids
            or str(row.get("trial_id"))
            != selected_trials[candidate_id]
        ):
            continue
        by_candidate_family[candidate_id][str(row["family"])][
            str(row["case_id"])
        ] = row
    family_routes: dict[str, str] = {}
    family_comparisons = []
    for candidate_id in eligible_ids:
        if candidate_id == primary:
            continue
        for family in sorted(by_candidate_family[primary]):
            primary_cases = by_candidate_family[primary][family]
            candidate_cases = by_candidate_family[candidate_id].get(
                family, {}
            )
            if set(primary_cases) != set(candidate_cases):
                continue
            truth_delta = 0
            certified_delta = 0
            quality_wins = 0
            quality_losses = 0
            for case_id, primary_row in primary_cases.items():
                candidate_row = candidate_cases[case_id]
                expected = str(primary_row["expected_truth"])
                primary_report = _mapping(
                    primary_row["report"], "primary portfolio report"
                )
                candidate_report = _mapping(
                    candidate_row["report"], "candidate portfolio report"
                )
                truth_delta += int(
                    _truth_matches(
                        expected, str(candidate_report["status"])
                    )
                ) - int(
                    _truth_matches(
                        expected, str(primary_report["status"])
                    )
                )
                certified_delta += int(
                    _mapping_or_empty(
                        candidate_report.get("recertification")
                    ).get("certified")
                    is True
                ) - int(
                    _mapping_or_empty(
                        primary_report.get("recertification")
                    ).get("certified")
                    is True
                )
                primary_axes = _quality_axes(primary_report)
                candidate_axes = _quality_axes(candidate_report)
                if primary_axes is not None and candidate_axes is not None:
                    if candidate_axes < primary_axes:
                        quality_wins += 1
                    elif primary_axes < candidate_axes:
                        quality_losses += 1
            wins_family = (
                truth_delta > 0
                or (
                    truth_delta == 0
                    and (
                        certified_delta > 0
                        or (
                            certified_delta == 0
                            and quality_wins > quality_losses
                        )
                    )
                )
            )
            family_comparisons.append(
                {
                    "candidate_id": candidate_id,
                    "family": family,
                    "truth_pass_delta": truth_delta,
                    "certified_solution_delta": certified_delta,
                    "quality_wins": quality_wins,
                    "quality_losses": quality_losses,
                    "wins_family": wins_family,
                }
            )
            if wins_family and family not in family_routes:
                family_routes[family] = candidate_id
    complementary = []
    for candidate_id in eligible_ids:
        if (
            candidate_id != primary
            and candidate_id in set(family_routes.values())
            and len(complementary) < 2
        ):
            complementary.append(candidate_id)
    portfolio_truth_delta = sum(
        int(item["truth_pass_delta"])
        for item in family_comparisons
        if family_routes.get(str(item["family"]))
        == item["candidate_id"]
    )
    portfolio_certified_delta = sum(
        int(item["certified_solution_delta"])
        for item in family_comparisons
        if family_routes.get(str(item["family"]))
        == item["candidate_id"]
    )
    portfolio_quality_wins = sum(
        int(item["quality_wins"])
        for item in family_comparisons
        if family_routes.get(str(item["family"]))
        == item["candidate_id"]
    )
    portfolio_quality_losses = sum(
        int(item["quality_losses"])
        for item in family_comparisons
        if family_routes.get(str(item["family"]))
        == item["candidate_id"]
    )
    beats_primary = (
        portfolio_truth_delta > 0
        or (
            portfolio_truth_delta == 0
            and (
                portfolio_certified_delta > 0
                or (
                    portfolio_certified_delta == 0
                    and portfolio_quality_wins > portfolio_quality_losses
                )
            )
        )
    )
    if not beats_primary:
        complementary = []
        family_routes = {}
    return {
        "primary_candidate_id": primary,
        "complementary_candidate_ids": complementary,
        "family_comparisons": family_comparisons,
        "portfolio_vs_primary": {
            "truth_pass_delta": portfolio_truth_delta,
            "certified_solution_delta": portfolio_certified_delta,
            "quality_wins": portfolio_quality_wins,
            "quality_losses": portfolio_quality_losses,
            "beats_best_single": beats_primary,
        },
        "router": {
            "schema_version": "bgig.external_solver_router.v1",
            "default_candidate_id": primary,
            "family_routes": (
                family_routes if complementary else {}
            ),
            "one_engine_invocation_per_case": True,
            "input_features_only": ["family"],
        },
    }


def _parse_orlib_controls(text: str) -> list[dict[str, object]]:
    lines = [
        line.split() for line in text.splitlines() if line.strip()
    ]
    if not lines or len(lines[0]) != 1:
        raise ExternalSolverTournamentError(
            "OR-Library THPACK9 header is invalid."
        )
    instance_count = int(lines[0][0])
    cursor = 1
    instances = {}
    for _ in range(instance_count):
        if cursor + 2 >= len(lines):
            raise ExternalSolverTournamentError(
                "OR-Library THPACK9 artifact is truncated."
            )
        instance_line = lines[cursor]
        bin_line = lines[cursor + 1]
        count_line = lines[cursor + 2]
        cursor += 3
        if (
            len(instance_line) != 1
            or len(bin_line) != 3
            or len(count_line) != 1
        ):
            raise ExternalSolverTournamentError(
                "OR-Library THPACK9 instance header is invalid."
            )
        instance_id = int(instance_line[0])
        bin_size = tuple(int(item) for item in bin_line)
        type_count = int(count_line[0])
        expanded_count = 0
        item_volume = 0
        for _ in range(type_count):
            if cursor >= len(lines):
                raise ExternalSolverTournamentError(
                    "OR-Library THPACK9 item table is truncated."
                )
            columns = [int(item) for item in lines[cursor]]
            cursor += 1
            if len(columns) == 8:
                length, width, height, quantity = (
                    columns[1],
                    columns[3],
                    columns[5],
                    columns[7],
                )
            elif len(columns) == 7:
                # Trois lignes historiques de THPACK9 omettent un indicateur
                # d'orientation avant la troisième dimension.
                length, width, height, quantity = (
                    columns[1],
                    columns[3],
                    columns[4],
                    columns[6],
                )
            else:
                raise ExternalSolverTournamentError(
                    "OR-Library THPACK9 item row is invalid."
                )
            expanded_count += quantity
            item_volume += length * width * height * quantity
        instances[instance_id] = {
            "bin_dimensions": list(bin_size),
            "item_type_count": type_count,
            "expanded_item_count": expanded_count,
            "total_item_volume": item_volume,
            "volume_lower_bound_container_count": ceil(
                item_volume / (bin_size[0] * bin_size[1] * bin_size[2])
            ),
        }
    if cursor != len(lines) or instance_count != 47:
        raise ExternalSolverTournamentError(
            "OR-Library THPACK9 instance count or format changed."
        )
    return [
        {
            "case_id": f"orlib-thpack9-{instance_id:03d}",
            "source_id": "orlib-thpack9",
            "source_case_id": f"instance-{instance_id:03d}",
            "objective_correspondence": "exact_decision_reduction",
            "method_control": instances[instance_id],
            "product_ranking_eligible": False,
        }
        for instance_id in range(1, 5)
    ]


def _parse_q4_controls(path: Path) -> list[dict[str, object]]:
    result = []
    with ZipFile(path) as archive:
        names = archive.namelist()
        for case_number in (1, 3, 5, 7):
            suffix = f"/Input/3dBPP_{case_number}.txt"
            matches = [name for name in names if name.endswith(suffix)]
            if len(matches) != 1:
                raise ExternalSolverTournamentError(
                    "Q4RealBPP selected member is missing or ambiguous."
                )
            text = archive.read(matches[0]).decode("utf-8")
            bin_match = _Q4_BIN_PATTERN.search(text)
            if bin_match is None:
                raise ExternalSolverTournamentError(
                    "Q4RealBPP bin dimensions are missing."
                )
            rows = []
            for line in text.splitlines():
                columns = line.split()
                if len(columns) == 6 and columns[0].isdigit():
                    rows.append(tuple(int(item) for item in columns))
            if not rows:
                raise ExternalSolverTournamentError(
                    "Q4RealBPP item table is empty."
                )
            bin_size = tuple(int(item) for item in bin_match.groups())
            expanded_count = sum(row[1] for row in rows)
            total_volume = sum(
                row[1] * row[2] * row[3] * row[4] for row in rows
            )
            result.append(
                {
                    "case_id": f"q4realbpp-{case_number}",
                    "source_id": "q4realbpp-v1",
                    "source_case_id": f"Input/3dBPP_{case_number}.txt",
                    "objective_correspondence": (
                        "exact_single_bin_feasibility"
                    ),
                    "method_control": {
                        "bin_dimensions": list(bin_size),
                        "item_type_count": len(rows),
                        "expanded_item_count": expanded_count,
                        "total_item_volume": total_volume,
                        "single_bin_volume_load_ratio": round(
                            total_volume
                            / (bin_size[0] * bin_size[1] * bin_size[2]),
                            8,
                        ),
                    },
                    "product_ranking_eligible": False,
                }
            )
    return result


def _validate_summary(
    value: object, expected_stage: str
) -> dict[str, object]:
    summary = _mapping(value, f"external tournament {expected_stage} summary")
    supplied_digest = summary.get("summary_digest")
    if (
        summary.get("schema_version")
        != EXTERNAL_TOURNAMENT_STAGE_SUMMARY_SCHEMA_V1
        or summary.get("stage") != expected_stage
        or not _is_digest(supplied_digest)
        or canonical_digest(
            {
                key: item
                for key, item in summary.items()
                if key != "summary_digest"
            }
        )
        != supplied_digest
    ):
        raise ExternalSolverTournamentError(
            f"External tournament {expected_stage} summary is invalid."
        )
    return summary


def _candidate_summary(
    summary: Mapping[str, object], candidate_id: str
) -> dict[str, object]:
    candidates = summary.get("candidates")
    if not isinstance(candidates, list):
        raise ExternalSolverTournamentError(
            "External tournament candidate summaries are missing."
        )
    matches = [
        item
        for item in candidates
        if isinstance(item, Mapping)
        and item.get("candidate_id") == candidate_id
    ]
    if len(matches) != 1:
        raise ExternalSolverTournamentError(
            "External tournament candidate summary is missing or duplicated."
        )
    return deepcopy(dict(matches[0]))


def _trial_candidate_summary(
    tuning: Mapping[str, object],
    candidate_id: str,
    trial_id: str,
) -> dict[str, object]:
    trials = tuning.get("trials")
    if not isinstance(trials, list):
        raise ExternalSolverTournamentError(
            "External tournament tuning trials are missing."
        )
    stage = f"tuning:{trial_id}"
    matches = [
        trial
        for trial in trials
        if isinstance(trial, Mapping) and trial.get("stage") == stage
    ]
    if len(matches) != 1:
        raise ExternalSolverTournamentError(
            "Selected external tuning trial is missing."
        )
    return _candidate_summary(matches[0], candidate_id)


def _validate_limits(limits: Mapping[str, object]) -> None:
    wall = limits.get("wall_seconds")
    memory = limits.get("memory_mebibytes")
    threads = limits.get("threads")
    seed = limits.get("seed")
    if (
        isinstance(wall, bool)
        or not isinstance(wall, (int, float))
        or not 0.1 <= float(wall) <= 3600.0
        or isinstance(memory, bool)
        or not isinstance(memory, int)
        or not 64 <= memory <= 8192
        or isinstance(threads, bool)
        or not isinstance(threads, int)
        or not 1 <= threads <= 2
        or isinstance(seed, bool)
        or not isinstance(seed, int)
        or seed < 0
    ):
        raise ExternalSolverTournamentError(
            "External tournament limits are outside P64-L07."
        )


def _finite_non_negative(value: object) -> float:
    if value is None:
        return 0.0
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ExternalSolverTournamentError(
            "External tournament resource metric is invalid."
        ) from exc
    if not isfinite(number) or number < 0:
        raise ExternalSolverTournamentError(
            "External tournament resource metric is invalid."
        )
    return number


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ExternalSolverTournamentError(f"{field} must be an object.")
    return deepcopy(dict(value))


def _mapping_or_empty(value: object) -> dict[str, object]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
