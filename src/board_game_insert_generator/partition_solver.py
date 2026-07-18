"""P57 deterministic partition solver for the Fusion-only MVP.

The solver partitions the printable storage volume between requested container
bodies and explicitly sized complements.  It never turns a free region into an
automatic body.  Cavities remain local to their P55 minimum envelope.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from time import perf_counter
from typing import Any

from board_game_insert_generator.expandable_envelope import derive_expandable_envelope_contract
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_contract import (
    run_stage_stack_adapter,
    validate_placement_geometry,
)
from board_game_insert_generator.solver_outcome import (
    SOLUTION_FOUND,
    SOLVER_RESULT_SCHEMA_V1,
    SOLVER_TELEMETRY_SCHEMA_V1,
    attach_solver_outcome,
    result_label,
)
from board_game_insert_generator.solver_settings import (
    EFFORT_NORMAL,
    SOLVER_METHOD_AUTO,
    SOLVER_METHOD_STAGE_STACK,
    normalize_solver_settings,
)
from board_game_insert_generator.top_inset_reservation import (
    apply_top_inset_reservations,
    compatibility_flat_stack_payload,
    derive_top_inset_reservations,
)
from board_game_insert_generator.volumetric_stage_solver import (
    SOLUTION_COMPLETE,
    SOLUTION_WITH_RESIDUALS,
    STRUCTURED_ORDER_STRATEGIES,
    solve_stage_portfolio,
)


PARTITION_PLAN_SCHEMA_V1 = "bgig.partition_plan.v1"
PARTITION_CAPACITY_SCHEMA_V1 = "bgig.partition_capacity.v1"
MAX_DIVERSIFIED_PORTFOLIOS = 6
_EPSILON = 0.0001
_DIVERSIFIED_RETRY_CODES = {"NO_STAGE_COMPOSITION_FITS", "NO_VALIDATED_STAGE_PROPOSAL"}


def solve_partition_plan(
    raw_project: object,
    *,
    request_id: str | None = None,
    request_revision: int | None = None,
    solver_method: str | None = None,
    effort_profile: str = EFFORT_NORMAL,
) -> dict[str, object]:
    """Run the H08 public method selector without moving solving into Fusion."""

    settings = normalize_solver_settings(
        {"method": solver_method or SOLVER_METHOD_STAGE_STACK, "effort": effort_profile}
    )
    if settings["method"] == SOLVER_METHOD_STAGE_STACK:
        started_at = perf_counter()
        baseline = solve_stage_stack_plan(
            raw_project,
            request_id=request_id,
            request_revision=request_revision,
        )
        if solver_method is None:
            return baseline
        return _attach_capacity_summary(
            _stage_stack_product_plan(
                baseline,
                effort_profile=settings["effort"],
                elapsed_ms=(perf_counter() - started_at) * 1000.0,
            ),
            raw_project,
        )

    from board_game_insert_generator.solver_portfolio import (
        FREE_3D_BEAM_FAMILY_ID,
        FREE_3D_GREEDY_FAMILY_ID,
        _ALLOWED_FAMILIES,
        solve_partition_portfolio,
    )

    started_at = perf_counter()
    selected_families = (
        _ALLOWED_FAMILIES
        if settings["method"] == SOLVER_METHOD_AUTO
        else (FREE_3D_GREEDY_FAMILY_ID, FREE_3D_BEAM_FAMILY_ID)
    )
    execution = solve_partition_portfolio(
        raw_project,
        effort_profile=settings["effort"],
        request_id=request_id,
        request_revision=request_revision,
        selected_family_ids=selected_families,
    )
    return _attach_capacity_summary(
        _portfolio_public_plan(
            raw_project,
            execution,
            solver_method=settings["method"],
            request_id=request_id,
            request_revision=request_revision,
            elapsed_ms=(perf_counter() - started_at) * 1000.0,
        ),
        raw_project,
    )


def _attach_capacity_summary(
    plan: dict[str, object],
    raw_project: object,
) -> dict[str, object]:
    """Expose a necessary volume bound without claiming 3D packability."""

    projected = deepcopy(plan)
    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    box = _mapping(project["box"])
    box_dimensions = _dimension(box["inner_dimensions_mm"])
    storage_height = min(float(box["usable_height_mm"]), box_dimensions["z"])
    envelope_report = derive_expandable_envelope_contract(
        project,
        max_container_height_mm=storage_height,
    )
    containers = _mappings(envelope_report["containers"])
    ready = [
        item
        for item in containers
        if item.get("status") == "ready"
        and isinstance(item.get("minimum_outer_envelope_mm"), dict)
    ]
    fill_elements = _mappings(project["fill_elements"])
    exact_complements = [
        item
        for item in fill_elements
        if item.get("mode") == "exact" and isinstance(item.get("dimensions_mm"), dict)
    ]
    complement_volume = sum(
        _volume(_mapping(item["dimensions_mm"]))
        for item in exact_complements
    )
    complete = (
        len(ready) == len(containers)
        and len(exact_complements) == len(fill_elements)
    )
    minimum_volume = sum(
        _volume(_mapping(item["minimum_outer_envelope_mm"]))
        for item in ready
    ) + complement_volume
    layout = _mapping(project["layout"])
    clearance = float(layout.get("container_box_xy_clearance_mm", 0.0))
    for group in _mappings(project["container_groups"]):
        policy_value = group.get("clearance_effective_v1")
        if not isinstance(policy_value, dict):
            continue
        per_side = _mapping(policy_value["box_per_side_xy_mm"])
        clearance = max(clearance, float(per_side["x"]), float(per_side["y"]))
    solver_x = max(0.0, box_dimensions["x"] - clearance * 2.0)
    solver_y = max(0.0, box_dimensions["y"] - clearance * 2.0)
    gross_volume = box_dimensions["x"] * box_dimensions["y"] * storage_height
    solver_volume = solver_x * solver_y * storage_height
    balance = solver_volume - minimum_volume if complete else None
    remaining = max(0.0, balance) if balance is not None else None
    flat_volume = sum(
        _volume(_mapping(item["dimensions_mm"])) * int(item["quantity"])
        for item in _mappings(project["flat_items"])
    )
    capacity = {
        "schema_version": PARTITION_CAPACITY_SCHEMA_V1,
        "status": (
            "incomplete_minimum_model"
            if not complete
            else "minimum_volume_exceeds_solver_volume"
            if balance is not None and balance < -_EPSILON
            else "positive_theoretical_margin"
        ),
        "complete_minimum_model": complete,
        "gross_usable_box_volume_mm3": _round(gross_volume),
        "solver_usable_volume_mm3": _round(solver_volume),
        "minimum_requested_envelope_volume_mm3": _round(minimum_volume),
        "flat_item_physical_volume_mm3": _round(flat_volume),
        "explicit_complement_volume_mm3": _round(complement_volume),
        "signed_volume_balance_mm3": None if balance is None else _round(balance),
        "theoretical_remaining_volume_mm3": None if remaining is None else _round(remaining),
        "theoretical_remaining_ratio": (
            None
            if remaining is None or solver_volume <= _EPSILON
            else _round(remaining / solver_volume)
        ),
        "requested_container_count": len(containers),
        "modeled_container_count": len(ready),
        "requested_complement_count": len(fill_elements),
        "modeled_complement_count": len(exact_complements),
        "perimeter_clearance_mm": {"x": _round(clearance), "y": _round(clearance)},
        "interpretation": "necessary_volume_bound_not_packing_proof",
        "not_scalarized_constraints": [
            "orthogonal_shapes_and_orientations",
            "between_body_clearances",
            "supports_and_removal",
            "localized_top_inset_reservations",
        ],
    }
    projected["capacity"] = capacity
    summary = _mapping(projected["summary"])
    summary["capacity_status"] = capacity["status"]
    summary["theoretical_remaining_volume_mm3"] = capacity["theoretical_remaining_volume_mm3"]
    projected.pop("plan_digest", None)
    projected["plan_digest"] = _digest(projected)
    return projected


def solve_stage_stack_plan(
    raw_project: object,
    *,
    request_id: str | None = None,
    request_revision: int | None = None,
) -> dict[str, object]:
    """Expose the preserved H05 baseline for explicit product selection."""

    return run_stage_stack_adapter(
        _solve_stage_stack_baseline,
        raw_project,
        request_id=request_id,
        request_revision=request_revision,
    )


def _stage_stack_product_plan(
    plan: dict[str, object],
    *,
    effort_profile: str,
    elapsed_ms: float,
) -> dict[str, object]:
    """Add H08 presentation metadata without changing the baseline result."""

    projected = deepcopy(plan)
    solver = _mapping(projected.get("solver"))
    telemetry = _mapping(solver.get("telemetry"))
    family_id = str(solver.get("family_id") or "stage_stack")
    portfolio = {
        "method": SOLVER_METHOD_STAGE_STACK,
        "effort_profile": effort_profile,
        "effort_label": {"quick": "Rapide", "normal": "Normal", "deep": "Approfondi"}[effort_profile],
        "selected_family_id": family_id,
        "eligible_family_ids": [family_id],
        "family_reports": [],
        "fast_path_used": True,
        "deduplicated_candidate_count": 0,
        "deterministic_digest": _digest({"method": SOLVER_METHOD_STAGE_STACK, "plan": plan.get("plan_digest", "")}),
    }
    telemetry["portfolio"] = portfolio
    telemetry["elapsed_ms"] = round(max(0.0, elapsed_ms), 3)
    solver["portfolio"] = deepcopy(portfolio)
    solver["telemetry"] = telemetry
    result = _mapping(solver.get("result"))
    if result.get("status") == "no_solution_within_budget":
        summary = _mapping(projected["summary"])
        summary["status"] = "unresolved"
        summary["solution_status"] = "unresolved"
        result["legacy_summary_status"] = "unresolved"
        solver["result"] = result
        projected["diagnostics"] = [
            _diagnostic(
                "STAGE_STACK_NO_SOLUTION_WITHIN_BUDGET",
                "Etages et piles n a trouve aucune disposition certifiee dans son budget. Ce resultat n est pas une preuve d impossibilite.",
                "Essaie Auto intelligent ou Placement 3D libre ; une marge de volume positive ne garantit pas la compatibilite des formes.",
            )
        ]
    projected.pop("plan_digest", None)
    projected["plan_digest"] = _digest(projected)
    return projected


def _portfolio_public_plan(
    raw_project: object,
    execution: Any,
    *,
    solver_method: str,
    request_id: str | None,
    request_revision: int | None,
    elapsed_ms: float,
) -> dict[str, object]:
    """Project one bounded portfolio execution onto the existing plan contract."""

    selected_plan = execution.selected_plan
    plan = deepcopy(selected_plan or execution.fallback_plan)
    if plan is None:
        plan = solve_stage_stack_plan(
            raw_project,
            request_id=request_id,
            request_revision=request_revision,
        )
    solution_found = selected_plan is not None and execution.status == SOLUTION_FOUND
    summary = _mapping(plan["summary"])
    solver = _mapping(plan["solver"])

    preserve_residual_proposal = (
        not solution_found and summary.get("status") == SOLUTION_WITH_RESIDUALS
    )
    if not solution_found and not preserve_residual_proposal:
        plan["placements"] = []
        plan["stages"] = []
        plan["removal_sequence"] = []
        plan["support"] = {
            "status": "unresolved",
            "top_support_count": 0,
            "coverage_ratio": 0.0,
        }
        plan["stage_support"] = {"status": "unresolved", "supports": []}
        plan["residuals"] = {
            "status": "unresolved",
            "zones": [],
            "residual_volume_mm3": 0.0,
        }
        plan["suggestions"] = []
        plan["validation"] = {
            "inside_box": False,
            "box_xy_clearance_respected": False,
            "no_collisions": False,
            "clearances_respected": False,
        }
        if execution.status == "no_solution_within_budget":
            plan["diagnostics"] = [
                _diagnostic(
                    "PORTFOLIO_NO_SOLUTION_WITHIN_BUDGET",
                    "Aucune disposition certifiee n a ete trouvee dans le budget. Ce resultat n est pas une preuve d impossibilite.",
                    "Essaie un effort plus profond ou une autre methode ; les formes, appuis et reservations peuvent bloquer malgre une marge de volume positive.",
                )
            ]
        unresolved_status = (
            "impossible"
            if execution.status == "proven_impossible"
            else "blocked"
            if execution.status == "invalid_input"
            else "unresolved"
        )
        summary.update(
            {
                "status": unresolved_status,
                "solution_status": unresolved_status,
                "materializable": False,
                "placed_container_count": 0,
                "final_body_count": 0,
                "stage_count": 0,
                "complete_printable_partition": False,
                "technical_voids_are_clearances_only": False,
            }
        )
    elif preserve_residual_proposal:
        summary["materializable"] = False
        summary["complete_printable_partition"] = False

    reports = [
        {
            "family_id": report.family_id,
            "status": report.status,
            "stop_reason": report.stop_reason,
            "proposed_candidate_count": report.proposed_candidate_count,
            "certified_candidate_count": report.certified_candidate_count,
            "rejection_codes": list(report.rejection_codes),
            "skipped_by_fast_path": report.skipped_by_fast_path,
        }
        for report in execution.family_reports
    ]
    budgets = {
        "profile": execution.effort_profile.profile_id,
        "greedy": dict(execution.effort_profile.greedy_budget.limits),
        "beam": dict(execution.effort_profile.beam_budget.limits),
    }
    container_variant_trace = None
    if execution.container_variant_search is not None:
        from board_game_insert_generator.container_variant_global_search import (
            container_variant_global_execution_to_dict,
        )

        container_variant_trace = container_variant_global_execution_to_dict(
            execution.container_variant_search
        )
        budgets["container_variants"] = {
            "schema_version": container_variant_trace["schema_version"],
            "lanes": [
                {
                    "effort_profile": value["effort_profile"],
                    "variant_budget": value["variant_budget"],
                    "beam_budget": value["beam_budget"],
                }
                for value in container_variant_trace["lanes"]
            ],
        }
    proof = _mapping(solver.get("result", {})).get("proof") if execution.status == "proven_impossible" else None
    solver.update(
        {
            "kind": "bounded_solver_portfolio",
            "family_id": execution.strategy.family_id,
            "schema_version": execution.strategy.version,
            "selected_family_id": execution.selected_family_id,
            "budgets": budgets,
            "portfolio": {
                "method": solver_method,
                "effort_profile": execution.effort_profile.profile_id,
                "effort_label": execution.effort_profile.product_label,
                "selected_family_id": execution.selected_family_id,
                "eligible_family_ids": list(execution.selected_family_ids),
                "family_reports": reports,
                "fast_path_used": execution.fast_path_used,
                "deduplicated_candidate_count": execution.deduplicated_candidate_count,
                "deterministic_digest": execution.deterministic_digest,
            },
            "deterministic": True,
            "globally_optimal": False,
        }
    )
    if container_variant_trace is not None:
        _mapping(solver["portfolio"])["container_variant_search"] = (
            container_variant_trace
        )
    elapsed = (
        round(max(0.0, float(elapsed_ms)), 3)
        if request_id is not None or request_revision is not None
        else "not_applicable"
    )
    telemetry = {
        "schema_version": SOLVER_TELEMETRY_SCHEMA_V1,
        "family": {
            "id": execution.strategy.family_id,
            "version": execution.strategy.version,
        },
        "request": {
            "id": request_id or "not_applicable",
            "revision": request_revision if request_revision is not None else "not_applicable",
        },
        "elapsed_ms": elapsed,
        "budgets": budgets,
        "counters": {
            "candidate_proposals": sum(item["proposed_candidate_count"] for item in reports),
            "search_states": "portfolio",
            "placements_attempted": "see_family_reports",
            "certified_complete_solutions": len(execution.certified_candidates),
            "z_start_levels": (
                len(
                    {
                        float(_mapping(item["origin_mm"])["z"])
                        for item in _mappings(plan.get("placements", []))
                    }
                )
                if solution_found
                else "not_applicable"
            ),
        },
        "prunes": {
            "candidate_budget_truncations": sum(
                1
                for item in reports
                if item["stop_reason"]
                in {"portfolio_budget_exhausted", "budget_exhausted", "time_budget_reached"}
            ),
            "visible_validation_rejections": sum(len(item["rejection_codes"]) for item in reports),
            "deduplicated_candidates": execution.deduplicated_candidate_count,
        },
        "diagnostic_code_counts": {},
        "stop_reason": execution.stop_reason,
        "portfolio": deepcopy(solver["portfolio"]),
    }
    result = {
        "schema_version": SOLVER_RESULT_SCHEMA_V1,
        "status": execution.status,
        "label": result_label(execution.status),
        "legacy_summary_status": summary.get("status"),
        "proof": deepcopy(proof) if isinstance(proof, dict) else None,
        "materializable": solution_found and bool(summary.get("materializable")),
    }
    summary["result_status"] = result["status"]
    summary["result_label"] = result["label"]
    solver["result"] = result
    solver["telemetry"] = telemetry
    plan.pop("plan_digest", None)
    plan["plan_digest"] = _digest(plan)
    return plan


def _solve_stage_stack_baseline(
    raw_project: object,
    *,
    request_id: str | None = None,
    request_revision: int | None = None,
) -> dict[str, object]:
    """Preserve the H03R canonical/directed/hash stage-stack sequence exactly."""

    started_at = perf_counter()
    attempts = [_solve_partition_plan_once(raw_project)]
    initial = attempts[0]
    diagnostic_codes = {str(item["code"]) for item in _mappings(initial["diagnostics"])}
    if not diagnostic_codes.intersection(_DIVERSIFIED_RETRY_CODES):
        return _attach_outcome(initial, request_id, request_revision, started_at)

    partial: dict[str, object] | None = None
    chosen: dict[str, object] | None = None
    for strategy in _structured_retry_strategies(diagnostic_codes):
        proposal = _solve_partition_plan_once(
            raw_project,
            structured_order_strategy=strategy,
        )
        attempts.append(proposal)
        status = str(_mapping(proposal["summary"])["status"])
        if status == "constructed":
            chosen = proposal
            break
        if status == SOLUTION_WITH_RESIDUALS and partial is None:
            partial = proposal

    if chosen is None:
        for seed in range(MAX_DIVERSIFIED_PORTFOLIOS):
            proposal = _solve_partition_plan_once(raw_project, diversified_order_seed=seed)
            attempts.append(proposal)
            status = str(_mapping(proposal["summary"])["status"])
            if status == "constructed":
                chosen = proposal
                break
            if status == SOLUTION_WITH_RESIDUALS and partial is None:
                partial = proposal

    return _attach_outcome(
        _finalize_portfolio_search(chosen or partial or initial, attempts),
        request_id,
        request_revision,
        started_at,
    )


def _solve_partition_plan_once(
    raw_project: object,
    *,
    diversified_order_seed: int | None = None,
    structured_order_strategy: str | None = None,
) -> dict[str, object]:
    """Evaluate one canonical, directed or hash-diversified portfolio."""

    normalization = normalize_project_draft(raw_project)
    project = normalization.project
    top_inset_plan = derive_top_inset_reservations(project)
    flat = compatibility_flat_stack_payload(top_inset_plan)
    stack = {"flat_stack": flat, "top_inset_reservations": top_inset_plan}
    box = _dimension(_mapping(project["box"])["inner_dimensions_mm"])
    storage_height = float(top_inset_plan["design_top_z_mm"])
    xy_clearance = float(_mapping(project["layout"])["layout_clearance_mm"])
    box_xy_clearance = float(_mapping(project["layout"])["container_box_xy_clearance_mm"])
    z_clearance = float(_mapping(project["layout"])["container_z_clearance_mm"])
    diagnostics = [
        _diagnostic(
            str(item["code"]), str(item["message"]), str(item["action"]), str(item.get("reference_id", ""))
        )
        for item in _mappings(top_inset_plan["blockers"])
    ]

    envelope_report = derive_expandable_envelope_contract(
        project, max_container_height_mm=max(storage_height, 0.001)
    )
    diagnostics.extend(
        _diagnostic(
            "CONTAINER_MINIMUM_BLOCKED",
            str(item["message"]),
            "Corrige l element, le conteneur ou une dimension fixe.",
            str(item["container_group_id"]),
        )
        for item in _mappings(envelope_report["blockers"])
    )
    diagnostics.extend(_minimum_envelope_box_proofs(envelope_report, project, box, storage_height))
    containers = [item for item in _mappings(envelope_report["containers"]) if item["status"] == "ready"]
    requested_group_count = len(_values(project["container_groups"]))
    if not requested_group_count:
        diagnostics.append(
            _diagnostic(
                "NO_CONTAINER_GROUP",
                "Aucun conteneur n est demande.",
                "Ajoute au moins un conteneur cible et une famille d elements.",
            )
        )
    if len(containers) != requested_group_count:
        diagnostics.append(
            _diagnostic(
                "CONTAINER_SET_INCOMPLETE",
                "Tous les conteneurs demandes ne possedent pas une enveloppe minimale constructible.",
                "Corrige les conteneurs bloques avant de recalculer.",
            )
        )

    groups_by_id = {
        str(group["id"]): group for group in _mappings(project["container_groups"])
    }
    default_floor = float(_mapping(project["layout"])["default_floor_thickness_mm"])
    participants = [
        _container_participant(
            item,
            groups_by_id[str(item["container_group_id"])],
            top_inset_plan=top_inset_plan,
            default_floor_mm=default_floor,
            storage_height_mm=storage_height,
        )
        for item in containers
    ]
    for value in _values(project["fill_elements"]):
        complement = _mapping(value)
        if complement["mode"] != "exact":
            diagnostics.append(
                _diagnostic(
                    "EXPLICIT_COMPLEMENT_NEEDS_EXACT_SIZE",
                    f"Le corps explicite '{complement['name']}' utilise encore le mode auto.",
                    "Renseigne ses dimensions exactes ; BGIG ne cree aucun volume automatiquement.",
                    str(complement["id"]),
                )
            )
            continue
        participants.append(_complement_participant(complement))

    if diagnostics or not participants or storage_height <= 0.0:
        return _result(
            normalization, project, stack, envelope_report, diagnostics,
            status="incomplete" if not requested_group_count else "impossible",
            evaluated=0, stage_solver=None,
        )

    solver_xy_clearance, solver_box_clearance, solver_z_clearance = _solver_clearance_fallbacks(
        participants, xy_clearance, box_xy_clearance, z_clearance
    )
    stage_solver = solve_stage_portfolio(
        participants,
        box,
        storage_height,
        solver_xy_clearance,
        box_clearance_mm=solver_box_clearance,
        vertical_clearance_mm=solver_z_clearance,
        preference=str(project["solver_preference"]),
        diversified_order_seed=diversified_order_seed,
        structured_order_strategy=structured_order_strategy,
        top_inset_search_context={
            "reservations": deepcopy(top_inset_plan["reservations"]),
        },
    )
    evaluated = int(_mapping(stage_solver["search"])["groupings_evaluated"])
    if not _values(stage_solver["candidates"]):
        diagnostics.extend(
            _diagnostic(str(item["code"]), str(item["message"]), str(item["action"]))
            for item in _mappings(stage_solver["blockers"])
        )
        return _result(
            normalization, project, stack, envelope_report, diagnostics,
            status="impossible", evaluated=evaluated, stage_solver=stage_solver,
        )

    chosen: dict[str, object] | None = None
    chosen_envelopes: dict[str, object] | None = None
    chosen_top_insets: dict[str, object] | None = None
    chosen_validation: dict[str, object] | None = None
    rejection_diagnostics: list[dict[str, object]] = []
    content_names = {str(item["id"]): str(item["name"]) for item in _mappings(project["contents"])}
    for candidate in _mappings(stage_solver["candidates"]):
        proposals = {
            str(item["container_group_id"]): deepcopy(item["final_outer_dimensions_mm"])
            for item in _mappings(candidate["placements"])
            if item["role"] == "container"
        }
        available_by_group = {
            str(item["container_group_id"]): {
                "x": box["y"] if int(item.get("rotation_deg_z", 0)) == 90 else box["x"],
                "y": box["x"] if int(item.get("rotation_deg_z", 0)) == 90 else box["y"],
                "z": storage_height,
            }
            for item in _mappings(candidate["placements"])
            if item["role"] == "container"
        }
        validated_envelopes = derive_expandable_envelope_contract(
            project,
            final_outer_dimensions_by_group=proposals,
            available_outer_dimensions_by_group=available_by_group,
            max_container_height_mm=storage_height,
        )
        if _mapping(validated_envelopes["summary"])["status"] == "blocked":
            rejection_diagnostics.extend(
                _diagnostic(
                    "FINAL_ENVELOPE_REJECTED", str(item["message"]),
                    "Relache la dimension fixe ou cible indiquee.", str(item["container_group_id"]),
                )
                for item in _mappings(validated_envelopes["blockers"])
            )
            continue
        envelope_by_group = {
            str(item["container_group_id"]): item
            for item in _mappings(validated_envelopes["containers"])
        }
        placements: list[dict[str, object]] = []
        for placement in _mappings(candidate["placements"]):
            final = deepcopy(placement)
            if final["role"] == "container":
                contract = envelope_by_group[str(final["container_group_id"])]
                final["cavity_layout"] = deepcopy(contract["cavity_layout"])
                final["minimum_outer_envelope_mm"] = deepcopy(contract["minimum_outer_envelope_mm"])
                final["surplus_distribution_mm"] = deepcopy(contract["surplus_distribution_mm"])
                final["minimum_envelope_origin_in_final_mm"] = deepcopy(contract["minimum_envelope_origin_in_final_mm"])
                final["source_content_ids"] = [
                    str(cavity["content_id"]) for cavity in _mappings(contract["cavity_layout"])
                ]
                final["source_contents"] = [
                    {"id": content_id, "name": content_names[content_id]}
                    for content_id in final["source_content_ids"]
                ]
            placements.append(final)

        applied_top_insets = apply_top_inset_reservations(project, placements)
        if _values(applied_top_insets["blockers"]):
            rejection_diagnostics.extend(
                _diagnostic(
                    str(item["code"]), str(item["message"]), str(item["action"]),
                    str(item.get("reference_id", "")),
                )
                for item in _mappings(applied_top_insets["blockers"])
            )
            continue
        placements = _mappings(applied_top_insets["placements"])
        validation = validate_placement_geometry(
            placements,
            box,
            storage_height,
            xy_clearance,
            box_xy_clearance,
            z_clearance,
        )
        if not all(
            bool(validation[key])
            for key in ("inside_box", "box_xy_clearance_respected", "no_collisions", "clearances_respected")
        ):
            rejection_diagnostics.append(
                _diagnostic(
                    "INTERNAL_STAGE_PLAN_INVALID",
                    "Une proposition par etages viole une borne geometrique interne.",
                    "Conserve le projet et signale ce cas pour correction.",
                    str(candidate["candidate_id"]),
                )
            )
            continue
        conservation = _mapping(candidate["volume_conservation"])
        validation.update(deepcopy(conservation))
        validation["unassigned_printable_volume_mm3"] = conservation["residual_volume_mm3"]
        candidate["placements"] = placements
        chosen = candidate
        chosen_envelopes = validated_envelopes
        chosen_top_insets = applied_top_insets
        chosen_validation = validation
        break

    if chosen is None or chosen_envelopes is None or chosen_top_insets is None or chosen_validation is None:
        diagnostics.extend(rejection_diagnostics[:8])
        diagnostics.append(
            _diagnostic(
                "NO_VALIDATED_STAGE_PROPOSAL",
                "Les arrangements trouves echouent apres validation des cavites, appuis ou reservations superieures.",
                "Relache une dimension fixe, deplace un plateau ou reduis un contenu.",
            )
        )
        return _result(
            normalization, project, stack, envelope_report, diagnostics,
            status="impossible", evaluated=evaluated, stage_solver=stage_solver,
        )

    stack["top_inset_reservations"] = chosen_top_insets
    placements = _mappings(chosen["placements"])
    complete = chosen["solution_status"] == SOLUTION_COMPLETE
    result_status = "constructed" if complete else SOLUTION_WITH_RESIDUALS
    if not complete:
        diagnostics.append(
            _notice(
                "PROPOSAL_HAS_RESIDUALS",
                "Une proposition tient dans la boite mais laisse un volume residuel explicite.",
                "Ajuste les cibles ou confirme plus tard une cale suggeree ; la materialisation reste bloquee.",
            )
        )
    flat_removal = [
        {
            "order": int(item["order"]),
            "target_id": item["flat_item_id"],
            "target_type": "flat_item",
            "name": item["name"],
            "access_direction": "top",
        }
        for item in _mappings(chosen_top_insets.get("removal_sequence", []))
    ]
    body_offset = len(flat_removal)
    body_removal = [
        {
            **deepcopy(item),
            "order": body_offset + int(item["order"]),
            "target_id": item["placement_id"],
            "target_type": "requested_body",
        }
        for item in _mappings(chosen["removal_sequence"])
    ]
    metrics = _mapping(chosen["metrics"])
    search = _mapping(stage_solver["search"])
    summary = {
        "status": result_status,
        "solution_status": chosen["solution_status"],
        "materializable": complete,
        "requested_container_count": requested_group_count,
        "placed_container_count": sum(1 for item in placements if item["role"] == "container"),
        "explicit_complement_count": sum(1 for item in placements if item["role"] == "explicit_complement"),
        "final_body_count": len(placements),
        "automatic_body_count": 0,
        "stage_count": int(chosen["stage_count"]),
        "row_count": int(metrics["row_count"]),
        "rotation_count": int(metrics["rotation_count"]),
        "simplicity_score": chosen["quality_score"],
        "quality_score": chosen["quality_score"],
        "score_breakdown": deepcopy(chosen["score_breakdown"]),
        "complete_printable_partition": complete,
        "technical_voids_are_clearances_only": complete,
        "residual_volume_mm3": _mapping(chosen["volume_conservation"])["residual_volume_mm3"],
        "candidate_count_evaluated": evaluated,
        "candidate_count_feasible": int(search["candidate_count"]),
    }
    cavity_compensation_count = int(
        _mapping(chosen_top_insets["summary"]).get("cavity_depth_compensation_count", 0)
    )
    plan = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "box": {"inner_dimensions_mm": _rounded(box), "storage_height_mm": _round(storage_height)},
        "clearance_policy": _clearance_policy(project),
        "flat_stack": deepcopy(flat),
        "top_inset_reservations": _top_inset_payload(chosen_top_insets),
        "support": deepcopy(chosen_top_insets["support"]),
        "stage_support": deepcopy(chosen["support"]),
        "stages": deepcopy(chosen["stages"]),
        "removal_sequence": flat_removal + body_removal,
        "residuals": deepcopy(chosen["residuals"]),
        "suggestions": deepcopy(chosen["suggestions"]),
        "placements": placements,
        "diagnostics": diagnostics,
        "validation": chosen_validation,
        "summary": summary,
        "solver": {
            "kind": "bounded_volumetric_stage_solver",
            "schema_version": stage_solver["schema_version"],
            "candidate_id": chosen["candidate_id"],
            "preference": project["solver_preference"],
            "search_origin": deepcopy(chosen["search_origin"]),
            "budgets": deepcopy(stage_solver["budgets"]),
            "search": deepcopy(stage_solver["search"]),
            "deterministic": True,
            "globally_optimal": False,
        },
        "envelope_contract": deepcopy(chosen_envelopes),
        "invariants": {
            "fixed_cavity_layouts": cavity_compensation_count == 0,
            "base_cavity_layouts_fixed": True,
            "top_inset_cavity_depth_compensated": cavity_compensation_count > 0,
            "localized_top_insets": True,
            "volumetric_stages": True,
            "weighted_surplus": True,
            "dimension_modes": ["auto", "target", "fixed"],
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    plan["plan_digest"] = _digest(plan)
    return plan


def _structured_retry_strategies(
    diagnostic_codes: set[str],
) -> tuple[str, ...]:
    """Prefer top-inset-aware orders only when validation exposed that constraint."""

    if any(code.startswith("TOP_INSET_") for code in diagnostic_codes):
        return STRUCTURED_ORDER_STRATEGIES
    return tuple(
        strategy
        for strategy in STRUCTURED_ORDER_STRATEGIES
        if not strategy.startswith("top_inset_")
    )


def _finalize_portfolio_search(
    proposal: dict[str, object],
    attempts: list[dict[str, object]],
) -> dict[str, object]:
    """Expose the bounded failure-driven retries without changing project semantics."""

    result = deepcopy(proposal)
    evaluated = sum(
        int(_mapping(item["summary"]).get("candidate_count_evaluated", 0))
        for item in attempts
    )
    feasible = sum(
        int(_mapping(item["summary"]).get("candidate_count_feasible", 0))
        for item in attempts
    )
    summary = _mapping(result["summary"])
    summary["candidate_count_evaluated"] = evaluated
    summary["candidate_count_feasible"] = feasible

    solver = _mapping(result["solver"])
    budgets = _mapping(solver["budgets"])
    budgets["max_structured_portfolios"] = len(STRUCTURED_ORDER_STRATEGIES)
    budgets["max_diversified_portfolios"] = MAX_DIVERSIFIED_PORTFOLIOS
    budgets["max_retry_portfolios"] = (
        len(STRUCTURED_ORDER_STRATEGIES) + MAX_DIVERSIFIED_PORTFOLIOS
    )
    attempt_searches = [
        _mapping(_mapping(item["solver"])["search"])
        for item in attempts
    ]
    directed_count = sum(
        "structured_order_strategy" in item for item in attempt_searches
    )
    hash_count = sum("diversified_order_seed" in item for item in attempt_searches)
    search = _mapping(solver["search"])
    search.update(
        {
            "canonical_portfolio_failed": True,
            "portfolios_evaluated": len(attempts),
            "directed_portfolios_evaluated": directed_count,
            "hash_portfolios_evaluated": hash_count,
            "diversified_portfolios_evaluated": directed_count + hash_count,
            "candidate_count_across_portfolios": feasible,
            "groupings_evaluated_across_portfolios": evaluated,
        }
    )
    result.pop("plan_digest", None)
    result["plan_digest"] = _digest(result)
    return result


def _result(
    normalization: Any,
    project: dict[str, object],
    stack: dict[str, object],
    envelopes: dict[str, object],
    diagnostics: list[dict[str, object]],
    *,
    status: str,
    evaluated: int,
    stage_solver: dict[str, object] | None,
) -> dict[str, object]:
    search = _mapping(stage_solver["search"]) if stage_solver is not None else {}
    result = {
        "schema_version": PARTITION_PLAN_SCHEMA_V1,
        "source": {"source_schema": normalization.source_schema, "migrated": normalization.migrated},
        "project_name": project["project_name"],
        "box": {
            "inner_dimensions_mm": deepcopy(_mapping(project["box"])["inner_dimensions_mm"]),
            "storage_height_mm": _mapping(stack["flat_stack"])["storage_height_mm"],
        },
        "clearance_policy": _clearance_policy(project),
        "flat_stack": deepcopy(stack["flat_stack"]),
        "top_inset_reservations": _top_inset_payload(_mapping(stack["top_inset_reservations"])),
        "support": {"status": "unresolved", "top_support_count": 0, "coverage_ratio": 0.0},
        "stage_support": {"status": "unresolved", "supports": []},
        "stages": [],
        "removal_sequence": [],
        "residuals": {"status": "unresolved", "zones": [], "residual_volume_mm3": 0.0},
        "suggestions": [],
        "placements": [],
        "diagnostics": diagnostics,
        "validation": {"inside_box": False, "box_xy_clearance_respected": False, "no_collisions": False, "clearances_respected": False},
        "summary": {
            "status": status,
            "solution_status": "impossible",
            "materializable": False,
            "requested_container_count": len(_values(project["container_groups"])),
            "placed_container_count": 0,
            "explicit_complement_count": 0,
            "final_body_count": 0,
            "automatic_body_count": 0,
            "stage_count": 0,
            "complete_printable_partition": False,
            "technical_voids_are_clearances_only": False,
            "candidate_count_evaluated": evaluated,
            "candidate_count_feasible": int(search.get("candidate_count", 0)),
        },
        "solver": {
            "kind": "bounded_volumetric_stage_solver",
            "schema_version": stage_solver.get("schema_version") if stage_solver else None,
            "budgets": deepcopy(stage_solver.get("budgets", {})) if stage_solver else {},
            "search": deepcopy(search),
            "deterministic": True,
            "globally_optimal": False,
        },
        "envelope_contract": deepcopy(envelopes),
        "invariants": {
            "fixed_cavity_layouts": True,
            "localized_top_insets": True,
            "volumetric_stages": True,
            "weighted_surplus": True,
            "requested_bodies_only": True,
            "automatic_body_count": 0,
            "suggestions_do_not_mutate": True,
            "free_space_materialized": False,
            "scene_is_not_source_of_truth": True,
        },
    }
    result["plan_digest"] = _digest(result)
    return result


def _clearance_policy(project: dict[str, object]) -> dict[str, object]:
    layout = _mapping(project["layout"])
    defaults = _mapping(layout["clearance_defaults_v1"])
    sources = _mapping(layout["clearance_default_sources_v1"])
    return {
        "box_perimeter_mm": _round(float(layout["container_box_xy_clearance_mm"])),
        "between_bodies_mm": _round(float(layout["layout_clearance_mm"])),
        "box_perimeter_xy_mm": _round(float(layout["container_box_xy_clearance_mm"])),
        "between_bodies_xy_mm": _round(float(layout["layout_clearance_mm"])),
        "between_bodies_z_mm": _round(float(layout["container_z_clearance_mm"])),
        "box_top_z_clearance_mm": _round(float(_mapping(project["box"])["lid_clearance_mm"])),
        "box_bottom_z_clearance_mm": 0.0,
        "vertical_support_gap_mm": _round(float(layout["container_z_clearance_mm"])),
        "vertical_support_contact_mm": 0.0,
        "role_defaults_v1": deepcopy(defaults),
        "role_default_sources_v1": deepcopy(sources),
        "materialize_clearances": False,
    }


def _container_participant(
    contract: dict[str, object],
    group: dict[str, object],
    *,
    top_inset_plan: dict[str, object],
    default_floor_mm: float,
    storage_height_mm: float,
) -> dict[str, object]:
    minimum = _dimension(contract["minimum_outer_envelope_mm"])
    constraints = _mapping(contract["constraints"])
    search_hint = _top_inset_search_hint(
        contract,
        group,
        top_inset_plan,
        default_floor_mm=default_floor_mm,
        storage_height_mm=storage_height_mm,
    )
    return {
        "id": f"container:{contract['container_group_id']}",
        "role": "container",
        "container_group_id": contract["container_group_id"],
        "name": contract["container_name"],
        "minimum_local_mm": minimum,
        "dimension_modes": deepcopy(constraints["dimension_modes"]),
        "target_local_mm": deepcopy(constraints["target_outer_dimensions_mm"]),
        "surplus_preference": constraints["surplus_preference"],
        "external_clearance_effective_v1": deepcopy(group["clearance_effective_v1"]),
        "top_inset_search_hint_v1": search_hint,
    }


def _top_inset_search_hint(
    contract: dict[str, object],
    group: dict[str, object],
    top_inset_plan: dict[str, object],
    *,
    default_floor_mm: float,
    storage_height_mm: float,
) -> dict[str, object]:
    """Expose bounded search hints; physical validation remains authoritative."""

    maximum_inset_depth = max(
        (
            float(item["inset_depth_from_top_mm"])
            for item in _mappings(top_inset_plan["reservations"])
        ),
        default=0.0,
    )
    maximum_cavity_depth = max(
        (
            float(_mapping(item["inner_dimensions_mm"])["z"])
            for item in _mappings(contract["cavity_layout"])
        ),
        default=0.0,
    )
    floor = float(group["floor_thickness_mm"] or default_floor_mm)
    required_height = maximum_cavity_depth + maximum_inset_depth + floor
    return {
        "maximum_inset_depth_mm": _round(maximum_inset_depth),
        "maximum_cavity_depth_mm": _round(maximum_cavity_depth),
        "required_safe_height_mm": _round(required_height),
        "headroom_deficit_mm": _round(max(0.0, required_height - storage_height_mm)),
        "floor_thickness_mm": _round(floor),
        "cavities": [
            {
                "local_origin_mm": deepcopy(item["local_origin_mm"]),
                "inner_dimensions_mm": deepcopy(item["inner_dimensions_mm"]),
            }
            for item in _mappings(contract["cavity_layout"])
        ],
    }


def _solver_clearance_fallbacks(
    participants: list[dict[str, object]],
    default_xy: float,
    default_box_xy: float,
    default_z: float,
) -> tuple[float, float, float]:
    policies = [
        _mapping(item["external_clearance_effective_v1"])
        for item in participants
        if isinstance(item.get("external_clearance_effective_v1"), dict)
    ]
    if not policies:
        return default_xy, default_box_xy, default_z
    between_xy = max(
        float(_mapping(policy["between_mm"])[axis])
        for policy in policies for axis in ("x", "y")
    )
    box_xy = max(
        float(_mapping(policy["box_per_side_xy_mm"])[axis])
        for policy in policies for axis in ("x", "y")
    )
    between_z = max(float(_mapping(policy["between_mm"])["z"]) for policy in policies)
    return between_xy, box_xy, between_z


def _complement_participant(value: dict[str, object]) -> dict[str, object]:
    dimensions = _dimension(value["dimensions_mm"])
    return {
        "id": f"complement:{value['id']}",
        "role": "explicit_complement",
        "requested_complement_id": value["id"],
        "complement_kind": value["kind"],
        "name": value["name"],
        "minimum_local_mm": dimensions,
        "dimension_modes": {"x": "fixed", "y": "fixed", "z": "fixed"},
        "target_local_mm": deepcopy(dimensions),
        "surplus_preference": "fixed",
    }


def _top_inset_payload(value: dict[str, object]) -> dict[str, object]:
    """Keep the resolved reservation contract without duplicating placements."""

    keys = (
        "schema_version", "status", "design_top_z_mm", "total_flat_height_mm",
        "clearance_mm", "reservations", "removal_sequence", "cuts", "supports",
        "cavity_depth_compensations", "support", "blockers", "warnings", "summary",
        "invariants",
    )
    return {key: deepcopy(value[key]) for key in keys if key in value}


def _minimum_envelope_box_proofs(
    envelope_report: dict[str, object],
    project: dict[str, object],
    box: dict[str, float],
    storage_height: float,
) -> list[dict[str, object]]:
    """Expose only orientation-independent necessary bounds as proofs."""

    proofs: list[dict[str, object]] = []
    for container in _mappings(envelope_report["containers"]):
        minimum_value = container.get("minimum_outer_envelope_mm")
        if not isinstance(minimum_value, dict):
            continue
        minimum = _mapping(minimum_value)
        height_exceeded = float(minimum["z"]) > storage_height + _EPSILON
        cavities = container.get("cavity_layout", [])
        single_cavity = isinstance(cavities, list) and len(cavities) <= 1
        direct_xy = float(minimum["x"]) <= box["x"] + _EPSILON and float(minimum["y"]) <= box["y"] + _EPSILON
        rotated_xy = float(minimum["x"]) <= box["y"] + _EPSILON and float(minimum["y"]) <= box["x"] + _EPSILON
        exact_xy_exceeded = single_cavity and not (direct_xy or rotated_xy)
        if not height_exceeded and not exact_xy_exceeded:
            continue
        reason = (
            "sa hauteur minimale depasse la hauteur utile"
            if height_exceeded and not exact_xy_exceeded
            else "son empreinte minimale ne tient dans aucune orientation X/Y"
            if exact_xy_exceeded and not height_exceeded
            else "sa hauteur et son empreinte minimales depassent les bornes utiles"
        )
        proofs.append(
            _diagnostic(
                "MINIMUM_ENVELOPE_EXCEEDS_BOX",
                f"Le conteneur '{container['container_name']}' est incompatible avec la boite : {reason}.",
                "Reduis ce contenu, sa quantite ou une dimension fixe avant de recalculer.",
                str(container["container_group_id"]),
                proof_code="minimum_outer_envelope_exceeds_box_limit_v1",
            )
        )
    minimum_volume = sum(
        _volume(_mapping(item["minimum_outer_envelope_mm"]))
        for item in _mappings(envelope_report["containers"])
        if item.get("status") == "ready"
        and isinstance(item.get("minimum_outer_envelope_mm"), dict)
    )
    minimum_volume += sum(
        _volume(_mapping(item["dimensions_mm"]))
        for item in _mappings(project["fill_elements"])
        if item.get("mode") == "exact"
        and isinstance(item.get("dimensions_mm"), dict)
    )
    box_volume = box["x"] * box["y"] * storage_height
    if minimum_volume > box_volume + _EPSILON:
        excess_cm3 = _round((minimum_volume - box_volume) / 1000.0)
        proofs.append(
            _diagnostic(
                "MINIMUM_VOLUME_EXCEEDS_BOX",
                f"Le volume minimal demande depasse le volume utile de la boite de {excess_cm3} cm3.",
                "Reduis un contenu, sa quantite ou une dimension fixe avant de recalculer.",
                "",
                proof_code="minimum_body_volume_exceeds_useful_box_v1",
            )
        )
    return proofs


def _attach_outcome(
    plan: dict[str, object],
    request_id: str | None,
    request_revision: int | None,
    started_at: float,
) -> dict[str, object]:
    attach_solver_outcome(
        plan,
        request_id=request_id,
        request_revision=request_revision,
        elapsed_ms=(perf_counter() - started_at) * 1000.0,
    )
    plan.pop("plan_digest", None)
    plan["plan_digest"] = _digest(plan)
    return plan


def _diagnostic(
    code: str,
    message: str,
    action: str,
    reference_id: str = "",
    *,
    proof_code: str | None = None,
) -> dict[str, object]:
    diagnostic: dict[str, object] = {
        "code": code,
        "severity": "blocker",
        "message": message,
        "action": action,
        "reference_id": reference_id,
    }
    if proof_code is not None:
        diagnostic["proof"] = {"code": proof_code, "kind": "necessary_bound"}
    return diagnostic


def _notice(code: str, message: str, action: str, reference_id: str = "") -> dict[str, object]:
    return {"code": code, "severity": "warning", "message": message, "action": action, "reference_id": reference_id}


def _digest(value: dict[str, object]) -> str:
    canonical = deepcopy(value)
    summary = _mapping(canonical.get("summary", {}))
    summary.pop("result_status", None)
    summary.pop("result_label", None)
    solver = _mapping(canonical.get("solver", {}))
    solver.pop("result", None)
    solver.pop("telemetry", None)
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("Internal partition value must be a mapping.")
    return value


def _mappings(value: object) -> list[dict[str, Any]]:
    return [_mapping(item) for item in _values(value)]


def _values(value: object) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError("Internal partition value must be a list.")
    return value


def _dimension(value: object) -> dict[str, float]:
    raw = _mapping(value)
    return {axis: float(raw[axis]) for axis in ("x", "y", "z")}


def _rounded(value: dict[str, object]) -> dict[str, float]:
    return {axis: _round(float(value[axis])) for axis in ("x", "y", "z")}


def _volume(value: dict[str, object]) -> float:
    return float(value["x"]) * float(value["y"]) * float(value["z"])


def _round(value: float) -> float:
    return round(float(value), 4)
