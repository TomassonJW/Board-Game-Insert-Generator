from __future__ import annotations

import http.client
import json
import threading
import unittest

from board_game_insert_generator.local_composer import create_local_composer_server, starter_draft
from board_game_insert_generator.project_v1 import PROJECT_SCHEMA_V1


class ProjectV1ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = create_local_composer_server(port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=3)

    def tearDown(self) -> None:
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def test_serves_blank_v1_project_and_migrates_legacy_draft(self) -> None:
        self.connection.request("GET", "/api/project-v1/starter")
        response = self.connection.getresponse()
        starter = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(starter["project"]["schema_version"], PROJECT_SCHEMA_V1)
        self.assertEqual(starter["project"]["contents"], [])

        payload = json.dumps(starter_draft()).encode("utf-8")
        self.connection.request(
            "POST",
            "/api/project-v1/normalize",
            body=payload,
            headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
        )
        response = self.connection.getresponse()
        normalized = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertTrue(normalized["migrated"])
        self.assertEqual(normalized["project"]["schema_version"], PROJECT_SCHEMA_V1)
        self.assertEqual(len(normalized["project"]["contents"]), 3)

    def test_derives_containers_from_a_migratable_project(self) -> None:
        payload = json.dumps(starter_draft()).encode("utf-8")
        self.connection.request(
            "POST",
            "/api/project-v1/derive-containers",
            body=payload,
            headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
        )
        response = self.connection.getresponse()
        result = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(result["schema_version"], "bgig.container_derivation.v1")
        self.assertTrue(result["source"]["migrated"])
        self.assertGreaterEqual(result["summary"]["requested_container_count"], 1)
        self.assertIn(result["summary"]["status"], {"ready_for_p40", "blocked"})

    def test_rejects_invalid_v1_project_with_a_draft_error(self) -> None:
        invalid = {"schema_version": PROJECT_SCHEMA_V1}
        payload = json.dumps(invalid).encode("utf-8")
        self.connection.request(
            "POST",
            "/api/project-v1/normalize",
            body=payload,
            headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
        )
        response = self.connection.getresponse()
        error = json.loads(response.read())

        self.assertEqual(response.status, 400)
        self.assertEqual(error["error"]["code"], "DRAFT_INVALID")


if __name__ == "__main__":
    unittest.main()
