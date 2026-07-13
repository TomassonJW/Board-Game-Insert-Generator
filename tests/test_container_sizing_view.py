from copy import deepcopy
import unittest

from board_game_insert_generator.container_sizing_view import (
    CONTAINER_SIZING_VIEW_SCHEMA_V1,
    build_container_sizing_view,
)
from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
from board_game_insert_generator.partition_solver import solve_partition_plan
from board_game_insert_generator.project_v1 import blank_project_v1


def project_with_container() -> dict[str, object]:
    project = blank_project_v1()
    project["box"]["inner_dimensions_mm"] = {"x": 120.0, "y": 120.0, "z": 30.0}
    project["box"]["usable_height_mm"] = 30.0
    project["container_groups"] = [{
        "id": "cards", "name": "Bac cartes", "wall_thickness_mm": None,
        "floor_thickness_mm": None,
        "dimension_modes": {"x": "auto", "y": "target", "z": "fixed"},
        "target_outer_dimensions_mm": {"x": None, "y": 100.0, "z": None},
        "locked_outer_dimensions_mm": {"x": None, "y": None, "z": 20.0},
    }]
    project["contents"] = [{
        "id": "deck", "name": "Cartes", "shape_kind": "cards",
        "dimensions_mm": {"x": 63.5, "y": 88.9, "z": 12.0}, "quantity": 1,
        "container_group_id": "cards", "content_clearance_mm": None,
        "measurement_confidence": "exact",
    }]
    return project


class ContainerSizingViewTests(unittest.TestCase):
    def test_exposes_minimum_and_axis_contracts_before_an_estimation(self) -> None:
        project = project_with_container()
        snapshot = deepcopy(project)
        view = build_container_sizing_view(project, derive_expandable_envelope_contract(project))

        container = view["containers"][0]
        self.assertEqual(view["schema_version"], CONTAINER_SIZING_VIEW_SCHEMA_V1)
        self.assertEqual(view["proposal_status"], "not_computed")
        self.assertEqual(container["container_group_id"], "cards")
        self.assertEqual(container["axis_contracts"]["x"]["mode"], "auto")
        self.assertEqual(container["axis_contracts"]["y"]["requested_mm"], 100.0)
        self.assertEqual(container["axis_contracts"]["z"]["mode"], "fixed")
        self.assertIsNone(container["calculated_outer_dimensions_mm"])
        self.assertEqual(container["axis_contracts"]["x"]["status"], "not_computed")
        self.assertEqual(project, snapshot)
        self.assertTrue(view["invariants"]["does_not_mutate_project"])

    def test_projects_real_calculated_dimensions_and_axis_reasons(self) -> None:
        project = project_with_container()
        partition = solve_partition_plan(project)
        view = build_container_sizing_view(
            project,
            derive_expandable_envelope_contract(project),
            partition,
        )

        container = view["containers"][0]
        self.assertIn(view["proposal_status"], {"complete", "partial"})
        self.assertIsNotNone(container["calculated_outer_dimensions_mm"])
        self.assertEqual(container["axis_contracts"]["y"]["mode"], "target")
        self.assertTrue(container["axis_contracts"]["y"]["reason"])
        self.assertIn(container["axis_contracts"]["z"]["status"], {"satisfied", "deviated"})
        self.assertIsNotNone(container["surplus_distribution_mm"])
        self.assertIsNotNone(container["stage"]["index"])

    def test_uses_stable_group_ids_when_human_labels_are_duplicate(self) -> None:
        project = project_with_container()
        duplicate = deepcopy(project["container_groups"][0])
        duplicate["id"] = "cards-duplicate"
        project["container_groups"].append(duplicate)
        content = deepcopy(project["contents"][0])
        content["id"] = "deck-duplicate"
        content["container_group_id"] = duplicate["id"]
        project["contents"].append(content)

        view = build_container_sizing_view(project, derive_expandable_envelope_contract(project))

        self.assertEqual([item["label"] for item in view["containers"]], ["Bac cartes", "Bac cartes"])
        self.assertEqual(
            [item["container_group_id"] for item in view["containers"]],
            ["cards", "cards-duplicate"],
        )
        self.assertEqual(view["summary"]["container_count"], 2)
    def test_impossible_plan_never_projects_a_fake_calculated_size(self) -> None:
        project = project_with_container()
        project["container_groups"][0]["locked_outer_dimensions_mm"]["z"] = 1.0
        partition = solve_partition_plan(project)
        view = build_container_sizing_view(
            project,
            derive_expandable_envelope_contract(project),
            partition,
        )

        container = view["containers"][0]
        self.assertIn(view["proposal_status"], {"impossible", "incomplete"})
        self.assertIsNone(container["calculated_outer_dimensions_mm"])
        self.assertNotEqual(container["proposal_status"], "complete")
        self.assertIn("ne permet pas", container["axis_contracts"]["z"]["reason"])
        self.assertTrue(container["minimum_message"])


if __name__ == "__main__":
    unittest.main()
