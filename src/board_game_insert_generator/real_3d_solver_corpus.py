"""Corpus P64-L08D des cas limites 3D, sans appel de solveur.

Les cas ouverts portent des recettes reproductibles et des témoins construits.
Le holdout garde ses recettes dans un sidecar privé ; le manifest public ne
contient que leur engagement cryptographique.
"""

from __future__ import annotations

from copy import deepcopy
import secrets
from typing import Mapping, Sequence

from .incremental_project_state import canonical_digest


MANIFEST_SCHEMA = "bgig.real_3d_solver_corpus.v1"
SEALED_HOLDOUT_SCHEMA = "bgig.real_3d_solver_holdout.v1"
HOLDOUT_RECEIPT_SCHEMA = "bgig.real_3d_solver_holdout_receipt.v1"
FAMILIES = (
    "layers",
    "support",
    "reservations",
    "access",
    "fragmentation",
    "variants",
    "many-containers",
    "many-assets",
    "mixed-extreme",
    "real-anonymized",
)
TIERS = ("small", "large", "xl")
_TIER_COUNTS = {"small": 8, "large": 32, "xl": 64}
_REVIEWED_SOURCE = {
    "fixture": "tests/fixtures/p64_l06a_reviewed_real_case.v1.json",
    "case_id": "real-18-containers-20-contents-normal",
    "bundle_digest": "0693aef760d92fb7b42f21210ec36efdda4ee738effbf237861cb5899c3f508d",
    "project_digest": "b5948ab249aded6c553ec004ca7074e66b1a73cab2493a10f874fb10137b6699",
}
_FAMILY_FEATURES = {
    "layers": ("xyz", "heterogeneous_layers", "stacking", "support"),
    "support": ("xyz", "stacking", "support", "multi_support"),
    "reservations": ("xyz", "lower_reservation", "upper_reservation"),
    "access": ("xyz", "stacking", "support", "top_down_access"),
    "fragmentation": ("xyz", "disjoint_regions", "near_saturation"),
    "variants": ("xyz", "p45_variant_front", "rotations"),
    "many-containers": ("xyz", "high_container_cardinality"),
    "many-assets": ("xyz", "high_content_cardinality", "content_assignment"),
    "mixed-extreme": (
        "xyz",
        "heterogeneous_layers",
        "stacking",
        "support",
        "multi_support",
        "lower_reservation",
        "upper_reservation",
        "top_down_access",
        "disjoint_regions",
        "p45_variant_front",
        "rotations",
        "high_container_cardinality",
        "high_content_cardinality",
        "content_assignment",
    ),
    "real-anonymized": ("xyz", "reviewed_bgig_source"),
}


class Real3DCorpusError(ValueError):
    pass


def build_open_case_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for family_index, family in enumerate(FAMILIES):
        for tier_index, tier in enumerate(TIERS):
            records.append(
                _build_record(
                    family,
                    tier,
                    seed=640_800 + family_index * 100 + tier_index,
                    split="discovery" if tier != "xl" else "tuning",
                    feasible=True,
                )
            )
        records.append(
            _build_record(
                family,
                "negative",
                seed=640_899 + family_index * 100,
                split="discovery",
                feasible=False,
            )
        )
    records.append(_build_reviewed_real_regression_record())
    return records


def build_sealed_holdout(*, campaign_nonce: str | None = None) -> dict[str, object]:
    nonce = campaign_nonce or secrets.token_hex(32)
    if len(nonce) != 64 or any(char not in "0123456789abcdef" for char in nonce):
        raise Real3DCorpusError("Holdout nonce must contain 256 lowercase hex bits.")
    records: list[dict[str, object]] = []
    for family_index, family in enumerate(FAMILIES):
        for tier_index, tier in enumerate(TIERS):
            records.append(
                _build_record(
                    family,
                    f"holdout-{tier}",
                    seed=_seed_from_nonce(
                        nonce, family, family_index * len(TIERS) + tier_index
                    ),
                    split="holdout",
                    feasible=True,
                )
            )
        records.append(
            _build_record(
                family,
                "holdout-negative",
                seed=_seed_from_nonce(nonce, family, 100 + family_index),
                split="holdout",
                feasible=False,
            )
        )
    payload: dict[str, object] = {
        "schema_version": SEALED_HOLDOUT_SCHEMA,
        "campaign_nonce": nonce,
        "case_records": records,
        "solver_invocation_count": 0,
        "opened": False,
    }
    payload["sealed_holdout_digest"] = canonical_digest(payload)
    return payload


