from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from board_game_insert_generator.free_3d_plan_adapter import (  # noqa: E402
    prepare_free_3d_problem,
)
from board_game_insert_generator.incremental_project_state import (  # noqa: E402
    canonical_digest,
)
from board_game_insert_generator.project_v1 import (  # noqa: E402
    normalize_project_draft,
)
from board_game_insert_generator.solver_benchmark_corpus import (  # noqa: E402
    _materialize_recipe,
    _validate_recipe,
)


FIXTURES = ROOT / "tests" / "fixtures"


def _load(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8-sig"))


def _project_metrics(case: dict[str, object], source: str) -> dict[str, object]:
    project = case["project"]
    assert isinstance(project, dict)
    box = project["box"]
    assert isinstance(box, dict)
    dimensions = box["inner_dimensions_mm"]
    assert isinstance(dimensions, dict)
    usable_height = float(box["usable_height_mm"])
    preparation = prepare_free_3d_problem(project)
    participants = preparation.problem.participants if preparation.problem else ()
    body_volumes: list[float] = []
    body_axes: list[float] = []
    for participant in participants:
        minimum = participant["minimum_local_mm"]
        assert isinstance(minimum, dict)
        axes = [float(minimum[axis]) for axis in ("x", "y", "z")]
        body_axes.extend(axes)
        body_volumes.append(axes[0] * axes[1] * axes[2])
    usable_volume = (
        float(dimensions["x"]) * float(dimensions["y"]) * usable_height
    )
    features = case.get("features", {})
    if not isinstance(features, dict):
        features = {}
    flat_items = project.get("flat_items", [])
    if not isinstance(flat_items, list):
        flat_items = []
    contents = project.get("contents", [])
    if not isinstance(contents, list):
        contents = []
    content_axes = [
        float(value)
        for item in contents
        if isinstance(item, dict)
        for dimensions_value in [item.get("dimensions_mm")]
        if isinstance(dimensions_value, dict)
        for value in dimensions_value.values()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    return {
        "case_id": str(case.get("case_id", "missing")),
        "source": source,
        "split": str(case.get("split", "regression")),
        "family": str(case.get("family", "historical-regression")),
        "container_count": len(project.get("container_groups", [])),
        "content_record_count": len(contents),
        "content_quantity": sum(
            int(item.get("quantity", 0))
            for item in contents
            if isinstance(item, dict)
            and isinstance(item.get("quantity"), int)
            and not isinstance(item.get("quantity"), bool)
        ),
        "flat_item_count": len(flat_items),
        "flat_item_kinds": sorted(
            str(item.get("kind", "missing"))
            for item in flat_items
            if isinstance(item, dict)
        ),
        "box_mm": [
            float(dimensions["x"]),
            float(dimensions["y"]),
            float(dimensions["z"]),
        ],
        "usable_height_mm": usable_height,
        "minimum_body_axis_min_mm": min(body_axes, default=None),
        "minimum_body_axis_max_mm": max(body_axes, default=None),
        "content_axis_min_mm": min(content_axes, default=None),
        "content_axis_max_mm": max(content_axes, default=None),
        "outer_load_ratio": (
            round(sum(body_volumes) / usable_volume, 9)
            if usable_volume > 0.0
            else None
        ),
        "declared_outer_load_ratio": features.get("oracle_outer_load_ratio"),
        "density_target": features.get("density_target", "missing"),
        "layer_target": features.get("layer_target", "missing"),
        "reservation_mode": features.get("reservation_mode", "missing"),
        "execution_mode": features.get("execution_mode", "cold"),
        "change_kind": features.get("change_kind", "none"),
        "rotation_policy_target": features.get(
            "rotation_policy_target", "missing"
        ),
        "oracle_kind": features.get("oracle_kind", "historical"),
        "effort": (
            case.get("solver_settings", {}).get("effort", "missing")
            if isinstance(case.get("solver_settings"), dict)
            else "missing"
        ),
    }


def _rebuild_generated(record: dict[str, object]) -> dict[str, object]:
    recipe = _validate_recipe(record["recipe"])
    core = _materialize_recipe(
        case_id=str(record["case_id"]),
        split=str(record["split"]),
        family=str(record["family"]),
        seed=int(record["seed"]),
        recipe=recipe,
    )
    current_project = normalize_project_draft(core["project"]).project
    core["project"] = current_project
    core["project_digest"] = canonical_digest(current_project)
    previous_project = core.get("previous_project")
    if previous_project is not None:
        current_previous = normalize_project_draft(previous_project).project
        core["previous_project"] = current_previous
        core["previous_project_digest"] = canonical_digest(current_previous)
    return {
        "case_id": record["case_id"],
        "split": record["split"],
        "family": record["family"],
        "seed": record["seed"],
        "recipe": recipe,
        "solver_settings": record["solver_settings"],
        **core,
    }


def _counter(records: list[dict[str, object]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(value[key]) for value in records).items()))


def _number_range(
    records: list[dict[str, object]], key: str
) -> list[float | int | None]:
    values = [
        value[key]
        for value in records
        if isinstance(value.get(key), (int, float))
        and not isinstance(value.get(key), bool)
    ]
    return [min(values), max(values)] if values else [None, None]


def _ratio_ranges_by_density(
    records: list[dict[str, object]]
) -> dict[str, list[float | int | None]]:
    return {
        density: _number_range(
            [
                value
                for value in records
                if value["density_target"] == density
                and value["oracle_kind"] == "feasible_by_construction"
            ],
            "outer_load_ratio",
        )
        for density in ("ample", "dense", "nearly_saturated")
    }


def _generator_drift(
    records: list[object],
) -> dict[str, object]:
    changed_fields: Counter[str] = Counter()
    affected: list[dict[str, object]] = []
    for raw in records:
        if not isinstance(raw, dict):
            continue
        rebuilt = _rebuild_generated(raw)
        fields = [
            field
            for field in (
                "project_digest",
                "previous_project_digest",
                "oracle_digest",
                "features",
            )
            if raw.get(field) != rebuilt.get(field)
        ]
        if fields:
            changed_fields.update(fields)
            affected.append(
                {
                    "case_id": raw["case_id"],
                    "split": raw["split"],
                    "reservation_mode": raw["features"]["reservation_mode"],
                    "fields": fields,
                }
            )
    return {
        "case_count": len(records),
        "drifted_case_count": len(affected),
        "changed_field_counts": dict(sorted(changed_fields.items())),
        "drifted_by_split": dict(
            sorted(Counter(str(value["split"]) for value in affected).items())
        ),
        "drifted_by_reservation_mode": dict(
            sorted(
                Counter(
                    str(value["reservation_mode"]) for value in affected
                ).items()
            )
        ),
        "sample": affected[:8],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Audit the coverage and current reconstructibility of the "
            "versioned L05-L08 solver fixtures."
        )
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    l05 = _load("p64_l05d_solver_case_corpus.v1.json")
    l06 = _load("p64_l06_solver_benchmark.v1.json")
    l07 = _load("p64_l07b_solver_benchmark.v2.json")
    l08 = _load("p64_l08d_real_3d_corpus.v1.json")

    direct_cases: list[tuple[str, dict[str, object]]] = [
        ("L05", value) for value in l05["cases"] if isinstance(value, dict)
    ]
    direct_cases.extend(
        ("L06", case)
        for source in l06["regression_corpora"]
        if isinstance(source, dict)
        for case in source["corpus"]["cases"]
        if isinstance(case, dict)
    )
    direct_cases.extend(
        ("L06", _rebuild_generated(value))
        for value in l06["generated_cases"]
        if isinstance(value, dict)
    )
    direct_cases.extend(
        ("L07", case)
        for source in l07["regression_corpora"]
        if isinstance(source, dict)
        for case in source["corpus"]["cases"]
        if isinstance(case, dict)
    )
    direct_cases.extend(
        ("L07", _rebuild_generated(value))
        for value in l07["bgig_generated_cases"]
        if isinstance(value, dict)
    )

    metrics = [_project_metrics(case, source) for source, case in direct_cases]
    unique_by_digest: dict[str, dict[str, object]] = {}
    for (source, case), record in zip(direct_cases, metrics, strict=True):
        digest = str(case.get("project_digest", ""))
        unique_by_digest.setdefault(digest, record)
    unique = list(unique_by_digest.values())
    l08_records = [
        value
        for value in l08["open_case_records"]
        if isinstance(value, dict)
    ]
    output = {
        "schema_version": "bgig.solver_fixture_coverage_audit.v1",
        "direct_case_count_with_duplicates": len(metrics),
        "unique_project_digest_count": len(unique),
        "source_counts": _counter(metrics, "source"),
        "split_counts": _counter(metrics, "split"),
        "family_counts": _counter(metrics, "family"),
        "density_targets": _counter(metrics, "density_target"),
        "layer_targets": _counter(metrics, "layer_target"),
        "reservation_modes": _counter(metrics, "reservation_mode"),
        "execution_modes": _counter(metrics, "execution_mode"),
        "change_kinds": _counter(metrics, "change_kind"),
        "rotation_policies": _counter(metrics, "rotation_policy_target"),
        "oracle_kinds": _counter(metrics, "oracle_kind"),
        "efforts": _counter(metrics, "effort"),
        "flat_item_count_distribution": _counter(metrics, "flat_item_count"),
        "feasible_outer_load_ratio_by_density": _ratio_ranges_by_density(
            metrics
        ),
        "container_count_range": _number_range(unique, "container_count"),
        "content_record_count_range": _number_range(
            unique, "content_record_count"
        ),
        "content_quantity_range": _number_range(unique, "content_quantity"),
        "flat_item_count_range": _number_range(unique, "flat_item_count"),
        "outer_load_ratio_range": _number_range(unique, "outer_load_ratio"),
        "minimum_body_axis_range_mm": [
            _number_range(unique, "minimum_body_axis_min_mm")[0],
            _number_range(unique, "minimum_body_axis_max_mm")[1],
        ],
        "content_axis_range_mm": [
            _number_range(unique, "content_axis_min_mm")[0],
            _number_range(unique, "content_axis_max_mm")[1],
        ],
        "box_axis_range_mm": [
            min(axis for value in unique for axis in value["box_mm"]),
            max(axis for value in unique for axis in value["box_mm"]),
        ],
        "sample_metrics": unique[:12],
        "l06_generator_drift": _generator_drift(l06["generated_cases"]),
        "l07_generator_drift": _generator_drift(
            l07["bgig_generated_cases"]
        ),
        "l08_core_only": {
            "case_count": len(l08_records),
            "families": dict(
                sorted(
                    Counter(str(value["family"]) for value in l08_records).items()
                )
            ),
            "splits": dict(
                sorted(
                    Counter(str(value["split"]) for value in l08_records).items()
                )
            ),
            "tiers": dict(
                sorted(
                    Counter(str(value["tier"]) for value in l08_records).items()
                )
            ),
            "expected": dict(
                sorted(
                    Counter(str(value["expected"]) for value in l08_records).items()
                )
            ),
            "product_path_complete": False,
        },
    }
    output["audit_digest"] = canonical_digest(output)
    rendered = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(rendered + "\n", encoding="utf-8")
        temporary.replace(args.output)
    print(rendered)


if __name__ == "__main__":
    main()
