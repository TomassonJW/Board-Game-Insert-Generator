"""Télécharge une source publique P64-L07 et vérifie son empreinte."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import BinaryIO, Sequence
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.external_solver_benchmark_corpus import (  # noqa: E402
    MAX_PUBLIC_SOURCE_BYTES,
    ExternalSolverBenchmarkCorpusError,
    public_source_catalog,
    verify_downloaded_public_source,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch one pinned P64-L07 public source into a caller-selected "
            "workspace cache and verify every required digest."
        )
    )
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--check-existing",
        action="store_true",
        help="Verify --output without network access.",
    )
    args = parser.parse_args(argv)
    sources = {
        str(source["source_id"]): source for source in public_source_catalog()
    }
    if args.source_id not in sources:
        parser.error(f"unknown source id: {args.source_id}")
    source = sources[args.source_id]
    output = args.output.resolve()
    if args.check_existing:
        result = verify_downloaded_public_source(source, output)
    else:
        if output.exists():
            raise ExternalSolverBenchmarkCorpusError(
                "Output already exists; use --check-existing or a fresh path."
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".part")
        if temporary.exists():
            raise ExternalSolverBenchmarkCorpusError(
                "Partial output already exists; inspect it before retrying."
            )
        try:
            request = Request(
                str(source["download_url"]),
                headers={"User-Agent": "BGIG-P64-L07B/1"},
            )
            with urlopen(request, timeout=60) as response:
                _copy_bounded(response, temporary)
            result = verify_downloaded_public_source(source, temporary)
            temporary.replace(output)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def _copy_bounded(source: BinaryIO, destination: Path) -> None:
    written = 0
    with destination.open("xb") as target:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > MAX_PUBLIC_SOURCE_BYTES:
                raise ExternalSolverBenchmarkCorpusError(
                    "Public source exceeds the 64 MiB acquisition cap."
                )
            target.write(chunk)


if __name__ == "__main__":
    raise SystemExit(main())
