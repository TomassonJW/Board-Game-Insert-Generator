"""Récupère le verdict L08F sans rouvrir le holdout ni rappeler un worker."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from board_game_insert_generator.incremental_project_state import canonical_digest  # noqa: E402
from board_game_insert_generator.real_3d_solver_tournament import (  # noqa: E402
    REAL_3D_EVIDENCE_SCHEMA_V1,
    REAL_3D_HOLDOUT_CAMPAIGN_SCHEMA_V1,
    build_holdout_decision,
    sanitize_oracle_leaked_baseline_rows,
    summarize_rows,
    validate_selection_evidence,
)

RECOVERY_RECEIPT_SCHEMA = "bgig.real_3d_holdout_recovery_receipt.v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--initial-evidence", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()

    campaign = _validate_digest(_read(args.campaign), "campaign_digest")
    initial = _validate_digest(_read(args.initial_evidence), "evidence_digest")
    if campaign.get("schema_version") != REAL_3D_HOLDOUT_CAMPAIGN_SCHEMA_V1:
        raise ValueError("Unexpected holdout campaign schema.")
    if initial.get("schema_version") != REAL_3D_EVIDENCE_SCHEMA_V1:
        raise ValueError("Unexpected compact evidence schema.")
    if initial.get("holdout_campaign_digest") != campaign["campaign_digest"]:
        raise ValueError("Initial evidence is not bound to the supplied campaign.")
    if initial.get("opening_receipt", {}).get("holdout_opening_count") != 1:
        raise ValueError("Recovery requires the unique opening receipt.")

    selection = validate_selection_evidence(initial["selection"])
    if campaign.get("selection_digest") != selection["selection_digest"]:
        raise ValueError("Campaign and sealed selection differ.")
    baseline_rows = sanitize_oracle_leaked_baseline_rows(campaign["baseline_rows"])
    sanitized_count = sum("recovery" in value for value in baseline_rows)
    if sanitized_count != 10:
        raise ValueError(f"Expected 10 leaked baseline rows, got {sanitized_count}.")

    decision = build_holdout_decision(
        portfolio_rows=campaign["portfolio_rows"],
        primary_rows=campaign["primary_rows"],
        baseline_rows=baseline_rows,
        selected_candidate_ids=selection["selected_candidate_ids"],
        primary_candidate_id=selection["primary_candidate_id"],
    )
    script_digest = sha256(Path(__file__).read_bytes()).hexdigest()
    recovery = {
        "reason": "baseline_consumed_formal_corpus_bound_instead_of_solving",
        "contract_rule_reapplied": "portfolio_only_if_no_loss_and_better_than_primary",
        "initial_evidence_digest": initial["evidence_digest"],
        "holdout_campaign_digest": campaign["campaign_digest"],
        "selection_digest": selection["selection_digest"],
        "recovery_script_sha256": script_digest,
        "sanitized_baseline_row_count": sanitized_count,
        "external_worker_reexecution_count": 0,
        "baseline_worker_reexecution_count": 0,
        "private_holdout_reopen_count": 0,
        "post_open_tuning_count": 0,
        "selection_changed": False,
        "family_routes_changed": False,
        "candidate_settings_changed": False,
        "external_results_changed": False,
        "initial_selected_vs_current_bgig_invalidated": True,
        "initial_open_baseline_comparison_invalidated": True,
    }

    evidence = deepcopy(initial)
    evidence.pop("evidence_digest", None)
    evidence.pop("selected_vs_current_bgig", None)
    evidence["holdout_summaries"] = deepcopy(dict(evidence["holdout_summaries"]))
    evidence["holdout_summaries"]["baseline"] = summarize_rows(baseline_rows)
    evidence["holdout_summaries"]["retained"] = summarize_rows(decision["retained_rows"])
    evidence["portfolio_vs_primary"] = decision["portfolio_vs_primary"]
    evidence["retained_vs_current_bgig"] = decision["retained_vs_current_bgig"]
    evidence["verdict"] = decision["verdict"]
    evidence["recovery"] = recovery
    evidence["invariants"] = deepcopy(dict(evidence["invariants"]))
    evidence["invariants"].update(
        {
            "external_worker_reexecution_count": 0,
            "baseline_worker_reexecution_count": 0,
            "private_holdout_reopen_count": 0,
            "postprocessing_recovery_count": 1,
            "external_workers_referenced_oracle_metadata": False,
            "future_worker_inputs_strip_oracle_metadata": True,
        }
    )
    evidence["evidence_digest"] = canonical_digest(evidence)

    receipt = {
        "schema_version": RECOVERY_RECEIPT_SCHEMA,
        **recovery,
        "recovered_evidence_digest": evidence["evidence_digest"],
        "retained_candidate_ids": decision["verdict"]["retained_candidate_ids"],
        "benchmark_winner_demonstrated": decision["verdict"]["benchmark_winner_demonstrated"],
        "product_integration_authorized": decision["verdict"]["product_integration_authorized"],
    }
    receipt["recovery_receipt_digest"] = canonical_digest(receipt)
    _write(args.evidence_output, evidence)
    _write(args.receipt_output, receipt)
    print(
        "REAL_3D_TOURNAMENT_RECOVERY_OK "
        f"evidence={evidence['evidence_digest']} "
        f"receipt={receipt['recovery_receipt_digest']}",
        flush=True,
    )
    return 0


def _validate_digest(value: Mapping[str, object], digest_key: str) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop(digest_key, None)
    if supplied != canonical_digest(payload):
        raise ValueError(f"Invalid {digest_key}.")
    payload[digest_key] = supplied
    return payload


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
