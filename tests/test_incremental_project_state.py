from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import unittest

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.incremental_project_state import (
    STATUS_CURRENT,
    STATUS_STALE,
    STAGE_ASSET_RESOLUTION,
    STAGE_CONTAINER_FRONTIER,
    STAGE_CONTEXT_ANNOTATION,
    STAGE_FINALIZED_PLAN,
    STAGE_GLOBAL_LAYOUT,
    STAGE_MATERIALIZED,
    AssetResolutionKey,
    BoundedArtifactCache,
    ContextAnnotationKey,
    IncrementalProjectState,
    build_project_dependency_snapshot,
    canonical_digest,
)
from board_game_insert_generator.project_v1 import blank_project_v1


def _artifact(label: str) -> str:
    return canonical_digest({"artifact": label})


def _project() -> dict[str, object]:
    project = blank_project_v1()
    project["project_name"] = "P64-L01 fixture"
    project["container_groups"] = [
        {
            "id": "g1",
            "name": "Groupe 1",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        },
        {
            "id": "g2",
            "name": "Groupe 2",
            "wall_thickness_mm": None,
            "floor_thickness_mm": None,
        },
    ]
    project["contents"] = [
        {
            "id": "a1",
            "name": "Asset hérité",
            "shape_kind": "rectangle",
            "dimensions_mm": {"x": 20.0, "y": 10.0, "z": 5.0},
            "quantity": 4,
            "container_group_id": "g1",
            "content_clearance_mm": None,
            "measurement_confidence": "exact",
        },
        {
            "id": "a2",
            "name": "Asset explicite",
            "shape_kind": "square",
            "dimensions_mm": {"x": 12.0, "y": 12.0, "z": 4.0},
            "quantity": 3,
            "container_group_id": "g2",
            "content_clearance_mm": 0.4,
            "measurement_confidence": "exact",
        },
    ]
    return project


def _record_local_artifacts(state: IncrementalProjectState) -> None:
    for asset_id in ("a1", "a2"):
        token = state.begin_local_request(STAGE_ASSET_RESOLUTION, asset_id)
        accepted = state.accept_local_result(token, _artifact(f"asset:{asset_id}"))
        assert accepted.accepted
    for group_id in ("g1", "g2"):
        token = state.begin_local_request(STAGE_CONTAINER_FRONTIER, group_id)
        accepted = state.accept_local_result(token, _artifact(f"frontier:{group_id}"))
        assert accepted.accepted
        token = state.begin_local_request(STAGE_CONTEXT_ANNOTATION, group_id)
        accepted = state.accept_local_result(token, _artifact(f"context:{group_id}"))
        assert accepted.accepted


