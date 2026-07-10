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
    starter_draft,
)


class LocalComposerTests(unittest.TestCase):
    def test_starter_draft_generates_a_deterministic_portfolio(self) -> None:
        first = portfolio_from_draft(starter_draft())
        second = portfolio_from_draft(starter_draft())

        self.assertEqual(first["schema_version"], "box_fill_variants.v0")
        self.assertEqual(first["portfolio_digest"], second["portfolio_digest"])
        self.assertIsNotNone(first["recommended_variant_id"])
        self.assertTrue(first["variants"])
        self.assertTrue(all(item["status"] == "solved" for item in first["variants"]))

    def test_export_carries_an_explicit_selection_in_cad_ir_without_materialization(self) -> None:
        bundle = export_from_draft(starter_draft())

        self.assertEqual(bundle["schema_version"], LOCAL_COMPOSER_EXPORT_SCHEMA_V0)
        self.assertEqual(bundle["cad_ir"]["schema_version"], "cad_ir.v0")
        self.assertIn("box_fill_variant_selection", bundle["cad_ir"]["metadata"])
        self.assertEqual(
            bundle["cad_ir"]["metadata"]["local_composer"]["materialization_status"],
            "not_authorized",
        )
        self.assertEqual(
            bundle["selection"]["selected_variant_id"],
            bundle["cad_ir"]["metadata"]["box_fill_variant_selection"]["selected_variant_id"],
        )

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


if __name__ == "__main__":
    unittest.main()