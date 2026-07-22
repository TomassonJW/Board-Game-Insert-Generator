"""Replay a versioned L05D corpus or one local SolverCaseBundle."""

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
    CORPUS_TIER_CI,
    CORPUS_TIER_EXTENDED,
    build_solver_case_corpus,
    replay_solver_case_corpus,
    solver_case_from_bundle,
)


DEFAULT_MANIFEST = ROOT / "tests" / "fixtures" / "p64_l05d_solver_case_corpus.v1.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Replay deterministic solver facts separately from non-normative "
            "wall-clock samples. No solver or Fusion state is modified."
        )
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Versioned corpus manifest (default: checked-in L05D corpus).",
    )
    source.add_argument(
        "--bundle",
        type=Path,
        help="One local bgig.solver_case_bundle.v1 to replay ephemerally.",
    )
    parser.add_argument(
        "--case-id",
        default="captured-solver-case",
        help="Portable case id used only with --bundle.",
    )
    parser.add_argument(
        "--tier",
        choices=(CORPUS_TIER_CI, CORPUS_TIER_EXTENDED, "all"),
        default=CORPUS_TIER_CI,
    )
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout; requires no change to the JSON report.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON report path; stdout is emitted unless --quiet.",
    )
    args = parser.parse_args(argv)

    if args.bundle is not None:
        bundle = _read_json(args.bundle)
        case = solver_case_from_bundle(
            bundle,
            case_id=args.case_id,
            execution_tier=CORPUS_TIER_EXTENDED,
        )
        corpus = build_solver_case_corpus([case])
        tiers = (CORPUS_TIER_EXTENDED,)
    else:
        corpus = _read_json(args.manifest)
        tiers = (CORPUS_TIER_CI, CORPUS_TIER_EXTENDED) if args.tier == "all" else (args.tier,)
    report = replay_solver_case_corpus(
        corpus,
        include_tiers=tiers,
        repetitions=args.repetitions,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if not args.quiet:
        print(rendered)
    if args.output is not None:
        _write_json_atomic(args.output, rendered + "\n")
    return 0 if report["summary"]["all_expectations_met"] else 2


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json_atomic(path: Path, rendered: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
