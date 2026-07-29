#!/usr/bin/env python3
"""Prepare the public P64-L09S-V composite tray fixture and receipt."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from time import perf_counter

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    ARTIFACT_KIND_MINIMAL,
    StagedCalculationSession,
)
from board_game_insert_generator.top_inset_reservation import (
    certify_top_inset_reservation_prisms,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


ADDIN_VERSION = "0.1.69"
REQUESTED_SETTINGS = {"method": "auto", "effort": "normal"}
FINISHING_EFFORT = "normal"
FIXTURE_FILENAME = "p64-l09sv-01-recent-tray-composite.bgig.json"


def recent_tray_project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "P64-L09S-V recent tray composite"
    project["box"] = {
        "inner_dimensions_mm": {"x": 200.0, "y": 150.0, "z": 60.0},
        "usable_height_mm": 59.6,
        "lid_clearance_mm": 0.4,
    }
    project["layout"] = {
        "layout_clearance_mm": 0.6,
        "container_box_xy_clearance_mm": 0.6,
        "container_z_clearance_mm": 0.6,
        "default_wall_thickness_mm": 1.2,
        "default_floor_thickness_mm": 1.2,
        "default_content_clearance_mm": 0.6,
    }
    project["container_groups"] = [
        {
            "id": "018",
            "name": "Conteneur limite 018",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        }
    ]
    project["contents"] = [
        {
            "id": "content-018",
            "name": "Contenu limite 018",
            "shape_kind": "custom",
            "dimensions_mm": {"x": 19.6, "y": 19.6, "z": 29.8},
            "quantity": 1,
            "container_group_id": "018",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    project["flat_items"] = [
        {
            "id": "tray",
            "name": "Plateau recent",
            "kind": "board",
            "dimensions_mm": {"x": 100.0, "y": 80.0, "z": 1.0},
            "quantity": 1,
            "stack_order": 0,
            "origin_mm": {"x": 10.0, "y": 10.0},
        }
    ]
    return normalize_project_draft(project).project


def recent_limit_contract(project: dict[str, object]) -> dict[str, object]:
    placements = [
        {
            "id": "container:018",
            "name": "Conteneur limite 018",
            "origin_mm": {"x": 20.0, "y": 20.0, "z": 21.2},
            "world_size_mm": {"x": 23.2, "y": 23.2, "z": 31.6},
        }
    ]
    result = certify_top_inset_reservation_prisms(project, placements)
    if result["status"] != "reserved_prisms_certified":
        raise RuntimeError("The recent minimal reservation contract is not certified.")
    placement = result["placements"][0]
    size = placement["world_size_mm"]
    support_plane = float(result["reserved_prisms"][0]["origin_mm"]["z"])
    body_top = float(placement["origin_mm"]["z"]) + float(size["z"])
    gap = round(support_plane - body_top, 4)
    if size != {"x": 23.2, "y": 23.2, "z": 31.6} or gap != 5.8:
        raise RuntimeError("The recent 23.2 / 31.6 / 5.8 contract drifted.")
    if any(
        certificate.get("certified") is not True
        for certificate in result["reservation_certificates"]
    ):
        raise RuntimeError("The recent reserved prism is not post-certified.")
    return {
        "body_origin_mm": deepcopy(placement["origin_mm"]),
        "body_size_mm": deepcopy(size),
        "body_top_z_mm": round(body_top, 4),
        "support_plane_z_mm": round(support_plane, 4),
        "gap_below_tray_mm": gap,
        "artificial_growth_mm": 0.0,
        "old_forbidden_height_mm": 38.4,
        "support_required": False,
        "reserved_prisms_certified": True,
    }


def run_end_to_end(
    project: dict[str, object],
    *,
    include_materialization_batches: bool = False,
) -> dict[str, object]:
    engine = IncrementalLocalAnalysisEngine(project, effort_profile="normal")
    session = StagedCalculationSession(project, solver_settings=REQUESTED_SETTINGS)
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=REQUESTED_SETTINGS,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )

    calculation_started = perf_counter()
    calculated = session.calculate_layout(
        request_id="p64-l09sv-recent-calculate",
        request_revision=0,
    )
    calculation_ms = round((perf_counter() - calculation_started) * 1000.0, 3)
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError("The recent tray fixture has no certified minimal plan.")
    minimal_selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
    minimal_plan = minimal_selection["partition"]
    minimal_placement = minimal_plan["placements"][0]
    minimum = minimal_placement["minimum_outer_envelope_mm"]
    if minimum != {"x": 23.2, "y": 23.2, "z": 31.6}:
        raise RuntimeError(f"Unexpected recent minimum envelope: {minimum!r}.")
    if float(minimal_placement.get("reservation_required_z_compensation_mm", 0.0)) != 0.0:
        raise RuntimeError("The minimal plan still manufactures tray support.")
    minimal_cad = build_partition_cad(
        project,
        partition=minimal_plan,
        artifact_identity=minimal_selection,
        effort_profile="normal",
    )
    if minimal_cad["status"] != "ready_for_fusion":
        raise RuntimeError("The recent minimal CAD IR is not ready.")

    finishing_started = perf_counter()
    finalized = session.finalize_volume(finishing_effort_profile=FINISHING_EFFORT)
    finishing_ms = round((perf_counter() - finishing_started) * 1000.0, 3)
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError("The recent tray fixture has no certified final plan.")
    final_selection = session.select_materializable_artifact(ARTIFACT_KIND_FINALIZED)
    final_plan = final_selection["partition"]
    finalization = final_plan["finalization"]
    certificate = finalization["composite_materialization_certificate"]
    if (
        finalization["selected_plan_source"]
        != "f_xy_composite_v2_union_cavities_insets"
        or certificate.get("certified") is not True
        or certificate.get("printable_residual_volume_mm3") != 0.0
        or certificate.get("cavity_calibrations_match_source_contract")
        is not True
        or certificate.get("cavity_anchor_certificate", {}).get(
            "certified"
        )
        is not True
    ):
        raise RuntimeError("The recent composite finalization is not exact.")
    final_cad = build_partition_cad(
        project,
        partition=final_plan,
        artifact_identity=final_selection,
        effort_profile="normal",
    )
    if final_cad["status"] != "ready_for_fusion":
        raise RuntimeError("The recent final CAD IR is not ready.")
    fusion = generation_plan_from_cad_ir(
        final_cad["cad_ir"],
        FUSION_GENERATION_MODE_COMPACT_ONLY,
    )
    if (
        fusion.module_component_count != 1
        or not fusion.additive_prism_joins
        or not any(
            cut.cavity_source == "top_inset_reservation"
            for cut in fusion.cavity_cuts
        )
    ):
        raise RuntimeError("The recent Fusion plan lost its owner, unions, or tray cut.")

    result = {
        "minimal": {
            "artifact_digest": minimal_selection["artifact_digest"],
            "partition_plan_digest": minimal_selection["partition_plan_digest"],
            "minimum_outer_envelope_mm": deepcopy(minimum),
            "reservation_required_z_compensation_mm": 0.0,
            "materializable": True,
            "cad_status": minimal_cad["status"],
            "observed_ms": calculation_ms,
        },
        "finalization": {
            "artifact_digest": final_selection["artifact_digest"],
            "partition_plan_digest": final_selection["partition_plan_digest"],
            "source_minimal_artifact_digest": finalization[
                "source_minimal_artifact_digest"
            ],
            "selected_plan_source": finalization["selected_plan_source"],
            "composite_certificate": deepcopy(certificate),
            "materializable": True,
            "cad_status": final_cad["status"],
            "cad_ir_digest": final_cad["cad_ir_digest"],
            "observed_ms": finishing_ms,
        },
        "fusion_plan": {
            "user_component_count": fusion.module_component_count,
            "joined_annex_count": len(fusion.additive_prism_joins),
            "top_inset_cut_count": sum(
                1
                for cut in fusion.cavity_cuts
                if cut.cavity_source.startswith("top_inset")
            ),
            "all_annexes_xy": all(
                join.attachment_axis in {"x", "y"}
                and join.policy == "finalized_container_union_v3"
                for join in fusion.additive_prism_joins
            ),
            "fusion_observed": False,
        },
    }
    if include_materialization_batches:
        result["fusion_plan"]["logical_additive_prism_join_count"] = len(
            fusion.additive_prism_joins
        )
        result["fusion_plan"]["additive_prism_join_batch_count"] = (
            fusion.additive_prism_join_batch_count
        )
        result["fusion_plan"]["logical_cavity_cut_count"] = len(
            fusion.cavity_cuts
        )
        result["fusion_plan"]["cavity_cut_batch_count"] = (
            fusion.cavity_cut_batch_count
        )
    return result


def _preflight_digest(summary: dict[str, object]) -> str:
    payload = deepcopy(summary)
    payload.pop("preflight_digest", None)
    payload["end_to_end"]["minimal"].pop("observed_ms", None)
    payload["end_to_end"]["finalization"].pop("observed_ms", None)
    return canonical_digest(payload)


def build_preflight() -> tuple[dict[str, object], dict[str, object]]:
    project = recent_tray_project()
    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l09sv_fusion_preflight.v1",
        "addin_version": ADDIN_VERSION,
        "fixture": {
            "filename": FIXTURE_FILENAME,
            "project_digest": canonical_digest(project),
        },
        "recent_limit_contract": recent_limit_contract(project),
        "end_to_end": run_end_to_end(project),
        "expected_ui": {
            "buttons": {
                "Calculer": "blue",
                "Finaliser": "orange_or_violet",
                "Materialiser": "green",
            },
            "calculation_budgets_seconds": [3, 10, 20, 60, 180],
            "finishing_budgets_seconds": [3, 10, 20, 60, 180],
        },
        "holdout_opened": False,
        "benchmark_executed": False,
        "fusion_validated": False,
        "print_validated": False,
    }
    summary["preflight_digest"] = _preflight_digest(summary)
    return project, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    project, summary = build_preflight()
    if args.output_directory is not None:
        args.output_directory.mkdir(parents=True, exist_ok=True)
        (args.output_directory / FIXTURE_FILENAME).write_text(
            json.dumps(project, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        "P64_L09SV_PREFLIGHT_OK "
        f"digest={summary['preflight_digest']} "
        "minimum=23.2x23.2x31.6 gap=5.8 "
        f"joins={summary['end_to_end']['fusion_plan']['joined_annex_count']} "
        f"cuts={summary['end_to_end']['fusion_plan']['top_inset_cut_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
