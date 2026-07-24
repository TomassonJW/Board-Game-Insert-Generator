#!/usr/bin/env python3
"""Validate the packaged SCIP lane through the public BGIG 3D solver."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.project_v1 import blank_project_v1
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARCHIVE_SHA256,
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    configure_scip_product_runtime,
)


SCHEMA_VERSION = "bgig.scip_product_integration_receipt.v1"


def _stacking_project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "P64-L08K SCIP forced stacking control"
    project["box"] = {
        "inner_dimensions_mm": {"x": 70.0, "y": 70.0, "z": 55.0},
        "usable_height_mm": 55.0,
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {
            "id": f"stack-{index}",
            "name": f"Stack {index}",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
        for index in range(3)
    ]
    project["contents"] = [
        {
            "id": f"content-{index}",
            "name": f"Content {index}",
            "shape_kind": "custom",
            "dimensions_mm": {"x": 58.0, "y": 58.0, "z": 14.0},
            "quantity": 1,
            "container_group_id": f"stack-{index}",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        for index in range(3)
    ]
    return project


def _run_summary(plan: dict[str, object]) -> dict[str, object]:
    solver = plan["solver"]
    result = solver["result"]
    minimal = plan["minimal_layout"]
    provenance = minimal["search_provenance"]
    external = provenance["external_lane"]
    placements = sorted(
        (
            {
                "participant_id": value["id"],
                "origin_mm": deepcopy(value["origin_mm"]),
                "world_size_mm": deepcopy(value["world_size_mm"]),
                "variant": deepcopy(value.get("container_internal_variant_v1", {})),
            }
            for value in plan["placements"]
            if value["role"] == "container"
        ),
        key=lambda value: value["participant_id"],
    )
    return {
        "result_status": result["status"],
        "plan_digest": plan["plan_digest"],
        "placement_digest": provenance["selected"]["placement_digest"],
        "candidate_source": provenance["selected"]["candidate_source"],
        "selected_lane_id": provenance["selected"]["lane_id"],
        "lane_prefix_ids": deepcopy(provenance["lane_prefix_ids"]),
        "internal_lane_count": len(provenance["lanes"]),
        "external_status": external["status"],
        "external_engine_status": external["engine_status"],
        "external_invocation_count": external["invocation_count"],
        "external_recertified": external["recertification"]["certified"],
        "external_rejection_codes": deepcopy(external["recertification"]["rejection_codes"]),
        "runtime_artifact_digest": external["candidate"]["runtime_artifact_digest"],
        "placements": placements,
    }


def validate(args: argparse.Namespace) -> dict[str, object]:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("This validation must run with Python 3.14.")
    configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root,
    )
    first = _run_summary(solve_minimal_layout(_stacking_project(), effort_profile="quick"))
    second = _run_summary(solve_minimal_layout(_stacking_project(), effort_profile="quick"))
    if first != second:
        raise RuntimeError("SCIP product results are not deterministic across two runs.")
    if first["result_status"] != "solution_found":
        raise RuntimeError("SCIP product lane did not return a solution.")
    if first["candidate_source"] != "external_scip_real_3d":
        raise RuntimeError("The public solver did not select the SCIP product lane.")
    if first["internal_lane_count"] != 0 or first["lane_prefix_ids"]:
        raise RuntimeError("An internal portfolio lane ran after the SCIP solution.")
    if first["external_invocation_count"] != 1:
        raise RuntimeError("The public calculation did not invoke SCIP exactly once.")
    if not first["external_recertified"] or first["external_rejection_codes"]:
        raise RuntimeError("BGIG did not recertify the SCIP placement cleanly.")
    if first["runtime_artifact_digest"] != SCIP_PRODUCT_ARTIFACT_DIGEST:
        raise RuntimeError("The selected runtime artifact does not match L08J.")
    z_values = sorted({value["origin_mm"]["z"] for value in first["placements"]})
    supported = [value for value in first["placements"] if value["origin_mm"]["z"] > 0.0]
    if len(z_values) < 3 or len(supported) < 2:
        raise RuntimeError("The control did not prove real stacking on the Z axis.")

    receipt: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L08K",
        "control_kind": "forced_three_level_product_stacking",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "runtime_archive_sha256": SCIP_PRODUCT_ARCHIVE_SHA256,
        "public_entrypoint": "solve_minimal_layout",
        "effort_profile": "quick",
        "repeat_count": 2,
        "runs_identical": True,
        "scip_invocations_per_calculation": 1,
        "internal_lane_count_after_scip_solution": 0,
        "real_3d": {
            "distinct_z_level_count": len(z_values),
            "z_levels_mm": z_values,
            "supported_placement_count": len(supported),
            "stacking_required_by_footprint": True,
        },
        "result": first,
        "invariants": {
            "bgig_certificate_required": True,
            "fusion_validated": False,
            "holdout_read": False,
            "network_invocation_count": 0,
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
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = validate(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "SCIP_PRODUCT_INTEGRATION_OK "
        f"digest={receipt['receipt_digest']} "
        f"z_levels={receipt['real_3d']['distinct_z_level_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
