"""Construit la configuration immuable P64-L07D annoncée avant le tournoi."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from board_game_insert_generator.external_solver_tournament import (
    EXTERNAL_TOURNAMENT_CONFIG_SCHEMA_V1,
    validate_external_tournament_config,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


def build_config() -> dict[str, object]:
    config: dict[str, object] = {
        "schema_version": EXTERNAL_TOURNAMENT_CONFIG_SCHEMA_V1,
        "candidate_ids": [
            "ortools_cp_sat",
            "highs",
            "scip",
            "laff",
        ],
        "stages": {
            "exact_controls": {
                "wall_seconds": 10.0,
                "memory_mebibytes": 1024,
                "threads": 1,
                "seed": 640707,
            },
            "regression": {
                "wall_seconds": 3.0,
                "memory_mebibytes": 1024,
                "threads": 1,
                "seed": 640707,
            },
            "discovery": {
                "wall_seconds": 3.0,
                "memory_mebibytes": 1024,
                "threads": 1,
                "seed": 640707,
            },
            "tuning_trials": [
                {
                    "trial_id": "seed-640707",
                    "wall_seconds": 3.0,
                    "memory_mebibytes": 1024,
                    "threads": 1,
                    "seed": 640707,
                },
                {
                    "trial_id": "seed-640708",
                    "wall_seconds": 3.0,
                    "memory_mebibytes": 1024,
                    "threads": 1,
                    "seed": 640708,
                },
            ],
            "holdout": {
                "wall_seconds": 3,
                "memory_mebibytes": 1024,
                "threads": 1,
                "seed": 640709,
            },
        },
        "ranking": {
            "gate_order": [
                "candidate_failure_count",
                "oracle_miss_count",
                "oracle_pass_count",
                "certified_solution_count",
                "shared_lexicographic_quality",
                "total_wall_seconds",
                "distribution_byte_count",
                "candidate_id",
            ],
            "quality_contract": "bgig.minimal_layout_lexicographic.v1",
            "invalid_output_policy": "fail_closed",
            "unsupported_policy": (
                "excluded_from_quality_but_counted_in_coverage"
            ),
            "public_method_controls_product_ranked": False,
        },
        "portfolio_policy": {
            "maximum_candidate_count": 3,
            "one_engine_invocation_per_case": True,
            "distinct_family_gain_required": True,
            "must_beat_best_single": True,
            "router_inputs": ["family"],
        },
        "invariants": {
            "minimum_external_candidate_count": 3,
            "minimum_external_family_count": 3,
            "holdout_opening_count_before_selection": 0,
            "post_open_tuning_allowed": False,
            "product_solver_routing_changed": False,
            "fusion_validated": False,
            "print_validated": False,
        },
    }
    config["config_digest"] = canonical_digest(config)
    return validate_external_tournament_config(config)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = build_config()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"CONFIG_DIGEST={config['config_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
