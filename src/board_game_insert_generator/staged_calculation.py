"""Explicit global layout, finalization and materialization gating for P64-L03.

The session consumes P64-L01 identities and P64-L02 frontier digests.  It does
not change solver search, budgets or geometry.  The compatibility finalizer
accepts an already complete, commonly certified partition without modifying it;
future finishing policies remain owned by P64-F01/F02/F03.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from board_game_insert_generator.incremental_project_state import (
    STAGE_FINALIZED_PLAN,
    STAGE_GLOBAL_LAYOUT,
    BoundedArtifactCache,
    FinalizationKey,
    GlobalLayoutKey,
    IncrementalProjectState,
    canonical_digest,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from board_game_insert_generator.solver_outcome import (
    SOLUTION_FOUND,
    SOLVER_RESULT_SCHEMA_V1,
    SOLVER_TELEMETRY_SCHEMA_V1,
    STALE_OR_CANCELLED,
    result_label,
)
from board_game_insert_generator.solver_settings import normalize_solver_settings


STAGED_CALCULATION_SCHEMA_V1 = "bgig.staged_calculation.v1"
GLOBAL_LAYOUT_ARTIFACT_SCHEMA_V1 = "bgig.global_layout_artifact.v1"
FINALIZED_PLAN_ARTIFACT_SCHEMA_V1 = "bgig.finalized_plan_artifact.v1"
GLOBAL_SOLVER_VERSION = "partition_solver_portfolio.v1"
COMPATIBILITY_FINALIZER_ID = "preserve_certified_partition"
COMPATIBILITY_FINALIZER_VERSION = "1"
COMPATIBILITY_FINISHING_POLICY = "preserve_existing_certified_closure"
FINISHING_BUDGET_DIGEST = canonical_digest(
    {
        "policy": COMPATIBILITY_FINISHING_POLICY,
        "geometry_transformations": 0,
        "automatic_bodies": 0,
    }
)

STATUS_NOT_COMPUTED = "not_computed"
STATUS_CURRENT = "current"
STATUS_STALE = "stale"
STATUS_NOT_FINALIZED = "not_finalized"
STATUS_CAD_READY = "cad_ready"
STATUS_NOT_MATERIALIZED = "not_materialized"
STATUS_DESYNCHRONIZED = "desynchronized"


class StagedCalculationError(ValueError):
    """Raised when an explicit stage cannot consume the current predecessor."""


@dataclass(frozen=True)
class GlobalRequestToken:
    request_id: str
    source_revision: int
    global_key_digest: str
    settings_digest: str


SolverCallable = Callable[..., dict[str, object]]
FinalCertificateCallable = Callable[[dict[str, object]], bool]


class StagedCalculationSession:
    """Keep reconstructible staged artifacts for one local Fusion document."""

    def __init__(
        self,
        raw_project: object,
        *,
        solver_settings: Mapping[str, object] | None = None,
        cache_entries: int = 16,
    ) -> None:
        self.state = IncrementalProjectState(raw_project)
        self.cache = BoundedArtifactCache(cache_entries)
        self._project = normalize_project_draft(raw_project).project
        self._settings = normalize_solver_settings(solver_settings or {})
        self._settings_digest = canonical_digest(self._settings)
        self._local_analysis: dict[str, object] = {}
        self._local_analysis_digest = canonical_digest({"status": "not_available"})
        self._request_sequence = 0
        self._active_global_request: GlobalRequestToken | None = None
        self._global_status = STATUS_NOT_COMPUTED
        self._global_partition: dict[str, object] | None = None
        self._global_artifact_digest = ""
        self._global_key_digest = ""
        self._global_cache_status = "not_queried"
        self._global_request_id = ""
        self._global_stop_reason = "not_started"
        self._finalized_status = STATUS_NOT_FINALIZED
        self._finalized_partition: dict[str, object] | None = None
        self._finalized_artifact_digest = ""
        self._finalization_key_digest = ""
        self._finalization_cache_status = "not_queried"
        self._cad_status = STATUS_NOT_MATERIALIZED
        self._cad_build_digest = ""

    def synchronize(
        self,
        raw_project: object,
        local_analysis: Mapping[str, object],
        *,
        solver_settings: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Refresh dependencies and mark downstream artifacts stale only."""

        project = normalize_project_draft(raw_project).project
        delta = self.state.update_project(project)
        settings = normalize_solver_settings(solver_settings or self._settings)
        settings_digest = canonical_digest(settings)
        settings_changed = settings_digest != self._settings_digest
        self._project = project
        self._settings = settings
        self._settings_digest = settings_digest
        self._local_analysis = deepcopy(dict(local_analysis))
        self._local_analysis_digest = canonical_digest(
            {
                "containers": self._local_analysis.get("containers", []),
                "reactive_global_bounds": self._local_analysis.get(
                    "reactive_global_bounds", {}
                ),
            }
        )
        if delta.changed or settings_changed:
            self._invalidate_downstream()
        return self.snapshot()

    def calculate_layout(
        self,
        *,
        request_id: str,
        request_revision: int | None,
        solver: SolverCallable | None = None,
    ) -> dict[str, object]:
        """Run or reuse one explicitly requested global layout."""

        key = self._global_layout_key()
        token = self._begin_global_request(key)
        lookup = self.cache.lookup(key)
        if lookup.status == "hit":
            if not isinstance(lookup.value, dict):
                raise TypeError("Cached global layout has an unexpected type.")
            partition = deepcopy(lookup.value)
            artifact_digest = lookup.artifact_digest or ""
        else:
            if solver is None:
                from board_game_insert_generator.partition_solver import (
                    solve_partition_plan,
                )

                solver = solve_partition_plan
            partition = solver(
                self._project,
                request_id=request_id,
                request_revision=request_revision,
                solver_method=self._settings["method"],
                effort_profile=self._settings["effort"],
            )
            artifact_digest = canonical_digest(
                {
                    "schema_version": GLOBAL_LAYOUT_ARTIFACT_SCHEMA_V1,
                    "global_key_digest": key.digest,
                    "partition": partition,
                }
            )

        if not self._accept_global_request(token):
            self._global_stop_reason = "dependencies_changed_during_global_run"
            return {
                "partition": None,
                "solver_result": _stale_solver_result(
                    request_id,
                    request_revision,
                    self._global_stop_reason,
                ),
                "staged_calculation": self.snapshot(),
            }

        if lookup.status != "hit":
            self.cache.put(key, artifact_digest, partition)
        self.state.mark_lifecycle_current(STAGE_GLOBAL_LAYOUT, artifact_digest)
        self._global_status = STATUS_CURRENT
        self._global_partition = deepcopy(partition)
        self._global_artifact_digest = artifact_digest
        self._global_key_digest = key.digest
        self._global_cache_status = lookup.status
        self._global_request_id = request_id
        self._global_stop_reason = _solver_stop_reason(partition)
        if self._finalized_partition is not None:
            self._finalized_status = STATUS_STALE
        else:
            self._finalized_status = STATUS_NOT_FINALIZED
        if self._cad_build_digest:
            self._cad_status = STATUS_DESYNCHRONIZED
        else:
            self._cad_status = STATUS_NOT_MATERIALIZED
        return {
            "partition": deepcopy(partition),
            "solver_result": _partition_solver_result(partition),
            "staged_calculation": self.snapshot(),
        }

    def finalize_volume(
        self,
        *,
        certify: FinalCertificateCallable | None = None,
    ) -> dict[str, object]:
        """Accept the current certified closure without changing its geometry."""

        if self._global_status != STATUS_CURRENT or self._global_partition is None:
            raise StagedCalculationError(
                "Calcule l agencement courant avant de finaliser le volume."
            )
        if not _placement_certified(self._global_partition):
            raise StagedCalculationError(
                "Seul un agencement complet et certifie peut etre finalise."
            )
        validator = certify or _placement_certified
        candidate = deepcopy(self._global_partition)
        if not validator(candidate):
            self._global_stop_reason = "finalization_certificate_rejected"
            raise StagedCalculationError(
                "La finalisation a ete rejetee ; l agencement de base est conserve."
            )

        key = FinalizationKey(
            global_layout_digest=self._global_artifact_digest,
            finishing_policy=COMPATIBILITY_FINISHING_POLICY,
            finishing_budget_digest=FINISHING_BUDGET_DIGEST,
            finalizer_id=COMPATIBILITY_FINALIZER_ID,
            finalizer_version=COMPATIBILITY_FINALIZER_VERSION,
        )
        lookup = self.cache.lookup(key)
        if lookup.status == "hit":
            if not isinstance(lookup.value, dict):
                raise TypeError("Cached finalized plan has an unexpected type.")
            finalized = deepcopy(lookup.value)
            artifact_digest = lookup.artifact_digest or ""
        else:
            finalized = candidate
            artifact_digest = canonical_digest(
                {
                    "schema_version": FINALIZED_PLAN_ARTIFACT_SCHEMA_V1,
                    "finalization_key_digest": key.digest,
                    "global_layout_digest": self._global_artifact_digest,
                    "partition_plan_digest": finalized.get("plan_digest"),
                    "geometry_changed": False,
                }
            )
            self.cache.put(key, artifact_digest, finalized)

        self.state.mark_lifecycle_current(STAGE_FINALIZED_PLAN, artifact_digest)
        self._finalized_status = STATUS_CURRENT
        self._finalized_partition = deepcopy(finalized)
        self._finalized_artifact_digest = artifact_digest
        self._finalization_key_digest = key.digest
        self._finalization_cache_status = lookup.status
        self._cad_status = STATUS_NOT_MATERIALIZED
        self._cad_build_digest = ""
        return {
            "partition": deepcopy(finalized),
            "solver_result": _partition_solver_result(finalized),
            "staged_calculation": self.snapshot(),
        }

    def materializable_partition(self) -> dict[str, object]:
        """Return only a current finalized plan; never trigger solving."""

        if (
            self._finalized_status != STATUS_CURRENT
            or self._finalized_partition is None
            or not self.state.can_materialize
        ):
            raise StagedCalculationError(
                "Finalise le volume courant avant de materialiser dans Fusion."
            )
        return deepcopy(self._finalized_partition)

    def record_cad_ready(self, cad_build: Mapping[str, object]) -> None:
        """Record a prepared CAD payload without claiming Fusion observation."""

        if str(cad_build.get("status")) != "ready_for_fusion":
            raise StagedCalculationError(
                "Le plan finalise n a pas produit de CAD IR materialisable."
            )
        self._cad_status = STATUS_CAD_READY
        self._cad_build_digest = canonical_digest(dict(cad_build))

    def snapshot(self) -> dict[str, object]:
        """Expose compact states, provenance and next explicit action."""

        placement_certified = (
            self._global_status == STATUS_CURRENT
            and self._global_partition is not None
            and _placement_certified(self._global_partition)
        )
        finalized_current = (
            self._finalized_status == STATUS_CURRENT
            and self._finalized_partition is not None
            and self.state.can_materialize
        )
        next_action = "calculate_layout"
        if placement_certified and not finalized_current:
            next_action = "finalize_volume"
        elif finalized_current and self._cad_status != STATUS_CAD_READY:
            next_action = "materialize_in_fusion"
        elif finalized_current:
            next_action = "none"
        return {
            "schema_version": STAGED_CALCULATION_SCHEMA_V1,
            "source_revision": self.state.source_revision,
            "local_analysis_digest": self._local_analysis_digest,
            "global_layout": {
                "status": self._global_status,
                "artifact_digest": self._global_artifact_digest,
                "key_digest": self._global_key_digest,
                "request_id": self._global_request_id,
                "cache_status": self._global_cache_status,
                "solver_result_status": _solver_status(self._global_partition),
                "stop_reason": self._global_stop_reason,
                "placement_certified": placement_certified,
                "finalization_required": placement_certified
                and not finalized_current,
            },
            "finalized_plan": {
                "status": self._finalized_status,
                "artifact_digest": self._finalized_artifact_digest,
                "key_digest": self._finalization_key_digest,
                "cache_status": self._finalization_cache_status,
                "finishing_policy": COMPATIBILITY_FINISHING_POLICY,
                "geometry_changed": False,
                "source_global_artifact_digest": (
                    self._global_artifact_digest if finalized_current else ""
                ),
                "partition_plan_digest": (
                    str(self._finalized_partition.get("plan_digest", ""))
                    if finalized_current and self._finalized_partition is not None
                    else ""
                ),
                "materializable": finalized_current,
            },
            "materialization": {
                "status": self._cad_status,
                "cad_build_digest": self._cad_build_digest,
                "fusion_observed": False,
            },
            "next_action": next_action,
            "cache": self.cache.telemetry(),
            "invariants": {
                "global_solve_is_explicit": True,
                "finalization_is_explicit": True,
                "materialization_requires_current_finalized_plan": True,
                "compatibility_finalizer_changes_geometry": False,
                "automatic_body_count_added_by_finalizer": 0,
                "solver_method_or_budget_changed": False,
                "project_schema_mutated": False,
                "fusion_validation_claimed": False,
            },
        }

    def _invalidate_downstream(self) -> None:
        self._active_global_request = None
        if self._global_partition is not None:
            self._global_status = STATUS_STALE
        if self._finalized_partition is not None:
            self._finalized_status = STATUS_STALE
        if self._cad_build_digest:
            self._cad_status = STATUS_DESYNCHRONIZED

    def _global_layout_key(self) -> GlobalLayoutKey:
        containers = _mappings(self._local_analysis.get("containers", []))
        frontier_digests = []
        for container in containers:
            group_id = str(container.get("container_group_id", ""))
            digest = str(container.get("frontier_digest", ""))
            if not digest:
                digest = canonical_digest(
                    {
                        "container_group_id": group_id,
                        "summary": container.get("summary", {}),
                    }
                )
            frontier_digests.append((group_id, digest))
        return GlobalLayoutKey(
            frontier_digests=tuple(sorted(frontier_digests)),
            box_context_digest=self.state.snapshot.box_context_digest,
            top_reservation_digest=self.state.snapshot.top_reservation_digest,
            solver_method=self._settings["method"],
            solver_version=GLOBAL_SOLVER_VERSION,
            effort_profile=self._settings["effort"],
            ranking_digest=canonical_digest(
                {
                    "solver_preference": self._project.get(
                        "solver_preference", "balanced"
                    ),
                    "project_solver_input_digest": canonical_digest(self._project),
                }
            ),
        )

    def _begin_global_request(self, key: GlobalLayoutKey) -> GlobalRequestToken:
        self._request_sequence += 1
        token = GlobalRequestToken(
            request_id=canonical_digest(
                {
                    "source_revision": self.state.source_revision,
                    "global_key_digest": key.digest,
                    "settings_digest": self._settings_digest,
                    "sequence": self._request_sequence,
                }
            ),
            source_revision=self.state.source_revision,
            global_key_digest=key.digest,
            settings_digest=self._settings_digest,
        )
        self._active_global_request = token
        return token

    def _accept_global_request(self, token: GlobalRequestToken) -> bool:
        active = self._active_global_request
        self._active_global_request = None
        return bool(
            active == token
            and token.source_revision == self.state.source_revision
            and token.settings_digest == self._settings_digest
            and token.global_key_digest == self._global_layout_key().digest
        )


