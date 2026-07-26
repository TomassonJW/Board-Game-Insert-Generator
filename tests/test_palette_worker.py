from __future__ import annotations

from pathlib import Path
import sys
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / "fusion_addin" / "BoardGameInsertGenerator"
sys.path.insert(0, str(ADDIN))

import palette_worker  # noqa: E402


class PaletteWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        with palette_worker._LOCK:
            palette_worker._JOBS.clear()
            palette_worker._ACTIVE_ACTIONS.clear()

    def _request(self, operation_id: str, action: str = "solve_project") -> dict[str, object]:
        return {
            "schema": "bgig.palette.request.v1",
            "request_id": operation_id,
            "action": action,
            "source_revision": 4,
            "project": {"project_name": "Worker proof", "contents": []},
            "solver_settings": {"method": "auto", "effort": "normal"},
            "finishing_effort": "normal",
        }

    def _poll_until_ready(
        self,
        operation_id: str,
        *,
        revision: int = 4,
        project: object | None = None,
    ) -> dict[str, object]:
        payload = {
            "operation_id": operation_id,
            "source_revision": revision,
            "project": project if project is not None else {"project_name": "Worker proof", "contents": []},
            "solver_settings": {"method": "auto", "effort": "normal"},
            "finishing_effort": "normal",
        }
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            response = palette_worker.poll_project_operation(payload)
            if response is not None:
                return response
            time.sleep(0.01)
        self.fail("Le worker n a pas publie sa reponse dans le delai du test.")

    def test_runs_long_project_work_off_the_caller_thread_with_pure_data(self) -> None:
        release = threading.Event()
        observed: dict[str, object] = {}

        def handler(raw_request: object, addin_dir: str | Path, project_root: str | Path | None) -> dict[str, object]:
            observed["thread_id"] = threading.get_ident()
            observed["request"] = raw_request
            observed["addin_dir"] = str(addin_dir)
            observed["project_root"] = str(project_root)
            release.wait(1.0)
            request = raw_request if isinstance(raw_request, dict) else {}
            return {
                "schema": "bgig.palette.response.v1",
                "request_id": request.get("request_id"),
                "status": "ready",
            }

        caller_thread = threading.get_ident()
        started = time.monotonic()
        immediate = palette_worker.submit_project_operation(
            self._request("solve-worker-1"),
            ADDIN,
            ROOT,
            handler=handler,
        )
        submit_elapsed = time.monotonic() - started

        self.assertIsNone(immediate)
        self.assertLess(submit_elapsed, 0.5)
        self.assertIsNone(
            palette_worker.poll_project_operation(
                {
                    "operation_id": "solve-worker-1",
                    "source_revision": 4,
                    "project": {"project_name": "Worker proof", "contents": []},
                    "solver_settings": {"method": "auto", "effort": "normal"},
                    "finishing_effort": "normal",
                }
            )
        )
        release.set()
        response = self._poll_until_ready("solve-worker-1")

        self.assertNotEqual(observed["thread_id"], caller_thread)
        self.assertEqual(observed["request"], self._request("solve-worker-1"))
        self.assertEqual(response["status"], "ready")
        self.assertTrue(response["async_execution"]["worker_pure_data_only"])
        self.assertFalse(response["async_execution"]["fusion_side_effects_in_worker"])

    def test_notifies_completion_once_after_the_result_is_stored(self) -> None:
        completed = threading.Event()
        operation_ids: list[str] = []

        def handler(
            raw_request: object,
            _addin_dir: str | Path,
            _project_root: str | Path | None,
        ) -> dict[str, object]:
            request = raw_request if isinstance(raw_request, dict) else {}
            return {
                "schema": "bgig.palette.response.v1",
                "request_id": request.get("request_id"),
                "status": "ready",
            }

        def on_completed(operation_id: str) -> None:
            with palette_worker._LOCK:
                self.assertTrue(
                    palette_worker._JOBS[operation_id].done
                )
            operation_ids.append(operation_id)
            completed.set()

        palette_worker.submit_project_operation(
            self._request("solve-completion-event"),
            ADDIN,
            ROOT,
            handler=handler,
            on_completed=on_completed,
        )

        self.assertTrue(completed.wait(2.0))
        response = self._poll_until_ready("solve-completion-event")
        self.assertEqual(response["status"], "ready")
        self.assertEqual(operation_ids, ["solve-completion-event"])

    def test_rejects_completed_result_when_revision_or_input_digest_changed(self) -> None:
        def handler(raw_request: object, _addin_dir: str | Path, _project_root: str | Path | None) -> dict[str, object]:
            request = raw_request if isinstance(raw_request, dict) else {}
            return {
                "schema": "bgig.palette.response.v1",
                "request_id": request.get("request_id"),
                "status": "ready",
                "solver_result": {"status": "solution_found"},
                "operation_activity": {
                    "schema_version": "bgig.operation_activity.v1",
                    "operation_id": request.get("request_id"),
                    "status": "completed",
                },
            }

        palette_worker.submit_project_operation(
            self._request("solve-stale-1"),
            ADDIN,
            ROOT,
            handler=handler,
        )
        response = self._poll_until_ready(
            "solve-stale-1",
            revision=5,
            project={"project_name": "Changed", "contents": []},
        )

        self.assertEqual(response["request_id"], "solve-stale-1")
        self.assertEqual(response["status"], "stale")
        self.assertEqual(response["solver_result"]["status"], "stale_or_cancelled")
        self.assertEqual(response["solver_result"]["stop_reason"], "source_identity_changed")
        self.assertEqual(response["operation_activity"]["status"], "rejected")
        self.assertTrue(response["async_execution"]["stale"])
        self.assertNotEqual(
            response["async_execution"]["input_digest"],
            response["async_execution"]["current_input_digest"],
        )

    def test_rejects_finalization_if_its_budget_changed_before_publication(self) -> None:
        def handler(raw_request: object, _addin_dir: str | Path, _project_root: str | Path | None) -> dict[str, object]:
            request = raw_request if isinstance(raw_request, dict) else {}
            return {
                "schema": "bgig.palette.response.v1",
                "request_id": request.get("request_id"),
                "status": "ready",
            }

        palette_worker.submit_project_operation(
            self._request("finish-stale-budget", action="finalize_project"),
            ADDIN,
            ROOT,
            handler=handler,
        )
        deadline = time.monotonic() + 2.0
        response = None
        while response is None and time.monotonic() < deadline:
            response = palette_worker.poll_project_operation(
                {
                    "operation_id": "finish-stale-budget",
                    "source_revision": 4,
                    "project": {"project_name": "Worker proof", "contents": []},
                    "solver_settings": {"method": "auto", "effort": "normal"},
                    "finishing_effort": "quick",
                }
            )
            if response is None:
                time.sleep(0.01)

        self.assertIsNotNone(response)
        self.assertEqual(response["status"], "stale")
        self.assertEqual(response["solver_result"]["stop_reason"], "source_identity_changed")
    def test_rejects_duplicate_action_without_starting_a_second_worker(self) -> None:
        release = threading.Event()
        starts: list[str] = []

        def handler(raw_request: object, _addin_dir: str | Path, _project_root: str | Path | None) -> dict[str, object]:
            request = raw_request if isinstance(raw_request, dict) else {}
            starts.append(str(request.get("request_id")))
            release.wait(1.0)
            return {
                "schema": "bgig.palette.response.v1",
                "request_id": request.get("request_id"),
                "status": "ready",
            }

        palette_worker.submit_project_operation(
            self._request("solve-first"),
            ADDIN,
            ROOT,
            handler=handler,
        )
        duplicate = palette_worker.submit_project_operation(
            self._request("solve-second", action="finalize_project"),
            ADDIN,
            ROOT,
            handler=handler,
        )

        self.assertEqual(duplicate["status"], "busy")
        self.assertEqual(
            duplicate["async_execution"]["conflicting_operation_id"],
            "solve-first",
        )
        blocked_validation = palette_worker.busy_response_while_project_operation_active(
            {"request_id": "validate-during-solve", "action": "validate_project"}
        )
        self.assertEqual(blocked_validation["status"], "busy")
        self.assertEqual(
            blocked_validation["async_execution"]["conflicting_operation_id"],
            "solve-first",
        )
        release.set()
        self._poll_until_ready("solve-first")
        self.assertEqual(starts, ["solve-first"])

    def test_worker_module_has_no_fusion_api_import_or_html_publication(self) -> None:
        source = (ADDIN / "palette_worker.py").read_text(encoding="utf-8")
        self.assertNotIn("import adsk", source)
        self.assertNotIn("sendInfoToHTML", source)
        self.assertNotIn("_synchronize_palette_cad_response", source)
        self.assertEqual(
            palette_worker.ASYNC_PROJECT_ACTIONS,
            frozenset({"solve_project", "finalize_project"}),
        )
        self.assertFalse(palette_worker.is_async_project_action("materialize_project"))


if __name__ == "__main__":
    unittest.main()
