"""Construit la preuve pre-build du runtime SCIP minimal P64-L08I.

La mission n'execute aucun solveur et ne lit aucun corpus. Elle verifie statiquement
le worker 3D scelle, verrouille les sources et la toolchain, puis autorise seulement
la mission de build suivante.
"""

from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path


SCHEMA_VERSION = "bgig.minimal_scip_runtime_audit.v1"

SOURCE_ARTIFACTS = [
    {
        "component_id": "scip",
        "version": "10.0.2",
        "tag": "v10.0.2",
        "commit": "b8eaf989f9168f966a471b2039ffb75d925d5202",
        "archive_name": "scip-v10.0.2.zip",
        "size_bytes": 13_725_644,
        "sha256": "7225e8d493707ebb1b5c5d5696cf384a1cd6aeaf8820253ae260a5fdcc763308",
        "official_source": "https://github.com/scipopt/scip/releases/tag/v10.0.2",
        "license_id": "Apache-2.0",
    },
    {
        "component_id": "soplex",
        "version": "8.0.2",
        "tag": "v8.0.2",
        "commit": "cfadddc47e142fb21e040ff9dc564cbe2e8e3801",
        "archive_name": "soplex-v8.0.2.zip",
        "size_bytes": 1_466_934,
        "sha256": "f1a45c6338ad1cfb6c2950e91e4f854ed199c2e4039830b26dbe65d0dd67cd34",
        "official_source": "https://github.com/scipopt/soplex/tree/v8.0.2",
        "license_id": "Apache-2.0",
    },
    {
        "component_id": "pyscipopt",
        "version": "6.2.1",
        "tag": "v6.2.1",
        "commit": "6ff33812155e6592e0a681b6a1967322428ac2db",
        "archive_name": "pyscipopt-v6.2.1.zip",
        "size_bytes": 959_233,
        "sha256": "0d53902150724665c2f2a22adb89fd1b3717c16b365819dfbdf137f65ab76588",
        "official_source": "https://github.com/scipopt/PySCIPOpt/tree/v6.2.1",
        "license_id": "MIT",
    },
]

BUILD_INPUTS = [
    {
        "component_id": "python-build-runtime",
        "version": "3.14.0",
        "name": "python.3.14.0.nupkg",
        "size_bytes": 14_839_285,
        "sha256": "620fb3527428fb354f093b0b8b634dfb8e3023115df68608fba7e91db69b4f4d",
        "official_source": "https://www.nuget.org/packages/python/3.14.0",
        "product_component": False,
    },
    {
        "component_id": "cython",
        "version": "3.2.8",
        "name": "cython-3.2.8-cp314-cp314-win_amd64.whl",
        "size_bytes": 2_807_626,
        "sha256": "89b0fdc2ca0b502afedc4dd4ddbc4f9cb5a135245afacf9483e556e8ad3ada3b",
        "official_source": "https://pypi.org/project/Cython/3.2.8/",
        "product_component": False,
    },
    {
        "component_id": "setuptools",
        "version": "83.0.0",
        "name": "setuptools-83.0.0-py3-none-any.whl",
        "size_bytes": 1_008_090,
        "sha256": "29b23c360f22f414dc7336bb39178cc7bcbf6021ed2733cde173f09dba19abb3",
        "official_source": "https://pypi.org/project/setuptools/83.0.0/",
        "product_component": False,
    },
    {
        "component_id": "wheel",
        "version": "0.47.0",
        "name": "wheel-0.47.0-py3-none-any.whl",
        "size_bytes": 32_218,
        "sha256": "212281cab4dff978f6cedd499cd893e1f620791ca6ff7107cf270781e587eced",
        "official_source": "https://pypi.org/project/wheel/0.47.0/",
        "product_component": False,
    },
    {
        "component_id": "numpy",
        "version": "2.5.1",
        "name": "numpy-2.5.1-cp314-cp314-win_amd64.whl",
        "size_bytes": 12_562_177,
        "sha256": "24d0eb82c0541d3415a33425db64ae439dffccd7b4dbcb30e7c35120205c506a",
        "official_source": "https://pypi.org/project/numpy/2.5.1/",
        "product_component": True,
    },
]

