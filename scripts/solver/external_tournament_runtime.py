"""Support d'exécution locale et isolée du tournoi externe P64-L07D."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter, sleep
from typing import Mapping, Sequence

from board_game_insert_generator.external_solver_adapters import (
    ExternalSolverLimits,
    ExternalSolverRuntime,
    _process_metrics,
)
from board_game_insert_generator.incremental_project_state import canonical_digest


ROOT = Path(__file__).resolve().parents[2]
WORKERS = ROOT / "scripts" / "solver" / "external_workers"


def build_external_runtimes(
    *,
    candidates: Sequence[Mapping[str, object]],
    receipts: Mapping[str, Mapping[str, object]],
    artifact_root: Path,
    environment_root: Path,
    java_home: Path,
    scratch_root: Path,
) -> dict[str, ExternalSolverRuntime]:
    """Construit quatre commandes locales sans installation globale."""

    scratch_root.mkdir(parents=True, exist_ok=True)
    helper = WORKERS / "_floor_worker_protocol.py"
    python_workers = {
        "ortools_cp_sat": WORKERS / "ortools_cp_sat_floor_worker.py",
        "highs": WORKERS / "highs_mip_floor_worker.py",
        "scip": WORKERS / "scip_mip_floor_worker.py",
    }
    runtimes: dict[str, ExternalSolverRuntime] = {}
    for candidate_id, worker in python_workers.items():
        runtimes[candidate_id] = ExternalSolverRuntime(
            candidate_id=candidate_id,
            command=(sys.executable, "-S", str(worker.resolve())),
            environment=(
                (
                    "PYTHONPATH",
                    str(
                        (
                            environment_root
                            / _environment_name(candidate_id)
                        ).resolve()
                    ),
                ),
            ),
            scratch_root=str((scratch_root / "runs").resolve()),
            worker_digest=_combined_digest((helper, worker)),
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
    classpath_for_build = os.pathsep.join(
        str(path.resolve()) for path in laff_jars
    )
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
        raise RuntimeError(
            "External runtime set does not match the locked candidates."
        )
    return runtimes


def run_bgig_baseline_case(
    case: Mapping[str, object],
    *,
    scratch_root: Path,
    limits: ExternalSolverLimits,
) -> dict[str, object]:
    """Mesure la baseline dans un processus séparé et reprenable."""

    worker = WORKERS / "bgig_baseline_worker.py"
    worker_digest = _sha256_path(worker)
    case_id = str(case.get("case_id", ""))
    project_digest = str(case.get("project_digest", ""))
    if not case_id or len(project_digest) != 64:
        raise RuntimeError("BGIG baseline case identity is invalid.")
    input_payload = json.dumps(
        dict(case), sort_keys=True, separators=(",", ":")
    ) + "\n"
    input_digest = sha256(input_payload.encode("utf-8")).hexdigest()
    run_key = (
        f"{_safe_name(case_id)}-{project_digest[:12]}-"
        f"{worker_digest[:12]}-"
        f"{canonical_digest(limits.to_dict())[:12]}"
    )
    run_dir = scratch_root / "baseline" / run_key
    run_dir.mkdir(parents=True, exist_ok=True)
    input_path = run_dir / "input.json"
    output_path = run_dir / "output.json"
    metadata_path = run_dir / "run.json"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    if input_path.exists():
        if input_path.read_text(encoding="utf-8") != input_payload:
            raise RuntimeError("BGIG baseline checkpoint input differs.")
    else:
        input_path.write_text(input_payload, encoding="utf-8")
    if output_path.exists() or metadata_path.exists():
        return _load_baseline_checkpoint(
            output_path,
            metadata_path,
            input_digest=input_digest,
            worker_digest=worker_digest,
        )
    environment = dict(os.environ)
    for key in (
        "ALL_PROXY",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "all_proxy",
        "http_proxy",
        "https_proxy",
    ):
        environment.pop(key, None)
    environment.update(
        {
            "NO_PROXY": "*",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": str((ROOT / "src").resolve()),
        }
    )
    started = perf_counter()
    peak_bytes = 0
    cpu_seconds = 0.0
    termination_reason = None
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            [
                sys.executable,
                "-S",
                str(worker.resolve()),
                str(input_path),
                str(output_path),
            ],
            cwd=str(run_dir),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            shell=False,
        )
        while process.poll() is None:
            elapsed = perf_counter() - started
            current_peak, current_cpu = _process_metrics(process.pid)
            peak_bytes = max(peak_bytes, current_peak or 0)
            cpu_seconds = max(cpu_seconds, current_cpu or 0.0)
            if peak_bytes > limits.memory_mebibytes * 1024 * 1024:
                termination_reason = "memory_limit_exceeded"
                process.terminate()
                break
            if elapsed > limits.wall_seconds:
                termination_reason = "wall_time_limit_exceeded"
                process.terminate()
                break
            sleep(0.02)
        if termination_reason is not None:
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
        exit_code = process.wait()
    total_wall = perf_counter() - started
    execution_status = (
        termination_reason
        or ("completed" if exit_code == 0 else "worker_exit_nonzero")
    )
    raw_report = (
        json.loads(output_path.read_text(encoding="utf-8"))
        if execution_status == "completed" and output_path.is_file()
        else None
    )
    common_report = _common_baseline_report(
        case,
        raw_report,
        execution_status=execution_status,
        total_wall_seconds=total_wall,
        cpu_seconds=cpu_seconds,
        peak_working_set_bytes=peak_bytes,
        checkpoint_reused=False,
        limits=limits,
    )
    if output_path.exists() and raw_report is None:
        output_path.unlink()
    output_path.write_text(
        json.dumps(common_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    metadata: dict[str, object] = {
        "schema_version": "bgig.baseline_worker_checkpoint.v1",
        "execution_status": execution_status,
        "input_digest": input_digest,
        "worker_digest": worker_digest,
        "output_digest": _sha256_path(output_path),
    }
    metadata["metadata_digest"] = canonical_digest(metadata)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return common_report


def _load_baseline_checkpoint(
    output_path: Path,
    metadata_path: Path,
    *,
    input_digest: str,
    worker_digest: str,
) -> dict[str, object]:
    if not output_path.is_file() or not metadata_path.is_file():
        raise RuntimeError("BGIG baseline checkpoint is incomplete.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    supplied = metadata.pop("metadata_digest", None)
    if (
        not isinstance(supplied, str)
        or canonical_digest(metadata) != supplied
        or metadata.get("input_digest") != input_digest
        or metadata.get("worker_digest") != worker_digest
        or metadata.get("output_digest") != _sha256_path(output_path)
    ):
        raise RuntimeError("BGIG baseline checkpoint is invalid.")
    report = json.loads(output_path.read_text(encoding="utf-8"))
    report_without_digest = {
        key: value for key, value in report.items() if key != "report_digest"
    }
    if canonical_digest(report_without_digest) != report.get("report_digest"):
        raise RuntimeError("BGIG baseline report digest mismatch.")
    timing = dict(report["timing"])
    timing["checkpoint_reused"] = True
    report["timing"] = timing
    report["report_digest"] = canonical_digest(
        {key: value for key, value in report.items() if key != "report_digest"}
    )
    return report


def _common_baseline_report(
    case: Mapping[str, object],
    raw_report: Mapping[str, object] | None,
    *,
    execution_status: str,
    total_wall_seconds: float,
    cpu_seconds: float,
    peak_working_set_bytes: int,
    checkpoint_reused: bool,
    limits: ExternalSolverLimits,
) -> dict[str, object]:
    raw = dict(raw_report) if raw_report is not None else {}
    status = (
        str(raw.get("status"))
        if raw_report is not None
        else "bounded_unknown"
    )
    report: dict[str, object] = {
        "schema_version": "bgig.external_tournament_baseline_result.v1",
        "candidate": {
            "candidate_id": "current_bgig",
            "family": "current_product_solver",
            "version": dict(raw.get("adapter", {})).get(
                "version", "current_runtime"
            ),
            "product_gate": "baseline",
        },
        "case": {
            "case_id": str(case["case_id"]),
            "family": str(case.get("family", "historical_regression")),
            "project_digest": str(case["project_digest"]),
            "split": str(case.get("split", "regression")),
        },
        "limits": limits.to_dict(),
        "model": {"kind": "current_bgig_product_contract"},
        "status": status,
        "stop_reason": (
            str(raw.get("stop_reason"))
            if raw_report is not None
            else execution_status
        ),
        "unsupported_constraints": list(
            raw.get("unsupported_constraints", [])
        ),
        "errors": (
            [] if execution_status == "completed" else [execution_status]
        ),
        "timing": {
            "checkpoint_reused": checkpoint_reused,
            "time_to_first_certifiable_seconds": (
                round(total_wall_seconds, 6)
                if status == "solution_found"
                else None
            ),
            "total_wall_seconds": round(total_wall_seconds, 6),
        },
        "resources": {
            "cpu_seconds": round(cpu_seconds, 6),
            "peak_working_set_bytes": peak_working_set_bytes or None,
            "threads_requested": limits.threads,
        },
        "recertification": dict(raw.get("recertification", {})),
        "solution": (
            dict(raw["solution"])
            if isinstance(raw.get("solution"), Mapping)
            else None
        ),
        "raw_report_digest": raw.get("deterministic_digest"),
        "invariants": {
            "worker_invocation_count": 1,
            "external_dependency_count": 0,
            "oracle_payload_consumed_by_adapter": False,
            "product_solver_routing_changed": False,
            "solution_requires_fresh_bgig_certificate": True,
        },
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _environment_name(candidate_id: str) -> str:
    return {
        "ortools_cp_sat": "ortools",
        "highs": "highs",
        "scip": "scip",
    }[candidate_id]


def _combined_digest(paths: Sequence[Path]) -> str:
    digest = sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _safe_name(value: str) -> str:
    return "".join(
        character if character.isalnum() or character in "._-" else "_"
        for character in value
    )
