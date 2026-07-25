#!/usr/bin/env python3
"""Prépare les fixtures publiques et le reçu de la gate P64-L09R-V."""

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


ADDIN_VERSION = "0.1.64"
REQUESTED_SETTINGS = {"method": "auto", "effort": "normal"}
FINISHING_EFFORT = "quick"
FIXTURE_FILENAMES = {
    "preference": "p64-l09rv-01-preference-envelope.bgig.json",
    "tray_flow": "p64-l09rv-02-tray-separated-flow.bgig.json",
}
ROOT = Path(__file__).resolve().parents[2]
P66_COMPLETE_FIXTURE = ROOT / "scripts" / "fusion" / "p66_mvp_complete_project.json"
PUBLIC_28X30_RECEIPT = ROOT / "tests" / "fixtures" / "p64_l08l_scip_repeated_fill_regression.v1.json"


def _group(identifier: str) -> dict[str, object]:
    return {
        "id": identifier,
        "name": f"Bac public {identifier}",
        "wall_thickness_mm": None,
        "floor_thickness_mm": None,
    }


def _content(
    identifier: str,
    group_id: str,
    dimensions: tuple[float, float, float],
) -> dict[str, object]:
    return {
        "id": identifier,
        "name": f"Contenu public {identifier}",
        "shape_kind": "custom",
        "dimensions_mm": dict(zip(("x", "y", "z"), dimensions)),
        "quantity": 1,
        "container_group_id": group_id,
        "content_clearance_mm": None,
        "measurement_confidence": "exact",
    }


def preference_project() -> dict[str, object]:
    """Force un choix entre petit-dessous préféré et inversion admissible."""

    project = blank_project_v1()
    project["project_name"] = "P64-L09R-V préférence d empilement par enveloppe"
    project["box"] = {
        "inner_dimensions_mm": {"x": 44.0, "y": 22.0, "z": 20.0},
        "usable_height_mm": 20.0,
        "lid_clearance_mm": 0.0,
    }
    project["layout"] = {
        "layout_clearance_mm": 0.0,
        "container_box_xy_clearance_mm": 0.0,
        "container_z_clearance_mm": 0.0,
        "default_wall_thickness_mm": 1.2,
        "default_floor_thickness_mm": 1.2,
        "default_content_clearance_mm": 0.6,
    }
    project["container_groups"] = [
        _group("small-a"),
        _group("small-b"),
        _group("large"),
    ]
    project["contents"] = [
        _content("small-a-content", "small-a", (18.0, 18.0, 8.0)),
        _content("small-b-content", "small-b", (18.0, 18.0, 8.0)),
        _content("large-content", "large", (38.0, 18.0, 8.0)),
    ]
    return normalize_project_draft(project).project


def tray_flow_project() -> dict[str, object]:
    project = json.loads(P66_COMPLETE_FIXTURE.read_text(encoding="utf-8"))
    project["project_name"] = "P64-L09R-V plateau calcul finition séparée"
    return normalize_project_draft(project).project


def _run_staged_flow(project: dict[str, object], case_id: str) -> dict[str, object]:
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
        request_id=f"p64-l09rv-{case_id}-calculate",
        request_revision=0,
    )
    calculation_observed_ms = round((perf_counter() - calculation_started) * 1000.0, 3)
    minimal = calculated["staged_calculation"]["minimal_layout"]
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError(f"Le cas {case_id} ne produit pas de plan minimal certifié.")
    if not minimal["materializable_without_finalization"]:
        raise RuntimeError(f"Le cas {case_id} ne permet pas la matérialisation minimale.")
    minimal_selection = session.select_materializable_artifact(ARTIFACT_KIND_MINIMAL)
    minimal_cad = build_partition_cad(
        project,
        partition=minimal_selection["partition"],
        artifact_identity=minimal_selection,
        effort_profile="normal",
    )
    if minimal_cad["status"] != "ready_for_fusion":
        raise RuntimeError(f"Le CAD minimal du cas {case_id} n est pas prêt.")

    finishing_started = perf_counter()
    finalized = session.finalize_volume(finishing_effort_profile=FINISHING_EFFORT)
    finishing_observed_ms = round((perf_counter() - finishing_started) * 1000.0, 3)
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError(f"Le cas {case_id} ne produit pas de plan final certifié.")
    final_selection = session.select_materializable_artifact(ARTIFACT_KIND_FINALIZED)
    final_cad = build_partition_cad(
        project,
        partition=final_selection["partition"],
        artifact_identity=final_selection,
        effort_profile="normal",
    )
    if final_cad["status"] != "ready_for_fusion":
        raise RuntimeError(f"Le CAD final du cas {case_id} n est pas prêt.")

    return {
        "minimal": {
            "artifact_digest": minimal_selection["artifact_digest"],
            "partition_plan_digest": minimal_selection["partition_plan_digest"],
            "materializable": True,
            "cad_status": minimal_cad["status"],
            "observed_ms": calculation_observed_ms,
            "budget_ms": 20_000,
        },
        "finishing": {
            "artifact_digest": final_selection["artifact_digest"],
            "partition_plan_digest": final_selection["partition_plan_digest"],
            "source_minimal_artifact_digest": finalized["partition"]["finalization"]["source_minimal_artifact_digest"],
            "materializable": True,
            "cad_status": final_cad["status"],
            "observed_ms": finishing_observed_ms,
            "budget_ms": 3_000,
        },
        "placement_count": len(calculated["partition"]["placements"]),
        "reservation_count": calculated["partition"]["top_inset_reservations"]["summary"]["reservation_count"],
        "placements": deepcopy(calculated["partition"]["placements"]),
    }


