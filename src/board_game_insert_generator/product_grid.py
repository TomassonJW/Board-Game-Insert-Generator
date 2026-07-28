"""Canonical product-grid conversions for derived layout geometry."""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP


PRODUCT_GRID_SCHEMA_V1 = "bgig.product_grid.v1"
PRODUCT_GRID_STEP_MM = 0.1
_TICKS_PER_MM = Decimal("10")


def nearest_ticks(value_mm: float) -> int:
    """Return the nearest 0.1 mm tick, with halves away from zero."""

    return int(
        (_decimal(value_mm) * _TICKS_PER_MM).to_integral_value(
            rounding=ROUND_HALF_UP
        )
    )


def floor_ticks(value_mm: float) -> int:
    """Return the greatest product tick not above ``value_mm``."""

    return int(
        (_decimal(value_mm) * _TICKS_PER_MM).to_integral_value(
            rounding=ROUND_FLOOR
        )
    )


def ceil_ticks(value_mm: float) -> int:
    """Return the smallest product tick not below ``value_mm``."""

    return int(
        (_decimal(value_mm) * _TICKS_PER_MM).to_integral_value(
            rounding=ROUND_CEILING
        )
    )


def ticks_to_mm(ticks: int) -> float:
    """Publish a canonical product value as millimetres."""

    return float(Decimal(int(ticks)) / _TICKS_PER_MM)


def nearest_mm(value_mm: float) -> float:
    return ticks_to_mm(nearest_ticks(value_mm))


def floor_mm(value_mm: float) -> float:
    return ticks_to_mm(floor_ticks(value_mm))


def ceil_mm(value_mm: float) -> float:
    return ticks_to_mm(ceil_ticks(value_mm))


def outward_interval_mm(
    start_mm: float,
    end_mm: float,
) -> tuple[float, float]:
    """Expand an interval to product-grid boundaries without shrinking it."""

    if end_mm < start_mm:
        raise ValueError("Product-grid interval end must not precede start.")
    return floor_mm(start_mm), ceil_mm(end_mm)


def outward_size_mm(value_mm: float) -> float:
    """Round a required positive envelope outward."""

    if value_mm < 0.0:
        raise ValueError("Product-grid envelope size must be non-negative.")
    return ceil_mm(value_mm)


def is_on_product_grid(value_mm: float) -> bool:
    """Return whether a published value is exactly representable in ticks."""

    return _decimal(value_mm) * _TICKS_PER_MM == Decimal(
        nearest_ticks(value_mm)
    )


def _decimal(value: float) -> Decimal:
    return Decimal(str(float(value)))
