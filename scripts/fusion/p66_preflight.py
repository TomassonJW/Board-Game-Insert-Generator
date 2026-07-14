"""Build deterministic, local-only evidence for the P66 Fusion acceptance gate.

This script intentionally consumes the same pure-Python project, partition, CAD
IR and Fusion-plan adapters as the add-in. It does not write a user project or
call Fusion; the PowerShell preparer owns those explicit local handoff actions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
for candidate in (ROOT / "src", ROOT):
    candidate_text = str(candidate)
    if candidate_text not in sys.path:
        sys.path.insert(0, candidate_text)

from board_game_insert_generator.partition_cad import (  # noqa: E402
    PARTITION_CAD_STATUS_READY,
    build_partition_cad,
)
from board_game_insert_generator.partition_result_view import build_partition_result_view  # noqa: E402
from board_game_insert_generator.partition_solver import solve_partition_plan  # noqa: E402
from board_game_insert_generator.project_v1 import normalize_project_draft  # noqa: E402
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (  # noqa: E402
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


P66_PREFLIGHT_SCHEMA = "bgig.p66.preflight.v1"


def stable_digest(payload: object) -> str:
    """Return the canonical digest used for deterministic preflight evidence."""

    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_preflight(raw_project: object) -> dict[str, object]:
    """Resolve all P66 evidence without persisting or materializing anything."""

    project = normalize_project_draft(raw_project).project
    partition = solve_partition_plan(project)
    result_view = (
        build_partition_result_view(partition)
        if partition["summary"]["status"] in {"constructed", "proposal_with_residuals"}
        else None
    )
    cad_build = build_partition_cad(project, partition=partition)
    fusion_plan = None
    if cad_build["status"] == PARTITION_CAD_STATUS_READY:
        fusion_plan = generation_plan_from_cad_ir(
            cad_build["cad_ir"],
            FUSION_GENERATION_MODE_COMPACT_ONLY,
        ).to_dict()

    return {
        "schema_version": P66_PREFLIGHT_SCHEMA,
        "normalized_project": project,
        "source_digest": stable_digest(project),
        "partition": partition,
        "result_view": result_view,
        "cad_build": cad_build,
        "fusion_generation_plan": fusion_plan,
        "summary": {
            "status": partition["summary"]["status"],
            "plan_digest": partition["plan_digest"],
            "cad_digest": cad_build.get("cad_ir_digest") or "",
            "source_digest": stable_digest(project),
            "materializable": partition["summary"]["materializable"],
            "cad_ready": cad_build["status"] == PARTITION_CAD_STATUS_READY,
            "fusion_plan_ready": fusion_plan is not None,
        },
    }


def write_preflight(preflight: dict[str, object], output_directory: Path) -> None:
    """Write named, human-readable artifacts for the explicit Fusion handoff."""

    output_directory.mkdir(parents=True, exist_ok=True)
    artifact_names = {
        "normalized_project": "normalized_project.json",
        "partition": "partition_plan.json",
        "result_view": "partition_result_view.json",
        "cad_build": "cad_build.json",
        "fusion_generation_plan": "fusion_generation_plan.json",
        "summary": "preflight_summary.json",
    }
    for key, filename in artifact_names.items():
        payload = preflight[key]
        (output_directory / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="P66 project JSON fixture")
    parser.add_argument("--output-dir", type=Path, required=True, help="Evidence directory")
    args = parser.parse_args()

    raw_project: Any = json.loads(args.fixture.read_text(encoding="utf-8"))
    preflight = build_preflight(raw_project)
    write_preflight(preflight, args.output_dir)
    summary = preflight["summary"]
    print(
        "P66 preflight: "
        f"status={summary['status']} plan={summary['plan_digest']} "
        f"cad={summary['cad_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