def build_public_manifest(
    open_records: Sequence[Mapping[str, object]],
    sealed_holdout: Mapping[str, object],
) -> dict[str, object]:
    accepted_open = [validate_case_record(record) for record in open_records]
    accepted_holdout = validate_sealed_holdout(sealed_holdout)
    receipt = {
        "schema_version": HOLDOUT_RECEIPT_SCHEMA,
        "sealed_holdout_digest": accepted_holdout["sealed_holdout_digest"],
        "case_count": len(accepted_holdout["case_records"]),
        "family_count": len(FAMILIES),
        "tier_counts": {tier: len(FAMILIES) for tier in TIERS},
        "positive_case_count": len(FAMILIES) * len(TIERS),
        "negative_case_count": len(FAMILIES),
        "opened": False,
        "solver_invocation_count": 0,
    }
    payload: dict[str, object] = {
        "schema_version": MANIFEST_SCHEMA,
        "families": list(FAMILIES),
        "family_features": {
            family: list(features) for family, features in _FAMILY_FEATURES.items()
        },
        "open_case_records": accepted_open,
        "open_case_count": len(accepted_open),
        "sealed_holdout_receipt": receipt,
        "invariants": {
            "full_3d_coordinates": True,
            "positive_witness_required": True,
            "negative_bound_required": True,
            "holdout_all_load_tiers": True,
            "holdout_recipes_embedded": False,
            "l06_l07_holdouts_reused": False,
            "solver_invocation_count": 0,
        },
    }
    payload["manifest_digest"] = canonical_digest(payload)
    return validate_public_manifest(payload)


def validate_public_manifest(value: Mapping[str, object]) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop("manifest_digest", None)
    if (
        payload.get("schema_version") != MANIFEST_SCHEMA
        or supplied != canonical_digest(payload)
    ):
        raise Real3DCorpusError("Invalid real 3D corpus manifest digest or schema.")
    records = payload.get("open_case_records")
    if not isinstance(records, list):
        raise Real3DCorpusError("Open case records are missing.")
    accepted = [validate_case_record(record) for record in records]
    if payload.get("open_case_count") != len(accepted):
        raise Real3DCorpusError("Open case count mismatch.")
    if set(payload.get("families", [])) != set(FAMILIES):
        raise Real3DCorpusError("Required 3D families are incomplete.")
    _validate_family_distribution(accepted, holdout=False)
    receipt = payload.get("sealed_holdout_receipt")
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema_version") != HOLDOUT_RECEIPT_SCHEMA
        or not _is_lower_hex_digest(receipt.get("sealed_holdout_digest"))
        or receipt.get("opened") is not False
        or receipt.get("solver_invocation_count") != 0
        or receipt.get("case_count") != len(FAMILIES) * (len(TIERS) + 1)
        or receipt.get("positive_case_count") != len(FAMILIES) * len(TIERS)
        or receipt.get("negative_case_count") != len(FAMILIES)
        or receipt.get("tier_counts") != {tier: len(FAMILIES) for tier in TIERS}
    ):
        raise Real3DCorpusError("Sealed holdout receipt is invalid.")
    if "case_records" in receipt or "campaign_nonce" in receipt:
        raise Real3DCorpusError("Public manifest leaks sealed recipes.")
    payload["manifest_digest"] = supplied
    return payload


def verify_sealed_holdout(
    manifest: Mapping[str, object], sealed_holdout: Mapping[str, object]
) -> dict[str, object]:
    accepted_manifest = validate_public_manifest(manifest)
    accepted_holdout = validate_sealed_holdout(sealed_holdout)
    receipt = accepted_manifest["sealed_holdout_receipt"]
    if receipt["sealed_holdout_digest"] != accepted_holdout["sealed_holdout_digest"]:
        raise Real3DCorpusError("Sealed holdout does not match its public receipt.")
    return {
        "status": "verified_closed",
        "case_count": receipt["case_count"],
        "sealed_holdout_digest": receipt["sealed_holdout_digest"],
        "solver_invocation_count": 0,
    }


def validate_sealed_holdout(value: Mapping[str, object]) -> dict[str, object]:
    payload = deepcopy(dict(value))
    supplied = payload.pop("sealed_holdout_digest", None)
    if (
        payload.get("schema_version") != SEALED_HOLDOUT_SCHEMA
        or supplied != canonical_digest(payload)
    ):
        raise Real3DCorpusError("Invalid sealed 3D holdout.")
    nonce = payload.get("campaign_nonce")
    records = payload.get("case_records")
    if (
        not _is_lower_hex_digest(nonce)
        or not isinstance(records, list)
    ):
        raise Real3DCorpusError("Sealed holdout recipe is incomplete.")
    accepted = [validate_case_record(record) for record in records]
    _validate_family_distribution(accepted, holdout=True)
    if payload.get("opened") is not False or payload.get("solver_invocation_count") != 0:
        raise Real3DCorpusError("Holdout must remain closed and unused.")
    payload["sealed_holdout_digest"] = supplied
    return payload


