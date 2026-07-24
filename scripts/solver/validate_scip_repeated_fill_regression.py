#!/usr/bin/env python3
"""Valide le remplissage répété SCIP sur un cas public BGIG 28x30."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    configure_scip_product_runtime,
)


SCHEMA_VERSION = "bgig.scip_repeated_fill_regression_receipt.v1"
SOURCE_CASE_ID = "real-18-containers-20-contents-normal"
GENERATED_CASE_ID = "public-28-containers-30-contents-repeated-fill"


def _generated_project(source: dict[str, object]) -> dict[str, object]:
    project = deepcopy(source)
    source_group = next(
        value for value in project["container_groups"] if value["id"] == "container-001"
    )
    source_content = next(
        value for value in project["contents"] if value["container_group_id"] == "container-001"
    )
    for ordinal in range(1, 11):
        group = deepcopy(source_group)
        group["id"] = f"repeated-container-{ordinal:03d}"
        group["name"] = f"Conteneur public répété {ordinal:03d}"
        content = deepcopy(source_content)
        content["id"] = f"repeated-content-{ordinal:03d}"
        content["name"] = f"Contenu public répété {ordinal:03d}"
        content["container_group_id"] = group["id"]
        project["container_groups"].append(group)
        project["contents"].append(content)
    project["project_name"] = "Régression publique SCIP 28x30 à remplissage répété"
    normalize_project_draft(project)
    return project


def validate(args: argparse.Namespace) -> dict[str, object]:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("This validation must run with Python 3.14.")
    corpus = json.loads(args.case_fixture.read_text(encoding="utf-8"))
    records = [value for value in corpus["cases"] if value["case_id"] == SOURCE_CASE_ID]
    if len(records) != 1:
        raise RuntimeError("The reviewed public source case is missing or duplicated.")
    project = _generated_project(records[0]["project"])
    if len(project["container_groups"]) != 28 or len(project["contents"]) != 30:
        raise RuntimeError("The public repeated-fill case is not 28x30.")
    configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root,
    )
    plan = solve_minimal_layout(project, effort_profile="deep")
    provenance = plan["minimal_layout"]["search_provenance"]
    external = provenance["external_lane"]
    if plan["solver"]["result"]["status"] != "solution_found":
        raise RuntimeError("The public 28x30 repeated-fill case was not solved.")
    if len(plan["placements"]) != 28:
        raise RuntimeError("The public 28x30 placement set is incomplete.")
    if external["status"] != "solution_found":
        raise RuntimeError("SCIP did not produce the selected public 28x30 solution.")
    if external["engine_status"] != "hybrid_anchor_and_fill":
        raise RuntimeError("The repeated-fill strategy was not exercised.")
    if external["recertification"]["certified"] is not True:
        raise RuntimeError("The public 28x30 solution was not recertified by BGIG.")
    if external["invocation_count"] != 1:
        raise RuntimeError("The public 28x30 case did not invoke SCIP exactly once.")
    if provenance["lanes"] or provenance["lane_prefix_ids"]:
        raise RuntimeError("The public 28x30 result used a hidden internal fallback lane.")
    if plan["solver"]["globally_optimal"]:
        raise RuntimeError("A first feasible solution was incorrectly called globally optimal.")
    max_top = max(
        float(value["origin_mm"]["z"]) + float(value["world_size_mm"]["z"])
        for value in plan["placements"]
    )
    receipt: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L08L",
        "case_id": GENERATED_CASE_ID,
        "source_case_id": SOURCE_CASE_ID,
        "case_fixture": args.case_fixture.name,
        "public_case": True,
        "generated_from_public_data_only": True,
        "private_project_data_in_repo": False,
        "holdout_read": False,
        "container_count": 28,
        "content_count": 30,
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "result": {
            "status": "solution_found",
            "placement_count": 28,
            "candidate_source": provenance["selected"]["candidate_source"],
            "external_status": external["status"],
            "external_engine_status": external["engine_status"],
            "external_invocation_count": external["invocation_count"],
            "external_recertified": external["recertification"]["certified"],
            "internal_lane_count": len(provenance["lanes"]),
            "maximum_top_mm": round(max_top, 6),
            "globally_optimal": plan["solver"]["globally_optimal"],
            "solution_digest": external["solution_digest"],
        },
        "limits": external["limits"],
        "invariants": {
            "network_invocation_count": 0,
            "finalization_invocation_count": 0,
            "fusion_materialization_invocation_count": 0,
            "fusion_validated": False,
            "print_validated": False,
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
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "SCIP_REPEATED_FILL_REGRESSION_OK "
        f"digest={receipt['receipt_digest']} "
        f"placements={receipt['result']['placement_count']} "
        f"engine={receipt['result']['external_engine_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
