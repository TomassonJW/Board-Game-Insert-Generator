from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest

from board_game_insert_generator.highs_product_solver import (
    HIGHS_PRODUCT_DLL_SHA256,
    HIGHS_PRODUCT_EXECUTABLE_SHA256,
    HIGHS_PRODUCT_SOURCE_ASSET_SHA256,
    HIGHS_PRODUCT_VERSION,
    STATUS_INVALID_RUNTIME,
    STATUS_SOLUTION_FOUND,
    configure_highs_product_runtime,
)
from board_game_insert_generator.minimal_layout_solver import (
    _plan_rank_axes,
    solve_minimal_layout,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = (
    ROOT / "tests" / "fixtures" / "p64_l05d_solver_case_corpus.v1.json"
)
VENDOR_ROOT = (
    ROOT
    / "fusion_addin"
    / "BoardGameInsertGenerator"
    / "vendor"
    / "highs"
    / HIGHS_PRODUCT_VERSION
    / "windows-x86_64"
)
HIGHS_EXE = VENDOR_ROOT / "bin" / "highs.exe"
ARTIFACT_PATH = VENDOR_ROOT / "ARTIFACT.json"


def _case(case_id: str) -> dict[str, object]:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return next(
        value for value in corpus["cases"] if value["case_id"] == case_id
    )


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(
    os.name == "nt" and HIGHS_EXE.is_file(),
    "Le binaire produit HiGHS est cible sur Windows x86_64.",
)
class HighsProductSolverTests(unittest.TestCase):
    def setUp(self) -> None:
        configure_highs_product_runtime(None)
        self.temporary = tempfile.TemporaryDirectory(
            prefix="bgig-highs-product-test-"
        )

    def tearDown(self) -> None:
        configure_highs_product_runtime(None)
        self.temporary.cleanup()

    def _configure_vendor(self) -> None:
        configure_highs_product_runtime(
            HIGHS_EXE,
            scratch_root=self.temporary.name,
        )

    def test_vendored_artifact_is_locked_and_offline(self) -> None:
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(artifact["version"], HIGHS_PRODUCT_VERSION)
        self.assertEqual(
            artifact["source_asset_sha256"],
            HIGHS_PRODUCT_SOURCE_ASSET_SHA256,
        )
        files = {value["path"]: value for value in artifact["files"]}
        self.assertEqual(
            _sha256_path(VENDOR_ROOT / "bin" / "highs.exe"),
            HIGHS_PRODUCT_EXECUTABLE_SHA256,
        )
        self.assertEqual(
            _sha256_path(VENDOR_ROOT / "bin" / "highs.dll"),
            HIGHS_PRODUCT_DLL_SHA256,
        )
        for relative, expected in files.items():
            path = VENDOR_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(path.stat().st_size, expected["byte_count"])
            self.assertEqual(_sha256_path(path), expected["sha256"])
        self.assertEqual(
            artifact["runtime_contract"],
            {
                "account_required": False,
                "global_install_required": False,
                "network_required": False,
                "service_required": False,
                "telemetry_enabled": False,
                "subprocess_isolation": True,
            },
        )

    def test_real_product_lane_wins_after_common_certificate(self) -> None:
        case = _case("multi-cavity-normal")
        baseline = solve_minimal_layout(
            case["project"],
            effort_profile=case["solver_settings"]["effort"],
        )

        self._configure_vendor()
        integrated = solve_minimal_layout(
            case["project"],
            effort_profile=case["solver_settings"]["effort"],
        )

        provenance = integrated["minimal_layout"]["search_provenance"]
        external = provenance["external_lane"]
        self.assertEqual(external["status"], STATUS_SOLUTION_FOUND)
        self.assertEqual(external["invocation_count"], 1)
        self.assertTrue(external["recertification"]["certified"])
        self.assertTrue(external["selected"])
        self.assertEqual(
            provenance["selected"]["candidate_source"],
            "external_highs",
        )
        self.assertLess(
            _plan_rank_axes(integrated),
            _plan_rank_axes(baseline),
        )
        self.assertFalse(integrated["solver"]["deterministic"])
        self.assertEqual(
            external["invariants"]["network_invocation_count"],
            0,
        )

    def test_deep_profile_invokes_highs_once_and_keeps_provenance(self) -> None:
        case = _case("simple-quick")
        self._configure_vendor()

        result = solve_minimal_layout(
            case["project"],
            effort_profile="deep",
        )

        provenance = result["minimal_layout"]["search_provenance"]
        self.assertEqual(
            provenance["external_lane"]["invocation_count"],
            1,
        )
        self.assertTrue(
            provenance["external_lane"]["recertification"]["certified"]
        )
        self.assertIn(
            provenance["selected"]["source_phase"],
            {"normal_incumbent", "deep_extension"},
        )
        self.assertFalse(result["solver"]["deterministic"])

    def test_corrupted_runtime_fails_closed_to_internal_portfolio(self) -> None:
        runtime = Path(self.temporary.name)
        executable = runtime / "highs.exe"
        library = runtime / "highs.dll"
        executable.write_bytes(b"not-highs")
        library.write_bytes(b"not-highs")
        configure_highs_product_runtime(
            executable,
            scratch_root=runtime / "scratch",
        )
        case = _case("simple-quick")

        result = solve_minimal_layout(
            case["project"],
            effort_profile="quick",
        )

        provenance = result["minimal_layout"]["search_provenance"]
        self.assertEqual(
            provenance["external_lane"]["status"],
            STATUS_INVALID_RUNTIME,
        )
        self.assertEqual(
            provenance["external_lane"]["invocation_count"],
            0,
        )
        self.assertNotEqual(
            provenance["selected"]["candidate_source"],
            "external_highs",
        )
        self.assertTrue(result["solver"]["deterministic"])

    def test_fusion_package_declares_every_runtime_file(self) -> None:
        helpers = (
            ROOT / "scripts" / "fusion" / "_fusion_helpers.ps1"
        ).read_text(encoding="utf-8")
        palette = (
            ROOT
            / "fusion_addin"
            / "BoardGameInsertGenerator"
            / "palette_project.py"
        ).read_text(encoding="utf-8")

        for marker in (
            "highs_product_solver.py",
            r"vendor\highs\1.15.1\windows-x86_64\bin\highs.exe",
            r"vendor\highs\1.15.1\windows-x86_64\bin\highs.dll",
            r"vendor\highs\1.15.1\windows-x86_64\ARTIFACT.json",
            r"vendor\highs\1.15.1\windows-x86_64\LICENSE.txt",
            r"vendor\highs\1.15.1\windows-x86_64\THIRD_PARTY_NOTICES.md",
        ):
            self.assertIn(marker, helpers)
        self.assertIn("configure_highs_product_runtime", palette)
        self.assertIn('if os.name == "nt" and installed_engine.is_file()', palette)


if __name__ == "__main__":
    unittest.main()
