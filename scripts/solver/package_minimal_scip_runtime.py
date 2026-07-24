"""Package le build SCIP L08J exact pour l'add-in Fusion P64-L08K."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)

SCHEMA = "bgig.scip_product_artifact.v1"
ARCHIVE_NAME = "scip-runtime-cp314.zip"
FIXED_TIMESTAMP = (2026, 7, 24, 0, 0, 0)
WORKERS = (
    ROOT / "scripts" / "solver" / "external_workers" / "scip_real_3d_worker.py",
    ROOT / "scripts" / "solver" / "external_workers" / "_real_3d_worker_common.py",
)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}.")
    return value


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


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


def _write_archive(runtime_root: Path, target: Path) -> None:
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    with zipfile.ZipFile(
        temporary,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for source in sorted(
            (value for value in runtime_root.rglob("*") if value.is_file()),
            key=lambda value: _relative(value, runtime_root).lower(),
        ):
            relative = f"runtime/{_relative(source, runtime_root)}"
            info = zipfile.ZipInfo(relative, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )
    os.replace(temporary, target)


def _assert_workspace_child(path: Path, label: str) -> None:
    try:
        path.resolve().relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError(f"{label} must remain below the BGIG workspace: {path}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--build-evidence", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    runtime_root = args.runtime_root.resolve()
    evidence_path = args.build_evidence.resolve()
    output_root = args.output_root.resolve()
    _assert_workspace_child(runtime_root, "runtime root")
    _assert_workspace_child(output_root, "output root")
    if not runtime_root.is_dir():
        raise RuntimeError(f"Runtime root is missing: {runtime_root}")
    evidence = _read_json(evidence_path)
    supplied_evidence_digest = evidence.pop("evidence_digest", None)
    if supplied_evidence_digest != canonical_digest(evidence):
        raise RuntimeError("L08J evidence digest mismatch.")
    if evidence.get("mission") != "P64-L08J":
        raise RuntimeError("Unexpected build evidence mission.")
    actual_tree = _runtime_tree(runtime_root)
    if actual_tree != evidence.get("runtime_tree"):
        raise RuntimeError(
            f"Runtime tree mismatch: expected={evidence.get('runtime_tree')} actual={actual_tree}"
        )
    output_root.mkdir(parents=True, exist_ok=True)
    worker_root = output_root / "worker"
    worker_root.mkdir(parents=True, exist_ok=True)
    worker_records = []
    for source in WORKERS:
        target = worker_root / source.name
        shutil.copyfile(source, target)
        worker_records.append(
            {
                "path": f"worker/{target.name}",
                "size_bytes": target.stat().st_size,
                "sha256": _sha256(target),
            }
        )
    archive_path = output_root / ARCHIVE_NAME
    _write_archive(runtime_root, archive_path)
    manifest: dict[str, object] = {
        "schema_version": SCHEMA,
        "candidate_id": "scip",
        "version": "10.0.2",
        "pyscipopt_version": "6.2.1",
        "soplex_version": "8.0.2",
        "numpy_version": "2.5.1",
        "python_tag": "cp314",
        "source_build_evidence_digest": supplied_evidence_digest,
        "archive": {
            "path": ARCHIVE_NAME,
            "size_bytes": archive_path.stat().st_size,
            "sha256": _sha256(archive_path),
            "content_root": "runtime",
            "deterministic_timestamp": "2026-07-24T00:00:00Z",
        },
        "runtime_tree": actual_tree,
        "worker_files": worker_records,
        "runtime_contract": {
            "account_required": False,
            "global_install_required": False,
            "network_required": False,
            "service_required": False,
            "telemetry_enabled": False,
            "fusion_cp314_in_process": True,
            "bgig_recertification_required": True,
        },
        "invariants": {
            "holdout_read": False,
            "benchmark_replayed": False,
            "post_holdout_tuning_count": 0,
            "fusion_validated": False,
            "print_validated": False,
        },
    }
    manifest["artifact_digest"] = canonical_digest(manifest)
    (output_root / "ARTIFACT.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "SCIP_PRODUCT_PACKAGE_OK "
        f"archive_bytes={archive_path.stat().st_size} "
        f"archive_sha256={manifest['archive']['sha256']} "
        f"artifact_digest={manifest['artifact_digest']}"
    )


if __name__ == "__main__":
    main()
