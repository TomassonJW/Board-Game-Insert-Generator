#!/usr/bin/env python3
"""Exercise the public reviewed 18-container BGIG case through product SCIP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    configure_scip_product_runtime,
)


SCHEMA_VERSION = "bgig.scip_product_limit_regression_receipt.v1"
CASE_ID = "real-18-containers-20-contents-normal"


def _summary(plan: dict[str, object], effort: str) -> dict[str, object]:
    provenance = plan["minimal_layout"]["search_provenance"]
    external = provenance["external_lane"]
    selected = provenance.get("selected")
    return {
        "effort_profile": effort,
        "result_status": plan["solver"]["result"]["status"],
        "plan_digest": plan["plan_digest"],
        "candidate_source": selected.get("candidate_source") if selected else None,
        "external_status": external["status"],
        "external_engine_status": external["engine_status"],
        "external_invocation_count": external["invocation_count"],
        "external_recertification": external["recertification"],
        "problem_digest": external["model"]["problem_digest"],
        "model_digest": external["model"]["model_digest"],
        "wall_seconds_cap": external["limits"]["wall_seconds"],
        "internal_lane_count": len(provenance["lanes"]),
        "lane_prefix_ids": provenance["lane_prefix_ids"],
        "placement_count": len(plan["placements"]),
        "globally_optimal": plan["solver"]["globally_optimal"],
    }


def validate(args: argparse.Namespace) -> dict[str, object]:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("This validation must run with Python 3.14.")
    corpus = json.loads(args.case_fixture.read_text(encoding="utf-8"))
    records = [value for value in corpus["cases"] if value["case_id"] == CASE_ID]
    if len(records) != 1:
        raise RuntimeError("The reviewed public case is missing or duplicated.")
    record = records[0]
    project = record["project"]
    configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root,
    )
    runs = [
        _summary(solve_minimal_layout(project, effort_profile=effort), effort)
        for effort in ("normal", "deep")
    ]
    for run in runs:
        if run["external_invocation_count"] != 1:
            raise RuntimeError("The limit case did not invoke SCIP exactly once.")
        if run["internal_lane_count"] != 0 or run["lane_prefix_ids"]:
            raise RuntimeError("The limit case silently doubled its search budget.")
        if run["result_status"] not in {
            "solution_found",
            "no_solution_within_budget",
        }:
            raise RuntimeError("The limit case returned an invalid product status.")
        if (
            run["result_status"] == "solution_found"
            and not run["external_recertification"]["certified"]
        ):
            raise RuntimeError("A limit-case solution escaped BGIG recertification.")

    receipt: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L08K",
        "case_id": CASE_ID,
        "case_fixture": args.case_fixture.name,
        "public_case": True,
        "holdout_read": False,
        "container_count": len(project["container_groups"]),
        "content_count": len(project["contents"]),
        "prior_bgig_baseline": {
            "status": record["baseline"]["status"],
            "stop_reason": record["baseline"]["stop_reason"],
        },
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "runs": runs,
        "interpretation": {
            "solution_gain_demonstrated": any(
                value["result_status"] == "solution_found" for value in runs
            ),
            "bounded_unknown_is_not_infeasible": True,
            "human_limit_case_gate_still_required": True,
            "no_hidden_internal_retry": True,
        },
        "invariants": {
            "fusion_validated": False,
            "print_validated": False,
            "finalization_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
            "network_invocation_count": 0,
        },
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--worker-root", required=True, type=Path)
    parser.add_argument("--scratch-root", required=True, type=Path)
    parser.add_argument("--case-fixture", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = validate(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "SCIP_PRODUCT_LIMIT_REGRESSION_OK "
        f"digest={receipt['receipt_digest']} "
        f"normal={receipt['runs'][0]['external_status']} "
        f"deep={receipt['runs'][1]['external_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
