"""Construit le corpus produit P64-L09W-B avec reprise par checkpoint."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import secrets
import sys
from time import monotonic


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from board_game_insert_generator.product_solver_robustness_corpus import (  # noqa: E402
    HOLDOUT_POSITIVE_COUNT,
    OPEN_POSITIVE_COUNT,
    build_holdout_recipe_plan,
    build_negative_control_records,
    build_open_recipe_plan,
    build_positive_case_record,
    build_public_manifest,
    seal_holdout_records,
    validate_positive_case_record,
    verify_sealed_holdout,
)


@dataclass(frozen=True)
class CheckpointBuildResult:
    records: list[dict[str, object]]
    existing_record_count: int
    new_record_count: int
    remaining_record_count: int


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sealed-holdout", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--campaign-nonce")
    parser.add_argument(
        "--max-new-records",
        type=_positive_integer,
        help=(
            "Nombre maximal de nouveaux checkpoints construits pendant cette "
            "invocation, partagé entre open et holdout."
        ),
    )
    args = parser.parse_args()

    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    nonce = _load_or_create_nonce(
        args.checkpoint_dir / "holdout_nonce.private.txt",
        supplied=args.campaign_nonce,
    )
    started = monotonic()

    open_recipes = build_open_recipe_plan()
    open_result = _build_checkpointed_records(
        "open",
        open_recipes,
        checkpoint_dir=args.checkpoint_dir / "open",
        max_new_records=args.max_new_records,
    )
    remaining_budget = (
        None
        if args.max_new_records is None
        else args.max_new_records - open_result.new_record_count
    )
    holdout_recipes = build_holdout_recipe_plan(campaign_nonce=nonce)
    holdout_result = _build_checkpointed_records(
        "holdout",
        holdout_recipes,
        checkpoint_dir=args.checkpoint_dir / "holdout",
        max_new_records=remaining_budget,
    )
    new_record_count = (
        open_result.new_record_count + holdout_result.new_record_count
    )
    remaining_record_count = (
        open_result.remaining_record_count
        + holdout_result.remaining_record_count
    )
    if remaining_record_count:
        print(
            json.dumps(
                {
                    "status": "paused",
                    "elapsed_seconds": round(monotonic() - started, 3),
                    "max_new_records": args.max_new_records,
                    "new_record_count": new_record_count,
                    "open_checkpoint_count": len(open_result.records),
                    "holdout_checkpoint_count": len(holdout_result.records),
                    "remaining_record_count": remaining_record_count,
                    "solver_invocation_count": 0,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )
        return 0

    open_records = open_result.records
    holdout_records = holdout_result.records
    if len(open_records) != OPEN_POSITIVE_COUNT:
        raise RuntimeError("Open positive checkpoint count mismatch.")
    if len(holdout_records) != HOLDOUT_POSITIVE_COUNT:
        raise RuntimeError("Holdout positive checkpoint count mismatch.")

    sealed = seal_holdout_records(
        campaign_nonce=nonce,
        records=holdout_records,
    )
    negatives = build_negative_control_records()
    manifest = build_public_manifest(open_records, negatives, sealed)
    receipt = verify_sealed_holdout(manifest, sealed)

    _write_json(args.manifest, manifest)
    _write_json(args.sealed_holdout, sealed)
    print(
        json.dumps(
            {
                "status": "complete",
                "elapsed_seconds": round(monotonic() - started, 3),
                "manifest": str(args.manifest),
                "manifest_digest": manifest["manifest_digest"],
                "open_positive_case_count": len(open_records),
                "negative_control_count": len(negatives),
                "sealed_holdout": str(args.sealed_holdout),
                "sealed_holdout_digest": receipt["sealed_holdout_digest"],
                "holdout_positive_case_count": len(holdout_records),
                "holdout_opening_count": receipt["opening_count"],
                "new_record_count": new_record_count,
                "solver_invocation_count": 0,
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


def _build_checkpointed_records(
    label: str,
    recipes: list[dict[str, object]],
    *,
    checkpoint_dir: Path,
    max_new_records: int | None,
) -> CheckpointBuildResult:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    existing_record_count = 0
    new_record_count = 0
    remaining_record_count = 0
    total = len(recipes)
    for index, recipe in enumerate(recipes):
        path = checkpoint_dir / f"{index:03d}.json"
        built_record = False
        if path.exists():
            record = validate_positive_case_record(
                json.loads(path.read_text(encoding="utf-8")),
                reconstruct=False,
            )
            if record["recipe_digest"] != canonical_digest(recipe):
                raise RuntimeError(
                    f"Stale {label} checkpoint at ordinal {index}."
                )
            existing_record_count += 1
        elif (
            max_new_records is not None
            and new_record_count >= max_new_records
        ):
            remaining_record_count += 1
            continue
        else:
            print(
                json.dumps(
                    {
                        "status": "building",
                        "split": label,
                        "ordinal": index,
                        "new_record_number": new_record_count + 1,
                        "max_new_records": max_new_records,
                        "solver_invocation_count": 0,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                flush=True,
            )
            record = build_positive_case_record(recipe)
            _write_json(path, record)
            new_record_count += 1
            built_record = True
        records.append(record)
        if not path.exists():
            raise RuntimeError(
                f"Checkpoint {label} ordinal {index} was not persisted."
            )
        if built_record:
            print(
                json.dumps(
                    {
                        "status": "checkpoint",
                        "split": label,
                        "ordinal": index,
                        "available": len(records),
                        "total": total,
                        "new_record_count": new_record_count,
                        "solver_invocation_count": 0,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                flush=True,
            )
    return CheckpointBuildResult(
        records=records,
        existing_record_count=existing_record_count,
        new_record_count=new_record_count,
        remaining_record_count=remaining_record_count,
    )


def _positive_integer(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("expected an integer greater than zero")
    return value


def _load_or_create_nonce(path: Path, *, supplied: str | None) -> str:
    if path.exists():
        nonce = path.read_text(encoding="utf-8").strip()
        if supplied is not None and supplied != nonce:
            raise RuntimeError("Supplied nonce differs from private checkpoint.")
        return nonce
    nonce = supplied or secrets.token_hex(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(nonce + "\n", encoding="utf-8")
    return nonce


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
