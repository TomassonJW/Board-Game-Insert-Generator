"""Volumetric grid helpers for the pure Python engine.

P8-M001 deliberately does not solve placement. It validates and reports an
explicit X/Y/Z grid declared by configuration so later missions can build a real
volumetric planner without putting business logic in Fusion 360.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from board_game_insert_generator.models import (
    GridPoint3D,
    GridSize3D,
    InsertConfig,
    VolumetricGrid,
    VolumetricModulePlacement,
    VolumetricZone,
)


CELL_FREE = "free"
CELL_OCCUPIED = "occupied"
CELL_RESERVED = "reserved"
CELL_FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class VolumetricCellRecord:
    coordinate: GridPoint3D
    state: str
    owner_id: str | None = None
    owner_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "coordinate_units": _grid_point_to_dict(self.coordinate),
            "state": self.state,
            "owner_id": self.owner_id,
            "owner_type": self.owner_type,
        }


@dataclass(frozen=True)
class VolumetricSummary:
    grid: VolumetricGrid
    cells: tuple[VolumetricCellRecord, ...]

    @property
    def total_cell_count(self) -> int:
        return len(self.cells)

    @property
    def occupied_cell_count(self) -> int:
        return _count_state(self.cells, CELL_OCCUPIED)

    @property
    def reserved_cell_count(self) -> int:
        return _count_state(self.cells, CELL_RESERVED)

    @property
    def forbidden_cell_count(self) -> int:
        return _count_state(self.cells, CELL_FORBIDDEN)

    @property
    def free_cell_count(self) -> int:
        return _count_state(self.cells, CELL_FREE)

    @property
    def cell_volume_mm3(self) -> float:
        unit = self.grid.unit_size_mm
        return unit.x * unit.y * unit.z

    @property
    def approximate_free_volume_mm3(self) -> float:
        return self.free_cell_count * self.cell_volume_mm3

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_mm": {
                "x": self.grid.unit_size_mm.x,
                "y": self.grid.unit_size_mm.y,
                "z": self.grid.unit_size_mm.z,
            },
            "size_units": _grid_size_to_dict(self.grid.size_units),
            "coverage_mm": {
                "x": self.grid.unit_size_mm.x * self.grid.size_units.x,
                "y": self.grid.unit_size_mm.y * self.grid.size_units.y,
                "z": self.grid.unit_size_mm.z * self.grid.size_units.z,
            },
            "total_cell_count": self.total_cell_count,
            "occupied_cell_count": self.occupied_cell_count,
            "reserved_cell_count": self.reserved_cell_count,
            "forbidden_cell_count": self.forbidden_cell_count,
            "free_cell_count": self.free_cell_count,
            "cell_volume_mm3": self.cell_volume_mm3,
            "approximate_free_volume_mm3": self.approximate_free_volume_mm3,
            "layers": [_layer_to_dict(layer) for layer in self.grid.layers],
            "module_placements": [
                _placement_to_dict(placement, self.grid.unit_size_mm)
                for placement in self.grid.module_placements
            ],
            "zones": [_zone_to_dict(zone, self.grid.unit_size_mm) for zone in self.grid.zones],
            "support_surfaces": [
                _support_surface_to_dict(surface, self.grid.unit_size_mm)
                for surface in self.grid.support_surfaces
            ],
            "removal_sequence": _removal_sequence_to_dict(self.grid),
            "cells": [cell.to_dict() for cell in self.cells],
            "comment": self.grid.comment,
        }


def build_volumetric_summary(config: InsertConfig) -> VolumetricSummary | None:
    if config.volumetric_grid is None:
        return None

    grid = config.volumetric_grid
    occupied: dict[tuple[int, int, int], VolumetricCellRecord] = {}

    for placement in grid.module_placements:
        for coordinate in _unit_cells(placement.origin_units, placement.size_units):
            occupied[_coord_key(coordinate)] = VolumetricCellRecord(
                coordinate=coordinate,
                state=CELL_OCCUPIED,
                owner_id=placement.id,
                owner_type="module_placement",
            )

    for zone in grid.zones:
        state = CELL_RESERVED if zone.kind.value == CELL_RESERVED else CELL_FORBIDDEN
        for coordinate in _unit_cells(zone.origin_units, zone.size_units):
            occupied[_coord_key(coordinate)] = VolumetricCellRecord(
                coordinate=coordinate,
                state=state,
                owner_id=zone.id,
                owner_type="zone",
            )

    cells: list[VolumetricCellRecord] = []
    for z in range(grid.size_units.z):
        for y in range(grid.size_units.y):
            for x in range(grid.size_units.x):
                key = (x, y, z)
                cells.append(
                    occupied.get(
                        key,
                        VolumetricCellRecord(
                            coordinate=GridPoint3D(x=x, y=y, z=z),
                            state=CELL_FREE,
                        ),
                    )
                )

    return VolumetricSummary(grid=grid, cells=tuple(cells))


def span_cells(origin: GridPoint3D, size: GridSize3D) -> set[tuple[int, int, int]]:
    return {_coord_key(coordinate) for coordinate in _unit_cells(origin, size)}


def span_fits_grid(origin: GridPoint3D, size: GridSize3D, grid_size: GridSize3D) -> bool:
    return (
        origin.x >= 0
        and origin.y >= 0
        and origin.z >= 0
        and size.x > 0
        and size.y > 0
        and size.z > 0
        and origin.x + size.x <= grid_size.x
        and origin.y + size.y <= grid_size.y
        and origin.z + size.z <= grid_size.z
    )


def _unit_cells(origin: GridPoint3D, size: GridSize3D) -> Iterable[GridPoint3D]:
    for z in range(origin.z, origin.z + size.z):
        for y in range(origin.y, origin.y + size.y):
            for x in range(origin.x, origin.x + size.x):
                yield GridPoint3D(x=x, y=y, z=z)


def _coord_key(point: GridPoint3D) -> tuple[int, int, int]:
    return point.x, point.y, point.z


def _count_state(cells: tuple[VolumetricCellRecord, ...], state: str) -> int:
    return sum(1 for cell in cells if cell.state == state)


def _grid_point_to_dict(point: GridPoint3D) -> dict[str, int]:
    return {"x": point.x, "y": point.y, "z": point.z}


def _grid_size_to_dict(size: GridSize3D) -> dict[str, int]:
    return {"x": size.x, "y": size.y, "z": size.z}


def _layer_to_dict(layer) -> dict[str, Any]:
    return {
        "id": layer.id,
        "name": layer.name,
        "z_start": layer.z_start,
        "z_count": layer.z_count,
        "role": layer.role,
        "comment": layer.comment,
    }


def _placement_to_dict(placement: VolumetricModulePlacement, unit_size) -> dict[str, Any]:
    return {
        "id": placement.id,
        "module_id": placement.module_id,
        "instance_id": placement.instance_id,
        "origin_units": _grid_point_to_dict(placement.origin_units),
        "size_units": _grid_size_to_dict(placement.size_units),
        "origin_mm": _grid_origin_to_mm(placement.origin_units, unit_size),
        "size_mm": _grid_size_to_mm(placement.size_units, unit_size),
        "layer_id": placement.layer_id,
        "removal_order": placement.removal_order,
        "access_direction": placement.access_direction,
        "support_surface_id": placement.support_surface_id,
        "comment": placement.comment,
    }


def _zone_to_dict(zone: VolumetricZone, unit_size) -> dict[str, Any]:
    return {
        "id": zone.id,
        "kind": zone.kind.value,
        "purpose": zone.purpose,
        "origin_units": _grid_point_to_dict(zone.origin_units),
        "size_units": _grid_size_to_dict(zone.size_units),
        "origin_mm": _grid_origin_to_mm(zone.origin_units, unit_size),
        "size_mm": _grid_size_to_mm(zone.size_units, unit_size),
        "layer_id": zone.layer_id,
        "reservation_kind": zone.reservation_kind,
        "asset_kind": zone.asset_kind,
        "removal_order": zone.removal_order,
        "access_direction": zone.access_direction,
        "support_surface_id": zone.support_surface_id,
        "comment": zone.comment,
    }


def _support_surface_to_dict(surface, unit_size) -> dict[str, Any]:
    return {
        "id": surface.id,
        "owner_type": surface.owner_type.value,
        "owner_id": surface.owner_id,
        "face": surface.face.value,
        "origin_units": _grid_point_to_dict(surface.origin_units),
        "size_units": _grid_size_to_dict(surface.size_units),
        "origin_mm": _grid_origin_to_mm(surface.origin_units, unit_size),
        "size_mm": _grid_size_to_mm(surface.size_units, unit_size),
        "layer_id": surface.layer_id,
        "purpose": surface.purpose,
        "status": "abstract_only",
        "physical_validation": "not_validated",
        "comment": surface.comment,
    }


def _removal_sequence_to_dict(grid: VolumetricGrid) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for placement in grid.module_placements:
        if placement.removal_order is None:
            continue
        entries.append(
            {
                "order": placement.removal_order,
                "target_id": placement.id,
                "target_type": "module_placement",
                "access_direction": placement.access_direction,
                "support_surface_id": placement.support_surface_id,
            }
        )
    for zone in grid.zones:
        if zone.removal_order is None:
            continue
        entries.append(
            {
                "order": zone.removal_order,
                "target_id": zone.id,
                "target_type": f"zone:{zone.kind.value}",
                "access_direction": zone.access_direction,
                "support_surface_id": zone.support_surface_id,
                "reservation_kind": zone.reservation_kind,
                "asset_kind": zone.asset_kind,
            }
        )
    return sorted(entries, key=lambda entry: entry["order"])

def _grid_origin_to_mm(origin: GridPoint3D, unit_size) -> dict[str, float]:
    return {
        "x": origin.x * unit_size.x,
        "y": origin.y * unit_size.y,
        "z": origin.z * unit_size.z,
    }


def _grid_size_to_mm(size: GridSize3D, unit_size) -> dict[str, float]:
    return {
        "x": size.x * unit_size.x,
        "y": size.y * unit_size.y,
        "z": size.z * unit_size.z,
    }
