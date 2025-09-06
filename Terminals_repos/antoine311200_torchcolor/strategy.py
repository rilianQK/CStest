# torchcolor/strategy.py

from .style import TextStyle, FunctionalStyle
from .color import Color
from .gradient import Gradient

class ColorStrategy:
    _registry = {}

    @classmethod
    def get_strategy(cls, key, *args, **kwargs):
        if key in cls._registry:
            return cls._registry[key](*args, **kwargs)
        else:
            raise ValueError(f"Strategy {key} not registered")

    @classmethod
    def available_strategies(cls):
        return list(cls._registry.keys())

    @classmethod
    def create(cls, key, *args, **kwargs):
        return cls.get_strategy(key, *args, **kwargs)

    def get_style(self, module, params):
        raise NotImplementedError

    @classmethod
    def register(cls, key):
        def decorator(strategy_cls):
            cls._registry[key] = strategy_cls
            return strategy_cls
        return decorator

@ColorStrategy.register("constant")
class ConstantColorStrategy(ColorStrategy):
    def __init__(self, color=""):
        self.color = color

    def get_style(self, module, config):
        return ModuleStyle(
            name_style=TextStyle(fg_style=Color(self.color), italic=True, double_underline=True),
            layer_style=TextStyle(fg_style=Color(self.color)),
            extra_style=TextStyle(fg_style=Color(self.color))
        )

@ColorStrategy.register("layer")
class LayerColorStrategy(ColorStrategy):
    def get_style(self, module, config):
        return ModuleStyle(
            name_style=TextStyle(fg_style=Color("blue")),
            layer_style=TextStyle(fg_style=Color("green")),
            extra_style=TextStyle(fg_style=Color("yellow"))
        )

@ColorStrategy.register("trainable")
class TrainableStrategy(ColorStrategy):
    def get_style(self, module, config):
        if config.get("is_root", False):
            return ModuleStyle(
                name_style=TextStyle(fg_style=Color("red")),
                layer_style=TextStyle(fg_style=Color("red")),
                extra_style=TextStyle(fg_style=Color("red"))
            )
        elif any(p.requires_grad for p in module.parameters()):
            return ModuleStyle(
                name_style=TextStyle(fg_style=Color("green")),
                layer_style=TextStyle(fg_style=Color("green")),
                extra_style=TextStyle(fg_style=Color("green"))
            )
        else:
            return ModuleStyle(
                name_style=TextStyle(fg_style=Color("yellow")),
                layer_style=TextStyle(fg_style=Color("yellow")),
                extra_style=TextStyle(fg_style=Color("yellow"))
            )

class ModuleStyle:
    def __init__(self, name_style, layer_style, extra_style):
        self.name_style = name_style
        self.layer_style = layer_style
        self.extra_style = extra_style