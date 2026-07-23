"""Exécute les contrôles réels P64-L07C dans quatre environnements isolés."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from board_game_insert_generator.external_solver_adapters import (
    ExternalSolverLimits,
    ExternalSolverRuntime,
    STATUS_BOUNDED_UNKNOWN,
    STATUS_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND,
    build_external_adapter_exact_controls,
    run_external_solver_adapter,
)
from board_game_insert_generator.external_solver_artifacts import (
    external_solver_candidate_catalog,
    validate_external_solver_artifact_lock,
    verify_external_solver_artifacts,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[2]
WORKERS = ROOT / "scripts" / "solver" / "external_workers"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-lock", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--environment-root", type=Path, required=True)
    parser.add_argument("--java-home", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wall-seconds", type=float, default=10.0)
    args = parser.parse_args()

    lock = validate_external_solver_artifact_lock(
        json.loads(args.artifact_lock.read_text(encoding="utf-8"))
    )
    candidates = external_solver_candidate_catalog(lock)
    receipts = {
        candidate["candidate_id"]: verify_external_solver_artifacts(
            lock, str(candidate["candidate_id"]), args.artifact_root
        )
        for candidate in candidates
    }
    runtimes = _build_runtimes(
        candidates=candidates,
        receipts=receipts,
        artifact_root=args.artifact_root.resolve(),
        environment_root=args.environment_root.resolve(),
        java_home=args.java_home.resolve(),
        scratch_root=args.scratch_root.resolve(),
    )
    controls = build_external_adapter_exact_controls()
    limits = ExternalSolverLimits(
        wall_seconds=args.wall_seconds,
        memory_mebibytes=1024,
        threads=1,
        seed=640_707,
    )
    results = []
    failed = []
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        for case in controls["cases"]:
            execution = run_external_solver_adapter(
                case,
                candidate_id,
                artifact_lock=lock,
                artifact_receipt=receipts[candidate_id],
                runtime=runtimes[candidate_id],
                limits=limits,
            )
            truth = str(case["exact_truth"])
            expected = (
                STATUS_SOLUTION_FOUND
                if truth == "feasible"
                else (
                    STATUS_INFEASIBLE_PROVEN
                    if bool(candidate["exact_for_floor_model"])
                    else STATUS_BOUNDED_UNKNOWN
                )
            )
            passed = execution.report["status"] == expected
            if not passed:
                failed.append(
                    {
                        "candidate_id": candidate_id,
                        "case_id": case["case_id"],
                        "expected_status": expected,
                        "observed_status": execution.report["status"],
                    }
                )
            results.append(
                {
                    "candidate_id": candidate_id,
                    "case_id": case["case_id"],
                    "exact_truth": truth,
                    "expected_status": expected,
                    "passed": passed,
                    "report": execution.report,
                }
            )
            print(
                f"{candidate_id} {case['case_id']} "
                f"{execution.report['status']} "
                f"{'OK' if passed else 'KO'}",
                flush=True,
            )
    payload = {
        "schema_version": "bgig.external_adapter_control_campaign.v1",
        "artifact_lock_digest": lock["lock_digest"],
        "controls_digest": controls["controls_digest"],
        "candidate_count": len(candidates),
        "family_count": len({item["family"] for item in candidates}),
        "limits": limits.to_dict(),
        "results": results,
        "summary": {
            "expected_result_count": len(candidates) * controls["case_count"],
            "failed": failed,
            "failed_count": len(failed),
            "passed_count": len(results) - len(failed),
            "result_count": len(results),
            "status": "passed" if not failed else "failed",
        },
        "invariants": {
            "global_install_count": 0,
            "heavy_processes_run_concurrently": 1,
            "holdout_case_count": 0,
            "network_service_invocation_count": 0,
            "product_solver_routing_changed": False,
        },
    }
    payload["campaign_digest"] = canonical_digest(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"CONTROL_GATE={payload['summary']['status']} "
        f"DIGEST={payload['campaign_digest']}",
        flush=True,
    )
    return 0 if not failed else 1


def _build_runtimes(
    *,
    candidates,
    receipts,
    artifact_root: Path,
    environment_root: Path,
    java_home: Path,
    scratch_root: Path,
) -> dict[str, ExternalSolverRuntime]:
    scratch_root.mkdir(parents=True, exist_ok=True)
    helper = WORKERS / "_floor_worker_protocol.py"
    python_workers = {
        "ortools_cp_sat": WORKERS / "ortools_cp_sat_floor_worker.py",
        "highs": WORKERS / "highs_mip_floor_worker.py",
        "scip": WORKERS / "scip_mip_floor_worker.py",
    }
    runtimes: dict[str, ExternalSolverRuntime] = {}
    for candidate_id, worker in python_workers.items():
        digest = _combined_digest((helper, worker))
        runtimes[candidate_id] = ExternalSolverRuntime(
            candidate_id=candidate_id,
            command=(sys.executable, "-S", str(worker.resolve())),
            environment=(
                (
                    "PYTHONPATH",
                    str((environment_root / _environment_name(candidate_id)).resolve()),
                ),
            ),
            scratch_root=str((scratch_root / "runs").resolve()),
            worker_digest=digest,
        )
    laff_source = WORKERS / "LaffFloorWorker.java"
    classes = scratch_root / "runtime" / "laff-classes"
    classes.mkdir(parents=True, exist_ok=True)
    laff_jars = [
        artifact_root / "laff" / name
        for name in (
            "api-4.2.1.jar",
            "core-4.2.1.jar",
            "points-4.2.1.jar",
            "eclipse-collections-13.0.0.jar",
            "eclipse-collections-api-13.0.0.jar",
        )
    ]
    classpath_for_build = os.pathsep.join(str(path.resolve()) for path in laff_jars)
    javac = java_home / "bin" / "javac.exe"
    java = java_home / "bin" / "java.exe"
    subprocess.run(
        [
            str(javac),
            "-cp",
            classpath_for_build,
            "-d",
            str(classes.resolve()),
            str(laff_source.resolve()),
        ],
        cwd=str(ROOT),
        check=True,
        timeout=120,
    )
    classpath = os.pathsep.join(
        [str(classes.resolve()), *(str(path.resolve()) for path in laff_jars)]
    )
    laff_digest = canonical_digest(
        {
            "source_sha256": _sha256_path(laff_source),
            "artifact_bundle_digest": receipts["laff"]["bundle_digest"],
            "java_runtime": "Temurin-17.0.19+10",
        }
    )
    runtimes["laff"] = ExternalSolverRuntime(
        candidate_id="laff",
        command=(str(java), "-cp", classpath, "LaffFloorWorker"),
        environment=(),
        scratch_root=str((scratch_root / "runs").resolve()),
        worker_digest=laff_digest,
    )
    expected = {str(item["candidate_id"]) for item in candidates}
    if set(runtimes) != expected:
        raise RuntimeError("Runtime set does not match the locked candidates.")
    return runtimes


def _environment_name(candidate_id: str) -> str:
    return {
        "ortools_cp_sat": "ortools",
        "highs": "highs",
        "scip": "scip",
    }[candidate_id]


def _combined_digest(paths: tuple[Path, ...]) -> str:
    digest = sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
