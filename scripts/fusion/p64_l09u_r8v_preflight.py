"""Build the local-only preflight summary for the P64-L09U-R8 Fusion gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Mapping

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    StagedCalculationSession,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    generation_plan_from_cad_ir,
)
from scripts.fusion.p64_l09sv_preflight import (
    FINISHING_EFFORT,
    REQUESTED_SETTINGS,
    recent_tray_project,
)
from scripts.fusion.p64_l09u_r7v_preflight import (
    build_preflight as build_r7_preflight,
)


ADDIN_VERSION = "0.1.79"
PREFLIGHT_SCHEMA = "bgig.p64_l09u_r8v.preflight.v1"
AUTHORIZED_EXCLUDED_TEST_MODULES = (
    "test_anonymized_solver_case_corpus_builder",
    "test_external_solver_benchmark_corpus",
    "test_external_solver_tournament",
    "test_external_solver_tournament_evidence",
    "test_external_solver_tournament_runner",
    "test_external_solver_tournament_selection",
    "test_real_3d_solver_corpus",
    "test_real_3d_solver_tournament",
    "test_solver_benchmark_adapters",
    "test_solver_benchmark_campaign",
    "test_solver_benchmark_corpus",
    "test_solver_case_corpus",
)


def stable_digest(payload: object) -> str:
    stable_payload = _without_volatile_observations(payload)
    if isinstance(stable_payload, dict):
        inherited_r7 = stable_payload.get(
            "inherited_r7_preflight"
        )
        if isinstance(inherited_r7, dict):
            inherited_r6 = inherited_r7.get(
                "inherited_r6_preflight"
            )
            if isinstance(inherited_r6, dict):
                inherited_r7["inherited_r6_preflight"] = {
                    key: value
                    for key, value in inherited_r6.items()
                    if key not in {"end_to_end", "preflight_digest"}
                }
    canonical = json.dumps(
        stable_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _without_volatile_observations(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _without_volatile_observations(item)
            for key, item in value.items()
            if not str(key).endswith("observed_ms")
        }
    if isinstance(value, (list, tuple)):
        return [
            _without_volatile_observations(item)
            for item in value
        ]
    return value


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{label} must be an object.")
    return value


def _strict_pipeline_summary() -> dict[str, object]:
    project = recent_tray_project()
    engine = IncrementalLocalAnalysisEngine(
        project,
        effort_profile="normal",
    )
    session = StagedCalculationSession(
        project,
        solver_settings=REQUESTED_SETTINGS,
    )
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=REQUESTED_SETTINGS,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    calculated = session.calculate_layout(
        request_id="p64-l09u-r8v-preflight",
        request_revision=0,
    )
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError("The R8 preflight fixture has no minimal plan.")
    finalized = session.finalize_volume(
        finishing_effort_profile=FINISHING_EFFORT
    )
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError("The R8 preflight fixture has no finalized plan.")
    selection = session.select_materializable_artifact(
        ARTIFACT_KIND_FINALIZED
    )
    plan = _mapping(selection.get("partition"), "final partition")
    flat_plan = _mapping(
        plan.get("flat_inset_subtraction_plan"),
        "flat inset subtraction plan",
    )
    certificate = _mapping(
        flat_plan.get("certificate"),
        "subtractive flat inset certificate",
    )
    operations = tuple(
        _mapping(value, "flat inset operation")
        for value in flat_plan.get("operations", ())
    )
    if not operations:
        raise RuntimeError(
            "The R8 preflight fixture has no flat inset subtraction."
        )

    cad = build_partition_cad(
        project,
        partition=plan,
        artifact_identity=selection,
        effort_profile="normal",
    )
    if cad["status"] != "ready_for_fusion":
        raise RuntimeError("The R8 preflight CAD IR is not ready.")
    cad_ir = _mapping(cad.get("cad_ir"), "CAD IR")
    metadata = _mapping(cad_ir.get("metadata"), "CAD IR metadata")
    box_fill_plan = _mapping(
        metadata.get("box_fill_plan"),
        "CAD IR box fill plan",
    )
    cad_flat_plan = _mapping(
        box_fill_plan.get("flat_inset_subtraction_plan"),
        "CAD IR flat inset subtraction plan",
    )
    cad_certificate = _mapping(
        box_fill_plan.get("subtractive_flat_inset_certificate"),
        "CAD IR subtractive flat inset certificate",
    )
    fusion = generation_plan_from_cad_ir(
        cad_ir,
        FUSION_GENERATION_MODE_COMPACT_ONLY,
    )
    fusion_cuts = tuple(
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
                        "source interval",
                    )["bottom"]
                ),
                float(
                    _mapping(
                        operation.get("local_interval_z_mm"),
                        "source interval",
                    )["top"]
                ),
            )
            for operation in operations
        )
    )
    fusion_intervals = tuple(
        sorted(
            (
                value.cavity_id,
                float(value.local_interval_bottom_z_mm),
                float(value.local_interval_top_z_mm),
            )
            for value in fusion_cuts
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
            for value in fusion_cuts
        )
    )
    zero_positive_contract = all(
        certificate.get(field) == expected
        for field, expected in (
            ("flat_positive_volume_mm3", 0.0),
            ("flat_positive_body_count", 0),
            ("flat_positive_union_count", 0),
            ("flat_positive_operation_count", 0),
            (
                "new_printable_body_count_attributed_to_flat_items",
                0,
            ),
        )
    )
    all_difference_only = all(
        operation.get("boolean_operation") == "difference"
        and operation.get("creates_positive_geometry") is False
        and operation.get("creates_printable_body") is False
        and operation.get("creates_union") is False
        for operation in operations
    )
    interval_chain_exact = (
        source_intervals == fusion_intervals == brep_intervals
    )
    if (
        certificate.get("certified") is not True
        or certificate.get("positive_geometry_unchanged") is not True
        or not zero_positive_contract
        or not all_difference_only
        or cad_flat_plan != flat_plan
        or cad_certificate != certificate
        or fusion.subtractive_flat_inset_certificate != certificate
        or not interval_chain_exact
    ):
        raise RuntimeError(
            "The R8 preflight pipeline is not strictly subtractive end to end."
        )
    return {
        "schema_version": "bgig.r8_strict_pipeline_preflight.v1",
        "operation_count": len(operations),
        "operation_ids": [value[0] for value in source_intervals],
        "observed_combined_local_depths_mm": list(
            certificate.get("observed_combined_local_depths_mm", ())
        ),
        "flat_positive_volume_mm3": 0.0,
        "flat_positive_body_count": 0,
        "flat_positive_union_count": 0,
        "flat_positive_operation_count": 0,
        "new_printable_body_count_attributed_to_flat_items": 0,
        "positive_geometry_unchanged": True,
        "all_operations_difference_only": True,
        "cad_plan_identical": True,
        "fusion_certificate_identical": True,
        "fusion_and_brep_intervals_identical": True,
        "transient_brep_difference_only": True,
    }


def build_preflight() -> dict[str, object]:
    inherited = deepcopy(build_r7_preflight())
    inherited["addin_version"] = ADDIN_VERSION
    return {
        "schema_version": PREFLIGHT_SCHEMA,
        "addin_version": ADDIN_VERSION,
        "inherited_r7_preflight": inherited,
        "strict_subtractive_pipeline": _strict_pipeline_summary(),
        "authorized_suite": {
            "excluded_before_import": True,
            "excluded_module_count": len(
                AUTHORIZED_EXCLUDED_TEST_MODULES
            ),
            "excluded_modules": list(
                AUTHORIZED_EXCLUDED_TEST_MODULES
            ),
            "forbidden_solver_campaigns_executed": False,
        },
        "r8_contract": {
            "final_result_is_finalized_containers_minus_local_insets": True,
            "product_grid_step_mm": 0.1,
            "numeric_epsilon_is_not_product_resolution": True,
            "automatic_flat_stack_smallest_oriented_footprint_first": True,
            "source_project_written": False,
            "fusion_validated": False,
            "print_validated": False,
        },
        "gate_status": "prepared_not_human_observed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    payload = build_preflight()
    digest = stable_digest(payload)
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(
                {**payload, "preflight_digest": digest},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    strict = payload["strict_subtractive_pipeline"]
    print(
        "P64_L09U_R8V_PREFLIGHT "
        f"status=passed version={ADDIN_VERSION} digest={digest} "
        f"operations={strict['operation_count']} "
        "flat_positive_volume_mm3=0.0 flat_positive_bodies=0 "
        "flat_positive_unions=0 new_printable_bodies=0 "
        "fusion_validated=false print_validated=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
