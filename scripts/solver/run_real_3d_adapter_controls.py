"""Execute les petits controles 3D reels de P64-L08E."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.external_solver_adapters import (  # noqa: E402
    ExternalSolverLimits,
    ExternalSolverRuntime,
)
from board_game_insert_generator.external_solver_artifacts import verify_external_solver_artifacts  # noqa: E402
from board_game_insert_generator.incremental_project_state import canonical_digest  # noqa: E402
from board_game_insert_generator.real_3d_solver_adapters import (  # noqa: E402
    STATUS_BOUNDED_UNKNOWN,
    STATUS_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND,
    STATUS_UNSUPPORTED,
    build_real_3d_exact_controls,
    run_real_3d_adapter,
)

WORKERS = ROOT / "scripts" / "solver" / "external_workers"
LOCK_PATH = ROOT / "tests" / "fixtures" / "p64_l07c_external_solver_artifacts.v1.json"
PACKING_LOCK_PATH = ROOT / "tests" / "fixtures" / "p64_l08e_packingsolver_build_lock.v1.json"


def digest_files(paths: list[Path], binding: str) -> str:
    return canonical_digest(
        {
            "binding": binding,
            "files": [
                {"path": path.name, "sha256": sha256(path.read_bytes()).hexdigest()}
                for path in paths
            ],
        }
    )


def verify_packingsolver_build(binary: Path) -> dict[str, object]:
    lock = json.loads(PACKING_LOCK_PATH.read_text(encoding="utf-8"))
    supplied = lock.pop("lock_digest", None)
    if supplied != canonical_digest(lock):
        raise RuntimeError("PackingSolver build lock digest mismatch.")
    build = lock["build"]
    resolved = binary.resolve()
    if (
        not resolved.is_file()
        or resolved.name != build["binary_filename"]
        or resolved.stat().st_size != build["binary_byte_count"]
        or sha256(resolved.read_bytes()).hexdigest() != build["binary_sha256"]
    ):
        raise RuntimeError("PackingSolver binary does not match its build lock.")
    receipt = {
        "candidate_id": "packingsolver_box",
        "build_lock_digest": supplied,
        "source_commit": lock["source"]["commit"],
        "binary_byte_count": build["binary_byte_count"],
        "binary_sha256": build["binary_sha256"],
        "product_gate": lock["product_gate"],
        "verified_before_execution": True,
    }
    receipt["bundle_digest"] = canonical_digest(receipt)
    return receipt


def build_runtimes(
    artifact_root: Path,
    runtime_root: Path,
    scratch_root: Path,
    packingsolver_binary: Path,
    receipts: dict[str, dict[str, object]],
) -> dict[str, ExternalSolverRuntime]:
    common = WORKERS / "_real_3d_worker_common.py"
    runtimes = {}
    for candidate_id, filename, environment in (
        ("ortools_cp_sat", "ortools_real_3d_worker.py", runtime_root / "ortools"),
        ("scip", "scip_real_3d_worker.py", runtime_root / "scip"),
    ):
        worker = WORKERS / filename
        runtimes[candidate_id] = ExternalSolverRuntime(
            candidate_id=candidate_id,
            command=(sys.executable, "-S", str(worker.resolve())),
            environment=(("PYTHONPATH", str(environment.resolve())),),
            scratch_root=str(scratch_root.resolve()),
            worker_digest=digest_files(
                [common, worker], str(receipts[candidate_id]["bundle_digest"])
            ),
        )
    java_home = next((runtime_root / "jdk17").glob("*"))
    classes = runtime_root / "laff-classes"
    classes.mkdir(parents=True, exist_ok=True)
    jars = [
        artifact_root / "laff" / name
        for name in (
            "api-4.2.1.jar",
            "core-4.2.1.jar",
            "points-4.2.1.jar",
            "eclipse-collections-13.0.0.jar",
            "eclipse-collections-api-13.0.0.jar",
        )
    ]
    classpath_for_build = os.pathsep.join(str(path.resolve()) for path in jars)
    java_source = WORKERS / "LaffReal3DWorker.java"
    subprocess.run(
        [
            str(java_home / "bin" / "javac.exe"),
            "-cp",
            classpath_for_build,
            "-d",
            str(classes.resolve()),
            str(java_source.resolve()),
        ],
        cwd=str(ROOT),
        check=True,
        timeout=120,
    )
    classpath = os.pathsep.join([str(classes.resolve()), *(str(path.resolve()) for path in jars)])
    wrapper = WORKERS / "laff_real_3d_worker.py"
    runtimes["laff"] = ExternalSolverRuntime(
        candidate_id="laff",
        command=(sys.executable, "-S", str(wrapper.resolve())),
        environment=(
            ("BGIG_LAFF_JAVA", str((java_home / "bin" / "java.exe").resolve())),
            ("BGIG_LAFF_CLASSPATH", classpath),
        ),
        scratch_root=str(scratch_root.resolve()),
        worker_digest=digest_files(
            [common, wrapper, java_source], str(receipts["laff"]["bundle_digest"])
        ),
    )
    packing_wrapper = WORKERS / "packingsolver_real_3d_worker.py"
    runtimes["packingsolver_box"] = ExternalSolverRuntime(
        candidate_id="packingsolver_box",
        command=(sys.executable, "-S", str(packing_wrapper.resolve())),
        environment=(("BGIG_PACKINGSOLVER_EXE", str(packingsolver_binary.resolve())),),
        scratch_root=str(scratch_root.resolve()),
        worker_digest=digest_files(
            [common, packing_wrapper], str(receipts["packingsolver_box"]["bundle_digest"])
        ),
    )
    return runtimes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--packingsolver-binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wall-seconds", type=float, default=20.0)
    args = parser.parse_args()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    receipts = {
        candidate_id: verify_external_solver_artifacts(lock, candidate_id, args.artifact_root)
        for candidate_id in ("ortools_cp_sat", "scip", "laff")
    }
    receipts["packingsolver_box"] = verify_packingsolver_build(args.packingsolver_binary)
    runtimes = build_runtimes(
        args.artifact_root,
        args.runtime_root,
        args.scratch_root,
        args.packingsolver_binary,
        receipts,
    )
    limits = ExternalSolverLimits(
        wall_seconds=args.wall_seconds,
        memory_mebibytes=1024,
        threads=1,
        seed=6408,
    )
    records = []
    controls = build_real_3d_exact_controls()
    for candidate_id in ("ortools_cp_sat", "scip", "packingsolver_box", "laff"):
        for control in controls:
            report = run_real_3d_adapter(
                control,
                candidate_id=candidate_id,
                runtime=runtimes[candidate_id],
                limits=limits,
                artifact_receipt=receipts[candidate_id],
                exact_control=True,
            )
            records.append(
                {
                    "candidate_id": candidate_id,
                    "control_id": control["control_id"],
                    "expected": control["expected"],
                    "status": report["status"],
                    "stop_reason": report["stop_reason"],
                    "worker_invocation_count": report["worker_invocation_count"],
                    "unsupported_constraints": report["unsupported_constraints"],
                    "recertification": report["recertification"],
                    "execution": {
                        key: value
                        for key, value in report["execution"].items()
                        if key != "output_path"
                    },
                    "engine": report["engine"],
                    "report_digest": report["report_digest"],
                }
            )
            print(
                f"CONTROL candidate={candidate_id} control={control['control_id']} status={report['status']}"
            )
    for record in records:
        candidate = record["candidate_id"]
        expected = record["expected"]
        if candidate in {"ortools_cp_sat", "scip"}:
            wanted = STATUS_SOLUTION_FOUND if expected == "feasible" else STATUS_INFEASIBLE_PROVEN
            if record["status"] != wanted:
                raise RuntimeError(
                    f"Exact control failed: {candidate}/{record['control_id']} -> {record['status']}"
                )
        elif (
            record["control_id"] == "stacking-feasible"
            and record["status"] != STATUS_SOLUTION_FOUND
        ):
            raise RuntimeError(
                f"Specialized engine did not produce a certified real-3D stack: {candidate}/{record['status']}"
            )
        elif record["control_id"] == "stacking-infeasible" and record["status"] not in {
            STATUS_BOUNDED_UNKNOWN,
            STATUS_SOLUTION_FOUND,
        }:
            raise RuntimeError(
                f"Specialized engine negative honesty failed: {candidate}/{record['status']}"
            )
        elif (
            record["control_id"] not in {"stacking-feasible", "stacking-infeasible"}
            and record["status"] != STATUS_UNSUPPORTED
        ):
            raise RuntimeError(
                f"Specialized engine hid unsupported semantics: {candidate}/{record['control_id']} -> {record['status']}"
            )
    result = {
        "schema_version": "bgig.real_3d_adapter_controls_receipt.v1",
        "candidate_count": 4,
        "candidate_family_count": 4,
        "control_count": len(controls),
        "record_count": len(records),
        "artifact_lock_digest": lock["lock_digest"],
        "packingsolver_build_lock_digest": receipts["packingsolver_box"]["build_lock_digest"],
        "artifact_receipts": receipts,
        "records": records,
        "invariants": {
            "external_engines_executed": 4,
            "real_xyz_output_required": True,
            "positive_witness_transmitted": False,
            "fresh_bgig_recertification_required": True,
            "unsupported_hidden_count": 0,
            "holdout_opened": False,
            "global_install_count": 0,
        },
    }
    result["receipt_digest"] = canonical_digest(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REAL_3D_CONTROLS_OK digest={result['receipt_digest']}")


if __name__ == "__main__":
    main()