def validate_case_record(value: Mapping[str, object]) -> dict[str, object]:
    record = deepcopy(dict(value))
    supplied = record.pop("case_digest", None)
    if supplied != canonical_digest(record):
        raise Real3DCorpusError("Case digest mismatch.")
    family = record.get("family")
    if family not in FAMILIES or record.get("split") not in {
        "discovery",
        "tuning",
        "holdout",
        "regression",
    }:
        raise Real3DCorpusError("Case family or split is invalid.")
    recipe = record.get("recipe")
    if not isinstance(recipe, dict):
        raise Real3DCorpusError("Case recipe is missing.")
    _validate_recipe(family, recipe)
    problem = materialize_case_problem(record)
    if record.get("problem_digest") != canonical_digest(problem):
        raise Real3DCorpusError("Case problem commitment mismatch.")
    if record.get("expected") == "feasible":
        witness = materialize_positive_witness(record)
        validate_positive_witness(record, witness)
        if record.get("witness_digest") != canonical_digest(witness):
            raise Real3DCorpusError("Positive witness commitment mismatch.")
    elif record.get("expected") == "infeasible":
        _validate_negative_bound(family, record.get("infeasibility_bound"))
    elif record.get("expected") == "bounded_unknown":
        if (
            family != "real-anonymized"
            or recipe.get("input_kind") != "reviewed_bgig_project_reference"
            or record.get("baseline_status") != "no_solution_within_budget"
        ):
            raise Real3DCorpusError("Only the reviewed real regression may be unknown.")
    else:
        raise Real3DCorpusError("Case expectation is invalid.")
    record["case_digest"] = supplied
    return record


def materialize_case_problem(
    record: Mapping[str, object],
) -> dict[str, object]:
    recipe = dict(record["recipe"])
    family = str(record["family"])
    if recipe.get("input_kind") == "reviewed_bgig_project_reference":
        return {
            "input_kind": recipe["input_kind"],
            "source": deepcopy(recipe["source"]),
            "project_digest": recipe["project_digest"],
            "container_count": recipe["container_count"],
            "content_count": recipe["content_count"],
            "baseline_status": "no_solution_within_budget",
            "semantic_reduction": "none",
        }
    participants = []
    for index in range(int(recipe["container_count"])):
        base_size = _participant_base_size(family, recipe, index)
        variant_count = _variant_count(recipe, index)
        variants = []
        for ordinal in range(variant_count):
            delta = recipe["variant_outer_size_deltas_mm"][ordinal]
            variants.append(
                {
                    "variant_id": f"v{ordinal}",
                    "size": [
                        base_size[0] + delta[0],
                        base_size[1] + delta[1],
                        base_size[2],
                    ],
                    "allowed_rotations": list(recipe["allowed_rotations"]),
                    "p45_certified": True,
                }
            )
        participants.append(
            {
                "participant_id": f"container-{index:03d}",
                "variants": variants,
                "assigned_content_count": _assigned_content_count(recipe, index),
                "minimum_support_count": (
                    2
                    if family in {"support", "mixed-extreme"} and index == 2
                    else 1
                ),
                "support_coverage_ratio": recipe["support_coverage_ratio"],
            }
        )
    return {
        "case_seed": recipe["seed"],
        "world_mm": list(recipe["world_mm"]),
        "participants": participants,
        "reservation_volumes": deepcopy(recipe["reservation_volumes"]),
        "fragment_cell_mm": list(recipe["fragment_cell_mm"]),
        "fragment_gap_mm": recipe["fragment_gap_mm"],
        "access_policy": recipe["access_policy"],
        "active_constraints": list(recipe["active_constraints"]),
        "project_mode": recipe["project_mode"],
    }


def materialize_positive_witness(record: Mapping[str, object]) -> dict[str, object]:
    recipe = dict(record["recipe"])
    family = str(record["family"])
    count = int(recipe["container_count"])
    layers = int(recipe["layer_count"])
    placements: list[dict[str, object]] = []
    if family in {"support", "mixed-extreme"}:
        placements.extend(
            [
                _placement(recipe, 0, 2, 2, 0, [5, 10, 4], [], 0),
                _placement(recipe, 1, 7, 2, 0, [5, 10, 4], [], 0),
                _placement(
                    recipe,
                    2,
                    2,
                    2,
                    4,
                    [10, 10, recipe["layer_heights_mm"][1]],
                    ["container-000", "container-001"],
                    1,
                ),
            ]
        )
        start_index = 3
        row_offset = 1
    else:
        start_index = 0
        row_offset = 0
    for index in range(start_index, count):
        local_index = index - start_index
        layer = local_index % layers
        slot = local_index // layers
        columns = int(recipe["columns"])
        if row_offset and slot < columns - 1:
            column = slot + 1
            row = 0
        elif row_offset:
            adjusted_slot = slot - (columns - 1)
            column = adjusted_slot % columns
            row = 1 + adjusted_slot // columns
        else:
            column = slot % columns
            row = slot // columns
        z = sum(recipe["layer_heights_mm"][:layer])
        support_ids = (
            []
            if layer == 0
            else [f"container-{index - 1:03d}"]
        )
        placements.append(
            _placement(
                recipe,
                index,
                2 + int(recipe["cell_stride_mm"]) * column,
                2 + int(recipe["cell_stride_mm"]) * row,
                z,
                _participant_base_size(family, recipe, index),
                support_ids,
                layer,
            )
        )
    return {"placements": placements, "constructed_without_solver": True}


