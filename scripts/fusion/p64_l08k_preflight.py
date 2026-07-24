#!/usr/bin/env python3
"""Validate L08K evidence and prepare the reviewed 18x20 Fusion fixture."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARCHIVE_SHA256,
    SCIP_PRODUCT_ARTIFACT_DIGEST,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
CASE_ID = "real-18-containers-20-contents-normal"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def _verify_digest(payload: dict[str, object], field: str) -> None:
    supplied = payload.pop(field, None)
    if not isinstance(supplied, str) or supplied != canonical_digest(payload):
        raise RuntimeError(f"Invalid {field} in L08K evidence.")
    payload[field] = supplied


def prepare_fixture() -> tuple[dict[str, object], dict[str, object]]:
    integration = _load(FIXTURES / "p64_l08k_scip_product_integration.v1.json")
    limit = _load(FIXTURES / "p64_l08k_scip_product_limit_regression.v1.json")
    source = _load(FIXTURES / "p64_l06a_reviewed_real_case.v1.json")
    _verify_digest(integration, "receipt_digest")
    _verify_digest(limit, "receipt_digest")
    if integration["runtime_artifact_digest"] != SCIP_PRODUCT_ARTIFACT_DIGEST:
        raise RuntimeError("L08K integration receipt uses the wrong runtime.")
    if integration["runtime_archive_sha256"] != SCIP_PRODUCT_ARCHIVE_SHA256:
        raise RuntimeError("L08K integration receipt uses the wrong archive.")
    if integration["result"]["candidate_source"] != "external_scip_real_3d":
        raise RuntimeError("L08K did not select SCIP on the forced stacking control.")
    if not integration["result"]["external_recertified"]:
        raise RuntimeError("L08K forced stacking control lacks BGIG recertification.")
    if integration["real_3d"]["distinct_z_level_count"] < 3:
        raise RuntimeError("L08K forced stacking control lacks real Z stacking.")
    if limit["case_id"] != CASE_ID or limit["container_count"] != 18:
        raise RuntimeError("L08K public limit receipt is not the reviewed 18x20 case.")
    if limit["content_count"] != 20 or limit["holdout_read"]:
        raise RuntimeError("L08K public limit receipt violates its gate contract.")
    if not limit["interpretation"]["human_limit_case_gate_still_required"]:
        raise RuntimeError("L08K limit receipt incorrectly closes the human gate.")
    for run in limit["runs"]:
        if run["external_invocation_count"] != 1 or run["internal_lane_count"] != 0:
            raise RuntimeError("L08K limit receipt hides a second solver budget.")

    records = [value for value in source["cases"] if value["case_id"] == CASE_ID]
    if len(records) != 1:
        raise RuntimeError("Reviewed 18x20 source case is missing or duplicated.")
    project = deepcopy(records[0]["project"])
    normalize_project_draft(project)
    summary = {
        "schema_version": "bgig.p64_l08k_fusion_preflight.v1",
        "case_id": CASE_ID,
        "project_digest": canonical_digest(project),
        "container_count": len(project["container_groups"]),
        "content_count": len(project["contents"]),
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "runtime_archive_sha256": SCIP_PRODUCT_ARCHIVE_SHA256,
        "forced_stacking_receipt_digest": integration["receipt_digest"],
        "limit_regression_receipt_digest": limit["receipt_digest"],
        "expected_effort": "deep",
        "expected_external_invocation_count": 1,
        "expected_internal_lane_count_after_scip": 0,
        "accepted_result_statuses": [
            "solution_found",
            "no_solution_within_budget",
        ],
        "fusion_validated": False,
        "print_validated": False,
    }
    summary["preflight_digest"] = canonical_digest(summary)
    return project, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-fixture", type=Path)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    project, summary = prepare_fixture()
    if args.write_fixture is not None:
        args.write_fixture.parent.mkdir(parents=True, exist_ok=True)
        args.write_fixture.write_text(
            json.dumps(project, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        "P64_L08K_PREFLIGHT_OK "
        f"digest={summary['preflight_digest']} "
        f"containers={summary['container_count']} "
        f"contents={summary['content_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
