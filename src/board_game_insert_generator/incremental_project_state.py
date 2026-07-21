"""Pure incremental dependency state for P64-L01.

The module deliberately does not schedule local analysis, global solving or
Fusion materialization.  It gives those future orchestrators deterministic
keys, targeted invalidation and fail-closed stale/cache decisions while the
existing P44 runtime remains unchanged.
"""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
import re
from typing import Mapping

from board_game_insert_generator.project_v1 import normalize_project_draft


INCREMENTAL_STATE_SCHEMA_V1 = "bgig.incremental_project_state.v1"
CACHE_SCHEMA_V1 = "bgig.incremental_artifact_cache.v1"

STAGE_ASSET_RESOLUTION = "asset_resolution"
STAGE_CONTAINER_FRONTIER = "container_frontier"
STAGE_CONTEXT_ANNOTATION = "context_annotation"
STAGE_GLOBAL_LAYOUT = "global_layout"
STAGE_FINALIZED_PLAN = "finalized_plan"
STAGE_MATERIALIZED = "materialized"

STATUS_CURRENT = "current"
STATUS_STALE = "stale"

_LOCAL_STAGES = frozenset(
    {STAGE_ASSET_RESOLUTION, STAGE_CONTAINER_FRONTIER, STAGE_CONTEXT_ANNOTATION}
)
_LIFECYCLE_STAGES = frozenset(
    {STAGE_GLOBAL_LAYOUT, STAGE_FINALIZED_PLAN, STAGE_MATERIALIZED}
)
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def canonical_digest(value: object) -> str:
    """Hash one JSON-compatible value with a deterministic representation."""

    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def _require_identifier(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")


def _require_digest(value: str, field: str) -> None:
    if not isinstance(value, str) or _DIGEST_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field} must be a complete lowercase SHA-256 digest.")


def _require_ordered_digest_pairs(
    values: tuple[tuple[str, str], ...], field: str
) -> None:
    identifiers = tuple(identifier for identifier, _ in values)
    if identifiers != tuple(sorted(identifiers)) or len(set(identifiers)) != len(identifiers):
        raise ValueError(f"{field} must contain unique identifiers in stable order.")
    for identifier, digest in values:
        _require_identifier(identifier, f"{field}.identifier")
        _require_digest(digest, f"{field}[{identifier}]")


@dataclass(frozen=True)
class AssetResolutionKey:
    asset_id: str
    asset_source_digest: str
    asset_pose_digest: str
    inherited_asset_defaults_digest: str
    resolver_id: str
    resolver_version: str

    def __post_init__(self) -> None:
        _require_identifier(self.asset_id, "asset_id")
        _require_digest(self.asset_source_digest, "asset_source_digest")
        _require_digest(self.asset_pose_digest, "asset_pose_digest")
        _require_digest(
            self.inherited_asset_defaults_digest,
            "inherited_asset_defaults_digest",
        )
        _require_identifier(self.resolver_id, "resolver_id")
        _require_identifier(self.resolver_version, "resolver_version")

    @property
    def digest(self) -> str:
        return canonical_digest(asdict(self))


@dataclass(frozen=True)
class ContainerFrontierKey:
    container_group_id: str
    container_source_digest: str
    member_asset_resolution_digests: tuple[tuple[str, str], ...]
    inherited_container_defaults_digest: str
    producer_set_digest: str
    effort_profile: str

    def __post_init__(self) -> None:
        _require_identifier(self.container_group_id, "container_group_id")
        _require_digest(self.container_source_digest, "container_source_digest")
        _require_ordered_digest_pairs(
            self.member_asset_resolution_digests,
            "member_asset_resolution_digests",
        )
        _require_digest(
            self.inherited_container_defaults_digest,
            "inherited_container_defaults_digest",
        )
        _require_digest(self.producer_set_digest, "producer_set_digest")
        _require_identifier(self.effort_profile, "effort_profile")

    @property
    def digest(self) -> str:
        return canonical_digest(asdict(self))


