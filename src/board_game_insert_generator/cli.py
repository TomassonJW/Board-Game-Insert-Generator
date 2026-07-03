from __future__ import annotations

import argparse
import sys
from pathlib import Path

from board_game_insert_generator.config_loader import ConfigError, load_config
from board_game_insert_generator.layout import LayoutError, generate_basic_layout
from board_game_insert_generator.report import layout_to_json, layout_to_markdown
from board_game_insert_generator.tolerance import ToleranceError
from board_game_insert_generator.validation import ValidationError


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "diagnose":
        return _diagnose(arguments[1:])
    return _report(arguments)


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


def _print_error(title: str, exc: Exception) -> None:
    print(f"{title}: {exc}", file=sys.stderr)
