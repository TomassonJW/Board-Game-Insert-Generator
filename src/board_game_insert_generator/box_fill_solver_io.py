"""File and legacy-plan adapters for the P20 BoxFill solver."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from board_game_insert_generator.asset_candidates import build_executable_asset_module_plan
from board_game_insert_generator.box_fill_solver import BoxFillCandidate, BoxFillSolveRequest
from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.models import AssetAllocation, BoxFillBox, BoxFillLayer, BoxFillPlan, Dimension3D, Point3D


def load_box_fill_solve_request(path: str | Path) -> BoxFillSolveRequest:
    request_path = Path(path)
    try:
        raw = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Invalid BoxFill solve request {path}: {exc}") from exc
    if set(raw) - {"schema_version", "source_config", "candidates"}:
        raise ConfigError("Unknown BoxFill solve request fields.")
    if raw.get("schema_version") != "box_fill_solve_request.v0":
        raise ConfigError("Unsupported solve request schema_version; expected 'box_fill_solve_request.v0'.")
    source = raw.get("source_config")
    if not isinstance(source, str):
        raise ConfigError("solve request source_config must be a string.")
    config = load_config(request_path.parent / source)
    if config.box_fill_plan is None:
        raise ConfigError("solve request source_config must declare box_fill_plan.")
    candidates = raw.get("candidates")
    if not isinstance(candidates, list):
        raise ConfigError("solve request candidates must be a list.")
    return BoxFillSolveRequest(config.box_fill_plan, tuple(_candidate(item) for item in candidates))


def solve_request_from_executable_asset_plan(config) -> BoxFillSolveRequest:
    """Bridge generated asset modules into explicit candidates with visible assumptions."""
    plan = config.box_fill_plan or BoxFillPlan(
        "box_fill_plan.v0", "derived:asset-first-source",
        BoxFillBox("derived-game-box", config.box.inner_dimensions, Point3D(0, 0, 0), config.box.usable_height_mm, config.box.lid_clearance_mm, config.units),
        config.assets, layers=(BoxFillLayer("derived-base-layer", 0.0, config.box.usable_height_mm, "derived"),),
        metadata={"source": "derived_from_executable_asset_plan", "bridge_warnings": ["No reservations, locks, layer intent or compartment geometry were inferred."]},
    )
    executable = build_executable_asset_module_plan(config)
    candidates = []
    for item in executable.get("generated_modules", []):
        size = item.get("printable_body_size_mm", {})
        asset_ids = item.get("source_asset_ids", [])
        allocations = tuple(AssetAllocation(asset_id, next(asset.quantity.count for asset in config.assets if asset.id == asset_id), item["module_id"], source="derived_from_executable_asset_plan") for asset_id in asset_ids if any(asset.id == asset_id for asset in config.assets))
        candidates.append(BoxFillCandidate(item["module_id"], item["module_id"], Dimension3D(size["x"], size["y"], size["z"]), allocations=allocations, source="derived_from_executable_asset_plan", metadata={"candidate_id": item.get("candidate_id"), "bridge_warnings": ["Layer and rotation constraints were not supplied by executable_asset_plan."]}))
    return BoxFillSolveRequest(plan, tuple(candidates))


def _candidate(raw: Any) -> BoxFillCandidate:
    if not isinstance(raw, dict) or set(raw) - {"module_id", "name", "size_mm", "allowed_layers", "allow_xy_rotation", "preferred_orientation", "priority", "source", "allocations", "metadata"}:
        raise ConfigError("Invalid candidate object or unknown candidate field.")
    size = raw.get("size_mm")
    if not isinstance(size, dict) or set(size) != {"x", "y", "z"}:
        raise ConfigError("candidate.size_mm must contain x, y and z.")
    allocations = tuple(AssetAllocation(str(entry["asset_id"]), int(entry["quantity"]), str(raw["module_id"]), entry.get("compartment_id"), source=str(raw.get("source", "manual"))) for entry in raw.get("allocations", []))
    return BoxFillCandidate(str(raw["module_id"]), str(raw.get("name", raw["module_id"])), Dimension3D(float(size["x"]), float(size["y"]), float(size["z"])), allocations, tuple(raw.get("allowed_layers", [])), bool(raw.get("allow_xy_rotation", False)), str(raw.get("preferred_orientation", "native")), int(raw.get("priority", 0)), str(raw.get("source", "manual")), dict(raw.get("metadata", {})))