def validate_positive_witness(
    record: Mapping[str, object], witness: Mapping[str, object]
) -> None:
    recipe = dict(record["recipe"])
    family = str(record["family"])
    world = recipe["world_mm"]
    placements = witness.get("placements")
    if not isinstance(placements, list) or len(placements) != recipe["container_count"]:
        raise Real3DCorpusError("Witness participant count mismatch.")
    placements_by_id = {str(item["participant_id"]): item for item in placements}
    if len(placements_by_id) != len(placements):
        raise Real3DCorpusError("Witness participant identifiers are not unique.")
    problem = materialize_case_problem(record)
    participants_by_id = {
        str(item["participant_id"]): item for item in problem["participants"]
    }
    content_total = 0
    for index, item in enumerate(placements):
        for axis, limit, size_index in (
            ("x", world[0], 0),
            ("y", world[1], 1),
            ("z", world[2], 2),
        ):
            if item[axis] < 0 or item[axis] + item["size"][size_index] > limit:
                raise Real3DCorpusError("Witness placement is outside the 3D world.")
        for other in placements[index + 1 :]:
            if _overlap_3d(item, other):
                raise Real3DCorpusError("Witness placements overlap.")
        if item["orientation"] not in recipe["allowed_rotations"]:
            raise Real3DCorpusError("Witness uses a forbidden rotation.")
        participant = participants_by_id.get(str(item["participant_id"]))
        if participant is None:
            raise Real3DCorpusError("Witness participant is absent from the problem.")
        selected = next(
            (
                variant
                for variant in participant["variants"]
                if variant["variant_id"] == item["selected_variant_id"]
            ),
            None,
        )
        if selected is None or selected["size"] != item["size"]:
            raise Real3DCorpusError("Witness variant is not in the certified front.")
        if item["assigned_content_count"] != participant["assigned_content_count"]:
            raise Real3DCorpusError("Witness changes the assigned contents.")
        content_total += int(item["assigned_content_count"])
        support_ids = item["support_ids"]
        if item["z"] > 0 and not support_ids:
            raise Real3DCorpusError("Elevated witness placement has no support.")
        if support_ids:
            supports = []
            for support_id in support_ids:
                support = placements_by_id.get(str(support_id))
                if support is None:
                    raise Real3DCorpusError("Witness references an unknown support.")
                if support["z"] + support["size"][2] != item["z"]:
                    raise Real3DCorpusError(
                        "Witness support is not directly below its load."
                    )
                supports.append(support)
            required_area = item["size"][0] * item["size"][1]
            if _covered_area(item, supports) < required_area:
                raise Real3DCorpusError("Witness support coverage is incomplete.")
    if content_total != recipe["content_count"]:
        raise Real3DCorpusError("Witness content assignment is incomplete.")
    for reservation in recipe["reservation_volumes"]:
        if any(_overlap_3d(item, reservation) for item in placements):
            raise Real3DCorpusError("Witness intersects an active reservation.")
    if "top_down_access" in recipe["active_constraints"]:
        _validate_top_down_access(placements)
    if "disjoint_regions" in recipe["active_constraints"]:
        for item in placements:
            if not _fits_fragment_cell(item, recipe):
                raise Real3DCorpusError("Witness crosses a fragmented allowed region.")
    if "heterogeneous_layers" in recipe["active_constraints"]:
        used_z = {int(item["z"]) for item in placements}
        if (
            len(used_z) != recipe["layer_count"]
            or len(set(recipe["layer_heights_mm"])) < 2
        ):
            raise Real3DCorpusError("Witness does not exercise heterogeneous layers.")
    if "multi_support" in recipe["active_constraints"] and not any(
        len(item["support_ids"]) >= 2 for item in placements
    ):
        raise Real3DCorpusError("Witness has no multi-support load.")


