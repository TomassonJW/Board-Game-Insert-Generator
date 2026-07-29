#!/usr/bin/env python3
"""Rejoue en lecture seule les cas personnels exigés par P64-L09U."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Mapping

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    StagedCalculationSession,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)


PROJECT_DIRECTORY = Path.home() / "Documents" / "BGIG" / "projects"
BASE_FILENAMES = {
    "case01_plus": "CasLimite01+.bgig.json",
    "case01_plus_plus": "CasLimite01++.bgig.json",
    "case02_plus": "CasLimite02+.bgig.json",
    "case02_plus_plus": "CasLimite02++.bgig.json",
}
EXPECTED_SOURCE_SHA256 = {
    "case02_plus": (
        "5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc"
    ),
    "case02_plus_plus": (
        "83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743"
    ),
}
EXPECTED_STRICT_LOCAL_DEPTHS_MM = {
    "case02_plus": [4.0, 6.0],
    "case02_plus_plus": [2.0, 4.0, 6.0],
}


def _file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_raw(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{label} must be an object.")
    return value


def _mappings(value: object, label: str) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, (list, tuple)):
        raise RuntimeError(f"{label} must be a list.")
    result = tuple(
        _mapping(item, f"{label}[]")
        for item in value
    )
    if len(result) != len(value):
        raise RuntimeError(f"{label} contains an invalid item.")
    return result


def _run_case(
    case_id: str,
    raw_project: dict[str, object],
    *,
    include_diagnostics: bool = False,
    calculation_effort: str = "normal",
) -> dict[str, object]:
    project = normalize_project_draft(raw_project).project
    settings = {"method": "auto", "effort": calculation_effort}
    engine = IncrementalLocalAnalysisEngine(
        project,
        effort_profile=calculation_effort,
    )
    session = StagedCalculationSession(project, solver_settings=settings)
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    started = perf_counter()
    calculated = session.calculate_layout(
        request_id=f"p64-l09t-local-{case_id}",
        request_revision=0,
        initial_incumbent=None,
    )
    calculation_ms = round((perf_counter() - started) * 1000.0, 3)
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError(
            f"{case_id}: calculation={calculated['solver_result']['status']}"
        )
    calculated_partition = _mapping(
        calculated["partition"],
        f"{case_id}: calculated partition",
    )
    calculated_provenance = _mapping(
        _mapping(
            calculated_partition["minimal_layout"],
            f"{case_id}: calculated minimal layout",
        )["search_provenance"],
        f"{case_id}: calculated search provenance",
    )
    calculated_selected = _mapping(
        calculated_provenance["selected"],
        f"{case_id}: calculated selected proposal",
    )
    started = perf_counter()
    finalized = session.finalize_volume(finishing_effort_profile="normal")
    finishing_ms = round((perf_counter() - started) * 1000.0, 3)
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError(
            f"{case_id}: finalization="
            f"{finalized['solver_result'].get('stop_diagnostics')}"
        )
    selected = session.select_materializable_artifact(
        ARTIFACT_KIND_FINALIZED
    )
    plan = selected["partition"]
    certificate = plan["finalization"][
        "composite_materialization_certificate"
    ]
    cavity_anchors = plan["finalization"][
        "cavity_anchor_certificate"
    ]
    cad = build_partition_cad(
        project,
        partition=plan,
        artifact_identity=selected,
        effort_profile=calculation_effort,
    )
    if cad["status"] != "ready_for_fusion":
        raise RuntimeError(
            f"{case_id}: CAD IR={cad['status']} "
            f"blockers={cad.get('blockers')}"
        )
    fusion = generation_plan_from_cad_ir(
        cad["cad_ir"],
        FUSION_GENERATION_MODE_COMPACT_ONLY,
    )
    flat_plan = _mapping(
        plan.get("flat_inset_subtraction_plan"),
        f"{case_id}: flat inset subtraction plan",
    )
    flat_certificate = _mapping(
        flat_plan.get("certificate"),
        f"{case_id}: subtractive certificate",
    )
    flat_operations = _mappings(
        flat_plan.get("operations"),
        f"{case_id}: flat inset operations",
    )
    cad_ir = _mapping(cad.get("cad_ir"), f"{case_id}: CAD IR")
    cad_metadata = _mapping(
        cad_ir.get("metadata"),
        f"{case_id}: CAD IR metadata",
    )
    cad_box_fill = _mapping(
        cad_metadata.get("box_fill_plan"),
        f"{case_id}: CAD IR box fill plan",
    )
    cad_flat_plan = _mapping(
        cad_box_fill.get("flat_inset_subtraction_plan"),
        f"{case_id}: CAD IR flat inset subtraction plan",
    )
    cad_flat_certificate = _mapping(
        cad_box_fill.get("subtractive_flat_inset_certificate"),
        f"{case_id}: CAD IR subtractive certificate",
    )
    fusion_flat_cuts = tuple(
        value
        for value in fusion.cavity_cuts
        if value.cavity_source
        in {"top_inset_reservation", "top_inset_grip"}
    )
    source_intervals = tuple(
        sorted(
            (
                str(operation["id"]),
                float(
                    _mapping(
                        operation.get("local_interval_z_mm"),
                        f"{case_id}: source interval",
                    )["bottom"]
                ),
                float(
                    _mapping(
                        operation.get("local_interval_z_mm"),
                        f"{case_id}: source interval",
                    )["top"]
                ),
            )
            for operation in flat_operations
        )
    )
    fusion_intervals = tuple(
        sorted(
            (
                value.cavity_id,
                float(value.local_interval_bottom_z_mm),
                float(value.local_interval_top_z_mm),
            )
            for value in fusion_flat_cuts
        )
    )
    brep_intervals = tuple(
        sorted(
            (
                value.cavity_id,
                float(
                    value.to_dict()["brep_tool_interval_z_mm"]["bottom"]
                ),
                float(
                    value.to_dict()["brep_tool_interval_z_mm"]["top"]
                ),
            )
            for value in fusion_flat_cuts
        )
    )
    strict_zero_fields = {
        "flat_positive_volume_mm3": 0.0,
        "flat_positive_body_count": 0,
        "flat_positive_union_count": 0,
        "flat_positive_operation_count": 0,
        "new_printable_body_count_attributed_to_flat_items": 0,
    }
    if (
        flat_certificate.get("certified") is not True
        or flat_certificate.get("positive_geometry_unchanged") is not True
        or any(
            flat_certificate.get(field) != expected
            for field, expected in strict_zero_fields.items()
        )
        or any(
            operation.get("boolean_operation") != "difference"
            or operation.get("creates_positive_geometry") is not False
            or operation.get("creates_printable_body") is not False
            or operation.get("creates_union") is not False
            for operation in flat_operations
        )
        or cad_flat_plan != flat_plan
        or cad_flat_certificate != flat_certificate
        or fusion.subtractive_flat_inset_certificate
        != flat_certificate
        or source_intervals != fusion_intervals
        or source_intervals != brep_intervals
    ):
        raise RuntimeError(
            f"{case_id}: strict subtractive flat inset contract diverges"
        )
    expected_depths = EXPECTED_STRICT_LOCAL_DEPTHS_MM.get(case_id)
    observed_depths = list(
        flat_certificate.get(
            "observed_combined_local_depths_mm",
            (),
        )
    )
    if expected_depths is not None and observed_depths != expected_depths:
        raise RuntimeError(
            f"{case_id}: expected strict local depths "
            f"{expected_depths}, got {observed_depths}"
        )
    if (
        certificate.get("certified") is not True
        or certificate.get("printable_residual_volume_mm3") != 0.0
        or cavity_anchors.get("certified") is not True
        or cavity_anchors.get("calibrated_depths_unchanged") is not True
    ):
        raise RuntimeError(f"{case_id}: final certificate is not exact")
    anchored_cavities = list(cavity_anchors.get("cavities", ()))
    tray_cavities = [
        item
        for item in anchored_cavities
        if item["anchor_kind"] == "below_top_inset"
    ]
    open_cavities = [
        item
        for item in anchored_cavities
        if item["anchor_kind"] == "open_top"
    ]
    for item in open_cavities:
        cavity_top = (
            float(item["world_origin_mm"]["z"])
            + float(item["world_size_mm"]["z"])
        )
        if (
            item["top_interface_kind"] != "open_functional_face"
            or item["functional_top_access_certified"] is not True
            or abs(
                cavity_top - float(item["functional_top_z_mm"])
            )
            > 0.0001
        ):
            raise RuntimeError(
                f"{case_id}: cavity {item['cavity_key']} is not open "
                "on its local functional top"
            )
    for item in tray_cavities:
        placement = next(
            value
            for value in plan["placements"]
            if value["id"] == item["owner_id"]
        )
        responsible_cut = next(
            (
                value
                for value in placement["top_inset_cuts"]
                if value["kind"] == "top_inset"
                and value["reservation_id"]
                == item["responsible_reservation_id"]
                and value["local_region_id"]
                == item["responsible_local_region_id"]
            ),
            None,
        )
        if responsible_cut is None:
            available = [
                (
                    value["reservation_id"],
                    value["local_region_id"],
                )
                for value in placement["top_inset_cuts"]
                if value["kind"] == "top_inset"
            ]
            raise RuntimeError(
                f"{case_id}: cavity {item['cavity_key']} has no matching "
                f"top inset cut for "
                f"{item['responsible_reservation_id']}/"
                f"{item['responsible_local_region_id']}; "
                f"available={available}"
            )
        cavity_top = (
            float(item["world_origin_mm"]["z"])
            + float(item["world_size_mm"]["z"])
        )
        if (
            abs(
                cavity_top
                - float(responsible_cut["world_origin_mm"]["z"])
            )
            > 0.0001
            or item["top_interface_kind"]
            != "direct_void_to_removable_top_inset"
            or item["intermediate_material_thickness_mm"] != 0.0
            or item["top_separation_mm"] != 0.0
            or item["top_void_continuity_certified"] is not True
        ):
            raise RuntimeError(
                f"{case_id}: cavity remains closed below a removable tray"
            )
    if (
        cavity_anchors.get("top_void_continuity_certified") is not True
        or cavity_anchors.get("direct_top_inset_void_count")
        != cavity_anchors.get("below_top_inset_count")
        or len(tray_cavities)
        != cavity_anchors.get("below_top_inset_count")
    ):
        raise RuntimeError(
            f"{case_id}: tray cavity continuity certificate diverges"
        )
    local_regions = [
        region
        for reservation in plan["top_inset_reservations"]["reservations"]
        for region in reservation.get("local_depth_regions", ())
    ]
    result = {
        "case_id": case_id,
        "calculation_effort": calculation_effort,
        "calculation_status": "solution_found",
        "placement_digest": str(
            calculated_selected["placement_digest"]
        ),
        "finalization_status": "solution_found",
        "cad_status": cad["status"],
        "witness_status": "disabled",
        "cavities_frozen": True,
        "calibrated_cavity_depths_unchanged": True,
        "top_void_continuity_certified": True,
        "covered_cavity_count": len(tray_cavities),
        "open_functional_cavity_count": len(open_cavities),
        "cavity_anchor_count": len(anchored_cavities),
        "cavity_anchors": [
            {
                "cavity_id": item["cavity_key"],
                "anchor_kind": item["anchor_kind"],
                "source_depth_mm": item["calibrated_depth_source_mm"],
                "final_depth_mm": item["calibrated_depth_final_mm"],
                "minimum_origin_z_mm": item[
                    "minimum_world_origin_mm"
                ]["z"],
                "final_origin_z_mm": item["world_origin_mm"]["z"],
                "top_interface_kind": item["top_interface_kind"],
                "intermediate_material_thickness_mm": item[
                    "intermediate_material_thickness_mm"
                ],
                "top_void_continuity_certified": item[
                    "top_void_continuity_certified"
                ],
            }
            for item in anchored_cavities
        ],
        "top_inset_local_region_count": len(local_regions),
        "top_inset_local_depths_mm": sorted(
            {
                float(item["inset_depth_from_top_mm"])
                for item in local_regions
            }
        ),
        "printable_residual_volume_mm3": 0.0,
        "component_count": fusion.module_component_count,
        "join_count": len(fusion.additive_prism_joins),
        "join_feature_batch_count": fusion.additive_prism_join_batch_count,
        "cut_count": len(fusion.cavity_cuts),
        "cut_feature_batch_count": fusion.cavity_cut_batch_count,
        "strict_flat_inset_operation_count": len(flat_operations),
        "strict_flat_inset_intervals_identical": True,
        "strict_flat_inset_certificate": {
            **strict_zero_fields,
            "certified": True,
            "positive_geometry_unchanged": True,
            "observed_combined_local_depths_mm": observed_depths,
        },
        "calculation_observed_ms": calculation_ms,
        "finishing_observed_ms": finishing_ms,
    }
    if include_diagnostics:
        result["diagnostics"] = {
            "flat_items": project["flat_items"],
            "minimal_plan": plan,
            "cad_ir": cad["cad_ir"],
            "fusion_plan": fusion.to_dict(),
        }
    return result


def run_local_replay(
    case_ids: tuple[str, ...] | None = None,
    *,
    include_diagnostics: bool = False,
    calculation_effort: str = "normal",
) -> dict[str, object]:
    selected_ids = case_ids or tuple(BASE_FILENAMES)
    paths = {
        case_id: PROJECT_DIRECTORY / filename
        for case_id, filename in BASE_FILENAMES.items()
        if case_id in selected_ids
    }
    missing = [
        case_id for case_id, path in paths.items() if not path.is_file()
    ]
    if missing:
        return {
            "schema_version": "bgig.p64_l09u_r4_local_replay.v2",
            "status": "skipped_local_projects_missing",
            "missing_case_ids": missing,
            "read_only": True,
        }
    before = {case_id: _file_digest(path) for case_id, path in paths.items()}
    for case_id, digest in before.items():
        expected = EXPECTED_SOURCE_SHA256.get(case_id)
        if expected is not None and digest.lower() != expected:
            raise RuntimeError(
                f"{case_id}: unexpected personal source SHA-256 before replay"
            )
    raw = {case_id: _load_raw(path) for case_id, path in paths.items()}
    cases = dict(raw)
    results = [
        _run_case(
            case_id,
            project,
            include_diagnostics=include_diagnostics,
            calculation_effort=calculation_effort,
        )
        for case_id, project in cases.items()
    ]
    after = {case_id: _file_digest(path) for case_id, path in paths.items()}
    if before != after:
        raise RuntimeError("A local source project changed during replay.")
    for case_id, digest in after.items():
        expected = EXPECTED_SOURCE_SHA256.get(case_id)
        if expected is not None and digest.lower() != expected:
            raise RuntimeError(
                f"{case_id}: unexpected personal source SHA-256 after replay"
            )
    return {
        "schema_version": "bgig.p64_l09u_r4_local_replay.v2",
        "status": "passed",
        "read_only": True,
        "source_projects_unchanged": True,
        "source_sha256_before": before,
        "source_sha256_after": after,
        "case_count": len(results),
        "calculation_effort": calculation_effort,
        "results": results,
        "repository_payload_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-summary", type=Path)
    parser.add_argument(
        "--case-id",
        action="append",
        choices=tuple(BASE_FILENAMES),
    )
    parser.add_argument("--include-diagnostics", action="store_true")
    parser.add_argument(
        "--calculation-effort",
        choices=("quick", "short", "normal", "long", "deep"),
        default="normal",
    )
    args = parser.parse_args()
    receipt = run_local_replay(
        tuple(args.case_id) if args.case_id else None,
        include_diagnostics=args.include_diagnostics,
        calculation_effort=args.calculation_effort,
    )
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        "P64_L09T_LOCAL_REPLAY "
        f"status={receipt['status']} "
        f"cases={receipt.get('case_count', 0)} "
        f"read_only={str(receipt['read_only']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
