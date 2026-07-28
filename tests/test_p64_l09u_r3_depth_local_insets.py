from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
import unittest

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.coupled_finalization import (
    _build_frozen_cavity_access_cuts,
    _conservative_closure_guard_zones,
    _resolve_final_cavity_contracts,
    _split_composite_owner_prisms,
)
from board_game_insert_generator.partition_cad import build_partition_cad
from board_game_insert_generator.partition_result_view import (
    build_partition_result_view,
)
from board_game_insert_generator.product_grid import is_on_product_grid
from board_game_insert_generator.staged_calculation import (
    ARTIFACT_KIND_FINALIZED,
    StagedCalculationSession,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    FusionSkeletonError,
    generation_plan_from_cad_ir,
)
from scripts.fusion.p64_l09sv_preflight import (
    FINISHING_EFFORT,
    REQUESTED_SETTINGS,
    recent_tray_project,
)


def _calibrated_project(*, with_reservation: bool) -> dict[str, object]:
    project = recent_tray_project()
    project["project_name"] = (
        "P64-L09U-R3 calibrated cavity with reservation"
        if with_reservation
        else "P64-L09U-R3 calibrated cavity without reservation"
    )
    project["contents"][0]["dimensions_mm"]["z"] = 10.0
    if not with_reservation:
        project["flat_items"] = []
    return project


def _stepped_reservation_project() -> dict[str, object]:
    project = _calibrated_project(with_reservation=True)
    project["project_name"] = "P64-L09U-R3 local stepped reservations"
    project["box"] = {
        "inner_dimensions_mm": {"x": 150.0, "y": 110.0, "z": 60.0},
        "usable_height_mm": 59.6,
        "lid_clearance_mm": 0.4,
    }
    project["flat_items"] = [
        {
            "id": "lower-board",
            "name": "Grand plateau",
            "kind": "board",
            "dimensions_mm": {"x": 130.0, "y": 90.0, "z": 2.0},
            "quantity": 1,
            "stack_order": 0,
        },
        {
            "id": "upper-booklet",
            "name": "Petit livret",
            "kind": "rulebook",
            "dimensions_mm": {"x": 80.0, "y": 60.0, "z": 3.0},
            "quantity": 1,
            "stack_order": 1,
        },
    ]
    return project


def _finalized_artifacts(
    project: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], object]:
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
        request_id="p64-l09u-r3-calibrated",
        request_revision=0,
    )
    if calculated["solver_result"]["status"] != "solution_found":
        raise RuntimeError("The R3 calibrated fixture has no minimal plan.")
    finalized = session.finalize_volume(
        finishing_effort_profile=FINISHING_EFFORT
    )
    if finalized["solver_result"]["status"] != "solution_found":
        raise RuntimeError("The R3 calibrated fixture has no final plan.")
    selection = session.select_materializable_artifact(
        ARTIFACT_KIND_FINALIZED
    )
    plan = selection["partition"]
    cad = build_partition_cad(
        project,
        partition=plan,
        artifact_identity=selection,
        effort_profile="normal",
    )
    fusion = generation_plan_from_cad_ir(
        cad["cad_ir"],
        FUSION_GENERATION_MODE_COMPACT_ONLY,
    )
    return plan, cad, fusion


