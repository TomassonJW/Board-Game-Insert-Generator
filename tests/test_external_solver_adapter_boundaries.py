from __future__ import annotations

from copy import deepcopy
import unittest

from board_game_insert_generator.external_solver_adapters import (
    STATUS_UNSUPPORTED,
    build_external_adapter_exact_controls,
    prepare_external_floor_case,
)
from board_game_insert_generator.incremental_project_state import canonical_digest
from board_game_insert_generator.project_v1 import normalize_project_draft


class ExternalSolverAdapterBoundaryTests(unittest.TestCase):
    def test_fixed_expansion_is_unsupported_in_minimal_layout_adapter(self) -> None:
        case = deepcopy(build_external_adapter_exact_controls()["cases"][0])
        project = case["project"]
        group = project["container_groups"][0]
        group["dimension_modes"]["x"] = "fixed"
        group["locked_outer_dimensions_mm"]["x"] = 41.0
        project = normalize_project_draft(project).project
        case["project"] = project
        case["project_digest"] = canonical_digest(project)

        preparation = prepare_external_floor_case(case)

        self.assertEqual(preparation.status, STATUS_UNSUPPORTED)
        self.assertEqual(
            preparation.reasons,
            ("fixed_expanded_envelope_not_supported_by_minimal_certificate",),
        )


if __name__ == "__main__":
    unittest.main()
