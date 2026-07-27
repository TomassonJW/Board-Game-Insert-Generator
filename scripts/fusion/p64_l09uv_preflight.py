#!/usr/bin/env python3
"""Prépare la fixture publique et le reçu correctif P64-L09U-V."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)
from scripts.fusion.p64_l09sv_preflight import (
    recent_limit_contract,
    run_end_to_end,
)
from scripts.fusion.p64_l09tv_preflight import gate_project


ADDIN_VERSION = "0.1.71"
FIXTURE_FILENAME = "p64-l09uv-01-fresh-batched-composite.bgig.json"
SUMMARY_FILENAME = "p64-l09uv-preflight-summary.json"
TARGETED_MATRIX = (
    "fresh_unsaved_startup",
    "named_document_open_only_on_explicit_action",
    "cross_session_witness_reuse_disabled",
    "explicit_fresh_calculation",
    "dense_floor_stack_with_automatic_top_reservation",
    "batched_additive_prisms",
    "batched_rectangular_cuts",
    "logical_cad_operations_preserved",
    "case_01_plus_read_only_replay",
    "case_02_plus_read_only_replay",
    "fusion_responsiveness_and_elapsed_time",
)


def _preflight_digest(summary: dict[str, object]) -> str:
    payload = deepcopy(summary)
    payload.pop("preflight_digest", None)
    payload["end_to_end"]["minimal"].pop("observed_ms", None)
    payload["end_to_end"]["finalization"].pop("observed_ms", None)
    return canonical_digest(payload)


def build_preflight() -> tuple[dict[str, object], dict[str, object]]:
    project = gate_project()
    end_to_end = run_end_to_end(
        project,
        include_materialization_batches=True,
    )
    fusion_plan = end_to_end["fusion_plan"]
    if (
        fusion_plan["logical_additive_prism_join_count"]
        <= fusion_plan["additive_prism_join_batch_count"]
        or fusion_plan["logical_cavity_cut_count"]
        <= fusion_plan["cavity_cut_batch_count"]
    ):
        raise RuntimeError(
            "The corrective fixture does not prove Fusion operation batching."
        )
    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l09uv_fusion_preflight.v1",
        "addin_version": ADDIN_VERSION,
        "fixture": {
            "filename": FIXTURE_FILENAME,
            "project_digest": canonical_digest(project),
        },
        "recent_limit_contract": recent_limit_contract(project),
        "end_to_end": end_to_end,
        "targeted_matrix": {
            "required_case_ids": list(TARGETED_MATRIX),
            "public_regression_tests": [
                "tests.test_fusion_materialization_batches",
                "tests.test_fusion_palette_project",
                "tests.test_p64_l09t_g_release_gate",
            ],
            "exact_personal_replay": {
                "required_before_install": True,
                "read_only": True,
                "source_mutation_forbidden": True,
                "repository_payload_forbidden": True,
            },
        },
        "runtime_contract": {
            "session_start_policy": "fresh_unsaved_project",
            "legacy_recovery_file_read": False,
            "cross_session_witness_reuse": False,
            "cross_session_witness_persistence": False,
            "explicit_calculation_required": True,
            "automatic_top_reservation_xy": True,
            "floor_first_rank_policy": True,
            "logical_cad_operations_preserved": True,
            "fusion_features_batched_per_owner": True,
            "composite_cavities_frozen": True,
            "composite_unions_before_cuts": True,
            "printable_residual_volume_mm3": 0.0,
        },
        "human_observations_required": {
            "fusion_stays_responsive_or_recovers_without_os_hang": True,
            "materialization_elapsed_seconds_recorded": True,
            "scene_synchronized": True,
            "fresh_restart_is_blank": True,
            "fresh_calculation_is_not_instant_reuse": True,
        },
        "holdout_opened": False,
        "benchmark_executed": False,
        "fusion_validated": False,
        "print_validated": False,
        "gate_status": "prepared_not_human_observed",
    }
    summary["preflight_digest"] = _preflight_digest(summary)
    return project, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    project, summary = build_preflight()
    if args.output_directory is not None:
        args.output_directory.mkdir(parents=True, exist_ok=True)
        (args.output_directory / FIXTURE_FILENAME).write_text(
            json.dumps(project, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    fusion_plan = summary["end_to_end"]["fusion_plan"]
    print(
        "P64_L09UV_PREFLIGHT_OK "
        f"version={ADDIN_VERSION} "
        f"digest={summary['preflight_digest']} "
        f"join_batches={fusion_plan['additive_prism_join_batch_count']}/"
        f"{fusion_plan['logical_additive_prism_join_count']} "
        f"cut_batches={fusion_plan['cavity_cut_batch_count']}/"
        f"{fusion_plan['logical_cavity_cut_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