class P64L09UR3DepthLocalInsetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.open_project = _calibrated_project(with_reservation=False)
        cls.open_plan, cls.open_cad, cls.open_fusion = _finalized_artifacts(
            cls.open_project
        )
        cls.inset_project = _calibrated_project(with_reservation=True)
        cls.inset_plan, cls.inset_cad, cls.inset_fusion = (
            _finalized_artifacts(cls.inset_project)
        )
        cls.partial_inset_project = _calibrated_project(
            with_reservation=True
        )
        cls.partial_inset_project["flat_items"][0]["dimensions_mm"][
            "x"
        ] = 15.0
        (
            cls.partial_inset_plan,
            cls.partial_inset_cad,
            cls.partial_inset_fusion,
        ) = _finalized_artifacts(cls.partial_inset_project)
        cls.stepped_project = _stepped_reservation_project()
        cls.stepped_plan, cls.stepped_cad, cls.stepped_fusion = (
            _finalized_artifacts(cls.stepped_project)
        )

    def test_ten_plus_clearance_remains_ten_point_six_end_to_end(self) -> None:
        for label, plan, cad, fusion in (
            (
                "open",
                self.open_plan,
                self.open_cad,
                self.open_fusion,
            ),
            (
                "inset",
                self.inset_plan,
                self.inset_cad,
                self.inset_fusion,
            ),
        ):
            with self.subTest(label=label):
                cavity = plan["placements"][0]["frozen_cavities_v1"][0]
                self.assertEqual(
                    cavity["calibrated_depth_source_mm"],
                    10.6,
                )
                self.assertEqual(
                    cavity["calibrated_depth_final_mm"],
                    10.6,
                )
                cad_cavity = cad["cad_ir"]["components"][0]["body"][
                    "cavities"
                ][0]
                self.assertEqual(cad_cavity["size_mm"]["z"], 10.6)
                fusion_cavity = next(
                    value
                    for value in fusion.cavity_cuts
                    if value.cavity_source == "frozen_content_cavity"
                )
                self.assertEqual(fusion_cavity.cut_size_mm.z, 10.6)
                self.assertEqual(
                    fusion_cavity.calibrated_depth_source_mm,
                    10.6,
                )
                self.assertEqual(
                    fusion_cavity.calibrated_depth_final_mm,
                    10.6,
                )

    def test_open_top_moves_only_z_and_keeps_surplus_as_floor(self) -> None:
        placement = self.open_plan["placements"][0]
        cavity = placement["frozen_cavities_v1"][0]

        self.assertEqual(cavity["anchor_kind"], "open_top")
        self.assertTrue(cavity["top_open"])
        self.assertEqual(cavity["responsible_reservation_id"], "")
        self.assertEqual(
            cavity["top_interface_kind"],
            "open_functional_face",
        )
        self.assertTrue(cavity["functional_top_access_certified"])
        self.assertEqual(
            cavity["world_origin_mm"]["z"]
            + cavity["world_size_mm"]["z"],
            cavity["functional_top_z_mm"],
        )
        self.assertGreaterEqual(
            cavity["retained_floor_mm"],
            cavity["minimum_floor_mm"],
        )
        self.assertEqual(
            cavity["world_origin_mm"]["x"],
            cavity["minimum_world_origin_mm"]["x"],
        )
        self.assertEqual(
            cavity["world_origin_mm"]["y"],
            cavity["minimum_world_origin_mm"]["y"],
        )

    def test_local_inset_joins_cavity_without_intermediate_wall(self) -> None:
        placement = self.inset_plan["placements"][0]
        cavity = placement["frozen_cavities_v1"][0]
        responsible_cut = next(
            value
            for value in placement["top_inset_cuts"]
            if value["kind"] == "top_inset"
            and value["reservation_id"]
            == cavity["responsible_reservation_id"]
            and value["local_region_id"]
            == cavity["responsible_local_region_id"]
        )
        cavity_top = (
            cavity["world_origin_mm"]["z"]
            + cavity["world_size_mm"]["z"]
        )

        self.assertEqual(cavity["anchor_kind"], "below_top_inset")
        self.assertFalse(cavity["top_open"])
        self.assertTrue(cavity["responsible_reservation_id"])
        self.assertTrue(cavity["responsible_local_region_id"])
        self.assertEqual(cavity_top, responsible_cut["world_origin_mm"]["z"])
        self.assertEqual(cavity["top_separation_mm"], 0.0)
        self.assertEqual(cavity["minimum_top_separation_mm"], 0.0)
        self.assertEqual(
            cavity["intermediate_material_thickness_mm"],
            0.0,
        )
        self.assertEqual(
            cavity["top_interface_kind"],
            "direct_void_to_removable_top_inset",
        )
        self.assertTrue(cavity["top_void_continuity_certified"])
        self.assertGreaterEqual(
            cavity["retained_floor_mm"],
            cavity["minimum_floor_mm"],
        )
        self.assertEqual(
            cavity["world_origin_mm"]["x"],
            cavity["minimum_world_origin_mm"]["x"],
        )
        self.assertEqual(
            cavity["world_origin_mm"]["y"],
            cavity["minimum_world_origin_mm"]["y"],
        )

    def test_result_view_cad_ir_and_fusion_share_the_same_anchor(self) -> None:
        view = build_partition_result_view(self.inset_plan)
        cavity = self.inset_plan["placements"][0][
            "frozen_cavities_v1"
        ][0]
        preview = view["top_view"]["cavities"][0]
        cad_operation = next(
            value
            for value in self.inset_cad["cad_ir"]["components"][0][
                "body"
            ]["operations"]
            if value["kind"] == "subtract_rectangular_cavity"
        )
        fusion_cut = next(
            value
            for value in self.inset_fusion.cavity_cuts
            if value.cavity_source == "frozen_content_cavity"
        )

        self.assertEqual(preview["anchor_kind"], "below_top_inset")
        self.assertEqual(
            preview["calibrated_depth_final_mm"],
            cavity["calibrated_depth_final_mm"],
        )
        self.assertEqual(
            cad_operation["parameters"]["anchor_kind"],
            "below_top_inset",
        )
        self.assertEqual(
            cad_operation["parameters"]["calibrated_depth_final_mm"],
            cavity["calibrated_depth_final_mm"],
        )
        self.assertEqual(fusion_cut.anchor_kind, "below_top_inset")
        self.assertEqual(
            fusion_cut.top_separation_mm,
            cavity["top_separation_mm"],
        )
        self.assertEqual(
            preview["top_interface_kind"],
            "direct_void_to_removable_top_inset",
        )
        self.assertTrue(preview["top_void_continuity_certified"])
        self.assertEqual(
            cad_operation["parameters"][
                "intermediate_material_thickness_mm"
            ],
            0.0,
        )
        self.assertEqual(
            cad_operation["parameters"]["top_interface_kind"],
            "direct_void_to_removable_top_inset",
        )
        self.assertTrue(
            cad_operation["parameters"][
                "top_void_continuity_certified"
            ]
        )
        self.assertEqual(
            fusion_cut.intermediate_material_thickness_mm,
            0.0,
        )
        self.assertEqual(
            fusion_cut.top_interface_kind,
            "direct_void_to_removable_top_inset",
        )
        self.assertTrue(fusion_cut.top_void_continuity_certified)

    def test_local_steps_reach_preview_cad_ir_and_fusion(self) -> None:
        reservations = self.stepped_plan["top_inset_reservations"][
            "reservations"
        ]
        lower = next(
            value
            for value in reservations
            if value["flat_item_id"] == "lower-board"
        )
        large_top_depths = {
            region["inset_depth_from_top_mm"]
            for region in lower["local_depth_regions"]
        }
        booklet = next(
            value
            for value in reservations
            if value["flat_item_id"] == "upper-booklet"
        )
        small_bottom_depths = {
            region["inset_depth_from_top_mm"]
            for region in booklet["local_depth_regions"]
        }
        view = build_partition_result_view(self.stepped_plan)
        cad_top_cuts = [
            operation
            for component in self.stepped_cad["cad_ir"]["components"]
            for operation in component["body"]["operations"]
            if operation["kind"] == "subtract_top_inset_reservation"
        ]
        fusion_top_cuts = [
            value
            for value in self.stepped_fusion.cavity_cuts
            if value.cavity_source == "top_inset_reservation"
        ]

        self.assertEqual(large_top_depths, {2.0})
        self.assertEqual(small_bottom_depths, {5.0})
        self.assertTrue(
            all(
                value["local_depth_regions"]
                for value in view["top_view"]["top_inset_reservations"]
            )
        )
        self.assertTrue(
            all(
                operation["parameters"]["local_region_id"]
                for operation in cad_top_cuts
            )
        )
        self.assertEqual(
            {
                operation["parameters"]["local_region_id"]
                for operation in cad_top_cuts
            },
            {
                value.local_region_id
                for value in fusion_top_cuts
            },
        )
        self.assertTrue(
            any(
                len(value.overlapping_reservation_ids) == 2
                for value in fusion_top_cuts
            )
        )
        overlap_cuts = [
            value
            for value in fusion_top_cuts
            if len(value.overlapping_reservation_ids) == 2
        ]
        self.assertEqual(
            {
                (
                    value.flat_item_id,
                    value.local_interval_bottom_z_mm,
                    value.local_interval_top_z_mm,
                )
                for value in overlap_cuts
            },
            {
                ("upper-booklet", 54.6, 57.6),
                ("lower-board", 57.6, 59.6),
            },
        )

    def test_closure_guard_uses_exact_local_regions_not_global_stack(
        self,
    ) -> None:
        reservations = self.stepped_plan["top_inset_reservations"]
        zones = _conservative_closure_guard_zones(
            reservations,
            float(reservations["design_top_z_mm"]),
        )

        depths_by_rect = {
            (
                zone.origin_xy_mm,
                zone.size_xy_mm,
            ): zone.inset_depth_mm
            for zone in zones
        }
        self.assertIn(2.0, depths_by_rect.values())
        self.assertIn(5.0, depths_by_rect.values())
        self.assertEqual(
            max(depths_by_rect.values()),
            5.0,
        )

    def test_low_body_is_not_split_by_unreachable_top_cut(self) -> None:
        owner = SimpleNamespace(
            prisms=(
                SimpleNamespace(
                    origin_mm=(0.4, 0.4, 0.0),
                    size_mm=(40.0, 30.0, 10.0),
                ),
            )
        )
        reservation = {
            "id": "top-inset:board",
            "flat_item_id": "board",
            "cut_origin_mm": {"x": 1.6, "y": 1.6},
            "cut_size_mm": {"x": 20.0, "y": 15.0},
            "support_plane_z_mm": 18.0,
            "inset_depth_from_top_mm": 2.0,
            "total_thickness_mm": 2.0,
            "grip_zone": {
                "origin_mm": {"x": 21.6, "y": 6.0},
                "size_mm": {"x": 8.0, "y": 4.0},
            },
            "local_depth_regions": [
                {
                    "id": "top-inset:board:local-region:0000",
                    "cut_origin_mm": {"x": 1.6, "y": 1.6},
                    "cut_size_mm": {"x": 20.0, "y": 15.0},
                    "layer_bottom_z_mm": 18.0,
                    "layer_top_z_mm": 20.0,
                }
            ],
        }

        cells = _split_composite_owner_prisms(
            owner,
            [reservation],
            [],
        )

        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0]["final_size_mm"], (40.0, 30.0, 10.0))

    def test_final_material_certificate_reaches_fusion_plan(self) -> None:
        certificate = self.stepped_plan["finalization"][
            "composite_materialization_certificate"
        ]["final_material_envelope_certificate"]

        self.assertTrue(certificate["certified"])
        self.assertEqual(certificate["failure_count"], 0)
        composite_certificate = self.stepped_plan["finalization"][
            "composite_materialization_certificate"
        ]
        self.assertTrue(
            composite_certificate[
                "no_additive_volume_above_final_bodies"
            ]
        )
        self.assertEqual(
            composite_certificate[
                "additive_above_final_residual_volume_mm3"
            ],
            0.0,
        )
        self.assertEqual(
            self.stepped_fusion.final_material_envelope_certificate,
            certificate,
        )
        self.assertTrue(
            all(
                is_on_product_grid(number)
                for cut in self.stepped_fusion.cavity_cuts
                for number in (
                    cut.cut_origin_mm.x,
                    cut.cut_origin_mm.y,
                    cut.cut_origin_mm.z,
                    cut.cut_size_mm.x,
                    cut.cut_size_mm.y,
                    cut.cut_size_mm.z,
                )
            )
        )

    def test_micro_overlap_smaller_than_a_wall_anchors_the_full_cavity(
        self,
    ) -> None:
        project = _calibrated_project(with_reservation=True)
        group_id = project["container_groups"][0]["id"]
        placement = {
            "id": "micro-owner",
            "container_group_id": group_id,
            "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
            "world_size_mm": {"x": 20.0, "y": 20.0, "z": 20.0},
        }
        source_cavity = {
            "owner_id": "micro-owner",
            "cavity_index": 0,
            "cavity_key": "micro-cavity",
            "world_origin_mm": {"x": 2.0, "y": 2.0, "z": 8.0},
            "world_size_mm": {"x": 8.0, "y": 8.0, "z": 10.0},
            "source_owner_origin_mm": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
            },
            "source_owner_world_size_mm": {
                "x": 20.0,
                "y": 20.0,
                "z": 20.0,
            },
            "source_rotation_deg_z": 0,
        }
        top_inset_cuts = [
            {
                "kind": "top_inset",
                "reservation_id": "micro-board",
                "local_region_id": "micro-region",
                "world_origin_mm": {
                    "x": 9.5,
                    "y": 2.0,
                    "z": 14.0,
                },
                "size_mm": {
                    "x": 4.0,
                    "y": 8.0,
                    "z": 4.0,
                },
            }
        ]

        certificate = _resolve_final_cavity_contracts(
            placement,
            [source_cavity],
            top_inset_cuts,
            project=project,
            cad_prisms=None,
        )
        cavity = certificate["cavities"][0]

        self.assertTrue(certificate["certified"])
        self.assertEqual(cavity["anchor_kind"], "below_top_inset")
        self.assertEqual(cavity["calibrated_depth_final_mm"], 10.0)
        self.assertEqual(cavity["world_origin_mm"]["z"], 4.0)
        self.assertEqual(
            cavity["world_origin_mm"]["z"]
            + cavity["world_size_mm"]["z"],
            14.0,
        )
        self.assertEqual(
            cavity["responsible_local_region_id"],
            "micro-region",
        )

    def test_every_tray_anchored_cavity_has_a_direct_void_path(self) -> None:
        for label, plan in (
            ("single", self.inset_plan),
            ("stepped", self.stepped_plan),
        ):
            with self.subTest(label=label):
                anchored = [
                    cavity
                    for placement in plan["placements"]
                    for cavity in placement.get("frozen_cavities_v1", [])
                    if cavity["anchor_kind"] == "below_top_inset"
                ]
                self.assertTrue(anchored)
                for cavity in anchored:
                    placement = next(
                        value
                        for value in plan["placements"]
                        if value["id"] == cavity["owner_id"]
                    )
                    responsible_cut = next(
                        value
                        for value in placement["top_inset_cuts"]
                        if value["kind"] == "top_inset"
                        and value["reservation_id"]
                        == cavity["responsible_reservation_id"]
                        and value["local_region_id"]
                        == cavity["responsible_local_region_id"]
                    )
                    self.assertEqual(
                        cavity["world_origin_mm"]["z"]
                        + cavity["world_size_mm"]["z"],
                        responsible_cut["world_origin_mm"]["z"],
                    )
                    self.assertEqual(
                        cavity["intermediate_material_thickness_mm"],
                        0.0,
                    )
                    self.assertTrue(
                        cavity["top_void_continuity_certified"]
                    )

    def test_every_other_cavity_opens_on_its_local_functional_top(self) -> None:
        open_cavities = [
            cavity
            for plan in (
                self.open_plan,
                self.inset_plan,
                self.stepped_plan,
            )
            for placement in plan["placements"]
            for cavity in placement.get("frozen_cavities_v1", [])
            if cavity["anchor_kind"] == "open_top"
        ]
        self.assertTrue(open_cavities)
        for cavity in open_cavities:
            self.assertEqual(
                cavity["top_interface_kind"],
                "open_functional_face",
            )
            self.assertTrue(
                cavity["functional_top_access_certified"]
            )
            self.assertEqual(
                cavity["world_origin_mm"]["z"]
                + cavity["world_size_mm"]["z"],
                cavity["functional_top_z_mm"],
            )

    def test_fusion_refuses_reintroduced_material_under_the_tray(self) -> None:
        cad_ir = deepcopy(self.inset_cad["cad_ir"])
        cad_ir["metadata"].pop("artifact_identity", None)
        cavity_operation = next(
            operation
            for operation in cad_ir["components"][0]["body"][
                "operations"
            ]
            if operation["kind"] == "subtract_rectangular_cavity"
            and operation["parameters"]["anchor_kind"]
            == "below_top_inset"
        )
        cavity_operation["parameters"][
            "intermediate_material_thickness_mm"
        ] = 1.2

        with self.assertRaisesRegex(
            FusionSkeletonError,
            "without intermediate material",
        ):
            generation_plan_from_cad_ir(
                cad_ir,
                FUSION_GENERATION_MODE_COMPACT_ONLY,
            )

    def test_global_tray_footprint_without_owner_cut_keeps_local_top_open(
        self,
    ) -> None:
        project = _calibrated_project(with_reservation=True)
        group_id = project["container_groups"][0]["id"]
        placement = {
            "id": "lower-owner",
            "container_group_id": group_id,
            "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
            "world_size_mm": {"x": 30.0, "y": 20.0, "z": 20.0},
        }
        source_cavity = {
            "owner_id": "lower-owner",
            "cavity_index": 0,
            "cavity_key": "lower-cavity",
            "world_origin_mm": {"x": 2.0, "y": 2.0, "z": 5.0},
            "world_size_mm": {"x": 10.0, "y": 10.0, "z": 5.0},
            "source_owner_origin_mm": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
            },
            "source_owner_world_size_mm": {
                "x": 20.0,
                "y": 20.0,
                "z": 10.0,
            },
            "source_rotation_deg_z": 0,
        }
        cad_prisms = [
            {
                "cad_origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                "cad_size_mm": {"x": 20.0, "y": 20.0, "z": 10.0},
            },
            {
                "cad_origin_mm": {"x": 20.0, "y": 0.0, "z": 0.0},
                "cad_size_mm": {"x": 10.0, "y": 20.0, "z": 20.0},
            },
        ]

        certificate = _resolve_final_cavity_contracts(
            placement,
            [source_cavity],
            [],
            project=project,
            cad_prisms=cad_prisms,
        )
        cavity = certificate["cavities"][0]

        self.assertTrue(certificate["certified"])
        self.assertEqual(cavity["anchor_kind"], "open_top")
        self.assertEqual(cavity["functional_top_z_mm"], 10.0)
        self.assertEqual(cavity["world_origin_mm"]["z"], 5.0)
        self.assertTrue(cavity["functional_top_access_certified"])

    def test_partial_tray_overlap_opens_only_the_uncovered_cavity_area(
        self,
    ) -> None:
        cad_prisms = [
            {
                "prism_id": "owner:under-tray",
                "cad_origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                "cad_size_mm": {"x": 5.0, "y": 10.0, "z": 20.0},
            },
            {
                "prism_id": "owner:outside-tray",
                "cad_origin_mm": {"x": 5.0, "y": 0.0, "z": 0.0},
                "cad_size_mm": {"x": 5.0, "y": 10.0, "z": 20.0},
            },
        ]
        top_inset_cuts = [
            {
                "kind": "top_inset",
                "target_prism_id": "owner:under-tray",
                "world_origin_mm": {"x": 0.0, "y": 0.0, "z": 10.0},
            }
        ]
        frozen_cavities = [
            {
                "cavity_key": "partial-cavity",
                "world_origin_mm": {"x": 2.0, "y": 2.0, "z": 5.0},
                "world_size_mm": {"x": 6.0, "y": 6.0, "z": 5.0},
            }
        ]

        result = _build_frozen_cavity_access_cuts(
            "owner",
            cad_prisms,
            top_inset_cuts,
            frozen_cavities,
            (0.0, 0.0, 0.0),
        )

        self.assertTrue(result["certified"])
        self.assertEqual(result["required_count"], 1)
        self.assertEqual(len(result["cuts"]), 1)
        access = result["cuts"][0]
        self.assertEqual(
            access["target_prism_id"],
            "owner:outside-tray",
        )
        self.assertEqual(
            access["world_origin_mm"],
            {"x": 5.0, "y": 2.0, "z": 10.0},
        )
        self.assertEqual(
            access["size_mm"],
            {"x": 3.0, "y": 6.0, "z": 10.0},
        )
        self.assertEqual(access["cavity_overlap_area_mm2"], 18.0)

    def test_partial_tray_overlap_reaches_cad_ir_and_fusion(self) -> None:
        placement = self.partial_inset_plan["placements"][0]
        cavity = placement["frozen_cavities_v1"][0]
        access_cuts = placement["composite_body"][
            "frozen_cavity_access_cuts"
        ]
        certificate = self.partial_inset_plan["finalization"][
            "composite_materialization_certificate"
        ]
        fusion_access_cuts = [
            value
            for value in self.partial_inset_fusion.cavity_cuts
            if value.cavity_source
            == "frozen_cavity_vertical_access"
        ]

        self.assertEqual(cavity["anchor_kind"], "below_top_inset")
        self.assertTrue(access_cuts)
        self.assertTrue(certificate["cavity_vertical_access_open"])
        self.assertEqual(
            certificate["cavity_vertical_access_required_count"],
            len(access_cuts),
        )
        self.assertEqual(len(fusion_access_cuts), len(access_cuts))
        cavity_rect = (
            cavity["world_origin_mm"]["x"],
            cavity["world_origin_mm"]["y"],
            cavity["world_origin_mm"]["x"]
            + cavity["world_size_mm"]["x"],
            cavity["world_origin_mm"]["y"]
            + cavity["world_size_mm"]["y"],
        )
        for access in access_cuts:
            access_rect = (
                access["world_origin_mm"]["x"],
                access["world_origin_mm"]["y"],
                access["world_origin_mm"]["x"]
                + access["size_mm"]["x"],
                access["world_origin_mm"]["y"]
                + access["size_mm"]["y"],
            )
            self.assertGreaterEqual(access_rect[0], cavity_rect[0])
            self.assertGreaterEqual(access_rect[1], cavity_rect[1])
            self.assertLessEqual(
                access_rect[2],
                cavity_rect[2] + 0.0001,
            )
            self.assertLessEqual(
                access_rect[3],
                cavity_rect[3] + 0.0001,
            )
            self.assertEqual(
                access["world_origin_mm"]["z"],
                cavity["world_origin_mm"]["z"]
                + cavity["world_size_mm"]["z"],
            )

    def test_local_higher_inset_is_joined_without_cutting_cavity_walls(
        self,
    ) -> None:
        result = _build_frozen_cavity_access_cuts(
            "owner",
            [
                {
                    "prism_id": "owner:shallow-inset",
                    "cad_origin_mm": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0,
                    },
                    "cad_size_mm": {
                        "x": 10.0,
                        "y": 10.0,
                        "z": 20.0,
                    },
                }
            ],
            [
                {
                    "kind": "top_inset",
                    "target_prism_id": "owner:shallow-inset",
                    "world_origin_mm": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 12.0,
                    },
                }
            ],
            [
                {
                    "cavity_key": "stepped-cavity",
                    "world_origin_mm": {
                        "x": 2.0,
                        "y": 2.0,
                        "z": 5.0,
                    },
                    "world_size_mm": {
                        "x": 6.0,
                        "y": 6.0,
                        "z": 5.0,
                    },
                }
            ],
            (0.0, 0.0, 0.0),
        )

        access = result["cuts"][0]
        self.assertEqual(
            access["world_origin_mm"],
            {"x": 2.0, "y": 2.0, "z": 10.0},
        )
        self.assertEqual(
            access["size_mm"],
            {"x": 6.0, "y": 6.0, "z": 2.0},
        )

    def test_source_project_is_not_mutated_by_the_artifact_build(self) -> None:
        source = _calibrated_project(with_reservation=True)
        before = deepcopy(source)

        _finalized_artifacts(source)

        self.assertEqual(source, before)


if __name__ == "__main__":
    unittest.main()
