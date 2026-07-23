from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import textwrap
import unittest

from board_game_insert_generator.external_solver_adapters import (
    ExternalSolverLimits,
    ExternalSolverRuntime,
    STATUS_BOUNDED_UNKNOWN,
    STATUS_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND,
    STATUS_UNSUPPORTED,
    build_external_adapter_exact_controls,
    prepare_external_floor_case,
    run_external_solver_adapter,
)
from board_game_insert_generator.external_solver_artifacts import (
    ExternalSolverArtifactError,
    external_solver_candidate_catalog,
    validate_external_solver_artifact_lock,
    verify_external_solver_artifacts,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = (
    ROOT / "tests" / "fixtures" / "p64_l07c_external_solver_artifacts.v1.json"
)


class ExternalSolverArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    def test_versioned_lock_covers_four_candidates_and_three_families(self) -> None:
        validated = validate_external_solver_artifact_lock(self.lock)
        catalog = external_solver_candidate_catalog(validated)

        self.assertEqual(validated["artifact_count"], 32)
        self.assertEqual(
            {item["candidate_id"] for item in catalog},
            {"ortools_cp_sat", "highs", "scip", "laff"},
        )
        self.assertGreaterEqual(len({item["family"] for item in catalog}), 3)
        self.assertEqual(
            next(item for item in catalog if item["candidate_id"] == "scip")[
                "version"
            ],
            "SCIP-10.0.2_PySCIPOpt-6.2.1",
        )

    def test_lock_digest_is_fail_closed(self) -> None:
        tampered = deepcopy(self.lock)
        tampered["candidates"][0]["version"] = "unlocked"

        with self.assertRaisesRegex(
            ExternalSolverArtifactError, "digest mismatch"
        ):
            validate_external_solver_artifact_lock(tampered)

    def test_local_artifact_receipt_hashes_before_execution(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            candidates = []
            artifacts = []
            for index in range(3):
                candidate_id = f"candidate-{index}"
                group = f"group-{index}"
                candidates.append(
                    {
                        "candidate_id": candidate_id,
                        "exact_for_floor_model": True,
                        "family": f"family-{index}",
                        "license": "MIT",
                        "product_gate": "candidate",
                        "source_url": "https://example.com/candidate",
                        "version": "1",
                    }
                )
                path = root / group / "artifact.bin"
                path.parent.mkdir()
                payload = f"artifact-{index}".encode("ascii")
                path.write_bytes(payload)
                artifacts.append(
                    {
                        "artifact_group": group,
                        "byte_count": len(payload),
                        "candidate_id": candidate_id,
                        "filename": "artifact.bin",
                        "license": "MIT",
                        "sha256": sha256(payload).hexdigest(),
                        "source_url": "https://example.com/artifact",
                    }
                )
            lock = {
                "schema_version": "bgig.external_solver_artifact_lock.v1",
                "created_on": "2026-07-23",
                "candidates": candidates,
                "artifact_count": len(artifacts),
                "artifacts": artifacts,
                "invariants": {
                    "artifacts_embedded_in_repository": False,
                    "download_before_lock_allowed": True,
                    "execution_count_at_lock": 0,
                    "global_install_count": 0,
                    "offline_execution_required": True,
                },
            }
            lock["lock_digest"] = canonical_digest(lock)

            receipt = verify_external_solver_artifacts(
                lock, "candidate-0", root
            )

            self.assertTrue(receipt["verified_before_execution"])
            self.assertEqual(receipt["artifact_count"], 1)


class ExternalSolverAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        self.controls = build_external_adapter_exact_controls()

    def test_controls_are_bgig_cases_complete_for_the_floor_model(self) -> None:
        self.assertEqual(self.controls["case_count"], 3)
        for case in self.controls["cases"]:
            preparation = prepare_external_floor_case(case)
            self.assertEqual(preparation.status, "ready")
            self.assertIsNotNone(preparation.problem)
            self.assertTrue(preparation.problem.complete_for_infeasibility)

    def test_multiple_layer_case_is_unsupported_without_worker(self) -> None:
        case = deepcopy(self.controls["cases"][0])
        case["features"]["layer_target"] = 2

        preparation = prepare_external_floor_case(case)

        self.assertEqual(preparation.status, STATUS_UNSUPPORTED)
        self.assertIn("multiple_layers_required_by_case", preparation.reasons)

    def test_positive_output_is_recertified_and_checkpoint_is_reused(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            worker = _write_fake_worker(root, "feasible")
            runtime = ExternalSolverRuntime(
                candidate_id="ortools_cp_sat",
                command=(sys.executable, str(worker)),
                environment=(),
                scratch_root=str(root / "runs"),
                worker_digest=_sha256_path(worker),
            )
            receipt = _receipt(self.lock, "ortools_cp_sat")
            case = self.controls["cases"][0]

            first = run_external_solver_adapter(
                case,
                "ortools_cp_sat",
                artifact_lock=self.lock,
                artifact_receipt=receipt,
                runtime=runtime,
                limits=ExternalSolverLimits(wall_seconds=5),
            )
            second = run_external_solver_adapter(
                case,
                "ortools_cp_sat",
                artifact_lock=self.lock,
                artifact_receipt=receipt,
                runtime=runtime,
                limits=ExternalSolverLimits(wall_seconds=5),
            )

            self.assertEqual(first.report["status"], STATUS_SOLUTION_FOUND)
            self.assertTrue(first.report["recertification"]["certified"])
            self.assertFalse(first.report["timing"]["checkpoint_reused"])
            self.assertEqual(second.report["status"], STATUS_SOLUTION_FOUND)
            self.assertTrue(second.report["timing"]["checkpoint_reused"])

    def test_exact_and_heuristic_negative_statuses_remain_distinct(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            worker = _write_fake_worker(root, "infeasible")
            case = self.controls["cases"][2]
            exact = run_external_solver_adapter(
                case,
                "highs",
                artifact_lock=self.lock,
                artifact_receipt=_receipt(self.lock, "highs"),
                runtime=ExternalSolverRuntime(
                    candidate_id="highs",
                    command=(sys.executable, str(worker)),
                    environment=(),
                    scratch_root=str(root / "exact"),
                    worker_digest=_sha256_path(worker),
                ),
            )
            heuristic = run_external_solver_adapter(
                case,
                "laff",
                artifact_lock=self.lock,
                artifact_receipt=_receipt(self.lock, "laff"),
                runtime=ExternalSolverRuntime(
                    candidate_id="laff",
                    command=(sys.executable, str(worker)),
                    environment=(),
                    scratch_root=str(root / "heuristic"),
                    worker_digest=_sha256_path(worker),
                ),
            )

            self.assertEqual(exact.report["status"], STATUS_INFEASIBLE_PROVEN)
            self.assertEqual(heuristic.report["status"], STATUS_BOUNDED_UNKNOWN)


def _receipt(lock: dict[str, object], candidate_id: str) -> dict[str, object]:
    artifacts = [
        {
            "artifact_group": item["artifact_group"],
            "byte_count": item["byte_count"],
            "filename": item["filename"],
            "sha256": item["sha256"],
        }
        for item in lock["artifacts"]
        if item["candidate_id"] == candidate_id
    ]
    artifacts.sort(key=lambda item: (item["artifact_group"], item["filename"]))
    receipt = {
        "schema_version": "bgig.external_solver_artifact_receipt.v1",
        "candidate_id": candidate_id,
        "lock_digest": lock["lock_digest"],
        "artifact_count": len(artifacts),
        "bundle_byte_count": sum(item["byte_count"] for item in artifacts),
        "artifacts": artifacts,
        "verified_before_execution": True,
    }
    receipt["bundle_digest"] = canonical_digest(receipt)
    return receipt


def _write_fake_worker(root: Path, status: str) -> Path:
    worker = root / f"fake_{status}.py"
    if status == "feasible":
        body = """
        import base64
        import sys
        from pathlib import Path

        rows = [line.split("\\t") for line in Path(sys.argv[1]).read_text().splitlines()]
        items = [row for row in rows if row[0] == "ITEM"]
        placements = []
        x = 0
        for row in items:
            placements.append(f"PLACEMENT\\t{row[1]}\\t{x}\\t0\\t0")
            x += int(row[2])
        output = [
            "P64L07RESULT\\t1",
            "RESULT\\tfeasible\\t1.0\\tZmFrZS1mZWFzaWJsZQ",
            *placements,
        ]
        Path(sys.argv[2]).write_text("\\n".join(output) + "\\n")
        """
    else:
        body = """
        import sys
        from pathlib import Path

        Path(sys.argv[2]).write_text(
            "P64L07RESULT\\t1\\n"
            "RESULT\\tinfeasible\\t1.0\\tZmFrZS1pbmZlYXNpYmxl\\n"
        )
        """
    worker.write_text(textwrap.dedent(body), encoding="utf-8")
    return worker.resolve()


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
