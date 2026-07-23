"""Crée une fois le sidecar privé du holdout P64-L07B."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from secrets import randbelow, token_hex
import sys
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.external_solver_benchmark_corpus import (  # noqa: E402
    build_external_sealed_holdout,
)
from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a fresh private P64-L07 holdout sidecar. The output must "
            "stay outside version control until the sealed selection."
        )
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(
            "Sealed holdout output already exists; never regenerate it in place."
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    sealed = build_external_sealed_holdout(
        seed_base=1_000_000_000 + randbelow(8_000_000_000),
        split_offset=1 + randbelow(10_000),
        campaign_nonce=token_hex(32),
    )
    _write_json_fresh(output, sealed)
    print(
        json.dumps(
            {
                "status": "sealed",
                "schema_version": sealed["schema_version"],
                "sealed_holdout_digest": sealed["sealed_holdout_digest"],
                "case_commitment_digest": canonical_digest(
                    sealed["case_records"]
                ),
                "case_count": len(sealed["case_records"]),
                "solver_invocation_count": 0,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _write_json_fresh(path: Path, value: object) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(
            "Sealed holdout temporary output already exists; inspect it first."
        )
    try:
        temporary.write_bytes(rendered.encode("utf-8"))
        temporary.replace(path)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


if __name__ == "__main__":
    raise SystemExit(main())
