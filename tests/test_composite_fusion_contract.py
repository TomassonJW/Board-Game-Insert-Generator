from __future__ import annotations

from copy import deepcopy
import unittest

from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FUSION_GENERATION_MODE_COMPACT_ONLY,
    FusionSkeletonError,
    generation_plan_from_cad_ir,
)


def _payload() -> dict[str, object]:
    return {
        "schema_version": "cad_ir.v0",
        "units": "mm",
        "coordinate_system": "right_handed_z_up_mm",
        "frame": {
            "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
            "x_axis": "+x",
            "y_axis": "+y",
            "z_axis": "+z",
            "handedness": "right",
        },
        "box_reference": {
            "id": "box-reference",
            "name": "Boite",
            "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
            "size_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
            "printable": False,
        },
        "parameters": [],
        "components": [
            {
                "id": "component:owner",
                "name": "Proprietaire composite",
                "module_id": "owner",
                "instance_id": "owner",
                "functional_type": "v0_1_storage_container",
                "metadata": {},
                "body": {
                    "id": "body:owner",
                    "name": "Corps composite",
                    "kind": "composite_rectangular_union",
                    "source_cell_instance_id": "owner",
                    "theoretical_origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "theoretical_size_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
                    "printable_origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "printable_size_mm": {"x": 20.0, "y": 10.0, "z": 10.0},
                    "cavities": [],
                    "face_classifications": [],
                    "applied_tolerances": [],
                    "operations": [
                        {
                            "id": "body:owner:create",
                            "kind": "create_rectangular_prism",
                            "target_id": "body:owner",
                            "parameters": {
                                "origin_mm": {"x": 0.0, "y": 0.0, "z": 0.0},
                                "size_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
                                "core_prism_id": "owner:core",
                                "coordinate_frame": "scene.frame",
                            },
                        },
                        {
                            "id": "body:owner:annex:join",
                            "kind": "join_rectangular_prism",
                            "target_id": "body:owner",
                            "parameters": {
                                "mechanism_policy": "bounded_xy_composite_v1",
                                "prism_id": "owner:annex",
                                "core_prism_id": "owner:core",
                                "attached_to_prism_id": "owner:core",
                                "attachment_axis": "x",
                                "local_origin_mm": {"x": 10.0, "y": 0.0, "z": 0.0},
                                "size_mm": {"x": 10.0, "y": 10.0, "z": 10.0},
                                "coordinate_frame": "body.local",
                            },
                        },
                        {
                            "id": "body:owner:plateau:cut",
                            "kind": "subtract_top_inset_reservation",
                            "target_id": "body:owner",
                            "parameters": {
                                "cut_id": "plateau-cut",
                                "cut_kind": "top_inset",
                                "reservation_id": "plateau",
                                "flat_item_id": "plateau",
                                "removal_order": 1,
                                "local_origin_mm": {"x": 15.0, "y": 0.0, "z": 8.0},
                                "size_mm": {"x": 5.0, "y": 10.0, "z": 2.0},
                                "retained_body_below_mm": 8.0,
                                "minimum_floor_mm": 1.2,
                                "non_perforating": True,
                                "coordinate_frame": "body.local",
                            },
                        },
                    ],
                },
            }
        ],
        "metadata": {"project_name": "Contrat composite"},
    }


class CompositeFusionContractTests(unittest.TestCase):
    def test_one_owner_joins_annex_before_exact_cut_outside_core(self) -> None:
        plan = generation_plan_from_cad_ir(
            _payload(),
            FUSION_GENERATION_MODE_COMPACT_ONLY,
        )

        self.assertEqual(plan.module_component_count, 1)
        self.assertEqual(len(plan.additive_prism_joins), 1)
        self.assertEqual(plan.additive_prism_joins[0].attachment_axis, "x")
        self.assertEqual(plan.additive_prism_joins[0].attached_to_prism_id, "owner:core")
        self.assertEqual(len(plan.cavity_cuts), 1)
        self.assertEqual(
            plan.cavity_cuts[0].cut_origin_mm.to_dict(),
            {"x": 15.0, "y": 0.0, "z": 10.0},
        )
        self.assertEqual(
            plan.blanks[0].printable_body_size_mm.to_dict(),
            {"x": 20.0, "y": 10.0, "z": 10.0},
        )

    def test_rejects_z_edge_point_wrong_axis_and_unresolved_parent(self) -> None:
        cases = {
            "z-only": {
                "local_origin_mm": {"x": 0.0, "y": 0.0, "z": 10.0},
            },
            "edge-or-point": {
                "local_origin_mm": {"x": 10.0, "y": 10.0, "z": 0.0},
            },
            "wrong-axis": {"attachment_axis": "y"},
            "unresolved-parent": {"attached_to_prism_id": "missing"},
        }
        for label, changes in cases.items():
            with self.subTest(label=label):
                payload = deepcopy(_payload())
                parameters = payload["components"][0]["body"]["operations"][1][
                    "parameters"
                ]
                parameters.update(changes)
                with self.assertRaises(FusionSkeletonError):
                    generation_plan_from_cad_ir(
                        payload,
                        FUSION_GENERATION_MODE_COMPACT_ONLY,
                    )


if __name__ == "__main__":
    unittest.main()
