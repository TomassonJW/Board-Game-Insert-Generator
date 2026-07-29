#!/usr/bin/env python3
"""Attribue finalisation et CAD IR sur les succès de la baseline P64-L09W-A."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SOLVER_SCRIPTS = ROOT / "scripts" / "solver"
for path in (SRC, SOLVER_SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from board_game_insert_generator.partition_cad import build_partition_cad  # noqa: E402
from board_game_insert_generator.scip_product_solver import (  # noqa: E402
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    configure_scip_product_runtime,
)
from board_game_insert_generator.solver_benchmark_adapters import (  # noqa: E402
    recertify_minimal_layout_plan,
)
from board_game_insert_generator.staged_calculation import (  # noqa: E402
    ARTIFACT_KIND_FINALIZED,
)
from run_p64_l09w_a_baseline import (  # noqa: E402
    _WorkingSetSampler,
    _code_bundle_digest,
    _placement_digest,
    _prepared_session,
    _read_json,
    _write_json_atomic,
    build_fixture_inventory,
)


SCHEMA_VERSION = "bgig.p64_l09w_a_downstream_audit.v1"


def _verified_document(path: Path, digest_key: str) -> dict[str, object]:
    value = _read_json(path)
    supplied = value.pop(digest_key, None)
    if not isinstance(supplied, str) or supplied != canonical_digest(value):
        raise RuntimeError(f"{path.name} has an invalid {digest_key}.")
    value[digest_key] = supplied
    return value


def _previous_incumbent(
    case: Mapping[str, object],
) -> tuple[dict[str, object] | None, dict[str, object]]:
    previous = case.get("previous_project")
    if not isinstance(previous, Mapping):
        return None, {"requested": False, "status": "not_applicable"}
    settings = dict(case["solver_settings"])
    session, preparation_ms = _prepared_session(previous, settings)
    started = perf_counter()
    calculated = session.calculate_layout(
        request_id=f"p64-l09w-a-{case['baseline_case_id']}-previous",
        request_revision=0,
    )
    elapsed_ms = (perf_counter() - started) * 1000.0
    plan = calculated["partition"]
    status = str(calculated["solver_result"]["status"])
    certified = False
    if status == "solution_found" and isinstance(plan, Mapping):
        certified = recertify_minimal_layout_plan(plan).certified
    return (
        deepcopy(dict(plan)) if certified and isinstance(plan, Mapping) else None,
        {
            "requested": True,
            "status": "certified_solution" if certified else status,
            "preparation_ms": round(preparation_ms, 3),
            "calculation_ms": round(elapsed_ms, 3),
        },
    )


def audit_case(
    case: Mapping[str, object],
    source_result: Mapping[str, object],
) -> dict[str, object]:
    settings = dict(case["solver_settings"])
    initial_incumbent, previous = _previous_incumbent(case)
    with _WorkingSetSampler() as sampler:
        session, preparation_ms = _prepared_session(case["project"], settings)
        calculation_started = perf_counter()
        calculated = session.calculate_layout(
            request_id=f"p64-l09w-a-{case['baseline_case_id']}",
            request_revision=1 if initial_incumbent is not None else 0,
            initial_incumbent=initial_incumbent,
        )
        calculation_ms = (perf_counter() - calculation_started) * 1000.0
        plan = calculated["partition"]
        solver_status = str(calculated["solver_result"]["status"])
        certified = False
        if solver_status == "solution_found" and isinstance(plan, Mapping):
            certified = recertify_minimal_layout_plan(plan).certified
        if not certified or not isinstance(plan, Mapping):
            raise RuntimeError(
                f"{case['baseline_case_id']} no longer reconstructs its "
                "certified baseline calculation."
            )
        source_placement_digest = source_result["runs"][0][
            "placement_digest"
        ]
        placement_digest = _placement_digest(plan)
        if placement_digest != source_placement_digest:
            raise RuntimeError(
                f"{case['baseline_case_id']} changed placement before "
                "downstream attribution."
            )

        finalization_started = perf_counter()
        finalized = session.finalize_volume(
            finishing_effort_profile="normal"
        )
        finalization_ms = (perf_counter() - finalization_started) * 1000.0
        finalization_result = deepcopy(dict(finalized["solver_result"]))
        finalization_status = str(finalization_result["status"])
        stop_diagnostics = (
            deepcopy(dict(finalization_result["stop_diagnostics"]))
            if isinstance(
                finalization_result.get("stop_diagnostics"), Mapping
            )
            else {}
        )
        cad_ir = {
            "attempted": False,
            "status": "not_applicable",
            "elapsed_ms": 0.0,
            "digest": None,
        }
        if finalization_status == "solution_found":
            selection = session.select_materializable_artifact(
                ARTIFACT_KIND_FINALIZED
            )
            cad_started = perf_counter()
            cad = build_partition_cad(
                case["project"],
                partition=selection["partition"],
                artifact_identity=selection,
                effort_profile=str(settings["effort"]),
            )
            cad_ir = {
                "attempted": True,
                "status": cad.get("status"),
                "elapsed_ms": round(
                    (perf_counter() - cad_started) * 1000.0, 3
                ),
                "digest": cad.get("cad_digest") or cad.get("build_digest"),
            }
    return {
        "baseline_case_id": case["baseline_case_id"],
        "source": case["source"],
        "family": case["family"],
        "expected": case["expected"],
        "placement_digest": placement_digest,
        "source_placement_digest": source_placement_digest,
        "calculation": {
            "status": "certified_solution",
            "preparation_ms": round(preparation_ms, 3),
            "elapsed_ms": round(calculation_ms, 3),
            "previous": previous,
        },
        "finalization": {
            "status": finalization_status,
            "effort_profile": "normal",
            "elapsed_ms": round(finalization_ms, 3),
            "stop_reason": (
                stop_diagnostics.get("stop_reason")
                or finalization_result.get("telemetry", {}).get(
                    "stop_reason", "not_reported"
                )
            ),
            "outcome_kind": stop_diagnostics.get(
                "outcome_kind", "not_available"
            ),
            "deadline_reached": stop_diagnostics.get(
                "deadline_reached", False
            ),
            "proof_of_impossibility": stop_diagnostics.get(
                "proof_of_impossibility", False
            ),
            "candidate_count": stop_diagnostics.get(
                "candidate_count", 0
            ),
            "rejection_codes": stop_diagnostics.get(
                "rejection_codes", []
            ),
        },
        "cad_ir": cad_ir,
        "resources": {
            "peak_working_set_bytes": sampler.peak_bytes,
            "measurement_method": sampler.method,
        },
    }


def summarize(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    finalization_statuses = Counter(
        str(value["finalization"]["status"]) for value in rows
    )
    stop_reasons = Counter(
        str(value["finalization"]["stop_reason"]) for value in rows
    )
    return {
        "case_count": len(rows),
        "calculation_recertified_count": sum(
            value["calculation"]["status"] == "certified_solution"
            for value in rows
        ),
        "placement_match_count": sum(
            value["placement_digest"] == value["source_placement_digest"]
            for value in rows
        ),
        "finalization_status_counts": dict(
            sorted(finalization_statuses.items())
        ),
        "finalization_stop_reason_counts": dict(
            sorted(stop_reasons.items())
        ),
        "finalization_deadline_reached_count": sum(
            value["finalization"]["deadline_reached"] is True
            for value in rows
        ),
        "finalization_proof_of_impossibility_count": sum(
            value["finalization"]["proof_of_impossibility"] is True
            for value in rows
        ),
        "cad_ir_attempt_count": sum(
            value["cad_ir"]["attempted"] is True for value in rows
        ),
        "cad_ir_success_count": sum(
            value["cad_ir"]["status"] == "ready_for_fusion"
            for value in rows
        ),
        "materialization_measurement_count": 0,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-report", type=Path, required=True)
    parser.add_argument("--baseline-checkpoint", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--worker-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    baseline_report = _verified_document(
        args.baseline_report, "report_digest"
    )
    checkpoint = _verified_document(
        args.baseline_checkpoint, "checkpoint_digest"
    )
    expected_binding = canonical_digest(baseline_report["bindings"])
    if checkpoint["binding_digest"] != expected_binding:
        raise RuntimeError("Baseline report and checkpoint bindings differ.")
    if (
        baseline_report["candidate"]["code_bundle_digest"]
        != _code_bundle_digest()
    ):
        raise RuntimeError("Measured solver and runner code bundle changed.")
    if (
        baseline_report["candidate"]["runtime_artifact_digest"]
        != SCIP_PRODUCT_ARTIFACT_DIGEST
    ):
        raise RuntimeError("Baseline runtime artifact is not the product one.")

    configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root / "scip",
    )
    built = build_fixture_inventory()
    case_by_id = {
        str(value["baseline_case_id"]): value
        for value in built["product_cases"]
    }
    source_results = {
        str(key): value
        for key, value in checkpoint["product_results"].items()
        if value["status"] == "certified_solution"
    }
    rows = []
    for index, case_id in enumerate(sorted(source_results), start=1):
        row = audit_case(case_by_id[case_id], source_results[case_id])
        rows.append(row)
        print(
            f"P64_L09W_A_DOWNSTREAM {index}/{len(source_results)} "
            f"case={case_id} finalization={row['finalization']['status']}",
            flush=True,
        )

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
        "baseline_report_digest": baseline_report["report_digest"],
        "baseline_checkpoint_digest": checkpoint["checkpoint_digest"],
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "audit_script_sha256": sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "rows": rows,
        "summary": summarize(rows),
        "invariants": {
            "calculation_budget_changed": False,
            "finalization_profile": "normal",
            "grid_changed": False,
            "epsilon_changed": False,
            "physical_value_changed": False,
            "fusion_materialization_invocation_count": 0,
        },
    }
    report["report_digest"] = canonical_digest(report)
    _write_json_atomic(args.output, report)
    print(
        "P64_L09W_A_DOWNSTREAM_OK "
        f"digest={report['report_digest']} cases={len(rows)}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
