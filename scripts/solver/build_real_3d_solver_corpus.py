"""Génère le manifest public P64-L08D et son sidecar privé scellé."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.real_3d_solver_corpus import (  # noqa: E402
    build_open_case_records,
    build_public_manifest,
    build_sealed_holdout,
    verify_sealed_holdout,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sealed-holdout", type=Path, required=True)
    parser.add_argument("--campaign-nonce")
    args = parser.parse_args()

    sealed = build_sealed_holdout(campaign_nonce=args.campaign_nonce)
    manifest = build_public_manifest(build_open_case_records(), sealed)
    receipt = verify_sealed_holdout(manifest, sealed)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.sealed_holdout.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.sealed_holdout.write_text(
        json.dumps(sealed, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest": str(args.manifest),
                "manifest_digest": manifest["manifest_digest"],
                "sealed_holdout": str(args.sealed_holdout),
                "sealed_holdout_digest": receipt["sealed_holdout_digest"],
                "open_case_count": manifest["open_case_count"],
                "holdout_case_count": receipt["case_count"],
                "solver_invocation_count": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
