from __future__ import annotations

from dataclasses import replace

from board_game_insert_generator.models import ToleranceProfile


PRINT_PROFILE_DEFAULT = "default"
PRINT_PROFILE_PLA_STANDARD = "pla_standard"
PRINT_PROFILE_PETG_STANDARD = "petg_standard"
PRINT_PROFILE_FAST_DRAFT = "fast_draft"
PRINT_PROFILE_FINE_DETAIL = "fine_detail"

PRINT_PROFILE_IDS = (
    PRINT_PROFILE_DEFAULT,
    PRINT_PROFILE_PLA_STANDARD,
    PRINT_PROFILE_PETG_STANDARD,
    PRINT_PROFILE_FAST_DRAFT,
    PRINT_PROFILE_FINE_DETAIL,
)

_PROFILE_PRESETS: dict[str, ToleranceProfile] = {
    PRINT_PROFILE_DEFAULT: ToleranceProfile(),
    PRINT_PROFILE_PLA_STANDARD: ToleranceProfile(),
    PRINT_PROFILE_PETG_STANDARD: ToleranceProfile(
        peripheral_clearance_mm=1.0,
        module_gap_mm=0.8,
        vertical_lid_clearance_mm=1.2,
        card_clearance_mm=0.6,
        sleeved_card_clearance_mm=1.1,
        token_clearance_mm=0.7,
        meeple_clearance_mm=1.1,
        sliding_lid_clearance_mm=0.45,
        hinge_clearance_mm=0.5,
        printer_compensation_mm=0.05,
    ),
    PRINT_PROFILE_FAST_DRAFT: ToleranceProfile(
        peripheral_clearance_mm=1.1,
        module_gap_mm=0.9,
        vertical_lid_clearance_mm=1.3,
        card_clearance_mm=0.7,
        sleeved_card_clearance_mm=1.2,
        token_clearance_mm=0.8,
        meeple_clearance_mm=1.2,
        sliding_lid_clearance_mm=0.5,
        hinge_clearance_mm=0.55,
        printer_compensation_mm=0.1,
        default_chamfer_mm=0.5,
    ),
    PRINT_PROFILE_FINE_DETAIL: ToleranceProfile(
        peripheral_clearance_mm=0.7,
        module_gap_mm=0.5,
        vertical_lid_clearance_mm=0.8,
        card_clearance_mm=0.4,
        sleeved_card_clearance_mm=0.8,
        token_clearance_mm=0.5,
        meeple_clearance_mm=0.8,
        sliding_lid_clearance_mm=0.3,
        hinge_clearance_mm=0.35,
        default_chamfer_mm=0.3,
    ),
}

_PROFILE_LABELS = {
    PRINT_PROFILE_DEFAULT: "Default V0 values",
    PRINT_PROFILE_PLA_STANDARD: "PLA standard starting point",
    PRINT_PROFILE_PETG_STANDARD: "PETG standard starting point",
    PRINT_PROFILE_FAST_DRAFT: "Fast draft starting point",
    PRINT_PROFILE_FINE_DETAIL: "Fine detail starting point",
}

_PROFILE_NOTE = "Preset values are experimental starting points, not physical validation."


def resolve_print_profile(
    profile_id: str,
    overrides: dict[str, float] | None = None,
) -> ToleranceProfile:
    if profile_id not in _PROFILE_PRESETS:
        allowed = ", ".join(PRINT_PROFILE_IDS)
        raise ValueError(f"Unsupported print_profile '{profile_id}'. Allowed values: {allowed}.")
    return replace(_PROFILE_PRESETS[profile_id], **(overrides or {}))


def print_profile_label(profile_id: str) -> str:
    return _PROFILE_LABELS.get(profile_id, profile_id)


def print_profile_note(profile_id: str) -> str:
    return _PROFILE_NOTE