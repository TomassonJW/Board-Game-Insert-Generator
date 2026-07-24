"""Execute P64-L08F en deux phases : ouvert, puis holdout unique."""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.external_solver_adapters import (  # noqa: E402
    ExternalSolverLimits,
    ExternalSolverRuntime,
)
from board_game_insert_generator.external_solver_artifacts import (  # noqa: E402
    verify_external_solver_artifacts,
)
from board_game_insert_generator.incremental_project_state import canonical_digest  # noqa: E402
from board_game_insert_generator.real_3d_solver_adapters import (  # noqa: E402
    STATUS_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND,
    STATUS_UNSUPPORTED,
    build_real_3d_exact_controls,
    run_real_3d_adapter,
)
from board_game_insert_generator.real_3d_solver_corpus import (  # noqa: E402
    materialize_case_problem,
    validate_public_manifest,
    validate_sealed_holdout,
    verify_sealed_holdout,
)
from board_game_insert_generator.real_3d_solver_tournament import (  # noqa: E402
    EXTERNAL_CANDIDATE_IDS,
    REAL_3D_EVIDENCE_SCHEMA_V1,
    REAL_3D_HOLDOUT_CAMPAIGN_SCHEMA_V1,
    REAL_3D_OPEN_CAMPAIGN_SCHEMA_V1,
    REAL_3D_OPENING_RECEIPT_SCHEMA_V1,
    build_holdout_decision,
    build_result_row,
    build_selection_evidence,
    materialize_tournament_problem,
    summarize_rows,
    truth_matches,
    validate_selection_evidence,
)
from external_tournament_runtime import run_bgig_baseline_case  # noqa: E402
from run_real_3d_adapter_controls import (  # noqa: E402
    LOCK_PATH,
    build_runtimes,
    verify_packingsolver_build,
)

OPENED_CACHE_SCHEMA = "bgig.real_3d_opened_holdout_cache.v1"
CHECKPOINT_SCHEMA = "bgig.real_3d_tournament_checkpoint.v1"
WORKERS = ROOT / "scripts" / "solver" / "external_workers"


def main() -> int:
    parser = argparse.ArgumentParser()
    phases = parser.add_subparsers(dest="phase", required=True)
    open_parser = phases.add_parser("open")
    _common_arguments(open_parser)
    open_parser.add_argument("--output", type=Path, required=True)
    open_parser.add_argument("--selection-output", type=Path, required=True)
    open_parser.add_argument("--checkpoint", type=Path, required=True)
    open_parser.add_argument("--resume", action="store_true")
    holdout_parser = phases.add_parser("holdout")
    _common_arguments(holdout_parser)
    holdout_parser.add_argument("--open-campaign", type=Path, required=True)
    holdout_parser.add_argument("--selection", type=Path, required=True)
    holdout_parser.add_argument("--sealed-holdout", type=Path, required=True)
    holdout_parser.add_argument("--opened-cache", type=Path, required=True)
    holdout_parser.add_argument("--opening-receipt", type=Path, required=True)
    holdout_parser.add_argument("--output", type=Path, required=True)
    holdout_parser.add_argument("--evidence-output", type=Path, required=True)
    holdout_parser.add_argument("--checkpoint", type=Path, required=True)
    holdout_parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    return _run_open(args) if args.phase == "open" else _run_holdout(args)


def _common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--packingsolver-binary", type=Path, required=True)


