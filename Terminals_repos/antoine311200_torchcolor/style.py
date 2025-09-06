# torchcolor/style.py

from dataclasses import dataclass, field
from typing import Union, List
import re
from .color import Color
from .gradient import Gradient

LAYER_SPLITTER = re.compile(r"\s*->\s*")
KeyType = str
DelimiterType = str
AnyType = Union[str, int, float]
FunctionalType = Union[Color, Gradient, str, tuple]

@dataclass
class TextStyle:
    fg_style: Union[Gradient, Color, str, tuple] = None
    bg_style: Union[Gradient, Color, str, tuple] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    double_underline: bool = False
    crossed: bool = False
    darken: bool = False

    def __post_init__(self):
        self.fg_style = self._ensure_style(self.fg_style)
        self.bg_style = self._ensure_style(self.bg_style)

    def _ensure_style(self, value):
        if isinstance(value, (Color, Gradient)):
            return value
        elif isinstance(value, str):
            if value.startswith("#") or re.match(r"^[0-9a-fA-F]{6}$", value):
                return Color(value)
            else:
                return Color(value)
        elif isinstance(value, tuple) and len(value) == 3:
            return Color(value)
        else:
            raise ValueError("Invalid style value")

    def apply(self, text):
        fg_code = self.fg_style.to_ansi() if self.fg_style else ""
        bg_code = self.bg_style.to_ansi(is_background=True) if self.bg_style else ""
        style_code = ""
        if self.bold:
            style_code += "\033[1m"
        if self.italic:
            style_code += "\033[3m"
        if self.underline:
            style_code += "\033[4m"
        if self.double_underline:
            style_code += "\033[21m"
        if self.crossed:
            style_code += "\033[9m"
        if self.darken:
            style_code += "\033[2m"
        return f"{bg_code}{fg_code}{style_code}{text}\033[0m"

@dataclass
class FunctionalStyle:
    infer_func: callable = None

    def __post_init__(self):
        self.styles = {}

    def apply(self, text):
        parts = LAYER_SPLITTER.split(text)
        styled_parts = []
        for part in parts:
            style = self.infer_func(part)
            styled_parts.append(style.apply(part))
        return "".join(styled_parts)

def colorize(text, text_color=None, bg_color=None):
    text_color = Color(text_color).to_ansi() if text_color else ""
    bg_color = Color(bg_color).to_ansi(is_background=True) if bg_color else ""
    return f"{bg_color}{text_color}{text}\033[0m"

def clean_style(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)

def infer_type(value):
    if isinstance(value, str):
        return KeyType
    elif isinstance(value, int):
        return DelimiterType
    elif isinstance(value, float):
        return AnyType
    else:
        return FunctionalType