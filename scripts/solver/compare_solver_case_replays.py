"""Compare two P64-L05D replay reports through the functional-first gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.solver_case_corpus import (  # noqa: E402
    compare_solver_case_replays,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two exact-corpus reports. Functional regressions always "
            "win over non-normative timing gains."
        )
    )
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--maximum-performance-regression-ratio",
        type=float,
        default=0.10,
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    comparison = compare_solver_case_replays(
        _read_json(args.baseline),
        _read_json(args.candidate),
        maximum_performance_regression_ratio=(args.maximum_performance_regression_ratio),
    )
    rendered = json.dumps(
        comparison,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    if not args.quiet:
        print(rendered)
    if args.output is not None:
        _write_json_atomic(args.output, rendered + "\n")
    return 0 if comparison["summary"]["candidate_acceptable"] else 2


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json_atomic(path: Path, rendered: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
