"""Qualifie le runtime SCIP minimal construit pour P64-L08J."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.external_solver_adapters import (  # noqa: E402
    ExternalSolverLimits,
    ExternalSolverRuntime,
)
from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from board_game_insert_generator.real_3d_solver_adapters import (  # noqa: E402
    STATUS_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND,
    build_real_3d_exact_controls,
    run_real_3d_adapter,
)
from board_game_insert_generator.real_3d_solver_corpus import (  # noqa: E402
    materialize_case_problem,
    validate_public_manifest,
)
from board_game_insert_generator.real_3d_solver_tournament import (  # noqa: E402
    build_result_row,
    materialize_tournament_problem,
)

SCHEMA = "bgig.minimal_scip_runtime_build_receipt.v1"
L08I_LOCK = ROOT / "tests" / "fixtures" / "p64_l08i_minimal_scip_runtime_audit.v1.json"
L08E_BASELINE = ROOT / "tests" / "fixtures" / "p64_l08e_real_3d_adapter_controls_receipt.v1.json"
L08D_MANIFEST = ROOT / "tests" / "fixtures" / "p64_l08d_real_3d_corpus.v1.json"
WORKER = ROOT / "scripts" / "solver" / "external_workers" / "scip_real_3d_worker.py"
COMMON_WORKER = ROOT / "scripts" / "solver" / "external_workers" / "_real_3d_worker_common.py"
FORBIDDEN_PREFIXES = (
    "ipopt",
    "coinmumps",
    "metis",
    "libifcoremd",
    "libiomp5md",
    "libmmd",
    "svml",
    "papilo",
    "tbb",
)
SYSTEM_DLLS = {
    "advapi32.dll",
    "bcrypt.dll",
    "crypt32.dll",
    "gdi32.dll",
    "kernel32.dll",
    "ole32.dll",
    "oleaut32.dll",
    "shell32.dll",
    "user32.dll",
    "ws2_32.dll",
}


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}.")
    return value


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _parse_cache(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line:
            continue
        key_and_type, value = line.split("=", 1)
        key = key_and_type.split(":", 1)[0]
        values[key] = value
    return values


def _verify_locked_inputs(
    lock: Mapping[str, object], artifact_root: Path
) -> list[dict[str, object]]:
    records = []
    entries = [*lock["source_artifacts"], *lock["build_inputs"]]
    for raw in entries:
        entry = dict(raw)
        name = str(entry.get("archive_name") or entry.get("name"))
        path = artifact_root / name
        if not path.is_file():
            raise RuntimeError(f"Missing locked input {name}.")
        size = path.stat().st_size
        digest = _sha256(path)
        if size != entry["size_bytes"] or digest != entry["sha256"]:
            raise RuntimeError(f"Locked input mismatch for {name}.")
        records.append({"name": name, "size_bytes": size, "sha256": digest})
    return records


def _verify_cmake_contract(
    lock: Mapping[str, object], soplex_cache_path: Path, scip_cache_path: Path
) -> dict[str, object]:
    soplex = _parse_cache(soplex_cache_path)
    scip = _parse_cache(scip_cache_path)
    mismatches = []
    for name, expected in lock["build_contract"]["soplex_cmake_options"].items():
        if name == "CMAKE_BUILD_TYPE":
            continue
        if soplex.get(name) != expected:
            mismatches.append(f"SoPlex {name}={soplex.get(name)!r}, expected {expected!r}")
    for name, expected in lock["build_contract"]["scip_cmake_options"].items():
        if name == "CMAKE_BUILD_TYPE":
            continue
        if scip.get(name) != expected:
            mismatches.append(f"SCIP {name}={scip.get(name)!r}, expected {expected!r}")
    for label, cache in (("SoPlex", soplex), ("SCIP", scip)):
        expected = {
            "CMAKE_GENERATOR": "Visual Studio 17 2022",
            "CMAKE_GENERATOR_PLATFORM": "x64",
            "CMAKE_GENERATOR_TOOLSET": "v143,version=14.44",
            "CMAKE_MSVC_RUNTIME_LIBRARY": "MultiThreadedDLL",
        }
        for name, value in expected.items():
            if cache.get(name) != value:
                mismatches.append(f"{label} {name}={cache.get(name)!r}, expected {value!r}")
    if mismatches:
        raise RuntimeError("CMake contract mismatch: " + "; ".join(mismatches))
    project_path = scip_cache_path.parent / "src" / "libscip.vcxproj"
    project_text = project_path.read_text(encoding="utf-8-sig")
    if (
        "<WindowsTargetPlatformVersion>10.0.26100.0</WindowsTargetPlatformVersion>"
        not in project_text
    ):
        raise RuntimeError("SCIP project does not target Windows SDK 10.0.26100.0.")
    if "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>" not in project_text:
        raise RuntimeError("SCIP project does not use the dynamic /MD runtime.")
    if "<WholeProgramOptimization>true</WholeProgramOptimization>" not in project_text:
        raise RuntimeError("SCIP LTO evidence is missing from the generated project.")
    return {
        "soplex_cache_sha256": _sha256(soplex_cache_path),
        "scip_cache_sha256": _sha256(scip_cache_path),
        "generator": scip["CMAKE_GENERATOR"],
        "platform": scip["CMAKE_GENERATOR_PLATFORM"],
        "toolset": scip["CMAKE_GENERATOR_TOOLSET"],
        "windows_sdk": "10.0.26100.0",
        "runtime_library": "MultiThreadedDLL (/MD)",
        "configuration": "Release",
        "lto": True,
        "soplex_options": {
            key: soplex[key]
            for key in lock["build_contract"]["soplex_cmake_options"]
            if key != "CMAKE_BUILD_TYPE"
        },
        "scip_options": {
            key: scip[key]
            for key in lock["build_contract"]["scip_cmake_options"]
            if key != "CMAKE_BUILD_TYPE"
        },
    }


def _dumpbin_dependencies(dumpbin: Path, binary: Path) -> list[str]:
    completed = subprocess.run(
        [str(dumpbin), "/dependents", str(binary)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=60,
    )
    dependencies = []
    active = False
    for raw in completed.stdout.splitlines():
        line = raw.strip()
        if line == "Image has the following dependencies:":
            active = True
            continue
        if active and line == "Summary":
            break
        if active and line.lower().endswith(".dll"):
            dependencies.append(line)
    return sorted(set(dependencies), key=str.lower)


def _is_forbidden_binary_name(value: str) -> bool:
    name = Path(value).name.lower()
    return name.startswith(FORBIDDEN_PREFIXES)


def _classify_dependency(name: str, local_names: Mapping[str, str]) -> tuple[str, str | None]:
    lowered = name.lower()
    if lowered in local_names:
        return "runtime_local", local_names[lowered]
    if lowered == "python314.dll":
        return "python_host", None
    if lowered.startswith(("api-ms-win-", "ext-ms-win-")) or lowered in SYSTEM_DLLS:
        return "windows_system", None
    return "unresolved", None


def _verify_binary_inventory(
    runtime_root: Path, dumpbin: Path, redist_root: Path
) -> tuple[list[dict[str, object]], dict[str, object]]:
    binaries = sorted(
        (
            path
            for path in runtime_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".dll", ".pyd"}
        ),
        key=lambda path: _relative(path, runtime_root).lower(),
    )
    local_names = {path.name.lower(): _relative(path, runtime_root) for path in binaries}
    inventory = []
    unresolved = []
    forbidden = []
    for binary in binaries:
        relative = _relative(binary, runtime_root)
        dependencies = []
        for name in _dumpbin_dependencies(dumpbin, binary):
            classification, resolved_path = _classify_dependency(name, local_names)
            dependencies.append(
                {"name": name, "classification": classification, "resolved_path": resolved_path}
            )
            if classification == "unresolved":
                unresolved.append(f"{relative}->{name}")
            if _is_forbidden_binary_name(name):
                forbidden.append(f"{relative}->{name}")
        if _is_forbidden_binary_name(relative):
            forbidden.append(relative)
        inventory.append(
            {
                "path": relative,
                "size_bytes": binary.stat().st_size,
                "sha256": _sha256(binary),
                "dependencies": dependencies,
            }
        )
    microsoft_sources = {
        "site-packages/pyscipopt/msvcp140.dll": redist_root / "msvcp140.dll",
        "site-packages/pyscipopt/vcruntime140.dll": redist_root / "vcruntime140.dll",
        "site-packages/pyscipopt/vcruntime140_1.dll": redist_root / "vcruntime140_1.dll",
    }
    numpy_msvcp = list((runtime_root / "site-packages" / "numpy.libs").glob("msvcp140-*.dll"))
    if len(numpy_msvcp) != 1:
        raise RuntimeError("Expected exactly one NumPy-private msvcp140 DLL.")
    microsoft_sources[_relative(numpy_msvcp[0], runtime_root)] = redist_root / "msvcp140.dll"
    microsoft_provenance = []
    for relative, source in microsoft_sources.items():
        destination = runtime_root / Path(relative)
        if (
            not destination.is_file()
            or not source.is_file()
            or _sha256(destination) != _sha256(source)
        ):
            raise RuntimeError(f"Microsoft runtime provenance mismatch for {relative}.")
        microsoft_provenance.append(
            {
                "path": relative,
                "source_path": f"VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT/{source.name}",
                "source_sha256": _sha256(source),
                "size_bytes": source.stat().st_size,
            }
        )
    microsoft_like = [
        item["path"]
        for item in inventory
        if "msvcp" in str(item["path"]).lower() or "vcruntime" in str(item["path"]).lower()
    ]
    if sorted(microsoft_like) != sorted(microsoft_sources):
        raise RuntimeError("A Microsoft runtime DLL has no VC/Redist provenance.")
    if unresolved or forbidden:
        raise RuntimeError(
            f"Native dependency gate failed: unresolved={unresolved}, forbidden={forbidden}"
        )
    return inventory, {
        "binary_count": len(inventory),
        "dll_count": sum(item["path"].lower().endswith(".dll") for item in inventory),
        "pyd_count": sum(item["path"].lower().endswith(".pyd") for item in inventory),
        "unresolved_dependency_count": 0,
        "forbidden_binary_count": 0,
        "microsoft_provenance": microsoft_provenance,
        "all_microsoft_runtime_from_vc_redist": True,
    }


def _runtime_tree(runtime_root: Path) -> dict[str, object]:
    records = []
    for path in sorted(
        (value for value in runtime_root.rglob("*") if value.is_file()),
        key=lambda value: _relative(value, runtime_root).lower(),
    ):
        records.append(
            {
                "path": _relative(path, runtime_root),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return {
        "file_count": len(records),
        "size_bytes": sum(int(item["size_bytes"]) for item in records),
        "tree_digest": canonical_digest({"files": records}),
    }


def _notice_inventory(runtime_root: Path) -> list[dict[str, object]]:
    notice_root = runtime_root / "notices"
    required = {
        "PySCIPOpt-MIT.txt",
        "SCIP/LICENSE",
        "SCIP/tclique/LICENSE",
        "SCIP/nauty/COPYRIGHT",
        "SCIP/dejavu/LICENSE",
        "SoPlex/LICENSE",
        "SoPlex/fmt/LICENSE.rst",
        "NumPy/LICENSE.txt",
        "Microsoft-Visual-Cpp-Runtime.txt",
    }
    inventory = [
        {
            "path": _relative(path, notice_root),
            "size_bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(
            (value for value in notice_root.rglob("*") if value.is_file()),
            key=lambda value: _relative(value, notice_root).lower(),
        )
    ]
    actual = {str(item["path"]) for item in inventory}
    missing = sorted(required - actual)
    if missing:
        raise RuntimeError(f"Missing required runtime notices: {missing}")
    return inventory


def _probe_runtime(python_executable: Path, site_packages: Path) -> dict[str, object]:
    code = (
        "import json,numpy,pyscipopt; from pyscipopt import Model; "
        "m=Model('p64_l08j_exact'); m.hideOutput(True); "
        "x=m.addVar('x',vtype='I',lb=0,ub=4); y=m.addVar('y',vtype='B'); "
        "m.addCons(2*x+y<=5); m.setObjective(3*x+y,'maximize'); m.optimize(); "
        "r={'python_abi':'cp314','numpy_version':numpy.__version__,'pyscipopt_version':pyscipopt.__version__,"
        "'scip_version':f'{m.getMajorVersion()}.{m.getMinorVersion()}.{m.getTechVersion()}',"
        "'status':str(m.getStatus()),'objective':m.getObjVal(),'x':m.getVal(x),'y':m.getVal(y)}; print(json.dumps(r,sort_keys=True))"
    )
    env = os.environ.copy()
    env.update(
        {"PYTHONPATH": str(site_packages), "PYTHONDONTWRITEBYTECODE": "1", "PIP_NO_INDEX": "1"}
    )
    completed = subprocess.run(
        [str(python_executable), "-S", "-c", code],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=True,
        timeout=60,
    )
    result = json.loads(completed.stdout.strip())
    expected = {
        "python_abi": "cp314",
        "numpy_version": "2.5.1",
        "pyscipopt_version": "6.2.1",
        "scip_version": "10.0.2",
        "status": "optimal",
        "objective": 7.0,
        "x": 2.0,
        "y": 1.0,
    }
    if result != expected:
        raise RuntimeError(f"Minimal runtime exact probe mismatch: {result!r}")
    return result


def _public_equivalence(
    python_executable: Path, site_packages: Path, scratch_root: Path, runtime_digest: str
) -> dict[str, object]:
    baseline = _read_json(L08E_BASELINE)
    baseline_records = {
        record["control_id"]: record
        for record in baseline["records"]
        if record["candidate_id"] == "scip"
    }
    worker_digest = canonical_digest(
        {
            "binding": runtime_digest,
            "files": [
                {"path": path.name, "sha256": _sha256(path)} for path in (COMMON_WORKER, WORKER)
            ],
        }
    )
    runtime = ExternalSolverRuntime(
        candidate_id="scip",
        command=(str(python_executable), "-S", str(WORKER)),
        environment=(("PYTHONDONTWRITEBYTECODE", "1"), ("PYTHONPATH", str(site_packages))),
        scratch_root=str(scratch_root),
        worker_digest=worker_digest,
    )
    limits = ExternalSolverLimits(wall_seconds=20.0, memory_mebibytes=1024, threads=1, seed=6408)
    artifact_receipt = {"bundle_digest": runtime_digest}
    records = []
    baseline_ms = 0.0
    candidate_ms = 0.0
    for control in build_real_3d_exact_controls():
        report = run_real_3d_adapter(
            control,
            candidate_id="scip",
            runtime=runtime,
            limits=limits,
            artifact_receipt=artifact_receipt,
            exact_control=True,
        )
        reference = baseline_records[str(control["control_id"])]
        engine = report["engine"]
        wanted = (
            STATUS_SOLUTION_FOUND if control["expected"] == "feasible" else STATUS_INFEASIBLE_PROVEN
        )
        if report["status"] != wanted or report["status"] != reference["status"]:
            raise RuntimeError(
                f"Public exact control status regression for {control['control_id']}."
            )
        if engine.get("proof_status") != reference["engine"].get("proof_status") or engine.get(
            "objective_value"
        ) != reference["engine"].get("objective_value"):
            raise RuntimeError(
                f"Public exact control proof regression for {control['control_id']}."
            )
        if report["recertification"]["certified"] != reference["recertification"]["certified"]:
            raise RuntimeError(
                f"Public exact control certificate regression for {control['control_id']}."
            )
        base_time = float(reference["engine"]["solve_milliseconds"])
        new_time = float(engine["solve_milliseconds"])
        baseline_ms += base_time
        candidate_ms += new_time
        records.append(
            {
                "control_id": control["control_id"],
                "expected": control["expected"],
                "baseline_status": reference["status"],
                "candidate_status": report["status"],
                "objective_value": engine.get("objective_value"),
                "proof_status": engine.get("proof_status"),
                "recertified": report["recertification"]["certified"],
                "baseline_solve_milliseconds": base_time,
                "candidate_solve_milliseconds": new_time,
            }
        )
    threshold_ms = max(baseline_ms * 2.0, baseline_ms + 20.0)
    if candidate_ms > threshold_ms:
        raise RuntimeError("Material public exact-control performance regression.")
    manifest = validate_public_manifest(_read_json(L08D_MANIFEST))
    record = next(
        value for value in manifest["open_case_records"] if value["split"] == "regression"
    )
    problem = materialize_tournament_problem(record) or materialize_case_problem(record)
    regression_runtime = ExternalSolverRuntime(
        candidate_id="scip",
        command=runtime.command,
        environment=tuple(sorted((*runtime.environment, ("BGIG_REAL3D_PROFILE", "balanced")))),
        scratch_root=runtime.scratch_root,
        worker_digest=runtime.worker_digest,
    )
    regression_report = run_real_3d_adapter(
        problem,
        candidate_id="scip",
        runtime=regression_runtime,
        limits=ExternalSolverLimits(wall_seconds=30.0, memory_mebibytes=1024, threads=1, seed=6408),
        artifact_receipt=artifact_receipt,
        exact_control=False,
    )
    regression_row = build_result_row(
        record,
        candidate_id="scip",
        report=regression_report,
        stage="regression-reference",
        trial_id="regression-reference",
    )
    if (
        regression_row["status"] != "unsupported"
        or regression_row["unsupported_constraints"] != ["incomplete_real_3d_problem"]
        or regression_row["worker_invocation_count"] != 0
    ):
        raise RuntimeError("Open regression honesty changed.")
    return {
        "tournament_baseline_receipt_digest": baseline["receipt_digest"],
        "exact_control_count": len(records),
        "exact_controls": records,
        "performance": {
            "baseline_total_solve_milliseconds": round(baseline_ms, 4),
            "candidate_total_solve_milliseconds": round(candidate_ms, 4),
            "material_regression_threshold_milliseconds": round(threshold_ms, 4),
            "material_regression": False,
        },
        "open_regression": {
            "case_id": regression_row["case_id"],
            "status": regression_row["status"],
            "truth_pass": regression_row["truth_pass"],
            "unsupported_constraints": regression_row["unsupported_constraints"],
            "worker_invocation_count": regression_row["worker_invocation_count"],
        },
        "semantic_loss_count": 0,
        "solution_loss_count": 0,
        "certificate_loss_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--soplex-cache", type=Path, required=True)
    parser.add_argument("--scip-cache", type=Path, required=True)
    parser.add_argument("--python-executable", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--dumpbin", type=Path, required=True)
    parser.add_argument("--vc-redist-root", type=Path, required=True)
    parser.add_argument("--built-wheel", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name in (
        "artifact_root",
        "soplex_cache",
        "scip_cache",
        "python_executable",
        "runtime_root",
        "dumpbin",
        "vc_redist_root",
        "built_wheel",
        "scratch_root",
        "output",
    ):
        setattr(args, name, getattr(args, name).resolve())
    lock = _read_json(L08I_LOCK)
    supplied = lock.pop("evidence_digest")
    if canonical_digest(lock) != supplied:
        raise RuntimeError("P64-L08I lock digest mismatch.")
    locked_inputs = _verify_locked_inputs(lock, args.artifact_root)
    cmake_contract = _verify_cmake_contract(lock, args.soplex_cache, args.scip_cache)
    runtime_tree = _runtime_tree(args.runtime_root)
    inventory, dependency_gate = _verify_binary_inventory(
        args.runtime_root, args.dumpbin, args.vc_redist_root
    )
    notices = _notice_inventory(args.runtime_root)
    probe = _probe_runtime(args.python_executable, args.runtime_root / "site-packages")
    equivalence = _public_equivalence(
        args.python_executable,
        args.runtime_root / "site-packages",
        args.scratch_root,
        str(runtime_tree["tree_digest"]),
    )
    wheel_record = {
        "name": args.built_wheel.name,
        "size_bytes": args.built_wheel.stat().st_size,
        "sha256": _sha256(args.built_wheel),
    }
    result = {
        "schema_version": SCHEMA,
        "mission": "P64-L08J",
        "l08i_evidence_digest": supplied,
        "locked_inputs": locked_inputs,
        "cmake_contract": cmake_contract,
        "built_wheel": wheel_record,
        "runtime_tree": runtime_tree,
        "binary_inventory": inventory,
        "dependency_gate": dependency_gate,
        "notice_inventory": notices,
        "exact_probe": probe,
        "public_equivalence": equivalence,
        "decision": {
            "minimal_runtime_build_passed": True,
            "public_equivalence_passed": True,
            "product_integration_authorized": True,
            "decision_code": "minimal_scip_runtime_build_and_public_equivalence_pass",
            "next_mission": "P64-L08K BGIG product integration and full regression",
        },
        "invariants": {
            "holdout_read": False,
            "holdout_worker_invocation_count": 0,
            "benchmark_replayed": False,
            "post_holdout_tuning_count": 0,
            "global_install_count": 0,
            "network_service_count": 0,
            "product_runtime_modified": False,
            "fusion_validated": False,
            "print_validated": False,
        },
    }
    result["evidence_digest"] = canonical_digest(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "MINIMAL_SCIP_RUNTIME_OK "
        f"binaries={dependency_gate['binary_count']} "
        f"bytes={runtime_tree['size_bytes']} "
        f"digest={result['evidence_digest']}"
    )


if __name__ == "__main__":
    main()
