"""Explicit minimal layout, optional finishing, and dual materialization.

The session consumes the versioned L01 dependency state, the L02 local
frontiers, and the L03R-B minimal solver. A certified ``minimal_layout`` is a
first-class artifact: it can produce CAD without a finalized plan. Finishing
remains an optional, separately certified transformation and is never invoked
implicitly by calculation, local edits, or materialization.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import time
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
from board_game_insert_generator.incremental_layout_reuse import (
    STATUS_PLACEMENT_REUSED,
    attempt_incremental_minimal_layout_reuse,
    empty_local_reuse_report,
)
from board_game_insert_generator.minimal_layout_solver import MINIMAL_LAYOUT_SOLVER_VERSION
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
GLOBAL_LAYOUT_ARTIFACT_SCHEMA_V1 = "bgig.minimal_layout_artifact.v1"
CACHED_MINIMAL_LAYOUT_SCHEMA_V1 = "bgig.cached_minimal_layout.v1"
CALCULATION_TIMING_SCHEMA_V1 = "bgig.calculation_timing.v1"
FINALIZED_PLAN_ARTIFACT_SCHEMA_V1 = "bgig.finalized_plan_artifact.v1"
ARTIFACT_SELECTION_SCHEMA_V1 = "bgig.materializable_artifact_selection.v1"
SCENE_ARTIFACT_IDENTITY_SCHEMA_V1 = "bgig.scene_artifact_identity.v1"
ARTIFACT_KIND_MINIMAL = "minimal_layout"
ARTIFACT_KIND_FINALIZED = "finalized_plan"
MATERIALIZABLE_ARTIFACT_KINDS = (ARTIFACT_KIND_MINIMAL, ARTIFACT_KIND_FINALIZED)
GLOBAL_SOLVER_VERSION = MINIMAL_LAYOUT_SOLVER_VERSION

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
FinalizerCallable = Callable[[dict[str, object]], dict[str, object]]
FinalCertificateCallable = Callable[[dict[str, object]], bool]


class StagedCalculationSession:
    """Keep reconstructible artifacts for one local Fusion document."""

    def __init__(
        self,
        raw_project: object,
        *,
        solver_settings: Mapping[str, object] | None = None,
        cache_entries: int = 16,
        monotonic_ms: Callable[[], int] | None = None,
    ) -> None:
        self.state = IncrementalProjectState(raw_project)
        self.cache = BoundedArtifactCache(cache_entries)
        self._project = normalize_project_draft(raw_project).project
        self._settings = normalize_solver_settings(solver_settings or {})
        self._settings_digest = canonical_digest(self._settings)
        self._monotonic_ms = monotonic_ms or _system_monotonic_ms
        self._local_analysis: dict[str, object] = {}
        self._local_analysis_digest = canonical_digest({"status": "not_available"})
        self._container_frontiers: tuple[object, ...] = ()
        self._frontier_digests: tuple[tuple[str, str], ...] = ()
        self._request_sequence = 0
        self._active_global_request: GlobalRequestToken | None = None
        self._global_status = STATUS_NOT_COMPUTED
        self._global_partition: dict[str, object] | None = None
        self._global_artifact_digest = ""
        self._global_key_digest = ""
        self._global_cache_status = "not_queried"
        self._global_cache_write_status = "not_attempted"
        self._global_result_source = "not_available"
        self._global_search_elapsed_ms: int | str = "not_applicable"
        self._global_request_elapsed_ms: int | str = "not_applicable"
        self._global_retrieval_elapsed_ms: int | str = "not_applicable"
        self._global_request_id = ""
        self._global_stop_reason = "not_started"
        self._local_reuse = empty_local_reuse_report()
        self._finalized_status = STATUS_NOT_FINALIZED
        self._finalized_partition: dict[str, object] | None = None
        self._finalized_artifact_digest = ""
        self._finalization_key_digest = ""
        self._finalization_cache_status = "not_queried"
        self._finalization_policy = "not_selected"
        self._cad_status = STATUS_NOT_MATERIALIZED
        self._cad_build_digest = ""
        self._cad_identity: dict[str, object] | None = None

    def synchronize(
        self,
        raw_project: object,
        local_analysis: Mapping[str, object],
        *,
        solver_settings: Mapping[str, object] | None = None,
        container_frontiers: Sequence[object] = (),
        frontier_digests: Sequence[tuple[str, str]] = (),
    ) -> dict[str, object]:
        """Refresh dependencies and try fixed-envelope local reuse first."""

        previous_project = deepcopy(self._project)
        previous_partition = deepcopy(self._global_partition)
        previous_minimal_current = self._minimal_current()
        project = normalize_project_draft(raw_project).project
        delta = self.state.update_project(project)
        settings = normalize_solver_settings(solver_settings or self._settings)
        settings_digest = canonical_digest(settings)
        settings_changed = settings_digest != self._settings_digest
        previous_local_analysis_digest = self._local_analysis_digest
        previous_frontier_digests = self._frontier_digests
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
        self._container_frontiers = tuple(container_frontiers)
        self._frontier_digests = tuple(
            sorted((str(key), str(value)) for key, value in frontier_digests)
        )
        local_dependencies_changed = bool(
            self._local_analysis_digest != previous_local_analysis_digest
            or self._frontier_digests != previous_frontier_digests
        )
        dependencies_changed = bool(
            delta.changed or settings_changed or local_dependencies_changed
        )
        self._local_reuse = empty_local_reuse_report(
            stop_reason=(
                "dependencies_unchanged"
                if not dependencies_changed
                else "no_eligible_local_edit"
            )
        )

        if (
            delta.changed
            and not settings_changed
            and previous_minimal_current
            and previous_partition is not None
        ):
            try:
                reuse = attempt_incremental_minimal_layout_reuse(
                    previous_project,
                    project,
                    previous_partition,
                    container_frontiers=self._container_frontiers,
                    effort_profile=str(self._settings["effort"]),
                )
                self._local_reuse = deepcopy(reuse.report)
            except (KeyError, TypeError, ValueError) as exc:
                self._local_reuse = empty_local_reuse_report(
                    status="global_solve_required",
                    stop_reason="local_reuse_input_rejected",
                )
                self._local_reuse["rejection_codes"] = [type(exc).__name__]
                reuse = None

            if (
                reuse is not None
                and reuse.report.get("status") == STATUS_PLACEMENT_REUSED
                and reuse.partition is not None
            ):
                key = self._global_layout_key()
                partition = deepcopy(reuse.partition)
                artifact_digest = canonical_digest(
                    {
                        "schema_version": GLOBAL_LAYOUT_ARTIFACT_SCHEMA_V1,
                        "artifact_kind": ARTIFACT_KIND_MINIMAL,
                        "global_key_digest": key.digest,
                        "partition_plan_digest": partition.get("plan_digest"),
                        "partition": partition,
                    }
                )
                self._active_global_request = None
                self.state.mark_lifecycle_current(
                    STAGE_GLOBAL_LAYOUT,
                    artifact_digest,
                )
                self._global_status = STATUS_CURRENT
                self._global_partition = partition
                self._global_artifact_digest = artifact_digest
                self._global_key_digest = key.digest
                self._global_cache_status = "local_reuse_not_cached"
                self._global_cache_write_status = "not_applicable"
                self._global_result_source = "local_reuse"
                self._global_search_elapsed_ms = "not_applicable"
                self._global_request_elapsed_ms = "not_applicable"
                self._global_retrieval_elapsed_ms = "not_applicable"
                self._global_request_id = (
                    f"local-reuse-revision-{self.state.source_revision}"
                )
                self._global_stop_reason = str(
                    reuse.report.get(
                        "stop_reason",
                        "fixed_envelope_plan_recertified",
                    )
                )
                if self._finalized_partition is not None:
                    self._finalized_status = STATUS_STALE
                else:
                    self._finalized_status = STATUS_NOT_FINALIZED
                self._cad_status = (
                    STATUS_DESYNCHRONIZED
                    if self._cad_identity is not None
                    else STATUS_NOT_MATERIALIZED
                )
                return self.snapshot()

        if settings_changed:
            self._local_reuse = empty_local_reuse_report(
                stop_reason="solver_settings_changed",
            )
        elif not delta.changed and local_dependencies_changed:
            self._local_reuse = empty_local_reuse_report(
                stop_reason="local_dependencies_changed_without_source_edit",
            )
        if dependencies_changed:
            self._invalidate_downstream()
        return self.snapshot()

    def calculate_layout(
        self,
        *,
        request_id: str,
        request_revision: int | None,
        solver: SolverCallable | None = None,
    ) -> dict[str, object]:
        """Run explicitly, or reuse only one certified minimal layout."""

        request_started_ms = self._monotonic_ms()
        key = self._global_layout_key()
        token = self._begin_global_request(key)
        lookup = self.cache.lookup(key)
        if lookup.status == "hit":
            cached = _mapping(lookup.value)
            if cached.get("schema_version") != CACHED_MINIMAL_LAYOUT_SCHEMA_V1:
                raise TypeError("Cached minimal layout has an unexpected schema.")
            cached_partition = cached.get("partition")
            if not isinstance(cached_partition, dict):
                raise TypeError("Cached minimal layout has an unexpected type.")
            partition = deepcopy(cached_partition)
            artifact_digest = lookup.artifact_digest or ""
            search_elapsed_ms = _non_negative_timing(
                cached.get("search_elapsed_ms"),
                "cached search_elapsed_ms",
            )
            request_elapsed_ms = max(0, self._monotonic_ms() - request_started_ms)
            retrieval_elapsed_ms: int | str = request_elapsed_ms
            result_source = "certified_cache"
            cache_write_status = "reused_certified"
        else:
            if solver is None:
                from board_game_insert_generator.minimal_layout_solver import (
                    solve_minimal_layout,
                )

                partition = solve_minimal_layout(
                    self._project,
                    request_id=request_id,
                    request_revision=request_revision,
                    effort_profile=self._settings["effort"],
                    container_frontiers=self._container_frontiers or None,
                    frontier_digests=self._frontier_digests,
                )
            else:
                # The injectable lane keeps deterministic legacy fixtures usable;
                # production always takes the minimal solver path above.
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
                    "artifact_kind": ARTIFACT_KIND_MINIMAL,
                    "global_key_digest": key.digest,
                    "partition_plan_digest": partition.get("plan_digest"),
                    "partition": partition,
                }
            )
            request_elapsed_ms = max(0, self._monotonic_ms() - request_started_ms)
            search_elapsed_ms = request_elapsed_ms
            retrieval_elapsed_ms = "not_applicable"
            result_source = "fresh_search"
            cache_write_status = "not_attempted"

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
            if _minimal_placement_certified(partition):
                self.cache.put(
                    key,
                    artifact_digest,
                    {
                        "schema_version": CACHED_MINIMAL_LAYOUT_SCHEMA_V1,
                        "partition": deepcopy(partition),
                        "search_elapsed_ms": search_elapsed_ms,
                    },
                )
                cache_write_status = "stored_certified"
            else:
                cache_write_status = "skipped_non_certified"
        self.state.mark_lifecycle_current(STAGE_GLOBAL_LAYOUT, artifact_digest)
        self._global_status = STATUS_CURRENT
        self._global_partition = deepcopy(partition)
        self._global_artifact_digest = artifact_digest
        self._global_key_digest = key.digest
        self._global_cache_status = lookup.status
        self._global_cache_write_status = cache_write_status
        self._global_result_source = result_source
        self._global_search_elapsed_ms = search_elapsed_ms
        self._global_request_elapsed_ms = request_elapsed_ms
        self._global_retrieval_elapsed_ms = retrieval_elapsed_ms
        self._global_request_id = request_id
        self._global_stop_reason = _solver_stop_reason(partition)
        if self._finalized_partition is not None:
            self._finalized_status = STATUS_STALE
        else:
            self._finalized_status = STATUS_NOT_FINALIZED
        self._cad_status = (
            STATUS_DESYNCHRONIZED
            if self._cad_identity is not None
            else STATUS_NOT_MATERIALIZED
        )
        return {
            "partition": deepcopy(partition),
            "solver_result": _partition_solver_result(
                partition,
                request_id=request_id,
                request_revision=request_revision,
            ),
            "staged_calculation": self.snapshot(),
        }

    def finalize_volume(
        self,
        *,
        finalizer: FinalizerCallable | None = None,
        finishing_policy: str = "not_selected",
        finishing_budget_digest: str = "",
        finalizer_id: str = "",
        finalizer_version: str = "",
        certify: FinalCertificateCallable | None = None,
    ) -> dict[str, object]:
        """Create a distinct finalized artifact through an explicit policy.

        L03R-C deliberately ships no finishing transformation. Callers must
        provide one; a missing or rejected transformation leaves the current
        minimal layout untouched and materializable.
        """

        if not self._minimal_current():
            raise StagedCalculationError(
                "Calcule un agencement minimal courant avant de choisir une finition."
            )
        if finalizer is None:
            raise StagedCalculationError(
                "Aucune methode de finition n est encore disponible dans ce lot ; "
                "les volumes minimaux restent materialisables."
            )
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                finishing_policy,
                finishing_budget_digest,
                finalizer_id,
                finalizer_version,
            )
        ):
            raise StagedCalculationError(
                "La politique, le budget et la version du finaliseur doivent etre explicites."
            )

        candidate = finalizer(deepcopy(self._global_partition))
        if not isinstance(candidate, dict):
            raise StagedCalculationError(
                "La methode de finition n a pas produit un plan exploitable."
            )
        validator = certify or (
            lambda value: _finalized_certified(
                value,
                source_minimal_artifact_digest=self._global_artifact_digest,
            )
        )
        if not validator(candidate):
            self._global_stop_reason = "finalization_certificate_rejected"
            raise StagedCalculationError(
                "La finalisation a ete rejetee ; le plan minimal courant est conserve."
            )

        key = FinalizationKey(
            global_layout_digest=self._global_artifact_digest,
            finishing_policy=finishing_policy,
            finishing_budget_digest=finishing_budget_digest,
            finalizer_id=finalizer_id,
            finalizer_version=finalizer_version,
        )
        lookup = self.cache.lookup(key)
        if lookup.status == "hit":
            if not isinstance(lookup.value, dict):
                raise TypeError("Cached finalized plan has an unexpected type.")
            finalized = deepcopy(lookup.value)
            artifact_digest = lookup.artifact_digest or ""
        else:
            finalized = deepcopy(candidate)
            artifact_digest = canonical_digest(
                {
                    "schema_version": FINALIZED_PLAN_ARTIFACT_SCHEMA_V1,
                    "artifact_kind": ARTIFACT_KIND_FINALIZED,
                    "finalization_key_digest": key.digest,
                    "source_minimal_artifact_digest": self._global_artifact_digest,
                    "partition_plan_digest": finalized.get("plan_digest"),
                    "partition": finalized,
                }
            )
            self.cache.put(key, artifact_digest, finalized)

        self.state.mark_lifecycle_current(STAGE_FINALIZED_PLAN, artifact_digest)
        self._finalized_status = STATUS_CURRENT
        self._finalized_partition = deepcopy(finalized)
        self._finalized_artifact_digest = artifact_digest
        self._finalization_key_digest = key.digest
        self._finalization_cache_status = lookup.status
        self._finalization_policy = finishing_policy
        return {
            "partition": deepcopy(finalized),
            "solver_result": _partition_solver_result(finalized),
            "staged_calculation": self.snapshot(),
        }

    def select_materializable_artifact(
        self,
        artifact_kind: str = ARTIFACT_KIND_MINIMAL,
    ) -> dict[str, object]:
        """Select one exact current artifact without solving or finalizing."""

        if artifact_kind not in MATERIALIZABLE_ARTIFACT_KINDS:
            raise StagedCalculationError(
                "Artefact inconnu ; choisis minimal_layout ou finalized_plan."
            )
        if artifact_kind == ARTIFACT_KIND_MINIMAL:
            if not self._minimal_current():
                raise StagedCalculationError(
                    "Calcule un agencement minimal certifie avant de le materialiser."
                )
            partition = self._global_partition
            artifact_digest = self._global_artifact_digest
        else:
            if not self._finalized_current():
                raise StagedCalculationError(
                    "Aucun plan finalise courant n est disponible ; "
                    "le plan minimal peut rester materialisable."
                )
            partition = self._finalized_partition
            artifact_digest = self._finalized_artifact_digest
        if partition is None:
            raise StagedCalculationError("L artefact courant est indisponible.")
        return {
            "schema_version": ARTIFACT_SELECTION_SCHEMA_V1,
            "artifact_kind": artifact_kind,
            "artifact_digest": artifact_digest,
            "partition_plan_digest": str(partition.get("plan_digest", "")),
            "source_revision": self.state.source_revision,
            "partition": deepcopy(partition),
        }

    def materializable_partition(
        self,
        artifact_kind: str = ARTIFACT_KIND_MINIMAL,
    ) -> dict[str, object]:
        """Compatibility accessor returning only the selected partition."""

        selection = self.select_materializable_artifact(artifact_kind)
        return deepcopy(_mapping(selection["partition"]))

    def record_cad_ready(self, cad_build: Mapping[str, object]) -> None:
        """Record CAD prepared for the exact selected artifact, not Fusion proof."""

        if str(cad_build.get("status")) != "ready_for_fusion":
            raise StagedCalculationError(
                "L artefact selectionne n a pas produit de CAD IR materialisable."
            )
        identity = _mapping(cad_build.get("artifact_identity", {}))
        artifact_kind = str(identity.get("artifact_kind", ""))
        selection = self.select_materializable_artifact(artifact_kind)
        expected = {
            "schema_version": SCENE_ARTIFACT_IDENTITY_SCHEMA_V1,
            "artifact_kind": artifact_kind,
            "artifact_digest": selection["artifact_digest"],
            "partition_plan_digest": selection["partition_plan_digest"],
            "source_revision": selection["source_revision"],
        }
        for key, value in expected.items():
            if identity.get(key) != value:
                raise StagedCalculationError(
                    "La CAD IR ne correspond pas exactement a l artefact courant."
                )
        cad_ir_digest = str(identity.get("cad_ir_digest", ""))
        if not cad_ir_digest or cad_ir_digest != str(cad_build.get("cad_ir_digest", "")):
            raise StagedCalculationError(
                "Le digest CAD IR de l artefact selectionne est absent ou incoherent."
            )
        self._cad_status = STATUS_CAD_READY
        self._cad_build_digest = canonical_digest(dict(cad_build))
        self._cad_identity = deepcopy(identity)

    def snapshot(self) -> dict[str, object]:
        """Expose compact states, identities, provenance and next action."""

        minimal_current = self._minimal_current()
        finalized_current = self._finalized_current()
        minimal_payload = {
            "status": self._global_status,
            "artifact_kind": ARTIFACT_KIND_MINIMAL,
            "artifact_digest": self._global_artifact_digest,
            "key_digest": self._global_key_digest,
            "request_id": self._global_request_id,
            "cache_status": self._global_cache_status,
            "cache_write_status": self._global_cache_write_status,
            "calculation_timing": {
                "schema_version": CALCULATION_TIMING_SCHEMA_V1,
                "result_source": self._global_result_source,
                "search_elapsed_ms": self._global_search_elapsed_ms,
                "request_elapsed_ms": self._global_request_elapsed_ms,
                "retrieval_elapsed_ms": self._global_retrieval_elapsed_ms,
            },
            "solver_result_status": _solver_status(self._global_partition),
            "stop_reason": self._global_stop_reason,
            "placement_certified": minimal_current,
            "partition_plan_digest": (
                str(self._global_partition.get("plan_digest", ""))
                if self._global_partition is not None
                else ""
            ),
            "source_revision": self.state.source_revision,
            "materializable_without_finalization": minimal_current,
            "finalization_required": False,
        }
        finalized_payload = {
            "status": self._finalized_status,
            "artifact_kind": ARTIFACT_KIND_FINALIZED,
            "artifact_digest": self._finalized_artifact_digest,
            "key_digest": self._finalization_key_digest,
            "cache_status": self._finalization_cache_status,
            "finishing_policy": self._finalization_policy,
            "source_minimal_artifact_digest": (
                self._global_artifact_digest if finalized_current else ""
            ),
            "partition_plan_digest": (
                str(self._finalized_partition.get("plan_digest", ""))
                if finalized_current and self._finalized_partition is not None
                else ""
            ),
            "source_revision": self.state.source_revision,
            "materializable": finalized_current,
        }
        next_action = "calculate_layout"
        if minimal_current:
            if not self._cad_identity_matches_artifact(ARTIFACT_KIND_MINIMAL):
                next_action = "materialize_minimal_in_fusion"
            else:
                next_action = "choose_optional_finishing_or_export"
        return {
            "schema_version": STAGED_CALCULATION_SCHEMA_V1,
            "source_revision": self.state.source_revision,
            "local_analysis_digest": self._local_analysis_digest,
            "local_reuse": deepcopy(self._local_reuse),
            # ``global_layout`` remains as an additive compatibility alias.
            "global_layout": deepcopy(minimal_payload),
            "minimal_layout": minimal_payload,
            "finalized_plan": finalized_payload,
            "materialization": {
                "status": self._cad_status,
                "cad_build_digest": self._cad_build_digest,
                "artifact_identity": deepcopy(self._cad_identity),
                "fusion_observed": False,
            },
            "available_artifacts": {
                ARTIFACT_KIND_MINIMAL: minimal_current,
                ARTIFACT_KIND_FINALIZED: finalized_current,
            },
            "next_action": next_action,
            "cache": self.cache.telemetry(),
            "invariants": {
                "global_solve_is_explicit": True,
                "global_solve_uses_minimal_layout_portfolio": True,
                "finalization_is_explicit": True,
                "finalization_is_optional": True,
                "minimal_materialization_requires_finalized_plan": False,
                "artifact_selection_is_explicit": True,
                "automatic_body_count_added_by_orchestrator": 0,
                "solver_method_or_budget_changed": False,
                "project_schema_mutated": False,
                "fusion_validation_claimed": False,
            },
        }

    def current_minimal_partition(self) -> dict[str, object] | None:
        """Return the current certified minimal plan without computing it."""

        return deepcopy(self._global_partition) if self._minimal_current() else None

    def _minimal_current(self) -> bool:
        return bool(
            self._global_status == STATUS_CURRENT
            and self._global_partition is not None
            and _minimal_placement_certified(self._global_partition)
        )

    def _finalized_current(self) -> bool:
        return bool(
            self._finalized_status == STATUS_CURRENT
            and self._finalized_partition is not None
            and _finalized_certified(
                self._finalized_partition,
                source_minimal_artifact_digest=self._global_artifact_digest,
            )
        )

    def _cad_identity_matches_artifact(self, artifact_kind: str) -> bool:
        if self._cad_identity is None:
            return False
        try:
            selection = self.select_materializable_artifact(artifact_kind)
        except StagedCalculationError:
            return False
        return all(
            self._cad_identity.get(key) == selection.get(key)
            for key in (
                "artifact_kind",
                "artifact_digest",
                "partition_plan_digest",
                "source_revision",
            )
        ) and bool(self._cad_identity.get("cad_ir_digest"))

    def _invalidate_downstream(self) -> None:
        self._active_global_request = None
        if self._global_partition is not None:
            self._global_status = STATUS_STALE
        if self._finalized_partition is not None:
            self._finalized_status = STATUS_STALE
        if self._cad_identity is not None:
            self._cad_status = STATUS_DESYNCHRONIZED

    def _global_layout_key(self) -> GlobalLayoutKey:
        frontier_digests = list(self._frontier_digests)
        if not frontier_digests:
            containers = _mappings(self._local_analysis.get("containers", []))
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


def _minimal_placement_certified(partition: dict[str, object]) -> bool:
    summary = _mapping(partition.get("summary", {}))
    minimal = _mapping(partition.get("minimal_layout", {}))
    certificate = _mapping(minimal.get("global_certificate", {}))
    variant_certificate_value = minimal.get("container_variant_certificate")
    variant_certified = True
    if isinstance(variant_certificate_value, Mapping):
        variant_certified = bool(variant_certificate_value.get("certified"))
    return bool(
        _solver_status(partition) == SOLUTION_FOUND
        and summary.get("status") == "constructed"
        and summary.get("placement_certified") is True
        and minimal.get("artifact_kind") == ARTIFACT_KIND_MINIMAL
        and minimal.get("finalization_applied") is False
        and certificate.get("certified") is True
        and variant_certified
    )


def _finalized_certified(
    partition: dict[str, object],
    *,
    source_minimal_artifact_digest: str,
) -> bool:
    summary = _mapping(partition.get("summary", {}))
    finalization = _mapping(partition.get("finalization", {}))
    certificate = _mapping(finalization.get("certificate", {}))
    return bool(
        _solver_status(partition) == SOLUTION_FOUND
        and summary.get("status") == "constructed"
        and summary.get("materializable") is True
        and finalization.get("artifact_kind") == ARTIFACT_KIND_FINALIZED
        and finalization.get("source_minimal_artifact_digest")
        == source_minimal_artifact_digest
        and certificate.get("certified") is True
    )


def _partition_solver_result(
    partition: dict[str, object] | None,
    *,
    request_id: str | None = None,
    request_revision: int | None = None,
) -> dict[str, object] | None:
    if not isinstance(partition, dict):
        return None
    solver = _mapping(partition.get("solver", {}))
    result = solver.get("result")
    if not isinstance(result, Mapping):
        return None
    payload = deepcopy(dict(result))
    telemetry = deepcopy(_mapping(solver.get("telemetry", {})))
    if request_id is not None:
        artifact_request = deepcopy(telemetry.get("request"))
        current_request = {
            "id": request_id,
            "revision": (
                request_revision
                if request_revision is not None
                else "not_applicable"
            ),
        }
        if artifact_request != current_request:
            telemetry["artifact_request"] = artifact_request
        telemetry["request"] = current_request
        telemetry["request_scope"] = "staged_action"
    payload["telemetry"] = telemetry
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
            "family": {"id": "staged_orchestrator", "version": "2"},
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


def _system_monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000


def _non_negative_timing(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TypeError(f"{field} must be a non-negative integer.")
    return value


def _mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError("Staged calculation collection must be a sequence.")
    return [_mapping(item) for item in value]