@dataclass(frozen=True)
class ContextAnnotationKey:
    container_group_id: str
    container_frontier_digest: str
    box_context_digest: str
    top_reservation_digest: str
    annotator_id: str
    annotator_version: str

    def __post_init__(self) -> None:
        _require_identifier(self.container_group_id, "container_group_id")
        _require_digest(self.container_frontier_digest, "container_frontier_digest")
        _require_digest(self.box_context_digest, "box_context_digest")
        _require_digest(self.top_reservation_digest, "top_reservation_digest")
        _require_identifier(self.annotator_id, "annotator_id")
        _require_identifier(self.annotator_version, "annotator_version")

    @property
    def digest(self) -> str:
        return canonical_digest(asdict(self))


@dataclass(frozen=True)
class GlobalLayoutKey:
    frontier_digests: tuple[tuple[str, str], ...]
    box_context_digest: str
    top_reservation_digest: str
    solver_method: str
    solver_version: str
    effort_profile: str
    ranking_digest: str

    def __post_init__(self) -> None:
        _require_ordered_digest_pairs(self.frontier_digests, "frontier_digests")
        _require_digest(self.box_context_digest, "box_context_digest")
        _require_digest(self.top_reservation_digest, "top_reservation_digest")
        _require_identifier(self.solver_method, "solver_method")
        _require_identifier(self.solver_version, "solver_version")
        _require_identifier(self.effort_profile, "effort_profile")
        _require_digest(self.ranking_digest, "ranking_digest")

    @property
    def digest(self) -> str:
        return canonical_digest(asdict(self))


@dataclass(frozen=True)
class FinalizationKey:
    global_layout_digest: str
    finishing_policy: str
    finishing_budget_digest: str
    finalizer_id: str
    finalizer_version: str

    def __post_init__(self) -> None:
        _require_digest(self.global_layout_digest, "global_layout_digest")
        _require_identifier(self.finishing_policy, "finishing_policy")
        _require_digest(self.finishing_budget_digest, "finishing_budget_digest")
        _require_identifier(self.finalizer_id, "finalizer_id")
        _require_identifier(self.finalizer_version, "finalizer_version")

    @property
    def digest(self) -> str:
        return canonical_digest(asdict(self))


ArtifactCacheKey = (
    AssetResolutionKey
    | ContainerFrontierKey
    | ContextAnnotationKey
    | GlobalLayoutKey
    | FinalizationKey
)


@dataclass(frozen=True)
class CacheEntry:
    key_digest: str
    artifact_digest: str
    value: object


@dataclass(frozen=True)
class CacheLookup:
    status: str
    reason: str
    artifact_digest: str | None
    value: object | None


class BoundedArtifactCache:
    """Small reconstructible LRU cache whose full keys fail closed."""

    def __init__(self, max_entries: int) -> None:
        if not isinstance(max_entries, int) or isinstance(max_entries, bool) or max_entries <= 0:
            raise ValueError("max_entries must be a positive integer.")
        self.max_entries = max_entries
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def put(self, key: ArtifactCacheKey, artifact_digest: str, value: object) -> None:
        _require_digest(artifact_digest, "artifact_digest")
        key_digest = key.digest
        self._entries.pop(key_digest, None)
        self._entries[key_digest] = CacheEntry(key_digest, artifact_digest, deepcopy(value))
        while len(self._entries) > self.max_entries:
            self._entries.popitem(last=False)
            self.evictions += 1

    def lookup(self, key: ArtifactCacheKey) -> CacheLookup:
        key_digest = key.digest
        entry = self._entries.get(key_digest)
        if entry is None:
            self.misses += 1
            return CacheLookup("miss", "complete_key_not_found", None, None)
        self._entries.move_to_end(key_digest)
        self.hits += 1
        return CacheLookup("hit", "exact_key_match", entry.artifact_digest, deepcopy(entry.value))

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)

    def telemetry(self) -> dict[str, int | str]:
        return {
            "schema_version": CACHE_SCHEMA_V1,
            "max_entries": self.max_entries,
            "current_entries": len(self._entries),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
        }


