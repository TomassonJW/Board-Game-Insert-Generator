from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import unittest

from board_game_insert_generator.container_derivation import derive_container_plan
from board_game_insert_generator.container_internal_variants import (
    EFFORT_DEEP,
    EFFORT_NORMAL,
    EFFORT_QUICK,
    certify_container_variant_draft,
    compute_variant_geometry_digest,
    container_internal_variant_to_dict,
    derive_container_internal_variant_frontiers,
    internal_variant_run_to_dict,
    standard_variant_budgets,
)
from board_game_insert_generator.project_v1 import normalize_project_draft
from p64_h04_fixture_cases import (
    h01_dense_project,
    h02_reservations_project,
    h03_contextual_unresolved_project,
    p64_v2_continuous_closure_project,
    simple_success_project,
)
from p64_v2h03b_fixture_cases import (
    dense_11_containers_34_contents_project,
    localized_reservation_project,
    multi_cavity_tradeoff_project,
    project_with_dimension_mode,
    with_asset_clearance_override,
    with_external_container_override,
)


class ContainerInternalVariantTests(unittest.TestCase):
    def test_standard_budgets_are_finite_monotone_and_serializable(self) -> None:
        quick, normal, deep = standard_variant_budgets()

        self.assertEqual(
            (quick.effort_profile, normal.effort_profile, deep.effort_profile),
            (EFFORT_QUICK, EFFORT_NORMAL, EFFORT_DEEP),
        )
        self.assertEqual(
            tuple(tuple(value for _, value in budget.limit_items()) for budget in (quick, normal, deep)),
            (
                (24, 24, 4, 2, 32, 128),
                (48, 48, 8, 4, 384, 3_072),
                (96, 96, 12, 6, 3_072, 36_864),
            ),
        )
        self.assertTrue(normal.is_at_least_as_permissive_as(quick))
        self.assertTrue(deep.is_at_least_as_permissive_as(normal))
        self.assertFalse(quick.is_at_least_as_permissive_as(normal))
        for budget in (quick, normal, deep):
            self.assertTrue(all(value >= 0 for _, value in budget.limit_items()))
            json.dumps(budget.to_dict(), sort_keys=True)

    def test_canonical_extraction_keeps_public_derivation_bit_identical(self) -> None:
        projects = (
            simple_success_project(),
            h01_dense_project(),
            h02_reservations_project(),
            h03_contextual_unresolved_project(),
            p64_v2_continuous_closure_project(),
        )
        for project in projects:
            with self.subTest(project=project["project_name"]):
                original = deepcopy(project)
                before = derive_container_plan(project)

                run = derive_container_internal_variant_frontiers(
                    project, effort_profile=EFFORT_QUICK
                )
                after = derive_container_plan(project)

                self.assertEqual(project, original)
                self.assertEqual(after, before)
                frontiers = {value.container_group_id: value for value in run.frontiers}
                for container in before["containers"]:
                    if container["outer_dimensions_mm"] is None:
                        continue
                    canonical = next(
                        value for value in frontiers[container["container_group_id"]].variants
                        if value.canonical
                    )
                    payload = container_internal_variant_to_dict(canonical)
                    self.assertEqual(
                        payload["minimum_outer_envelope_mm"],
                        container["outer_dimensions_mm"],
                    )
                    public_cavities = {
                        value["id"]: value for value in container["compartments"]
                    }
                    for cavity in payload["cavity_layout"]:
                        public = public_cavities[cavity["cavity_id"]]
                        self.assertEqual(cavity["local_origin_mm"], public["local_origin_mm"])
                        self.assertEqual(
                            cavity["inner_dimensions_mm"], public["inner_dimensions_mm"]
                        )
                    self.assertEqual(payload["producer_id"], "canonical_v1")
                    self.assertTrue(payload["local_certificate"]["certified"])

    def test_generation_is_deterministic_and_merges_duplicate_provenance(self) -> None:
        project = multi_cavity_tradeoff_project()

        first = derive_container_internal_variant_frontiers(project, effort_profile=EFFORT_DEEP)
        second = derive_container_internal_variant_frontiers(project, effort_profile=EFFORT_DEEP)

        first_frontier = first.frontiers[0]
        second_frontier = second.frontiers[0]
        self.assertEqual(
            [value.geometry_digest for value in first_frontier.variants],
            [value.geometry_digest for value in second_frontier.variants],
        )
        self.assertGreater(first_frontier.duplicate_count, 0)
        self.assertTrue(any(len(value.provenance) > 1 for value in first_frontier.variants))
        json.dumps(internal_variant_run_to_dict(first), sort_keys=True)

    def test_local_certificate_fails_closed_for_bounds_and_digest_tampering(self) -> None:
        project = multi_cavity_tradeoff_project()
        normalized = normalize_project_draft(project).project
        container = derive_container_plan(project)["containers"][0]
        group = normalized["container_groups"][0]
        canonical = derive_container_internal_variant_frontiers(project).frontiers[0].variants[0]

        outer = canonical.draft.minimum_outer_envelope_mm
        undersized = replace(
            canonical.draft,
            minimum_outer_envelope_mm=(outer[0] - 1.0, outer[1], outer[2]),
        )
        undersized = replace(
            undersized,
            geometry_digest=compute_variant_geometry_digest(undersized),
        )
        rejected_bounds = certify_container_variant_draft(undersized, container, group)
        rejected_digest = certify_container_variant_draft(
            replace(canonical.draft, geometry_digest="0" * 64),
            container,
            group,
        )

        self.assertFalse(rejected_bounds.local_certificate.certified)
        self.assertIn(
            "LOCAL_CAVITY_OUT_OF_BOUNDS",
            rejected_bounds.local_certificate.rejection_codes,
        )
        self.assertFalse(rejected_digest.local_certificate.certified)
        self.assertIn(
            "LOCAL_GEOMETRY_DIGEST_MISMATCH",
            rejected_digest.local_certificate.rejection_codes,
        )

    def test_fixed_axis_rejects_oversized_variants_but_target_and_auto_do_not(self) -> None:
        fixed = derive_container_internal_variant_frontiers(
            project_with_dimension_mode("fixed"), effort_profile=EFFORT_DEEP
        ).frontiers[0]
        target = derive_container_internal_variant_frontiers(
            project_with_dimension_mode("target"), effort_profile=EFFORT_DEEP
        ).frontiers[0]
        auto = derive_container_internal_variant_frontiers(
            project_with_dimension_mode("auto"), effort_profile=EFFORT_DEEP
        ).frontiers[0]

        self.assertTrue(
            any("LOCAL_FIXED_AXIS_EXCEEDED" in value.rejection_codes for value in fixed.rejected)
        )
        self.assertFalse(
            any("LOCAL_FIXED_AXIS_EXCEEDED" in value.rejection_codes for value in target.rejected)
        )
        self.assertFalse(
            any("LOCAL_FIXED_AXIS_EXCEEDED" in value.rejection_codes for value in auto.rejected)
        )
        self.assertLess(fixed.certified_count, auto.certified_count)

    def test_localized_reservations_do_not_change_the_local_frontier(self) -> None:
        without_reservation = derive_container_internal_variant_frontiers(
            multi_cavity_tradeoff_project(), effort_profile=EFFORT_DEEP
        ).frontiers[0]
        with_reservation = derive_container_internal_variant_frontiers(
            localized_reservation_project(), effort_profile=EFFORT_DEEP
        ).frontiers[0]

        self.assertEqual(
            without_reservation.certified_digests,
            with_reservation.certified_digests,
        )
        self.assertEqual(
            [value.geometry_digest for value in without_reservation.variants],
            [value.geometry_digest for value in with_reservation.variants],
        )

    def test_asset_clearance_is_certified_but_external_container_overrides_are_not_local(self) -> None:
        base_project = multi_cavity_tradeoff_project()
        base = derive_container_internal_variant_frontiers(
            base_project, effort_profile=EFFORT_NORMAL
        ).frontiers[0]
        external = derive_container_internal_variant_frontiers(
            with_external_container_override(base_project), effort_profile=EFFORT_NORMAL
        ).frontiers[0]
        asset = derive_container_internal_variant_frontiers(
            with_asset_clearance_override(base_project), effort_profile=EFFORT_NORMAL
        ).frontiers[0]

        self.assertEqual(base.certified_digests, external.certified_digests)
        self.assertNotEqual(base.certified_digests, asset.certified_digests)
        canonical = asset.variants[0]
        changed = next(value for value in canonical.draft.cavities if value.content_id == "long")
        self.assertEqual(changed.clearance_values_mm, (1.0, 0.5, 0.25))
        self.assertTrue(
            all(
                next(
                    cavity
                    for cavity in variant.draft.cavities
                    if cavity.content_id == "long"
                ).clearance_values_mm
                == changed.clearance_values_mm
                for variant in asset.variants
            )
        )

    def test_multi_cavity_fixture_exposes_certified_xy_tradeoffs(self) -> None:
        frontier = derive_container_internal_variant_frontiers(
            multi_cavity_tradeoff_project(), effort_profile=EFFORT_DEEP
        ).frontiers[0]

        self.assertGreaterEqual(len(frontier.variants), 2)
        self.assertTrue(all(value.local_certificate.certified for value in frontier.variants))
        envelopes = [value.draft.minimum_outer_envelope_mm for value in frontier.variants]
        self.assertTrue(
            any(
                left[0] < right[0] and left[1] > right[1]
                for left in envelopes
                for right in envelopes
            )
        )

    def test_global_rotation_is_not_part_of_local_variant_identity(self) -> None:
        variant = derive_container_internal_variant_frontiers(
            multi_cavity_tradeoff_project(), effort_profile=EFFORT_QUICK
        ).frontiers[0].variants[0]
        payload = container_internal_variant_to_dict(variant)

        self.assertNotIn("rotation_deg_z", payload)
        self.assertNotIn("rotation_deg_z", payload["cavity_layout"][0])
        self.assertEqual(
            compute_variant_geometry_digest(variant.draft),
            variant.geometry_digest,
        )

    def test_dense_11_by_34_fixture_is_bounded_and_profile_prefixes_are_monotone(self) -> None:
        project = dense_11_containers_34_contents_project()
        runs = {
            profile: derive_container_internal_variant_frontiers(
                project, effort_profile=profile
            )
            for profile in (EFFORT_QUICK, EFFORT_NORMAL, EFFORT_DEEP)
        }

        self.assertEqual(len(project["container_groups"]), 11)
        self.assertEqual(len(project["contents"]), 34)
        self.assertTrue(all(len(run.frontiers) == 11 for run in runs.values()))
        by_profile = {
            profile: {value.container_group_id: value for value in run.frontiers}
            for profile, run in runs.items()
        }
        for group_id in by_profile[EFFORT_QUICK]:
            quick = by_profile[EFFORT_QUICK][group_id]
            normal = by_profile[EFFORT_NORMAL][group_id]
            deep = by_profile[EFFORT_DEEP][group_id]
            self.assertLessEqual(quick.generated_count, quick.budget.max_generated_variants_per_container)
            self.assertLessEqual(normal.generated_count, normal.budget.max_generated_variants_per_container)
            self.assertLessEqual(deep.generated_count, deep.budget.max_generated_variants_per_container)
            self.assertTrue(set(quick.certified_digests).issubset(normal.certified_digests))
            self.assertTrue(set(normal.certified_digests).issubset(deep.certified_digests))
            self.assertTrue(
                all(
                    variant.draft.automatic_body_count == 0
                    for variant in deep.variants
                )
            )
        self.assertTrue(
            by_profile[EFFORT_DEEP]["dense-core"].generation_limit_reached
        )


if __name__ == "__main__":
    unittest.main()
