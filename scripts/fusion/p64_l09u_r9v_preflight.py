"""Build the local-only preflight summary for the P64-L09U-R9 Fusion gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Mapping

from board_game_insert_generator.contextual_local_analysis import (
    IncrementalLocalAnalysisEngine,
)
from board_game_insert_generator.minimal_layout_solver import (
    MINIMAL_LAYOUT_SOLVER_VERSION,
)
from board_game_insert_generator.staged_calculation import (
    StagedCalculationSession,
)
from scripts.fusion.p64_l09sv_preflight import recent_tray_project
from scripts.fusion.p64_l09u_r8v_preflight import (
    AUTHORIZED_EXCLUDED_TEST_MODULES,
    build_preflight as build_r8_preflight,
    stable_digest as stable_r8_digest,
)


ADDIN_VERSION = "0.1.80"
PREFLIGHT_SCHEMA = "bgig.p64_l09u_r9v.preflight.v1"
R9_SOLVER_VERSION = "p64-l09u-r9-c-v2"
R9_SELECTED_STATEMENT = (
    "best_certified_proposal_from_first_geometric_group_of_"
    "first_lane_within_budget"
)
AUTHORITATIVE_PLACEMENT_DIGEST = (
    "a3ef2f440a212ed29496fe50072e065a0c861388e6e55e68c548c2bf8817bc46"
)
AUTHORITATIVE_PROJECT_SHA256 = {
    "case02_plus": (
        "5e84fe6f5c0b3e5f046201d442c414504dd95d4db8e711169a2624485466d7dc"
    ),
    "case02_plus_plus": (
        "83e9e90a6bfd86b18d3a157077a0e63dc2f543ddab626adb2151e269e01d9743"
    ),
}
EXPECTED_DEEP_BUDGET = {
    "max_complete_candidates": 12,
    "max_elapsed_ms": 15_000,
    "max_placement_trials": 250_000,
    "max_search_states": 5_000,
    "max_total_elapsed_ms": 180_000,
}


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{label} must be an object.")
    return value


def _without_volatile_observations(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _without_volatile_observations(item)
            for key, item in value.items()
            if not str(key).endswith("observed_ms")
        }
    if isinstance(value, (list, tuple)):
        return [
            _without_volatile_observations(item)
            for item in value
        ]
    return value


def stable_digest(payload: object) -> str:
    canonical = json.dumps(
        _without_volatile_observations(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _performance_route_summary() -> dict[str, object]:
    project = recent_tray_project()
    settings = {"method": "auto", "effort": "deep"}
    engine = IncrementalLocalAnalysisEngine(
        project,
        effort_profile="deep",
    )
    session = StagedCalculationSession(
        project,
        solver_settings=settings,
    )
    session.synchronize(
        project,
        engine.snapshot(),
        solver_settings=settings,
        container_frontiers=engine.certified_frontiers(),
        frontier_digests=engine.frontier_digests(),
    )
    started = perf_counter()
    calculated = session.calculate_layout(
        request_id="p64-l09u-r9v-preflight",
        request_revision=0,
    )
    calculation_observed_ms = round(
        (perf_counter() - started) * 1000.0,
        3,
    )
    solver_result = _mapping(
        calculated.get("solver_result"),
        "solver result",
    )
    if solver_result.get("status") != "solution_found":
        raise RuntimeError(
            "The R9 preflight fixture has no certified solution."
        )
    partition = _mapping(
        calculated.get("partition"),
        "calculated partition",
    )
    minimal = _mapping(
        partition.get("minimal_layout"),
        "minimal layout",
    )
    provenance = _mapping(
        minimal.get("search_provenance"),
        "search provenance",
    )
    selected = _mapping(
        provenance.get("selected"),
        "selected proposal",
    )
    budget = _mapping(
        provenance.get("budget"),
        "Deep budget",
    )
    lanes = tuple(
        _mapping(value, "internal lane")
        for value in provenance.get("lanes", ())
    )
    if MINIMAL_LAYOUT_SOLVER_VERSION != R9_SOLVER_VERSION:
        raise RuntimeError(
            "The installed R9 minimal solver version is not selected."
        )
    if any(
        budget.get(key) != expected
        for key, expected in EXPECTED_DEEP_BUDGET.items()
    ):
        raise RuntimeError(
            "The R9 Deep budget diverges from the inherited budget."
        )
    if (
        provenance.get(
            "first_certified_geometric_group_authority"
        )
        is not True
        or selected.get("statement") != R9_SELECTED_STATEMENT
        or provenance.get("external_lane") is not None
        or len(lanes) != 1
        or not selected.get("placement_digest")
    ):
        raise RuntimeError(
            "The R9 certified internal prefix is not authoritative."
        )
    lane = lanes[0]
    telemetry = _mapping(
        lane.get("telemetry"),
        "internal lane telemetry",
    )
    return {
        "schema_version": "bgig.r9_performance_route_preflight.v1",
        "minimal_layout_solver_version": MINIMAL_LAYOUT_SOLVER_VERSION,
        "effort_profile": "deep",
        "calculation_observed_ms": calculation_observed_ms,
        "selected_statement": selected["statement"],
        "selected_placement_digest": selected["placement_digest"],
        "lane_prefix_ids": list(
            provenance.get("lane_prefix_ids", ())
        ),
        "internal_lane_count": len(lanes),
        "scip_call_count": 0,
        "external_lane_absent": True,
        "first_certified_geometric_group_authority": True,
        "certified_candidate_count": int(
            lane.get("certified_candidate_count", 0)
        ),
        "geometric_rank_group_count": int(
            lane.get("geometric_rank_group_count", 0)
        ),
        "geometric_candidate_count_skipped_after_authority": int(
            lane.get(
                "geometric_candidate_count_skipped_after_authority",
                0,
            )
        ),
        "search_states": int(
            telemetry.get("search_states", 0)
        ),
        "placement_trials": int(
            telemetry.get("placement_trials", 0)
        ),
        "admitted_complete_solutions": int(
            telemetry.get("admitted_complete_solutions", 0)
        ),
        "deep_budget": {
            key: int(budget[key])
            for key in EXPECTED_DEEP_BUDGET
        },
        "budget_increased": False,
    }


def build_preflight() -> dict[str, object]:
    inherited = deepcopy(build_r8_preflight())
    inherited_summary = {
        "addin_version": inherited["addin_version"],
        "preflight_digest": stable_r8_digest(inherited),
        "strict_subtractive_pipeline": inherited[
            "strict_subtractive_pipeline"
        ],
        "r8_contract": inherited["r8_contract"],
        "gate_status": inherited["gate_status"],
    }
    return {
        "schema_version": PREFLIGHT_SCHEMA,
        "addin_version": ADDIN_VERSION,
        "inherited_r8_preflight": inherited_summary,
        "performance_route": _performance_route_summary(),
        "personal_project_replay_contract": {
            "effort_profile": "deep",
            "placement_digest": AUTHORITATIVE_PLACEMENT_DIGEST,
            "source_sha256": dict(AUTHORITATIVE_PROJECT_SHA256),
            "source_project_written": False,
            "new_benchmark_or_corpus_created": False,
        },
        "authorized_suite": {
            "excluded_before_import": True,
            "excluded_module_count": len(
                AUTHORIZED_EXCLUDED_TEST_MODULES
            ),
            "excluded_modules": list(
                AUTHORIZED_EXCLUDED_TEST_MODULES
            ),
            "forbidden_solver_campaigns_executed": False,
        },
        "r9_contract": {
            "functional_result_0179_remains_authoritative": True,
            "product_grid_step_mm": 0.1,
            "numeric_epsilon_mm": 0.0001,
            "numeric_epsilon_is_not_product_resolution": True,
            "flat_positive_volume_mm3": 0.0,
            "flat_positive_body_count": 0,
            "flat_positive_union_count": 0,
            "new_printable_body_count_attributed_to_flat_items": 0,
            "budget_increased": False,
            "source_project_written": False,
            "fusion_validated": False,
            "print_validated": False,
        },
        "gate_status": "prepared_not_human_observed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    payload = build_preflight()
    digest = stable_digest(payload)
    if args.write_summary is not None:
        args.write_summary.parent.mkdir(parents=True, exist_ok=True)
        args.write_summary.write_text(
            json.dumps(
                {**payload, "preflight_digest": digest},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    route = payload["performance_route"]
    print(
        "P64_L09U_R9V_PREFLIGHT "
        f"status=passed version={ADDIN_VERSION} digest={digest} "
        f"solver={route['minimal_layout_solver_version']} "
        f"calculation_observed_ms={route['calculation_observed_ms']} "
        f"lanes={route['internal_lane_count']} "
        f"scip_calls={route['scip_call_count']} "
        "budget_increased=false source_project_written=false "
        "fusion_validated=false print_validated=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