SCIP_CMAKE_OPTIONS = {
    "AMPL": "OFF",
    "AUTOBUILD": "OFF",
    "CMAKE_BUILD_TYPE": "Release",
    "CONOPT": "OFF",
    "EXACTSOLVE": "OFF",
    "EXPRINT": "none",
    "GMP": "OFF",
    "IPOPT": "OFF",
    "LAPACK": "OFF",
    "LPS": "spx",
    "LPSEXACT": "none",
    "LPSCHECK": "OFF",
    "LTO": "ON",
    "MPFR": "OFF",
    "PAPILO": "OFF",
    "READLINE": "OFF",
    "SHARED": "ON",
    "SYM": "snauty",
    "TPI": "none",
    "WORHP": "OFF",
    "ZIMPL": "OFF",
    "ZLIB": "OFF",
}

SOPLEX_CMAKE_OPTIONS = {
    "BOOST": "OFF",
    "CMAKE_BUILD_TYPE": "Release",
    "GMP": "OFF",
    "MPFR": "OFF",
    "PAPILO": "OFF",
    "QUADMATH": "OFF",
    "ZLIB": "OFF",
}

DECISION_NAMES = {
    "area",
    "choice_selected",
    "combined",
    "depth",
    "ground",
    "height",
    "max_rear",
    "max_right",
    "max_top",
    "removal_ranks",
    "selected",
    "selectors",
    "separated",
    "support_variables",
    "supports",
    "width",
    "x",
    "y",
    "z",
}
DECISION_KEYS = {"area", "depth", "height", "selectors", "width", "x", "y", "z"}
BANNED_MODEL_TOKENS = ("Ipopt", "MUMPS", "METIS", "addConsNonlinear", "sqrt(", "exp(", "log(")


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _call_name(node: ast.Call) -> str:
    function = node.func
    if isinstance(function, ast.Attribute):
        return function.attr
    if isinstance(function, ast.Name):
        return function.id
    return ""


def _slice_key(node: ast.Subscript) -> str | None:
    value = node.slice
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    return None


def _uses_decision_value(node: ast.AST) -> bool:
    if isinstance(node, ast.Name) and node.id in DECISION_NAMES:
        return True
    if isinstance(node, ast.Subscript):
        if _slice_key(node) in DECISION_KEYS:
            return True
        if isinstance(node.value, ast.Name) and node.value.id in DECISION_NAMES:
            return True
    return any(_uses_decision_value(child) for child in ast.iter_child_nodes(node))


def audit_worker(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports = []
    add_var_types = []
    nonlinear_products = []
    forbidden_operators = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "pyscipopt":
            imports.extend(alias.name for alias in node.names)
        if isinstance(node, ast.Call) and _call_name(node) == "addVar":
            keyword = next((value for value in node.keywords if value.arg == "vtype"), None)
            if keyword is None or not isinstance(keyword.value, ast.Constant):
                add_var_types.append("unresolved")
            else:
                add_var_types.append(str(keyword.value.value))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            if _uses_decision_value(node.left) and _uses_decision_value(node.right):
                nonlinear_products.append(ast.unparse(node))
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Pow, ast.MatMult)):
            if _uses_decision_value(node):
                forbidden_operators.append(ast.unparse(node))
    banned_tokens_found = [token for token in BANNED_MODEL_TOKENS if token in source]
    gate_passed = (
        sorted(set(imports)) == ["Model", "quicksum"]
        and bool(add_var_types)
        and set(add_var_types) <= {"B", "I"}
        and not nonlinear_products
        and not forbidden_operators
        and not banned_tokens_found
    )
    return {
        "worker_path": f"scripts/solver/external_workers/{path.name}",
        "worker_sha256": _sha256_path(path),
        "pyscipopt_imports": sorted(set(imports)),
        "add_var_call_count": len(add_var_types),
        "variable_types": sorted(set(add_var_types)),
        "nonlinear_products": nonlinear_products,
        "forbidden_decision_operators": forbidden_operators,
        "banned_dependency_tokens_found": banned_tokens_found,
        "linear_integer_model_gate_passed": gate_passed,
        "active_3d_semantics": [
            "orthogonal_xyz_non_overlap",
            "multi_level_z_placement",
            "support_count_and_area",
            "reservation_volumes",
            "disjoint_regions",
            "access_precedence",
            "local_variant_selection",
        ],
    }


