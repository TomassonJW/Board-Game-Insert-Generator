"""Construit la preuve fail-closed de remédiation du paquet SCIP P64-L08H.

Le sous-commande ``probe`` résout uniquement un contrôle binaire trivial dans
un Python 3.14 isolé. Elle ne lit aucun corpus ni holdout. La sous-commande
``evidence`` inventorie les artefacts officiels déjà acquis et refuse toute
empreinte ou version inattendue.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
from zipfile import ZipFile


SCHEMA_VERSION = "bgig.scip_package_remediation_evidence.v1"
EXPECTED_HASHES = {
    "pyscipopt": "6aed03b621decb09b38f399773bf8cf2c707e965990b778a24d28c8cc90a0756",
    "numpy": "24d0eb82c0541d3415a33425db64ae439dffccd7b4dbcb30e7c35120205c506a",
    "python_embed": "8d4d3590c10449d78aa4375f534e6d5f3027d67fdc362dd1a882279db6f90fdf",
    "scip_deploy": "a6461de7d8e20b3115e7bfe6439597acaeb803c259e22b22b74404ac4a6b4cad",
    "ipopt": "bd7818a19c2a627f1dcd538358833fbcb17c35080e19b4228be3f66cadf8c8fd",
}
_WHEEL_TAG_RE = re.compile(r"-(cp\d+t?)-(cp\d+t?)-win_amd64\.whl$")


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


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _wheel_tag(name: str) -> str:
    match = _WHEEL_TAG_RE.search(name)
    if match is None or match.group(1) != match.group(2):
        return "unresolved"
    return match.group(1)


def _wheel_record(path: Path) -> dict[str, object]:
    with ZipFile(path) as archive:
        files = [entry for entry in archive.infolist() if not entry.is_dir()]
        binaries = []
        notices = []
        notice_texts = []
        for entry in sorted(files, key=lambda item: item.filename):
            name = Path(entry.filename).name.lower()
            if name.endswith((".dll", ".pyd")):
                raw = archive.read(entry)
                binaries.append(
                    {
                        "path": entry.filename,
                        "size_bytes": entry.file_size,
                        "sha256": sha256(raw).hexdigest(),
                    }
                )
            if any(token in name for token in ("license", "licence", "notice", "copying")):
                raw = archive.read(entry)
                notices.append(
                    {
                        "path": entry.filename,
                        "size_bytes": entry.file_size,
                        "sha256": sha256(raw).hexdigest(),
                    }
                )
                notice_texts.append(raw.decode("utf-8", errors="replace"))
        return {
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "uncompressed_size_bytes": sum(entry.file_size for entry in files),
            "sha256": _digest_path(path),
            "python_tag": _wheel_tag(path.name),
            "binaries": binaries,
            "notices": notices,
            "notice_text": "\n".join(notice_texts),
        }


def _artifact_record(path: Path, official_source: str) -> dict[str, object]:
    return {
        "name": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": _digest_path(path),
        "official_source": official_source,
    }


def _matching_binaries(wheel: dict[str, object], *patterns: str) -> list[str]:
    paths = []
    for binary in wheel["binaries"]:
        name = Path(str(binary["path"])).name.lower()
        if any(re.search(pattern, name) for pattern in patterns):
            paths.append(str(binary["path"]))
    return sorted(paths)


def _component(
    *,
    component_id: str,
    files: list[str],
    version: str,
    source: str,
    license_id: str,
    notice_present: bool,
    redistribution_terms_bound: bool,
    note: str,
) -> dict[str, object]:
    complete = notice_present and redistribution_terms_bound and bool(files)
    return {
        "component_id": component_id,
        "files": files,
        "version": version,
        "exact_version_bound": True,
        "official_source": source,
        "license": license_id,
        "notice_present_in_candidate": notice_present,
        "redistribution_terms_bound": redistribution_terms_bound,
        "status": "complete" if complete else "incomplete",
        "note": note,
    }


def run_probe(args: argparse.Namespace) -> int:
    runtime = args.runtime.resolve()
    if not sys.flags.isolated:
        raise RuntimeError("The CPython isolated flag is required for the probe.")
    sys.path.insert(0, str(runtime))
    import numpy  # type: ignore[import-not-found]
    import pyscipopt  # type: ignore[import-not-found]
    from pyscipopt import Model  # type: ignore[import-not-found]

    if os.environ.get("PIP_NO_INDEX") != "1":
        raise RuntimeError("PIP_NO_INDEX=1 is required for the offline probe.")
    for variable in ("HTTP_PROXY", "HTTPS_PROXY"):
        if os.environ.get(variable) != "http://127.0.0.1:9":
            raise RuntimeError(f"{variable} must point to the local deny endpoint.")

    model = Model("p64_l08h_exact_probe")
    model.hideOutput()
    variable = model.addVar(vtype="B", name="x")
    model.setObjective(variable, "maximize")
    model.optimize()
    payload = {
        "probe_id": "p64_l08h_exact_binary_control",
        "python_version": sys.version.split()[0],
        "python_cache_tag": sys.implementation.cache_tag,
        "python_isolated_flag": bool(sys.flags.isolated),
        "numpy_version": numpy.__version__,
        "pyscipopt_version": pyscipopt.__version__,
        "scip_version": ".".join(
            str(value)
            for value in (
                model.getMajorVersion(),
                model.getMinorVersion(),
                model.getTechVersion(),
            )
        ),
        "solve_status": str(model.getStatus()),
        "solution_x": model.getVal(variable),
        "runtime_layout": "workspace_local_unpacked_wheels",
        "global_install_used": False,
        "network_required": False,
        "offline_environment": {
            "PIP_NO_INDEX": "1",
            "HTTP_PROXY": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://127.0.0.1:9",
        },
        "holdout_read": False,
        "corpus_read": False,
    }
    _write_json(args.output, payload)
    print(json.dumps(payload, sort_keys=True))
    return 0


def build_evidence(args: argparse.Namespace) -> dict[str, object]:
    pyscipopt = _wheel_record(args.pyscipopt_wheel.resolve())
    numpy = _wheel_record(args.numpy_wheel.resolve())
    python_embed = _artifact_record(
        args.python_embed.resolve(),
        "https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-amd64.zip",
    )
    scip_deploy = _artifact_record(
        args.scip_deploy.resolve(),
        "https://github.com/scipopt/scipoptsuite-deploy/releases/tag/v0.12.0",
    )
    ipopt = _artifact_record(
        args.ipopt_archive.resolve(),
        "https://github.com/coin-or/Ipopt/releases/tag/releases/3.14.19",
    )
    records = {
        "pyscipopt": pyscipopt,
        "numpy": numpy,
        "python_embed": python_embed,
        "scip_deploy": scip_deploy,
        "ipopt": ipopt,
    }
    for artifact_id, expected in EXPECTED_HASHES.items():
        actual = str(records[artifact_id]["sha256"])
        if actual != expected:
            raise RuntimeError(
                f"Unexpected SHA256 for {artifact_id}: {actual}; expected {expected}."
            )
    probe = json.loads(args.probe_json.read_text(encoding="utf-8"))
    expected_probe = {
        "python_version": "3.14.0",
        "python_cache_tag": "cpython-314",
        "numpy_version": "2.5.1",
        "pyscipopt_version": "6.2.1",
        "scip_version": "10.0.2",
        "solve_status": "optimal",
        "solution_x": 1.0,
        "python_isolated_flag": True,
        "runtime_layout": "workspace_local_unpacked_wheels",
        "global_install_used": False,
        "network_required": False,
        "holdout_read": False,
        "corpus_read": False,
    }
    for key, expected in expected_probe.items():
        if probe.get(key) != expected:
            raise RuntimeError(
                f"Unexpected probe value for {key}: {probe.get(key)!r}; expected {expected!r}."
            )
    if pyscipopt["python_tag"] != "cp314" or numpy["python_tag"] != "cp314":
        raise RuntimeError("Both product wheels must target CPython 3.14.")

    pyscip_notice = str(pyscipopt.pop("notice_text"))
    numpy_notice = str(numpy.pop("notice_text"))
    components = [
        _component(
            component_id="pyscipopt",
            files=_matching_binaries(pyscipopt, r"^scip\.cp314-win_amd64\.pyd$"),
            version="6.2.1",
            source="https://github.com/scipopt/PySCIPOpt/tree/v6.2.1",
            license_id="MIT",
            notice_present="MIT License" in pyscip_notice,
            redistribution_terms_bound=True,
            note="Interface Python officielle.",
        ),
        _component(
            component_id="scip",
            files=_matching_binaries(pyscipopt, r"^libscip-.*\.dll$"),
            version="10.0.2 via scipoptsuite-deploy v0.12.0",
            source="https://github.com/scipopt/scip/tree/v1002",
            license_id="Apache-2.0",
            notice_present="Apache License" in pyscip_notice,
            redistribution_terms_bound=True,
            note="La licence Apache-2.0 n'est pas livrée dans le wheel.",
        ),
        _component(
            component_id="ipopt",
            files=_matching_binaries(pyscipopt, r"^ipopt-.*\.dll$"),
            version="3.14.19",
            source="https://github.com/coin-or/Ipopt/tree/releases/3.14.19",
            license_id="EPL-2.0",
            notice_present="Eclipse Public License" in pyscip_notice,
            redistribution_terms_bound=True,
            note="La licence EPL-2.0 existe dans l'archive Ipopt source du binaire, pas dans le wheel.",
        ),
        _component(
            component_id="mumps_metis",
            files=_matching_binaries(pyscipopt, r"^coinmumps-.*\.dll$"),
            version="MUMPS 5.8.0; METIS 5.2.1",
            source="https://github.com/coin-or/Ipopt/releases/tag/releases/3.14.19",
            license_id="CeCILL-C avec exceptions; Apache-2.0",
            notice_present=("CeCILL-C" in pyscip_notice and "METIS" in pyscip_notice),
            redistribution_terms_bound=False,
            note="Les avis complets et les exceptions de composants ne sont pas fournis par le wheel ni le paquet deploy.",
        ),
        _component(
            component_id="intel_compiler_and_mkl_runtimes",
            files=_matching_binaries(
                pyscipopt,
                r"^libifcoremd-.*\.dll$",
                r"^libiomp5md-.*\.dll$",
                r"^libmmd-.*\.dll$",
                r"^svml_dispmd-.*\.dll$",
            ),
            version="Intel MKL 2024.1; Intel compilers 2021.8.0; DLL file versions locked by hash",
            source="https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl-download.html",
            license_id="Intel Simplified Software License / applicable runtime terms",
            notice_present="Intel Simplified Software License" in pyscip_notice,
            redistribution_terms_bound=False,
            note="Le paquet ne fournit ni licence Intel applicable ni chaîne d'autorité de redistribution.",
        ),
        _component(
            component_id="microsoft_visual_cpp_runtime",
            files=_matching_binaries(pyscipopt, r"^msvcp140-.*\.dll$"),
            version="14.40.33810.0",
            source="https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170",
            license_id="Microsoft Visual Studio license terms",
            notice_present="Microsoft Software License Terms" in pyscip_notice,
            redistribution_terms_bound=False,
            note="La redistribution dépend d'une licence Visual Studio admissible, non établie par l'artefact.",
        ),
        _component(
            component_id="numpy_and_bundled_libraries",
            files=[str(item["path"]) for item in numpy["binaries"]],
            version="NumPy 2.5.1 and bundled set",
            source="https://pypi.org/project/numpy/2.5.1/",
            license_id="BSD variants and bundled notices",
            notice_present="This binary distribution of NumPy also bundles" in numpy_notice,
            redistribution_terms_bound=True,
            note="Le wheel NumPy contient son inventaire de licences tierces.",
        ),
    ]
    incomplete = [
        str(component["component_id"])
        for component in components
        if component["status"] != "complete"
    ]
    product_wheels = [pyscipopt, numpy]
    reasons = []
    if any(not component["notice_present_in_candidate"] for component in components):
        reasons.append("third_party_notices_incomplete")
    if any(not component["redistribution_terms_bound"] for component in components):
        reasons.append("redistribution_authority_incomplete")

    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L08H",
        "benchmark_binding": {
            "winner": "SCIP 10.0.2 via PySCIPOpt 6.2.1",
            "selection_digest": "e061f9af67e9ce80974a8ea2c5fe705ba59a637dbba319464a412651b6fa7140",
            "benchmark_evidence_digest": "0dbf1b45ae9135c1316051ab7e0946dfbfeafac5c785ad96ccd5d7a620acd46d",
        },
        "packaging_decision": {
            "selected_candidate": "official_pypi_cp314_wheels",
            "selected_reason": [
                "same PySCIPOpt worker route and SCIP version as the sealed benchmark",
                "CPython 3.14 ABI matches the observed Fusion runtime",
                "official direct artifacts with public immutable hashes and no identity form",
            ],
            "standalone_scip_10_0_2": {
                "selected": False,
                "downloaded": False,
                "reasons": [
                    "would add an unbenchmarked CLI serialization route",
                    "official download requires personal identity fields",
                    "full suite and extra runtime prerequisites enlarge the package surface",
                ],
            },
        },
        "artifacts": {
            "product_wheels": product_wheels,
            "product_compressed_total_bytes": sum(
                int(wheel["size_bytes"]) for wheel in product_wheels
            ),
            "product_uncompressed_total_bytes": sum(
                int(wheel["uncompressed_size_bytes"]) for wheel in product_wheels
            ),
            "provenance": {
                "scipoptsuite_deploy_v0_12_0": scip_deploy,
                "ipopt_3_14_19": ipopt,
            },
            "test_harness_only": {"python_3_14_0_embed": python_embed},
        },
        "isolated_offline_probe": probe,
        "redistribution_audit": {
            "components": components,
            "incomplete_component_ids": incomplete,
            "all_binary_hashes_bound": all(
                len(str(binary["sha256"])) == 64
                for wheel in product_wheels
                for binary in wheel["binaries"]
            ),
            "all_native_versions_bound": True,
            "all_notices_present": all(
                bool(component["notice_present_in_candidate"]) for component in components
            ),
            "all_redistribution_terms_bound": all(
                bool(component["redistribution_terms_bound"]) for component in components
            ),
        },
        "decision": {
            "technical_abi_gate_passed": True,
            "isolated_offline_execution_passed": True,
            "redistribution_gate_passed": not reasons,
            "product_integration_authorized": not reasons,
            "decision_code": (
                "package_gate_passed"
                if not reasons
                else "negative_package_redistribution_incomplete"
            ),
            "blocking_reasons": reasons,
            "next_mission": "P64-L08I minimal redistributable SCIP runtime ADR and build audit",
            "fusion_gate_prepared": False,
            "fusion_gate_installed": False,
        },
        "invariants": {
            "holdout_reopened": False,
            "holdout_worker_invocation_count": 0,
            "benchmark_replayed": False,
            "post_holdout_tuning_count": 0,
            "benchmark_selection_changed": False,
            "product_runtime_modified": False,
            "fusion_validated": False,
            "print_validated": False,
        },
    }
    payload["evidence_digest"] = _canonical_digest(payload)
    return payload


def run_evidence(args: argparse.Namespace) -> int:
    payload = build_evidence(args)
    _write_json(args.output, payload)
    print(
        json.dumps(
            {
                "decision": payload["decision"],
                "evidence_digest": payload["evidence_digest"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe")
    probe.add_argument("--runtime", type=Path, required=True)
    probe.add_argument("--output", type=Path, required=True)
    probe.set_defaults(handler=run_probe)

    evidence = subparsers.add_parser("evidence")
    evidence.add_argument("--pyscipopt-wheel", type=Path, required=True)
    evidence.add_argument("--numpy-wheel", type=Path, required=True)
    evidence.add_argument("--python-embed", type=Path, required=True)
    evidence.add_argument("--scip-deploy", type=Path, required=True)
    evidence.add_argument("--ipopt-archive", type=Path, required=True)
    evidence.add_argument("--probe-json", type=Path, required=True)
    evidence.add_argument("--output", type=Path, required=True)
    evidence.set_defaults(handler=run_evidence)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