@dataclass(frozen=True)
class ProjectDependencySnapshot:
    schema_version: str
    project_digest: str
    box_context_digest: str
    top_reservation_digest: str
    solver_settings_digest: str
    asset_source_digests: tuple[tuple[str, str], ...]
    asset_pose_digests: tuple[tuple[str, str], ...]
    asset_defaults_digests: tuple[tuple[str, str], ...]
    container_source_digests: tuple[tuple[str, str], ...]
    container_defaults_digests: tuple[tuple[str, str], ...]
    container_members: tuple[tuple[str, tuple[str, ...]], ...]

    def _digest_map(self, field_name: str) -> dict[str, str]:
        return dict(getattr(self, field_name))

    @property
    def asset_ids(self) -> tuple[str, ...]:
        return tuple(identifier for identifier, _ in self.asset_source_digests)

    @property
    def container_group_ids(self) -> tuple[str, ...]:
        return tuple(identifier for identifier, _ in self.container_source_digests)

    def members_for(self, container_group_id: str) -> tuple[str, ...]:
        members = dict(self.container_members)
        if container_group_id not in members:
            raise KeyError(f"Unknown container group {container_group_id!r}.")
        return members[container_group_id]

    def local_dependencies(
        self, stage: str, owner_id: str
    ) -> tuple[tuple[str, str], ...]:
        if stage == STAGE_ASSET_RESOLUTION:
            sources = self._digest_map("asset_source_digests")
            poses = self._digest_map("asset_pose_digests")
            defaults = self._digest_map("asset_defaults_digests")
            if owner_id not in sources:
                raise KeyError(f"Unknown asset {owner_id!r}.")
            return (
                ("asset_source", sources[owner_id]),
                ("asset_pose", poses[owner_id]),
                ("asset_defaults", defaults[owner_id]),
            )
        if stage == STAGE_CONTAINER_FRONTIER:
            sources = self._digest_map("container_source_digests")
            defaults = self._digest_map("container_defaults_digests")
            if owner_id not in sources:
                raise KeyError(f"Unknown container group {owner_id!r}.")
            dependencies: list[tuple[str, str]] = [
                ("container_source", sources[owner_id]),
                ("container_defaults", defaults[owner_id]),
            ]
            for asset_id in self.members_for(owner_id):
                dependencies.append(
                    (
                        f"member:{asset_id}",
                        canonical_digest(
                            dict(self.local_dependencies(STAGE_ASSET_RESOLUTION, asset_id))
                        ),
                    )
                )
            return tuple(dependencies)
        if stage == STAGE_CONTEXT_ANNOTATION:
            return (
                (
                    "container_frontier_source",
                    canonical_digest(
                        dict(self.local_dependencies(STAGE_CONTAINER_FRONTIER, owner_id))
                    ),
                ),
                ("box_context", self.box_context_digest),
                ("top_reservation", self.top_reservation_digest),
            )
        raise ValueError(f"Unsupported local stage {stage!r}.")

    def global_dependencies(self) -> tuple[tuple[str, str], ...]:
        dependencies = [
            (
                f"context:{container_group_id}",
                canonical_digest(
                    dict(
                        self.local_dependencies(
                            STAGE_CONTEXT_ANNOTATION, container_group_id
                        )
                    )
                ),
            )
            for container_group_id in self.container_group_ids
        ]
        dependencies.extend(
            (
                ("box_context", self.box_context_digest),
                ("top_reservation", self.top_reservation_digest),
                ("solver_settings", self.solver_settings_digest),
            )
        )
        return tuple(dependencies)

    def asset_resolution_key(
        self, asset_id: str, *, resolver_id: str, resolver_version: str
    ) -> AssetResolutionKey:
        dependencies = dict(self.local_dependencies(STAGE_ASSET_RESOLUTION, asset_id))
        return AssetResolutionKey(
            asset_id=asset_id,
            asset_source_digest=dependencies["asset_source"],
            asset_pose_digest=dependencies["asset_pose"],
            inherited_asset_defaults_digest=dependencies["asset_defaults"],
            resolver_id=resolver_id,
            resolver_version=resolver_version,
        )

    def container_frontier_key(
        self,
        container_group_id: str,
        *,
        asset_resolution_digests: Mapping[str, str],
        producer_set_digest: str,
        effort_profile: str,
    ) -> ContainerFrontierKey:
        members = self.members_for(container_group_id)
        supplied_ids = set(asset_resolution_digests)
        if supplied_ids != set(members):
            missing = sorted(set(members) - supplied_ids)
            extra = sorted(supplied_ids - set(members))
            raise ValueError(
                "asset_resolution_digests must match the exact member set; "
                f"missing={missing}, extra={extra}."
            )
        sources = self._digest_map("container_source_digests")
        defaults = self._digest_map("container_defaults_digests")
        return ContainerFrontierKey(
            container_group_id=container_group_id,
            container_source_digest=sources[container_group_id],
            member_asset_resolution_digests=tuple(
                (asset_id, asset_resolution_digests[asset_id]) for asset_id in members
            ),
            inherited_container_defaults_digest=defaults[container_group_id],
            producer_set_digest=producer_set_digest,
            effort_profile=effort_profile,
        )


