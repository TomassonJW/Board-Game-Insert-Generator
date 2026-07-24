"""Exécute P64-L07D en deux temps : ouvert, puis holdout scellé."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping, Sequence

from board_game_insert_generator.external_solver_adapters import (
    ExternalSolverLimits,
    build_external_adapter_exact_controls,
    prepare_external_floor_case,
    run_external_solver_adapter,
)
from board_game_insert_generator.external_solver_artifacts import (
    external_solver_candidate_catalog,
    validate_external_solver_artifact_lock,
    verify_external_solver_artifacts,
)
from board_game_insert_generator.external_solver_benchmark_corpus import (
    materialize_external_benchmark_split,
    open_external_holdout_cases,
    validate_external_solver_benchmark_manifest,
)
from board_game_insert_generator.external_solver_tournament import (
    build_external_public_method_evidence,
    build_external_tournament_selection_evidence,
    quality_axes_from_report,
    summarize_external_tournament_stage,
    summarize_external_tournament_tuning,
    validate_external_tournament_config,
    validate_external_tournament_selection_evidence,
)
from board_game_insert_generator.incremental_project_state import canonical_digest

from external_tournament_runtime import (
    build_external_runtimes,
    run_bgig_baseline_case,
)


ROOT = Path(__file__).resolve().parents[2]
OPEN_CAMPAIGN_SCHEMA = "bgig.external_solver_open_tournament.v1"
HOLDOUT_CAMPAIGN_SCHEMA = "bgig.external_solver_holdout_tournament.v1"
COMPACT_EVIDENCE_SCHEMA = "bgig.external_solver_tournament_evidence.v1"
OPENING_RECEIPT_SCHEMA = "bgig.external_solver_holdout_opening_receipt.v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="phase", required=True)
    open_parser = subparsers.add_parser("open")
    _add_common_arguments(open_parser)
    open_parser.add_argument("--orlib-artifact", type=Path, required=True)
    open_parser.add_argument("--q4realbpp-artifact", type=Path, required=True)
    open_parser.add_argument("--output", type=Path, required=True)
    open_parser.add_argument("--selection-output", type=Path, required=True)
    open_parser.add_argument("--resume", action="store_true")

    holdout_parser = subparsers.add_parser("holdout")
    _add_common_arguments(holdout_parser)
    holdout_parser.add_argument("--open-campaign", type=Path, required=True)
    holdout_parser.add_argument("--selection", type=Path, required=True)
    holdout_parser.add_argument("--sealed-holdout", type=Path, required=True)
    holdout_parser.add_argument("--opening-receipt", type=Path, required=True)
    holdout_parser.add_argument("--output", type=Path, required=True)
    holdout_parser.add_argument("--evidence-output", type=Path, required=True)
    holdout_parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.phase == "open":
        return _run_open(args)
    return _run_holdout(args)


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifact-lock", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--environment-root", type=Path, required=True)
    parser.add_argument("--java-home", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)


def _run_open(args: argparse.Namespace) -> int:
    if args.output.exists() and not args.resume:
        raise RuntimeError(
            "Open tournament output exists; pass --resume to reuse checkpoints."
        )
    common = _load_common(args)
    config = common["config"]
    manifest = common["manifest"]
    lock = common["lock"]
    candidate_ids = common["candidate_ids"]
    candidates = common["candidates"]
    receipts = common["receipts"]
    runtimes = common["runtimes"]
    public_evidence = build_external_public_method_evidence(
        manifest=manifest,
        downloaded_sources={
            "orlib-thpack9": args.orlib_artifact.resolve(),
            "q4realbpp-v1": args.q4realbpp_artifact.resolve(),
        },
    )
    print(
        f"PUBLIC_METHOD_CONTROLS={public_evidence['control_count']}/8 OK",
        flush=True,
    )

    controls = build_external_adapter_exact_controls()
    control_rows = _run_external_stage(
        controls["cases"],
        candidate_ids=candidate_ids,
        candidates=candidates,
        lock=lock,
        receipts=receipts,
        runtimes=runtimes,
        limits=_limits(config["stages"]["exact_controls"]),
        trial_id="exact-controls",
        expected_truth=lambda case: (
            "feasible"
            if case["exact_truth"] == "feasible"
            else "impossible"
        ),
        stage="exact_controls",
    )
    _assert_exact_control_gate(control_rows, candidates)
    control_summary = summarize_external_tournament_stage(
        "exact_controls",
        control_rows,
        artifact_lock=lock,
        candidate_ids=candidate_ids,
    )

    regression_cases = materialize_external_benchmark_split(
        manifest, "regression"
    )
    regression_rows = _run_external_stage(
        regression_cases,
        candidate_ids=candidate_ids,
        candidates=candidates,
        lock=lock,
        receipts=receipts,
        runtimes=runtimes,
        limits=_limits(config["stages"]["regression"]),
        trial_id="regression",
        expected_truth=lambda _case: "regression_open",
        stage="regression",
    )
    regression_summary = summarize_external_tournament_stage(
        "regression",
        regression_rows,
        artifact_lock=lock,
        candidate_ids=candidate_ids,
    )
    _assert_no_candidate_failure(regression_summary)

    discovery_cases = materialize_external_benchmark_split(
        manifest, "discovery"
    )
    discovery_limits = _limits(config["stages"]["discovery"])
    discovery_rows = _run_external_stage(
        discovery_cases,
        candidate_ids=candidate_ids,
        candidates=candidates,
        lock=lock,
        receipts=receipts,
        runtimes=runtimes,
        limits=discovery_limits,
        trial_id="discovery",
        expected_truth=_generated_truth,
        stage="discovery",
    )
    discovery_summary = summarize_external_tournament_stage(
        "discovery",
        discovery_rows,
        artifact_lock=lock,
        candidate_ids=candidate_ids,
    )
    _assert_discovery_gate(discovery_summary)
    discovery_baseline = _run_baseline_stage(
        discovery_cases,
        scratch_root=args.scratch_root.resolve(),
        limits=discovery_limits,
        trial_id="discovery-baseline",
        stage="discovery",
    )

    tuning_cases = materialize_external_benchmark_split(manifest, "tuning")
    tuning_rows = []
    trial_ids = []
    for trial in config["stages"]["tuning_trials"]:
        trial_id = str(trial["trial_id"])
        trial_ids.append(trial_id)
        tuning_rows.extend(
            _run_external_stage(
                tuning_cases,
                candidate_ids=candidate_ids,
                candidates=candidates,
                lock=lock,
                receipts=receipts,
                runtimes=runtimes,
                limits=_limits(trial),
                trial_id=trial_id,
                expected_truth=_generated_truth,
                stage=f"tuning:{trial_id}",
            )
        )
    tuning_summary = summarize_external_tournament_tuning(
        tuning_rows,
        artifact_lock=lock,
        candidate_ids=candidate_ids,
        trial_ids=trial_ids,
    )
    for trial in tuning_summary["trials"]:
        _assert_no_candidate_failure(trial)
    tuning_baseline = _run_baseline_stage(
        tuning_cases,
        scratch_root=args.scratch_root.resolve(),
        limits=_limits(config["stages"]["tuning_trials"][0]),
        trial_id="tuning-baseline",
        stage="tuning",
    )

    code_bundle = _code_bundle(config_path=args.config.resolve())
    selection = build_external_tournament_selection_evidence(
        config=config,
        manifest=manifest,
        artifact_lock=lock,
        code_bundle_digest=code_bundle["code_bundle_digest"],
        public_evidence=public_evidence,
        exact_control_summary=control_summary,
        regression_summary=regression_summary,
        discovery_summary=discovery_summary,
        tuning_summary=tuning_summary,
        tuning_rows=tuning_rows,
    )
    selected_trials = tuning_summary["selected_trial_by_candidate"]
    baseline_comparisons = {
        candidate_id: {
            "discovery": _compare_external_to_baseline(
                discovery_rows,
                discovery_baseline,
                candidate_id=candidate_id,
                trial_id="discovery",
            ),
            "tuning": _compare_external_to_baseline(
                tuning_rows,
                tuning_baseline,
                candidate_id=candidate_id,
                trial_id=str(selected_trials[candidate_id]),
            ),
        }
        for candidate_id in candidate_ids
    }
    campaign: dict[str, object] = {
        "schema_version": OPEN_CAMPAIGN_SCHEMA,
        "config_digest": config["config_digest"],
        "manifest_digest": manifest["manifest_digest"],
        "open_corpus_digest": manifest["open_corpus_digest"],
        "artifact_lock_digest": lock["lock_digest"],
        "code_bundle": code_bundle,
        "public_method_evidence": public_evidence,
        "rows": {
            "exact_controls": control_rows,
            "regression": regression_rows,
            "discovery": discovery_rows,
            "tuning": tuning_rows,
            "baseline_discovery": discovery_baseline,
            "baseline_tuning": tuning_baseline,
        },
        "summaries": {
            "exact_controls": control_summary,
            "regression": regression_summary,
            "discovery": discovery_summary,
            "tuning": tuning_summary,
        },
        "baseline_comparisons": baseline_comparisons,
        "selection_evidence_digest": selection[
            "selection_evidence_digest"
        ],
        "invariants": {
            "external_candidate_count": len(candidate_ids),
            "external_family_count": len(
                {str(item["family"]) for item in candidates}
            ),
            "public_source_count": public_evidence["source_count"],
            "heavy_processes_run_concurrently": 1,
            "holdout_case_count_seen": 0,
            "holdout_sidecar_path_accepted_by_open_phase": False,
            "network_service_invocation_count": 0,
            "product_solver_routing_changed": False,
        },
    }
    campaign["campaign_digest"] = canonical_digest(campaign)
    _write_json_atomic(args.selection_output, selection)
    _write_json_atomic(args.output, campaign)
    print(
        f"OPEN_TOURNAMENT=passed DIGEST={campaign['campaign_digest']}",
        flush=True,
    )
    print(
        "SEALED_SELECTION="
        f"{selection['primary_candidate_id']} "
        f"DIGEST={selection['selection_evidence_digest']}",
        flush=True,
    )
    return 0


def _run_holdout(args: argparse.Namespace) -> int:
    if args.output.exists() and not args.resume:
        raise RuntimeError(
            "Holdout output exists; the unique campaign cannot be overwritten."
        )
    common = _load_common(args)
    config = common["config"]
    manifest = common["manifest"]
    lock = common["lock"]
    candidates = common["candidates"]
    receipts = common["receipts"]
    runtimes = common["runtimes"]
    selection = validate_external_tournament_selection_evidence(
        _read_json(args.selection)
    )
    open_campaign = _validate_open_campaign(
        _read_json(args.open_campaign)
    )
    current_bundle = _code_bundle(config_path=args.config.resolve())
    if (
        open_campaign["selection_evidence_digest"]
        != selection["selection_evidence_digest"]
        or open_campaign["campaign_digest"]
        != _read_json(args.open_campaign)["campaign_digest"]
        or selection["code_bundle_digest"]
        != current_bundle["code_bundle_digest"]
        or selection["manifest_digest"] != manifest["manifest_digest"]
        or selection["artifact_lock_digest"] != lock["lock_digest"]
    ):
        raise RuntimeError(
            "Holdout bindings differ from the sealed open tournament."
        )
    sealed = _read_json(args.sealed_holdout)
    opened = open_external_holdout_cases(
        manifest,
        selection["holdout_selection"],
        sealed,
    )
    opening_receipt = {
        "schema_version": OPENING_RECEIPT_SCHEMA,
        "selection_evidence_digest": selection[
            "selection_evidence_digest"
        ],
        "selection_digest": selection["holdout_selection"][
            "selection_digest"
        ],
        "manifest_digest": manifest["manifest_digest"],
        "sealed_holdout_digest": opened["sealed_holdout_digest"],
        "holdout_commitment_digest": opened[
            "holdout_commitment_digest"
        ],
        "case_count": len(opened["cases"]),
        "post_open_tuning_allowed": False,
    }
    opening_receipt["opening_receipt_digest"] = canonical_digest(
        opening_receipt
    )
    _write_or_verify_opening_receipt(
        args.opening_receipt,
        opening_receipt,
        resume=args.resume,
    )
    router = selection["router"]
    family_routes = dict(router["family_routes"])
    default_candidate = str(router["default_candidate_id"])
    selected_ids = [str(item) for item in selection["selected_candidate_ids"]]
    holdout_limits = _limits(selection["holdout_limits"])
    candidate_by_id = {
        str(item["candidate_id"]): item for item in candidates
    }
    portfolio_rows = []
    for index, case in enumerate(opened["cases"], start=1):
        candidate_id = str(
            family_routes.get(str(case["family"]), default_candidate)
        )
        if candidate_id not in selected_ids:
            raise RuntimeError("Sealed holdout router selected an unknown engine.")
        execution = run_external_solver_adapter(
            case,
            candidate_id,
            artifact_lock=lock,
            artifact_receipt=receipts[candidate_id],
            runtime=runtimes[candidate_id],
            limits=holdout_limits,
        )
        portfolio_rows.append(
            _result_row(
                case,
                candidate_id=candidate_id,
                candidate=candidate_by_id[candidate_id],
                report=execution.report,
                trial_id="holdout-portfolio",
                expected_truth=_generated_truth(case),
            )
        )
        if index % 8 == 0:
            print(f"HOLDOUT_PORTFOLIO={index}/{len(opened['cases'])}", flush=True)
    if len(selected_ids) == 1:
        primary_rows = deepcopy(portfolio_rows)
    else:
        primary_rows = _run_external_stage(
            opened["cases"],
            candidate_ids=[default_candidate],
            candidates=[candidate_by_id[default_candidate]],
            lock=lock,
            receipts=receipts,
            runtimes=runtimes,
            limits=holdout_limits,
            trial_id="holdout-primary",
            expected_truth=_generated_truth,
            stage="holdout-primary",
        )
    baseline_rows = _run_baseline_stage(
        opened["cases"],
        scratch_root=args.scratch_root.resolve(),
        limits=holdout_limits,
        trial_id="holdout-baseline",
        stage="holdout",
    )
    holdout_summary = _summarize_holdout_rows(portfolio_rows)
    primary_summary = _summarize_holdout_rows(primary_rows)
    portfolio_vs_primary = _compare_result_sets(
        portfolio_rows, primary_rows
    )
    selected_vs_baseline = _compare_external_to_baseline(
        portfolio_rows,
        baseline_rows,
        candidate_id=None,
        trial_id=None,
    )
    campaign: dict[str, object] = {
        "schema_version": HOLDOUT_CAMPAIGN_SCHEMA,
        "config_digest": config["config_digest"],
        "manifest_digest": manifest["manifest_digest"],
        "artifact_lock_digest": lock["lock_digest"],
        "code_bundle_digest": current_bundle["code_bundle_digest"],
        "open_campaign_digest": open_campaign["campaign_digest"],
        "selection_evidence_digest": selection[
            "selection_evidence_digest"
        ],
        "opening_receipt": opening_receipt,
        "portfolio_rows": portfolio_rows,
        "primary_rows": primary_rows,
        "baseline_rows": baseline_rows,
        "portfolio_summary": holdout_summary,
        "primary_summary": primary_summary,
        "portfolio_vs_primary": portfolio_vs_primary,
        "selected_vs_baseline": selected_vs_baseline,
        "invariants": {
            "holdout_opening_count": 1,
            "post_open_tuning_count": 0,
            "heavy_processes_run_concurrently": 1,
            "one_engine_invocation_per_portfolio_case": True,
            "positive_results_require_bgig_certificate": True,
            "network_service_invocation_count": 0,
            "product_solver_routing_changed": False,
        },
    }
    campaign["campaign_digest"] = canonical_digest(campaign)
    evidence = _compact_evidence(
        open_campaign=open_campaign,
        selection=selection,
        holdout_campaign=campaign,
    )
    _write_json_atomic(args.output, campaign)
    _write_json_atomic(args.evidence_output, evidence)
    print(
        f"HOLDOUT_TOURNAMENT=completed DIGEST={campaign['campaign_digest']}",
        flush=True,
    )
    print(
        "HOLDOUT_COMMON_SCOPE="
        f"{holdout_summary['representable_count']} "
        f"CERTIFIED={holdout_summary['certified_solution_count']} "
        f"TRUTH={holdout_summary['oracle_pass_count']}/"
        f"{holdout_summary['oracle_evaluable_count']}",
        flush=True,
    )
    return 0


def _load_common(args: argparse.Namespace) -> dict[str, object]:
    config = validate_external_tournament_config(_read_json(args.config))
    manifest = validate_external_solver_benchmark_manifest(
        _read_json(args.manifest)
    )
    lock = validate_external_solver_artifact_lock(
        _read_json(args.artifact_lock)
    )
    candidates = external_solver_candidate_catalog(lock)
    candidate_ids = [str(item) for item in config["candidate_ids"]]
    if candidate_ids != [str(item["candidate_id"]) for item in candidates]:
        raise RuntimeError(
            "Tournament config candidate order differs from artifact lock."
        )
    receipts = {
        candidate_id: verify_external_solver_artifacts(
            lock,
            candidate_id,
            args.artifact_root.resolve(),
        )
        for candidate_id in candidate_ids
    }
    runtimes = build_external_runtimes(
        candidates=candidates,
        receipts=receipts,
        artifact_root=args.artifact_root.resolve(),
        environment_root=args.environment_root.resolve(),
        java_home=args.java_home.resolve(),
        scratch_root=args.scratch_root.resolve(),
    )
    return {
        "config": config,
        "manifest": manifest,
        "lock": lock,
        "candidates": candidates,
        "candidate_ids": candidate_ids,
        "receipts": receipts,
        "runtimes": runtimes,
    }


def _run_external_stage(
    cases: Sequence[Mapping[str, object]],
    *,
    candidate_ids: Sequence[str],
    candidates: Sequence[Mapping[str, object]],
    lock: Mapping[str, object],
    receipts: Mapping[str, Mapping[str, object]],
    runtimes: Mapping[str, object],
    limits: ExternalSolverLimits,
    trial_id: str,
    expected_truth,
    stage: str,
) -> list[dict[str, object]]:
    candidate_by_id = {
        str(item["candidate_id"]): item for item in candidates
    }
    rows = []
    for candidate_id in candidate_ids:
        candidate = candidate_by_id[candidate_id]
        for case in cases:
            execution = run_external_solver_adapter(
                case,
                candidate_id,
                artifact_lock=lock,
                artifact_receipt=receipts[candidate_id],
                runtime=runtimes[candidate_id],
                limits=limits,
            )
            rows.append(
                _result_row(
                    case,
                    candidate_id=candidate_id,
                    candidate=candidate,
                    report=execution.report,
                    trial_id=trial_id,
                    expected_truth=expected_truth(case),
                )
            )
        print(
            f"{stage} {candidate_id}={len(cases)}/{len(cases)}",
            flush=True,
        )
    return rows


def _run_baseline_stage(
    cases: Sequence[Mapping[str, object]],
    *,
    scratch_root: Path,
    limits: ExternalSolverLimits,
    trial_id: str,
    stage: str,
) -> list[dict[str, object]]:
    rows = []
    common_cases = [
        case
        for case in cases
        if prepare_external_floor_case(case).problem is not None
    ]
    for case in common_cases:
        report = run_bgig_baseline_case(
            case,
            scratch_root=scratch_root,
            limits=limits,
        )
        rows.append(
            {
                "candidate_id": "current_bgig",
                "case_id": str(case["case_id"]),
                "family": str(
                    case.get("family", "historical_regression")
                ),
                "expected_truth": (
                    _generated_truth(case)
                    if isinstance(case.get("oracle"), Mapping)
                    else "regression_open"
                ),
                "trial_id": trial_id,
                "report": report,
            }
        )
    print(
        f"{stage} current_bgig={len(rows)}/{len(cases)} common-scope",
        flush=True,
    )
    return rows


def _result_row(
    case: Mapping[str, object],
    *,
    candidate_id: str,
    candidate: Mapping[str, object],
    report: Mapping[str, object],
    trial_id: str,
    expected_truth: str,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "candidate_family": str(candidate["family"]),
        "case_id": str(case["case_id"]),
        "family": str(case.get("family", "historical_regression")),
        "expected_truth": expected_truth,
        "trial_id": trial_id,
        "report": deepcopy(dict(report)),
    }


def _assert_exact_control_gate(
    rows: Sequence[Mapping[str, object]],
    candidates: Sequence[Mapping[str, object]],
) -> None:
    exact_by_id = {
        str(item["candidate_id"]): bool(item["exact_for_floor_model"])
        for item in candidates
    }
    failures = []
    for row in rows:
        expected_truth = str(row["expected_truth"])
        candidate_id = str(row["candidate_id"])
        expected_status = (
            "solution_found"
            if expected_truth == "feasible"
            else (
                "infeasible_proven"
                if exact_by_id[candidate_id]
                else "bounded_unknown"
            )
        )
        observed = str(row["report"]["status"])
        if observed != expected_status:
            failures.append(
                {
                    "candidate_id": candidate_id,
                    "case_id": row["case_id"],
                    "expected": expected_status,
                    "observed": observed,
                }
            )
    if failures:
        raise RuntimeError(f"Exact control gate failed: {failures}")


def _assert_no_candidate_failure(summary: Mapping[str, object]) -> None:
    failures = [
        item["candidate_id"]
        for item in summary["candidates"]
        if int(item["candidate_failure_count"]) != 0
    ]
    if failures:
        raise RuntimeError(
            f"Candidate failures in {summary['stage']}: {failures}"
        )


def _assert_discovery_gate(summary: Mapping[str, object]) -> None:
    _assert_no_candidate_failure(summary)
    if (
        int(summary["candidate_count"]) < 3
        or int(summary["external_family_count"]) < 3
        or any(
            int(item["worker_invocation_count"]) == 0
            for item in summary["candidates"]
        )
    ):
        raise RuntimeError(
            "Discovery did not compare three real external families."
        )


def _compare_external_to_baseline(
    external_rows: Sequence[Mapping[str, object]],
    baseline_rows: Sequence[Mapping[str, object]],
    *,
    candidate_id: str | None,
    trial_id: str | None,
) -> dict[str, object]:
    baseline = {
        str(row["case_id"]): row for row in baseline_rows
    }
    selected = {}
    for row in external_rows:
        if candidate_id is not None and row["candidate_id"] != candidate_id:
            continue
        if trial_id is not None and row["trial_id"] != trial_id:
            continue
        case_id = str(row["case_id"])
        if case_id in baseline:
            selected[case_id] = row
    if set(selected) != set(baseline):
        raise RuntimeError(
            "External and BGIG baseline common-scope cases differ."
        )
    comparison = _compare_result_sets(
        list(selected.values()), list(baseline.values())
    )
    baseline_unsupported_count = sum(
        int(row["report"]["status"] == "unsupported")
        for row in baseline.values()
    )
    comparison["baseline_unsupported_count"] = (
        baseline_unsupported_count
    )
    comparison["product_gain_demonstrated"] = bool(
        comparison["beats_second"]
        and baseline_unsupported_count == 0
    )
    comparison["comparison_status"] = (
        "product_comparable"
        if baseline_unsupported_count == 0
        else "baseline_cannot_represent_declared_benchmark_constraint"
    )
    return comparison


def _mapping_or_empty(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _compare_result_sets(
    first_rows: Sequence[Mapping[str, object]],
    second_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    first = {str(row["case_id"]): row for row in first_rows}
    second = {str(row["case_id"]): row for row in second_rows}
    common = sorted(set(first) & set(second))
    truth_delta = 0
    certified_delta = 0
    quality_wins = 0
    quality_losses = 0
    quality_ties = 0
    first_wall = 0.0
    second_wall = 0.0
    details = []
    for case_id in common:
        first_row = first[case_id]
        second_row = second[case_id]
        expected = str(first_row["expected_truth"])
        first_report = first_row["report"]
        second_report = second_row["report"]
        if expected != "regression_open":
            first_truth = _truth_matches(
                expected, str(first_report["status"])
            )
            second_truth = _truth_matches(
                expected, str(second_report["status"])
            )
            truth_delta += int(first_truth) - int(second_truth)
        first_certified = (
            _mapping_or_empty(
                first_report.get("recertification", {})
            ).get("certified")
            is True
        )
        second_certified = (
            _mapping_or_empty(
                second_report.get("recertification", {})
            ).get("certified")
            is True
        )
        certified_delta += int(first_certified) - int(second_certified)
        first_axes = quality_axes_from_report(first_report)
        second_axes = quality_axes_from_report(second_report)
        relation = "not_comparable"
        if first_axes is not None and second_axes is not None:
            if first_axes < second_axes:
                quality_wins += 1
                relation = "first_better"
            elif second_axes < first_axes:
                quality_losses += 1
                relation = "second_better"
            else:
                quality_ties += 1
                relation = "tie"
        first_wall += float(
            _mapping_or_empty(first_report.get("timing", {})).get(
                "total_wall_seconds"
            )
            or 0.0
        )
        second_wall += float(
            _mapping_or_empty(second_report.get("timing", {})).get(
                "total_wall_seconds"
            )
            or 0.0
        )
        details.append(
            {
                "case_id": case_id,
                "first_status": first_report["status"],
                "second_status": second_report["status"],
                "quality_relation": relation,
            }
        )
    beats_second = (
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
    return {
        "common_case_count": len(common),
        "truth_pass_delta": truth_delta,
        "certified_solution_delta": certified_delta,
        "quality_wins": quality_wins,
        "quality_losses": quality_losses,
        "quality_ties": quality_ties,
        "first_total_wall_seconds": round(first_wall, 6),
        "second_total_wall_seconds": round(second_wall, 6),
        "beats_second": beats_second,
        "details": details,
    }


def _summarize_holdout_rows(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    statuses: dict[str, int] = {}
    representable = 0
    certified = 0
    oracle_count = 0
    oracle_pass = 0
    candidate_failures = 0
    total_wall = 0.0
    routed: dict[str, int] = {}
    for row in rows:
        report = row["report"]
        status = str(report["status"])
        statuses[status] = statuses.get(status, 0) + 1
        candidate_id = str(row["candidate_id"])
        routed[candidate_id] = routed.get(candidate_id, 0) + 1
        if report.get("model") is not None:
            representable += 1
            oracle_count += 1
            oracle_pass += int(
                _truth_matches(str(row["expected_truth"]), status)
            )
        certified += int(
            _mapping_or_empty(
                report.get("recertification", {})
            ).get("certified")
            is True
        )
        candidate_failures += int(
            status in {"certificate_rejected", "external_error"}
        )
        total_wall += float(
            _mapping_or_empty(report.get("timing", {})).get(
                "total_wall_seconds"
            )
            or 0.0
        )
    summary = {
        "case_count": len(rows),
        "representable_count": representable,
        "oracle_evaluable_count": oracle_count,
        "oracle_pass_count": oracle_pass,
        "certified_solution_count": certified,
        "candidate_failure_count": candidate_failures,
        "statuses": dict(sorted(statuses.items())),
        "routed_case_count_by_candidate": dict(sorted(routed.items())),
        "total_wall_seconds": round(total_wall, 6),
    }
    summary["summary_digest"] = canonical_digest(summary)
    return summary


def _compact_evidence(
    *,
    open_campaign: Mapping[str, object],
    selection: Mapping[str, object],
    holdout_campaign: Mapping[str, object],
) -> dict[str, object]:
    rows = holdout_campaign["portfolio_rows"]
    compact_rows = [
        {
            "candidate_id": row["candidate_id"],
            "case_id": row["case_id"],
            "family": row["family"],
            "expected_truth": row["expected_truth"],
            "status": row["report"]["status"],
            "certified": _mapping_or_empty(
                row["report"].get("recertification", {})
            ).get("certified")
            is True,
            "report_digest": row["report"]["report_digest"],
        }
        for row in rows
    ]
    evidence: dict[str, object] = {
        "schema_version": COMPACT_EVIDENCE_SCHEMA,
        "config_digest": open_campaign["config_digest"],
        "manifest_digest": open_campaign["manifest_digest"],
        "artifact_lock_digest": open_campaign["artifact_lock_digest"],
        "code_bundle_digest": open_campaign["code_bundle"][
            "code_bundle_digest"
        ],
        "open_campaign_digest": open_campaign["campaign_digest"],
        "public_method_evidence": open_campaign[
            "public_method_evidence"
        ],
        "open_summaries": open_campaign["summaries"],
        "open_baseline_comparisons": open_campaign[
            "baseline_comparisons"
        ],
        "selection": selection,
        "holdout_campaign_digest": holdout_campaign["campaign_digest"],
        "opening_receipt": holdout_campaign["opening_receipt"],
        "holdout_portfolio_summary": holdout_campaign[
            "portfolio_summary"
        ],
        "holdout_primary_summary": holdout_campaign["primary_summary"],
        "holdout_portfolio_vs_primary": holdout_campaign[
            "portfolio_vs_primary"
        ],
        "holdout_selected_vs_bgig_baseline": holdout_campaign[
            "selected_vs_baseline"
        ],
        "holdout_results": compact_rows,
        "invariants": deepcopy(holdout_campaign["invariants"]),
    }
    evidence["evidence_digest"] = canonical_digest(evidence)
    return evidence


def _validate_open_campaign(
    value: object,
) -> dict[str, object]:
    campaign = dict(value) if isinstance(value, Mapping) else {}
    supplied = campaign.pop("campaign_digest", None)
    if (
        campaign.get("schema_version") != OPEN_CAMPAIGN_SCHEMA
        or not isinstance(supplied, str)
        or canonical_digest(campaign) != supplied
    ):
        raise RuntimeError("Open tournament campaign digest mismatch.")
    campaign["campaign_digest"] = supplied
    return campaign


def _code_bundle(*, config_path: Path) -> dict[str, object]:
    paths = [
        ROOT
        / "src"
        / "board_game_insert_generator"
        / "external_solver_adapters.py",
        ROOT
        / "src"
        / "board_game_insert_generator"
        / "external_solver_artifacts.py",
        ROOT
        / "src"
        / "board_game_insert_generator"
        / "external_solver_benchmark_corpus.py",
        ROOT
        / "src"
        / "board_game_insert_generator"
        / "external_solver_tournament.py",
        ROOT / "scripts" / "solver" / "run_external_solver_tournament.py",
        ROOT / "scripts" / "solver" / "external_tournament_runtime.py",
        ROOT
        / "scripts"
        / "solver"
        / "external_workers"
        / "_floor_worker_protocol.py",
        ROOT
        / "scripts"
        / "solver"
        / "external_workers"
        / "ortools_cp_sat_floor_worker.py",
        ROOT
        / "scripts"
        / "solver"
        / "external_workers"
        / "highs_mip_floor_worker.py",
        ROOT
        / "scripts"
        / "solver"
        / "external_workers"
        / "scip_mip_floor_worker.py",
        ROOT
        / "scripts"
        / "solver"
        / "external_workers"
        / "LaffFloorWorker.java",
        ROOT
        / "scripts"
        / "solver"
        / "external_workers"
        / "bgig_baseline_worker.py",
        config_path,
    ]
    files = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path.read_bytes()).hexdigest(),
        }
        for path in paths
    ]
    return {
        "schema_version": "bgig.external_solver_code_bundle.v1",
        "files": files,
        "code_bundle_digest": canonical_digest(files),
    }


def _write_or_verify_opening_receipt(
    path: Path,
    receipt: Mapping[str, object],
    *,
    resume: bool,
) -> None:
    if path.exists():
        if not resume or _read_json(path) != dict(receipt):
            raise RuntimeError(
                "Holdout was already opened with a different receipt."
            )
        return
    _write_json_atomic(path, receipt)


def _limits(value: Mapping[str, object]) -> ExternalSolverLimits:
    return ExternalSolverLimits(
        wall_seconds=float(value["wall_seconds"]),
        memory_mebibytes=int(value["memory_mebibytes"]),
        threads=int(value["threads"]),
        seed=int(value["seed"]),
    )


def _generated_truth(case: Mapping[str, object]) -> str:
    oracle = case.get("oracle")
    if not isinstance(oracle, Mapping):
        raise RuntimeError("Generated tournament case has no oracle.")
    truth = str(oracle.get("expected_truth"))
    if truth not in {"feasible", "impossible"}:
        raise RuntimeError("Generated tournament truth is invalid.")
    return truth


def _truth_matches(expected_truth: str, status: str) -> bool:
    return (
        expected_truth == "feasible" and status == "solution_found"
    ) or (
        expected_truth == "impossible"
        and status == "infeasible_proven"
    )


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain one JSON object.")
    return value


def _write_json_atomic(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(
        json.dumps(dict(value), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
