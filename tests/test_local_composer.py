from __future__ import annotations

import http.client
import json
import threading
import unittest

from board_game_insert_generator.local_composer import (
    LOCAL_COMPOSER_EXPORT_SCHEMA_V0,
    LOCAL_COMPOSER_SCHEMA_V0,
    LocalComposerError,
    create_local_composer_server,
    export_from_draft,
    portfolio_from_draft,
    starter_catalog,
    starter_draft,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import generation_plan_from_cad_ir


class LocalComposerTests(unittest.TestCase):
    def test_starter_draft_generates_a_deterministic_portfolio(self) -> None:
        first = portfolio_from_draft(starter_draft())
        second = portfolio_from_draft(starter_draft())

        self.assertEqual(first["schema_version"], "box_fill_variants.v0")
        self.assertEqual(first["portfolio_digest"], second["portfolio_digest"])
        self.assertIsNotNone(first["recommended_variant_id"])
        self.assertTrue(first["variants"])
        self.assertTrue(all(item["status"] == "solved" for item in first["variants"]))

    def test_starter_catalog_contains_solved_local_examples(self) -> None:
        starters = starter_catalog()

        self.assertEqual([starter["id"] for starter in starters], ["mixed-box", "card-game", "board-game"])
        self.assertTrue(all(portfolio_from_draft(starter["draft"])["recommended_variant_id"] for starter in starters))

    def test_export_preserves_appearance_without_changing_the_solved_layout(self) -> None:
        draft = starter_draft()
        baseline_digest = portfolio_from_draft(draft)["portfolio_digest"]
        self.assertEqual(draft["appearance"]["schema_version"], "bgig.appearance.v0")
        draft["appearance"]["shape"]["corner_style"] = "chamfered"
        draft["appearance"]["shape"]["chamfer_mm"] = 4.0
        draft["appearance"]["visual"]["theme"] = "graphite"

        bundle = export_from_draft(draft)

        self.assertEqual(portfolio_from_draft(draft)["portfolio_digest"], baseline_digest)
        self.assertEqual(bundle["appearance"], draft["appearance"])
        self.assertEqual(bundle["selection"]["appearance"], draft["appearance"])
        self.assertEqual(bundle["cad_ir"]["metadata"]["appearance"], draft["appearance"])
        self.assertEqual(
            bundle["cad_ir"]["metadata"]["local_composer"]["appearance_status"],
            "stored_for_preview_only_not_materialized",
        )

    def test_rejects_an_invalid_appearance_as_a_draft_error(self) -> None:
        draft = starter_draft()
        draft["appearance"]["visual"]["theme"] = "neon"

        with self.assertRaisesRegex(LocalComposerError, "theme"):
            portfolio_from_draft(draft)

    def test_export_materializes_the_explicit_selection_as_open_top_trays(self) -> None:
        bundle = export_from_draft(starter_draft())

        self.assertEqual(bundle["schema_version"], LOCAL_COMPOSER_EXPORT_SCHEMA_V0)
        self.assertEqual(bundle["cad_ir"]["schema_version"], "cad_ir.v0")
        self.assertIn("box_fill_variant_selection", bundle["cad_ir"]["metadata"])
        self.assertEqual(
            bundle["cad_ir"]["metadata"]["local_composer"]["materialization_status"],
            "prepared_open_top_trays_for_fusion_smoke",
        )
        self.assertEqual(
            bundle["selection"]["selected_variant_id"],
            bundle["cad_ir"]["metadata"]["box_fill_variant_selection"]["selected_variant_id"],
        )
        modules = bundle["selection"]["variant"]["solution"]["solved_plan"]["modules"]
        components = bundle["cad_ir"]["components"]
        self.assertEqual(len(components), len(modules))
        self.assertEqual(
            [component["module_id"] for component in components],
            [module["id"] for module in modules],
        )
        self.assertTrue(all(component["body"]["kind"] == "rectangular_blank" for component in components))
        self.assertTrue(all(component["metadata"]["geometry_status"] == "open_top_tray_candidate" for component in components))
        for component, module in zip(components, modules):
            body = component["body"]
            self.assertEqual(len(body["cavities"]), 1)
            cavity = body["cavities"][0]
            self.assertEqual(cavity["functional_type"], "free")
            self.assertEqual(cavity["local_origin_mm"], {"x": 1.2, "y": 1.2, "z": 1.2})
            self.assertEqual(cavity["size_mm"]["x"], module["size_mm"]["x"] - 2.4)
            self.assertEqual(cavity["size_mm"]["y"], module["size_mm"]["y"] - 2.4)
            self.assertEqual(cavity["size_mm"]["z"], module["size_mm"]["z"] - 1.2)
            self.assertEqual(
                [operation["kind"] for operation in body["operations"]],
                ["create_rectangular_prism", "subtract_rectangular_cavity"],
            )
        plan = generation_plan_from_cad_ir(bundle["cad_ir"])
        self.assertEqual(len(plan.blanks), len(modules))
        self.assertEqual(len(plan.cavity_cuts), len(modules))
        for cut in plan.cavity_cuts:
            self.assertAlmostEqual(cut.retained_floor_mm, 1.2)
        self.assertEqual(plan.blanks[0].origin_mm.to_dict(), modules[0]["origin_mm"])

    def test_export_refuses_a_selected_module_that_cannot_retain_walls_and_floor(self) -> None:
        draft = starter_draft()
        draft["candidates"][0]["size_mm"] = {"x": 2.4, "y": 50, "z": 20}

        with self.assertRaisesRegex(LocalComposerError, "P31_TRAY_CAVITY_NOT_FEASIBLE"):
            export_from_draft(draft)
    def test_rejects_unknown_layer_before_engine_execution(self) -> None:
        draft = starter_draft()
        draft["candidates"][0]["allowed_layers"] = ["missing"]

        with self.assertRaisesRegex(LocalComposerError, "known layer"):
            portfolio_from_draft(draft)

    def test_supports_explicit_multi_asset_allocation_in_one_candidate(self) -> None:
        draft = starter_draft()
        cards_and_tokens = dict(draft["candidates"][0])
        cards_and_tokens["asset_ids"] = ["cards", "tokens"]
        draft["candidates"] = [cards_and_tokens, draft["candidates"][2]]

        portfolio = portfolio_from_draft(draft)

        self.assertIsNotNone(portfolio["recommended_variant_id"])
        allocation_ids = {
            allocation["asset_id"]
            for allocation in portfolio["variants"][0]["solution"]["solved_plan"]["allocations"]
            if allocation["module_id"] == "card-tray"
        }
        self.assertEqual(allocation_ids, {"cards", "tokens"})

    def test_loopback_api_serves_only_the_local_composer_contract(self) -> None:
        server = create_local_composer_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_address[1]
        try:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
            connection.request("GET", "/api/health", headers={"Origin": "http://127.0.0.1:5173"})
            response = connection.getresponse()
            health = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(response.getheader("Access-Control-Allow-Origin"), "http://127.0.0.1:5173")
            self.assertEqual(health["schema_version"], LOCAL_COMPOSER_SCHEMA_V0)

            connection.request("GET", "/api/starters")
            response = connection.getresponse()
            starters = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(len(starters["starters"]), 3)

            payload = json.dumps(starter_draft()).encode("utf-8")
            connection.request(
                "POST",
                "/api/portfolio",
                body=payload,
                headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
            )
            response = connection.getresponse()
            result = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertIn("portfolio", result)
            self.assertIsNotNone(result["portfolio"]["recommended_variant_id"])

            connection.request("GET", "/api/not-a-route")
            response = connection.getresponse()
            self.assertEqual(response.status, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


    def test_mechanism_is_transport_only_and_does_not_change_layout(self) -> None:
        draft = starter_draft()
        baseline_digest = portfolio_from_draft(draft)["portfolio_digest"]
        draft["mechanism"]["kind"] = "sliding_lid"

        bundle = export_from_draft(draft)

        self.assertEqual(portfolio_from_draft(draft)["portfolio_digest"], baseline_digest)
        self.assertEqual(bundle["mechanism"], draft["mechanism"])
        self.assertEqual(bundle["selection"]["mechanism"], draft["mechanism"])
        self.assertEqual(bundle["cad_ir"]["metadata"]["mechanism"], draft["mechanism"])
        self.assertEqual(
            bundle["cad_ir"]["metadata"]["local_composer"]["mechanism_status"],
            "coupon_prepared_for_fusion_smoke",
        )
        self.assertTrue(bundle["mechanism_readiness"])
        self.assertTrue(
            all(
                item["status"] in {"planned_for_coupon", "refused"}
                for item in bundle["mechanism_readiness"]
            )
        )

    def test_rejects_an_invalid_mechanism_as_a_draft_error(self) -> None:
        draft = starter_draft()
        draft["mechanism"]["rail_clearance_mm"] = 0.7

        with self.assertRaisesRegex(LocalComposerError, "rail_clearance_mm"):
            portfolio_from_draft(draft)

    def test_sliding_lid_adds_one_two_piece_coupon_outside_the_packed_layout(self) -> None:
        draft = starter_draft()
        draft["mechanism"]["kind"] = "sliding_lid"

        bundle = export_from_draft(draft)
        coupon = bundle["mechanism_coupon"]
        plan = generation_plan_from_cad_ir(bundle["cad_ir"])

        self.assertEqual(coupon["status"], "prepared_for_fusion_smoke")
        self.assertEqual(coupon["materialization_status"], "two_piece_coupon_cad_ir")
        self.assertEqual(coupon["piece_count"], 2)
        coupon_components = [
            component for component in bundle["cad_ir"]["components"] if component["metadata"].get("coupon")
        ]
        self.assertEqual(len(coupon_components), 2)
        lid = next(component for component in coupon_components if component["functional_type"] == "sliding_lid_coupon_cap")
        self.assertEqual(
            [operation["kind"] for operation in lid["body"]["operations"]],
            ["create_rectangular_prism", "join_rectangular_prism", "join_rectangular_prism"],
        )
        self.assertEqual(len(plan.additive_prism_joins), 2)
        self.assertEqual(len(plan.blanks), len(bundle["cad_ir"]["components"]))

if __name__ == "__main__":
    unittest.main()