@dataclass(frozen=True)
class InvalidationEvent:
    scope: str
    owner_id: str
    reason: str


@dataclass(frozen=True)
class InvalidationDelta:
    previous_revision: int
    source_revision: int
    invalidated_asset_ids: tuple[str, ...]
    invalidated_container_group_ids: tuple[str, ...]
    invalidated_context_group_ids: tuple[str, ...]
    global_layout_stale: bool
    finalized_plan_stale: bool
    materialized_scene_desynchronized: bool
    events: tuple[InvalidationEvent, ...]

    @property
    def changed(self) -> bool:
        return self.source_revision != self.previous_revision


@dataclass(frozen=True)
class AnalysisRequestToken:
    request_id: str
    stage: str
    owner_id: str
    source_revision: int
    dependency_digests: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ArtifactState:
    stage: str
    owner_id: str
    artifact_digest: str
    dependency_digests: tuple[tuple[str, str], ...]
    source_revision: int
    status: str


@dataclass(frozen=True)
class ResultAcceptance:
    accepted: bool
    status: str
    reason: str
    artifact: ArtifactState | None


class IncrementalProjectState:
    """Track current/stale artifacts without executing any producer."""

    def __init__(self, raw_project: object) -> None:
        self.snapshot = build_project_dependency_snapshot(raw_project)
        self.source_revision = 0
        self._request_sequence = 0
        self._active_requests: dict[str, AnalysisRequestToken] = {}
        self._artifacts: dict[tuple[str, str], ArtifactState] = {}
        self.last_invalidation = InvalidationDelta(
            0, 0, (), (), (), False, False, False, ()
        )

    def begin_local_request(self, stage: str, owner_id: str) -> AnalysisRequestToken:
        if stage not in _LOCAL_STAGES:
            raise ValueError(f"Stage {stage!r} is not a local-analysis stage.")
        dependencies = self.snapshot.local_dependencies(stage, owner_id)
        self._request_sequence += 1
        request_id = canonical_digest(
            {
                "stage": stage,
                "owner_id": owner_id,
                "source_revision": self.source_revision,
                "dependencies": dependencies,
                "sequence": self._request_sequence,
            }
        )
        token = AnalysisRequestToken(
            request_id,
            stage,
            owner_id,
            self.source_revision,
            dependencies,
        )
        self._active_requests[request_id] = token
        return token

    def accept_local_result(
        self, token: AnalysisRequestToken, artifact_digest: str
    ) -> ResultAcceptance:
        _require_digest(artifact_digest, "artifact_digest")
        active_request = self._active_requests.pop(token.request_id, None)
        if active_request is None:
            return ResultAcceptance(False, "stale_or_cancelled", "unknown_request", None)
        if active_request != token:
            return ResultAcceptance(
                False, "stale_or_cancelled", "request_identity_mismatch", None
            )
        if token.source_revision != self.source_revision:
            return ResultAcceptance(False, "stale_or_cancelled", "source_revision_changed", None)
        current_dependencies = self.snapshot.local_dependencies(token.stage, token.owner_id)
        if token.dependency_digests != current_dependencies:
            return ResultAcceptance(False, "stale_or_cancelled", "dependency_digest_changed", None)
        artifact = ArtifactState(
            token.stage,
            token.owner_id,
            artifact_digest,
            token.dependency_digests,
            token.source_revision,
            STATUS_CURRENT,
        )
        self._artifacts[(token.stage, token.owner_id)] = artifact
        return ResultAcceptance(True, STATUS_CURRENT, "exact_request_match", artifact)

    def mark_lifecycle_current(self, stage: str, artifact_digest: str) -> ArtifactState:
        if stage not in _LIFECYCLE_STAGES:
            raise ValueError(f"Stage {stage!r} is not a lifecycle stage.")
        _require_digest(artifact_digest, "artifact_digest")
        if stage == STAGE_GLOBAL_LAYOUT:
            dependencies = self.snapshot.global_dependencies()
        elif stage == STAGE_FINALIZED_PLAN:
            global_state = self.artifact(STAGE_GLOBAL_LAYOUT, "project")
            if global_state is None or global_state.status != STATUS_CURRENT:
                raise ValueError("A current global layout is required before finalization.")
            dependencies = (("global_layout", global_state.artifact_digest),)
        else:
            final_state = self.artifact(STAGE_FINALIZED_PLAN, "project")
            if final_state is None or final_state.status != STATUS_CURRENT:
                raise ValueError("A current finalized plan is required before materialization.")
            dependencies = (("finalized_plan", final_state.artifact_digest),)
        artifact = ArtifactState(
            stage,
            "project",
            artifact_digest,
            dependencies,
            self.source_revision,
            STATUS_CURRENT,
        )
        self._artifacts[(stage, "project")] = artifact
        return artifact

    def artifact(self, stage: str, owner_id: str) -> ArtifactState | None:
        return self._artifacts.get((stage, owner_id))

    @property
    def can_materialize(self) -> bool:
        artifact = self.artifact(STAGE_FINALIZED_PLAN, "project")
        return artifact is not None and artifact.status == STATUS_CURRENT

    def update_project(self, raw_project: object) -> InvalidationDelta:
        updated = build_project_dependency_snapshot(raw_project)
        if updated.project_digest == self.snapshot.project_digest:
            self.last_invalidation = InvalidationDelta(
                self.source_revision,
                self.source_revision,
                (),
                (),
                (),
                False,
                False,
                False,
                (),
            )
            return self.last_invalidation

        previous_revision = self.source_revision
        self.source_revision += 1
        delta = diff_project_dependencies(
            self.snapshot,
            updated,
            previous_revision=previous_revision,
            source_revision=self.source_revision,
        )
        self.snapshot = updated
        self._mark_invalidated_artifacts(delta)
        self.last_invalidation = delta
        return delta

    def _mark_invalidated_artifacts(self, delta: InvalidationDelta) -> None:
        stale_keys = {
            (STAGE_ASSET_RESOLUTION, asset_id)
            for asset_id in delta.invalidated_asset_ids
        }
        stale_keys.update(
            (STAGE_CONTAINER_FRONTIER, group_id)
            for group_id in delta.invalidated_container_group_ids
        )
        stale_keys.update(
            (STAGE_CONTEXT_ANNOTATION, group_id)
            for group_id in delta.invalidated_context_group_ids
        )
        if delta.global_layout_stale:
            stale_keys.add((STAGE_GLOBAL_LAYOUT, "project"))
        if delta.finalized_plan_stale:
            stale_keys.add((STAGE_FINALIZED_PLAN, "project"))
        if delta.materialized_scene_desynchronized:
            stale_keys.add((STAGE_MATERIALIZED, "project"))
        for key in stale_keys:
            artifact = self._artifacts.get(key)
            if artifact is not None:
                self._artifacts[key] = replace(artifact, status=STATUS_STALE)


