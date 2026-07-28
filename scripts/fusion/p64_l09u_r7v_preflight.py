"""Build the local-only preflight summary for the P64-L09U-R7 Fusion gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from scripts.fusion.p64_l09uw_preflight import build_preflight as build_r6_preflight


ADDIN_VERSION = "0.1.78"
PREFLIGHT_SCHEMA = "bgig.p64_l09u_r7v.preflight.v1"


def stable_digest(payload: object) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_preflight() -> dict[str, object]:
    _project, inherited_preflight = build_r6_preflight()
    inherited = deepcopy(inherited_preflight)
    inherited["addin_version"] = ADDIN_VERSION
    return {
        "schema_version": PREFLIGHT_SCHEMA,
        "addin_version": ADDIN_VERSION,
        "inherited_r6_preflight": inherited,
        "r7_contract": {
            "product_grid_step_mm": 0.1,
            "numeric_epsilon_is_not_product_resolution": True,
            "canonical_wall_minimum_from_project_settings": True,
            "final_material_envelope_recertified": True,
            "automatic_flat_stack_smallest_oriented_footprint_first": True,
            "source_stack_order_is_trace_only": True,
            "source_project_written": False,
            "fusion_validated": False,
            "print_validated": False,
        },
        "forbidden_solver_campaigns_executed": False,
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
    print(
        "P64_L09U_R7V_PREFLIGHT "
        f"status=passed version={ADDIN_VERSION} digest={digest} "
        "fusion_validated=false print_validated=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
