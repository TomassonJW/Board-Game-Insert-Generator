"""Versioned solver-case corpus and bounded replay for P64-L05D.

Functional evidence is deterministic and separated from observed wall-clock
samples. Replaying a case never edits the solver, project, CAD, or Fusion scene.
"""

from __future__ import annotations

from copy import deepcopy
from statistics import median
from time import perf_counter
from typing import Callable, Mapping, Sequence

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import (
    minimal_lane_specs,
    solve_minimal_layout,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_case_bundle import (
    SOLVER_CASE_BUNDLE_SCHEMA_V1,
)
from board_game_insert_generator.solver_outcome import (
    NO_SOLUTION_WITHIN_BUDGET,
    SOLUTION_FOUND,
)


SOLVER_CASE_CORPUS_SCHEMA_V1 = "bgig.solver_case_corpus.v1"
SOLVER_CASE_REPLAY_SCHEMA_V1 = "bgig.solver_case_replay.v1"
SOLVER_CASE_COMPARISON_SCHEMA_V1 = "bgig.solver_case_comparison.v1"
SOLVER_CASE_CORPUS_PRODUCER_ID = "solver_case_corpus_v1"
SOLVER_CASE_CORPUS_PRODUCER_VERSION = "1"
CORPUS_TIER_CI = "ci"
CORPUS_TIER_EXTENDED = "extended"
_ALLOWED_TIERS = (CORPUS_TIER_CI, CORPUS_TIER_EXTENDED)
_ALLOWED_EFFORTS = ("quick", "normal", "deep")
_REPLAYABLE_STATUSES = (SOLUTION_FOUND, NO_SOLUTION_WITHIN_BUDGET)
_SECRET_KEY_FRAGMENTS = (
    "api_key",
    "authorization",
    "password",
    "secret",
    "token",
)

SolverCallable = Callable[..., dict[str, object]]
ClockCallable = Callable[[], float]


class SolverCaseCorpusError(ValueError):
    """Raised when a corpus or captured bundle is not replayable fail-closed."""


def build_solver_case(
    case_id: str,
    raw_project: object,
    *,
    solver_settings: Mapping[str, object],
    execution_tier: str = CORPUS_TIER_CI,
    accepted_statuses: Sequence[str] = _REPLAYABLE_STATUSES,
    baseline: Mapping[str, object] | None = None,
    source: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build one normalized, portable case without performance observations."""

    identifier = _identifier(case_id, "case_id")
    tier = _tier(execution_tier)
    settings = _solver_settings(solver_settings)
    statuses = _accepted_statuses(accepted_statuses)
    project = normalize_project_draft(raw_project).project
    project_digest = canonical_digest(project)
    source_payload = _source(source or {"kind": "fixture", "id": identifier})
    baseline_payload = _baseline(baseline)
    return {
        "case_id": identifier,
        "execution_tier": tier,
        "source": source_payload,
        "project": deepcopy(project),
        "project_digest": project_digest,
        "solver_settings": settings,
        "expectations": {
            "accepted_statuses": list(statuses),
            "require_certificate_if_solution": True,
            "required_lane_ids": [
                value.lane_id for value in minimal_lane_specs(str(settings["effort"]))
            ],
            "allow_solution_improvement": True,
            "proven_impossible_claim_allowed": False,
        },
        "baseline": baseline_payload,
    }


def solver_case_from_bundle(
    bundle: object,
    *,
    case_id: str,
    execution_tier: str = CORPUS_TIER_EXTENDED,
) -> dict[str, object]:
    """Import only replay-safe facts from one exact SolverCaseBundle."""

    validated = validate_solver_case_bundle(bundle)
    capture = _mapping(validated.get("capture"), "bundle.capture")
    summary = _mapping(validated.get("summary"), "bundle.summary")
    captured_status = str(summary.get("solver_result_status", ""))
    accepted = (SOLUTION_FOUND,) if captured_status == SOLUTION_FOUND else _REPLAYABLE_STATUSES
    baseline: dict[str, object] = {}
    if captured_status in _REPLAYABLE_STATUSES:
        baseline["status"] = captured_status
    captured_stop_reason = str(summary.get("stop_reason", ""))
    if captured_stop_reason:
        baseline["stop_reason"] = captured_stop_reason
    observed = _mapping_or_empty(
        _mapping(validated.get("solver_case_state"), "bundle.solver_case_state").get(
            "observed_partition"
        )
    )
    if isinstance(observed.get("plan_digest"), str):
        baseline["plan_digest"] = str(observed["plan_digest"])
    return build_solver_case(
        case_id,
        validated["project"],
        solver_settings=_mapping(
            validated.get("solver_settings"),
            "bundle.solver_settings",
        ),
        execution_tier=execution_tier,
        accepted_statuses=accepted,
        baseline=baseline,
        source={
            "kind": "solver_case_bundle",
            "id": str(capture.get("capture_id", case_id)),
            "bundle_digest": str(validated["bundle_digest"]),
        },
    )


def build_solver_case_corpus(
    cases: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Build a deterministic manifest from already-normalized case entries."""

    normalized = [_validate_case(value) for value in cases]
    normalized.sort(key=lambda value: str(value["case_id"]))
    identifiers = [str(value["case_id"]) for value in normalized]
    if len(identifiers) != len(set(identifiers)):
        raise SolverCaseCorpusError("Corpus case identifiers must be unique.")
    corpus: dict[str, object] = {
        "schema_version": SOLVER_CASE_CORPUS_SCHEMA_V1,
        "producer": {
            "id": SOLVER_CASE_CORPUS_PRODUCER_ID,
            "version": SOLVER_CASE_CORPUS_PRODUCER_VERSION,
        },
        "cases": normalized,
        "summary": {
            "case_count": len(normalized),
            "ci_case_count": sum(value["execution_tier"] == CORPUS_TIER_CI for value in normalized),
            "extended_case_count": sum(
                value["execution_tier"] == CORPUS_TIER_EXTENDED for value in normalized
            ),
        },
        "invariants": {
            "functional_evidence_deterministic": True,
            "wall_clock_samples_non_normative": True,
            "automatic_solver_modification": False,
            "finalization_invocation_count": 0,
            "cad_build_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
            "personal_project_paths_embedded": False,
        },
    }
    _reject_secret_keys(corpus)
    corpus["corpus_digest"] = canonical_digest(corpus)
    return corpus


def validate_solver_case_corpus(corpus: object) -> dict[str, object]:
    """Validate the complete manifest and return an isolated copy."""

    if not isinstance(corpus, Mapping):
        raise SolverCaseCorpusError("Solver case corpus must be an object.")
    payload = deepcopy(dict(corpus))
    if payload.get("schema_version") != SOLVER_CASE_CORPUS_SCHEMA_V1:
        raise SolverCaseCorpusError("Unsupported solver case corpus schema.")
    supplied_digest = payload.pop("corpus_digest", None)
    if not _is_digest(supplied_digest):
        raise SolverCaseCorpusError("Solver case corpus digest is missing.")
    if canonical_digest(payload) != supplied_digest:
        raise SolverCaseCorpusError("Solver case corpus digest mismatch.")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise SolverCaseCorpusError("Solver case corpus cases must be a list.")
    rebuilt = build_solver_case_corpus([_mapping(value, "corpus.cases[]") for value in cases])
    if rebuilt != dict(corpus):
        raise SolverCaseCorpusError("Solver case corpus is not canonical.")
    return deepcopy(rebuilt)


def validate_solver_case_bundle(bundle: object) -> dict[str, object]:
    """Validate a captured bundle before extracting replay-safe inputs."""

    if not isinstance(bundle, Mapping):
        raise SolverCaseCorpusError("SolverCaseBundle must be an object.")
    payload = deepcopy(dict(bundle))
    if payload.get("schema_version") != SOLVER_CASE_BUNDLE_SCHEMA_V1:
        raise SolverCaseCorpusError("Unsupported SolverCaseBundle schema.")
    supplied_digest = payload.pop("bundle_digest", None)
    if not _is_digest(supplied_digest):
        raise SolverCaseCorpusError("SolverCaseBundle digest is missing.")
    if canonical_digest(payload) != supplied_digest:
        raise SolverCaseCorpusError("SolverCaseBundle digest mismatch.")
    digests = _mapping(payload.get("digests"), "bundle.digests")
    components = (
        ("project_digest", payload.get("project")),
        ("solver_case_state_digest", payload.get("solver_case_state")),
        ("local_analysis_digest", payload.get("local_analysis")),
        ("container_frontiers_digest", payload.get("container_variant_frontiers")),
        ("interaction_trace_digest", payload.get("interaction_trace")),
    )
    for field, value in components:
        expected = digests.get(field)
        if not _is_digest(expected) or canonical_digest(value) != expected:
            raise SolverCaseCorpusError(f"SolverCaseBundle component digest mismatch: {field}.")
    normalized = normalize_project_draft(payload.get("project")).project
    if canonical_digest(normalized) != digests["project_digest"]:
        raise SolverCaseCorpusError("SolverCaseBundle project is not canonical.")
    _solver_settings(_mapping(payload.get("solver_settings"), "bundle.solver_settings"))
    payload["bundle_digest"] = supplied_digest
    return payload


def replay_solver_case_corpus(
    corpus: object,
    *,
    include_tiers: Sequence[str] = (CORPUS_TIER_CI,),
    repetitions: int = 1,
    solver: SolverCallable = solve_minimal_layout,
    clock: ClockCallable = perf_counter,
) -> dict[str, object]:
    """Replay selected cases under current code and bounded explicit settings."""

    validated = validate_solver_case_corpus(corpus)
    tiers = tuple(dict.fromkeys(_tier(value) for value in include_tiers))
    if not tiers:
        raise SolverCaseCorpusError("At least one corpus tier must be selected.")
    if isinstance(repetitions, bool) or not isinstance(repetitions, int):
        raise SolverCaseCorpusError("Replay repetitions must be an integer.")
    if repetitions < 1 or repetitions > 20:
        raise SolverCaseCorpusError("Replay repetitions must stay within 1..20.")
    results: list[dict[str, object]] = []
    functional_records: list[dict[str, object]] = []
    for case in validated["cases"]:
        if str(case["execution_tier"]) not in tiers:
            continue
        samples: list[float] = []
        functional: dict[str, object] | None = None
        for _index in range(repetitions):
            started = clock()
            partition = solver(
                deepcopy(case["project"]),
                effort_profile=str(case["solver_settings"]["effort"]),
            )
            elapsed_ms = max(0.0, (clock() - started) * 1000.0)
            samples.append(round(elapsed_ms, 3))
            observed = _functional_summary(partition)
            if functional is None:
                functional = observed
            elif functional != observed:
                raise SolverCaseCorpusError(
                    f"Functional replay is not deterministic for {case['case_id']}."
                )
        if functional is None:
            raise AssertionError("Replay loop did not execute.")
        comparison = _compare_case(case, functional)
        record = {
            "case_id": case["case_id"],
            "execution_tier": case["execution_tier"],
            "source": deepcopy(case["source"]),
            "solver_settings": deepcopy(case["solver_settings"]),
            "functional": functional,
            "comparison": comparison,
            "performance": {
                "kind": "observed_wall_clock_non_normative",
                "sample_count": len(samples),
                "samples_ms": samples,
                "minimum_ms": min(samples),
                "median_ms": round(float(median(samples)), 3),
                "maximum_ms": max(samples),
            },
        }
        results.append(record)
        functional_records.append(
            {
                "case_id": case["case_id"],
                "functional": functional,
                "comparison": comparison,
            }
        )
    all_expectations_met = all(bool(value["comparison"]["expectations_met"]) for value in results)
    report: dict[str, object] = {
        "schema_version": SOLVER_CASE_REPLAY_SCHEMA_V1,
        "corpus_digest": validated["corpus_digest"],
        "selected_tiers": list(tiers),
        "repetitions": repetitions,
        "cases": results,
        "summary": {
            "executed_case_count": len(results),
            "expectation_failure_count": sum(
                not value["comparison"]["expectations_met"] for value in results
            ),
            "all_expectations_met": all_expectations_met,
            "solution_found_count": sum(
                value["functional"]["status"] == SOLUTION_FOUND for value in results
            ),
            "no_solution_within_budget_count": sum(
                value["functional"]["status"] == NO_SOLUTION_WITHIN_BUDGET for value in results
            ),
        },
        "functional_digest": canonical_digest(
            {
                "corpus_digest": validated["corpus_digest"],
                "selected_tiers": list(tiers),
                "cases": functional_records,
            }
        ),
        "invariants": {
            "performance_excluded_from_functional_digest": True,
            "automatic_solver_modification": False,
            "finalization_invocation_count": 0,
            "cad_build_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
        },
    }
    return report


def compare_solver_case_replays(
    baseline_report: object,
    candidate_report: object,
    *,
    maximum_performance_regression_ratio: float = 0.10,
) -> dict[str, object]:
    """Compare A/B reports without promoting wall-clock samples to proof."""

    baseline = _replay_report(baseline_report, "baseline_report")
    candidate = _replay_report(candidate_report, "candidate_report")
    if baseline["corpus_digest"] != candidate["corpus_digest"]:
        raise SolverCaseCorpusError("A/B reports use different corpus digests.")
    if baseline["selected_tiers"] != candidate["selected_tiers"]:
        raise SolverCaseCorpusError("A/B reports use different selected tiers.")
    if not isinstance(maximum_performance_regression_ratio, (int, float)):
        raise SolverCaseCorpusError("Performance tolerance must be numeric.")
    tolerance = float(maximum_performance_regression_ratio)
    if tolerance < 0.0 or tolerance > 1.0:
        raise SolverCaseCorpusError("Performance tolerance must stay within 0..1.")
    baseline_cases = {
        str(value["case_id"]): value for value in _report_cases(baseline, "baseline_report")
    }
    candidate_cases = {
        str(value["case_id"]): value for value in _report_cases(candidate, "candidate_report")
    }
    if set(baseline_cases) != set(candidate_cases):
        raise SolverCaseCorpusError("A/B reports do not contain the same cases.")
    comparisons: list[dict[str, object]] = []
    deterministic: list[dict[str, object]] = []
    baseline_total_ms = 0.0
    candidate_total_ms = 0.0
    for case_id in sorted(baseline_cases):
        before = baseline_cases[case_id]
        after = candidate_cases[case_id]
        before_functional = _mapping(
            before.get("functional"),
            f"baseline_report.cases[{case_id}].functional",
        )
        after_functional = _mapping(
            after.get("functional"),
            f"candidate_report.cases[{case_id}].functional",
        )
        before_status = str(before_functional.get("status", ""))
        after_status = str(after_functional.get("status", ""))
        regression_reasons: list[str] = []
        if before_status == SOLUTION_FOUND and after_status != SOLUTION_FOUND:
            regression_reasons.append("known_solution_lost")
        if (
            after_status == SOLUTION_FOUND
            and after_functional.get("certificate_certified") is not True
        ):
            regression_reasons.append("candidate_solution_not_certified")
        if list(after_functional.get("lane_ids", [])) != list(
            before_functional.get("lane_ids", [])
        ):
            regression_reasons.append("lane_contract_changed")
        quality_improved = False
        if before_status == SOLUTION_FOUND and after_status == SOLUTION_FOUND:
            before_rank = tuple(float(value) for value in before_functional.get("rank_axes", []))
            after_rank = tuple(float(value) for value in after_functional.get("rank_axes", []))
            if not before_rank or not after_rank or after_rank > before_rank:
                regression_reasons.append("certified_plan_quality_regressed")
            quality_improved = bool(before_rank and after_rank < before_rank)
        after_comparison = _mapping(
            after.get("comparison"),
            f"candidate_report.cases[{case_id}].comparison",
        )
        if after_comparison.get("expectations_met") is not True:
            regression_reasons.append("corpus_expectation_failed")
        solution_improved = bool(
            before_status == NO_SOLUTION_WITHIN_BUDGET and after_status == SOLUTION_FOUND
        )
        before_performance = _mapping(
            before.get("performance"),
            f"baseline_report.cases[{case_id}].performance",
        )
        after_performance = _mapping(
            after.get("performance"),
            f"candidate_report.cases[{case_id}].performance",
        )
        before_ms = float(before_performance.get("median_ms", 0.0))
        after_ms = float(after_performance.get("median_ms", 0.0))
        baseline_total_ms += before_ms
        candidate_total_ms += after_ms
        functional_result = {
            "case_id": case_id,
            "baseline_status": before_status,
            "candidate_status": after_status,
            "solution_improved": solution_improved,
            "quality_improved": quality_improved,
            "functional_regression": bool(regression_reasons),
            "regression_reasons": regression_reasons,
        }
        comparisons.append(
            {
                **functional_result,
                "performance": {
                    "kind": "observed_wall_clock_non_normative",
                    "baseline_median_ms": round(before_ms, 3),
                    "candidate_median_ms": round(after_ms, 3),
                    "candidate_to_baseline_ratio": (
                        round(after_ms / before_ms, 6) if before_ms > 0.0 else "not_applicable"
                    ),
                },
            }
        )
        deterministic.append(functional_result)
    regression_count = sum(bool(value["functional_regression"]) for value in comparisons)
    improvement_count = sum(
        bool(value["solution_improved"] or value["quality_improved"]) for value in comparisons
    )
    performance_ratio = candidate_total_ms / baseline_total_ms if baseline_total_ms > 0.0 else 1.0
    performance_within_tolerance = bool(performance_ratio <= 1.0 + tolerance)
    candidate_acceptable = bool(
        regression_count == 0 and (improvement_count > 0 or performance_within_tolerance)
    )
    return {
        "schema_version": SOLVER_CASE_COMPARISON_SCHEMA_V1,
        "corpus_digest": baseline["corpus_digest"],
        "selected_tiers": deepcopy(baseline["selected_tiers"]),
        "cases": comparisons,
        "summary": {
            "case_count": len(comparisons),
            "functional_regression_count": regression_count,
            "functional_improvement_count": improvement_count,
            "candidate_acceptable": candidate_acceptable,
            "performance_within_tolerance": performance_within_tolerance,
            "maximum_performance_regression_ratio": tolerance,
            "baseline_total_median_ms": round(baseline_total_ms, 3),
            "candidate_total_median_ms": round(candidate_total_ms, 3),
            "candidate_to_baseline_ratio": round(performance_ratio, 6),
        },
        "functional_comparison_digest": canonical_digest(
            {
                "corpus_digest": baseline["corpus_digest"],
                "selected_tiers": baseline["selected_tiers"],
                "cases": deterministic,
            }
        ),
        "invariants": {
            "wall_clock_samples_non_normative": True,
            "automatic_solver_modification": False,
        },
    }


def _replay_report(value: object, field: str) -> dict[str, object]:
    report = _mapping(value, field)
    if report.get("schema_version") != SOLVER_CASE_REPLAY_SCHEMA_V1:
        raise SolverCaseCorpusError(f"{field} uses an unsupported schema.")
    if not _is_digest(report.get("corpus_digest")):
        raise SolverCaseCorpusError(f"{field} corpus digest is invalid.")
    if not isinstance(report.get("selected_tiers"), list):
        raise SolverCaseCorpusError(f"{field} selected tiers are invalid.")
    return report


def _report_cases(
    report: Mapping[str, object],
    field: str,
) -> list[dict[str, object]]:
    raw = report.get("cases")
    if not isinstance(raw, list):
        raise SolverCaseCorpusError(f"{field} cases must be a list.")
    cases = [_mapping(value, f"{field}.cases[]") for value in raw]
    identifiers = [str(value.get("case_id", "")) for value in cases]
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise SolverCaseCorpusError(f"{field} case identifiers are invalid.")
    return cases


def _functional_summary(partition: Mapping[str, object]) -> dict[str, object]:
    solver = _mapping_or_empty(partition.get("solver"))
    result = _mapping_or_empty(solver.get("result"))
    telemetry = _mapping_or_empty(solver.get("telemetry"))
    minimal = _mapping_or_empty(partition.get("minimal_layout"))
    provenance = _mapping_or_empty(minimal.get("search_provenance"))
    certificate = _mapping_or_empty(minimal.get("global_certificate"))
    metrics = _mapping_or_empty(minimal.get("metrics"))
    selected = _mapping_or_empty(provenance.get("selected"))
    lanes: list[dict[str, object]] = []
    raw_lanes = provenance.get("lanes")
    if isinstance(raw_lanes, list):
        for raw in raw_lanes:
            if not isinstance(raw, Mapping):
                continue
            lane_telemetry = _mapping_or_empty(raw.get("telemetry"))
            lanes.append(
                {
                    "lane_id": str(raw.get("lane_id", "")),
                    "status": str(raw.get("status", "")),
                    "stop_reason": str(raw.get("stop_reason", "")),
                    "search_variant": str(raw.get("search_variant", "")),
                    "search_states": int(lane_telemetry.get("search_states", 0)),
                    "placement_trials": int(lane_telemetry.get("placement_trials", 0)),
                    "geometric_solution_count": int(raw.get("geometric_solution_count", 0)),
                    "certified_candidate_count": int(raw.get("certified_candidate_count", 0)),
                    "deterministic_digest": str(raw.get("deterministic_digest", "")),
                }
            )
    status = str(result.get("status", ""))
    rank_axes: list[float] = []
    if status == SOLUTION_FOUND:
        rank_axes = [
            float(metrics["cluster_volume_mm3"]),
            float(metrics["internal_gap_mm3"]),
            float(metrics["cluster_height_mm"]),
            float(metrics["cluster_footprint_mm2"]),
            float(metrics["residual_fragmentation"]),
            -float(metrics["contact_count"]),
            -float(metrics["minimum_support_ratio"]),
        ]
    return {
        "status": status,
        "stop_reason": str(
            provenance.get("stop_reason")
            or telemetry.get("search_stop_reason")
            or result.get("reason_code")
            or ""
        ),
        "plan_digest": str(partition.get("plan_digest", "")),
        "placement_digest": str(selected.get("placement_digest", "")),
        "certificate_schema": str(certificate.get("schema_version", "")),
        "certificate_certified": certificate.get("certified") is True,
        "rank_axes": rank_axes,
        "lane_ids": [value["lane_id"] for value in lanes],
        "lanes": lanes,
        "candidate_count_before_deduplication": int(
            provenance.get("candidate_count_before_deduplication", 0)
        ),
        "candidate_count_after_deduplication": int(
            provenance.get("candidate_count_after_deduplication", 0)
        ),
        "pareto_candidate_count": int(provenance.get("pareto_candidate_count", 0)),
        "provenance_digest": str(provenance.get("deterministic_digest", "")),
    }


def _compare_case(
    case: Mapping[str, object],
    functional: Mapping[str, object],
) -> dict[str, object]:
    expectations = _mapping(case.get("expectations"), "case.expectations")
    accepted = tuple(str(value) for value in expectations["accepted_statuses"])
    status = str(functional.get("status", ""))
    status_allowed = status in accepted
    certificate_ok = bool(
        status != SOLUTION_FOUND or functional.get("certificate_certified") is True
    )
    lane_prefix_ok = list(functional.get("lane_ids", [])) == list(expectations["required_lane_ids"])
    baseline = _mapping_or_empty(case.get("baseline"))
    baseline_status = str(baseline.get("status", ""))
    if baseline_status == status:
        transition = "stable"
    elif baseline_status == NO_SOLUTION_WITHIN_BUDGET and status == SOLUTION_FOUND:
        transition = "improved_to_solution"
    elif baseline_status == SOLUTION_FOUND and status != SOLUTION_FOUND:
        transition = "regressed_from_solution"
    elif baseline_status:
        transition = "changed"
    else:
        transition = "baseline_not_recorded"
    baseline_rank = baseline.get("rank_axes")
    quality_not_worse = True
    if isinstance(baseline_rank, list) and baseline_rank:
        current_rank = functional.get("rank_axes")
        quality_not_worse = bool(
            isinstance(current_rank, list)
            and current_rank
            and tuple(float(value) for value in current_rank)
            <= tuple(float(value) for value in baseline_rank)
        )
    checks = {
        "status_allowed": status_allowed,
        "certificate_if_solution": certificate_ok,
        "lane_prefix_exact": lane_prefix_ok,
        "baseline_quality_not_worse": quality_not_worse,
    }
    return {
        "expectations_met": all(checks.values()),
        "checks": checks,
        "baseline_transition": transition,
        "baseline_status": baseline_status,
        "current_status": status,
    }


def _validate_case(value: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise SolverCaseCorpusError("Every corpus case must be an object.")
    return build_solver_case(
        str(value.get("case_id", "")),
        value.get("project"),
        solver_settings=_mapping(
            value.get("solver_settings"),
            "case.solver_settings",
        ),
        execution_tier=str(value.get("execution_tier", "")),
        accepted_statuses=tuple(
            str(item)
            for item in _sequence(
                _mapping(value.get("expectations"), "case.expectations").get("accepted_statuses"),
                "case.expectations.accepted_statuses",
            )
        ),
        baseline=_mapping_or_empty(value.get("baseline")),
        source=_mapping(value.get("source"), "case.source"),
    )


def _solver_settings(value: Mapping[str, object]) -> dict[str, str]:
    method = _identifier(str(value.get("method", "auto")), "solver method")
    effort = str(value.get("effort", "normal"))
    if effort not in _ALLOWED_EFFORTS:
        raise SolverCaseCorpusError("Solver effort must be quick, normal, or deep.")
    return {"method": method, "effort": effort}


def _accepted_statuses(value: Sequence[str]) -> tuple[str, ...]:
    statuses = tuple(dict.fromkeys(str(item) for item in value))
    if not statuses or any(item not in _REPLAYABLE_STATUSES for item in statuses):
        raise SolverCaseCorpusError(
            "Accepted statuses must use solution_found or no_solution_within_budget."
        )
    return tuple(item for item in _REPLAYABLE_STATUSES if item in statuses)


def _baseline(value: Mapping[str, object] | None) -> dict[str, object]:
    if value is None:
        return {}
    payload = deepcopy(dict(value))
    allowed = {"status", "stop_reason", "plan_digest", "placement_digest", "rank_axes"}
    if any(key not in allowed for key in payload):
        raise SolverCaseCorpusError("Corpus baseline contains unsupported fields.")
    status = payload.get("status")
    if status not in (None, "", *_REPLAYABLE_STATUSES):
        raise SolverCaseCorpusError("Corpus baseline status is not replayable.")
    for field in ("plan_digest", "placement_digest"):
        if field in payload and payload[field] != "" and not _is_digest(payload[field]):
            raise SolverCaseCorpusError(f"Corpus baseline {field} is invalid.")
    rank_axes = payload.get("rank_axes")
    if rank_axes is not None:
        if not isinstance(rank_axes, list) or len(rank_axes) != 7:
            raise SolverCaseCorpusError("Corpus baseline rank_axes must have seven values.")
        payload["rank_axes"] = [float(item) for item in rank_axes]
    return payload


def _source(value: Mapping[str, object]) -> dict[str, object]:
    kind = str(value.get("kind", "fixture"))
    if kind not in {"fixture", "solver_case_bundle"}:
        raise SolverCaseCorpusError("Corpus source kind is unsupported.")
    payload: dict[str, object] = {
        "kind": kind,
        "id": _identifier(str(value.get("id", "")), "source.id"),
    }
    if kind == "solver_case_bundle":
        digest = value.get("bundle_digest")
        if not _is_digest(digest):
            raise SolverCaseCorpusError("Bundle source digest is invalid.")
        payload["bundle_digest"] = str(digest)
    return payload


def _tier(value: str) -> str:
    if value not in _ALLOWED_TIERS:
        raise SolverCaseCorpusError("Corpus tier must be ci or extended.")
    return value


def _identifier(value: str, field: str) -> str:
    result = str(value).strip()
    if any(separator in result for separator in ("/", "\\")):
        raise SolverCaseCorpusError(f"{field} must not contain a path.")
    if not result or len(result) > 128:
        raise SolverCaseCorpusError(f"{field} must contain 1..128 characters.")
    return result


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise SolverCaseCorpusError(f"{field} must be an object.")
    return dict(value)


def _mapping_or_empty(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _sequence(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise SolverCaseCorpusError(f"{field} must be a list.")
    return list(value)


def _is_digest(value: object) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _reject_secret_keys(value: object, path: str = "corpus") -> None:
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key).lower()
            if any(fragment in key for fragment in _SECRET_KEY_FRAGMENTS):
                raise SolverCaseCorpusError(
                    f"Secret-like key is forbidden in corpus: {path}.{raw_key}."
                )
            _reject_secret_keys(item, f"{path}.{raw_key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_secret_keys(item, f"{path}[{index}]")