def build_project_dependency_snapshot(raw_project: object) -> ProjectDependencySnapshot:
    """Normalize one project and extract only dependency-relevant identities."""

    project = normalize_project_draft(raw_project).project
    layout = dict(project["layout"])
    assets = [dict(value) for value in project["contents"]]
    groups = [dict(value) for value in project["container_groups"]]
    fill_elements = [dict(value) for value in project["fill_elements"]]
    fill_elements_by_group: dict[str, list[dict[str, object]]] = {
        str(group["id"]): [] for group in groups
    }
    unassigned_fill_elements: list[dict[str, object]] = []
    for fill_element in fill_elements:
        group_id = fill_element.get("container_group_id")
        if group_id is None:
            unassigned_fill_elements.append(fill_element)
        else:
            fill_elements_by_group[str(group_id)].append(fill_element)

    asset_sources: list[tuple[str, str]] = []
    asset_poses: list[tuple[str, str]] = []
    asset_defaults: list[tuple[str, str]] = []
    members: dict[str, list[str]] = {str(group["id"]): [] for group in groups}
    for asset in assets:
        asset_id = str(asset["id"])
        members[str(asset["container_group_id"])].append(asset_id)
        asset_sources.append((asset_id, canonical_digest(_asset_source_payload(asset))))
        asset_poses.append((asset_id, canonical_digest(_asset_pose_payload(asset))))
        asset_defaults.append((asset_id, canonical_digest(_asset_defaults_payload(asset))))

    container_sources: list[tuple[str, str]] = []
    container_defaults: list[tuple[str, str]] = []
    for group in groups:
        group_id = str(group["id"])
        container_sources.append(
            (
                group_id,
                canonical_digest(
                    {
                        "container": _container_source_payload(group),
                        "fill_elements": sorted(
                            fill_elements_by_group[group_id],
                            key=lambda value: str(value["id"]),
                        ),
                    }
                ),
            )
        )
        container_defaults.append(
            (
                group_id,
                canonical_digest(_container_defaults_payload(group, layout)),
            )
        )

    box_context = {
        "box": project["box"],
        "layout": {
            name: layout[name]
            for name in (
                "layout_clearance_mm",
                "container_z_clearance_mm",
                "container_box_xy_clearance_mm",
            )
        },
        "container_between": dict(layout["clearance_defaults_v1"])[
            "container_between_mm"
        ],
        "container_box": dict(layout["clearance_defaults_v1"])[
            "container_box_per_side_xy_mm"
        ],
        "unassigned_fill_elements": sorted(
            unassigned_fill_elements, key=lambda value: str(value["id"])
        ),
    }

    sorted_asset_sources = tuple(sorted(asset_sources))
    sorted_asset_poses = tuple(sorted(asset_poses))
    sorted_asset_defaults = tuple(sorted(asset_defaults))
    sorted_container_sources = tuple(sorted(container_sources))
    sorted_container_defaults = tuple(sorted(container_defaults))
    sorted_members = tuple(
        (group_id, tuple(sorted(asset_ids))) for group_id, asset_ids in sorted(members.items())
    )
    snapshot_payload = {
        "box_context": box_context,
        "top_reservations": project["flat_items"],
        "solver_settings": {"solver_preference": project["solver_preference"]},
        "asset_sources": sorted_asset_sources,
        "asset_poses": sorted_asset_poses,
        "asset_defaults": sorted_asset_defaults,
        "container_sources": sorted_container_sources,
        "container_defaults": sorted_container_defaults,
        "container_members": sorted_members,
    }
    return ProjectDependencySnapshot(
        schema_version=INCREMENTAL_STATE_SCHEMA_V1,
        project_digest=canonical_digest(snapshot_payload),
        box_context_digest=canonical_digest(box_context),
        top_reservation_digest=canonical_digest(project["flat_items"]),
        solver_settings_digest=canonical_digest(
            {"solver_preference": project["solver_preference"]}
        ),
        asset_source_digests=sorted_asset_sources,
        asset_pose_digests=sorted_asset_poses,
        asset_defaults_digests=sorted_asset_defaults,
        container_source_digests=sorted_container_sources,
        container_defaults_digests=sorted_container_defaults,
        container_members=sorted_members,
    )