class IncrementalProjectStateTests(unittest.TestCase):
    def test_snapshot_is_deterministic_and_preserves_derivation_parity(self) -> None:
        project = _project()
        original = deepcopy(project)
        before = derive_container_plan(project)

        first = build_project_dependency_snapshot(project)
        second = build_project_dependency_snapshot(deepcopy(project))
        IncrementalProjectState(project)
        after = derive_container_plan(project)

        self.assertEqual(first, second)
        self.assertEqual(before, after)
        self.assertEqual(project, original)

    def test_complete_versioned_keys_and_cache_fail_closed(self) -> None:
        snapshot = build_project_dependency_snapshot(_project())
        key_v1 = snapshot.asset_resolution_key(
            "a1", resolver_id="asset_resolver", resolver_version="1"
        )
        key_v2 = replace(key_v1, resolver_version="2")
        cache = BoundedArtifactCache(max_entries=2)
        cached_value = {"resolved": {"count": 1}}
        cache.put(key_v1, _artifact("a1-v1"), cached_value)
        cached_value["resolved"]["count"] = 99

        hit = cache.lookup(key_v1)
        hit.value["resolved"]["count"] = 42
        second_hit = cache.lookup(key_v1)
        miss = cache.lookup(key_v2)

        self.assertEqual(hit.status, "hit")
        self.assertEqual(second_hit.value["resolved"]["count"], 1)
        self.assertEqual(hit.reason, "exact_key_match")
        self.assertEqual(miss.status, "miss")
        self.assertEqual(miss.reason, "complete_key_not_found")
        self.assertNotEqual(key_v1.digest, key_v2.digest)
        with self.assertRaisesRegex(ValueError, "complete lowercase SHA-256"):
            AssetResolutionKey(
                asset_id="a1",
                asset_source_digest="partial",
                asset_pose_digest=key_v1.asset_pose_digest,
                inherited_asset_defaults_digest=key_v1.inherited_asset_defaults_digest,
                resolver_id="asset_resolver",
                resolver_version="1",
            )

    def test_container_key_requires_exact_member_resolution_set(self) -> None:
        snapshot = build_project_dependency_snapshot(_project())
        with self.assertRaisesRegex(ValueError, "exact member set"):
            snapshot.container_frontier_key(
                "g1",
                asset_resolution_digests={},
                producer_set_digest=_artifact("producers"),
                effort_profile="quick",
            )

        key = snapshot.container_frontier_key(
            "g1",
            asset_resolution_digests={"a1": _artifact("resolved:a1")},
            producer_set_digest=_artifact("producers"),
            effort_profile="quick",
        )
        context = ContextAnnotationKey(
            container_group_id="g1",
            container_frontier_digest=_artifact("frontier:g1"),
            box_context_digest=snapshot.box_context_digest,
            top_reservation_digest=snapshot.top_reservation_digest,
            annotator_id="box_context",
            annotator_version="1",
        )
        self.assertEqual(key.member_asset_resolution_digests[0][0], "a1")
        self.assertEqual(len(context.digest), 64)

    def test_cache_capacity_is_observable_and_evicts_only_performance_state(self) -> None:
        snapshot = build_project_dependency_snapshot(_project())
        key_a1 = snapshot.asset_resolution_key(
            "a1", resolver_id="resolver", resolver_version="1"
        )
        key_a2 = snapshot.asset_resolution_key(
            "a2", resolver_id="resolver", resolver_version="1"
        )
        key_a1_v2 = replace(key_a1, resolver_version="2")
        cache = BoundedArtifactCache(max_entries=2)

        cache.put(key_a1, _artifact("a1"), "a1")
        cache.put(key_a2, _artifact("a2"), "a2")
        self.assertEqual(cache.lookup(key_a1).status, "hit")
        cache.put(key_a1_v2, _artifact("a1-v2"), "a1-v2")

        self.assertEqual(len(cache), 2)
        self.assertEqual(cache.lookup(key_a2).status, "miss")
        self.assertEqual(cache.telemetry()["evictions"], 1)

    def test_asset_change_invalidates_only_its_local_chain_and_lifecycle(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        _record_local_artifacts(state)
        state.mark_lifecycle_current(STAGE_GLOBAL_LAYOUT, _artifact("global"))
        state.mark_lifecycle_current(STAGE_FINALIZED_PLAN, _artifact("final"))
        materialized = state.mark_lifecycle_current(
            STAGE_MATERIALIZED, _artifact("scene")
        )
        changed = deepcopy(project)
        changed["contents"][0]["quantity"] = 5

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ("a1",))
        self.assertEqual(delta.invalidated_container_group_ids, ("g1",))
        self.assertEqual(delta.invalidated_context_group_ids, ("g1",))
        self.assertTrue(delta.global_layout_stale)
        self.assertEqual(state.artifact(STAGE_ASSET_RESOLUTION, "a1").status, STATUS_STALE)
        self.assertEqual(state.artifact(STAGE_ASSET_RESOLUTION, "a2").status, STATUS_CURRENT)
        self.assertEqual(state.artifact(STAGE_CONTAINER_FRONTIER, "g1").status, STATUS_STALE)
        self.assertEqual(state.artifact(STAGE_CONTAINER_FRONTIER, "g2").status, STATUS_CURRENT)
        self.assertEqual(state.artifact(STAGE_GLOBAL_LAYOUT, "project").status, STATUS_STALE)
        self.assertEqual(state.artifact(STAGE_FINALIZED_PLAN, "project").status, STATUS_STALE)
        self.assertEqual(state.artifact(STAGE_MATERIALIZED, "project").status, STATUS_STALE)
        self.assertEqual(
            state.artifact(STAGE_MATERIALIZED, "project").artifact_digest,
            materialized.artifact_digest,
        )
        self.assertFalse(state.can_materialize)

    def test_container_change_preserves_asset_resolutions(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        _record_local_artifacts(state)
        changed = deepcopy(project)
        changed["container_groups"][0]["wall_thickness_mm"] = 1.8

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ("g1",))
        self.assertEqual(state.artifact(STAGE_ASSET_RESOLUTION, "a1").status, STATUS_CURRENT)
        self.assertEqual(state.artifact(STAGE_ASSET_RESOLUTION, "a2").status, STATUS_CURRENT)

    def test_moving_asset_invalidates_exactly_old_and_new_frontiers(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        moved = deepcopy(project)
        moved["contents"][0]["container_group_id"] = "g2"

        delta = state.update_project(moved)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ("g1", "g2"))
        self.assertEqual(delta.invalidated_context_group_ids, ("g1", "g2"))

    def test_box_change_reuses_intrinsic_geometries_and_refreshes_contexts(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["box"]["inner_dimensions_mm"]["x"] = 210.0

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ())
        self.assertEqual(delta.invalidated_context_group_ids, ("g1", "g2"))
        self.assertTrue(delta.global_layout_stale)

    def test_asset_default_change_only_invalidates_inheritors(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["layout"]["default_content_clearance_mm"] = 0.9

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ("a1",))
        self.assertEqual(delta.invalidated_container_group_ids, ("g1",))

    def test_local_override_does_not_invalidate_neighbor(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["container_groups"][0]["floor_thickness_mm"] = 2.0

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ("g1",))
        self.assertNotIn("g2", delta.invalidated_context_group_ids)

    def test_group_fill_element_invalidates_only_its_container(self) -> None:
        project = _project()
        project["fill_elements"] = [
            {
                "id": "fill-g1",
                "name": "Volume local",
                "kind": "hollow",
                "mode": "exact",
                "dimensions_mm": {"x": 15.0, "y": 10.0, "z": 5.0},
                "container_group_id": "g1",
            }
        ]
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["fill_elements"][0]["dimensions_mm"]["x"] = 16.0

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ("g1",))
        self.assertEqual(delta.invalidated_context_group_ids, ("g1",))

    def test_container_default_change_only_invalidates_inheriting_groups(self) -> None:
        project = _project()
        project["container_groups"][1]["wall_thickness_mm"] = 1.5
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["layout"]["default_wall_thickness_mm"] = 1.7

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ("g1",))
        self.assertEqual(delta.invalidated_context_group_ids, ("g1",))

    def test_late_local_response_is_rejected_after_new_source_revision(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        token = state.begin_local_request(STAGE_ASSET_RESOLUTION, "a1")
        changed = deepcopy(project)
        changed["contents"][0]["dimensions_mm"]["x"] = 21.0
        state.update_project(changed)

        acceptance = state.accept_local_result(token, _artifact("late-a1"))

        self.assertFalse(acceptance.accepted)
        self.assertEqual(acceptance.status, "stale_or_cancelled")
        self.assertEqual(acceptance.reason, "source_revision_changed")
        self.assertIsNone(state.artifact(STAGE_ASSET_RESOLUTION, "a1"))

    def test_request_identity_is_single_use_and_cannot_be_forged(self) -> None:
        state = IncrementalProjectState(_project())
        token = state.begin_local_request(STAGE_ASSET_RESOLUTION, "a1")
        forged = replace(token, owner_id="a2")

        rejected = state.accept_local_result(forged, _artifact("forged"))
        replayed = state.accept_local_result(token, _artifact("replayed"))

        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.reason, "request_identity_mismatch")
        self.assertFalse(replayed.accepted)
        self.assertEqual(replayed.reason, "unknown_request")

    def test_solver_setting_change_invalidates_only_global_stages(self) -> None:
        project = _project()
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["solver_preference"] = "compact"

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ())
        self.assertEqual(delta.invalidated_container_group_ids, ())
        self.assertEqual(delta.invalidated_context_group_ids, ())
        self.assertTrue(delta.global_layout_stale)

    def test_fifty_container_fixture_keeps_invalidation_cardinality_bounded(self) -> None:
        project = blank_project_v1()
        project["container_groups"] = [
            {
                "id": f"g{index:02d}",
                "name": f"Groupe {index}",
                "wall_thickness_mm": None,
                "floor_thickness_mm": None,
            }
            for index in range(50)
        ]
        project["contents"] = [
            {
                "id": f"a{index:02d}",
                "name": f"Asset {index}",
                "shape_kind": "rectangle",
                "dimensions_mm": {"x": 8.0, "y": 8.0, "z": 4.0},
                "quantity": 2,
                "container_group_id": f"g{index:02d}",
                "content_clearance_mm": None,
                "measurement_confidence": "exact",
            }
            for index in range(50)
        ]
        state = IncrementalProjectState(project)
        changed = deepcopy(project)
        changed["contents"][23]["quantity"] = 3

        delta = state.update_project(changed)

        self.assertEqual(delta.invalidated_asset_ids, ("a23",))
        self.assertEqual(delta.invalidated_container_group_ids, ("g23",))
        self.assertEqual(delta.invalidated_context_group_ids, ("g23",))


if __name__ == "__main__":
    unittest.main()
