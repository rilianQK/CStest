# torchcolor/palette.py

from dataclasses import dataclass, field
from typing import List, Dict, ClassVar
from .color import Color

@dataclass
class Palette:
    name: str
    colors: List[Color]
    _registry: ClassVar[Dict[str, "Palette"]] = {}
    disable_registry: bool = False

    def __post_init__(self):
        if not self.disable_registry:
            self._registry[self.name] = self

    @classmethod
    def get_palette(cls, name):
        return cls._registry.get(name)

    def __getitem__(self, index):
        return self.colors[index % len(self.colors)]

    def generate_gradient(self, n):
        if n <= 1:
            return [self.colors[0]]
        gradient = []
        for i in range(n):
            idx = int(i * (len(self.colors) - 1) / (n - 1))
            gradient.append(self.colors[idx])
        return gradient

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

palette_autumn_foliage = Palette(
    name="autumn_foliage",
    colors=[
        Color("#FF4500"), Color("#FF8C00"), Color("#FFD700"), Color("#ADFF2F"),
        Color("#32CD32"), Color("#00FF00"), Color("#00FA9A"), Color("#00CED1"),
        Color("#1E90FF"), Color("#0000FF"), Color("#8A2BE2"), Color("#FF1493"),
        Color("#FF69B4"), Color("#FFB6C1"), Color("#FFC0CB")
    ]
)

palette_forest_greens = Palette(
    name="forest_greens",
    colors=[
        Color("#228B22"), Color("#2E8B57"), Color("#3CB371"), Color("#66CDAA"),
        Color("#8FBC8F"), Color("#20B2AA"), Color("#5F9EA0"), Color("#4682B4"),
        Color("#B0C4DE"), Color("#B0E0E6"), Color("#ADD8E6"), Color("#87CEEB"),
        Color("#87CEFA"), Color("#00BFFF"), Color("#1E90FF")
    ]
)

palette_lavender_dreams = Palette(
    name="lavender_dreams",
    colors=[
        Color("#E6E6FA"), Color("#D8BFD8"), Color("#DDA0DD"), Color("#EE82EE"),
        Color("#DA70D6"), Color("#FF00FF"), Color("#BA55D3"), Color("#9932CC"),
        Color("#9400D3"), Color("#8A2BE2"), Color("#8B008B"), Color("#800080"),
        Color("#9370DB"), Color("#7B68EE"), Color("#6A5ACD")
    ]
)

palette_monochrome = Palette(
    name="monochrome",
    colors=[
        Color("#000000"), Color("#2F4F4F"), Color("#696969"), Color("#808080"),
        Color("#A9A9A9"), Color("#C0C0C0"), Color("#D3D3D3"), Color("#DCDCDC"),
        Color("#F5F5F5"), Color("#FFFFFF")
    ]
)

palette_ocean_breeze = Palette(
    name="ocean_breeze",
    colors=[
        Color("#00CED1"), Color("#20B2AA"), Color("#48D1CC"), Color("#40E0D0"),
        Color("#00FFFF"), Color("#7FFFD4"), Color("#66CDAA"), Color("#5F9EA0"),
        Color("#4682B4"), Color("#B0C4DE"), Color("#B0E0E6"), Color("#ADD8E6"),
        Color("#87CEEB"), Color("#87CEFA"), Color("#00BFFF")
    ]
)

palette_pastel = Palette(
    name="pastel",
    colors=[
        Color("#FFB6C1"), Color("#FFDAB9"), Color("#E6E6FA"), Color("#FFFACD"),
        Color("#FFE4E1"), Color("#F0FFF0"), Color("#F5FFFA"), Color("#F0F8FF"),
        Color("#E0FFFF"), Color("#F5F5DC"), Color("#FFF5EE"), Color("#F8F8FF"),
        Color("#F0FFFF"), Color("#FAFAD2"), Color("#FFEFD5")
    ]
)

palette_rainbow = Palette(
    name="rainbow",
    colors=[
        Color("#FF0000"), Color("#FF7F00"), Color("#FFFF00"), Color("#00FF00"),
        Color("#0000FF"), Color("#4B0082"), Color("#8B00FF")
    ]
)

palette_retro_neon = Palette(
    name="retro_neon",
    colors=[
        Color("#FF1493"), Color("#FF69B4"), Color("#FFB6C1"), Color("#FFC0CB"),
        Color("#DB7093"), Color("#FF4500"), Color("#FF6347"), Color("#FF7F50"),
        Color("#FF8C00"), Color("#FFA07A"), Color("#FFD700"), Color("#FFFF00"),
        Color("#ADFF2F"), Color("#7FFF00"), Color("#7CFC00")
    ]
)

palette_warm_sunset = Palette(
    name="warm_sunset",
    colors=[
        Color("#FF4500"), Color("#FF6347"), Color("#FF7F50"), Color("#FF8C00"),
        Color("#FFA07A"), Color("#FFD700"), Color("#FFFF00"), Color("#ADFF2F"),
        Color("#7FFF00"), Color("#7CFC00"), Color("#00FF00"), Color("#32CD32"),
        Color("#00FA9A"), Color("#00FF7F"), Color("#00FF00")
    ]
)