def diff_project_dependencies(
    previous: ProjectDependencySnapshot,
    current: ProjectDependencySnapshot,
    *,
    previous_revision: int = 0,
    source_revision: int = 1,
) -> InvalidationDelta:
    """Apply the ADR-0071 invalidation matrix to two normalized snapshots."""

    previous_assets = _snapshot_asset_maps(previous)
    current_assets = _snapshot_asset_maps(current)
    previous_groups = _snapshot_container_maps(previous)
    current_groups = _snapshot_container_maps(current)
    previous_members = dict(previous.container_members)
    current_members = dict(current.container_members)

    invalid_assets: set[str] = set()
    invalid_groups: set[str] = set()
    events: list[InvalidationEvent] = []

    for asset_id in sorted(set(previous.asset_ids) | set(current.asset_ids)):
        reasons = [
            name
            for name in ("source", "pose", "defaults")
            if previous_assets[name].get(asset_id) != current_assets[name].get(asset_id)
        ]
        if reasons:
            invalid_assets.add(asset_id)
            events.append(
                InvalidationEvent(
                    STAGE_ASSET_RESOLUTION,
                    asset_id,
                    "+".join(f"asset_{reason}_changed" for reason in reasons),
                )
            )

    all_group_ids = set(previous.container_group_ids) | set(current.container_group_ids)
    for group_id in sorted(all_group_ids):
        reasons = [
            name
            for name in ("source", "defaults")
            if previous_groups[name].get(group_id) != current_groups[name].get(group_id)
        ]
        if previous_members.get(group_id) != current_members.get(group_id):
            reasons.append("members")
        previous_group_assets = set(previous_members.get(group_id, ()))
        current_group_assets = set(current_members.get(group_id, ()))
        if invalid_assets & (previous_group_assets | current_group_assets):
            reasons.append("member_resolution")
        if reasons:
            invalid_groups.add(group_id)
            events.append(
                InvalidationEvent(
                    STAGE_CONTAINER_FRONTIER,
                    group_id,
                    "+".join(f"container_{reason}_changed" for reason in reasons),
                )
            )

    box_changed = previous.box_context_digest != current.box_context_digest
    reservations_changed = (
        previous.top_reservation_digest != current.top_reservation_digest
    )
    invalid_contexts = set(invalid_groups)
    if box_changed or reservations_changed:
        invalid_contexts.update(all_group_ids)
    for group_id in sorted(invalid_contexts):
        reasons = []
        if group_id in invalid_groups:
            reasons.append("frontier")
        if box_changed:
            reasons.append("box")
        if reservations_changed:
            reasons.append("top_reservation")
        events.append(
            InvalidationEvent(
                STAGE_CONTEXT_ANNOTATION,
                group_id,
                "+".join(f"context_{reason}_changed" for reason in reasons),
            )
        )

    solver_changed = previous.solver_settings_digest != current.solver_settings_digest
    global_stale = bool(invalid_assets or invalid_groups or invalid_contexts or solver_changed)
    if global_stale:
        global_reasons = []
        if invalid_groups or invalid_contexts or invalid_assets:
            global_reasons.append("dependency")
        if solver_changed:
            global_reasons.append("solver_settings")
        events.append(
            InvalidationEvent(
                STAGE_GLOBAL_LAYOUT,
                "project",
                "+".join(f"global_{reason}_changed" for reason in global_reasons),
            )
        )
        events.append(
            InvalidationEvent(STAGE_FINALIZED_PLAN, "project", "global_layout_stale")
        )
        events.append(
            InvalidationEvent(STAGE_MATERIALIZED, "project", "finalized_plan_stale")
        )

    return InvalidationDelta(
        previous_revision=previous_revision,
        source_revision=source_revision,
        invalidated_asset_ids=tuple(sorted(invalid_assets)),
        invalidated_container_group_ids=tuple(sorted(invalid_groups)),
        invalidated_context_group_ids=tuple(sorted(invalid_contexts)),
        global_layout_stale=global_stale,
        finalized_plan_stale=global_stale,
        materialized_scene_desynchronized=global_stale,
        events=tuple(events),
    )


