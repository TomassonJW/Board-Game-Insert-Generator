"""Audite hors ligne le runtime SCIP retenu par P64-L08F.

Le script ne lance aucun solveur et ne lit aucun corpus. Il inventorie les wheels
Windows déjà acquis, leurs DLL et les avis redistribués, puis compare leur ABI
avec le Python embarqué par l'installation Fusion observée.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable
from zipfile import ZipFile


SCHEMA_VERSION = "bgig.scip_product_gate_evidence.v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WHEEL_TAG_RE = re.compile(r"-(cp\d+t?)-(cp\d+t?)-win_amd64\.whl$")
_FUSION_PYTHON_RE = re.compile(r"python(\d+)\.dll$", re.IGNORECASE)


def _digest_path(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def _wheel_tag(name: str) -> str:
    match = _WHEEL_TAG_RE.search(name)
    if match is None or match.group(1) != match.group(2):
        return "unresolved"
    return match.group(1)


def _fusion_python_tag(path: Path) -> str:
    match = _FUSION_PYTHON_RE.fullmatch(path.name)
    if match is None:
        return "unresolved"
    return f"cp{match.group(1)}"


def _wheel_record(path: Path) -> dict[str, object]:
    with ZipFile(path) as archive:
        files = [entry for entry in archive.infolist() if not entry.is_dir()]
        dll_entries = sorted(
            (entry for entry in files if entry.filename.lower().endswith(".dll")),
            key=lambda entry: entry.filename,
        )
        notice_entries = sorted(
            (
                entry
                for entry in files
                if any(
                    token in Path(entry.filename).name.lower()
                    for token in ("license", "licence", "notice", "copying")
                )
            ),
            key=lambda entry: entry.filename,
        )
        notices: list[dict[str, object]] = []
        notice_texts: list[str] = []
        for entry in notice_entries:
            raw = archive.read(entry)
            notices.append(
                {
                    "path": entry.filename,
                    "size_bytes": entry.file_size,
                    "sha256": sha256(raw).hexdigest(),
                }
            )
            notice_texts.append(raw.decode("utf-8", errors="replace"))
        dlls = []
        for entry in dll_entries:
            raw = archive.read(entry)
            dlls.append(
                {
                    "path": entry.filename,
                    "size_bytes": entry.file_size,
                    "sha256": sha256(raw).hexdigest(),
                }
            )
        return {
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "uncompressed_size_bytes": sum(entry.file_size for entry in files),
            "sha256": _digest_path(path),
            "python_tag": _wheel_tag(path.name),
            "dlls": dlls,
            "notices": notices,
            "notice_text": "\n".join(notice_texts),
        }


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def _component(
    *,
    component_id: str,
    files: list[str],
    version: str,
    license_id: str,
    source: str,
    notice_present: bool,
    exact_version_bound: bool,
    redistribution_terms_bound: bool,
) -> dict[str, object]:
    return {
        "component_id": component_id,
        "files": files,
        "version": version,
        "license": license_id,
        "official_source": source,
        "notice_present_in_wheels": notice_present,
        "exact_version_bound": exact_version_bound,
        "redistribution_terms_bound": redistribution_terms_bound,
        "status": (
            "complete"
            if notice_present and exact_version_bound and redistribution_terms_bound
            else "incomplete"
        ),
    }


def _matching_paths(wheels: Iterable[dict[str, object]], *patterns: str) -> list[str]:
    matches = []
    for wheel in wheels:
        for raw in wheel["dlls"]:
            path = str(raw["path"])
            name = Path(path).name.lower()
            if any(re.search(pattern, name) for pattern in patterns):
                matches.append(path)
    return sorted(matches)


def build_evidence(args: argparse.Namespace) -> dict[str, object]:
    pyscipopt = _wheel_record(args.pyscipopt_wheel.resolve())
    numpy = _wheel_record(args.numpy_wheel.resolve())
    wheels = [pyscipopt, numpy]
    all_notice_text = "\n".join(str(wheel["notice_text"]) for wheel in wheels)
    fusion_tag = _fusion_python_tag(args.fusion_python_dll)
    pyscipopt_tag = str(pyscipopt["python_tag"])

    components = [
        _component(
            component_id="pyscipopt",
            files=[pyscipopt["name"]],
            version="6.2.1",
            license_id="MIT",
            source="https://github.com/scipopt/PySCIPOpt",
            notice_present=_contains_any(all_notice_text, ("MIT License",)),
            exact_version_bound=True,
            redistribution_terms_bound=True,
        ),
        _component(
            component_id="scip",
            files=_matching_paths(wheels, r"^libscip-.*\.dll$"),
            version="10.0.2 reported by the benchmark worker",
            license_id="Apache-2.0",
            source="https://github.com/scipopt/scip/tree/v1002",
            notice_present=_contains_any(all_notice_text, ("Apache License", "Apache-2.0")),
            exact_version_bound=True,
            redistribution_terms_bound=False,
        ),
        _component(
            component_id="ipopt",
            files=_matching_paths(wheels, r"^ipopt-.*\.dll$"),
            version="unresolved in wheel metadata",
            license_id="EPL-2.0",
            source="https://coin-or.github.io/Ipopt/LICENSE.html",
            notice_present=_contains_any(all_notice_text, ("Eclipse Public License", "EPL-2.0")),
            exact_version_bound=False,
            redistribution_terms_bound=False,
        ),
        _component(
            component_id="coinmumps",
            files=_matching_paths(wheels, r"^coinmumps-.*\.dll$"),
            version="unresolved in wheel metadata",
            license_id="CeCILL-C plus component exceptions",
            source="https://mumps-solver.org/index.php?page=dwnld",
            notice_present=_contains_any(all_notice_text, ("CeCILL-C",)),
            exact_version_bound=False,
            redistribution_terms_bound=False,
        ),
        _component(
            component_id="intel_compiler_runtimes",
            files=_matching_paths(
                wheels,
                r"^libifcoremd-.*\.dll$",
                r"^libiomp5md-.*\.dll$",
                r"^libmmd-.*\.dll$",
                r"^svml_dispmd-.*\.dll$",
            ),
            version="mixed or unresolved in wheel metadata",
            license_id="exact binary terms unresolved",
            source=(
                "https://www.intel.com/content/www/us/en/docs/"
                "dpcpp-cpp-compiler/developer-guide-reference/2023-0/"
                "redistribute-libraries-when-deploying-apps.html"
            ),
            notice_present=_contains_any(all_notice_text, ("Intel Simplified Software License",)),
            exact_version_bound=False,
            redistribution_terms_bound=False,
        ),
        _component(
            component_id="microsoft_visual_cpp_runtime",
            files=_matching_paths(wheels, r"^msvcp140-.*\.dll$"),
            version="14.40.33810.0 observed after extraction",
            license_id="Microsoft Software License Terms",
            source=(
                "https://learn.microsoft.com/en-us/cpp/windows/"
                "redistributing-visual-cpp-files?view=msvc-170"
            ),
            notice_present=_contains_any(all_notice_text, ("Microsoft Software License Terms",)),
            exact_version_bound=True,
            redistribution_terms_bound=False,
        ),
        _component(
            component_id="numpy_openblas_lapack_gcc_runtime",
            files=_matching_paths(wheels, r"^libscipy_openblas.*\.dll$"),
            version="NumPy 2.2.6 bundled set",
            license_id="BSD variants and GPL-3.0 with GCC exception",
            source="https://numpy.org/",
            notice_present=_contains_any(
                str(numpy["notice_text"]),
                ("This binary distribution of NumPy also bundles",),
            ),
            exact_version_bound=True,
            redistribution_terms_bound=True,
        ),
    ]
    incomplete = [
        str(component["component_id"])
        for component in components
        if component["status"] != "complete"
    ]
    reasons = []
    if pyscipopt_tag != fusion_tag:
        reasons.append("python_abi_mismatch")
    if any(not component["exact_version_bound"] for component in components):
        reasons.append("native_component_versions_incomplete")
    if any(not component["notice_present_in_wheels"] for component in components):
        reasons.append("third_party_notices_incomplete")
    if any(not component["redistribution_terms_bound"] for component in components):
        reasons.append("redistribution_authority_incomplete")

    for wheel in wheels:
        wheel.pop("notice_text")
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "candidate": {
            "candidate_id": "scip",
            "engine_version": "10.0.2",
            "python_binding": "PySCIPOpt 6.2.1",
            "benchmark_selection_digest": args.selection_digest,
            "benchmark_evidence_digest": args.benchmark_evidence_digest,
        },
        "artifacts": {
            "wheels": wheels,
            "compressed_total_bytes": sum(int(wheel["size_bytes"]) for wheel in wheels),
            "uncompressed_total_bytes": sum(
                int(wheel["uncompressed_size_bytes"]) for wheel in wheels
            ),
        },
        "fusion_runtime_observation": {
            "fusion_version": args.fusion_version,
            "fusion_executable_sha256": _digest_path(args.fusion_exe.resolve()),
            "python_dll": args.fusion_python_dll.name,
            "python_dll_sha256": _digest_path(args.fusion_python_dll.resolve()),
            "python_tag": fusion_tag,
            "candidate_python_tag": pyscipopt_tag,
            "abi_compatible": pyscipopt_tag == fusion_tag,
        },
        "redistribution_audit": {
            "components": components,
            "incomplete_component_ids": incomplete,
            "all_native_versions_bound": all(
                bool(component["exact_version_bound"]) for component in components
            ),
            "all_notices_present": all(
                bool(component["notice_present_in_wheels"]) for component in components
            ),
            "all_redistribution_terms_bound": all(
                bool(component["redistribution_terms_bound"]) for component in components
            ),
        },
        "decision": {
            "product_integration_authorized": not reasons,
            "decision_code": (
                "integrate_scip" if not reasons else "negative_no_product_integrable_winner"
            ),
            "blocking_reasons": reasons,
            "fusion_gate_prepared": False,
            "fusion_gate_installed": False,
        },
        "invariants": {
            "holdout_reopened": False,
            "holdout_worker_invocation_count": 0,
            "post_holdout_tuning_count": 0,
            "benchmark_selection_changed": False,
            "product_runtime_modified": False,
            "fusion_validated": False,
            "print_validated": False,
        },
    }
    payload["evidence_digest"] = _canonical_digest(payload)
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pyscipopt-wheel", type=Path, required=True)
    parser.add_argument("--numpy-wheel", type=Path, required=True)
    parser.add_argument("--fusion-exe", type=Path, required=True)
    parser.add_argument("--fusion-version", required=True)
    parser.add_argument("--fusion-python-dll", type=Path, required=True)
    parser.add_argument("--selection-digest", required=True)
    parser.add_argument("--benchmark-evidence-digest", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    evidence = build_evidence(args)
    if not _SHA256_RE.fullmatch(str(evidence["evidence_digest"])):
        raise RuntimeError("Invalid evidence digest.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "decision": evidence["decision"],
                "evidence_digest": evidence["evidence_digest"],
                "output": str(args.output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
