# torchcolor/print.py

from .color import Color, reset_color
from .style import TextStyle

def print_color(text, text_color=None, bg_color=None):
    """
    Print the given text with specified text color and background color using ANSI color codes.
    """
    if text_color:
        text_color = Color(text_color).to_ansi()
    else:
        text_color = ""
    
    if bg_color:
        bg_color = Color(bg_color).to_ansi(is_background=True)
    else:
        bg_color = ""
    
    print(f"{bg_color}{text_color}{text}{reset_color}")

def print_more(*args, **kwargs):
    """
    Print a sequence of strings and styled text segments with customizable separation, where strings are concatenated
    and styled text segments are formatted according to their specified styles before being joined and printed.
    """
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    styled_texts = []
    
    for arg in args:
        if isinstance(arg, TextStyle):
            styled_texts.append(arg.apply(arg.text))
        else:
            styled_texts.append(str(arg))
    
    print(sep.join(styled_texts), end=end)