def _public_28x30_control() -> dict[str, object]:
    receipt = json.loads(PUBLIC_28X30_RECEIPT.read_text(encoding="utf-8"))
    supplied_digest = receipt.pop("receipt_digest")
    if canonical_digest(receipt) != supplied_digest:
        raise RuntimeError("Le reçu public 28x30 n est plus intègre.")
    result = receipt["result"]
    if result["status"] != "solution_found" or result["placement_count"] != 28:
        raise RuntimeError("Le reçu public 28x30 n est plus certifié.")
    if receipt["holdout_read"] or not receipt["generated_from_public_data_only"]:
        raise RuntimeError("Le contrôle 28x30 ne respecte plus la frontière publique.")
    return {
        "receipt_digest": supplied_digest,
        "status": result["status"],
        "placement_count": result["placement_count"],
        "external_recertified": result["external_recertified"],
        "holdout_read": receipt["holdout_read"],
    }


def _preflight_digest(summary: dict[str, object]) -> str:
    digest_payload = deepcopy(summary)
    digest_payload.pop("preflight_digest", None)
    for fixture in digest_payload["fixtures"].values():
        fixture["flow"]["minimal"].pop("observed_ms", None)
        fixture["flow"]["finishing"].pop("observed_ms", None)
    return canonical_digest(digest_payload)


def build_preflight() -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    projects = {
        "preference": preference_project(),
        "tray_flow": tray_flow_project(),
    }
    flows = {
        case_id: _run_staged_flow(project, case_id)
        for case_id, project in projects.items()
    }
    preference = flows["preference"]
    placements = {
        item["container_group_id"]: item for item in preference["placements"]
    }
    small_top = max(
        placements["small-a"]["origin_mm"]["z"],
        placements["small-b"]["origin_mm"]["z"],
    )
    if placements["large"]["origin_mm"]["z"] <= small_top:
        raise RuntimeError("La fixture de préférence ne place plus le grand bac au-dessus.")
    tray = flows["tray_flow"]
    if tray["reservation_count"] < 1:
        raise RuntimeError("La fixture plateau ne transporte plus ses réservations.")

    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l09rv_fusion_preflight.v1",
        "addin_version": ADDIN_VERSION,
        "fixtures": {
            case_id: {
                "filename": FIXTURE_FILENAMES[case_id],
                "project_digest": canonical_digest(project),
                "flow": flows[case_id],
            }
            for case_id, project in projects.items()
        },
        "public_28x30": _public_28x30_control(),
        "separate_measurements": True,
        "expected_ui": {
            "buttons": ["Calculer", "Finaliser", "Matérialiser"],
            "calculation_budgets_seconds": [3, 10, 20, 60, 180],
            "finishing_budgets_seconds": [3, 10, 20, 60, 180],
            "activity_refresh_ms": 1_000,
            "activity_absent_at_rest": True,
        },
        "automated_controls": {
            "necessary_inversion_admissible": "tests.test_minimal_layout_solver::test_necessary_large_below_small_inversion_remains_admissible",
            "opening_diagnostic_only": "tests.test_solver_outcome::test_anonymised_h01_and_h02_use_envelope_support_with_material_diagnostic",
            "collision_negative": "tests.test_minimal_layout_solver::test_floating_body_is_rejected_by_the_common_support_contract",
            "reservation_negative": "tests.test_scip_product_solver",
            "timeout_not_impossible": "tests.test_minimal_layout_solver::test_global_deadline_without_incumbent_is_not_impossibility",
            "finishing_failure_preserves_minimal": "tests.test_staged_calculation::test_total_finishing_timeout_preserves_exact_minimal_artifact",
        },
        "holdout_opened": False,
        "benchmark_executed": False,
        "fusion_validated": False,
        "print_validated": False,
    }
    summary["preflight_digest"] = _preflight_digest(summary)
    return projects, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    projects, summary = build_preflight()
    if args.output_directory is not None:
        args.output_directory.mkdir(parents=True, exist_ok=True)
        for case_id, project in projects.items():
            (args.output_directory / FIXTURE_FILENAMES[case_id]).write_text(
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
        "P64_L09RV_PREFLIGHT_OK "
        f"digest={summary['preflight_digest']} "
        f"fixtures={len(projects)} "
        f"tray_reservations={summary['fixtures']['tray_flow']['flow']['reservation_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())