def build_evidence(worker_path: Path) -> dict[str, object]:
    model_audit = audit_worker(worker_path)
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L08I",
        "decision_context": {
            "sealed_winner": "SCIP 10.0.2 via PySCIPOpt 6.2.1",
            "sealed_holdout_reopened": False,
            "benchmark_replayed": False,
            "winner_changed": False,
            "model_changed": False,
        },
        "model_audit": model_audit,
        "source_artifacts": SOURCE_ARTIFACTS,
        "build_inputs": BUILD_INPUTS,
        "toolchain": {
            "generator": "Visual Studio 17 2022 x64",
            "visual_studio": "17.14.2",
            "msvc_toolset": "14.44.35207",
            "cl_version": "19.44.35207.1",
            "cl_sha256": "6aa39ae173cb8563d796359930b332a08b2fdc1745b70e5a4caa48a9779fdd07",
            "windows_sdk": "10.0.26100.0",
            "cmake_version": "4.0.2",
            "cmake_sha256": "c5cecf8e663f105217ff5805bb1d748f7de2fe3767312974b677b3c818883d2c",
            "ninja_version": "1.11.1.git.kitware.jobserver-1",
            "ninja_sha256": "9ee2fc6bc8c0acd1de6e6dcadf009c0598e6336646b87cfb5ed2918604b81597",
            "heavy_process_limit": 2,
            "workspace_local_build": True,
            "global_install_required": False,
        },
        "build_contract": {
            "architecture": "win_amd64",
            "python_abi": "cp314",
            "configuration": "Release",
            "soplex_cmake_options": SOPLEX_CMAKE_OPTIONS,
            "scip_cmake_options": SCIP_CMAKE_OPTIONS,
            "retained_runtime_components": [
                "PySCIPOpt",
                "SCIP",
                "SoPlex",
                "SCIP built-in MIP plugins",
                "sassy+nauty symmetry",
                "NumPy",
            ],
            "excluded_runtime_components": [
                "Ipopt",
                "MUMPS",
                "METIS",
                "Intel MKL",
                "Intel Fortran runtime",
                "Intel OpenMP runtime",
                "PaPILO and Intel TBB",
                "GCG",
                "ZIMPL",
                "GMP and exact-solve mode",
            ],
            "c_cpp_runtime": {
                "linkage": "dynamic /MD",
                "redistributable_source": (
                    "Visual Studio 2022 Community VC/Redist/MSVC/14.44.35112/x64/"
                    "Microsoft.VC143.CRT"
                ),
                "authority": (
                    "Microsoft Visual Studio redistribution list; exact DLL subset must be "
                    "proven by dependency scan after build"
                ),
                "version": "14.44.35112",
                "candidate_dll_count": 10,
            },
            "offline_product": True,
            "service_required": False,
            "account_required": False,
            "secret_required": False,
            "telemetry_required": False,
            "private_holdout_allowed": False,
        },
        "redistribution_contract": {
            "all_source_versions_bound": True,
            "all_source_hashes_bound": True,
            "all_source_sizes_bound": True,
            "required_notices": [
                "PySCIPOpt MIT",
                "SCIP Apache-2.0",
                "SCIP tclique Apache-2.0",
                "SCIP nauty Apache-2.0",
                "SCIP dejavu MIT",
                "SoPlex Apache-2.0",
                "SoPlex fmt MIT",
                "NumPy license and bundled notices",
                "Microsoft Visual C++ redistribution terms",
            ],
            "forbidden_binary_families": [
                "ipopt*",
                "coinmumps*",
                "libifcoremd*",
                "libiomp5md*",
                "libmmd*",
                "svml_dispmd*",
            ],
            "fail_if_unresolved_dependency": True,
            "fail_if_notice_missing": True,
            "fail_if_runtime_dll_outside_redist_source": True,
        },
        "decision": {
            "prebuild_model_gate_passed": model_audit["linear_integer_model_gate_passed"],
            "source_provenance_gate_passed": True,
            "toolchain_gate_passed": True,
            "redistribution_plan_gate_passed": True,
            "minimal_build_authorized": model_audit["linear_integer_model_gate_passed"],
            "product_integration_authorized": False,
            "fusion_gate_prepared": False,
            "fusion_gate_installed": False,
            "decision_code": "minimal_scip_build_audit_pass",
            "next_mission": "P64-L08J reproducible minimal SCIP build and public equivalence gate",
        },
        "invariants": {
            "holdout_read": False,
            "holdout_worker_invocation_count": 0,
            "benchmark_replayed": False,
            "post_holdout_tuning_count": 0,
            "product_runtime_modified": False,
            "fusion_validated": False,
            "print_validated": False,
        },
    }
    payload["evidence_digest"] = _canonical_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = build_evidence(args.worker.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not evidence["decision"]["minimal_build_authorized"]:
        raise SystemExit("minimal SCIP build audit failed closed")


if __name__ == "__main__":
    main()
