# torchcolor/gradient.py

from dataclasses import dataclass, field
from typing import List, Union
from .palette import Palette
from .color import Color

@dataclass
class GradientChunk:
    start: int
    end: int
    color: Color

@dataclass
class Gradient:
    interpolate: bool = True
    repeat: bool = True
    reverse: bool = False
    window_size: int = 1

    def __post_init__(self):
        pass

    def _ensure_palette(self, palette):
        if isinstance(palette, Palette):
            return palette
        elif isinstance(palette, str):
            return Palette.get(palette)
        else:
            raise ValueError("Invalid palette type")

    def apply(self, palette, text):
        palette = self._ensure_palette(palette)
        length = len(text)
        colors = palette.generate_gradient(length)
        if self.reverse:
            colors = colors[::-1]
        chunks = []
        for i, char in enumerate(text):
            color = colors[i % len(colors)] if self.repeat else colors[i]
            chunks.append(GradientChunk(start=i, end=i+1, color=color))
        return chunks