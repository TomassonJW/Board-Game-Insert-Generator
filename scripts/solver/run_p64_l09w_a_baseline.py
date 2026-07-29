#!/usr/bin/env python3
"""Baseline 0.1.80 sur les seules fixtures solveur déjà versionnées.

Le runner classe d'abord les sources historiques. Il n'exécute jamais une
recette dont les digests ne sont plus reconstructibles avec le contrat
courant. Les résultats produit et les problèmes 3D de cœur restent séparés.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import ctypes
from hashlib import sha256
import json
from math import ceil
import os
from pathlib import Path
import sys
from threading import Event, Thread
from time import perf_counter, process_time
from typing import Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.contextual_local_analysis import (  # noqa: E402
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.external_solver_adapters import (  # noqa: E402
    ExternalSolverLimits,
    ExternalSolverRuntime,
)
from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from board_game_insert_generator.partition_cad import build_partition_cad  # noqa: E402
from board_game_insert_generator.project_v1 import normalize_project_draft  # noqa: E402
from board_game_insert_generator.real_3d_solver_adapters import (  # noqa: E402
    STATUS_BOUNDED_UNKNOWN as CORE_BOUNDED_UNKNOWN,
    STATUS_INFEASIBLE_PROVEN as CORE_INFEASIBLE_PROVEN,
    STATUS_SOLUTION_FOUND as CORE_SOLUTION_FOUND,
    STATUS_UNSUPPORTED as CORE_UNSUPPORTED,
    run_real_3d_adapter,
)
from board_game_insert_generator.real_3d_solver_corpus import (  # noqa: E402
    materialize_case_problem,
    validate_public_manifest,
)
from board_game_insert_generator.real_3d_solver_tournament import (  # noqa: E402
    materialize_tournament_problem,
)
from board_game_insert_generator.scip_product_solver import (  # noqa: E402
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    configure_scip_product_runtime,
)
from board_game_insert_generator.solver_benchmark_adapters import (  # noqa: E402
    recertify_minimal_layout_plan,
)
from board_game_insert_generator.solver_benchmark_corpus import (  # noqa: E402
    _materialize_recipe,
    _validate_recipe,
)
from board_game_insert_generator.staged_calculation import (  # noqa: E402
    ARTIFACT_KIND_FINALIZED,
    StagedCalculationSession,
)


SCHEMA_VERSION = "bgig.p64_l09w_a_fixture_baseline.v1"
CHECKPOINT_SCHEMA_VERSION = "bgig.p64_l09w_a_fixture_checkpoint.v1"
FIXTURES = ROOT / "tests" / "fixtures"
CORE_WORKER = ROOT / "scripts" / "solver" / "external_workers" / "bgig_real_3d_worker.py"
_DIGEST_FIELDS = (
    "project_digest",
    "previous_project_digest",
    "oracle_digest",
    "features",
)
_RESULT_CERTIFIED = "certified_solution"
_RESULT_PROVEN_IMPOSSIBLE = "proven_impossible"
_RESULT_BOUNDED_UNKNOWN = "bounded_unknown"
_RESULT_UNSUPPORTED = "unsupported"
_RESULT_ERROR = "error"
_SOLVER_SOLUTION_FOUND = "solution_found"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain one JSON object.")
    return value


def _write_json_atomic(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _code_bundle_digest() -> str:
    digest = sha256()
    paths = [
        *sorted((ROOT / "src" / "board_game_insert_generator").glob("*.py")),
        Path(__file__).resolve(),
        CORE_WORKER,
    ]
    for path in paths:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _rebuild_generated_case(raw: Mapping[str, object]) -> dict[str, object]:
    recipe = _validate_recipe(raw["recipe"])
    rebuilt = _materialize_recipe(
        case_id=str(raw["case_id"]),
        split=str(raw["split"]),
        family=str(raw["family"]),
        seed=int(raw["seed"]),
        recipe=recipe,
    )
    current_project = normalize_project_draft(rebuilt["project"]).project
    rebuilt["project"] = current_project
    rebuilt["project_digest"] = canonical_digest(current_project)
    previous_project = rebuilt.get("previous_project")
    if previous_project is not None:
        current_previous = normalize_project_draft(previous_project).project
        rebuilt["previous_project"] = current_previous
        rebuilt["previous_project_digest"] = canonical_digest(
            current_previous
        )
    return {
        "case_id": str(raw["case_id"]),
        "split": str(raw["split"]),
        "family": str(raw["family"]),
        "seed": int(raw["seed"]),
        "recipe": recipe,
        "solver_settings": deepcopy(dict(raw["solver_settings"])),
        **rebuilt,
    }


def _derived_features(
    project: Mapping[str, object],
    features: Mapping[str, object],
) -> dict[str, object]:
    result = deepcopy(dict(features))
    groups = project.get("container_groups", [])
    contents = project.get("contents", [])
    flat_items = project.get("flat_items", [])
    if isinstance(groups, list):
        result.setdefault("container_group_count", len(groups))
    if isinstance(contents, list):
        result.setdefault("content_count", len(contents))
        counts = Counter(
            str(value.get("container_group_id"))
            for value in contents
            if isinstance(value, Mapping)
        )
        if counts:
            result.setdefault(
                "contents_per_container_maximum", max(counts.values())
            )
            result.setdefault(
                "contents_per_container_minimum", min(counts.values())
            )
    if isinstance(flat_items, list):
        result["flat_item_count"] = len(flat_items)
    return result


def build_fixture_inventory() -> dict[str, object]:
    """Reconstruit la gate de vérité et le planning sans lancer le solveur."""

    l05 = _read_json(FIXTURES / "p64_l05d_solver_case_corpus.v1.json")
    l06 = _read_json(FIXTURES / "p64_l06_solver_benchmark.v1.json")
    l07 = _read_json(FIXTURES / "p64_l07b_solver_benchmark.v2.json")
    l08 = validate_public_manifest(
        _read_json(FIXTURES / "p64_l08d_real_3d_corpus.v1.json")
    )

    classifications: list[dict[str, object]] = []
    product_cases: list[dict[str, object]] = []
    for raw_value in l05["cases"]:
        raw = dict(raw_value)
        project = normalize_project_draft(raw["project"]).project
        effective_digest = canonical_digest(project)
        reconstructible = effective_digest == raw["project_digest"]
        classifications.append(
            {
                "source": "L05",
                "case_id": raw["case_id"],
                "fixture_class": (
                    "current-reconstructible"
                    if reconstructible
                    else "historical-semantic-drift"
                ),
                "changed_fields": (
                    [] if reconstructible else ["project_digest"]
                ),
            }
        )
        if reconstructible:
            product_cases.append(
                {
                    "baseline_case_id": f"L05:{raw['case_id']}",
                    "source": "L05",
                    "source_case_id": raw["case_id"],
                    "source_split": "regression",
                    "family": "historical-regression",
                    "project": project,
                    "project_digest": effective_digest,
                    "previous_project": None,
                    "features": _derived_features(
                        project,
                        {
                            "density_target": "historical",
                            "execution_mode": "cold",
                            "change_kind": "none",
                            "layer_target": "historical",
                            "reservation_mode": "historical",
                            "rotation_policy_target": "permitted",
                        },
                    ),
                    "solver_settings": deepcopy(dict(raw["solver_settings"])),
                    "expected": "historical",
                    "expectations": deepcopy(dict(raw["expectations"])),
                }
            )

    generated_candidates: list[dict[str, object]] = []
    for source, manifest, key in (
        ("L07", l07, "bgig_generated_cases"),
        ("L06", l06, "generated_cases"),
    ):
        for raw_value in manifest[key]:
            raw = dict(raw_value)
            rebuilt = _rebuild_generated_case(raw)
            changed = [
                field
                for field in _DIGEST_FIELDS
                if raw.get(field) != rebuilt.get(field)
            ]
            classifications.append(
                {
                    "source": source,
                    "case_id": raw["case_id"],
                    "fixture_class": (
                        "current-reconstructible"
                        if not changed
                        else "historical-semantic-drift"
                    ),
                    "changed_fields": changed,
                    "reservation_mode": raw["features"]["reservation_mode"],
                    "source_split": raw["split"],
                }
            )
            if changed:
                continue
            expected = str(rebuilt["oracle"]["expected_truth"])
            generated_candidates.append(
                {
                    "baseline_case_id": f"{source}:{raw['case_id']}",
                    "source": source,
                    "source_case_id": raw["case_id"],
                    "source_split": raw["split"],
                    "family": raw["family"],
                    "project": rebuilt["project"],
                    "project_digest": rebuilt["project_digest"],
                    "previous_project": rebuilt["previous_project"],
                    "features": _derived_features(
                        rebuilt["project"], rebuilt["features"]
                    ),
                    "solver_settings": deepcopy(dict(raw["solver_settings"])),
                    "expected": expected,
                    "oracle_digest": rebuilt["oracle_digest"],
                    "rotation_relaxed_for_positive": bool(
                        expected == "feasible"
                        and rebuilt["features"]["rotation_policy_target"]
                        == "forbidden_by_benchmark"
                    ),
                    "negative_rotation_proof_supported": bool(
                        expected != "impossible"
                        or rebuilt["features"]["rotation_policy_target"]
                        == "permitted"
                    ),
                }
            )

    by_project_digest: dict[str, dict[str, object]] = {}
    duplicate_count = 0
    for case in generated_candidates:
        digest = str(case["project_digest"])
        if digest in by_project_digest:
            duplicate_count += 1
            continue
        by_project_digest[digest] = case
    product_cases.extend(by_project_digest.values())
    product_cases.sort(key=lambda value: str(value["baseline_case_id"]))

    core_cases = [
        {
            "baseline_case_id": f"L08:{value['case_id']}",
            "source": "L08",
            "source_case_id": value["case_id"],
            "source_split": value["split"],
            "family": value["family"],
            "tier": value["tier"],
            "expected": value["expected"],
            "record": deepcopy(value),
        }
        for value in l08["open_case_records"]
    ]
    core_cases.sort(key=lambda value: str(value["baseline_case_id"]))

    class_counts = Counter(
        str(value["fixture_class"]) for value in classifications
    )
    drift_by_source = Counter(
        str(value["source"])
        for value in classifications
        if value["fixture_class"] == "historical-semantic-drift"
    )
    drift_by_reservation = Counter(
        str(value.get("reservation_mode", "historical"))
        for value in classifications
        if value["fixture_class"] == "historical-semantic-drift"
    )
    product_expected = Counter(str(value["expected"]) for value in product_cases)
    inventory = {
        "schema_version": "bgig.p64_l09w_a_fixture_inventory.v1",
        "bindings": {
            "l05_corpus_digest": l05["corpus_digest"],
            "l06_manifest_digest": l06["manifest_digest"],
            "l07_manifest_digest": l07["manifest_digest"],
            "l08_manifest_digest": l08["manifest_digest"],
        },
        "class_counts": dict(sorted(class_counts.items())),
        "drift_by_source": dict(sorted(drift_by_source.items())),
        "drift_by_reservation_mode": dict(
            sorted(drift_by_reservation.items())
        ),
        "drift_samples": [
            deepcopy(value)
            for value in classifications
            if value["fixture_class"] == "historical-semantic-drift"
        ][:12],
        "generated_current_duplicate_count": duplicate_count,
        "product_case_count": len(product_cases),
        "product_expected_counts": dict(sorted(product_expected.items())),
        "core_only_case_count": len(core_cases),
        "core_only_expected_counts": dict(
            sorted(
                Counter(str(value["expected"]) for value in core_cases).items()
            )
        ),
        "invariants": {
            "historical_manifests_rewritten": False,
            "semantic_drift_executed": False,
            "l08_counted_as_product_path": False,
            "old_holdout_counted_as_new_holdout": False,
        },
    }
    inventory["inventory_digest"] = canonical_digest(inventory)
    return {
        "inventory": inventory,
        "product_cases": product_cases,
        "core_cases": core_cases,
    }


class _WorkingSetSampler:
    def __init__(self, interval_seconds: float = 0.05) -> None:
        self.interval_seconds = interval_seconds
        self.method = "not_available"
        self.peak_bytes: int | None = None
        self._stop = Event()
        self._thread: Thread | None = None
        self._reader = self._build_reader()

    def _build_reader(self) -> Callable[[], int | None] | None:
        if os.name != "nt":
            return None

        class ProcessMemoryCountersEx(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        counters_type = ProcessMemoryCountersEx
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        process_id = os.getpid()

        def read() -> int | None:
            handle = kernel32.OpenProcess(
                0x1000 | 0x0400, False, process_id
            )
            if not handle:
                return None
            try:
                counters = counters_type()
                counters.cb = ctypes.sizeof(counters)
                if not psapi.GetProcessMemoryInfo(
                    handle, ctypes.byref(counters), counters.cb
                ):
                    return None
                return int(counters.WorkingSetSize)
            finally:
                kernel32.CloseHandle(handle)

        self.method = "windows_get_process_memory_info_working_set_50ms"
        return read

    def __enter__(self) -> "_WorkingSetSampler":
        if self._reader is None:
            return self
        self._sample()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, _kind, _value, _traceback) -> None:
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=1.0)
        self._sample()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            self._sample()

    def _sample(self) -> None:
        if self._reader is None:
            return
        try:
            value = self._reader()
        except (AttributeError, OSError, ValueError):
            value = None
        if value is not None:
            self.peak_bytes = max(self.peak_bytes or 0, value)


def _prepared_session(
    project: Mapping[str, object],
    settings: Mapping[str, object],
) -> tuple[StagedCalculationSession, float]:
    started = perf_counter()
    effort = str(settings["effort"])
    engine = IncrementalLocalAnalysisEngine(project, effort_profile=effort)
    session = StagedCalculationSession(project, solver_settings=settings)
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    return session, (perf_counter() - started) * 1000.0


def _solve_product_once(
    case: Mapping[str, object],
    *,
    repetition: int,
    downstream: bool,
) -> dict[str, object]:
    settings = dict(case["solver_settings"])
    previous_project = case.get("previous_project")
    context: dict[str, object] = {
        "requested": previous_project is not None,
        "status": "not_applicable",
        "preparation_ms": 0.0,
        "calculation_ms": 0.0,
        "plan_digest": None,
    }
    initial_incumbent = None
    if isinstance(previous_project, Mapping):
        previous_session, previous_preparation_ms = _prepared_session(
            previous_project, settings
        )
        previous_started = perf_counter()
        previous_result = previous_session.calculate_layout(
            request_id=(
                f"p64-l09w-a-{case['baseline_case_id']}-previous"
            ),
            request_revision=0,
        )
        previous_calculation_ms = (
            perf_counter() - previous_started
        ) * 1000.0
        previous_plan = previous_result["partition"]
        previous_status = str(previous_result["solver_result"]["status"])
        previous_certified = False
        if previous_status == _SOLVER_SOLUTION_FOUND and isinstance(
            previous_plan, Mapping
        ):
            previous_certified = recertify_minimal_layout_plan(
                previous_plan
            ).certified
            if previous_certified:
                initial_incumbent = previous_plan
        context = {
            "requested": True,
            "status": (
                "certified_solution"
                if previous_certified
                else previous_status
            ),
            "preparation_ms": round(previous_preparation_ms, 3),
            "calculation_ms": round(previous_calculation_ms, 3),
            "plan_digest": (
                previous_plan.get("plan_digest")
                if isinstance(previous_plan, Mapping)
                else None
            ),
        }

    session, preparation_ms = _prepared_session(case["project"], settings)
    calculation_started = perf_counter()
    calculated = session.calculate_layout(
        request_id=f"p64-l09w-a-{case['baseline_case_id']}",
        request_revision=1 if initial_incumbent is not None else 0,
        initial_incumbent=initial_incumbent,
    )
    calculation_ms = (perf_counter() - calculation_started) * 1000.0
    plan = calculated["partition"]
    solver_status = str(calculated["solver_result"]["status"])
    certification_ms = 0.0
    certificate_payload = {
        "attempted": False,
        "certified": False,
        "rejection_codes": [],
    }
    if solver_status == _SOLVER_SOLUTION_FOUND and isinstance(plan, Mapping):
        certificate_started = perf_counter()
        certificate = recertify_minimal_layout_plan(plan)
        certification_ms = (perf_counter() - certificate_started) * 1000.0
        certificate_payload = {
            "attempted": True,
            "certified": certificate.certified,
            "rejection_codes": list(certificate.rejection_codes),
        }
    status = _product_status(solver_status, certificate_payload)

    finalization: dict[str, object] = {
        "attempted": False,
        "status": "not_applicable",
        "elapsed_ms": 0.0,
        "plan_digest": None,
    }
    cad_ir: dict[str, object] = {
        "attempted": False,
        "status": "not_applicable",
        "elapsed_ms": 0.0,
        "cad_digest": None,
    }
    if downstream and status == _RESULT_CERTIFIED:
        finalization_started = perf_counter()
        finalized = session.finalize_volume(
            finishing_effort_profile="normal"
        )
        finalization_ms = (perf_counter() - finalization_started) * 1000.0
        finalization_status = str(finalized["solver_result"]["status"])
        finalized_plan = finalized["partition"]
        finalization = {
            "attempted": True,
            "status": finalization_status,
            "elapsed_ms": round(finalization_ms, 3),
            "effort_profile": "normal",
            "plan_digest": (
                finalized_plan.get("plan_digest")
                if isinstance(finalized_plan, Mapping)
                else None
            ),
        }
        if finalization_status == _SOLVER_SOLUTION_FOUND:
            selection = session.select_materializable_artifact(
                ARTIFACT_KIND_FINALIZED
            )
            cad_started = perf_counter()
            cad = build_partition_cad(
                case["project"],
                partition=selection["partition"],
                artifact_identity=selection,
                effort_profile=str(settings["effort"]),
            )
            cad_ms = (perf_counter() - cad_started) * 1000.0
            cad_ir = {
                "attempted": True,
                "status": cad.get("status"),
                "elapsed_ms": round(cad_ms, 3),
                "cad_digest": cad.get("cad_digest")
                or cad.get("build_digest"),
            }

    plan_payload = dict(plan) if isinstance(plan, Mapping) else {}
    return {
        "repetition": repetition,
        "status": status,
        "solver_status": solver_status,
        "stop_reason": _stop_reason(plan_payload),
        "plan_digest": plan_payload.get("plan_digest"),
        "functional_digest": _functional_digest(plan_payload),
        "placement_digest": _placement_digest(plan_payload),
        "preparation_ms": round(preparation_ms, 3),
        "calculation_ms": round(calculation_ms, 3),
        "time_to_first_certified_ms": (
            round(calculation_ms + certification_ms, 3)
            if status == _RESULT_CERTIFIED
            else None
        ),
        "certification_ms": round(certification_ms, 3),
        "certificate": certificate_payload,
        "context": context,
        "route": _route(plan_payload),
        "counters": _counters(plan_payload),
        "finalization": finalization,
        "cad_ir": cad_ir,
        "materialization": {
            "status": "not-measured-offline",
            "elapsed_ms": None,
        },
    }


def _product_status(
    solver_status: str, certificate: Mapping[str, object]
) -> str:
    if solver_status == _SOLVER_SOLUTION_FOUND:
        return (
            _RESULT_CERTIFIED
            if certificate.get("certified") is True
            else _RESULT_ERROR
        )
    if solver_status in {"infeasible_proven", "proven_impossible"}:
        return _RESULT_PROVEN_IMPOSSIBLE
    if solver_status in {
        "no_solution_within_budget",
        "bounded_unknown",
    }:
        return _RESULT_BOUNDED_UNKNOWN
    if solver_status in {"unsupported", "invalid_input"}:
        return _RESULT_UNSUPPORTED
    return _RESULT_ERROR


def _stop_reason(plan: Mapping[str, object]) -> str:
    solver = plan.get("solver")
    if not isinstance(solver, Mapping):
        return "not_available"
    telemetry = solver.get("telemetry")
    if isinstance(telemetry, Mapping) and telemetry.get("stop_reason"):
        return str(telemetry["stop_reason"])
    search = solver.get("search")
    if isinstance(search, Mapping) and search.get("stop_reason"):
        return str(search["stop_reason"])
    return "not_reported"


def _placement_digest(plan: Mapping[str, object]) -> str | None:
    minimal = plan.get("minimal_layout")
    if not isinstance(minimal, Mapping):
        return None
    provenance = minimal.get("search_provenance")
    if not isinstance(provenance, Mapping):
        return None
    selected = provenance.get("selected")
    if not isinstance(selected, Mapping):
        return None
    value = selected.get("placement_digest")
    return str(value) if value else None


def _functional_digest(plan: Mapping[str, object]) -> str | None:
    minimal = plan.get("minimal_layout")
    if not isinstance(minimal, Mapping):
        return None
    value = minimal.get("certifiable_payload_digest")
    return str(value) if value else None


def _route(plan: Mapping[str, object]) -> dict[str, object]:
    minimal = plan.get("minimal_layout")
    provenance = (
        minimal.get("search_provenance")
        if isinstance(minimal, Mapping)
        else None
    )
    if not isinstance(provenance, Mapping):
        return {
            "candidate_source": "not_available",
            "lane_id": "not_available",
            "internal_lane_count": 0,
            "external_invocation_count": 0,
        }
    selected = (
        dict(provenance.get("selected", {}))
        if isinstance(provenance.get("selected"), Mapping)
        else {}
    )
    external = (
        dict(provenance.get("external_lane", {}))
        if isinstance(provenance.get("external_lane"), Mapping)
        else {}
    )
    lanes = provenance.get("lanes", [])
    return {
        "candidate_source": selected.get("candidate_source", "not_available"),
        "lane_id": selected.get("lane_id", "not_available"),
        "internal_lane_count": len(lanes) if isinstance(lanes, list) else 0,
        "external_invocation_count": int(
            external.get("invocation_count", 0)
        ),
        "external_status": external.get("status", "not_available"),
        "external_engine_status": external.get(
            "engine_status", "not_available"
        ),
    }


def _counters(plan: Mapping[str, object]) -> dict[str, int]:
    totals = Counter()
    solver = plan.get("solver")
    if isinstance(solver, Mapping):
        telemetry = solver.get("telemetry")
        if isinstance(telemetry, Mapping):
            counters = telemetry.get("counters")
            if isinstance(counters, Mapping):
                for key, value in counters.items():
                    if isinstance(value, int) and not isinstance(value, bool):
                        totals[str(key)] += value
    minimal = plan.get("minimal_layout")
    provenance = (
        minimal.get("search_provenance")
        if isinstance(minimal, Mapping)
        else None
    )
    if isinstance(provenance, Mapping):
        for key in (
            "candidate_count_before_deduplication",
            "candidate_count_after_deduplication",
            "deduplicated_candidate_count",
            "pareto_candidate_count",
        ):
            value = provenance.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                totals[key] = value
        lanes = provenance.get("lanes", [])
        if isinstance(lanes, list):
            for lane in lanes:
                if not isinstance(lane, Mapping):
                    continue
                lane_telemetry = lane.get("telemetry")
                if isinstance(lane_telemetry, Mapping):
                    for key, value in lane_telemetry.items():
                        if isinstance(value, int) and not isinstance(
                            value, bool
                        ):
                            totals[str(key)] += value
                rejections = lane.get("rejection_code_counts")
                if isinstance(rejections, Mapping):
                    totals["certificate_rejections"] += sum(
                        int(value)
                        for value in rejections.values()
                        if isinstance(value, int)
                        and not isinstance(value, bool)
                    )
    return dict(sorted(totals.items()))


def run_product_case(
    case: Mapping[str, object], *, repeat_count: int
) -> dict[str, object]:
    if (
        case["expected"] == "impossible"
        and case.get("negative_rotation_proof_supported") is False
    ):
        return {
            "baseline_case_id": case["baseline_case_id"],
            "source": case["source"],
            "source_case_id": case["source_case_id"],
            "source_split": case["source_split"],
            "family": case["family"],
            "expected": case["expected"],
            "features": deepcopy(dict(case["features"])),
            "status": _RESULT_UNSUPPORTED,
            "stop_reason": (
                "historical_negative_rotation_constraint_not_exposed_"
                "by_project_v1"
            ),
            "runs": [],
            "deterministic": None,
            "resources": {
                "peak_working_set_bytes": None,
                "measurement_method": "not_started",
                "cpu_seconds": 0.0,
            },
        }

    started_cpu = process_time()
    with _WorkingSetSampler() as sampler:
        runs = [
            _solve_product_once(
                case,
                repetition=index + 1,
                downstream=index == 0,
            )
            for index in range(repeat_count)
        ]
    first = runs[0]
    deterministic = _functional_runs_identical(runs)
    return {
        "baseline_case_id": case["baseline_case_id"],
        "source": case["source"],
        "source_case_id": case["source_case_id"],
        "source_split": case["source_split"],
        "family": case["family"],
        "expected": case["expected"],
        "features": deepcopy(dict(case["features"])),
        "status": first["status"],
        "stop_reason": first["stop_reason"],
        "runs": runs,
        "deterministic": deterministic,
        "rotation_relaxed_for_positive": bool(
            case.get("rotation_relaxed_for_positive", False)
        ),
        "resources": {
            "peak_working_set_bytes": sampler.peak_bytes,
            "measurement_method": sampler.method,
            "cpu_seconds": round(process_time() - started_cpu, 6),
        },
    }


def _functional_runs_identical(
    runs: Sequence[Mapping[str, object]],
) -> bool | None:
    if len(runs) < 2:
        return None
    expected = (
        runs[0]["status"],
        runs[0]["solver_status"],
        runs[0]["functional_digest"],
        runs[0]["placement_digest"],
        runs[0]["route"],
    )
    return all(
        (
            value["status"],
            value["solver_status"],
            value["functional_digest"],
            value["placement_digest"],
            value["route"],
        )
        == expected
        for value in runs[1:]
    )


def _core_limits(
    config: Mapping[str, object], split: str
) -> tuple[ExternalSolverLimits, str]:
    stages = dict(config["stages"])
    if split == "regression":
        raw = dict(stages["regression"])
    elif split == "discovery":
        raw = dict(stages["discovery"])
    else:
        raw = dict(stages["tuning_trials"][0])
    return (
        ExternalSolverLimits(
            wall_seconds=float(raw["wall_seconds"]),
            memory_mebibytes=int(raw["memory_mebibytes"]),
            threads=int(raw["threads"]),
            seed=int(raw["seed"]),
        ),
        str(raw.get("profile", "balanced")),
    )


def run_core_case(
    case: Mapping[str, object],
    *,
    scratch_root: Path,
    config: Mapping[str, object],
) -> dict[str, object]:
    record = dict(case["record"])
    problem = materialize_tournament_problem(record)
    if problem is None:
        problem = materialize_case_problem(record)
    limits, profile = _core_limits(config, str(case["source_split"]))
    worker_digest = _sha256_path(CORE_WORKER)
    environment = {
        "BGIG_REAL3D_PROFILE": profile,
        "NO_PROXY": "*",
        "PYTHONNOUSERSITE": "1",
        "PYTHONPATH": str(SRC.resolve()),
    }
    runtime = ExternalSolverRuntime(
        candidate_id="current_bgig",
        command=(sys.executable, "-S", str(CORE_WORKER.resolve())),
        environment=tuple(sorted(environment.items())),
        scratch_root=str((scratch_root / "core-runs").resolve()),
        worker_digest=worker_digest,
    )
    report = run_real_3d_adapter(
        problem,
        candidate_id="current_bgig",
        runtime=runtime,
        limits=limits,
        artifact_receipt={"bundle_digest": worker_digest},
        exact_control=case["expected"] == "infeasible",
    )
    status = {
        CORE_SOLUTION_FOUND: _RESULT_CERTIFIED,
        CORE_INFEASIBLE_PROVEN: _RESULT_PROVEN_IMPOSSIBLE,
        CORE_BOUNDED_UNKNOWN: _RESULT_BOUNDED_UNKNOWN,
        CORE_UNSUPPORTED: _RESULT_UNSUPPORTED,
    }.get(str(report["status"]), _RESULT_ERROR)
    execution = (
        dict(report["execution"])
        if isinstance(report.get("execution"), Mapping)
        else {}
    )
    return {
        "baseline_case_id": case["baseline_case_id"],
        "source": "L08",
        "source_case_id": case["source_case_id"],
        "source_split": case["source_split"],
        "family": case["family"],
        "tier": case["tier"],
        "expected": case["expected"],
        "status": status,
        "stop_reason": report["stop_reason"],
        "certified": report["recertification"]["certified"],
        "timing": {
            "total_wall_seconds": execution.get("total_wall_seconds"),
            "cpu_seconds": execution.get("cpu_seconds"),
        },
        "resources": {
            "peak_working_set_bytes": execution.get(
                "peak_working_set_bytes"
            ),
            "measurement_method": "isolated_worker_20ms",
        },
        "telemetry": deepcopy(dict(report.get("engine", {}))).get(
            "telemetry", {}
        ),
        "report_digest": report["report_digest"],
    }


def _nearest_rank(values: Sequence[float], proportion: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    index = min(len(ordered), max(1, ceil(proportion * len(ordered)))) - 1
    return round(ordered[index], 6)


def _percentiles(values: Sequence[float]) -> dict[str, object]:
    return {
        "sample_count": len(values),
        "p50": _nearest_rank(values, 0.50),
        "p95": _nearest_rank(values, 0.95),
        "p99": _nearest_rank(values, 0.99),
    }


def _group_summary(
    rows: Sequence[Mapping[str, object]], key: str
) -> dict[str, object]:
    groups: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        features = row.get("features")
        if key in row:
            value = row[key]
        elif isinstance(features, Mapping):
            value = features.get(key, "missing")
        else:
            value = "missing"
        groups.setdefault(str(value), []).append(row)
    return {
        name: {
            "case_count": len(values),
            "certified_count": sum(
                value["status"] == _RESULT_CERTIFIED for value in values
            ),
            "certified_rate": round(
                sum(value["status"] == _RESULT_CERTIFIED for value in values)
                / len(values),
                6,
            ),
            "status_counts": dict(
                sorted(Counter(str(value["status"]) for value in values).items())
            ),
        }
        for name, values in sorted(groups.items())
    }


def _timing_summary(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    fields = (
        "preparation_ms",
        "calculation_ms",
        "time_to_first_certified_ms",
        "certification_ms",
    )
    result = {}
    for field in fields:
        values = [
            float(run[field])
            for row in rows
            for run in row.get("runs", [])[:1]
            if isinstance(run.get(field), (int, float))
            and not isinstance(run.get(field), bool)
        ]
        result[field] = _percentiles(values)
    finalization = [
        float(run["finalization"]["elapsed_ms"])
        for row in rows
        for run in row.get("runs", [])[:1]
        if isinstance(run.get("finalization"), Mapping)
        and run["finalization"].get("attempted") is True
    ]
    cad_ir = [
        float(run["cad_ir"]["elapsed_ms"])
        for row in rows
        for run in row.get("runs", [])[:1]
        if isinstance(run.get("cad_ir"), Mapping)
        and run["cad_ir"].get("attempted") is True
    ]
    memory = [
        float(row["resources"]["peak_working_set_bytes"])
        for row in rows
        if isinstance(row.get("resources"), Mapping)
        and isinstance(
            row["resources"].get("peak_working_set_bytes"), int
        )
    ]
    result["finalization_ms"] = _percentiles(finalization)
    result["cad_ir_ms"] = _percentiles(cad_ir)
    result["peak_working_set_bytes"] = _percentiles(memory)
    return result


def build_summary(
    product_results: Sequence[Mapping[str, object]],
    core_results: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    positives = [
        value for value in product_results if value["expected"] == "feasible"
    ]
    negatives = [
        value for value in product_results if value["expected"] == "impossible"
    ]
    certified_positives = sum(
        value["status"] == _RESULT_CERTIFIED for value in positives
    )
    false_impossible = sum(
        value["status"] == _RESULT_PROVEN_IMPOSSIBLE
        for value in positives
    )
    negative_contradictions = sum(
        value["status"] == _RESULT_CERTIFIED for value in negatives
    )
    deterministic_rows = [
        value for value in product_results if value["deterministic"] is not None
    ]
    return {
        "product": {
            "case_count": len(product_results),
            "status_counts": dict(
                sorted(
                    Counter(
                        str(value["status"]) for value in product_results
                    ).items()
                )
            ),
            "feasible_case_count": len(positives),
            "certified_feasible_count": certified_positives,
            "certified_feasible_rate": (
                round(certified_positives / len(positives), 6)
                if positives
                else None
            ),
            "false_impossible_count": false_impossible,
            "negative_control_count": len(negatives),
            "negative_oracle_contradiction_count": negative_contradictions,
            "deterministic_replay_count": len(deterministic_rows),
            "deterministic_replay_pass_count": sum(
                value["deterministic"] is True
                for value in deterministic_rows
            ),
            "downstream": {
                "finalization_attempt_count": sum(
                    bool(row.get("runs"))
                    and row["runs"][0]["finalization"]["attempted"] is True
                    for row in product_results
                ),
                "finalization_success_count": sum(
                    bool(row.get("runs"))
                    and row["runs"][0]["finalization"]["status"]
                    == _SOLVER_SOLUTION_FOUND
                    for row in product_results
                ),
                "cad_ir_attempt_count": sum(
                    bool(row.get("runs"))
                    and row["runs"][0]["cad_ir"]["attempted"] is True
                    for row in product_results
                ),
                "cad_ir_success_count": sum(
                    bool(row.get("runs"))
                    and row["runs"][0]["cad_ir"]["status"]
                    == "ready_for_fusion"
                    for row in product_results
                ),
                "materialization_measurement_count": 0,
            },
            "timings_and_memory": _timing_summary(product_results),
            "by_source": _group_summary(product_results, "source"),
            "by_family": _group_summary(product_results, "family"),
            "by_density": _group_summary(
                product_results, "density_target"
            ),
            "by_container_count": _group_summary(
                product_results, "container_group_count"
            ),
            "by_contents_per_container_maximum": _group_summary(
                product_results, "contents_per_container_maximum"
            ),
            "by_flat_item_count": _group_summary(
                product_results, "flat_item_count"
            ),
            "by_layer": _group_summary(product_results, "layer_target"),
            "by_execution_mode": _group_summary(
                product_results, "execution_mode"
            ),
            "positive_losses": [
                {
                    "baseline_case_id": value["baseline_case_id"],
                    "family": value["family"],
                    "status": value["status"],
                    "stop_reason": value["stop_reason"],
                }
                for value in positives
                if value["status"] != _RESULT_CERTIFIED
            ],
            "negative_contradictions": [
                {
                    "baseline_case_id": value["baseline_case_id"],
                    "family": value["family"],
                    "status": value["status"],
                }
                for value in negatives
                if value["status"] == _RESULT_CERTIFIED
            ],
            "nondeterministic_cases": [
                value["baseline_case_id"]
                for value in product_results
                if value["deterministic"] is False
            ],
        },
        "core_only": {
            "case_count": len(core_results),
            "status_counts": dict(
                sorted(
                    Counter(
                        str(value["status"]) for value in core_results
                    ).items()
                )
            ),
            "truth_pass_count": sum(
                (
                    value["expected"] == "feasible"
                    and value["status"] == _RESULT_CERTIFIED
                )
                or (
                    value["expected"] == "infeasible"
                    and value["status"]
                    in {
                        _RESULT_PROVEN_IMPOSSIBLE,
                        _RESULT_BOUNDED_UNKNOWN,
                    }
                )
                for value in core_results
            ),
            "by_family": _group_summary(core_results, "family"),
            "by_tier": _group_summary(core_results, "tier"),
            "product_path_complete": False,
        },
    }


def _checkpoint(
    path: Path,
    *,
    binding: str,
    resume: bool,
) -> dict[str, object]:
    if path.exists():
        if not resume:
            raise RuntimeError(
                "Checkpoint already exists; use --resume or choose another path."
            )
        value = _read_json(path)
        supplied = value.pop("checkpoint_digest", None)
        if (
            value.get("schema_version") != CHECKPOINT_SCHEMA_VERSION
            or value.get("binding_digest") != binding
            or supplied != canonical_digest(value)
        ):
            raise RuntimeError("Baseline checkpoint binding or digest mismatch.")
        value["checkpoint_digest"] = supplied
        return value
    value = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "binding_digest": binding,
        "product_results": {},
        "core_results": {},
    }
    value["checkpoint_digest"] = canonical_digest(value)
    _write_json_atomic(path, value)
    return value


def _save_checkpoint(path: Path, value: dict[str, object]) -> None:
    value.pop("checkpoint_digest", None)
    value["checkpoint_digest"] = canonical_digest(value)
    _write_json_atomic(path, value)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--worker-root", type=Path)
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--repeat-count", type=int, default=2)
    parser.add_argument("--max-product-cases", type=int, default=0)
    parser.add_argument("--max-core-cases", type=int, default=0)
    parser.add_argument("--skip-core", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    built = build_fixture_inventory()
    inventory = built["inventory"]
    if args.inventory_only:
        report = {
            "schema_version": SCHEMA_VERSION,
            "status": "inventory-only",
            "inventory": inventory,
        }
        report["report_digest"] = canonical_digest(report)
        _write_json_atomic(args.output, report)
        print(
            "P64_L09W_A_INVENTORY_OK "
            f"digest={report['report_digest']} "
            f"product={inventory['product_case_count']} "
            f"core={inventory['core_only_case_count']}",
            flush=True,
        )
        return 0

    required = (
        args.runtime_root,
        args.artifact,
        args.worker_root,
        args.scratch_root,
        args.checkpoint,
    )
    if any(value is None for value in required):
        raise RuntimeError(
            "Runtime, artifact, worker, scratch and checkpoint paths are required."
        )
    if args.repeat_count < 1 or args.repeat_count > 5:
        raise ValueError("repeat-count must stay between 1 and 5.")
    args.scratch_root.mkdir(parents=True, exist_ok=True)
    code_digest = _code_bundle_digest()
    binding_payload = {
        "inventory_digest": inventory["inventory_digest"],
        "code_bundle_digest": code_digest,
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "repeat_count": args.repeat_count,
        "skip_core": args.skip_core,
    }
    binding = canonical_digest(binding_payload)
    checkpoint = _checkpoint(
        args.checkpoint, binding=binding, resume=args.resume
    )
    configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root / "scip",
    )

    product_cases = list(built["product_cases"])
    if args.max_product_cases:
        product_cases = product_cases[: args.max_product_cases]
    for index, case in enumerate(product_cases, start=1):
        key = str(case["baseline_case_id"])
        if key in checkpoint["product_results"]:
            continue
        result = run_product_case(case, repeat_count=args.repeat_count)
        checkpoint["product_results"][key] = result
        _save_checkpoint(args.checkpoint, checkpoint)
        print(
            f"P64_L09W_A_PRODUCT {index}/{len(product_cases)} "
            f"case={key} status={result['status']}",
            flush=True,
        )

    core_cases = [] if args.skip_core else list(built["core_cases"])
    if args.max_core_cases:
        core_cases = core_cases[: args.max_core_cases]
    core_config = _read_json(
        FIXTURES / "p64_l08f_real_3d_tournament_config.v1.json"
    )
    for index, case in enumerate(core_cases, start=1):
        key = str(case["baseline_case_id"])
        if key in checkpoint["core_results"]:
            continue
        result = run_core_case(
            case,
            scratch_root=args.scratch_root,
            config=core_config,
        )
        checkpoint["core_results"][key] = result
        _save_checkpoint(args.checkpoint, checkpoint)
        print(
            f"P64_L09W_A_CORE {index}/{len(core_cases)} "
            f"case={key} status={result['status']}",
            flush=True,
        )

    product_results = [
        checkpoint["product_results"][str(case["baseline_case_id"])]
        for case in product_cases
    ]
    core_results = [
        checkpoint["core_results"][str(case["baseline_case_id"])]
        for case in core_cases
    ]
    complete = (
        len(product_cases) == inventory["product_case_count"]
        and (
            args.skip_core
            or len(core_cases) == inventory["core_only_case_count"]
        )
        and args.max_product_cases == 0
        and args.max_core_cases == 0
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "complete" if complete else "partial",
        "candidate": {
            "release_baseline": "0.1.80",
            "code_bundle_digest": code_digest,
            "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
            "attribution_fix": (
                "stable_scip_model_digest_excludes_remaining_deadline"
            ),
        },
        "inventory": inventory,
        "execution": {
            "python_version": (
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
            "platform": sys.platform,
            "repeat_count": args.repeat_count,
            "product_result_count": len(product_results),
            "core_result_count": len(core_results),
            "checkpoint_digest": checkpoint["checkpoint_digest"],
            "materialization_measured": False,
        },
        "summary": build_summary(product_results, core_results),
        "bindings": binding_payload,
        "invariants": {
            "historical_semantic_drift_executed": False,
            "old_holdout_used_as_new_holdout": False,
            "solver_budget_changed": False,
            "physical_value_changed": False,
            "grid_changed": False,
            "epsilon_changed": False,
            "fusion_materialization_invocation_count": 0,
        },
    }
    report["report_digest"] = canonical_digest(report)
    _write_json_atomic(args.output, report)
    print(
        "P64_L09W_A_BASELINE_OK "
        f"status={report['status']} "
        f"digest={report['report_digest']} "
        f"product={len(product_results)} core={len(core_results)}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
