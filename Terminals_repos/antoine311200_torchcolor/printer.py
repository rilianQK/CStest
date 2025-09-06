# torchcolor/printer.py

from .strategy import ColorStrategy
from .style import TextStyle, FunctionalStyle

def _addindent(s_, numSpaces):
    s = s_.split('\n')
    if len(s) == 1:
        return s_
    return s[0] + '\n' + '\n'.join(' ' * numSpaces + line for line in s[1:])

def summarize_repeated_modules(lines):
    summarized_lines = []
    previous_line = None
    count = 1

    for line in lines:
        if line == previous_line:
            count += 1
        else:
            if count > 1:
                summarized_lines.append(f"{previous_line} (x{count})")
            else:
                summarized_lines.append(previous_line)
            previous_line = line
            count = 1

    if count > 1:
        summarized_lines.append(f"{previous_line} (x{count})")
    else:
        summarized_lines.append(previous_line)

    return summarized_lines

class ModuleParam:
    pass

class Printer:
    def __init__(self, strategy):
        self.strategy = strategy

    def print(self, module, display_depth=False, display_legend=False):
        lines = self.repr_module(module, display_depth, indent=0)
        if display_legend:
            lines.append(self.strategy.get_legend())
        lines = summarize_repeated_modules(lines)
        for line in lines:
            print(line)

    def repr_module(self, parent_module, display_depth, indent):
        lines = []
        for name, module in parent_module.named_children():
            style = self.strategy.get_style(module, {"is_root": False})
            line = f"{name}: {module.__class__.__name__}"
            if display_depth:
                line += f" (depth: {indent})"
            lines.append(_addindent(style.apply(line), indent))
            lines.extend(self.repr_module(module, display_depth, indent + 2))
        return lines

    def set_strategy(self, strategy, *args, **kwargs):
        self.strategy = ColorStrategy.create(strategy, *args, **kwargs)