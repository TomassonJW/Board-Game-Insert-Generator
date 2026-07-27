#!/usr/bin/env python3
"""Prépare la fixture publique et le reçu de gate P64-L09T-V."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from scripts.fusion.p64_l09sv_preflight import (
    recent_limit_contract,
    recent_tray_project,
    run_end_to_end,
)


ADDIN_VERSION = "0.1.70"
FIXTURE_FILENAME = "p64-l09tv-01-explicit-composite.bgig.json"
SUMMARY_FILENAME = "p64-l09tv-preflight-summary.json"
TARGETED_MATRIX = (
    "public_smoke",
    "anonymized_case_01_plus",
    "case_02_base",
    "case_02_content_only",
    "case_02_clearance_only",
    "case_02_combined",
    "automatic_off_center_top_reservation",
    "top_reservation_near_cavity",
    "all_floor_plan",
    "required_stack_plan",
    "rectangular_closure",
    "annex_closure",
    "rejections_stale_and_early_stops",
)


def gate_project() -> dict[str, object]:
    project = deepcopy(recent_tray_project())
    project["project_name"] = "P64-L09T-V fermeture composite explicite"
    return normalize_project_draft(project).project


def _preflight_digest(summary: dict[str, object]) -> str:
    payload = deepcopy(summary)
    payload.pop("preflight_digest", None)
    payload["end_to_end"]["minimal"].pop("observed_ms", None)
    payload["end_to_end"]["finalization"].pop("observed_ms", None)
    return canonical_digest(payload)


def build_preflight() -> tuple[dict[str, object], dict[str, object]]:
    project = gate_project()
    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l09tv_fusion_preflight.v1",
        "addin_version": ADDIN_VERSION,
        "fixture": {
            "filename": FIXTURE_FILENAME,
            "project_digest": canonical_digest(project),
        },
        "recent_limit_contract": recent_limit_contract(project),
        "end_to_end": run_end_to_end(project),
        "targeted_matrix": {
            "required_case_ids": list(TARGETED_MATRIX),
            "public_regression_test": "tests.test_p64_l09t_g_release_gate",
            "exact_personal_replay": {
                "required_before_install": True,
                "read_only": True,
                "source_mutation_forbidden": True,
                "repository_payload_forbidden": True,
            },
        },
        "runtime_contract": {
            "automatic_plan_reuse_disabled": True,
            "explicit_calculation_required": True,
            "legacy_witness_recertified_and_migrated": True,
            "early_stop_diagnostics_explicit": True,
            "flat_item_xy_automatic": True,
            "floor_first_rank_policy": True,
            "composite_cavities_frozen": True,
            "composite_unions_before_cuts": True,
            "printable_residual_volume_mm3": 0.0,
        },
        "expected_ui": {
            "buttons": {
                "Calculer": "blue",
                "Finaliser": "orange_or_violet",
                "Materialiser": "green",
            },
            "calculation_budgets_seconds": [3, 10, 20, 60, 180],
            "finishing_budgets_seconds": [3, 10, 20, 60, 180],
            "early_stop_fields": [
                "phase",
                "stop_reason",
                "budget_cap_ms",
                "elapsed_ms",
                "proof_of_impossibility",
            ],
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
    print(
        "P64_L09TV_PREFLIGHT_OK "
        f"version={ADDIN_VERSION} "
        f"digest={summary['preflight_digest']} "
        f"matrix={len(TARGETED_MATRIX)} "
        f"joins={summary['end_to_end']['fusion_plan']['joined_annex_count']} "
        f"cuts={summary['end_to_end']['fusion_plan']['top_inset_cut_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
