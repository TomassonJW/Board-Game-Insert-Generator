"""Lane produit HiGHS locale, hors ligne, isolée et fail-closed.

Le binaire est fourni par l'add-in Fusion. Le coeur ne l'importe jamais et ne
le considère jamais comme une autorité : une proposition positive doit encore
passer le certificat BGIG commun dans ``minimal_layout_solver``.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import tempfile
from time import perf_counter, sleep
from typing import Callable, Mapping, Sequence

from board_game_insert_generator.free_3d_greedy_solver import Free3DPlacement
from board_game_insert_generator.free_3d_plan_adapter import (
    Free3DPreparedProblem,
)
from board_game_insert_generator.incremental_project_state import (
    canonical_digest,
)


HIGHS_PRODUCT_SCHEMA_V1 = "bgig.highs_product_lane.v1"
HIGHS_PRODUCT_VERSION = "1.15.1"
HIGHS_PRODUCT_FAMILY = "mixed_integer_programming"
HIGHS_PRODUCT_MODEL = "axis_aligned_single_floor_rectangles_v1"
HIGHS_PRODUCT_SOURCE_ASSET_SHA256 = (
    "26302d9024f307e09128a45a58898917287351dcf754c55aebc07742237f78bf"
)
HIGHS_PRODUCT_EXECUTABLE_SHA256 = (
    "4ff24abf4cfdd5f4e87e73edf6886d1b9333c13c388b328466ca15a502b4c46d"
)
HIGHS_PRODUCT_DLL_SHA256 = (
    "722dfd5eb66e1de2fe306d8e6e9c68085ca1b454c04e1860dd22f636557e6de5"
)

STATUS_NOT_CONFIGURED = "not_configured"
STATUS_UNSUPPORTED = "unsupported"
STATUS_INVALID_RUNTIME = "invalid_runtime"
STATUS_SOLUTION_FOUND = "solution_found"
STATUS_BOUNDED_UNKNOWN = "bounded_unknown"
STATUS_EXTERNAL_ERROR = "external_error"
STATUS_CANCELLED = "cancelled"

_SCALE_PER_MM = 1000
_EPSILON_MM = 1e-6
_MAX_ITEM_COUNT = 64
_POLL_SECONDS = 0.02
_configured_executable: Path | None = None
_configured_scratch_root: Path | None = None


@dataclass(frozen=True)
class HighsProductLimits:
    """Sous-budget explicite ajouté au portefeuille produit."""

    wall_seconds: float
    memory_mebibytes: int = 1024
    threads: int = 1
    seed: int = 640708

    def to_dict(self) -> dict[str, object]:
        return {
            "wall_seconds": self.wall_seconds,
            "memory_mebibytes": self.memory_mebibytes,
            "threads": self.threads,
            "seed": self.seed,
        }


@dataclass(frozen=True)
class _FloorItem:
    participant_id: str
    role: str
    name: str
    local_size_mm: tuple[float, float, float]
    packed_width: int
    packed_height: int


@dataclass(frozen=True)
class _FloorProblem:
    problem_digest: str
    bin_width: int
    bin_height: int
    box_clearance_mm: float
    scale_per_mm: int
    items: tuple[_FloorItem, ...]


@dataclass(frozen=True)
class HighsProductExecution:
    """Résultat isolé ; les mesures volatiles ne sont pas certifiables."""

    status: str
    stop_reason: str
    limits: HighsProductLimits
    problem_digest: str
    engine_status: str
    placements: tuple[Free3DPlacement, ...]
    model_digest: str
    solution_digest: str
    invocation_count: int
    total_wall_seconds: float | None = None
    cpu_seconds: float | None = None
    peak_working_set_bytes: int | None = None

    def deterministic_report(self) -> dict[str, object]:
        report: dict[str, object] = {
            "schema_version": HIGHS_PRODUCT_SCHEMA_V1,
            "candidate": {
                "candidate_id": "highs",
                "family": HIGHS_PRODUCT_FAMILY,
                "version": HIGHS_PRODUCT_VERSION,
                "source_asset_sha256": HIGHS_PRODUCT_SOURCE_ASSET_SHA256,
            },
            "model": {
                "kind": HIGHS_PRODUCT_MODEL,
                "problem_digest": self.problem_digest,
                "model_digest": self.model_digest,
            },
            "limits": self.limits.to_dict(),
            "status": self.status,
            "stop_reason": self.stop_reason,
            "engine_status": self.engine_status,
            "solution_digest": self.solution_digest,
            "invocation_count": self.invocation_count,
            "invariants": {
                "bgig_certificate_required": True,
                "global_install_required": False,
                "network_invocation_count": 0,
                "subprocess_isolated": True,
                "telemetry_enabled": False,
                "volatile_runtime_metrics_in_certifiable_payload": False,
            },
        }
        report["report_digest"] = canonical_digest(report)
        return report


def configure_highs_product_runtime(
    executable: str | Path | None,
    *,
    scratch_root: str | Path | None = None,
) -> None:
    """Configure la ressource locale fournie par la surface produit."""

    global _configured_executable, _configured_scratch_root
    _configured_executable = (
        Path(executable).resolve() if executable is not None else None
    )
    _configured_scratch_root = (
        Path(scratch_root).resolve() if scratch_root is not None else None
    )


def highs_product_limits(effort_profile: str) -> HighsProductLimits:
    """Expose les caps ajoutés explicitement par ADR-0082."""

    if effort_profile == "quick":
        return HighsProductLimits(wall_seconds=0.75)
    if effort_profile in {"normal", "deep"}:
        return HighsProductLimits(wall_seconds=3.0)
    raise ValueError(f"Unknown effort profile {effort_profile!r}.")


def solve_highs_product_floor(
    participants: Sequence[Mapping[str, object]],
    problem: Free3DPreparedProblem,
    *,
    effort_profile: str,
    cancel_check: Callable[[], bool] | None = None,
) -> HighsProductExecution:
    """Produit au plus une proposition sol 2D, sinon laisse BGIG poursuivre."""

    limits = highs_product_limits(effort_profile)
    if _configured_executable is None:
        return _empty_execution(
            limits,
            status=STATUS_NOT_CONFIGURED,
            stop_reason="product_runtime_not_configured",
        )
    runtime_error = _runtime_error(_configured_executable)
    if runtime_error is not None:
        return _empty_execution(
            limits,
            status=STATUS_INVALID_RUNTIME,
            stop_reason=runtime_error,
        )
    prepared, rejection = _prepare_floor_problem(participants, problem)
    if prepared is None:
        return _empty_execution(
            limits,
            status=STATUS_UNSUPPORTED,
            stop_reason=rejection,
        )
    if cancel_check is not None and cancel_check():
        return _empty_execution(
            limits,
            status=STATUS_CANCELLED,
            stop_reason="cancelled_before_external_start",
            problem_digest=prepared.problem_digest,
        )
    try:
        return _execute_highs(
            prepared,
            _configured_executable,
            limits,
            cancel_check=cancel_check,
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return _empty_execution(
            limits,
            status=STATUS_EXTERNAL_ERROR,
            stop_reason="highs_runtime_io_failed",
            problem_digest=prepared.problem_digest,
            invocation_count=1,
        )


def _runtime_error(executable: Path) -> str | None:
    if not executable.is_file():
        return "highs_executable_missing"
    library = executable.with_name("highs.dll")
    if not library.is_file():
        return "highs_runtime_library_missing"
    try:
        executable_digest = _sha256_path(executable)
        library_digest = _sha256_path(library)
    except OSError:
        return "highs_runtime_unreadable"
    if executable_digest != HIGHS_PRODUCT_EXECUTABLE_SHA256:
        return "highs_executable_digest_mismatch"
    if library_digest != HIGHS_PRODUCT_DLL_SHA256:
        return "highs_runtime_library_digest_mismatch"
    return None


def _prepare_floor_problem(
    participants: Sequence[Mapping[str, object]],
    problem: Free3DPreparedProblem,
) -> tuple[_FloorProblem | None, str]:
    if problem.top_inset_zones:
        return None, "top_inset_reservations_not_supported"
    if not 1 <= len(participants) <= _MAX_ITEM_COUNT:
        return None, "participant_count_outside_highs_cap"
    box_clearance = float(problem.box_xy_clearance_mm)
    between_clearance = float(problem.xy_clearance_mm)
    usable_x = float(problem.box["x"]) - 2.0 * box_clearance
    usable_y = float(problem.box["y"]) - 2.0 * box_clearance
    if usable_x <= 0.0 or usable_y <= 0.0:
        return None, "non_positive_floor_bounds"
    try:
        bin_width = _scaled(usable_x + between_clearance)
        bin_height = _scaled(usable_y + between_clearance)
        items: list[_FloorItem] = []
        for raw in participants:
            participant = dict(raw)
            minimum = _mapping(participant.get("minimum_local_mm"))
            local = tuple(
                float(minimum[axis]) for axis in ("x", "y", "z")
            )
            if any(value <= 0.0 for value in local):
                return None, "non_positive_participant_size"
            if local[2] > problem.storage_height_mm + _EPSILON_MM:
                return None, "participant_height_exceeds_storage_height"
            items.append(
                _FloorItem(
                    participant_id=str(participant["id"]),
                    role=str(participant["role"]),
                    name=str(participant["name"]),
                    local_size_mm=local,
                    packed_width=_scaled(local[0] + between_clearance),
                    packed_height=_scaled(local[1] + between_clearance),
                )
            )
    except (KeyError, TypeError, ValueError, OverflowError):
        return None, "participant_dimensions_not_representable"
    canonical_items = tuple(
        sorted(items, key=lambda value: value.participant_id)
    )
    payload = {
        "model": HIGHS_PRODUCT_MODEL,
        "bin_width": bin_width,
        "bin_height": bin_height,
        "box_clearance_mm": box_clearance,
        "scale_per_mm": _SCALE_PER_MM,
        "items": [
            {
                "participant_id": item.participant_id,
                "role": item.role,
                "name": item.name,
                "local_size_mm": list(item.local_size_mm),
                "packed_width": item.packed_width,
                "packed_height": item.packed_height,
            }
            for item in canonical_items
        ],
    }
    return (
        _FloorProblem(
            problem_digest=canonical_digest(payload),
            bin_width=bin_width,
            bin_height=bin_height,
            box_clearance_mm=box_clearance,
            scale_per_mm=_SCALE_PER_MM,
            items=canonical_items,
        ),
        "",
    )


def _execute_highs(
    problem: _FloorProblem,
    executable: Path,
    limits: HighsProductLimits,
    *,
    cancel_check: Callable[[], bool] | None,
) -> HighsProductExecution:
    scratch_root = _configured_scratch_root
    if scratch_root is not None:
        scratch_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="bgig-highs-",
        dir=str(scratch_root) if scratch_root is not None else None,
    ) as temporary:
        run_root = Path(temporary)
        model_path = run_root / "model.lp"
        options_path = run_root / "highs.options"
        solution_path = run_root / "highs.sol"
        model, variable_names = _build_lp(problem)
        model_path.write_text(model, encoding="ascii")
        model_digest = sha256(model.encode("ascii")).hexdigest()
        options_path.write_text(
            _options_text(limits),
            encoding="ascii",
        )
        environment = dict(os.environ)
        for key in (
            "ALL_PROXY",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "all_proxy",
            "http_proxy",
            "https_proxy",
        ):
            environment.pop(key, None)
        environment["NO_PROXY"] = "*"
        started = perf_counter()
        peak_bytes = 0
        cpu_seconds = 0.0
        termination_reason: str | None = None
        try:
            process = subprocess.Popen(
                [
                    str(executable),
                    str(model_path),
                    "--options_file",
                    str(options_path),
                ],
                cwd=str(run_root),
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError:
            return _empty_execution(
                limits,
                status=STATUS_EXTERNAL_ERROR,
                stop_reason="highs_process_start_failed",
                problem_digest=problem.problem_digest,
                model_digest=model_digest,
                invocation_count=1,
            )
        while process.poll() is None:
            elapsed = perf_counter() - started
            current_peak, current_cpu = _process_metrics(process.pid)
            peak_bytes = max(peak_bytes, current_peak or 0)
            cpu_seconds = max(cpu_seconds, current_cpu or 0.0)
            if cancel_check is not None and cancel_check():
                termination_reason = "cancelled_during_external_solve"
                process.terminate()
                break
            if peak_bytes > limits.memory_mebibytes * 1024 * 1024:
                termination_reason = "memory_limit_exceeded"
                process.terminate()
                break
            if elapsed > limits.wall_seconds:
                termination_reason = "wall_time_limit_exceeded"
                process.terminate()
                break
            sleep(_POLL_SECONDS)
        if termination_reason is not None:
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
        exit_code = process.wait()
        total_wall = perf_counter() - started
        common = {
            "limits": limits,
            "problem_digest": problem.problem_digest,
            "model_digest": model_digest,
            "invocation_count": 1,
            "total_wall_seconds": round(total_wall, 6),
            "cpu_seconds": round(cpu_seconds, 6),
            "peak_working_set_bytes": peak_bytes or None,
        }
        if termination_reason is not None:
            return _empty_execution(
                **common,
                status=(
                    STATUS_CANCELLED
                    if termination_reason.startswith("cancelled")
                    else STATUS_BOUNDED_UNKNOWN
                ),
                stop_reason=termination_reason,
            )
        if exit_code != 0:
            return _empty_execution(
                **common,
                status=STATUS_EXTERNAL_ERROR,
                stop_reason=f"highs_exit_nonzero:{exit_code}",
            )
        if not solution_path.is_file():
            return _empty_execution(
                **common,
                status=STATUS_EXTERNAL_ERROR,
                stop_reason="highs_solution_missing",
            )
        try:
            solution_raw = solution_path.read_text(encoding="utf-8")
            model_status, primal_status, values = _read_solution(solution_raw)
        except (OSError, UnicodeError, ValueError):
            return _empty_execution(
                **common,
                status=STATUS_EXTERNAL_ERROR,
                stop_reason="highs_solution_invalid",
            )
        solution_digest = sha256(solution_raw.encode("utf-8")).hexdigest()
        if model_status == "Infeasible":
            return _empty_execution(
                **common,
                status=STATUS_BOUNDED_UNKNOWN,
                stop_reason="floor_model_infeasible_not_product_impossible",
                engine_status=model_status,
                solution_digest=solution_digest,
            )
        if model_status != "Optimal" or primal_status != "Feasible":
            return _empty_execution(
                **common,
                status=STATUS_BOUNDED_UNKNOWN,
                stop_reason="no_optimal_floor_proposal_within_limit",
                engine_status=model_status,
                solution_digest=solution_digest,
            )
        try:
            placements = _placements_from_values(
                problem, variable_names, values
            )
        except (KeyError, TypeError, ValueError, OverflowError):
            return _empty_execution(
                **common,
                status=STATUS_EXTERNAL_ERROR,
                stop_reason="highs_placement_payload_invalid",
                engine_status=model_status,
                solution_digest=solution_digest,
            )
        return HighsProductExecution(
            status=STATUS_SOLUTION_FOUND,
            stop_reason="optimal_floor_proposal_returned",
            engine_status=model_status,
            placements=placements,
            solution_digest=solution_digest,
            **common,
        )


def _build_lp(
    problem: _FloorProblem,
) -> tuple[str, dict[str, tuple[str | None, str, str]]]:
    x_names = [f"x_{index}" for index, _ in enumerate(problem.items)]
    y_names = [f"y_{index}" for index, _ in enumerate(problem.items)]
    rotation_names: list[str | None] = []
    width_terms: list[tuple[int, str | None]] = []
    height_terms: list[tuple[int, str | None]] = []
    binary_names: list[str] = []
    constraints: list[str] = []
    variables: dict[str, tuple[str | None, str, str]] = {}
    for index, item in enumerate(problem.items):
        if item.packed_width != item.packed_height:
            rotation = f"r_{index}"
            binary_names.append(rotation)
        else:
            rotation = None
        rotation_names.append(rotation)
        width_terms.append(
            (item.packed_height - item.packed_width, rotation)
        )
        height_terms.append(
            (item.packed_width - item.packed_height, rotation)
        )
        variables[item.participant_id] = (
            rotation,
            x_names[index],
            y_names[index],
        )
        x_constraint = [(1, x_names[index])]
        y_constraint = [(1, y_names[index])]
        if rotation is not None:
            x_constraint.append(
                (item.packed_height - item.packed_width, rotation)
            )
            y_constraint.append(
                (item.packed_width - item.packed_height, rotation)
            )
        constraints.append(
            f" floor_x_{index}: {_expression(x_constraint)} <= "
            f"{problem.bin_width - item.packed_width}"
        )
        constraints.append(
            f" floor_y_{index}: {_expression(y_constraint)} <= "
            f"{problem.bin_height - item.packed_height}"
        )
    big_m = max(problem.bin_width, problem.bin_height)
    for first in range(len(problem.items)):
        for second in range(first + 1, len(problem.items)):
            separated = [
                f"sep_{first}_{second}_{axis}" for axis in range(4)
            ]
            binary_names.extend(separated)
            directions = (
                (
                    x_names[first],
                    x_names[second],
                    width_terms[first],
                    problem.items[first].packed_width,
                    separated[0],
                ),
                (
                    x_names[second],
                    x_names[first],
                    width_terms[second],
                    problem.items[second].packed_width,
                    separated[1],
                ),
                (
                    y_names[first],
                    y_names[second],
                    height_terms[first],
                    problem.items[first].packed_height,
                    separated[2],
                ),
                (
                    y_names[second],
                    y_names[first],
                    height_terms[second],
                    problem.items[second].packed_height,
                    separated[3],
                ),
            )
            for axis, (
                positive,
                negative,
                (rotation_coefficient, rotation),
                base_size,
                separation,
            ) in enumerate(directions):
                terms = [(1, positive), (-1, negative)]
                if rotation is not None:
                    terms.append((rotation_coefficient, rotation))
                terms.append((big_m, separation))
                constraints.append(
                    f" separate_{first}_{second}_{axis}: "
                    f"{_expression(terms)} <= {big_m - base_size}"
                )
            constraints.append(
                f" choose_{first}_{second}: "
                f"{_expression([(1, value) for value in separated])} >= 1"
            )
    lines = [
        "Minimize",
        f" objective: "
        f"{_expression([(1, value) for value in x_names + y_names])}",
        "Subject To",
        *constraints,
        "Bounds",
        *[
            f" 0 <= {name} <= {problem.bin_width}"
            for name in x_names
        ],
        *[
            f" 0 <= {name} <= {problem.bin_height}"
            for name in y_names
        ],
        "General",
        *[f" {name}" for name in x_names + y_names],
    ]
    if binary_names:
        lines.extend(["Binary", *[f" {name}" for name in binary_names]])
    lines.append("End")
    return "\n".join(lines) + "\n", variables


def _options_text(limits: HighsProductLimits) -> str:
    internal_limit = max(0.05, limits.wall_seconds * 0.9)
    return (
        "\n".join(
            (
                "output_flag = false",
                f"time_limit = {internal_limit}",
                f"threads = {limits.threads}",
                f"random_seed = {limits.seed}",
                "parallel = off",
                "solution_file = highs.sol",
                "write_solution_to_file = true",
                "write_solution_style = 0",
            )
        )
        + "\n"
    )


def _read_solution(
    raw: str,
) -> tuple[str, str, dict[str, float]]:
    lines = raw.splitlines()
    if len(lines) < 5 or lines[0] != "Model status":
        raise ValueError("Unsupported HiGHS solution format.")
    model_status = lines[1].strip()
    try:
        primal_index = lines.index("# Primal solution values")
    except ValueError as exc:
        raise ValueError("Missing HiGHS primal section.") from exc
    primal_status = lines[primal_index + 1].strip()
    if primal_status != "Feasible":
        return model_status, primal_status, {}
    try:
        columns_index = next(
            index
            for index, line in enumerate(lines)
            if line.startswith("# Columns ")
        )
        rows_index = next(
            index
            for index, line in enumerate(lines)
            if line.startswith("# Rows ")
        )
    except StopIteration as exc:
        raise ValueError("Incomplete HiGHS solution columns.") from exc
    values: dict[str, float] = {}
    for line in lines[columns_index + 1 : rows_index]:
        if not line.strip():
            continue
        name, value = line.rsplit(" ", 1)
        values[name] = float(value)
    return model_status, primal_status, values


def _placements_from_values(
    problem: _FloorProblem,
    variable_names: Mapping[str, tuple[str | None, str, str]],
    values: Mapping[str, float],
) -> tuple[Free3DPlacement, ...]:
    rectangles = []
    placements = []
    for item in problem.items:
        rotation_name, x_name, y_name = variable_names[item.participant_id]
        x = _integer_value(values[x_name], x_name)
        y = _integer_value(values[y_name], y_name)
        rotation = (
            _integer_value(values.get(rotation_name, 0.0), rotation_name)
            if rotation_name is not None
            else 0
        )
        if rotation not in {0, 1}:
            raise ValueError("Invalid HiGHS rotation value.")
        packed_width, packed_height = (
            (item.packed_height, item.packed_width)
            if rotation
            else (item.packed_width, item.packed_height)
        )
        if (
            x < 0
            or y < 0
            or x + packed_width > problem.bin_width
            or y + packed_height > problem.bin_height
        ):
            raise ValueError("HiGHS placement is outside the floor.")
        rectangles.append(
            (
                item.participant_id,
                x,
                y,
                packed_width,
                packed_height,
            )
        )
        local = item.local_size_mm
        world = (
            (local[1], local[0], local[2])
            if rotation
            else local
        )
        placements.append(
            Free3DPlacement(
                participant_id=item.participant_id,
                role=item.role,
                name=item.name,
                origin_mm=(
                    _round_mm(
                        problem.box_clearance_mm
                        + x / problem.scale_per_mm
                    ),
                    _round_mm(
                        problem.box_clearance_mm
                        + y / problem.scale_per_mm
                    ),
                    0.0,
                ),
                world_size_mm=world,
                local_size_mm=local,
                rotation_deg_z=90 if rotation else 0,
                supporting_ids=(),
                support_coverage_ratio=1.0,
            )
        )
    for first_index, first in enumerate(rectangles):
        for second in rectangles[first_index + 1 :]:
            if not (
                first[1] + first[3] <= second[1]
                or second[1] + second[3] <= first[1]
                or first[2] + first[4] <= second[2]
                or second[2] + second[4] <= first[2]
            ):
                raise ValueError("HiGHS placements overlap.")
    return tuple(
        sorted(placements, key=lambda value: value.participant_id)
    )


def _empty_execution(
    limits: HighsProductLimits,
    *,
    status: str,
    stop_reason: str,
    problem_digest: str = "",
    engine_status: str = "",
    model_digest: str = "",
    solution_digest: str = "",
    invocation_count: int = 0,
    total_wall_seconds: float | None = None,
    cpu_seconds: float | None = None,
    peak_working_set_bytes: int | None = None,
) -> HighsProductExecution:
    return HighsProductExecution(
        status=status,
        stop_reason=stop_reason,
        limits=limits,
        problem_digest=problem_digest,
        engine_status=engine_status,
        placements=(),
        model_digest=model_digest,
        solution_digest=solution_digest,
        invocation_count=invocation_count,
        total_wall_seconds=total_wall_seconds,
        cpu_seconds=cpu_seconds,
        peak_working_set_bytes=peak_working_set_bytes,
    )


def _expression(terms: Sequence[tuple[int, str]]) -> str:
    rendered: list[str] = []
    for coefficient, name in terms:
        if coefficient == 0:
            continue
        absolute = abs(coefficient)
        value = name if absolute == 1 else f"{absolute} {name}"
        if not rendered:
            rendered.append(value if coefficient > 0 else f"- {value}")
        else:
            rendered.append(
                f"+ {value}" if coefficient > 0 else f"- {value}"
            )
    return " ".join(rendered) or "0"


def _integer_value(value: object, name: str) -> int:
    number = float(value)
    rounded = int(round(number))
    if abs(number - rounded) > 1e-5:
        raise ValueError(f"HiGHS variable {name} is not integral.")
    return rounded


def _scaled(value_mm: float) -> int:
    scaled = int(round(float(value_mm) * _SCALE_PER_MM))
    if (
        scaled <= 0
        or scaled > 2_000_000_000
        or abs(scaled / _SCALE_PER_MM - float(value_mm)) > _EPSILON_MM
    ):
        raise ValueError("Dimension cannot be scaled exactly.")
    return scaled


def _round_mm(value: float) -> float:
    return round(float(value), 6)


def _process_metrics(process_id: int) -> tuple[int | None, float | None]:
    if os.name != "nt":
        return None, None
    try:
        return _windows_process_metrics(process_id)
    except (AttributeError, OSError, ValueError):
        return None, None


def _windows_process_metrics(
    process_id: int,
) -> tuple[int | None, float | None]:
    class ProcessMemoryCountersEx(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    class FileTime(ctypes.Structure):
        _fields_ = [
            ("low", ctypes.c_ulong),
            ("high", ctypes.c_ulong),
        ]

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    handle = kernel32.OpenProcess(0x1000 | 0x0400, False, process_id)
    if not handle:
        return None, None
    try:
        memory = ProcessMemoryCountersEx()
        memory.cb = ctypes.sizeof(memory)
        peak: int | None = None
        if psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(memory), ctypes.sizeof(memory)
        ):
            peak = int(memory.PeakWorkingSetSize)
        creation = FileTime()
        exit_time = FileTime()
        kernel = FileTime()
        user = FileTime()
        cpu: float | None = None
        if kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ):
            kernel_ticks = (kernel.high << 32) + kernel.low
            user_ticks = (user.high << 32) + user.low
            cpu = (kernel_ticks + user_ticks) / 10_000_000.0
        return peak, cpu
    finally:
        kernel32.CloseHandle(handle)


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Expected an object.")
    return dict(value)


def _sha256_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
