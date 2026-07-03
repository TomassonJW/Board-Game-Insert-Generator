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
    except (ConfigError, ValidationError, LayoutError, ToleranceError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0
