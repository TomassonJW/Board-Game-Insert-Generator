"""Board Game Insert Generator core package."""

from board_game_insert_generator.config_loader import load_config
from board_game_insert_generator.layout import generate_basic_layout
from board_game_insert_generator.report import layout_to_dict, layout_to_markdown

__all__ = [
    "generate_basic_layout",
    "layout_to_dict",
    "layout_to_markdown",
    "load_config",
]

__version__ = "0.1.0"
