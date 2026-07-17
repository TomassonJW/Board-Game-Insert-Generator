from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.container_derivation import (
    CONTAINER_DERIVATION_SCHEMA_V1,
    _bounded_target_widths,
    derive_container_plan,
)
from board_game_insert_generator.project_v1 import blank_project_v1


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "Boite temoin"
    project["container_groups"] = [
        {"id": "shared", "name": "Pieces de jeu", "wall_thickness_mm": None, "floor_thickness_mm": None}
    ]
    project["contents"] = [
        {
            "id": "tokens",
            "name": "Jetons ronds",
            "shape_kind": "round",
            "dimensions_mm": {"x": 10.0, "y": 10.0, "z": 5.0},
            "quantity": 12,
            "container_group_id": "shared",
            "content_clearance_mm": 1.0,
            "measurement_confidence": "exact",
        }
    ]
    return project


class ContainerDerivationTests(unittest.TestCase):
    def test_derives_count_aware_round_compartment_without_mutating_project(self) -> None:
        project = _project()
        original = deepcopy(project)

        result = derive_container_plan(project)

        self.assertEqual(project, original)
        self.assertEqual(result["schema_version"], CONTAINER_DERIVATION_SCHEMA_V1)
        self.assertEqual(result["summary"]["status"], "ready_for_p40")
        container = result["containers"][0]
        compartment = container["compartments"][0]
        self.assertEqual(container["status"], "ready")
        self.assertEqual(compartment["footprint_profile"]["policy"], "round_bounding_box_v1")
        self.assertEqual(compartment["quantity"]["capacity_per_stack"], 10)
        self.assertEqual(compartment["quantity"]["pile_count"], 2)
        self.assertEqual(compartment["quantity"]["items_per_pile"], 6)
        self.assertEqual(compartment["inner_dimensions_mm"]["z"], 31.0)
        self.assertEqual(container["outer_dimensions_mm"]["z"], 32.2)

    def test_cards_keep_declared_deck_height_while_other_shapes_share_one_container(self) -> None:
        project = _project()
        project["contents"].append(
            {
                "id": "deck",
                "name": "Cartes",
                "shape_kind": "cards",
                "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0},
                "quantity": 110,
                "container_group_id": "shared",
                "content_clearance_mm": 0.6,
                "measurement_confidence": "exact",
            }
        )

        result = derive_container_plan(project)

        container = result["containers"][0]
        card_compartment = next(item for item in container["compartments"] if item["content_id"] == "deck")
        self.assertEqual(len(container["compartments"]), 2)
        self.assertEqual(card_compartment["sizing_policy"], "declared_deck_height_v1")
        self.assertEqual(card_compartment["quantity"]["pile_count"], 1)
        self.assertEqual(card_compartment["quantity"]["capacity_per_stack"], 110)
        self.assertEqual(card_compartment["inner_dimensions_mm"]["z"], 18.6)
        self.assertEqual(container["compartment_layout"]["internal_wall_thickness_mm"], 1.2)
        self.assertTrue(all(item["local_origin_mm"] is not None for item in container["compartments"]))

    def test_reports_an_explainable_blocker_when_a_container_cannot_fit(self) -> None:
        project = _project()
        project["box"] = {
            "inner_dimensions_mm": {"x": 30.0, "y": 30.0, "z": 20.0},
            "usable_height_mm": 18.0,
            "lid_clearance_mm": 2.0,
        }
        project["contents"][0]["dimensions_mm"] = {"x": 40.0, "y": 40.0, "z": 5.0}

        result = derive_container_plan(project)

        self.assertEqual(result["summary"]["status"], "blocked")
        self.assertEqual(result["containers"][0]["status"], "blocked")
        self.assertTrue(any("orientation X/Y" in blocker for blocker in result["containers"][0]["blockers"]))
        self.assertEqual(result["blockers"][0]["container_group_id"], "shared")

    def test_uses_per_container_wall_floor_and_a_zero_content_clearance(self) -> None:
        project = _project()
        project["container_groups"][0]["wall_thickness_mm"] = 2.0
        project["container_groups"][0]["floor_thickness_mm"] = 3.0
        project["contents"][0]["quantity"] = 1
        project["contents"][0]["content_clearance_mm"] = 0.0

        result = derive_container_plan(project)

        container = result["containers"][0]
        compartment = container["compartments"][0]
        self.assertEqual(compartment["content_clearance_mm"], 0.0)
        self.assertEqual(compartment["inner_dimensions_mm"], {"x": 10.0, "y": 10.0, "z": 5.0})
        self.assertEqual(container["outer_dimensions_mm"], {"x": 14.0, "y": 14.0, "z": 8.0})

    def test_all_user_shape_kinds_are_derived_in_one_shared_container(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "mixed", "name": "Tout ensemble", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        shape_kinds = ("round", "square", "rectangle", "cards", "cube", "meeple", "custom")
        project["contents"] = [
            {
                "id": shape,
                "name": shape,
                "shape_kind": shape,
                "dimensions_mm": {"x": 10.0, "y": 12.0, "z": 5.0},
                "quantity": 2,
                "container_group_id": "mixed",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for shape in shape_kinds
        ]

        result = derive_container_plan(project)

        container = result["containers"][0]
        self.assertEqual(container["status"], "ready")
        self.assertEqual({item["shape_kind"] for item in container["compartments"]}, set(shape_kinds))

    def test_shelf_width_candidates_remain_bounded_for_dense_containers(self) -> None:
        compartments = [
            {
                "id": f"cavity-{index}",
                "inner_dimensions_mm": {
                    "x": 8.0 + index % 11,
                    "y": 10.0 + index % 7,
                    "z": 5.0,
                },
            }
            for index in range(100)
        ]

        widths = _bounded_target_widths(compartments, 1.2, 247.6, 177.6)

        self.assertLessEqual(len(widths), 48)
        self.assertIn(247.6, widths)
        self.assertIn(177.6, widths)

    def test_dense_mixed_container_uses_a_box_bounded_multi_row_layout(self) -> None:
        project = blank_project_v1()
        project["box"] = {
            "inner_dimensions_mm": {"x": 250.0, "y": 180.0, "z": 70.0},
            "usable_height_mm": 69.8,
            "lid_clearance_mm": 0.2,
        }
        project["container_groups"] = [
            {"id": "dense", "name": "Dense", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]
        project["contents"] = [
            {
                "id": f"cards-{index}",
                "name": "Cards",
                "shape_kind": "cards",
                "dimensions_mm": {"x": 89.0, "y": 30.16, "z": 64.0},
                "quantity": 1,
                "container_group_id": "dense",
                "content_clearance_mm": 0.6,
                "measurement_confidence": "exact",
            }
            for index in range(2)
        ] + [
            {
                "id": f"tokens-{index}",
                "name": "Tokens",
                "shape_kind": "round",
                "dimensions_mm": {"x": 20.0, "y": 20.0, "z": 3.0},
                "quantity": 60,
                "container_group_id": "dense",
                "content_clearance_mm": 0.6,
                "measurement_confidence": "exact",
            }
            for index in range(4)
        ]

        result = derive_container_plan(project)

        container = result["containers"][0]
        self.assertEqual(container["status"], "ready")
        self.assertEqual(container["outer_dimensions_mm"], {"x": 92.6, "y": 129.92, "z": 65.8})
        self.assertEqual(container["compartment_layout"]["policy"], "bounded_shelf_candidates_v2")
        self.assertGreater(container["compartment_layout"]["candidate_count_evaluated"], 1)
        self.assertNotEqual(container["compartment_layout"]["box_fit_orientation"], "none")

    def test_empty_requested_container_waits_for_fill_resolution(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {"id": "future", "name": "Bac vide", "wall_thickness_mm": None, "floor_thickness_mm": None}
        ]

        result = derive_container_plan(project)

        self.assertEqual(result["summary"]["status"], "ready_for_p40")
        self.assertEqual(result["containers"][0]["status"], "pending_fill_resolution")
        self.assertIsNone(result["containers"][0]["outer_dimensions_mm"])

    def test_large_quantity_is_derived_without_a_business_cardinality_limit(self) -> None:
        project = _project()
        project["contents"][0]["quantity"] = 1_000_000

        result = derive_container_plan(project)

        quantity = result["containers"][0]["compartments"][0]["quantity"]
        self.assertEqual(quantity["declared_count"], 1_000_000)
        self.assertGreater(quantity["pile_count"], 1)


if __name__ == "__main__":
    unittest.main()
