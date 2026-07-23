from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from board_game_insert_generator.solver_benchmark_campaign import (
    CampaignPhaseConfig,
    run_campaign_phase,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one resumable P64-L06 benchmark phase."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--split",
        required=True,
        choices=("regression", "discovery", "tuning", "holdout"),
    )
    parser.add_argument("--adapter", action="append", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--max-case-executions", required=True, type=int)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument(
        "--experiment",
        default="canonical",
        choices=(
            "canonical",
            "relax_rotation_policy",
            "remove_top_reservations",
            "relax_rotation_and_reservations",
            "lane_center_quick_v1",
            "lane_lowest_quick_v1",
            "lane_interleave_quick_v1",
        ),
    )
    parser.add_argument("--holdout-selection", type=Path)
    return parser


def _read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    selection = _read(args.holdout_selection) if args.holdout_selection else None
    execution = run_campaign_phase(
        _read(args.manifest),
        CampaignPhaseConfig(
            split=args.split,
            adapter_ids=tuple(args.adapter),
            base_sha=args.base_sha,
            branch=args.branch,
            max_case_executions=args.max_case_executions,
            case_ids=tuple(args.case_id),
            experiment_id=args.experiment,
        ),
        args.output_dir,
        holdout_selection=selection,
    )
    print(
        json.dumps(
            {
                "checkpoint_digest": execution.checkpoint["checkpoint_digest"],
                "executed_now": execution.executed_now,
                "run_id": execution.checkpoint["run_id"],
                "skipped_existing": execution.skipped_existing,
                "status": execution.checkpoint["stop_reason"],
                "summary_digest": execution.checkpoint["summary_digest"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
