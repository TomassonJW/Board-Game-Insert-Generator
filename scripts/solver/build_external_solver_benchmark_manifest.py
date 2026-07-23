"""Construit le manifest P64-L07B depuis le manifest historique L06."""

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

from board_game_insert_generator.external_solver_benchmark_corpus import (  # noqa: E402
    build_external_solver_benchmark_manifest,
    validate_external_solver_benchmark_manifest,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the deterministic P64-L07 T0/T1 manifest from the consumed "
            "historical L06 manifest."
        )
    )
    parser.add_argument("--historical-l06-manifest", required=True, type=Path)
    parser.add_argument(
        "--sealed-holdout",
        required=True,
        type=Path,
        help="Private sidecar created once and kept outside version control.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--check-existing",
        action="store_true",
        help="Compare with --output instead of writing it.",
    )
    args = parser.parse_args(argv)
    manifest = build_external_solver_benchmark_manifest(
        _read_json(args.historical_l06_manifest.resolve()),
        _read_json(args.sealed_holdout.resolve()),
    )
    output = args.output.resolve()
    if args.check_existing:
        existing = validate_external_solver_benchmark_manifest(_read_json(output))
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
                "regression_case_count": manifest["summary"][
                    "regression_case_count"
                ],
                "generated_case_count": manifest["summary"][
                    "bgig_generated_case_count"
                ],
                "public_source_count": manifest["summary"]["public_source_count"],
                "sealed_holdout_digest": manifest["sealed_holdout_receipt"][
                    "sealed_holdout_digest"
                ],
                "holdout_recipe_records_embedded": manifest["invariants"][
                    "holdout_recipe_records_embedded"
                ],
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json_atomic(path: Path, value: object) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(rendered.encode("utf-8"))
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