def _run_open(args: argparse.Namespace) -> int:
    if (args.output.exists() or args.selection_output.exists()) and not args.resume:
        raise RuntimeError("Open outputs already exist; use --resume after interruption.")
    common = _load_common(args)
    checkpoint = _load_checkpoint(
        args.checkpoint, phase="open", binding=common["open_binding"], resume=args.resume
    )
    exact_rows = _run_controls(
        build_real_3d_exact_controls(),
        common=common,
        limits=_limits(common["config"]["stages"]["exact_controls"]),
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    _assert_exact_controls(exact_rows)
    records = common["manifest"]["open_case_records"]
    regression = [value for value in records if value["split"] == "regression"]
    discovery = [value for value in records if value["split"] == "discovery"]
    tuning = [value for value in records if value["split"] == "tuning"]
    regression_rows = _run_records(
        regression,
        candidate_ids=(*EXTERNAL_CANDIDATE_IDS, "current_bgig"),
        common=common,
        limits=_limits(common["config"]["stages"]["regression"]),
        profile="balanced",
        stage="regression-reference",
        trial_id="regression-reference",
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    product_regression = _run_product_regression(
        regression[0],
        common=common,
        limits=_limits(common["config"]["stages"]["regression"]),
    )
    discovery_limits = _limits(common["config"]["stages"]["discovery"])
    discovery_rows = _run_records(
        discovery,
        candidate_ids=EXTERNAL_CANDIDATE_IDS,
        common=common,
        limits=discovery_limits,
        profile="balanced",
        stage="discovery",
        trial_id="discovery",
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    baseline_discovery = _run_records(
        discovery,
        candidate_ids=("current_bgig",),
        common=common,
        limits=discovery_limits,
        profile="balanced",
        stage="discovery",
        trial_id="baseline-discovery",
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    tuning_rows = []
    for trial in common["config"]["stages"]["tuning_trials"]:
        tuning_rows.extend(
            _run_records(
                tuning,
                candidate_ids=EXTERNAL_CANDIDATE_IDS,
                common=common,
                limits=_limits(trial),
                profile=str(trial["profile"]),
                stage="tuning",
                trial_id=str(trial["trial_id"]),
                checkpoint=checkpoint,
                checkpoint_path=args.checkpoint,
            )
        )
    baseline_trial = common["config"]["stages"]["tuning_trials"][0]
    baseline_tuning = _run_records(
        tuning,
        candidate_ids=("current_bgig",),
        common=common,
        limits=_limits(baseline_trial),
        profile="balanced",
        stage="tuning",
        trial_id="baseline-tuning",
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    selection = build_selection_evidence(
        open_rows=[*discovery_rows, *tuning_rows],
        baseline_rows=[*baseline_discovery, *baseline_tuning],
        config_digest=common["config_digest"],
        manifest_digest=common["manifest"]["manifest_digest"],
        artifact_bundle_digest=common["artifact_bundle_digest"],
        code_bundle_digest=common["code_bundle"]["code_bundle_digest"],
        holdout_limits=common["config"]["stages"]["holdout"],
        maximum_complements=int(common["config"]["selection"]["maximum_complements"]),
    )
    campaign = {
        "schema_version": REAL_3D_OPEN_CAMPAIGN_SCHEMA_V1,
        "config_digest": common["config_digest"],
        "manifest_digest": common["manifest"]["manifest_digest"],
        "artifact_bundle_digest": common["artifact_bundle_digest"],
        "code_bundle": common["code_bundle"],
        "rows": {
            "exact_controls": exact_rows,
            "regression_reference": regression_rows,
            "product_regression": [product_regression],
            "discovery": discovery_rows,
            "tuning": tuning_rows,
            "baseline_discovery": baseline_discovery,
            "baseline_tuning": baseline_tuning,
        },
        "summaries": {
            "exact_controls": summarize_rows(exact_rows),
            "regression_reference": summarize_rows(regression_rows),
            "discovery": summarize_rows(discovery_rows),
            "tuning": summarize_rows(tuning_rows),
            "baseline_discovery": summarize_rows(baseline_discovery),
            "baseline_tuning": summarize_rows(baseline_tuning),
        },
        "selection_digest": selection["selection_digest"],
        "invariants": {
            "external_engines_executed": 4,
            "external_families_executed": 4,
            "positive_witness_transmitted": False,
            "holdout_case_count_seen": 0,
            "holdout_path_accepted_by_open_phase": False,
            "heavy_processes_concurrently": 1,
            "network_service_invocation_count": 0,
            "global_install_count": 0,
        },
    }
    campaign["campaign_digest"] = canonical_digest(campaign)
    _write_json_atomic(args.selection_output, selection)
    _write_json_atomic(args.output, campaign)
    print(f"OPEN_REAL_3D_TOURNAMENT_OK digest={campaign['campaign_digest']}", flush=True)
    print(
        f"SEALED_SELECTION primary={selection['primary_candidate_id']} "
        f"selected={','.join(selection['selected_candidate_ids'])} "
        f"digest={selection['selection_digest']}",
        flush=True,
    )
    return 0


def _run_holdout(args: argparse.Namespace) -> int:
    if (args.output.exists() or args.evidence_output.exists()) and not args.resume:
        raise RuntimeError("Holdout outputs exist; the unique campaign cannot be overwritten.")
    common = _load_common(args)
    selection = validate_selection_evidence(_read_json(args.selection))
    open_campaign = _validate_bound_document(
        _read_json(args.open_campaign), REAL_3D_OPEN_CAMPAIGN_SCHEMA_V1, "campaign_digest"
    )
    if (
        selection["config_digest"] != common["config_digest"]
        or selection["manifest_digest"] != common["manifest"]["manifest_digest"]
        or selection["artifact_bundle_digest"] != common["artifact_bundle_digest"]
        or selection["code_bundle_digest"] != common["code_bundle"]["code_bundle_digest"]
        or open_campaign["selection_digest"] != selection["selection_digest"]
    ):
        raise RuntimeError("Holdout bindings differ from the sealed open campaign.")
    records, opening_receipt = _open_holdout_once(args, common=common, selection=selection)
    holdout_binding = canonical_digest(
        {
            "open_binding": common["open_binding"],
            "selection_digest": selection["selection_digest"],
            "opening_receipt_digest": opening_receipt["opening_receipt_digest"],
        }
    )
    checkpoint = _load_checkpoint(
        args.checkpoint, phase="holdout", binding=holdout_binding, resume=args.resume
    )
    portfolio_rows = []
    for record in records:
        candidate_id = str(selection["family_routes"][str(record["family"])])
        portfolio_rows.extend(
            _run_records(
                [record],
                candidate_ids=(candidate_id,),
                common=common,
                limits=_holdout_limits(selection, candidate_id),
                profile=_selected_profile(common["config"], selection, candidate_id),
                stage="holdout-portfolio",
                trial_id="holdout-portfolio",
                checkpoint=checkpoint,
                checkpoint_path=args.checkpoint,
            )
        )
    primary_id = str(selection["primary_candidate_id"])
    if len(selection["selected_candidate_ids"]) == 1:
        primary_rows = deepcopy(portfolio_rows)
    else:
        primary_rows = _run_records(
            records,
            candidate_ids=(primary_id,),
            common=common,
            limits=_holdout_limits(selection, primary_id),
            profile=_selected_profile(common["config"], selection, primary_id),
            stage="holdout-primary",
            trial_id="holdout-primary",
            checkpoint=checkpoint,
            checkpoint_path=args.checkpoint,
        )
    baseline_rows = _run_records(
        records,
        candidate_ids=("current_bgig",),
        common=common,
        limits=_holdout_limits(selection, primary_id),
        profile="balanced",
        stage="holdout-baseline",
        trial_id="holdout-baseline",
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    decision = build_holdout_decision(
        portfolio_rows=portfolio_rows,
        primary_rows=primary_rows,
        baseline_rows=baseline_rows,
        selected_candidate_ids=selection["selected_candidate_ids"],
        primary_candidate_id=primary_id,
    )
    verdict = decision["verdict"]
    campaign = {
        "schema_version": REAL_3D_HOLDOUT_CAMPAIGN_SCHEMA_V1,
        "config_digest": common["config_digest"],
        "manifest_digest": common["manifest"]["manifest_digest"],
        "artifact_bundle_digest": common["artifact_bundle_digest"],
        "code_bundle_digest": common["code_bundle"]["code_bundle_digest"],
        "open_campaign_digest": open_campaign["campaign_digest"],
        "selection_digest": selection["selection_digest"],
        "opening_receipt": opening_receipt,
        "portfolio_rows": portfolio_rows,
        "primary_rows": primary_rows,
        "baseline_rows": baseline_rows,
        "retained_rows": decision["retained_rows"],
        "summaries": {
            "portfolio": summarize_rows(portfolio_rows),
            "primary": summarize_rows(primary_rows),
            "baseline": summarize_rows(baseline_rows),
            "retained": summarize_rows(decision["retained_rows"]),
        },
        "portfolio_vs_primary": decision["portfolio_vs_primary"],
        "retained_vs_current_bgig": decision["retained_vs_current_bgig"],
        "verdict": verdict,
        "invariants": {
            "holdout_opening_count": 1,
            "post_open_tuning_count": 0,
            "one_engine_invocation_per_portfolio_case": True,
            "positive_witness_transmitted": False,
            "fresh_bgig_recertification_required": True,
            "heavy_processes_concurrently": 1,
            "network_service_invocation_count": 0,
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
        f"HOLDOUT_REAL_3D_TOURNAMENT_OK digest={campaign['campaign_digest']} "
        f"decision={verdict['decision']}",
        flush=True,
    )
    return 0


def _load_common(args: argparse.Namespace) -> dict[str, object]:
    config = _validate_config(_read_json(args.config))
    manifest = validate_public_manifest(_read_json(args.manifest))
    lock = _read_json(LOCK_PATH)
    receipts = {
        candidate_id: verify_external_solver_artifacts(
            lock, candidate_id, args.artifact_root.resolve()
        )
        for candidate_id in ("ortools_cp_sat", "scip", "laff")
    }
    receipts["packingsolver_box"] = verify_packingsolver_build(args.packingsolver_binary.resolve())
    runtimes = build_runtimes(
        args.artifact_root.resolve(),
        args.runtime_root.resolve(),
        args.scratch_root.resolve(),
        args.packingsolver_binary.resolve(),
        receipts,
    )
    current_worker = WORKERS / "bgig_real_3d_worker.py"
    current_bundle = _file_bundle(
        [
            current_worker,
            ROOT / "src" / "board_game_insert_generator" / "free_3d_beam_solver.py",
            ROOT / "src" / "board_game_insert_generator" / "real_3d_solver_adapters.py",
        ],
        "current_bgig_real_3d",
    )
    receipts["current_bgig"] = {
        "candidate_id": "current_bgig",
        "bundle_digest": current_bundle,
        "verified_before_execution": True,
        "product_gate": "current_product_baseline",
    }
    runtimes["current_bgig"] = ExternalSolverRuntime(
        candidate_id="current_bgig",
        command=(sys.executable, "-S", str(current_worker.resolve())),
        environment=(("PYTHONPATH", str((ROOT / "src").resolve())),),
        scratch_root=str(args.scratch_root.resolve()),
        worker_digest=_file_bundle([current_worker], current_bundle),
    )
    code_bundle = _code_bundle(args.config.resolve())
    artifact_bundle_digest = canonical_digest(
        {
            candidate_id: receipts[candidate_id]["bundle_digest"]
            for candidate_id in (*EXTERNAL_CANDIDATE_IDS, "current_bgig")
        }
    )
    open_binding = canonical_digest(
        {
            "config_digest": config["config_digest"],
            "manifest_digest": manifest["manifest_digest"],
            "artifact_bundle_digest": artifact_bundle_digest,
            "code_bundle_digest": code_bundle["code_bundle_digest"],
        }
    )
    return {
        "config": config,
        "config_digest": config["config_digest"],
        "manifest": manifest,
        "receipts": receipts,
        "runtimes": runtimes,
        "artifact_bundle_digest": artifact_bundle_digest,
        "code_bundle": code_bundle,
        "open_binding": open_binding,
        "scratch_root": args.scratch_root.resolve(),
    }


def _run_controls(
    controls: Sequence[Mapping[str, object]],
    *,
    common: Mapping[str, object],
    limits: ExternalSolverLimits,
    checkpoint: dict[str, object],
    checkpoint_path: Path,
) -> list[dict[str, object]]:
    rows = []
    for candidate_id in EXTERNAL_CANDIDATE_IDS:
        for control in controls:
            key = f"exact-controls|{candidate_id}|{control['control_id']}"
            stored = checkpoint["rows"].get(key)
            if stored is not None:
                rows.append(deepcopy(stored))
                continue
            report = run_real_3d_adapter(
                control,
                candidate_id=candidate_id,
                runtime=_runtime_profile(common["runtimes"][candidate_id], "balanced"),
                limits=limits,
                artifact_receipt=common["receipts"][candidate_id],
                exact_control=True,
            )
            row = _control_row(control, candidate_id, report)
            checkpoint["rows"][key] = row
            _write_json_atomic(checkpoint_path, checkpoint)
            rows.append(row)
            print(
                f"exact-controls candidate={candidate_id} "
                f"case={control['control_id']} status={row['status']}",
                flush=True,
            )
    return rows


def _run_records(
    records: Sequence[Mapping[str, object]],
    *,
    candidate_ids: Sequence[str],
    common: Mapping[str, object],
    limits: ExternalSolverLimits,
    profile: str,
    stage: str,
    trial_id: str,
    checkpoint: dict[str, object],
    checkpoint_path: Path,
) -> list[dict[str, object]]:
    rows = []
    for candidate_id in candidate_ids:
        for record in records:
            key = f"{stage}|{trial_id}|{candidate_id}|{record['case_id']}"
            stored = checkpoint["rows"].get(key)
            if stored is not None:
                rows.append(deepcopy(stored))
                continue
            problem = materialize_tournament_problem(record)
            if problem is None:
                problem = materialize_case_problem(record)
            report = run_real_3d_adapter(
                problem,
                candidate_id=candidate_id,
                runtime=_runtime_profile(common["runtimes"][candidate_id], profile),
                limits=limits,
                artifact_receipt=common["receipts"][candidate_id],
                exact_control=record["expected"] == "infeasible",
            )
            row = build_result_row(
                record,
                candidate_id=candidate_id,
                report=report,
                stage=stage,
                trial_id=trial_id,
            )
            checkpoint["rows"][key] = row
            _write_json_atomic(checkpoint_path, checkpoint)
            rows.append(row)
            print(
                f"{stage} trial={trial_id} candidate={candidate_id} "
                f"case={record['case_id']} status={row['status']}",
                flush=True,
            )
    return rows


def _run_product_regression(
    record: Mapping[str, object],
    *,
    common: Mapping[str, object],
    limits: ExternalSolverLimits,
) -> dict[str, object]:
    fixture = _read_json(ROOT / "tests" / "fixtures" / "p64_l06a_reviewed_real_case.v1.json")
    source = next(
        value
        for value in fixture["cases"]
        if value["case_id"] == record["recipe"]["source"]["case_id"]
    )
    project_digest = canonical_digest(source["project"])
    if project_digest != record["recipe"]["project_digest"]:
        raise RuntimeError("Reviewed regression project digest changed.")
    case = {
        "case_id": record["case_id"],
        "family": "real-anonymized",
        "split": "regression",
        "project": source["project"],
        "project_digest": project_digest,
        "solver_settings": {"method": "auto", "effort": "normal"},
        "features": {
            "rotation_policy_target": "permitted",
            "execution_mode": "cold",
        },
    }
    report = run_bgig_baseline_case(case, scratch_root=common["scratch_root"], limits=limits)
    status = str(report["status"])
    execution = report.get("execution") if isinstance(report.get("execution"), Mapping) else {}
    row = {
        "candidate_id": "current_bgig_product",
        "case_id": record["case_id"],
        "case_digest": record["case_digest"],
        "family": record["family"],
        "tier": record["tier"],
        "expected": "bounded_unknown",
        "stage": "product-regression",
        "trial_id": "product-regression-normal",
        "status": status,
        "truth_pass": truth_matches("bounded_unknown", status),
        "representable": status != STATUS_UNSUPPORTED,
        "candidate_failure": status in {"certificate_rejected", "external_error"},
        "certified": bool(
            isinstance(report.get("recertification"), Mapping)
            and report["recertification"].get("certified") is True
        ),
        "worker_invocation_count": 1,
        "unsupported_constraints": list(report.get("unsupported_constraints", [])),
        "quality": {},
        "execution": deepcopy(dict(execution)),
        "report_digest": report.get("report_digest"),
    }
    row["row_digest"] = canonical_digest(row)
    return row


def _open_holdout_once(
    args: argparse.Namespace,
    *,
    common: Mapping[str, object],
    selection: Mapping[str, object],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    if args.opening_receipt.exists() or args.opened_cache.exists():
        if not args.resume or not (args.opening_receipt.exists() and args.opened_cache.exists()):
            raise RuntimeError("Partial or unauthorized holdout reopening state.")
        receipt = _validate_bound_document(
            _read_json(args.opening_receipt),
            REAL_3D_OPENING_RECEIPT_SCHEMA_V1,
            "opening_receipt_digest",
        )
        cache = _validate_bound_document(
            _read_json(args.opened_cache), OPENED_CACHE_SCHEMA, "cache_digest"
        )
        if (
            receipt["selection_digest"] != selection["selection_digest"]
            or cache["selection_digest"] != selection["selection_digest"]
            or receipt["sealed_holdout_digest"] != cache["sealed_holdout_digest"]
        ):
            raise RuntimeError("Holdout resume binding mismatch.")
        return [dict(value) for value in cache["case_records"]], receipt
    sealed = validate_sealed_holdout(_read_json(args.sealed_holdout))
    verify_sealed_holdout(common["manifest"], sealed)
    cache = {
        "schema_version": OPENED_CACHE_SCHEMA,
        "selection_digest": selection["selection_digest"],
        "sealed_holdout_digest": sealed["sealed_holdout_digest"],
        "case_records": sealed["case_records"],
    }
    cache["cache_digest"] = canonical_digest(cache)
    receipt = {
        "schema_version": REAL_3D_OPENING_RECEIPT_SCHEMA_V1,
        "selection_digest": selection["selection_digest"],
        "manifest_digest": common["manifest"]["manifest_digest"],
        "sealed_holdout_digest": sealed["sealed_holdout_digest"],
        "case_count": len(sealed["case_records"]),
        "holdout_opening_count": 1,
        "post_open_tuning_allowed": False,
    }
    receipt["opening_receipt_digest"] = canonical_digest(receipt)
    _write_json_atomic(args.opened_cache, cache)
    _write_json_atomic(args.opening_receipt, receipt)
    return [dict(value) for value in sealed["case_records"]], receipt


def _compact_evidence(
    *,
    open_campaign: Mapping[str, object],
    selection: Mapping[str, object],
    holdout_campaign: Mapping[str, object],
) -> dict[str, object]:
    compact_rows = [
        {
            "candidate_id": value["candidate_id"],
            "case_id": value["case_id"],
            "family": value["family"],
            "tier": value["tier"],
            "expected": value["expected"],
            "status": value["status"],
            "truth_pass": value["truth_pass"],
            "certified": value["certified"],
            "quality": value["quality"],
            "execution": value["execution"],
            "report_digest": value["report_digest"],
            "row_digest": value["row_digest"],
        }
        for value in holdout_campaign["portfolio_rows"]
    ]
    evidence = {
        "schema_version": REAL_3D_EVIDENCE_SCHEMA_V1,
        "config_digest": open_campaign["config_digest"],
        "manifest_digest": open_campaign["manifest_digest"],
        "artifact_bundle_digest": open_campaign["artifact_bundle_digest"],
        "code_bundle_digest": open_campaign["code_bundle"]["code_bundle_digest"],
        "open_campaign_digest": open_campaign["campaign_digest"],
        "open_summaries": open_campaign["summaries"],
        "selection": deepcopy(dict(selection)),
        "opening_receipt": holdout_campaign["opening_receipt"],
        "holdout_campaign_digest": holdout_campaign["campaign_digest"],
        "holdout_summaries": holdout_campaign["summaries"],
        "portfolio_vs_primary": holdout_campaign["portfolio_vs_primary"],
        "retained_vs_current_bgig": holdout_campaign["retained_vs_current_bgig"],
        "verdict": holdout_campaign["verdict"],
        "holdout_results": compact_rows,
        "invariants": deepcopy(dict(holdout_campaign["invariants"])),
    }
    evidence["evidence_digest"] = canonical_digest(evidence)
    return evidence


def _control_row(
    control: Mapping[str, object], candidate_id: str, report: Mapping[str, object]
) -> dict[str, object]:
    status = str(report["status"])
    expected = str(control["expected"])
    row = {
        "candidate_id": candidate_id,
        "case_id": control["control_id"],
        "case_digest": control["problem_digest"],
        "family": "exact-controls",
        "tier": "small",
        "expected": expected,
        "stage": "exact-controls",
        "trial_id": "exact-controls",
        "status": status,
        "truth_pass": truth_matches(expected, status),
        "representable": status != STATUS_UNSUPPORTED,
        "candidate_failure": status in {"certificate_rejected", "external_error"},
        "certified": bool(report["recertification"]["certified"]),
        "worker_invocation_count": int(report["worker_invocation_count"]),
        "unsupported_constraints": list(report["unsupported_constraints"]),
        "quality": deepcopy(dict(report.get("quality", {}))),
        "execution": {
            key: report["execution"].get(key)
            for key in (
                "execution_status",
                "exit_code",
                "total_wall_seconds",
                "cpu_seconds",
                "peak_working_set_bytes",
                "input_digest",
            )
        },
        "report_digest": report["report_digest"],
    }
    row["row_digest"] = canonical_digest(row)
    return row


def _assert_exact_controls(rows: Sequence[Mapping[str, object]]) -> None:
    failures = []
    for row in rows:
        if row["candidate_id"] in {"ortools_cp_sat", "scip"}:
            wanted = (
                STATUS_SOLUTION_FOUND if row["expected"] == "feasible" else STATUS_INFEASIBLE_PROVEN
            )
            if row["status"] != wanted:
                failures.append((row["candidate_id"], row["case_id"], row["status"]))
        elif row["case_id"] == "stacking-feasible" and row["status"] != STATUS_SOLUTION_FOUND:
            failures.append((row["candidate_id"], row["case_id"], row["status"]))
    if failures:
        raise RuntimeError(f"Real-3D exact control gate failed: {failures}")


def _runtime_profile(runtime: ExternalSolverRuntime, profile: str) -> ExternalSolverRuntime:
    environment = dict(runtime.environment)
    environment["BGIG_REAL3D_PROFILE"] = profile
    return replace(runtime, environment=tuple(sorted(environment.items())))


def _holdout_limits(selection: Mapping[str, object], candidate_id: str) -> ExternalSolverLimits:
    limits = selection["holdout_limits"]
    return ExternalSolverLimits(
        wall_seconds=float(limits["wall_seconds"]),
        memory_mebibytes=int(limits["memory_mebibytes"]),
        threads=int(limits["threads"]),
        seed=_selected_seed(selection, candidate_id),
    )


def _selected_seed(selection: Mapping[str, object], candidate_id: str) -> int:
    trial = str(selection["selected_trial_by_candidate"].get(candidate_id, ""))
    return 6419 if "6419" in trial else 6408


def _selected_profile(
    config: Mapping[str, object],
    selection: Mapping[str, object],
    candidate_id: str,
) -> str:
    trial_id = str(selection["selected_trial_by_candidate"].get(candidate_id, ""))
    for trial in config["stages"]["tuning_trials"]:
        if trial["trial_id"] == trial_id:
            return str(trial["profile"])
    return "balanced"


def _limits(value: Mapping[str, object]) -> ExternalSolverLimits:
    return ExternalSolverLimits(
        wall_seconds=float(value["wall_seconds"]),
        memory_mebibytes=int(value["memory_mebibytes"]),
        threads=int(value["threads"]),
        seed=int(value["seed"]),
    )


def _validate_config(value: Mapping[str, object]) -> dict[str, object]:
    payload = deepcopy(dict(value))
    if (
        payload.get("schema_version") != "bgig.real_3d_tournament_config.v1"
        or tuple(payload.get("candidate_ids", [])) != EXTERNAL_CANDIDATE_IDS
        or payload.get("selection", {}).get("post_selection_tuning_allowed") is not False
        or payload.get("invariants", {}).get("heavy_processes_concurrently") != 1
        or payload.get("invariants", {}).get("holdout_openings") != 1
    ):
        raise RuntimeError("Invalid P64-L08F tournament configuration.")
    payload["config_digest"] = canonical_digest(payload)
    return payload


def _load_checkpoint(
    path: Path,
    *,
    phase: str,
    binding: str,
    resume: bool,
) -> dict[str, object]:
    if path.exists():
        if not resume:
            raise RuntimeError("Checkpoint exists; use --resume after verification.")
        checkpoint = _read_json(path)
        supplied = checkpoint.pop("checkpoint_digest", None)
        if (
            checkpoint.get("schema_version") != CHECKPOINT_SCHEMA
            or checkpoint.get("phase") != phase
            or checkpoint.get("binding") != binding
            or supplied != canonical_digest(checkpoint)
            or not isinstance(checkpoint.get("rows"), dict)
        ):
            raise RuntimeError("Tournament checkpoint binding is invalid.")
        checkpoint["checkpoint_digest"] = supplied
        return checkpoint
    checkpoint = {
        "schema_version": CHECKPOINT_SCHEMA,
        "phase": phase,
        "binding": binding,
        "rows": {},
    }
    checkpoint["checkpoint_digest"] = canonical_digest(checkpoint)
    _write_json_atomic(path, checkpoint)
    return checkpoint


def _write_json_atomic(path: Path, value: Mapping[str, object]) -> None:
    payload = deepcopy(dict(value))
    if payload.get("schema_version") == CHECKPOINT_SCHEMA:
        payload.pop("checkpoint_digest", None)
        payload["checkpoint_digest"] = canonical_digest(payload)
        value.clear()
        value.update(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain one JSON object.")
    return value


def _validate_bound_document(
    value: Mapping[str, object], schema: str, digest_field: str
) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop(digest_field, None)
    if payload.get("schema_version") != schema or supplied != canonical_digest(payload):
        raise RuntimeError(f"Invalid bound document for schema {schema}.")
    payload[digest_field] = supplied
    return payload


def _file_bundle(paths: Sequence[Path], binding: str) -> str:
    return canonical_digest(
        {
            "binding": binding,
            "files": [
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256": sha256(path.read_bytes()).hexdigest(),
                }
                for path in paths
            ],
        }
    )


def _code_bundle(config_path: Path) -> dict[str, object]:
    paths = [
        ROOT / "src" / "board_game_insert_generator" / "real_3d_solver_corpus.py",
        ROOT / "src" / "board_game_insert_generator" / "real_3d_solver_adapters.py",
        ROOT / "src" / "board_game_insert_generator" / "real_3d_solver_tournament.py",
        ROOT / "scripts" / "solver" / "run_real_3d_solver_tournament.py",
        ROOT / "scripts" / "solver" / "run_real_3d_adapter_controls.py",
        ROOT / "scripts" / "solver" / "external_workers" / "_real_3d_worker_common.py",
        ROOT / "scripts" / "solver" / "external_workers" / "ortools_real_3d_worker.py",
        ROOT / "scripts" / "solver" / "external_workers" / "scip_real_3d_worker.py",
        ROOT / "scripts" / "solver" / "external_workers" / "packingsolver_real_3d_worker.py",
        ROOT / "scripts" / "solver" / "external_workers" / "laff_real_3d_worker.py",
        ROOT / "scripts" / "solver" / "external_workers" / "LaffReal3DWorker.java",
        ROOT / "scripts" / "solver" / "external_workers" / "bgig_real_3d_worker.py",
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
        "schema_version": "bgig.real_3d_code_bundle.v1",
        "files": files,
        "code_bundle_digest": canonical_digest(files),
    }


if __name__ == "__main__":
    raise SystemExit(main())
