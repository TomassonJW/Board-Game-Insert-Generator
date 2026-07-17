"""Stable P64-H08 product settings for the bounded solver portfolio.

The settings describe how much search to run and which family is eligible.
They deliberately stay separate from physical project dimensions, tolerances and
the public project schema: the Fusion palette persists them as local document
preferences.
"""

from __future__ import annotations

from typing import Mapping


SOLVER_METHOD_AUTO = "auto"
SOLVER_METHOD_STAGE_STACK = "stage_stack"
SOLVER_METHOD_FREE_3D = "free_3d"
SOLVER_METHODS = frozenset(
    {SOLVER_METHOD_AUTO, SOLVER_METHOD_STAGE_STACK, SOLVER_METHOD_FREE_3D}
)

EFFORT_QUICK = "quick"
EFFORT_NORMAL = "normal"
EFFORT_DEEP = "deep"
EFFORT_PROFILES = frozenset({EFFORT_QUICK, EFFORT_NORMAL, EFFORT_DEEP})

DEFAULT_SOLVER_SETTINGS = {
    "method": SOLVER_METHOD_AUTO,
    "effort": EFFORT_NORMAL,
}


def normalize_solver_settings(value: object) -> dict[str, str]:
    """Return the safe local product defaults for one untrusted settings object."""

    raw = value if isinstance(value, Mapping) else {}
    method = raw.get("method")
    effort = raw.get("effort")
    return {
        "method": method if isinstance(method, str) and method in SOLVER_METHODS else SOLVER_METHOD_AUTO,
        "effort": effort if isinstance(effort, str) and effort in EFFORT_PROFILES else EFFORT_NORMAL,
    }


def solver_method_label(method: str) -> str:
    """Return the short French product label without making Fusion the authority."""

    return {
        SOLVER_METHOD_AUTO: "Auto intelligent",
        SOLVER_METHOD_STAGE_STACK: "Étages et piles",
        SOLVER_METHOD_FREE_3D: "Placement 3D libre",
    }.get(method, "Auto intelligent")
