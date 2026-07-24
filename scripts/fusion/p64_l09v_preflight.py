#!/usr/bin/env python3
"""Prépare les cas publics de la gate Fusion combinée P64-L09V."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from board_game_insert_generator.free_3d_plan_adapter import prepare_free_3d_problem
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.minimal_layout_solver import solve_minimal_layout
from board_game_insert_generator.material_support import (
    BRIDGED_ON_MATERIAL,
    FALLS_THROUGH_OPENING,
    material_support_contract,
)
from board_game_insert_generator.project_v1 import blank_project_v1, normalize_project_draft
from board_game_insert_generator.scip_product_solver import (
    SCIP_PRODUCT_ARCHIVE_SHA256,
    SCIP_PRODUCT_ARTIFACT_DIGEST,
)


ADDIN_VERSION = "0.1.63"
FIXTURE_FILENAMES = {
    "anti_fall": "p64-l09v-01-anti-fall-negative.bgig.json",
    "stable_bridge": "p64-l09v-02-stable-bridge.bgig.json",
    "tray_finalization": "p64-l09v-03-tray-finalization.bgig.json",
}


def _stacking_project(
    name: str,
    *,
    content_xy_mm: float = 36.0,
    wall_thickness_mm: float | None = 10.0,
) -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = name
    project["box"] = {
        "inner_dimensions_mm": {"x": 70.0, "y": 70.0, "z": 55.0},
        "usable_height_mm": 55.0,
        "lid_clearance_mm": 0.0,
    }
    project["container_groups"] = [
        {
            "id": f"stack-{index}",
            "name": f"Conteneur public {index}",
            "wall_thickness_mm": wall_thickness_mm,
            "floor_thickness_mm": None,
        }
        for index in range(3)
    ]
    project["contents"] = [
        {
            "id": f"content-{index}",
            "name": f"Contenu public {index}",
            "shape_kind": "custom",
            "dimensions_mm": {"x": content_xy_mm, "y": content_xy_mm, "z": 14.0},
            "quantity": 1,
            "container_group_id": f"stack-{index}",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
        for index in range(3)
    ]
    normalize_project_draft(project)
    return project


def _anti_fall_project() -> dict[str, object]:
    project = _stacking_project(
        "P64-L09V 01 anti-chute négatif",
        content_xy_mm=58.0,
        wall_thickness_mm=None,
    )
    project["contents"][2]["name"] = "Petit contenu qui ne doit pas tenir sur un trou"
    project["contents"][2]["dimensions_mm"] = {"x": 22.0, "y": 22.0, "z": 14.0}
    normalize_project_draft(project)
    return project


def _tray_finalization_project() -> dict[str, object]:
    project = _stacking_project("P64-L09V 03 plateau et fermeture finale")
    project["flat_items"] = [
        {
            "id": "tray",
            "name": "Plateau public",
            "kind": "board",
            "dimensions_mm": {"x": 20.0, "y": 18.0, "z": 3.0},
            "quantity": 1,
            "stack_order": None,
            "origin_mm": {"x": 10.0, "y": 12.0},
            "rotation_deg_z": 0,
        }
    ]
    normalize_project_draft(project)
    return project


def _placement(
    identifier: str,
    origin: tuple[float, float, float],
    size: tuple[float, float, float],
    *,
    cavity: tuple[float, float, float, float] | None = None,
    has_lid: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {
        "id": identifier,
        "role": "container",
        "origin_mm": dict(zip(("x", "y", "z"), origin)),
        "world_size_mm": dict(zip(("x", "y", "z"), size)),
        "final_outer_dimensions_mm": dict(zip(("x", "y", "z"), size)),
        "minimum_envelope_origin_in_final_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation_deg_z": 0,
        "stage_id": "",
        "has_lid": has_lid,
        "cavity_layout": [],
    }
    if cavity is not None:
        x, y, width, depth = cavity
        result["cavity_layout"] = [
            {
                "local_origin_mm": {"x": x, "y": y, "z": 2.0},
                "inner_dimensions_mm": {
                    "x": width,
                    "y": depth,
                    "z": size[2] - 2.0,
                },
            }
        ]
    return result


def _support_proofs() -> dict[str, object]:
    anti_fall = material_support_contract(
        [
            _placement(
                "lower-open-with-uncertified-lid",
                (0.0, 0.0, 0.0),
                (100.0, 100.0, 20.0),
                cavity=(10.0, 10.0, 80.0, 80.0),
                has_lid=True,
            ),
            _placement("small-upper", (30.0, 30.0, 20.0), (40.0, 40.0, 10.0)),
        ],
        fallback_xy_clearance=0.0,
        fallback_z_clearance=0.0,
    )
    bridge = material_support_contract(
        [
            _placement(
                "lower-open",
                (0.0, 0.0, 0.0),
                (100.0, 100.0, 20.0),
                cavity=(30.0, 30.0, 40.0, 40.0),
            ),
            _placement("bridging-upper", (20.0, 40.0, 20.0), (60.0, 20.0, 10.0)),
        ],
        fallback_xy_clearance=0.0,
        fallback_z_clearance=0.0,
    )
    anti_fall_upper = next(
        item for item in anti_fall["supports"] if item["placement_id"] == "small-upper"
    )
    bridge_upper = next(
        item for item in bridge["supports"] if item["placement_id"] == "bridging-upper"
    )
    if anti_fall_upper["status"] != FALLS_THROUGH_OPENING:
        raise RuntimeError("P64-L09V anti-fall proof no longer rejects the small upper body.")
    if anti_fall["invariants"]["uncertified_lid_ignored"] is not True:
        raise RuntimeError("P64-L09V lid invariant is no longer explicit.")
    if bridge_upper["status"] != BRIDGED_ON_MATERIAL:
        raise RuntimeError("P64-L09V stable bridge proof is no longer accepted.")
    return {
        "anti_fall_status": anti_fall_upper["status"],
        "anti_fall_has_lid_ignored": anti_fall["invariants"]["uncertified_lid_ignored"],
        "bridge_status": bridge_upper["status"],
        "bridge_coverage_ratio": bridge_upper["coverage_ratio"],
        "bridge_stable_support_polygon": bridge_upper["stable_support_polygon"],
    }


def prepare_fixtures() -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    projects = {
        "anti_fall": _anti_fall_project(),
        "stable_bridge": _stacking_project("P64-L09V 02 pontage stable"),
        "tray_finalization": _tray_finalization_project(),
    }
    preparations = {
        key: prepare_free_3d_problem(project) for key, project in projects.items()
    }
    rejected = {
        key: value.rejection_codes
        for key, value in preparations.items()
        if value.status != "ready" or value.problem is None
    }
    if rejected:
        raise RuntimeError(f"P64-L09V fixture preparation rejected: {rejected}")
    stable_control = solve_minimal_layout(
        projects["stable_bridge"],
        effort_profile="quick",
        request_id="p64-l09v-stable-bridge-control",
        request_revision=0,
    )
    if len(stable_control.get("placements", [])) != 3:
        raise RuntimeError("P64-L09V stable bridge public fixture is not solved in quick control.")
    tray_problem = preparations["tray_finalization"].problem
    assert tray_problem is not None
    if len(tray_problem.top_inset_zones) != 1:
        raise RuntimeError("P64-L09V tray fixture must expose exactly one top inset zone.")

    summary: dict[str, object] = {
        "schema_version": "bgig.p64_l09v_fusion_preflight.v1",
        "addin_version": ADDIN_VERSION,
        "fixture_digests": {
            key: canonical_digest(value) for key, value in projects.items()
        },
        "cases": {
            "anti_fall": {
                "filename": FIXTURE_FILENAMES["anti_fall"],
                "expected_product_observation": "no_certified_fall_through_stack",
            },
            "stable_bridge": {
                "filename": FIXTURE_FILENAMES["stable_bridge"],
                "expected_product_observation": "certified_material_bridge",
                "quick_control_placement_count": len(stable_control["placements"]),
            },
            "tray_finalization": {
                "filename": FIXTURE_FILENAMES["tray_finalization"],
                "expected_product_observation": "scip_then_certified_finalized_plan",
                "top_inset_zone_count": len(tray_problem.top_inset_zones),
            },
        },
        "support_proofs": _support_proofs(),
        "expected_solver_settings": {"method": "auto", "effort": "deep"},
        "scip_runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "scip_runtime_archive_sha256": SCIP_PRODUCT_ARCHIVE_SHA256,
        "required_runtime_markers": {
            "material_support": "material_surface_v1",
            "scip_top_inset": "top_inset_support",
            "coupled_finalization": "bounded_growth_local_repair_balanced_proportional",
            "secondary_objectives": "bgig.finalization_secondary_objectives.v1",
        },
        "fusion_validated": False,
        "print_validated": False,
    }
    summary["preflight_digest"] = canonical_digest(summary)
    return projects, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    projects, summary = prepare_fixtures()
    if args.output_directory is not None:
        args.output_directory.mkdir(parents=True, exist_ok=True)
        for key, project in projects.items():
            path = args.output_directory / FIXTURE_FILENAMES[key]
            path.write_text(
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
        "P64_L09V_PREFLIGHT_OK "
        f"digest={summary['preflight_digest']} "
        f"fixtures={len(projects)} "
        f"top_inset={summary['cases']['tray_finalization']['top_inset_zone_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
