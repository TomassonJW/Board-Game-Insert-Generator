"""Worker local isolé pour mesurer la baseline BGIG dans P64-L07D."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from board_game_insert_generator.solver_benchmark_adapters import (
    CURRENT_BGIG_ADAPTER_ID,
    run_benchmark_adapter,
)


def main(input_path: str, output_path: str) -> None:
    case = json.loads(Path(input_path).read_text(encoding="utf-8"))
    execution = run_benchmark_adapter(case, CURRENT_BGIG_ADAPTER_ID)
    Path(output_path).write_text(
        json.dumps(execution.report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
