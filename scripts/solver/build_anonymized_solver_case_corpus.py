"""Build a reviewed corpus candidate from one local SolverCaseBundle."""

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
    CORPUS_TIER_EXTENDED,
    anonymize_solver_case_project,
    build_solver_case,
    build_solver_case_corpus,
    solver_case_from_bundle,
    validate_solver_case_bundle,
    validate_solver_case_corpus,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a separate, reviewable corpus candidate from one explicit "
            "local bundle. The source manifest is never modified."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Write only the reviewed case instead of appending the source manifest.",
    )
    args = parser.parse_args(argv)

    manifest_path = args.manifest.resolve()
    bundle_path = args.bundle.resolve()
    output_path = args.output.resolve()
    if output_path in {manifest_path, bundle_path}:
        parser.error("--output must differ from both input files for explicit review.")

    candidate = build_anonymized_corpus_candidate(
        _read_json(manifest_path),
        _read_json(bundle_path),
        case_id=args.case_id,
        source_id=args.source_id,
    )
    if args.standalone:
        reviewed = next(case for case in candidate["cases"] if case["case_id"] == args.case_id)
        candidate = build_solver_case_corpus([reviewed])
    _write_json_atomic(output_path, candidate)
    print(
        json.dumps(
            {
                "case_id": args.case_id,
                "case_count": candidate["summary"]["case_count"],
                "corpus_digest": candidate["corpus_digest"],
                "output": str(output_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def build_anonymized_corpus_candidate(
    manifest: object,
    bundle: object,
    *,
    case_id: str,
    source_id: str,
) -> dict[str, object]:
    """Return a separate canonical candidate without editing either input."""

    corpus = validate_solver_case_corpus(manifest)
    validated_bundle = validate_solver_case_bundle(bundle)
    imported = solver_case_from_bundle(
        validated_bundle,
        case_id=case_id,
        execution_tier=CORPUS_TIER_EXTENDED,
    )
    anonymized = build_solver_case(
        case_id,
        anonymize_solver_case_project(validated_bundle["project"]),
        solver_settings=imported["solver_settings"],
        execution_tier=CORPUS_TIER_EXTENDED,
        accepted_statuses=imported["expectations"]["accepted_statuses"],
        baseline=imported["baseline"],
        source={
            "kind": "solver_case_bundle",
            "id": source_id,
            "bundle_digest": validated_bundle["bundle_digest"],
        },
    )
    return build_solver_case_corpus([*corpus["cases"], anonymized])


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
