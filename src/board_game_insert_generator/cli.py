from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from board_game_insert_generator.box_fill import analyze_box_fill_plan, box_fill_plan_to_dict
from board_game_insert_generator.box_fill_solver import BoxFillCandidate, BoxFillSolveRequest, format_box_fill_solution_markdown, render_box_fill_solution_svg, solve_box_fill_greedy
from board_game_insert_generator.box_fill_solver_io import load_box_fill_solve_request
from board_game_insert_generator.box_fill_variants import (
    BoxFillVariantRequest,
    SUPPORTED_POLICY_IDS,
    format_variant_portfolio_markdown,
    generate_box_fill_variants,
    render_variant_portfolio_html,
    selected_variant_to_dict,
    standard_preference_profile,
    variant_portfolio_to_dict,
)
from board_game_insert_generator.models import Dimension3D
from board_game_insert_generator.cad_ir import CadIrError, build_blank_cad_scene
from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.layout import LayoutError, generate_basic_layout
from board_game_insert_generator.report import layout_to_json, layout_to_markdown
from board_game_insert_generator.tolerance import ToleranceError
from board_game_insert_generator.validation import ValidationError


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] in {"-h", "--help"}:
        _print_top_level_help()
        return 0
    if arguments and arguments[0] == "diagnose":
        return _diagnose(arguments[1:])
    if arguments and arguments[0] == "export-cad-ir":
        return _export_cad_ir(arguments[1:])
    if arguments and arguments[0] == "validate-box-fill":
        return _validate_box_fill(arguments[1:])
    if arguments and arguments[0] == "report-box-fill":
        return _report_box_fill(arguments[1:])
    if arguments and arguments[0] == "export-box-fill-plan":
        return _export_box_fill_plan(arguments[1:])
    if arguments and arguments[0] == "solve-box-fill-greedy":
        return _solve_box_fill_greedy(arguments[1:])
    if arguments and arguments[0] == "render-box-fill-preview":
        return _render_box_fill_preview(arguments[1:])
    if arguments and arguments[0] == "report-box-fill-solution":
        return _report_box_fill_solution(arguments[1:])
    if arguments and arguments[0] == "export-box-fill-solution":
        return _export_box_fill_solution(arguments[1:])
    if arguments and arguments[0] == "report-box-fill-variants":
        return _report_box_fill_variants(arguments[1:])
    if arguments and arguments[0] == "render-box-fill-variant-dashboard":
        return _render_box_fill_variant_dashboard(arguments[1:])
    if arguments and arguments[0] == "export-box-fill-variant":
        return _export_box_fill_variant(arguments[1:])
    return _report(arguments)



def _print_top_level_help() -> None:
    print(
        "Board Game Insert Generator CLI\n"
        "\n"
        "Usage:\n"
        "  python -m board_game_insert_generator CONFIG --format markdown|json [--output PATH]\n"
        "  python -m board_game_insert_generator diagnose CONFIG\n"
        "  python -m board_game_insert_generator export-cad-ir CONFIG --output PATH\n"
        "  python -m board_game_insert_generator validate-box-fill CONFIG [--format text|json]\n"
        "  python -m board_game_insert_generator report-box-fill CONFIG --format markdown|json [--output PATH]\n"
        "  python -m board_game_insert_generator export-box-fill-plan CONFIG --output PATH\n"
        "  python -m board_game_insert_generator report-box-fill-variants REQUEST --format markdown|json|html [--output PATH]\n"
        "  python -m board_game_insert_generator render-box-fill-variant-dashboard REQUEST --output PATH\n"
        "  python -m board_game_insert_generator export-box-fill-variant REQUEST --variant recommended|ID --output PATH [--cad-ir-output PATH]\n"
        "\n"
        "CAD IR export is a subcommand named export-cad-ir; it is not an --export-cad-ir option."
    )


