from __future__ import annotations

import unittest

from board_game_insert_generator.material_support import (
    BRIDGED_ON_MATERIAL,
    FALLS_THROUGH_OPENING,
    SUPPORTED_ON_MATERIAL,
    UNSTABLE_SUPPORT_POLYGON,
    evaluate_search_support,
    material_support_contract,
)
from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.solver_contract import validate_placement_geometry


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


class MaterialSupportTests(unittest.TestCase):
    def test_small_upper_body_falls_through_open_container(self) -> None:
        placements = [
            _placement(
                "lower", (0.0, 0.0, 0.0), (100.0, 100.0, 20.0), cavity=(10.0, 10.0, 80.0, 80.0)
            ),
            _placement("upper", (30.0, 30.0, 20.0), (40.0, 40.0, 10.0)),
        ]

        contract = material_support_contract(
            placements,
            fallback_xy_clearance=0.0,
            fallback_z_clearance=0.0,
        )

        upper = next(value for value in contract["supports"] if value["placement_id"] == "upper")
        self.assertEqual(contract["status"], "unsupported")
        self.assertEqual(upper["status"], FALLS_THROUGH_OPENING)
        self.assertTrue(upper["falls_through_opening"])
        self.assertFalse(upper["supported"])

    def test_connected_openings_are_treated_as_one_fall_through_region(self) -> None:
        lower = _placement(
            "lower",
            (0.0, 0.0, 0.0),
            (100.0, 100.0, 20.0),
        )
        lower["cavity_layout"] = [
            {
                "local_origin_mm": {"x": 10.0, "y": 10.0, "z": 2.0},
                "inner_dimensions_mm": {"x": 40.0, "y": 80.0, "z": 18.0},
            },
            {
                "local_origin_mm": {"x": 50.0, "y": 10.0, "z": 2.0},
                "inner_dimensions_mm": {"x": 40.0, "y": 80.0, "z": 18.0},
            },
        ]
        placements = [
            lower,
            _placement("upper", (30.0, 30.0, 20.0), (40.0, 40.0, 10.0)),
        ]

        contract = material_support_contract(
            placements,
            fallback_xy_clearance=0.0,
            fallback_z_clearance=0.0,
        )

        upper = next(value for value in contract["supports"] if value["placement_id"] == "upper")
        self.assertEqual(upper["status"], FALLS_THROUGH_OPENING)

    def test_bridge_is_accepted_when_material_spans_the_projected_center(self) -> None:
        placements = [
            _placement(
                "lower", (0.0, 0.0, 0.0), (100.0, 100.0, 20.0), cavity=(30.0, 30.0, 40.0, 40.0)
            ),
            _placement("upper", (20.0, 40.0, 20.0), (60.0, 20.0, 10.0)),
        ]

        contract = material_support_contract(
            placements,
            fallback_xy_clearance=0.0,
            fallback_z_clearance=0.0,
        )

        upper = next(value for value in contract["supports"] if value["placement_id"] == "upper")
        self.assertEqual(contract["status"], "supported")
        self.assertEqual(upper["status"], BRIDGED_ON_MATERIAL)
        self.assertAlmostEqual(upper["coverage_ratio"], 1.0 / 3.0, places=6)
        self.assertTrue(upper["stable_support_polygon"])

    def test_one_sided_quarter_support_is_rejected_as_unstable(self) -> None:
        placements = [
            _placement(
                "lower", (0.0, 0.0, 0.0), (100.0, 40.0, 20.0), cavity=(10.0, 0.0, 90.0, 40.0)
            ),
            _placement("upper", (0.0, 0.0, 20.0), (40.0, 40.0, 10.0)),
        ]

        contract = material_support_contract(
            placements,
            fallback_xy_clearance=0.0,
            fallback_z_clearance=0.0,
        )

        upper = next(value for value in contract["supports"] if value["placement_id"] == "upper")
        self.assertEqual(upper["status"], UNSTABLE_SUPPORT_POLYGON)
        self.assertAlmostEqual(upper["coverage_ratio"], 0.25)
        self.assertFalse(upper["stable_support_polygon"])

    def test_solid_body_exposes_a_full_face(self) -> None:
        placements = [
            _placement("solid", (0.0, 0.0, 0.0), (50.0, 50.0, 20.0)),
            _placement("upper", (5.0, 5.0, 20.0), (40.0, 40.0, 10.0)),
        ]

        contract = material_support_contract(
            placements,
            fallback_xy_clearance=0.0,
            fallback_z_clearance=0.0,
        )

        upper = next(value for value in contract["supports"] if value["placement_id"] == "upper")
        self.assertEqual(upper["status"], SUPPORTED_ON_MATERIAL)
        self.assertEqual(upper["coverage_ratio"], 1.0)

    def test_uncertified_has_lid_never_closes_the_opening(self) -> None:
        placements = [
            _placement(
                "lower",
                (0.0, 0.0, 0.0),
                (100.0, 100.0, 20.0),
                cavity=(10.0, 10.0, 80.0, 80.0),
                has_lid=True,
            ),
            _placement("upper", (30.0, 30.0, 20.0), (40.0, 40.0, 10.0)),
        ]

        contract = material_support_contract(
            placements,
            fallback_xy_clearance=0.0,
            fallback_z_clearance=0.0,
        )

        upper = next(value for value in contract["supports"] if value["placement_id"] == "upper")
        self.assertEqual(upper["status"], FALLS_THROUGH_OPENING)
        self.assertTrue(contract["invariants"]["uncertified_lid_ignored"])

    def test_search_path_uses_the_same_open_rim_certificate(self) -> None:
        lower_participant = {
            "id": "lower",
            "minimum_local_mm": {"x": 100.0, "y": 100.0, "z": 20.0},
            "top_inset_search_hint_v1": {
                "cavities": [
                    {
                        "local_origin_mm": {"x": 10.0, "y": 10.0, "z": 2.0},
                        "inner_dimensions_mm": {"x": 80.0, "y": 80.0, "z": 18.0},
                    }
                ]
            },
        }
        upper_participant = {
            "id": "upper",
            "minimum_local_mm": {"x": 40.0, "y": 40.0, "z": 10.0},
        }
        lower = Free3DPlacement(
            participant_id="lower",
            role="container",
            name="lower",
            origin_mm=(0.0, 0.0, 0.0),
            world_size_mm=(100.0, 100.0, 20.0),
            local_size_mm=(100.0, 100.0, 20.0),
            rotation_deg_z=0,
            supporting_ids=("box-floor",),
            support_coverage_ratio=1.0,
        )

        evaluation = evaluate_search_support(
            (30.0, 30.0, 20.0),
            (40.0, 40.0, 10.0),
            [lower],
            upper_participant,
            {"lower": lower_participant, "upper": upper_participant},
            0.0,
            0.0,
        )

        self.assertEqual(evaluation.status, FALLS_THROUGH_OPENING)
        self.assertFalse(evaluation.certified)

    def test_common_geometry_validator_rejects_void_support(self) -> None:
        placements = [
            _placement(
                "lower", (0.0, 0.0, 0.0), (100.0, 100.0, 20.0), cavity=(10.0, 10.0, 80.0, 80.0)
            ),
            _placement("upper", (30.0, 30.0, 20.0), (40.0, 40.0, 10.0)),
        ]

        validation = validate_placement_geometry(
            placements,
            {"x": 100.0, "y": 100.0, "z": 40.0},
            40.0,
            0.0,
            0.0,
            0.0,
        )

        self.assertFalse(validation["material_support_certified"])
        self.assertEqual(
            validation["material_support_contract"]["rejection_statuses"],
            [FALLS_THROUGH_OPENING],
        )


if __name__ == "__main__":
    unittest.main()
