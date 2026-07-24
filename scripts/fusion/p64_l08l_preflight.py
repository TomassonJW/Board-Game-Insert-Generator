#!/usr/bin/env python3
"""Valide L08L et prépare la régression publique 28x30 pour Fusion."""

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
SOURCE_CASE_ID = "real-18-containers-20-contents-normal"
L08L_RECEIPT_ARTIFACT_DIGEST = "05d4566e93efef2b6606b0d1807abaaf29bc460c37accee31da20ae2a6462065"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def _verify_digest(payload: dict[str, object], field: str) -> None:
    supplied = payload.pop(field, None)
    if not isinstance(supplied, str) or supplied != canonical_digest(payload):
        raise RuntimeError(f"Invalid {field} in L08L evidence.")
    payload[field] = supplied


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
    project["project_name"] = "P64-L08L public 28x30 repeated fill"
    normalize_project_draft(project)
    return project


def prepare_fixture() -> tuple[dict[str, object], dict[str, object]]:
    receipt = _load(FIXTURES / "p64_l08l_scip_repeated_fill_regression.v1.json")
    source = _load(FIXTURES / "p64_l06a_reviewed_real_case.v1.json")
    _verify_digest(receipt, "receipt_digest")
    if receipt["runtime_artifact_digest"] != L08L_RECEIPT_ARTIFACT_DIGEST:
        raise RuntimeError("L08L receipt uses the wrong historical SCIP artifact.")
    result = receipt["result"]
    if receipt["container_count"] != 28 or receipt["content_count"] != 30:
        raise RuntimeError("L08L receipt is not the public 28x30 regression.")
    if result["status"] != "solution_found" or result["placement_count"] != 28:
        raise RuntimeError("L08L public 28x30 regression is not fully solved.")
    if result["external_engine_status"] != "hybrid_anchor_and_fill":
        raise RuntimeError("L08L repeated-fill strategy was not exercised.")
    if result["external_recertified"] is not True:
        raise RuntimeError("L08L public 28x30 result lacks BGIG recertification.")
    if result["external_invocation_count"] != 1 or result["internal_lane_count"] != 0:
        raise RuntimeError("L08L public 28x30 result hides extra search lanes.")
    records = [value for value in source["cases"] if value["case_id"] == SOURCE_CASE_ID]
    if len(records) != 1:
        raise RuntimeError("Reviewed public source case is missing or duplicated.")
    project = _generated_project(records[0]["project"])
    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l08l_fusion_preflight.v1",
        "case_id": receipt["case_id"],
        "project_digest": canonical_digest(project),
        "container_count": 28,
        "content_count": 30,
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "source_receipt_artifact_digest": L08L_RECEIPT_ARTIFACT_DIGEST,
        "runtime_archive_sha256": SCIP_PRODUCT_ARCHIVE_SHA256,
        "repeated_fill_receipt_digest": receipt["receipt_digest"],
        "expected_effort": "deep",
        "expected_external_status": "solution_found",
        "expected_external_engine_status": "hybrid_anchor_and_fill",
        "expected_external_invocation_count": 1,
        "expected_internal_lane_count": 0,
        "expected_recertified": True,
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
        "P64_L08L_PREFLIGHT_OK "
        f"digest={summary['preflight_digest']} "
        f"containers={summary['container_count']} "
        f"contents={summary['content_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
