"""Mesure bornée de la lane HiGHS de sol face au portefeuille interne.

Le script n'ouvre aucun holdout et ne modifie aucun réglage produit. Il compare
le même corpus de régression avec le runtime HiGHS configuré puis absent, afin de
détecter une régression de latence ou de résultat avant toute décision de
quarantaine.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
import tracemalloc
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.highs_product_solver import (  # noqa: E402
    HIGHS_PRODUCT_VERSION,
    configure_highs_product_runtime,
)
from board_game_insert_generator.minimal_layout_solver import (  # noqa: E402
    _solve_minimal_layout_once,
)


SCHEMA = "bgig.highs_product_lane_diagnostic.v1"


def _percentile(values: Iterable[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _vendor_executable() -> Path:
    return (
        ROOT
        / "fusion_addin"
        / "BoardGameInsertGenerator"
        / "vendor"
        / "highs"
        / HIGHS_PRODUCT_VERSION
        / "windows-x86_64"
        / "bin"
        / "highs.exe"
    )


def _run_one(
    case: dict[str, Any],
    *,
    mode: str,
    executable: Path,
    scratch_root: Path,
) -> dict[str, object]:
    if mode == "internal_only":
        configure_highs_product_runtime(None)
    elif mode == "highs_configured":
        configure_highs_product_runtime(executable, scratch_root=scratch_root)
    else:
        raise ValueError(f"Unknown mode {mode!r}")

    tracemalloc.start()
    started_ns = time.perf_counter_ns()
    try:
        result = _solve_minimal_layout_once(
            case["project"],
            effort_profile=case["solver_settings"]["effort"],
            request_id=None,
            request_revision=None,
            cancel_check=None,
            container_frontiers=None,
            frontier_digests=(),
            external_lane_enabled=(mode == "highs_configured"),
        )
    finally:
        elapsed_ms = (time.perf_counter_ns() - started_ns) / 1_000_000
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    layout = result["minimal_layout"]
    provenance = layout["search_provenance"]
    external = provenance.get("external_lane")
    return {
        "mode": mode,
        "elapsed_ms": round(elapsed_ms, 3),
        "python_tracemalloc_peak_bytes": peak_bytes,
        "status": result["solver"]["result"]["status"],
        "certificate_digest": result.get("plan_digest", ""),
        "placement_digest": provenance.get("selected", {}).get("placement_digest", ""),
        "selected_source": provenance.get("selected", {}).get("candidate_source", ""),
        "external_lane": external,
    }


def _summary(samples: list[dict[str, object]]) -> dict[str, object]:
    elapsed = [float(sample["elapsed_ms"]) for sample in samples]
    peaks = [int(sample["python_tracemalloc_peak_bytes"]) for sample in samples]
    external = [sample.get("external_lane") for sample in samples]
    invocations = sum(
        int(item.get("invocation_count", 0))
        for item in external
        if isinstance(item, dict)
    )
    statuses = sorted(
        {
            str(item.get("status", "not_reported"))
            for item in external
            if isinstance(item, dict)
        }
    )
    selected_sources = sorted(
        {str(sample.get("selected_source", "")) for sample in samples}
    )
    return {
        "sample_count": len(samples),
        "selected_sources": selected_sources,
        "elapsed_ms": {
            "p50": round(_percentile(elapsed, 0.50), 3),
            "p95": round(_percentile(elapsed, 0.95), 3),
            "min": round(min(elapsed), 3),
            "max": round(max(elapsed), 3),
        },
        "python_tracemalloc_peak_bytes": max(peaks, default=0),
        "external_process_invocation_count": invocations,
        "external_statuses": statuses,
        "process_rss_bytes": "not_measured_without_extra_dependency",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "p64_l05d_solver_case_corpus.v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    if args.repetitions < 2:
        raise ValueError("At least two repetitions are required for P50/P95.")

    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    executable = _vendor_executable()
    if not executable.is_file():
        raise FileNotFoundError(executable)
    args.scratch_root.mkdir(parents=True, exist_ok=True)

    runs: dict[str, dict[str, list[dict[str, object]]]] = {}
    for case in corpus["cases"]:
        case_id = str(case["case_id"])
        runs[case_id] = {"internal_only": [], "highs_configured": []}
        for _ in range(args.repetitions):
            for mode in ("internal_only", "highs_configured"):
                runs[case_id][mode].append(
                    _run_one(
                        case,
                        mode=mode,
                        executable=executable,
                        scratch_root=args.scratch_root,
                    )
                )

    cases: list[dict[str, object]] = []
    for case in corpus["cases"]:
        case_id = str(case["case_id"])
        internal = _summary(runs[case_id]["internal_only"])
        highs = _summary(runs[case_id]["highs_configured"])
        p50_delta = round(
            float(highs["elapsed_ms"]["p50"])
            - float(internal["elapsed_ms"]["p50"]),
            3,
        )
        p95_delta = round(
            float(highs["elapsed_ms"]["p95"])
            - float(internal["elapsed_ms"]["p95"]),
            3,
        )
        internal_digests = {
            (sample["status"], sample["certificate_digest"])
            for sample in runs[case_id]["internal_only"]
        }
        highs_digests = {
            (sample["status"], sample["certificate_digest"])
            for sample in runs[case_id]["highs_configured"]
        }
        cases.append(
            {
                "case_id": case_id,
                "effort_profile": case["solver_settings"]["effort"],
                "internal_only": internal,
                "highs_configured": highs,
                "delta_elapsed_ms": {"p50": p50_delta, "p95": p95_delta},
                "result_signatures": {
                    "internal_only": sorted(internal_digests),
                    "highs_configured": sorted(highs_digests),
                },
            }
        )

    payload: dict[str, object] = {
        "schema_version": SCHEMA,
        "corpus": {
            "path": args.corpus.relative_to(ROOT).as_posix(),
            "digest": _canonical_digest(corpus),
            "case_count": len(corpus["cases"]),
        },
        "execution": {
            "repetitions": args.repetitions,
            "modes": ["internal_only", "highs_configured"],
            "highs_version": HIGHS_PRODUCT_VERSION,
            "network_invocation_count": 0,
            "holdout_opened": False,
            "memory_limit": "not_measured_without_extra_dependency",
        },
        "cases": cases,
    }
    payload["evidence_digest"] = _canonical_digest(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(args.output), "evidence_digest": payload["evidence_digest"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