def _build_record(
    family: str, tier: str, *, seed: int, split: str, feasible: bool
) -> dict[str, object]:
    base_tier = tier.removeprefix("holdout-")
    count = _TIER_COUNTS.get(base_tier, 64)
    if family == "many-containers":
        count = max(count, 32 if base_tier != "xl" else 64)
    elif family == "mixed-extreme":
        count = {
            "small": 32,
            "large": 64,
            "xl": 158,
        }.get(base_tier, 158)
    source_kind = "constructed_adversarial"
    source = None
    if family == "real-anonymized":
        scale = {"small": 1, "large": 2, "xl": 4}.get(base_tier, 4)
        count = 18 * scale
        source_kind = (
            "reviewed_anonymized_bgig_case"
            if scale == 1
            else "scaled_from_reviewed_anonymized_bgig_case"
        )
        source = dict(_REVIEWED_SOURCE, scale_factor=scale)
    layers = (
        5
        if family in {"layers", "mixed-extreme"} and base_tier == "xl"
        else 3
        if family in {"layers", "support", "access", "mixed-extreme"}
        else 1
    )
    base_heights = [4, 5, 6, 4, 5]
    height_shift = 0 if family in {"support", "mixed-extreme"} else seed % layers
    layer_heights = (
        base_heights[height_shift:layers] + base_heights[:height_shift]
    )
    columns = 8
    special_count = 3 if family in {"support", "mixed-extreme"} else 0
    regular_count = max(0, count - special_count)
    regular_slots = (regular_count + layers - 1) // layers
    if special_count:
        remaining_slots = max(0, regular_slots - (columns - 1))
        regular_rows = 1 + (remaining_slots + columns - 1) // columns
    else:
        regular_rows = max(1, (regular_slots + columns - 1) // columns)
    row_offset = 1 if special_count else 0
    tier_slack = {"small": 2, "large": 1, "xl": 0}.get(base_tier, 0)
    cell_stride = (
        12
        if family in {"fragmentation", "mixed-extreme"}
        else 10 + tier_slack
    )
    world = [
        columns * cell_stride + 3,
        regular_rows * cell_stride + 3,
        sum(layer_heights) + tier_slack,
    ]
    content_count = count * 4
    if family == "real-anonymized":
        content_count = 20 * int(source["scale_factor"])
    if family in {"many-assets", "mixed-extreme"}:
        content_count = max(content_count, 256)
    variant_cycle = (
        [8]
        if family == "mixed-extreme"
        else [1, 2, 4, 8]
        if family == "variants"
        else [1]
    )
    reservations: list[dict[str, object]] = []
    if family in {"reservations", "mixed-extreme"}:
        reservations = [
            {
                "reservation_id": "lower-booklet-clearance",
                "zone": "lower",
                "x": 0,
                "y": 0,
                "z": 0,
                "size": [1, world[1], min(6, world[2])],
            },
            {
                "reservation_id": "upper-board-clearance",
                "zone": "upper",
                "x": world[0] - 1,
                "y": 0,
                "z": max(0, world[2] - 6),
                "size": [1, world[1], min(6, world[2])],
            },
        ]
    recipe: dict[str, object] = {
        "seed": seed,
        "container_count": count,
        "content_count": content_count,
        "layer_count": layers,
        "layer_heights_mm": layer_heights,
        "columns": columns,
        "regular_rows": regular_rows,
        "cell_stride_mm": cell_stride,
        "difficulty_profile": {
            "small": "exact-control",
            "large": "adversarial",
            "xl": "adversarial-xl",
        }.get(base_tier, "formal-negative"),
        "world_mm": world,
        "active_constraints": list(_FAMILY_FEATURES[family]),
        "allowed_rotations": ["xyz", "yxz"],
        "variant_front_cycle": variant_cycle,
        "variant_outer_size_deltas_mm": [
            [0, 0],
            [-1, 0],
            [-1, -1],
            [-2, -1],
            [-2, -2],
            [-3, -2],
            [-3, -3],
            [-4, -3],
        ],
        "support_coverage_ratio": 1.0,
        "reservation_volumes": reservations,
        "fragment_cell_mm": [10, 10, max(layer_heights)],
        "fragment_gap_mm": cell_stride - 10,
        "access_policy": (
            "top_down"
            if family in {"access", "mixed-extreme"}
            else "unconstrained"
        ),
        "project_mode": (
            "cold_and_incremental_replay"
            if family == "mixed-extreme"
            else "cold"
        ),
        "source_kind": source_kind,
    }
    if source is not None:
        recipe["source"] = source
    record: dict[str, object] = {
        "case_id": f"p64-l08d-{split}-{family}-{tier}",
        "split": split,
        "family": family,
        "tier": tier,
        "expected": "feasible" if feasible else "infeasible",
        "recipe": recipe,
    }
    record["problem_digest"] = canonical_digest(materialize_case_problem(record))
    if feasible:
        record["witness_digest"] = canonical_digest(
            materialize_positive_witness(record)
        )
    else:
        record["infeasibility_bound"] = _negative_bound(family, recipe)
    record["case_digest"] = canonical_digest(record)
    return record


def _build_reviewed_real_regression_record() -> dict[str, object]:
    recipe: dict[str, object] = {
        "input_kind": "reviewed_bgig_project_reference",
        "source": dict(_REVIEWED_SOURCE),
        "project_digest": _REVIEWED_SOURCE["project_digest"],
        "container_count": 18,
        "content_count": 20,
        "active_constraints": list(_FAMILY_FEATURES["real-anonymized"]),
        "source_kind": "reviewed_anonymized_bgig_case",
    }
    record: dict[str, object] = {
        "case_id": "p64-l08d-regression-real-18-containers-20-contents",
        "split": "regression",
        "family": "real-anonymized",
        "tier": "reviewed-real",
        "expected": "bounded_unknown",
        "baseline_status": "no_solution_within_budget",
        "recipe": recipe,
    }
    record["problem_digest"] = canonical_digest(materialize_case_problem(record))
    record["case_digest"] = canonical_digest(record)
    return record


def _placement(
    recipe: Mapping[str, object],
    index: int,
    x: int,
    y: int,
    z: int,
    size: list[int],
    support_ids: list[str],
    layer_index: int,
) -> dict[str, object]:
    assigned = _assigned_content_count(recipe, index)
    variant_count = _variant_count(recipe, index)
    if "p45_variant_front" in recipe["active_constraints"]:
        variant_ordinal = (
            index % variant_count
            if int(recipe["layer_count"]) == 1
            else min(layer_index, variant_count - 1)
        )
    else:
        variant_ordinal = 0
    delta = recipe["variant_outer_size_deltas_mm"][variant_ordinal]
    selected_size = [size[0] + delta[0], size[1] + delta[1], size[2]]
    return {
        "participant_id": f"container-{index:03d}",
        "x": x,
        "y": y,
        "z": z,
        "size": selected_size,
        "orientation": recipe["allowed_rotations"][index % len(recipe["allowed_rotations"])],
        "selected_variant_id": f"v{variant_ordinal}",
        "assigned_content_count": assigned,
        "support_ids": support_ids,
        "removal_rank": int(recipe["layer_count"]) - 1 - layer_index,
    }


def _participant_base_size(
    family: str, recipe: Mapping[str, object], index: int
) -> list[int]:
    if family in {"support", "mixed-extreme"}:
        if index in {0, 1}:
            return [5, 10, 4]
        if index == 2:
            return [10, 10, int(recipe["layer_heights_mm"][1])]
        local_index = index - 3
    else:
        local_index = index
    layer_count = int(recipe["layer_count"])
    layer = local_index % layer_count
    stack = local_index // layer_count
    mixed_seed = _seed_from_nonce(
        f"{int(recipe['seed']):064x}"[-64:],
        "participant-footprint",
        stack,
    )
    width = 10 - mixed_seed % 2
    depth = 10 - (mixed_seed // 2) % 2
    return [width, depth, int(recipe["layer_heights_mm"][layer])]


def _assigned_content_count(recipe: Mapping[str, object], index: int) -> int:
    content_count = int(recipe["content_count"])
    container_count = int(recipe["container_count"])
    return content_count // container_count + (
        1 if index < content_count % container_count else 0
    )


def _validate_recipe(family: str, recipe: Mapping[str, object]) -> None:
    if recipe.get("input_kind") == "reviewed_bgig_project_reference":
        source = recipe.get("source")
        if (
            family != "real-anonymized"
            or set(recipe.get("active_constraints", []))
            != set(_FAMILY_FEATURES["real-anonymized"])
            or not isinstance(source, dict)
            or source != _REVIEWED_SOURCE
            or recipe.get("project_digest") != _REVIEWED_SOURCE["project_digest"]
            or recipe.get("container_count") != 18
            or recipe.get("content_count") != 20
        ):
            raise Real3DCorpusError("Reviewed BGIG project reference is invalid.")
        return
    world = recipe.get("world_mm")
    if (
        not isinstance(world, list)
        or len(world) != 3
        or any(not isinstance(value, int) or value <= 0 for value in world)
        or not isinstance(recipe.get("container_count"), int)
        or recipe["container_count"] <= 0
        or not isinstance(recipe.get("content_count"), int)
        or recipe["content_count"] < 0
        or recipe.get("allowed_rotations") != ["xyz", "yxz"]
    ):
        raise Real3DCorpusError("Case dimensions or cardinalities are invalid.")
    if set(recipe.get("active_constraints", [])) != set(_FAMILY_FEATURES[family]):
        raise Real3DCorpusError("Case does not activate its complete family contract.")
    layers = int(recipe.get("layer_count", 0))
    heights = recipe.get("layer_heights_mm")
    if not isinstance(heights, list) or len(heights) != layers or layers < 1:
        raise Real3DCorpusError("Layer recipe is inconsistent.")
    if "heterogeneous_layers" in recipe["active_constraints"]:
        if not 2 <= layers <= 5 or len(set(heights)) < 2:
            raise Real3DCorpusError("Layer family lacks heterogeneous levels.")
    if "multi_support" in recipe["active_constraints"] and recipe["container_count"] < 3:
        raise Real3DCorpusError("Multi-support recipe is too small.")
    if {"lower_reservation", "upper_reservation"} <= set(
        recipe["active_constraints"]
    ):
        zones = {value.get("zone") for value in recipe["reservation_volumes"]}
        if not {"lower", "upper"} <= zones:
            raise Real3DCorpusError("Lower and upper reservations are required.")
    if "p45_variant_front" in recipe["active_constraints"]:
        cycle = set(recipe["variant_front_cycle"])
        if not {1, 2, 4, 8} <= cycle and cycle != {8}:
            raise Real3DCorpusError("P45 variant front is incomplete.")
    if (
        "high_container_cardinality" in recipe["active_constraints"]
        and recipe["container_count"] < 32
    ):
        raise Real3DCorpusError("High-container case is below 32 groups.")
    if (
        "high_content_cardinality" in recipe["active_constraints"]
        and recipe["content_count"] < 256
    ):
        raise Real3DCorpusError("High-content case is below 256 contents.")
    if family == "real-anonymized":
        source = recipe.get("source")
        if (
            not isinstance(source, dict)
            or source.get("case_id") != _REVIEWED_SOURCE["case_id"]
            or source.get("bundle_digest") != _REVIEWED_SOURCE["bundle_digest"]
        ):
            raise Real3DCorpusError("Reviewed BGIG source receipt is missing.")


def _negative_bound(
    family: str, recipe: Mapping[str, object]
) -> dict[str, object]:
    if family == "layers":
        return {
            "kind": "required_stack_height_exceeds_world",
            "world_height_mm": recipe["world_mm"][2],
            "required_stack_height_mm": recipe["world_mm"][2] + 1,
        }
    if family == "support":
        return {
            "kind": "required_support_area_exceeds_available",
            "available_support_area_mm2": 100,
            "required_support_area_mm2": 101,
        }
    if family == "reservations":
        capacity = _usable_volume(recipe)
        return {
            "kind": "required_volume_exceeds_unreserved_capacity",
            "unreserved_capacity_mm3": capacity,
            "required_volume_mm3": capacity + 1,
        }
    if family == "access":
        return {
            "kind": "top_down_precedence_cycle",
            "cycle": ["container-a", "container-b", "container-a"],
        }
    if family == "fragmentation":
        return {
            "kind": "item_axis_exceeds_every_fragment",
            "largest_fragment_axis_mm": recipe["fragment_cell_mm"][0],
            "required_item_axis_mm": recipe["fragment_cell_mm"][0] + 1,
        }
    if family == "variants":
        return {
            "kind": "no_certified_variant_fits_world",
            "certified_variant_count": 8,
            "fitting_variant_count": 0,
        }
    capacity = _usable_volume(recipe)
    return {
        "kind": "required_volume_exceeds_capacity",
        "capacity_volume_mm3": capacity,
        "required_volume_mm3": capacity + 1,
    }


def _validate_negative_bound(family: str, value: object) -> None:
    if not isinstance(value, dict):
        raise Real3DCorpusError("Negative case has no formal bound.")
    expected_kinds = {
        "layers": "required_stack_height_exceeds_world",
        "support": "required_support_area_exceeds_available",
        "reservations": "required_volume_exceeds_unreserved_capacity",
        "access": "top_down_precedence_cycle",
        "fragmentation": "item_axis_exceeds_every_fragment",
        "variants": "no_certified_variant_fits_world",
    }
    expected_kind = expected_kinds.get(
        family, "required_volume_exceeds_capacity"
    )
    try:
        if family == "layers":
            valid = value["required_stack_height_mm"] > value["world_height_mm"]
        elif family == "support":
            valid = value["required_support_area_mm2"] > value["available_support_area_mm2"]
        elif family == "reservations":
            valid = value["required_volume_mm3"] > value["unreserved_capacity_mm3"]
        elif family == "access":
            cycle = value.get("cycle", [])
            valid = len(cycle) >= 3 and cycle[0] == cycle[-1]
        elif family == "fragmentation":
            valid = value["required_item_axis_mm"] > value["largest_fragment_axis_mm"]
        elif family == "variants":
            valid = value["certified_variant_count"] > 0 and value["fitting_variant_count"] == 0
        else:
            valid = value["required_volume_mm3"] > value["capacity_volume_mm3"]
    except (KeyError, TypeError):
        valid = False
    if value.get("kind") != expected_kind or not valid:
        raise Real3DCorpusError("Negative bound does not prove its announced scope.")


def _validate_family_distribution(
    records: Sequence[Mapping[str, object]], *, holdout: bool
) -> None:
    expected_tiers = {
        *(f"holdout-{tier}" if holdout else tier for tier in TIERS),
        "holdout-negative" if holdout else "negative",
    }
    core_records = [record for record in records if record["tier"] in expected_tiers]
    extra_records = [record for record in records if record["tier"] not in expected_tiers]
    expected_count = len(FAMILIES) * len(expected_tiers)
    if len(core_records) != expected_count:
        raise Real3DCorpusError("Corpus family distribution has the wrong size.")
    for family in FAMILIES:
        family_records = [
            record for record in core_records if record["family"] == family
        ]
        if (
            len(family_records) != len(expected_tiers)
            or {record["tier"] for record in family_records} != expected_tiers
            or sum(record["expected"] == "infeasible" for record in family_records)
            != 1
        ):
            raise Real3DCorpusError("Corpus family distribution is incomplete.")
    if holdout and extra_records:
        raise Real3DCorpusError("Sealed holdout contains an unexpected case.")
    if not holdout and (
        len(extra_records) != 1
        or extra_records[0].get("family") != "real-anonymized"
        or extra_records[0].get("tier") != "reviewed-real"
        or extra_records[0].get("expected") != "bounded_unknown"
    ):
        raise Real3DCorpusError("Reviewed real regression is missing.")


def _is_lower_hex_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_top_down_access(placements: Sequence[Mapping[str, object]]) -> None:
    for lower in placements:
        lower_top = lower["z"] + lower["size"][2]
        for upper in placements:
            if (
                upper["z"] >= lower_top
                and _overlap_xy(lower, upper)
                and upper["removal_rank"] >= lower["removal_rank"]
            ):
                raise Real3DCorpusError(
                    "Witness removal order violates top-down access."
                )


def _covered_area(
    load: Mapping[str, object], supports: Sequence[Mapping[str, object]]
) -> int:
    x_points = {int(load["x"]), int(load["x"] + load["size"][0])}
    y_points = {int(load["y"]), int(load["y"] + load["size"][1])}
    for support in supports:
        x_points.add(max(int(load["x"]), int(support["x"])))
        x_points.add(
            min(
                int(load["x"] + load["size"][0]),
                int(support["x"] + support["size"][0]),
            )
        )
        y_points.add(max(int(load["y"]), int(support["y"])))
        y_points.add(
            min(
                int(load["y"] + load["size"][1]),
                int(support["y"] + support["size"][1]),
            )
        )
    xs = sorted(x_points)
    ys = sorted(y_points)
    area = 0
    for x_index in range(len(xs) - 1):
        for y_index in range(len(ys) - 1):
            x0, x1 = xs[x_index], xs[x_index + 1]
            y0, y1 = ys[y_index], ys[y_index + 1]
            if x1 <= x0 or y1 <= y0:
                continue
            if any(
                support["x"] <= x0
                and support["x"] + support["size"][0] >= x1
                and support["y"] <= y0
                and support["y"] + support["size"][1] >= y1
                for support in supports
            ):
                area += (x1 - x0) * (y1 - y0)
    return area


def _fits_fragment_cell(
    item: Mapping[str, object], recipe: Mapping[str, object]
) -> bool:
    if item["x"] < 2 or item["y"] < 2:
        return False
    stride = int(recipe["cell_stride_mm"])
    cell_x = 2 + stride * ((item["x"] - 2) // stride)
    cell_y = 2 + stride * ((item["y"] - 2) // stride)
    return (
        item["x"] + item["size"][0] <= cell_x + 10
        and item["y"] + item["size"][1] <= cell_y + 10
    )


def _variant_count(recipe: Mapping[str, object], index: int) -> int:
    cycle = recipe["variant_front_cycle"]
    return int(cycle[index % len(cycle)])


def _usable_volume(recipe: Mapping[str, object]) -> int:
    world = recipe["world_mm"]
    reserved = sum(
        value["size"][0] * value["size"][1] * value["size"][2]
        for value in recipe["reservation_volumes"]
    )
    return world[0] * world[1] * world[2] - reserved


def _seed_from_nonce(nonce: str, family: str, index: int) -> int:
    return int(
        canonical_digest({"nonce": nonce, "family": family, "index": index})[:12],
        16,
    )


def _overlap_xy(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    return (
        left["x"] < right["x"] + right["size"][0]
        and right["x"] < left["x"] + left["size"][0]
        and left["y"] < right["y"] + right["size"][1]
        and right["y"] < left["y"] + left["size"][1]
    )


def _overlap_3d(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    return _overlap_xy(left, right) and (
        left["z"] < right["z"] + right["size"][2]
        and right["z"] < left["z"] + left["size"][2]
    )
