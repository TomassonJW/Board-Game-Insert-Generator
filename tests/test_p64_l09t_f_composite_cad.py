from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.coupled_finalization import (
    _composite_positive_geometry_payload,
    _frozen_cavity_contracts,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
)
from board_game_insert_generator.partition_cad import (
    PartitionCadBuildError,
    build_partition_cad,
)
from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    ARTIFACT_KIND_MINIMAL,
    StagedCalculationSession,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    additive_prism_join_batches,
    cavity_cut_batches,
    generation_plan_from_cad_ir,
)
from scripts.fusion.p64_l09sv_preflight import (
    FINISHING_EFFORT,
    REQUESTED_SETTINGS,
    recent_tray_project,
)


class P64L09TFCompositeCadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project = recent_tray_project()
        engine = IncrementalLocalAnalysisEngine(
            cls.project,
            effort_profile="normal",
        )
        session = StagedCalculationSession(
            cls.project,
            solver_settings=REQUESTED_SETTINGS,
        )
        session.synchronize(
            cls.project,
            engine.snapshot(),
            solver_settings=REQUESTED_SETTINGS,
            container_frontiers=engine.certified_frontiers(),
            frontier_digests=engine.frontier_digests(),
        )
        calculated = session.calculate_layout(
            request_id="p64-l09t-f",
            request_revision=0,
        )
        if calculated["solver_result"]["status"] != "solution_found":
            raise RuntimeError("The F fixture has no minimal plan.")
        cls.minimal_selection = session.select_materializable_artifact(
            ARTIFACT_KIND_MINIMAL
        )
        finalized = session.finalize_volume(
            finishing_effort_profile=FINISHING_EFFORT
        )
        if finalized["solver_result"]["status"] != "solution_found":
            raise RuntimeError("The F fixture has no finalized plan.")
        cls.final_selection = session.select_materializable_artifact(
            ARTIFACT_KIND_FINALIZED
        )
        cls.plan = cls.final_selection["partition"]
        cls.cad = build_partition_cad(
            cls.project,
            partition=cls.plan,
            artifact_identity=cls.final_selection,
            effort_profile="normal",
        )
        cls.fusion = generation_plan_from_cad_ir(
            cls.cad["cad_ir"],
            FUSION_GENERATION_MODE_COMPACT_ONLY,
        )

    def test_finalized_container_v3_is_the_published_positive_geometry(
        self,
    ) -> None:
        finalization = self.plan["finalization"]
        certificate = finalization[
            "composite_materialization_certificate"
        ]
        geometry_certificate = finalization[
            "finalized_container_geometry_certificate"
        ]

        self.assertEqual(
            finalization["selected_plan_source"],
            "f_xy_composite_v2_union_cavities_insets",
        )
        self.assertEqual(
            finalization["xy_composite_closure"]["certificate"][
                "schema_version"
            ],
            "bgig.xy_composite_partition_certificate.v2",
        )
        self.assertTrue(
            self.plan["invariants"]["continuous_closure_applied"]
        )
        self.assertFalse(
            self.plan["invariants"][
                "global_rectangular_partition_by_construction"
            ]
        )
        self.assertTrue(certificate["certified"])
        self.assertEqual(
            certificate["schema_version"],
            "bgig.xy_composite_container_materialization_certificate.v3",
        )
        self.assertEqual(certificate["printable_residual_volume_mm3"], 0.0)
        self.assertTrue(certificate["owner_unions_connected"])
        self.assertTrue(certificate["minimum_reservation_wall_certified"])
        self.assertGreater(
            certificate["content_cavity_subtraction_volume_mm3"],
            0.0,
        )
        self.assertAlmostEqual(
            certificate["exact_subtraction_volume_mm3"],
            certificate["content_cavity_subtraction_volume_mm3"]
            + certificate["access_and_top_subtraction_volume_mm3"],
            places=6,
        )
        self.assertAlmostEqual(
            certificate["final_material_volume_mm3"],
            certificate[
                "finalized_container_union_before_subtractions_volume_mm3"
            ]
            - certificate["exact_subtraction_volume_mm3"],
            places=6,
        )
        self.assertTrue(geometry_certificate["certified"])
        self.assertEqual(
            geometry_certificate["schema_version"],
            "bgig.finalized_container_geometry.v1",
        )
        self.assertEqual(
            geometry_certificate["flat_positive_body_count"],
            0,
        )
        self.assertEqual(
            geometry_certificate["flat_positive_union_count"],
            0,
        )
        self.assertEqual(
            geometry_certificate["flat_positive_volume_mm3"],
            0.0,
        )
        self.assertTrue(
            geometry_certificate[
                "positive_geometry_frozen_before_flat_subtractions"
            ]
        )
        self.assertEqual(
            geometry_certificate,
            certificate[
                "finalized_container_geometry_certificate"
            ],
        )
        for placement in self.plan["placements"]:
            body = placement["composite_body"]
            self.assertEqual(
                body["schema_version"],
                "bgig.xy_composite_container_body.v3",
            )
            self.assertEqual(
                body["positive_geometry_source"],
                "container_finalization",
            )
            self.assertEqual(
                body["positive_geometry_digest"],
                canonical_digest(
                    _composite_positive_geometry_payload(body)
                ),
            )
            for prism in body["prisms"]:
                self.assertNotIn("cad_origin_mm", prism)
                self.assertNotIn("cad_size_mm", prism)
                self.assertEqual(
                    prism["geometry_role"],
                    "finalized_container",
                )
                self.assertEqual(
                    prism["positive_geometry_source"],
                    "container_finalization",
                )
                self.assertGreaterEqual(
                    prism["final_size_mm"]["z"],
                    prism["closure_size_mm"]["z"],
                )

    def test_cavity_depth_is_exact_and_final_z_anchor_is_certified(self) -> None:
        minimal = self.minimal_selection["partition"]["placements"][0]
        cavity = minimal["cavity_layout"][0]
        frozen = self.plan["placements"][0]["frozen_cavities_v1"][0]
        certificate = self.plan["finalization"][
            "composite_materialization_certificate"
        ]

        self.assertEqual(
            frozen["world_size_mm"],
            cavity["inner_dimensions_mm"],
        )
        self.assertEqual(
            frozen["calibrated_depth_source_mm"],
            cavity["inner_dimensions_mm"]["z"],
        )
        self.assertEqual(
            frozen["calibrated_depth_final_mm"],
            cavity["inner_dimensions_mm"]["z"],
        )
        self.assertTrue(frozen["anchor_certified"])
        self.assertTrue(
            certificate["cavity_calibrations_match_source_contract"]
        )
        self.assertTrue(
            certificate["cavity_anchor_certificate"]["certified"]
        )
        self.assertTrue(
            self.plan["invariants"][
                "cavity_xy_pose_orientation_and_dimensions_frozen"
            ]
        )
        self.assertTrue(
            self.plan["invariants"]["cavity_final_z_anchor_resolved"]
        )
        content_cuts = [
            value
            for value in self.fusion.cavity_cuts
            if value.cavity_source == "frozen_content_cavity"
        ]
        access_cuts = [
            value
            for value in self.fusion.cavity_cuts
            if value.cavity_source
            == "frozen_cavity_vertical_access"
        ]
        self.assertEqual(len(content_cuts), 1)
        self.assertFalse(access_cuts)
        content_cut = content_cuts[0]
        self.assertEqual(
            content_cut.anchor_kind,
            frozen["anchor_kind"],
        )
        self.assertEqual(
            content_cut.calibrated_depth_source_mm,
            content_cut.calibrated_depth_final_mm,
        )
        self.assertAlmostEqual(
            content_cut.cut_origin_mm.x,
            frozen["world_origin_mm"]["x"],
            places=6,
        )
        self.assertAlmostEqual(
            content_cut.cut_origin_mm.y,
            frozen["world_origin_mm"]["y"],
            places=6,
        )
        self.assertAlmostEqual(
            content_cut.cut_origin_mm.z,
            frozen["world_origin_mm"]["z"]
            + frozen["world_size_mm"]["z"],
            places=6,
        )

    def test_cad_ir_joins_before_cavities_and_exact_top_cuts(self) -> None:
        self.assertEqual(self.cad["status"], "ready_for_fusion")
        component = self.cad["cad_ir"]["components"][0]
        operations = component["body"]["operations"]
        kinds = [value["kind"] for value in operations]
        join_indexes = [
            index
            for index, kind in enumerate(kinds)
            if kind == "join_rectangular_prism"
        ]
        cavity_indexes = [
            index
            for index, kind in enumerate(kinds)
            if kind == "subtract_rectangular_cavity"
        ]
        top_indexes = [
            index
            for index, kind in enumerate(kinds)
            if kind
            in {
                "subtract_top_inset_reservation",
                "subtract_top_inset_grip",
            }
        ]

        self.assertTrue(join_indexes)
        self.assertTrue(cavity_indexes)
        self.assertTrue(top_indexes)
        self.assertLess(max(join_indexes), min(cavity_indexes))
        self.assertLess(max(cavity_indexes), min(top_indexes))
        self.assertEqual(self.fusion.module_component_count, 1)
        self.assertTrue(self.fusion.additive_prism_joins)
        self.assertTrue(
            all(
                value.policy
                in {
                    "hybrid_xy_composite_v2",
                    "finalized_container_union_v3",
                }
                and value.attachment_axis in {"x", "y"}
                for value in self.fusion.additive_prism_joins
            )
        )

    def test_fusion_materialization_batches_preserve_every_logical_operation(self) -> None:
        join_batches = additive_prism_join_batches(
            self.fusion.additive_prism_joins
        )
        cut_batches = cavity_cut_batches(self.fusion)

        self.assertEqual(
            sum(len(batch) for batch in join_batches),
            len(self.fusion.additive_prism_joins),
        )
        self.assertEqual(
            sum(len(batch) for batch in cut_batches),
            len(self.fusion.cavity_cuts),
        )
        self.assertLess(
            len(join_batches),
            len(self.fusion.additive_prism_joins),
        )
        self.assertLess(
            len(cut_batches),
            len(self.fusion.cavity_cuts),
        )
        self.assertEqual(
            self.fusion.to_dict()["fusion_materialization_batches"],
            {
                "additive_prism_join_batches": len(join_batches),
                "cavity_cut_batches": len(cut_batches),
                "logical_additive_prism_joins": len(
                    self.fusion.additive_prism_joins
                ),
                "logical_cavity_cuts": len(self.fusion.cavity_cuts),
            },
        )

    def test_cad_refuses_a_composite_geometry_digest_divergence(self) -> None:
        corrupted = deepcopy(self.plan)
        body = corrupted["placements"][0]["composite_body"]
        body["prisms"][0]["final_size_mm"]["x"] += 0.1
        corrupted.pop("plan_digest")
        corrupted["plan_digest"] = canonical_digest(corrupted)
        identity = deepcopy(self.final_selection)
        identity["partition_plan_digest"] = corrupted["plan_digest"]

        result = build_partition_cad(
            self.project,
            partition=corrupted,
            artifact_identity=identity,
            effort_profile="normal",
        )

        self.assertNotEqual(result["status"], "ready_for_fusion")
        self.assertTrue(
            any(
                "diverge de son certificat" in blocker
                for blocker in result["blockers"]
            )
        )

    def test_cad_refuses_a_frozen_cavity_pose_divergence(self) -> None:
        corrupted = deepcopy(self.plan)
        frozen = corrupted["placements"][0]["frozen_cavities_v1"][0]
        frozen["world_origin_mm"]["x"] += 0.1
        corrupted.pop("plan_digest")
        corrupted["plan_digest"] = canonical_digest(corrupted)
        identity = deepcopy(self.final_selection)
        identity["partition_plan_digest"] = corrupted["plan_digest"]

        result = build_partition_cad(
            self.project,
            partition=corrupted,
            artifact_identity=identity,
            effort_profile="normal",
        )

        self.assertNotEqual(result["status"], "ready_for_fusion")
        self.assertTrue(
            any(
                "empreinte de cavite figee diverge" in blocker
                for blocker in result["blockers"]
            )
        )

    def test_cad_refuses_flat_positive_volume_in_finalized_certificate(
        self,
    ) -> None:
        corrupted = deepcopy(self.plan)
        certificate = corrupted["finalization"][
            "finalized_container_geometry_certificate"
        ]
        certificate["flat_positive_volume_mm3"] = 1.0
        corrupted.pop("plan_digest")
        corrupted["plan_digest"] = canonical_digest(corrupted)
        identity = deepcopy(self.final_selection)
        identity["partition_plan_digest"] = corrupted["plan_digest"]

        with self.assertRaisesRegex(
            PartitionCadBuildError,
            "certificat de geometrie positive",
        ):
            build_partition_cad(
                self.project,
                partition=corrupted,
                artifact_identity=identity,
                effort_profile="normal",
            )

    def test_frozen_cavity_pose_follows_a_quarter_turn_exactly(self) -> None:
        placement = Free3DPlacement(
            participant_id="container:rotated",
            role="container",
            name="Rotated",
            origin_mm=(10.0, 20.0, 0.0),
            world_size_mm=(60.0, 40.0, 10.0),
            local_size_mm=(40.0, 60.0, 10.0),
            rotation_deg_z=90,
            supporting_ids=(),
            support_coverage_ratio=1.0,
        )
        minimal_plan = {
            "placements": [
                {
                    "id": placement.participant_id,
                    "final_outer_dimensions_mm": {
                        "x": 40.0,
                        "y": 60.0,
                        "z": 10.0,
                    },
                    "minimum_envelope_origin_in_final_mm": {
                        "x": 1.0,
                        "y": 2.0,
                        "z": 0.0,
                    },
                    "cavity_layout": [
                        {
                            "cavity_id": "rotated:cavity",
                            "local_origin_mm": {
                                "x": 3.0,
                                "y": 4.0,
                                "z": 0.0,
                            },
                            "inner_dimensions_mm": {
                                "x": 10.0,
                                "y": 20.0,
                                "z": 8.0,
                            },
                        }
                    ],
                }
            ]
        }

        frozen = _frozen_cavity_contracts(
            minimal_plan,
            (placement,),
            20.0,
        )[0]

        self.assertEqual(
            frozen["world_origin_mm"],
            {"x": 44.0, "y": 24.0, "z": 2.0},
        )
        self.assertEqual(
            frozen["world_size_mm"],
            {"x": 20.0, "y": 10.0, "z": 8.0},
        )
        self.assertEqual(
            frozen["access_zone"].origin_xy_mm,
            (44.0, 24.0),
        )


if __name__ == "__main__":
    unittest.main()
