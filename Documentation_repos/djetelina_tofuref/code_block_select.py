from textual.widgets import OptionList
from textual.binding import Binding
from textual import events
from rich.syntax import Syntax
from rich.text import Text
from typing import Any, List, Dict
import pyperclip

from ..data.helpers import CODEBLOCK_REGEX

class CodeBlockSelect(OptionList):
    """A class for selecting and copying code blocks from a list of options, displaying them with syntax highlighting, and providing clipboard functionality."""
    
    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
        Binding("y", "yank", "Yank", show=True),
    ]
    
    def __init__(self, **kwargs):
        """Initialize a CodeBlocks widget with a default name, ID, and CSS classes, and set a border title for the widget."""
        super().__init__(**kwargs)
        self.border_title = "Code Blocks"
        self.highlighted = None
    
    def action_close(self) -> None:
        """Close the current window by minimizing or maximizing it based on the fullscreen mode, then remove it from the parent container."""
        if self.parent:
            self.parent.remove_widget(self)
    
    def set_new_options(self, code_blocks: List[Dict[str, str]]) -> None:
        """Replace the current options in the object with new code blocks, each displayed with syntax highlighting and grouped under labeled sections, then reset the focus and highlighting to the first option."""
        self.clear_options()
        
        if not code_blocks:
            self.add_option("No code blocks found")
            return
        
        for i, block in enumerate(code_blocks):
            code = block.get('code', '')
            language = block.get('language', '')
            
            try:
                syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                display_text = Text.assemble(
                    f"[{i+1}] ",
                    (f"{language}: " if language else ""),
                    syntax
                )
            except:
                display_text = f"[{i+1}] {code[:50]}..." if len(code) > 50 else f"[{i+1}] {code}"
            
            self.add_option(display_text, id=str(i))
        
        self.highlighted = 0
        if self.option_count > 0:
            self.highlighted = 0
    
    def on_option_selected(self, event: events.OptionSelected) -> None:
        """Handle option selection by copying the selected code block to clipboard."""
        if event.option_id is not None:
            try:
                index = int(event.option_id)
                if hasattr(self, '_code_blocks') and index < len(self._code_blocks):
                    code_block = self._code_blocks[index]
                    code = code_block.get('code', '')
                    pyperclip.copy(code)
                    self.notify("Code copied to clipboard!", title="Success")
            except (ValueError, IndexError):
                pass
    
    def action_yank(self) -> None:
        """Copy the currently highlighted code block to clipboard."""
        if self.highlighted is not None and hasattr(self, '_code_blocks'):
            try:
                code_block = self._code_blocks[self.highlighted]
                code = code_block.get('code', '')
                pyperclip.copy(code)
                self.notify("Code copied to clipboard!", title="Success")
            except IndexError:
                pass