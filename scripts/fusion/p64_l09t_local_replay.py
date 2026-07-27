#!/usr/bin/env python3
"""Rejoue en lecture seule les cas locaux P64-L09T s'ils sont présents."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    StagedCalculationSession,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


PROJECT_DIRECTORY = Path.home() / "Documents" / "BGIG" / "projects"
BASE_FILENAMES = {
    "case01": "CasLimite01.bgig.json",
    "case01_plus": "CasLimite01+.bgig.json",
    "case02": "CasLimite02.bgig.json",
    "case02_plus": "CasLimite02+.bgig.json",
}


def _file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_raw(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _case_02_variants(
    base: dict[str, object],
    plus: dict[str, object],
) -> dict[str, dict[str, object]]:
    content_only = deepcopy(base)
    content_only["contents"] = deepcopy(plus["contents"])
    clearance_only = deepcopy(base)
    clearance_only["layout"] = deepcopy(plus["layout"])
    return {
        "case02": base,
        "case02_content_only": content_only,
        "case02_clearance_only": clearance_only,
        "case02_combined": plus,
    }


def _run_case(
    case_id: str,
    raw_project: dict[str, object],
) -> dict[str, object]:
    project = normalize_project_draft(raw_project).project
    settings = {"method": "auto", "effort": "normal"}
    engine = IncrementalLocalAnalysisEngine(project, effort_profile="normal")
    session = StagedCalculationSession(project, solver_settings=settings)
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    started = perf_counter()
    calculated = session.calculate_layout(
        request_id=f"p64-l09t-local-{case_id}",
        request_revision=0,
        initial_incumbent=None,
    )
    calculation_ms = round((perf_counter() - started) * 1000.0, 3)
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError(
            f"{case_id}: calculation={calculated['solver_result']['status']}"
        )
    started = perf_counter()
    finalized = session.finalize_volume(finishing_effort_profile="normal")
    finishing_ms = round((perf_counter() - started) * 1000.0, 3)
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError(
            f"{case_id}: finalization="
            f"{finalized['solver_result'].get('stop_diagnostics')}"
        )
    selected = session.select_materializable_artifact(
        ARTIFACT_KIND_FINALIZED
    )
    plan = selected["partition"]
    certificate = plan["finalization"][
        "composite_materialization_certificate"
    ]
    cad = build_partition_cad(
        project,
        partition=plan,
        artifact_identity=selected,
        effort_profile="normal",
    )
    if cad["status"] != "ready_for_fusion":
        raise RuntimeError(f"{case_id}: CAD IR={cad['status']}")
    fusion = generation_plan_from_cad_ir(
        cad["cad_ir"],
        FUSION_GENERATION_MODE_COMPACT_ONLY,
    )
    if (
        certificate.get("certified") is not True
        or certificate.get("printable_residual_volume_mm3") != 0.0
        or certificate.get("cavity_world_poses_match_frozen_contract")
        is not True
    ):
        raise RuntimeError(f"{case_id}: final certificate is not exact")
    return {
        "case_id": case_id,
        "calculation_status": "solution_found",
        "finalization_status": "solution_found",
        "cad_status": cad["status"],
        "witness_status": "disabled",
        "cavities_frozen": True,
        "printable_residual_volume_mm3": 0.0,
        "component_count": fusion.module_component_count,
        "join_count": len(fusion.additive_prism_joins),
        "join_feature_batch_count": fusion.additive_prism_join_batch_count,
        "cut_count": len(fusion.cavity_cuts),
        "cut_feature_batch_count": fusion.cavity_cut_batch_count,
        "calculation_observed_ms": calculation_ms,
        "finishing_observed_ms": finishing_ms,
    }


def run_local_replay() -> dict[str, object]:
    paths = {
        case_id: PROJECT_DIRECTORY / filename
        for case_id, filename in BASE_FILENAMES.items()
    }
    missing = [
        case_id for case_id, path in paths.items() if not path.is_file()
    ]
    if missing:
        return {
            "schema_version": "bgig.p64_l09t_local_replay.v1",
            "status": "skipped_local_projects_missing",
            "missing_case_ids": missing,
            "read_only": True,
        }
    before = {case_id: _file_digest(path) for case_id, path in paths.items()}
    raw = {case_id: _load_raw(path) for case_id, path in paths.items()}
    cases = {
        "case01": raw["case01"],
        "case01_plus": raw["case01_plus"],
        **_case_02_variants(raw["case02"], raw["case02_plus"]),
    }
    results = [
        _run_case(case_id, project)
        for case_id, project in cases.items()
    ]
    after = {case_id: _file_digest(path) for case_id, path in paths.items()}
    if before != after:
        raise RuntimeError("A local source project changed during replay.")
    return {
        "schema_version": "bgig.p64_l09t_local_replay.v1",
        "status": "passed",
        "read_only": True,
        "source_projects_unchanged": True,
        "case_count": len(results),
        "results": results,
        "repository_payload_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    receipt = run_local_replay()
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        "P64_L09T_LOCAL_REPLAY "
        f"status={receipt['status']} "
        f"cases={receipt.get('case_count', 0)} "
        f"read_only={str(receipt['read_only']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
