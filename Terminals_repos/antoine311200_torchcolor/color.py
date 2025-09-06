# torchcolor/color.py

from dataclasses import dataclass
import re

@dataclass
class Color:
    value: str

    def to_ansi(self, is_background=False):
        if isinstance(self.value, str):
            if self.value.startswith("#"):
                r, g, b = self.to_rgb()
                return f"\033[{48 if is_background else 38};2;{r};{g};{b}m"
            else:
                return f"\033[{48 if is_background else 38};5;{self.value}m"
        elif isinstance(self.value, tuple):
            r, g, b = self.value
            return f"\033[{48 if is_background else 38};2;{r};{g};{b}m"
        else:
            raise ValueError("Invalid color value")

    def to_rgb(self):
        if isinstance(self.value, str) and self.value.startswith("#"):
            hex_color = self.value.lstrip("#")
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        elif isinstance(self.value, tuple) and len(self.value) == 3:
            return self.value
        else:
            raise ValueError("Invalid color value")

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def is_rgb(color):
    return isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)

background_colors = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}

foreground_colors = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

reset_color = "\033[0m"