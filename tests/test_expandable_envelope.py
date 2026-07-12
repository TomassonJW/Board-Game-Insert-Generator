from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.expandable_envelope import (
    EXPANDABLE_ENVELOPE_SCHEMA_V1,
    ExpandableEnvelopeError,
    derive_expandable_envelope_contract,
)
from board_game_insert_generator.project_v1 import (
    ProjectContractError,
    blank_project_v1,
    normalize_project_draft,
)


def _project_for(shape_kind: str = "round", quantity: int = 12) -> dict[str, object]:
    project = blank_project_v1()
    project["box"]["inner_dimensions_mm"] = {"x": 500.0, "y": 400.0, "z": 120.0}
    project["box"]["usable_height_mm"] = 110.0
    project["container_groups"] = [
        {"id": "main", "name": "Bac principal", "wall_thickness_mm": None, "floor_thickness_mm": None}
    ]
    dimensions = {
        "round": {"x": 14.0, "y": 12.0, "z": 3.0},
        "square": {"x": 14.0, "y": 13.0, "z": 3.0},
        "rectangle": {"x": 20.0, "y": 10.0, "z": 4.0},
        "cards": {"x": 63.0, "y": 88.0, "z": 18.0},
        "cube": {"x": 12.0, "y": 13.0, "z": 14.0},
        "meeple": {"x": 18.0, "y": 12.0, "z": 8.0},
        "custom": {"x": 22.0, "y": 17.0, "z": 6.0},
    }[shape_kind]
    project["contents"] = [
        {
            "id": f"asset-{shape_kind}",
            "name": f"Asset {shape_kind}",
            "shape_kind": shape_kind,
            "dimensions_mm": dimensions,
            "quantity": quantity,
            "container_group_id": "main",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        }
    ]
    return project


class ExpandableEnvelopeContractTests(unittest.TestCase):
    def test_supports_all_mvp_shapes_with_calibrated_cavities(self) -> None:
        for shape_kind in ("round", "square", "rectangle", "cards", "cube", "meeple", "custom"):
            with self.subTest(shape_kind=shape_kind):
                result = derive_expandable_envelope_contract(_project_for(shape_kind))
                container = result["containers"][0]

                self.assertEqual(result["schema_version"], EXPANDABLE_ENVELOPE_SCHEMA_V1)
                self.assertEqual(result["summary"]["status"], "ready_for_p56")
                self.assertEqual(result["summary"]["automatic_body_count"], 0)
                self.assertEqual(container["cavity_layout"][0]["shape_kind"], shape_kind)
                self.assertEqual(
                    container["minimum_outer_envelope_mm"],
                    container["final_outer_envelope_mm"],
                )

    def test_card_orientation_changes_the_calibrated_cavity_envelope(self) -> None:
        flat_project = _project_for("cards", quantity=100)
        flat_project["contents"][0]["storage_orientation"] = "flat"
        upright_project = deepcopy(flat_project)
        upright_project["contents"][0]["storage_orientation"] = "upright_long_edge"

        flat = derive_expandable_envelope_contract(flat_project)["containers"][0]["cavity_layout"][0]
        upright = derive_expandable_envelope_contract(upright_project)["containers"][0]["cavity_layout"][0]

        self.assertNotEqual(flat["inner_dimensions_mm"], upright["inner_dimensions_mm"])
        self.assertLess(upright["inner_dimensions_mm"]["y"], flat["inner_dimensions_mm"]["y"])
        self.assertGreater(upright["inner_dimensions_mm"]["z"], flat["inner_dimensions_mm"]["z"])

    def test_expanding_final_envelope_never_changes_local_cavities(self) -> None:
        project = _project_for("round", quantity=40)
        minimum_result = derive_expandable_envelope_contract(project)
        minimum_container = minimum_result["containers"][0]
        minimum = minimum_container["minimum_outer_envelope_mm"]
        final = {"x": minimum["x"] + 40.0, "y": minimum["y"] + 20.0, "z": minimum["z"] + 10.0}

        expanded_result = derive_expandable_envelope_contract(
            project, final_outer_dimensions_by_group={"main": final}
        )
        expanded = expanded_result["containers"][0]

        self.assertEqual(expanded["status"], "ready")
        self.assertEqual(expanded["cavity_layout"], minimum_container["cavity_layout"])
        self.assertEqual(expanded["final_outer_envelope_mm"], final)
        self.assertEqual(expanded["surplus_distribution_mm"]["below"], 10.0)
        self.assertEqual(expanded["minimum_envelope_origin_in_final_mm"]["x"], 20.0)
        self.assertTrue(expanded["invariants"]["cavity_local_origins_fixed"])

    def test_schema_defaults_are_additive_and_legacy_safe(self) -> None:
        normalized = normalize_project_draft(_project_for()).project
        group = normalized["container_groups"][0]

        self.assertEqual(group["expansion_axes"], {"x": True, "y": True, "z": True})
        self.assertEqual(group["locked_outer_dimensions_mm"], {"x": None, "y": None, "z": None})
        self.assertEqual(group["surplus_preference"], "balanced")

    def test_enforces_disabled_axes_locks_and_minimum_dimensions(self) -> None:
        project = _project_for()
        minimum = derive_expandable_envelope_contract(project)["containers"][0]["minimum_outer_envelope_mm"]
        project["container_groups"][0]["expansion_axes"] = {"x": False, "y": True, "z": True}
        project["container_groups"][0]["locked_outer_dimensions_mm"] = {
            "x": None,
            "y": minimum["y"] + 10.0,
            "z": None,
        }
        proposal = {
            "x": minimum["x"] + 1.0,
            "y": minimum["y"] + 8.0,
            "z": minimum["z"] - 1.0,
        }

        result = derive_expandable_envelope_contract(
            project, final_outer_dimensions_by_group={"main": proposal}
        )
        messages = " ".join(result["containers"][0]["blockers"])

        self.assertEqual(result["summary"]["status"], "blocked")
        self.assertIn("cannot expand", messages)
        self.assertIn("locked", messages)
        self.assertIn("below the minimum", messages)

    def test_multiple_contents_keep_distinct_fixed_cavities(self) -> None:
        project = _project_for("rectangle", quantity=24)
        second = deepcopy(project["contents"][0])
        second.update(
            {
                "id": "asset-cards",
                "name": "Cartes",
                "shape_kind": "cards",
                "dimensions_mm": {"x": 63.0, "y": 88.0, "z": 18.0},
                "quantity": 100,
            }
        )
        project["contents"].append(second)

        result = derive_expandable_envelope_contract(project)
        cavities = result["containers"][0]["cavity_layout"]

        self.assertEqual(len(cavities), 2)
        self.assertEqual({item["content_id"] for item in cavities}, {"asset-rectangle", "asset-cards"})
        self.assertEqual(result["summary"]["fixed_cavity_count"], 2)

    def test_rejects_invalid_constraint_values_and_unknown_proposals(self) -> None:
        project = _project_for()
        project["container_groups"][0]["expansion_axes"] = {"x": "yes"}

        with self.assertRaisesRegex(ProjectContractError, "must be a boolean"):
            normalize_project_draft(project)
        with self.assertRaisesRegex(ExpandableEnvelopeError, "unknown container groups"):
            derive_expandable_envelope_contract(
                _project_for(), final_outer_dimensions_by_group={"missing": {"x": 10.0}}
            )


if __name__ == "__main__":
    unittest.main()