def _placement_certified(partition: dict[str, object]) -> bool:
    summary = _mapping(partition.get("summary", {}))
    return bool(
        _solver_status(partition) == SOLUTION_FOUND
        and summary.get("status") == "constructed"
        and summary.get("materializable")
    )


def _partition_solver_result(
    partition: dict[str, object] | None,
) -> dict[str, object] | None:
    if not isinstance(partition, dict):
        return None
    solver = _mapping(partition.get("solver", {}))
    result = solver.get("result")
    if not isinstance(result, Mapping):
        return None
    payload = deepcopy(dict(result))
    payload["telemetry"] = deepcopy(solver.get("telemetry"))
    return payload


def _solver_status(partition: dict[str, object] | None) -> str:
    result = _partition_solver_result(partition)
    return str(result.get("status", "not_computed")) if result else "not_computed"


def _solver_stop_reason(partition: dict[str, object]) -> str:
    result = _partition_solver_result(partition) or {}
    telemetry = _mapping(result.get("telemetry", {}))
    return str(telemetry.get("stop_reason", "not_available"))


def _stale_solver_result(
    request_id: str,
    request_revision: int | None,
    stop_reason: str,
) -> dict[str, object]:
    return {
        "schema_version": SOLVER_RESULT_SCHEMA_V1,
        "status": STALE_OR_CANCELLED,
        "label": result_label(STALE_OR_CANCELLED),
        "legacy_summary_status": "not_applicable",
        "proof": None,
        "materializable": False,
        "telemetry": {
            "schema_version": SOLVER_TELEMETRY_SCHEMA_V1,
            "family": {"id": "staged_orchestrator", "version": "1"},
            "request": {
                "id": request_id,
                "revision": (
                    request_revision
                    if request_revision is not None
                    else "not_applicable"
                ),
            },
            "elapsed_ms": "not_applicable",
            "budgets": {},
            "counters": {},
            "prunes": {},
            "diagnostic_code_counts": {},
            "stop_reason": stop_reason,
        },
    }


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Staged calculation value must be a mapping.")
    return dict(value)


def _mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError("Staged calculation collection must be a sequence.")
    return [_mapping(item) for item in value]
