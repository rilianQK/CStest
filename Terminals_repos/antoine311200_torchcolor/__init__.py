# torchcolor/__init__.py

from .color import Color, hex_to_rgb, is_rgb, background_colors, foreground_colors, reset_color
from .gradient import Gradient, GradientChunk
from .palette import Palette, palette_autumn_foliage, palette_forest_greens, palette_lavender_dreams, palette_monochrome, palette_ocean_breeze, palette_pastel, palette_rainbow, palette_retro_neon, palette_warm_sunset
from .print import print_color, print_more
from .printer import Printer, ModuleParam, _addindent, summarize_repeated_modules
from .strategy import ColorStrategy, ModuleStyle, ConstantColorStrategy, LayerColorStrategy, TrainableStrategy
from .style import TextStyle, FunctionalStyle, colorize, clean_style, infer_type, LAYER_SPLITTER, KeyType, DelimiterType, AnyType, FunctionalType

__all__ = [
    "Color", "hex_to_rgb", "is_rgb", "background_colors", "foreground_colors", "reset_color",
    "Gradient", "GradientChunk",
    "Palette", "palette_autumn_foliage", "palette_forest_greens", "palette_lavender_dreams", "palette_monochrome", "palette_ocean_breeze", "palette_pastel", "palette_rainbow", "palette_retro_neon", "palette_warm_sunset",
    "print_color", "print_more",
    "Printer", "ModuleParam", "_addindent", "summarize_repeated_modules",
    "ColorStrategy", "ModuleStyle", "ConstantColorStrategy", "LayerColorStrategy", "TrainableStrategy",
    "TextStyle", "FunctionalStyle", "colorize", "clean_style", "infer_type", "LAYER_SPLITTER", "KeyType", "DelimiterType", "AnyType", "FunctionalType"
]