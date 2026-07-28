#!/usr/bin/env python3
"""Prépare la fixture publique et le reçu correctif P64-L09U-R5-V."""

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


ADDIN_VERSION = "0.1.76"
FIXTURE_FILENAME = "p64-l09uw-01-exact-composite.bgig.json"
SUMMARY_FILENAME = "p64-l09uw-preflight-summary.json"
TARGETED_MATRIX = (
    "fresh_unsaved_startup",
    "explicit_fresh_calculation",
    "exact_selected_minimal_finalization",
    "frozen_cavity_world_pose",
    "calibrated_cavity_depth_unchanged",
    "deterministic_final_cavity_z_anchor",
    "direct_void_between_top_inset_and_cavity",
    "zero_intermediate_material_under_removable_tray",
    "partial_top_inset_preserves_uncovered_cavity_access",
    "local_disjoint_top_insets",
    "local_overlapping_top_inset_steps",
    "truthful_budget_wall_and_cleanup_timing",
    "composite_preview_uses_real_prisms",
    "final_z_anchor_distinct_from_calibrated_depth",
    "residual_multi_cell_consumption",
    "emergent_clearance_corridor_preserved",
    "late_wider_stack_support_insertion",
    "transient_boolean_module_body",
    "no_parametric_combine_tool_reference",
    "failed_generation_partial_scene_rollback",
    "case_01_plus_read_only_replay",
    "case_01_plus_without_flat_read_only_replay",
    "case_01_plus_plus_read_only_replay",
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
            "The corrective fixture does not prove bounded owner batches."
        )
    anchor_certificate = end_to_end["finalization"][
        "composite_certificate"
    ]["cavity_anchor_certificate"]
    anchored_cavities = [
        value
        for value in anchor_certificate["cavities"]
        if value["anchor_kind"] == "below_top_inset"
    ]
    if (
        anchor_certificate["certified"] is not True
        or not anchored_cavities
        or anchor_certificate["direct_top_inset_void_count"]
        != anchor_certificate["below_top_inset_count"]
        or anchor_certificate["top_void_continuity_certified"] is not True
        or any(
            value["top_interface_kind"]
            != "direct_void_to_removable_top_inset"
            or value["intermediate_material_thickness_mm"] != 0.0
            or value["top_separation_mm"] != 0.0
            for value in anchored_cavities
        )
    ):
        raise RuntimeError(
            "The corrective fixture does not prove direct cavity access below the removable tray."
        )
    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l09uw_fusion_preflight.v2",
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
                "tests.test_plateau_candidate_pool",
                "tests.test_partition_result_view",
                "tests.test_reserved_floor_stack_solver",
                "tests.test_xy_composite_closure",
                "tests.test_fusion_materialization_batches",
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
            "finalization_uses_exact_selected_minimal_plan": True,
            "alternate_minimal_candidate_attempted": False,
            "automatic_top_reservation_xy": True,
            "floor_first_rank_policy": True,
            "late_support_insertion_supported": True,
            "composite_cavities_frozen": True,
            "calibrated_cavity_depths_unchanged": True,
            "final_cavity_z_anchor_deterministic": True,
            "top_inset_cavity_interface": (
                "direct_void_to_removable_top_inset"
            ),
            "intermediate_material_thickness_mm": 0.0,
            "top_void_continuity_certified": True,
            "partial_top_inset_preserves_uncovered_cavity_access": True,
            "top_inset_depth_is_local_by_xy_region": True,
            "budget_wall_and_cleanup_times_separated": True,
            "composite_preview_uses_cad_prisms": True,
            "composite_unions_before_cuts": True,
            "transient_boolean_body_per_module": True,
            "parametric_combine_feature_count": 0,
            "fusion_ui_yield_between_modules": True,
            "failed_generation_partial_scene_rollback": True,
            "printable_residual_volume_mm3": 0.0,
        },
        "human_observations_required": {
            "fusion_stays_responsive_or_recovers_without_os_hang": True,
            "materialization_elapsed_seconds_recorded": True,
            "scene_synchronized": True,
            "preview_matches_fusion": True,
            "cavity_dimensions_match_project": True,
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
        "P64_L09UW_PREFLIGHT_OK "
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