def _snapshot_asset_maps(
    snapshot: ProjectDependencySnapshot,
) -> dict[str, dict[str, str]]:
    return {
        "source": dict(snapshot.asset_source_digests),
        "pose": dict(snapshot.asset_pose_digests),
        "defaults": dict(snapshot.asset_defaults_digests),
    }


def _snapshot_container_maps(
    snapshot: ProjectDependencySnapshot,
) -> dict[str, dict[str, str]]:
    return {
        "source": dict(snapshot.container_source_digests),
        "defaults": dict(snapshot.container_defaults_digests),
    }


def _asset_source_payload(asset: Mapping[str, object]) -> dict[str, object]:
    excluded = {
        "id",
        "name",
        "container_group_id",
        "clearance_effective_v1",
        "storage_orientation",
        "resolved_orientation",
        "dimensions_mm",
        "base_dimensions_mm",
    }
    payload = {name: value for name, value in asset.items() if name not in excluded}
    payload["physical_dimensions_mm"] = asset.get(
        "base_dimensions_mm", asset["dimensions_mm"]
    )
    return payload


def _asset_pose_payload(asset: Mapping[str, object]) -> dict[str, object]:
    return {
        "shape_kind": asset["shape_kind"],
        "storage_orientation": asset.get("storage_orientation", "locked_xyz"),
        "resolved_orientation": asset.get("resolved_orientation", "locked_xyz"),
        "physical_dimensions_mm": asset.get(
            "base_dimensions_mm", asset["dimensions_mm"]
        ),
        "resolved_dimensions_mm": asset["dimensions_mm"],
    }


def _asset_defaults_payload(asset: Mapping[str, object]) -> dict[str, object]:
    effective = dict(asset["clearance_effective_v1"])
    values = dict(effective["values_mm"])
    sources = dict(effective["source_by_axis"])
    inherited = {
        axis: {"value_mm": values[axis], "source": sources[axis]}
        for axis in sorted(values)
        if sources[axis] not in {"object_override", "legacy_content_clearance_mm"}
    }
    return {"inherited_asset_clearance": inherited}


def _container_source_payload(group: Mapping[str, object]) -> dict[str, object]:
    return {
        name: value
        for name, value in group.items()
        if name not in {"id", "name", "clearance_effective_v1"}
    }


def _container_defaults_payload(
    group: Mapping[str, object], layout: Mapping[str, object]
) -> dict[str, object]:
    inherited: dict[str, object] = {}
    if group.get("wall_thickness_mm") is None:
        inherited["wall_thickness_mm"] = layout["default_wall_thickness_mm"]
    if group.get("floor_thickness_mm") is None:
        inherited["floor_thickness_mm"] = layout["default_floor_thickness_mm"]
    return {"inherited_container_defaults": inherited}