def _report(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a V0 layout report for a board game insert configuration."
    )
    parser.add_argument("config", help="Path to a JSON configuration file.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Report format.",
    )
    parser.add_argument(
        "--output",
        help="Optional output file. Prints to stdout when omitted.",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        result = generate_basic_layout(config)
        report = (
            layout_to_json(config, result)
            if args.format == "json"
            else layout_to_markdown(config, result)
        )
    except ConfigError as exc:
        _print_error("Configuration error", exc)
        return 2
    except ValidationError as exc:
        _print_error("Validation error", exc)
        return 2
    except LayoutError as exc:
        _print_error("Layout error", exc)
        return 2
    except ToleranceError as exc:
        _print_error("Tolerance error", exc)
        return 2

    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


def _diagnose(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run a short diagnostic over config loading, layout and report generation."
    )
    parser.add_argument("config", help="Path to a JSON configuration file.")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        result = generate_basic_layout(config)
        markdown_report = layout_to_markdown(config, result)
        json_report = layout_to_json(config, result)
    except ConfigError as exc:
        _print_error("Configuration error", exc)
        return 2
    except ValidationError as exc:
        _print_error("Validation error", exc)
        return 2
    except LayoutError as exc:
        _print_error("Layout error", exc)
        return 2
    except ToleranceError as exc:
        _print_error("Tolerance error", exc)
        return 2

    lines = [
        f"Diagnostic OK - {config.project_name}",
        f"- Config loaded: {config.source_path or args.config}",
        f"- Units: {config.units}",
        f"- Layout strategy: {config.layout.strategy}",
        f"- Requested modules: {len(config.modules)}",
        f"- Generated instances: {len(result.cells)}",
        f"- Printable bodies: {len(result.printable_bodies)}",
        f"- Warnings: {len(result.warnings)}",
        f"- Markdown report: OK ({len(markdown_report)} chars)",
        f"- JSON report: OK ({len(json_report)} chars)",
    ]
    print("\n".join(lines))
    return 0


def _export_cad_ir(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Export a CAD IR V0 JSON scene from a board game insert configuration."
    )
    parser.add_argument("config", help="Path to a JSON configuration file.")
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output CAD IR JSON file.",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        result = generate_basic_layout(config)
        scene = build_blank_cad_scene(config, result)
    except ConfigError as exc:
        _print_error("Configuration error", exc)
        return 2
    except ValidationError as exc:
        _print_error("Validation error", exc)
        return 2
    except LayoutError as exc:
        _print_error("Layout error", exc)
        return 2
    except ToleranceError as exc:
        _print_error("Tolerance error", exc)
        return 2
    except CadIrError as exc:
        _print_error("CAD IR error", exc)
        return 2

    output_path = Path(args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(scene.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        _print_error("Output error", exc)
        return 2

    lines = [
        f"CAD IR export OK - {config.project_name}",
        f"- Output: {output_path}",
        f"- Schema: {scene.schema_version}",
        f"- Components: {len(scene.components)}",
        "- Fusion input target: fusion_addin/BoardGameInsertGenerator/cad_ir_input.json",
    ]
    print("\n".join(lines))
    return 0

def _print_error(title: str, exc: Exception) -> None:
    print(f"{title}: {exc}", file=sys.stderr)


def _require_box_fill_config(config_path: str):
    config = load_config(config_path)
    if config.box_fill_plan is None:
        raise ConfigError("Configuration does not declare a box_fill_plan.")
    return config


def _validate_box_fill(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a BoxFillPlan V0 without running a solver.")
    parser.add_argument("config", help="Path to a JSON configuration containing box_fill_plan.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        config = _require_box_fill_config(args.config)
        analysis = analyze_box_fill_plan(config.box_fill_plan)
    except ConfigError as exc:
        _print_error("Configuration error", exc)
        return 2
    payload = analysis.to_dict()
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"BoxFillPlan validation {'OK' if not analysis.issues else 'FAILED'} - {config.box_fill_plan.id}")
        print(f"- Exact free volume: {analysis.free_volume.total_free_volume_mm3:.2f} mm3")
        print(f"- Free regions: {len(analysis.free_volume.regions)}")
        for issue in analysis.issues:
            print(f"- {issue.severity} {issue.code}: {issue.message} Action: {issue.corrective_action}")
    return 0 if not analysis.issues else 2


def _report_box_fill(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Render a BoxFillPlan report through the standard report contract.")
    parser.add_argument("config", help="Path to a JSON configuration containing box_fill_plan.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Optional output file.")
    args = parser.parse_args(argv)
    try:
        config = _require_box_fill_config(args.config)
        result = generate_basic_layout(config)
        report = layout_to_json(config, result) if args.format == "json" else layout_to_markdown(config, result)
    except (ConfigError, ValidationError, LayoutError, ToleranceError) as exc:
        _print_error("BoxFillPlan report error", exc)
        return 2
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


def _export_box_fill_plan(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Export the stable BoxFillPlan V0 JSON contract.")
    parser.add_argument("config", help="Path to a JSON configuration containing box_fill_plan.")
    parser.add_argument("--output", "-o", required=True, help="Output BoxFillPlan JSON file.")
    args = parser.parse_args(argv)
    try:
        config = _require_box_fill_config(args.config)
        analysis = analyze_box_fill_plan(config.box_fill_plan)
    except ConfigError as exc:
        _print_error("Configuration error", exc)
        return 2
    if analysis.issues:
        _print_error("BoxFillPlan validation error", ValueError("Cannot export an invalid BoxFillPlan; run validate-box-fill for diagnostics."))
        return 2
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(box_fill_plan_to_dict(config.box_fill_plan), indent=2) + "\n", encoding="utf-8")
    print(f"BoxFillPlan export OK - {config.box_fill_plan.id}\n- Output: {output_path}")
    return 0


def _parse_candidate(value: str) -> BoxFillCandidate:
    fields = value.split(":")
    if len(fields) not in (5, 6, 7):
        raise ConfigError("Candidate must be ID:NAME:X:Y:Z[:LAYER][:rotate].")
    module_id, name, x, y, z = fields[:5]
    layer = () if len(fields) < 6 or not fields[5] else (fields[5],)
    rotate = len(fields) == 7 and fields[6].lower() in {"rotate", "true", "yes"}
    try:
        size = Dimension3D(float(x), float(y), float(z))
    except ValueError as exc:
        raise ConfigError("Candidate dimensions must be numeric.") from exc
    return BoxFillCandidate(module_id, name, size, allowed_layer_ids=layer, allow_xy_rotation=rotate)


def _solve_box_fill_greedy(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Solve explicit BoxFillPlan candidates with deterministic greedy 2D placement.")
    parser.add_argument("config")
    parser.add_argument("--candidate", action="append", required=True, help="ID:NAME:X:Y:Z[:LAYER][:rotate], repeatable.")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        config = _require_box_fill_config(args.config)
        result = solve_box_fill_greedy(BoxFillSolveRequest(config.box_fill_plan, tuple(_parse_candidate(value) for value in args.candidate)))
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill solver error", exc)
        return 2
    payload = {**result.to_dict(), "solved_plan": box_fill_plan_to_dict(result.solved_plan)}
    serialized = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)
    return 0 if result.status == "solved" else 2


def _render_box_fill_preview(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Render a static SVG preview from a greedy BoxFill solve.")
    parser.add_argument("config")
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--layer")
    args = parser.parse_args(argv)
    try:
        config = _require_box_fill_config(args.config)
        result = solve_box_fill_greedy(BoxFillSolveRequest(config.box_fill_plan, tuple(_parse_candidate(value) for value in args.candidate)))
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill preview error", exc)
        return 2
    Path(args.output).write_text(render_box_fill_solution_svg(result, args.layer), encoding="utf-8")
    return 0 if result.status == "solved" else 2


def _solution_from_request(path: str):
    return solve_box_fill_greedy(load_box_fill_solve_request(path))


def _report_box_fill_solution(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Report a file-backed BoxFill greedy solution.")
    parser.add_argument("request")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        result = _solution_from_request(args.request)
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill solution error", exc); return 2
    value = json.dumps({**result.to_dict(), "solved_plan": box_fill_plan_to_dict(result.solved_plan)}, indent=2) if args.format == "json" else format_box_fill_solution_markdown(result)
    if args.output: Path(args.output).write_text(value + "\n", encoding="utf-8")
    else: print(value)
    return 0 if result.status == "solved" else 2


def _export_box_fill_solution(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Export solved BoxFillPlan and CAD IR metadata-ready result JSON.")
    parser.add_argument("request")
    parser.add_argument("--output", required=True)
    parser.add_argument("--cad-ir-output")
    args = parser.parse_args(argv)
    try:
        result = _solution_from_request(args.request)
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill solution error", exc)
        return 2
    payload = {**result.to_dict(), "solved_plan": box_fill_plan_to_dict(result.solved_plan)}
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.cad_ir_output:
        raw = json.loads(Path(args.request).read_text(encoding="utf-8"))
        config = load_config(Path(args.request).parent / raw["source_config"])
        scene = build_blank_cad_scene(config, generate_basic_layout(config)).to_dict()
        scene["metadata"]["box_fill_solution"] = payload
        Path(args.cad_ir_output).write_text(json.dumps(scene, indent=2) + "\n", encoding="utf-8")
    return 0 if result.status == "solved" else 2


def _variant_portfolio_from_args(args):
    solve_request = load_box_fill_solve_request(args.request)
    policies = tuple(args.policy) if args.policy else SUPPORTED_POLICY_IDS
    return generate_box_fill_variants(
        BoxFillVariantRequest(
            solve_request=solve_request,
            preference=standard_preference_profile(args.preference),
            policies=policies,
            max_variants=args.max_variants,
        )
    )


def _add_variant_arguments(parser: argparse.ArgumentParser, *, include_variant: bool = False) -> None:
    parser.add_argument(
        "--preference",
        default="balanced",
        help="P21 profile: balanced, compact, accessible or print_simple.",
    )
    parser.add_argument(
        "--policy",
        action="append",
        choices=SUPPORTED_POLICY_IDS,
        help="Repeat to restrict the bounded P21 policy set.",
    )
    parser.add_argument("--max-variants", type=int, default=5)
    if include_variant:
        parser.add_argument(
            "--variant",
            default="recommended",
            help="Variant id from report-box-fill-variants, or recommended.",
        )


def _report_box_fill_variants(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Compare bounded deterministic P21 BoxFill variants from a file-backed P20 request."
    )
    parser.add_argument("request")
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--output")
    _add_variant_arguments(parser)
    args = parser.parse_args(argv)
    try:
        portfolio = _variant_portfolio_from_args(args)
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill variant portfolio error", exc)
        return 2
    if args.format == "json":
        value = json.dumps(variant_portfolio_to_dict(portfolio), indent=2)
    elif args.format == "html":
        value = render_variant_portfolio_html(portfolio)
    else:
        value = format_variant_portfolio_markdown(portfolio)
    if args.output:
        Path(args.output).write_text(value + ("" if args.format == "html" else "\n"), encoding="utf-8")
    else:
        print(value)
    return 0 if portfolio.recommended_variant_id is not None else 2


def _render_box_fill_variant_dashboard(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Render a static self-contained P21 comparison dashboard; it stores no UI state."
    )
    parser.add_argument("request")
    parser.add_argument("--output", required=True)
    parser.add_argument("--layer")
    _add_variant_arguments(parser)
    args = parser.parse_args(argv)
    try:
        portfolio = _variant_portfolio_from_args(args)
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill variant dashboard error", exc)
        return 2
    Path(args.output).write_text(render_variant_portfolio_html(portfolio, args.layer), encoding="utf-8")
    return 0 if portfolio.recommended_variant_id is not None else 2


def _export_box_fill_variant(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Export an explicit P21 variant selection and optional CAD IR metadata without materializing Fusion."
    )
    parser.add_argument("request")
    parser.add_argument("--output", required=True)
    parser.add_argument("--cad-ir-output")
    _add_variant_arguments(parser, include_variant=True)
    args = parser.parse_args(argv)
    try:
        portfolio = _variant_portfolio_from_args(args)
        selection = selected_variant_to_dict(portfolio, args.variant)
    except (ConfigError, ValueError) as exc:
        _print_error("BoxFill variant export error", exc)
        return 2
    payload = {
        "portfolio": variant_portfolio_to_dict(portfolio),
        "selection": selection,
    }
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.cad_ir_output:
        raw = json.loads(Path(args.request).read_text(encoding="utf-8"))
        config = load_config(Path(args.request).parent / raw["source_config"])
        scene = build_blank_cad_scene(config, generate_basic_layout(config)).to_dict()
        scene["metadata"]["box_fill_variant_portfolio"] = payload["portfolio"]
        scene["metadata"]["box_fill_variant_selection"] = selection
        scene["metadata"]["box_fill_solution"] = selection["variant"]["solution"]
        Path(args.cad_ir_output).write_text(json.dumps(scene, indent=2) + "\n", encoding="utf-8")
    return 0