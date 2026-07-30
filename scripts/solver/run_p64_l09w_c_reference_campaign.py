#!/usr/bin/env python3
"""Campagne produit ouverte P64-L09W-C, bornée et reprenable.

Le runner ne reçoit que le manifest public de P64-L09W-B. Il reconstruit les
400 projets ouverts, ne transmet jamais les témoins au solveur évalué et ne
possède aucun argument permettant de lire le holdout privé.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import ctypes
from functools import wraps
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
from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from board_game_insert_generator.selected_product_identity import (  # noqa: E402
    selected_product_digest,
)
from board_game_insert_generator.partition_cad import build_partition_cad  # noqa: E402
from board_game_insert_generator.product_solver_robustness_corpus import (  # noqa: E402
    HOLDOUT_RECEIPT_SCHEMA,
    MANIFEST_SCHEMA,
    OPEN_POSITIVE_COUNT,
    materialize_positive_case_bundle,
    validate_public_manifest,
)
from board_game_insert_generator.scip_product_solver import (  # noqa: E402
    SCIP_PRODUCT_ARTIFACT_DIGEST,
    configure_scip_product_runtime,
)
from board_game_insert_generator.solver_benchmark_adapters import (  # noqa: E402
    recertify_minimal_layout_plan,
)
from board_game_insert_generator.staged_calculation import (  # noqa: E402
    ARTIFACT_KIND_FINALIZED,
    StagedCalculationSession,
)


SCHEMA_VERSION = "bgig.p64_l09w_c_reference_campaign.v1"
CHECKPOINT_SCHEMA_VERSION = "bgig.p64_l09w_c_reference_checkpoint.v1"
CASE_RESULT_SCHEMA_VERSION = "bgig.p64_l09w_c_case_result.v1"
RUNTIME_RECEIPT_SCHEMA = "bgig.scip_product_integration_receipt.v1"
RELEASE_BASELINE = "0.1.80"
DEFAULT_SETTINGS = {"method": "auto", "effort": "normal"}
MAX_BATCH_SIZE = 25

RESULT_CERTIFIED = "certified_solution"
RESULT_PROVEN_IMPOSSIBLE = "proven_impossible"
RESULT_BOUNDED_UNKNOWN = "bounded_unknown"
RESULT_UNSUPPORTED = "unsupported"
RESULT_ERROR = "error"
SOLVER_SOLUTION_FOUND = "solution_found"

_GROUP_KEYS = (
    "split",
    "stratum",
    "target_density_pct",
    "container_count",
    "contents_per_container",
    "flat_count",
    "layer_bucket",
    "layer_count",
    "box_size",
    "execution",
    "aspect_profile",
    "fragmentation_class",
    "difficulty",
)
_TIMING_FIELDS = (
    "project_reconstruction_ms",
    "local_analysis_ms",
    "session_projection_ms",
    "calculation_ms",
    "time_to_first_certified_ms",
    "runner_recertification_ms",
    "internal_lanes_ms",
    "scip_ms",
    "solver_projection_ms",
    "common_certificate_ms",
    "finalization_ms",
    "cad_ir_ms",
)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain one JSON object.")
    return value


def _write_json_atomic(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _code_bundle_digest() -> str:
    digest = sha256()
    paths = [
        *sorted((ROOT / "src/board_game_insert_generator").glob("*.py")),
        Path(__file__).resolve(),
    ]
    for path in paths:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _validate_runtime_receipt(value: Mapping[str, object]) -> dict[str, object]:
    receipt = deepcopy(dict(value))
    supplied = receipt.pop("receipt_digest", None)
    if (
        receipt.get("schema_version") != RUNTIME_RECEIPT_SCHEMA
        or supplied != canonical_digest(receipt)
        or receipt.get("python_version") != "3.14.0"
        or receipt.get("runtime_artifact_digest")
        != SCIP_PRODUCT_ARTIFACT_DIGEST
        or receipt.get("runs_identical") is not True
    ):
        raise RuntimeError("SCIP product runtime receipt is invalid.")
    result = receipt.get("result")
    if (
        not isinstance(result, Mapping)
        or result.get("result_status") != SOLVER_SOLUTION_FOUND
        or result.get("candidate_source") != "external_scip_real_3d"
        or result.get("external_recertified") is not True
    ):
        raise RuntimeError("SCIP product runtime receipt did not pass its gate.")
    receipt["receipt_digest"] = supplied
    return receipt


def build_open_inventory(
    manifest: Mapping[str, object],
) -> dict[str, object]:
    accepted = validate_public_manifest(manifest)
    if accepted.get("schema_version") != MANIFEST_SCHEMA:
        raise RuntimeError("Unexpected P64-L09W-B manifest schema.")
    records = accepted["open_positive_case_records"]
    if len(records) != OPEN_POSITIVE_COUNT:
        raise RuntimeError("Reference campaign needs exactly 400 open cases.")
    if any(record.get("split") == "holdout" for record in records):
        raise RuntimeError("Public open schedule contains a holdout case.")
    receipt = deepcopy(dict(accepted["sealed_holdout_receipt"]))
    if (
        receipt.get("schema_version") != HOLDOUT_RECEIPT_SCHEMA
        or receipt.get("opened") is not False
        or receipt.get("opening_count") != 0
        or receipt.get("solver_invocation_count") != 0
        or "case_records" in receipt
        or "campaign_nonce" in receipt
    ):
        raise RuntimeError("Public holdout receipt is not closed.")
    case_ids = [str(record["case_id"]) for record in records]
    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError("Open schedule contains duplicate case ids.")
    return {
        "manifest": accepted,
        "records": records,
        "inventory": {
            "schema_version": "bgig.p64_l09w_c_open_inventory.v1",
            "manifest_digest": accepted["manifest_digest"],
            "case_count": len(records),
            "split_counts": dict(
                sorted(Counter(str(value["split"]) for value in records).items())
            ),
            "stratum_counts": dict(
                sorted(
                    Counter(str(value["stratum"]) for value in records).items()
                )
            ),
            "negative_control_execution_count": 0,
            "sealed_holdout_receipt": receipt,
            "holdout_case_records_loaded": False,
        },
    }


class _WorkingSetSampler:
    """Échantillonne le working set du processus natif au plus toutes les 50 ms."""

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
                0x1000 | 0x0400,
                False,
                process_id,
            )
            if not handle:
                return None
            try:
                counters = counters_type()
                counters.cb = ctypes.sizeof(counters)
                if not psapi.GetProcessMemoryInfo(
                    handle,
                    ctypes.byref(counters),
                    counters.cb,
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


class _SolverTimingProbe:
    """Chronomètre les appels internes sans modifier leurs entrées ni sorties."""

    _TARGETS = (
        ("problem_preparation", "prepare_free_3d_problem"),
        ("internal_beam", "solve_free_3d_beam"),
        ("internal_floor", "solve_floor_maxrects"),
        ("internal_reserved_stack", "solve_reserved_floor_stacks"),
        ("scip", "solve_scip_product_3d"),
        ("solver_projection", "_rebuild_empty_spaces"),
        ("common_certificate", "certify_minimal_free_3d_plan"),
    )

    def __init__(self) -> None:
        self._module: object | None = None
        self._originals: dict[str, Callable[..., object]] = {}
        self._counts: Counter[str] = Counter()
        self._elapsed_ms: Counter[str] = Counter()

    def __enter__(self) -> "_SolverTimingProbe":
        import board_game_insert_generator.minimal_layout_solver as module

        self._module = module
        for category, attribute in self._TARGETS:
            original = getattr(module, attribute)
            self._originals[attribute] = original
            setattr(module, attribute, self._wrapper(category, original))
        return self

    def __exit__(self, _kind, _value, _traceback) -> None:
        if self._module is None:
            return
        for attribute, original in self._originals.items():
            setattr(self._module, attribute, original)

    def _wrapper(
        self,
        category: str,
        original: Callable[..., object],
    ) -> Callable[..., object]:
        @wraps(original)
        def measured(*args: object, **kwargs: object) -> object:
            started = perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                self._counts[category] += 1
                self._elapsed_ms[category] += (
                    perf_counter() - started
                ) * 1000.0

        return measured

    def report(self, total_calculation_ms: float) -> dict[str, object]:
        calls = {
            category: {
                "invocation_count": int(self._counts[category]),
                "elapsed_ms": round(float(self._elapsed_ms[category]), 3),
            }
            for category, _attribute in self._TARGETS
        }
        internal_ms = sum(
            float(self._elapsed_ms[value])
            for value in (
                "internal_beam",
                "internal_floor",
                "internal_reserved_stack",
            )
        )
        attributed = sum(float(value) for value in self._elapsed_ms.values())
        return {
            "method": "runner_monotonic_wrappers_restored_after_calculation",
            "calls": calls,
            "internal_lanes_ms": round(internal_ms, 3),
            "scip_ms": round(float(self._elapsed_ms["scip"]), 3),
            "solver_projection_ms": round(
                float(self._elapsed_ms["solver_projection"]),
                3,
            ),
            "common_certificate_ms": round(
                float(self._elapsed_ms["common_certificate"]),
                3,
            ),
            "problem_preparation_ms": round(
                float(self._elapsed_ms["problem_preparation"]),
                3,
            ),
            "unattributed_solver_ms": round(
                max(0.0, total_calculation_ms - attributed),
                3,
            ),
        }


def _prepared_session(
    project: Mapping[str, object],
    settings: Mapping[str, object],
) -> tuple[
    IncrementalLocalAnalysisEngine,
    StagedCalculationSession,
    dict[str, float],
]:
    local_started = perf_counter()
    engine = IncrementalLocalAnalysisEngine(
        project,
        effort_profile=str(settings["effort"]),
    )
    local_ms = (perf_counter() - local_started) * 1000.0
    projection_started = perf_counter()
    session = StagedCalculationSession(project, solver_settings=settings)
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    projection_ms = (perf_counter() - projection_started) * 1000.0
    return (
        engine,
        session,
        {
            "local_analysis_ms": round(local_ms, 3),
            "session_projection_ms": round(projection_ms, 3),
        },
    )


def _incremental_summary(snapshot: Mapping[str, object]) -> dict[str, object]:
    incremental = snapshot.get("incremental")
    if not isinstance(incremental, Mapping):
        return {"status": "not_available"}
    return {
        "status": "observed",
        "recomputed_frontier_group_count": len(
            incremental.get("recomputed_frontier_group_ids", [])
        ),
        "recomputed_context_group_count": len(
            incremental.get("recomputed_context_group_ids", [])
        ),
        "reused_frontier_group_count": len(
            incremental.get("reused_frontier_group_ids", [])
        ),
        "reused_context_group_count": len(
            incremental.get("reused_context_group_ids", [])
        ),
        "invalidation_event_count": len(
            incremental.get("invalidation_events", [])
        ),
        "cache": deepcopy(dict(incremental.get("cache", {}))),
    }


def _prepare_execution_context(
    *,
    case_id: str,
    after_project: Mapping[str, object],
    before_project: Mapping[str, object] | None,
    settings: Mapping[str, object],
) -> tuple[
    StagedCalculationSession,
    Mapping[str, object] | None,
    dict[str, object],
    dict[str, float],
]:
    if before_project is None:
        engine, session, timings = _prepared_session(
            after_project,
            settings,
        )
        return (
            session,
            None,
            {
                "mode": "cold_reconstruction",
                "previous_calculation_requested": False,
                "previous_status": "not_applicable",
                "initial_incumbent_supplied": False,
                "incremental": _incremental_summary(engine.snapshot()),
            },
            timings,
        )

    engine, session, before_timings = _prepared_session(
        before_project,
        settings,
    )
    previous_started = perf_counter()
    with _SolverTimingProbe() as previous_probe:
        previous = session.calculate_layout(
            request_id=f"p64-l09w-c-{case_id}-previous",
            request_revision=0,
        )
    previous_calculation_ms = (perf_counter() - previous_started) * 1000.0
    previous_plan = previous.get("partition")
    previous_status = str(
        dict(previous.get("solver_result", {})).get("status", "error")
    )
    previous_certified = False
    initial_incumbent: Mapping[str, object] | None = None
    if (
        previous_status == SOLVER_SOLUTION_FOUND
        and isinstance(previous_plan, Mapping)
    ):
        previous_certified = recertify_minimal_layout_plan(
            previous_plan
        ).certified
        if previous_certified:
            initial_incumbent = previous_plan

    update_started = perf_counter()
    local_snapshot = engine.update_project(after_project)
    update_local_ms = (perf_counter() - update_started) * 1000.0
    projection_started = perf_counter()
    synchronized = session.synchronize(
        after_project,
        local_snapshot,
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    update_projection_ms = (perf_counter() - projection_started) * 1000.0
    previous_timing_report = previous_probe.report(
        previous_calculation_ms
    )
    return (
        session,
        initial_incumbent,
        {
            "mode": "incremental_edit",
            "previous_calculation_requested": True,
            "previous_status": (
                RESULT_CERTIFIED
                if previous_certified
                else previous_status
            ),
            "previous_plan_digest": (
                previous_plan.get("plan_digest")
                if isinstance(previous_plan, Mapping)
                else None
            ),
            "previous_calculation_ms": round(previous_calculation_ms, 3),
            "previous_instrumentation": previous_timing_report,
            "initial_incumbent_supplied": initial_incumbent is not None,
            "incremental": _incremental_summary(local_snapshot),
            "staged_cache_after_edit": deepcopy(
                dict(synchronized.get("cache", {}))
            ),
        },
        {
            "local_analysis_ms": round(
                before_timings["local_analysis_ms"] + update_local_ms,
                3,
            ),
            "session_projection_ms": round(
                before_timings["session_projection_ms"]
                + update_projection_ms,
                3,
            ),
        },
    )


def _product_status(
    solver_status: str,
    certificate: Mapping[str, object],
) -> str:
    if solver_status == SOLVER_SOLUTION_FOUND:
        return (
            RESULT_CERTIFIED
            if certificate.get("certified") is True
            else RESULT_ERROR
        )
    if solver_status in {"infeasible_proven", "proven_impossible"}:
        return RESULT_PROVEN_IMPOSSIBLE
    if solver_status in {"no_solution_within_budget", "bounded_unknown"}:
        return RESULT_BOUNDED_UNKNOWN
    if solver_status in {"unsupported", "invalid_input"}:
        return RESULT_UNSUPPORTED
    return RESULT_ERROR


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
    provenance = (
        minimal.get("search_provenance")
        if isinstance(minimal, Mapping)
        else None
    )
    selected = (
        provenance.get("selected")
        if isinstance(provenance, Mapping)
        else None
    )
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


def _selected_product_digest(plan: Mapping[str, object]) -> str:
    return selected_product_digest(plan)


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
            "external_status": "not_available",
            "external_stop_reason": "not_available",
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
    recertification = (
        dict(external.get("recertification", {}))
        if isinstance(external.get("recertification"), Mapping)
        else {}
    )
    lane_values = (
        [value for value in lanes if isinstance(value, Mapping)]
        if isinstance(lanes, list)
        else []
    )
    return {
        "candidate_source": selected.get(
            "candidate_source",
            "not_available",
        ),
        "lane_id": selected.get("lane_id", "not_available"),
        "internal_lane_count": len(lane_values),
        "internal_lane_status_counts": dict(
            sorted(
                Counter(
                    str(value.get("status", "not_available"))
                    for value in lane_values
                ).items()
            )
        ),
        "external_invocation_count": int(
            external.get("invocation_count", 0)
        ),
        "external_status": external.get("status", "not_available"),
        "external_stop_reason": external.get(
            "stop_reason",
            "not_available",
        ),
        "external_engine_status": external.get(
            "engine_status",
            "not_available",
        ),
        "external_recertified": recertification.get("certified", False),
        "external_rejection_codes": deepcopy(
            list(recertification.get("rejection_codes", []))
        ),
    }


def _counters(plan: Mapping[str, object]) -> dict[str, object]:
    solver = plan.get("solver")
    telemetry = (
        solver.get("telemetry")
        if isinstance(solver, Mapping)
        else None
    )
    solver_counters = (
        {
            str(key): int(value)
            for key, value in dict(
                telemetry.get("counters", {})
            ).items()
            if isinstance(value, int) and not isinstance(value, bool)
        }
        if isinstance(telemetry, Mapping)
        and isinstance(telemetry.get("counters"), Mapping)
        else {}
    )
    minimal = plan.get("minimal_layout")
    provenance = (
        minimal.get("search_provenance")
        if isinstance(minimal, Mapping)
        else None
    )
    candidate_counts: dict[str, int] = {}
    lane_totals: Counter[str] = Counter()
    if isinstance(provenance, Mapping):
        for key in (
            "candidate_count_before_deduplication",
            "candidate_count_after_deduplication",
            "deduplicated_candidate_count",
            "pareto_candidate_count",
        ):
            value = provenance.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                candidate_counts[key] = value
        lanes = provenance.get("lanes", [])
        if isinstance(lanes, list):
            for lane in lanes:
                if not isinstance(lane, Mapping):
                    continue
                lane_telemetry = lane.get("telemetry")
                if isinstance(lane_telemetry, Mapping):
                    for key, value in lane_telemetry.items():
                        if isinstance(value, int) and not isinstance(
                            value,
                            bool,
                        ):
                            lane_totals[str(key)] += value
                rejections = lane.get("rejection_code_counts")
                if isinstance(rejections, Mapping):
                    lane_totals["certificate_rejections"] += sum(
                        int(value)
                        for value in rejections.values()
                        if isinstance(value, int)
                        and not isinstance(value, bool)
                    )
    return {
        "solver": dict(sorted(solver_counters.items())),
        "candidate_counts": dict(sorted(candidate_counts.items())),
        "lane_totals": dict(sorted(lane_totals.items())),
    }


def _staged_observation(
    calculated: Mapping[str, object],
) -> dict[str, object]:
    staged = calculated.get("staged_calculation")
    if not isinstance(staged, Mapping):
        return {"status": "not_available"}
    minimal = staged.get("minimal_layout")
    if not isinstance(minimal, Mapping):
        return {"status": "not_available"}
    return {
        "status": "observed",
        "cache_status": minimal.get("cache_status"),
        "cache_write_status": minimal.get("cache_write_status"),
        "calculation_timing": deepcopy(
            dict(minimal.get("calculation_timing", {}))
        ),
        "warm_start": deepcopy(dict(minimal.get("warm_start", {}))),
        "source_revision": minimal.get("source_revision"),
    }


def _result_stop_reason(value: Mapping[str, object]) -> str:
    result = value.get("solver_result")
    if not isinstance(result, Mapping):
        return "not_available"
    telemetry = result.get("telemetry")
    if isinstance(telemetry, Mapping):
        return str(
            telemetry.get(
                "search_stop_reason",
                telemetry.get("stop_reason", "not_reported"),
            )
        )
    return "not_reported"


def _detached_plan_payload(value: object) -> dict[str, object]:
    return (
        deepcopy(dict(value))
        if isinstance(value, Mapping)
        else {}
    )


def _run_once(
    *,
    case_id: str,
    after_project: Mapping[str, object],
    before_project: Mapping[str, object] | None,
    settings: Mapping[str, object],
    repetition: int,
    downstream: bool,
) -> dict[str, object]:
    (
        session,
        initial_incumbent,
        context,
        preparation,
    ) = _prepare_execution_context(
        case_id=case_id,
        after_project=after_project,
        before_project=before_project,
        settings=settings,
    )
    calculation_started = perf_counter()
    with _SolverTimingProbe() as probe:
        calculated = session.calculate_layout(
            request_id=f"p64-l09w-c-{case_id}",
            request_revision=1 if initial_incumbent is not None else 0,
            initial_incumbent=initial_incumbent,
        )
    calculation_ms = (perf_counter() - calculation_started) * 1000.0
    instrumentation = probe.report(calculation_ms)
    plan = calculated.get("partition")
    plan_payload = _detached_plan_payload(plan)
    solver_result = calculated.get("solver_result")
    solver_status = (
        str(solver_result.get("status", "error"))
        if isinstance(solver_result, Mapping)
        else "error"
    )
    certificate_started = perf_counter()
    certificate_payload: dict[str, object] = {
        "attempted": False,
        "certified": False,
        "rejection_codes": [],
    }
    if solver_status == SOLVER_SOLUTION_FOUND and plan_payload:
        certificate = recertify_minimal_layout_plan(plan_payload)
        certificate_payload = {
            "attempted": True,
            "certified": certificate.certified,
            "rejection_codes": list(certificate.rejection_codes),
        }
    certification_ms = (perf_counter() - certificate_started) * 1000.0
    status = _product_status(solver_status, certificate_payload)

    finalization: dict[str, object] = {
        "attempted": False,
        "status": "not_applicable",
        "stop_reason": "minimal_layout_not_certified",
        "elapsed_ms": None,
        "plan_digest": None,
    }
    cad_ir: dict[str, object] = {
        "attempted": False,
        "status": "not_applicable",
        "stop_reason": "finalization_not_ready",
        "elapsed_ms": None,
        "cad_digest": None,
    }
    if downstream and status == RESULT_CERTIFIED:
        finalization_started = perf_counter()
        try:
            finalized = session.finalize_volume(
                finishing_effort_profile="normal"
            )
            finalization_ms = (
                perf_counter() - finalization_started
            ) * 1000.0
            finalization_status = str(
                dict(finalized.get("solver_result", {})).get(
                    "status",
                    "error",
                )
            )
            finalized_plan = finalized.get("partition")
            finalization = {
                "attempted": True,
                "status": finalization_status,
                "stop_reason": _result_stop_reason(finalized),
                "elapsed_ms": round(finalization_ms, 3),
                "effort_profile": "normal",
                "plan_digest": (
                    finalized_plan.get("plan_digest")
                    if isinstance(finalized_plan, Mapping)
                    else None
                ),
            }
        except (
            KeyError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            finalization = {
                "attempted": True,
                "status": "error",
                "stop_reason": (
                    f"runner_finalization_exception:{type(exc).__name__}"
                ),
                "elapsed_ms": round(
                    (perf_counter() - finalization_started) * 1000.0,
                    3,
                ),
                "effort_profile": "normal",
                "plan_digest": None,
            }
            finalization_status = "error"
        if finalization_status == SOLVER_SOLUTION_FOUND:
            cad_started = perf_counter()
            try:
                selection = session.select_materializable_artifact(
                    ARTIFACT_KIND_FINALIZED
                )
                cad = build_partition_cad(
                    after_project,
                    partition=selection["partition"],
                    artifact_identity=selection,
                    effort_profile=str(settings["effort"]),
                )
                cad_ir = {
                    "attempted": True,
                    "status": cad.get("status"),
                    "stop_reason": cad.get(
                        "stop_reason",
                        "cad_ir_build_completed",
                    ),
                    "elapsed_ms": round(
                        (perf_counter() - cad_started) * 1000.0,
                        3,
                    ),
                    "cad_digest": cad.get("cad_digest")
                    or cad.get("build_digest"),
                }
            except (
                KeyError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as exc:
                cad_ir = {
                    "attempted": True,
                    "status": "error",
                    "stop_reason": (
                        f"runner_cad_ir_exception:{type(exc).__name__}"
                    ),
                    "elapsed_ms": round(
                        (perf_counter() - cad_started) * 1000.0,
                        3,
                    ),
                    "cad_digest": None,
                }

    route = _route(plan_payload)
    staged = _staged_observation(calculated)
    context["warm_start_outcome"] = deepcopy(
        dict(staged.get("warm_start", {}))
    )
    timings = {
        **preparation,
        "calculation_ms": round(calculation_ms, 3),
        "time_to_first_certified_ms": (
            round(calculation_ms + certification_ms, 3)
            if status == RESULT_CERTIFIED
            else None
        ),
        "runner_recertification_ms": round(certification_ms, 3),
        "internal_lanes_ms": instrumentation["internal_lanes_ms"],
        "scip_ms": instrumentation["scip_ms"],
        "solver_projection_ms": instrumentation[
            "solver_projection_ms"
        ],
        "common_certificate_ms": instrumentation[
            "common_certificate_ms"
        ],
        "finalization_ms": finalization["elapsed_ms"],
        "cad_ir_ms": cad_ir["elapsed_ms"],
    }
    return {
        "repetition": repetition,
        "status": status,
        "solver_status": solver_status,
        "stop_reason": _stop_reason(plan_payload),
        "plan_digest": plan_payload.get("plan_digest"),
        "functional_digest": _functional_digest(plan_payload),
        "selected_product_digest": _selected_product_digest(plan_payload),
        "execution_trace_digest": _functional_digest(plan_payload),
        "placement_digest": _placement_digest(plan_payload),
        "timings": timings,
        "certificate": certificate_payload,
        "context": context,
        "staged_calculation": staged,
        "route": route,
        "counters": _counters(plan_payload),
        "instrumentation": instrumentation,
        "limits": {
            "product_effort": settings["effort"],
            "product_method": settings["method"],
            "solver_budgets": deepcopy(
                dict(
                    dict(plan_payload.get("solver", {})).get(
                        "budgets",
                        {},
                    )
                )
            ),
            "external": deepcopy(
                dict(
                    dict(
                        dict(
                            plan_payload.get(
                                "minimal_layout",
                                {},
                            )
                        ).get("search_provenance", {})
                    ).get("external_lane", {})
                ).get("limits", {})
            ),
        },
        "finalization": finalization,
        "cad_ir": cad_ir,
        "materialization": {
            "status": "not-measured-offline",
            "elapsed_ms": None,
            "fusion_invocation_count": 0,
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
        runs[0].get("selected_product_digest")
        or runs[0].get("functional_digest"),
        runs[0]["placement_digest"],
    )
    return all(
        (
            value["status"],
            value["solver_status"],
            value.get("selected_product_digest")
            or value.get("functional_digest"),
            value["placement_digest"],
        )
        == expected
        for value in runs[1:]
    )


def _execution_traces_identical(
    runs: Sequence[Mapping[str, object]],
) -> bool | None:
    if len(runs) < 2:
        return None
    expected = runs[0].get(
        "execution_trace_digest",
        runs[0].get("functional_digest"),
    )
    return all(
        value.get(
            "execution_trace_digest",
            value.get("functional_digest"),
        )
        == expected
        for value in runs[1:]
    )


def _execution_routes_identical(
    runs: Sequence[Mapping[str, object]],
) -> bool | None:
    if len(runs) < 2:
        return None
    expected = (
        dict(runs[0]["route"]).get("candidate_source"),
        dict(runs[0]["route"]).get("lane_id"),
    )
    return all(
        (
            dict(value["route"]).get("candidate_source"),
            dict(value["route"]).get("lane_id"),
        )
        == expected
        for value in runs[1:]
    )


def _case_features(record: Mapping[str, object]) -> dict[str, object]:
    axes = deepcopy(dict(record["axes"]))
    recipe = dict(record["recipe"])
    constructive = dict(recipe.get("constructive_metrics", {}))
    minimum_margin = float(
        constructive.get("minimum_axis_margin_pct", 100.0)
    )
    density = int(axes["target_density_pct"])
    difficulty = "common"
    if (
        record["stratum"] == "stress"
        or density >= 85
        or minimum_margin < 20.0
        or int(axes["container_count"]) >= 30
    ):
        difficulty = "stress"
    return {
        **axes,
        "split": record["split"],
        "stratum": record["stratum"],
        "aspect_profile": recipe.get("aspect_profile"),
        "fragmentation_class": constructive.get(
            "fragmentation_class"
        ),
        "minimum_axis_margin_pct": minimum_margin,
        "free_region_lower_bound": constructive.get(
            "free_region_lower_bound"
        ),
        "difficulty": difficulty,
    }


def classify_case_losses(
    result: Mapping[str, object],
) -> list[dict[str, object]]:
    losses: list[dict[str, object]] = []
    runs = result.get("runs", [])
    first = (
        dict(runs[0])
        if isinstance(runs, list)
        and runs
        and isinstance(runs[0], Mapping)
        else {}
    )
    status = str(result.get("status", RESULT_ERROR))
    route = (
        dict(first.get("route", {}))
        if isinstance(first.get("route"), Mapping)
        else {}
    )
    stop_reason = str(first.get("stop_reason", "not_available"))
    if status == RESULT_PROVEN_IMPOSSIBLE:
        losses.append(
            {
                "stage": "calculation",
                "cause": "false_impossible_on_constructed_positive",
                "detail": stop_reason,
                "candidate_invalidating": True,
            }
        )
    elif status == RESULT_BOUNDED_UNKNOWN:
        external_status = str(
            route.get("external_status", "not_available")
        )
        if "deadline" in stop_reason:
            cause = "global_deadline_exhausted"
        elif external_status in {
            "bounded_unknown",
            "certificate_rejected",
        }:
            cause = (
                "internal_lanes_exhausted_and_scip_not_certified"
            )
        else:
            cause = "bounded_search_exhaustion"
        losses.append(
            {
                "stage": "calculation",
                "cause": cause,
                "detail": (
                    f"{stop_reason};external={external_status}"
                ),
                "candidate_invalidating": False,
            }
        )
    elif status == RESULT_UNSUPPORTED:
        losses.append(
            {
                "stage": "projection",
                "cause": "product_domain_unsupported",
                "detail": stop_reason,
                "candidate_invalidating": False,
            }
        )
    elif status == RESULT_ERROR:
        certificate = (
            dict(first.get("certificate", {}))
            if isinstance(first.get("certificate"), Mapping)
            else {}
        )
        cause = (
            "solver_solution_failed_current_recertification"
            if certificate.get("attempted") is True
            and certificate.get("certified") is not True
            else "calculation_error"
        )
        losses.append(
            {
                "stage": "certificate",
                "cause": cause,
                "detail": stop_reason,
                "candidate_invalidating": True,
            }
        )

    if status == RESULT_CERTIFIED:
        finalization = (
            dict(first.get("finalization", {}))
            if isinstance(first.get("finalization"), Mapping)
            else {}
        )
        cad_ir = (
            dict(first.get("cad_ir", {}))
            if isinstance(first.get("cad_ir"), Mapping)
            else {}
        )
        if finalization.get("status") != SOLVER_SOLUTION_FOUND:
            losses.append(
                {
                    "stage": "finalization",
                    "cause": "certified_minimal_not_finalized",
                    "detail": finalization.get(
                        "stop_reason",
                        "not_available",
                    ),
                    "candidate_invalidating": True,
                }
            )
        elif cad_ir.get("status") != "ready_for_fusion":
            losses.append(
                {
                    "stage": "cad_ir",
                    "cause": "finalized_plan_not_ready_for_fusion",
                    "detail": cad_ir.get(
                        "stop_reason",
                        "not_available",
                    ),
                    "candidate_invalidating": True,
                }
            )
    if result.get("deterministic") is False:
        losses.append(
            {
                "stage": "replay",
                "cause": "functional_nondeterminism",
                "detail": "functional_digest_or_route_differs",
                "candidate_invalidating": True,
            }
        )
    return losses


def run_open_case(
    record: Mapping[str, object],
    *,
    repeat_count: int,
) -> dict[str, object]:
    reconstruction_started = perf_counter()
    bundle = materialize_positive_case_bundle(record["recipe"])
    reconstruction_ms = (
        perf_counter() - reconstruction_started
    ) * 1000.0
    if canonical_digest(bundle["after_project"]) != record["project_digest"]:
        raise RuntimeError("Open project commitment mismatch.")
    before_project = bundle["before_project"]
    if (
        None
        if before_project is None
        else canonical_digest(before_project)
    ) != record["before_project_digest"]:
        raise RuntimeError("Open previous-project commitment mismatch.")

    started_cpu = process_time()
    with _WorkingSetSampler() as sampler:
        runs = [
            _run_once(
                case_id=str(record["case_id"]),
                after_project=bundle["after_project"],
                before_project=before_project,
                settings=DEFAULT_SETTINGS,
                repetition=index + 1,
                downstream=index == 0,
            )
            for index in range(repeat_count)
        ]
    runs[0]["timings"]["project_reconstruction_ms"] = round(
        reconstruction_ms,
        3,
    )
    for run in runs[1:]:
        run["timings"]["project_reconstruction_ms"] = 0.0
    result: dict[str, object] = {
        "schema_version": CASE_RESULT_SCHEMA_VERSION,
        "case_id": record["case_id"],
        "case_digest": record["case_digest"],
        "project_digest": record["project_digest"],
        "oracle_digest": record["oracle_receipt"]["oracle_digest"],
        "split": record["split"],
        "stratum": record["stratum"],
        "expected": "feasible",
        "features": _case_features(record),
        "status": runs[0]["status"],
        "stop_reason": runs[0]["stop_reason"],
        "runs": runs,
        "deterministic": _functional_runs_identical(runs),
        "execution_trace_deterministic": _execution_traces_identical(
            runs
        ),
        "execution_route_deterministic": _execution_routes_identical(
            runs
        ),
        "resources": {
            "peak_working_set_bytes": sampler.peak_bytes,
            "measurement_method": sampler.method,
            "cpu_seconds": round(process_time() - started_cpu, 6),
        },
        "witness_disclosed_to_evaluated_solver": False,
    }
    result["losses"] = classify_case_losses(result)
    result["case_result_digest"] = canonical_digest(result)
    return result


def _nearest_rank(
    values: Sequence[float],
    proportion: float,
) -> float | None:
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


def _offline_ready(row: Mapping[str, object]) -> bool:
    runs = row.get("runs", [])
    if not isinstance(runs, list) or not runs:
        return False
    first = runs[0]
    if not isinstance(first, Mapping):
        return False
    finalization = first.get("finalization")
    cad_ir = first.get("cad_ir")
    return bool(
        isinstance(finalization, Mapping)
        and finalization.get("status") == SOLVER_SOLUTION_FOUND
        and isinstance(cad_ir, Mapping)
        and cad_ir.get("status") == "ready_for_fusion"
    )


def _timing_value(
    row: Mapping[str, object],
    field: str,
) -> float | None:
    runs = row.get("runs", [])
    if not isinstance(runs, list) or not runs:
        return None
    first = runs[0]
    if not isinstance(first, Mapping):
        return None
    timings = first.get("timings")
    if not isinstance(timings, Mapping):
        return None
    value = timings.get(field)
    return (
        float(value)
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
        else None
    )


def _group_result(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    certified = [
        value
        for value in rows
        if value.get("status") == RESULT_CERTIFIED
    ]
    offline_ready = sum(_offline_ready(value) for value in rows)
    timings = {}
    for field in _TIMING_FIELDS:
        values = [
            timing
            for row in certified
            for timing in [_timing_value(row, field)]
            if timing is not None
        ]
        timings[field] = _percentiles(values)
    memory = [
        float(dict(value.get("resources", {}))["peak_working_set_bytes"])
        for value in certified
        if isinstance(value.get("resources"), Mapping)
        and isinstance(
            dict(value["resources"]).get("peak_working_set_bytes"),
            int,
        )
    ]
    timings["peak_working_set_bytes"] = _percentiles(memory)
    return {
        "case_count": len(rows),
        "certified_count": len(certified),
        "censored_count": len(rows) - len(certified),
        "certified_rate": (
            round(len(certified) / len(rows), 6)
            if rows
            else None
        ),
        "offline_ready_count": offline_ready,
        "offline_ready_rate": (
            round(offline_ready / len(rows), 6)
            if rows
            else None
        ),
        "status_counts": dict(
            sorted(
                Counter(
                    str(value.get("status", RESULT_ERROR))
                    for value in rows
                ).items()
            )
        ),
        "timings_certified_only": timings,
    }


def _group_summary(
    rows: Sequence[Mapping[str, object]],
    key: str,
) -> dict[str, object]:
    groups: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        features = row.get("features")
        value = (
            features.get(key, "missing")
            if isinstance(features, Mapping)
            else "missing"
        )
        groups.setdefault(str(value), []).append(row)
    return {
        name: _group_result(values)
        for name, values in sorted(groups.items())
    }


def _hypothesis_comparison(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    causes = Counter(
        str(loss["cause"])
        for row in rows
        for loss in row.get("losses", [])
        if isinstance(loss, Mapping)
    )
    candidates: list[dict[str, object]] = [
        {
            "hypothesis_id": "no_algorithm_change_v1",
            "measured_target_count": 0,
            "simplicity": "very_high",
            "maintenance": "lowest",
            "testability": "high",
            "probable_gain": "none",
            "functional_risk": "lowest",
        }
    ]
    mappings = (
        (
            "bounded_internal_or_scip_search",
            {
                "internal_lanes_exhausted_and_scip_not_certified",
                "bounded_search_exhaustion",
                "global_deadline_exhausted",
            },
            "medium",
            "medium",
            "high",
        ),
        (
            "incremental_warm_start_path",
            {"functional_nondeterminism"},
            "medium",
            "medium",
            "high",
        ),
        (
            "finalization_or_cad_path",
            {
                "certified_minimal_not_finalized",
                "finalized_plan_not_ready_for_fusion",
            },
            "medium",
            "high",
            "high",
        ),
        (
            "projection_or_certificate_path",
            {
                "product_domain_unsupported",
                "solver_solution_failed_current_recertification",
                "calculation_error",
            },
            "low",
            "high",
            "high",
        ),
    )
    for hypothesis, mapped, simplicity, maintenance, risk in mappings:
        target_count = sum(causes[value] for value in mapped)
        if target_count:
            candidates.append(
                {
                    "hypothesis_id": hypothesis,
                    "measured_target_count": target_count,
                    "measured_causes": sorted(
                        value for value in mapped if causes[value]
                    ),
                    "simplicity": simplicity,
                    "maintenance": maintenance,
                    "testability": "medium",
                    "probable_gain": (
                        f"at_most_{target_count}_open_cases_before_replay"
                    ),
                    "functional_risk": risk,
                }
            )
    total_losses = sum(causes.values())
    recommendation = (
        "no_algorithm_change_v1"
        if total_losses == 0
        else "causal_review_required_before_one_change"
    )
    return {
        "measured_loss_counts": dict(sorted(causes.items())),
        "candidates": candidates,
        "recommendation": recommendation,
        "selected_optimization_count": 0,
    }


def build_summary(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    losses = [
        {
            "case_id": row["case_id"],
            "split": row["split"],
            "stratum": row["stratum"],
            **deepcopy(dict(loss)),
        }
        for row in rows
        for loss in row.get("losses", [])
        if isinstance(loss, Mapping)
    ]
    first_runs = [
        row["runs"][0]
        for row in rows
        if isinstance(row.get("runs"), list) and row["runs"]
    ]
    return {
        "overall": _group_result(rows),
        "by_axis": {
            key: _group_summary(rows, key)
            for key in _GROUP_KEYS
        },
        "false_impossible_count": sum(
            value.get("status") == RESULT_PROVEN_IMPOSSIBLE
            for value in rows
        ),
        "uncertified_solution_count": sum(
            value.get("status") == RESULT_ERROR
            and any(
                isinstance(run, Mapping)
                and run.get("solver_status") == SOLVER_SOLUTION_FOUND
                for run in value.get("runs", [])
            )
            for value in rows
        ),
        "deterministic_replay_count": sum(
            value.get("deterministic") is not None for value in rows
        ),
        "deterministic_replay_pass_count": sum(
            value.get("deterministic") is True for value in rows
        ),
        "route_counts": dict(
            sorted(
                Counter(
                    str(dict(value.get("route", {})).get(
                        "lane_id",
                        "not_available",
                    ))
                    for value in first_runs
                ).items()
            )
        ),
        "external_status_counts": dict(
            sorted(
                Counter(
                    str(dict(value.get("route", {})).get(
                        "external_status",
                        "not_available",
                    ))
                    for value in first_runs
                ).items()
            )
        ),
        "loss_count": len(losses),
        "losses": losses,
        "hypothesis_comparison": _hypothesis_comparison(rows),
    }


def _checkpoint(
    path: Path,
    *,
    binding_digest: str,
    binding_payload: Mapping[str, object],
    resume: bool,
    recover_interrupted_case: str | None,
) -> dict[str, object]:
    if path.exists():
        if not resume:
            raise RuntimeError(
                "Checkpoint already exists; use --resume."
            )
        value = _read_json(path)
        supplied = value.pop("checkpoint_digest", None)
        if (
            value.get("schema_version") != CHECKPOINT_SCHEMA_VERSION
            or value.get("binding_digest") != binding_digest
            or value.get("binding_payload") != dict(binding_payload)
            or supplied != canonical_digest(value)
            or not isinstance(value.get("case_results"), dict)
        ):
            raise RuntimeError(
                "Reference checkpoint binding or digest mismatch."
            )
        value["checkpoint_digest"] = supplied
        active = value.get("active_case_id")
        if active is not None:
            if recover_interrupted_case != active:
                raise RuntimeError(
                    "Checkpoint has an ambiguous active case; verify no "
                    "campaign process remains, then pass the exact "
                    "--recover-interrupted-case id."
                )
            value["active_case_id"] = None
            _save_checkpoint(path, value)
        elif recover_interrupted_case is not None:
            raise RuntimeError(
                "No interrupted case exists in this checkpoint."
            )
        return value
    if resume:
        raise RuntimeError("Cannot --resume a missing checkpoint.")
    if recover_interrupted_case is not None:
        raise RuntimeError(
            "Cannot recover an interrupted case without a checkpoint."
        )
    value = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "binding_digest": binding_digest,
        "binding_payload": deepcopy(dict(binding_payload)),
        "active_case_id": None,
        "case_results": {},
    }
    value["checkpoint_digest"] = canonical_digest(value)
    _write_json_atomic(path, value)
    return value


def _save_checkpoint(
    path: Path,
    value: dict[str, object],
) -> None:
    value.pop("checkpoint_digest", None)
    value["checkpoint_digest"] = canonical_digest(value)
    _write_json_atomic(path, value)


def _validate_case_result(value: Mapping[str, object]) -> dict[str, object]:
    result = deepcopy(dict(value))
    supplied = result.pop("case_result_digest", None)
    if (
        result.get("schema_version") != CASE_RESULT_SCHEMA_VERSION
        or supplied != canonical_digest(result)
    ):
        raise RuntimeError("Checkpoint contains an invalid case result.")
    result["case_result_digest"] = supplied
    return result


def _report(
    *,
    inventory: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
    checkpoint: Mapping[str, object],
    binding_payload: Mapping[str, object],
    runtime_receipt: Mapping[str, object],
) -> dict[str, object]:
    case_results = dict(checkpoint["case_results"])
    rows = [
        _validate_case_result(case_results[str(record["case_id"])])
        for record in records
        if str(record["case_id"]) in case_results
    ]
    complete = len(rows) == len(records)
    result_digest_map = {
        str(value["case_id"]): str(value["case_result_digest"])
        for value in rows
    }
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mission": "P64-L09W-C",
        "status": "complete" if complete else "partial",
        "candidate": {
            "release_baseline": RELEASE_BASELINE,
            "code_bundle_digest": binding_payload[
                "code_bundle_digest"
            ],
            "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
            "solver_settings": deepcopy(DEFAULT_SETTINGS),
        },
        "corpus": deepcopy(dict(inventory)),
        "execution": {
            "python_version": (
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
            "platform": sys.platform,
            "repeat_count": binding_payload["repeat_count"],
            "completed_case_count": len(rows),
            "remaining_case_count": len(records) - len(rows),
            "checkpoint_digest": checkpoint["checkpoint_digest"],
            "case_result_set_digest": canonical_digest(
                result_digest_map
            ),
            "runtime_receipt_digest": runtime_receipt[
                "receipt_digest"
            ],
            "materialization_measured": False,
        },
        "summary": build_summary(rows),
        "bindings": {
            **deepcopy(dict(binding_payload)),
            "binding_digest": checkpoint["binding_digest"],
            "checkpoint_digest": checkpoint["checkpoint_digest"],
            "runtime_receipt_digest": runtime_receipt[
                "receipt_digest"
            ],
        },
        "invariants": {
            "open_positive_case_count": len(records),
            "negative_control_execution_count": 0,
            "holdout_file_read": False,
            "holdout_opening_count": 0,
            "holdout_solver_invocation_count": 0,
            "witness_disclosed_to_evaluated_solver": False,
            "solver_budget_changed": False,
            "physical_value_changed": False,
            "product_grid_changed": False,
            "geometry_epsilon_changed": False,
            "fusion_materialization_invocation_count": 0,
            "print_validated": False,
        },
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--worker-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--repeat-count", type=int, default=2)
    parser.add_argument("--max-new-records", type=int, required=True)
    parser.add_argument("--recover-interrupted-case")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError(
            "P64-L09W-C must run with the Fusion CPython 3.14 ABI."
        )
    if args.repeat_count < 2 or args.repeat_count > 3:
        raise ValueError("repeat-count must stay between 2 and 3.")
    if not 1 <= args.max_new_records <= MAX_BATCH_SIZE:
        raise ValueError(
            f"max-new-records must stay between 1 and {MAX_BATCH_SIZE}."
        )
    built = build_open_inventory(_read_json(args.manifest))
    records = list(built["records"])
    inventory = dict(built["inventory"])
    runtime_receipt = _validate_runtime_receipt(
        _read_json(args.runtime_receipt)
    )
    code_digest = _code_bundle_digest()
    binding_payload = {
        "manifest_digest": inventory["manifest_digest"],
        "regression_source": deepcopy(
            dict(built["manifest"]["regression_source"])
        ),
        "code_bundle_digest": code_digest,
        "runtime_artifact_digest": SCIP_PRODUCT_ARTIFACT_DIGEST,
        "runtime_receipt_digest": runtime_receipt["receipt_digest"],
        "solver_settings": deepcopy(DEFAULT_SETTINGS),
        "repeat_count": args.repeat_count,
    }
    binding_digest = canonical_digest(binding_payload)
    checkpoint = _checkpoint(
        args.checkpoint,
        binding_digest=binding_digest,
        binding_payload=binding_payload,
        resume=args.resume,
        recover_interrupted_case=args.recover_interrupted_case,
    )
    configure_scip_product_runtime(
        args.runtime_root,
        artifact_path=args.artifact,
        worker_root=args.worker_root,
        scratch_root=args.scratch_root,
    )

    completed = dict(checkpoint["case_results"])
    pending = [
        record
        for record in records
        if str(record["case_id"]) not in completed
    ]
    selected = pending[: args.max_new_records]
    initial_completed = len(completed)
    for record in selected:
        case_id = str(record["case_id"])
        checkpoint["active_case_id"] = case_id
        _save_checkpoint(args.checkpoint, checkpoint)
        result = run_open_case(
            record,
            repeat_count=args.repeat_count,
        )
        checkpoint["case_results"][case_id] = result
        checkpoint["active_case_id"] = None
        _save_checkpoint(args.checkpoint, checkpoint)
        print(
            "P64_L09W_C_CASE "
            f"completed={len(checkpoint['case_results'])}/"
            f"{len(records)} case={case_id} "
            f"status={result['status']} "
            f"losses={len(result['losses'])}",
            flush=True,
        )

    report = _report(
        inventory=inventory,
        records=records,
        checkpoint=checkpoint,
        binding_payload=binding_payload,
        runtime_receipt=runtime_receipt,
    )
    _write_json_atomic(args.output, report)
    print(
        "P64_L09W_C_BATCH_OK "
        f"status={report['status']} "
        f"new={len(checkpoint['case_results']) - initial_completed} "
        f"completed={len(checkpoint['case_results'])}/{len(records)} "
        f"checkpoint={checkpoint['checkpoint_digest']} "
        f"report={report['report_digest']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
