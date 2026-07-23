"""Construit le manifest versionné P64-L06B depuis des corpus explicites."""

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

from board_game_insert_generator.solver_benchmark_corpus import (  # noqa: E402
    build_solver_benchmark_manifest,
    validate_solver_benchmark_manifest,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the deterministic P64-L06 T0/T1 manifest. Each source uses "
            "the portable form SOURCE_ID=JSON_PATH."
        )
    )
    parser.add_argument(
        "--regression-corpus",
        action="append",
        required=True,
        metavar="SOURCE_ID=JSON_PATH",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--check-existing",
        action="store_true",
        help="Compare with --output instead of writing it.",
    )
    args = parser.parse_args(argv)
    sources = _regression_sources(args.regression_corpus, parser)
    manifest = build_solver_benchmark_manifest(sources)
    output = args.output.resolve()
    if args.check_existing:
        existing = validate_solver_benchmark_manifest(_read_json(output))
        if existing != manifest:
            print(
                json.dumps(
                    {
                        "status": "mismatch",
                        "expected_digest": manifest["manifest_digest"],
                        "actual_digest": existing["manifest_digest"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 1
        status = "identical"
    else:
        _write_json_atomic(output, manifest)
        status = "written"
    print(
        json.dumps(
            {
                "status": status,
                "manifest_digest": manifest["manifest_digest"],
                "regression_case_count": manifest["summary"]["regression_case_count"],
                "generated_case_count": manifest["summary"]["generated_case_count"],
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _regression_sources(
    values: Sequence[str],
    parser: argparse.ArgumentParser,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for value in values:
        source_id, separator, raw_path = value.partition("=")
        if not separator or not source_id.strip() or not raw_path.strip():
            parser.error("--regression-corpus must use SOURCE_ID=JSON_PATH.")
        source_id = source_id.strip()
        if source_id in result:
            parser.error(f"duplicate regression source id: {source_id}")
        result[source_id] = _read_json(Path(raw_path).resolve())
    return result


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json_atomic(path: Path, value: object) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
