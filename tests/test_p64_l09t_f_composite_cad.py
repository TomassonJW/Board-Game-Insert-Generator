from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.coupled_finalization import (
    _frozen_cavity_contracts,
)
from board_game_insert_generator.free_3d_greedy_solver import (
    Free3DPlacement,
)
from board_game_insert_generator.partition_cad import build_partition_cad
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

    def test_hybrid_v2_is_the_published_exact_finalization(self) -> None:
        finalization = self.plan["finalization"]
        certificate = finalization[
            "composite_materialization_certificate"
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
        self.assertEqual(certificate["printable_residual_volume_mm3"], 0.0)
        self.assertTrue(certificate["owner_unions_connected"])
        self.assertTrue(certificate["minimum_reservation_wall_certified"])
        self.assertGreater(
            certificate["content_cavity_cut_volume_mm3"],
            0.0,
        )
        self.assertAlmostEqual(
            certificate["exact_cut_volume_mm3"],
            certificate["content_cavity_cut_volume_mm3"]
            + certificate["access_and_top_cut_volume_mm3"],
            places=6,
        )
        self.assertAlmostEqual(
            certificate["final_material_volume_mm3"],
            certificate["cad_union_before_cuts_volume_mm3"]
            - certificate["exact_cut_volume_mm3"],
            places=6,
        )

    def test_cavity_world_pose_is_exact_and_vertical_access_is_open(self) -> None:
        minimal = self.minimal_selection["partition"]["placements"][0]
        cavity = minimal["cavity_layout"][0]
        expected_origin = {
            axis: round(
                float(minimal["origin_mm"][axis])
                + float(cavity["local_origin_mm"][axis]),
                6,
            )
            for axis in ("x", "y", "z")
        }
        frozen = self.plan["finalization"]["frozen_cavities"][0]
        certificate = self.plan["finalization"][
            "composite_materialization_certificate"
        ]

        self.assertEqual(frozen["world_origin_mm"], expected_origin)
        self.assertEqual(
            frozen["world_size_mm"],
            cavity["inner_dimensions_mm"],
        )
        self.assertTrue(frozen["top_open"])
        self.assertTrue(
            certificate["cavity_world_poses_match_frozen_contract"]
        )
        self.assertTrue(certificate["cavity_vertical_access_open"])
        self.assertTrue(
            self.plan["invariants"]["cavity_world_poses_frozen"]
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
        self.assertTrue(access_cuts)
        content_cut = content_cuts[0]
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
        geometry_origin_z = (
            self.fusion.blanks[0].geometry_frame_origin_mm.z
        )
        for access_cut in access_cuts:
            self.assertAlmostEqual(
                access_cut.cut_origin_mm.z,
                geometry_origin_z
                + access_cut.requested_local_origin_mm.z
                + access_cut.cut_size_mm.z,
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
                value.policy == "hybrid_xy_composite_v2"
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
        body["prisms"][0]["cad_size_mm"]["x"] += 0.1
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
