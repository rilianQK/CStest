from textual.widgets import MarkdownViewer
from textual.binding import Binding
from textual import events
from rich.syntax import Syntax
from rich.text import Text
from typing import Any, List, Dict
import re

from ..data.helpers import CODEBLOCK_REGEX
from .code_block_select import CodeBlockSelect

class ContentWindow(MarkdownViewer):
    """A Markdown viewer class with navigation controls, content display, and interactive features like table of contents toggling and code block copying."""
    
    BINDINGS = [
        Binding("up", "up", "Up", show=True),
        Binding("down", "down", "Down", show=True),
        Binding("pageup", "page_up", "Page Up", show=True),
        Binding("pagedown", "page_down", "Page Down", show=True),
        Binding("home", "scroll_home", "Home", show=True),
        Binding("end", "scroll_end", "End", show=True),
        Binding("t", "toggle_toc", "Toggle TOC", show=True),
        Binding("y", "yank", "Yank Code", show=True),
    ]
    
    ALLOW_MAXIMIZE = True
    
    def __init__(self, content: Any = "", **kwargs):
        """Initialize the content window with the given content."""
        super().__init__(content, **kwargs)
        self.show_table_of_contents = True
        self.border_title = "Content"
    
    def action_up(self) -> None:
        """Scroll the document up by one unit."""
        self.scroll_up()
    
    def action_down(self) -> None:
        """Scroll the document down by one unit."""
        self.scroll_down()
    
    def action_page_up(self) -> None:
        """Move the document view up by one page."""
        self.scroll_page_up()
    
    def action_page_down(self) -> None:
        """Move the view of the document down by one page."""
        self.scroll_page_down()
    
    def action_scroll_home(self) -> None:
        """Scroll the document to the home position (typically the top of the document)."""
        self.scroll_home()
    
    def action_scroll_end(self) -> None:
        """Scroll the document to the end of its content."""
        self.scroll_end()
    
    def action_toggle_toc(self) -> None:
        """Toggle the visibility of the table of contents, update its border title if empty, and manage focus between the table of contents and the document."""
        self.show_table_of_contents = not self.show_table_of_contents
        self.refresh()
    
    def action_yank(self) -> None:
        """Extract and display code blocks from the content in a selector widget for user interaction."""
        content = self.document.plain_text if hasattr(self, 'document') and self.document else ""
        
        if not content:
            self.notify("No content available to extract code blocks from", title="Warning")
            return
        
        code_blocks = []
        matches = CODEBLOCK_REGEX.findall(content)
        
        for match in matches:
            code_block = match.strip()
            if code_block:
                # Try to detect language from the code block
                language = self._detect_language(code_block)
                code_blocks.append({
                    'code': code_block,
                    'language': language
                })
        
        if not code_blocks:
            self.notify("No code blocks found in the content", title="Info")
            return
        
        # Create and show code block selector
        code_block_selector = CodeBlockSelect()
        code_block_selector.set_new_options(code_blocks)
        code_block_selector._code_blocks = code_blocks  # Store for later access
        
        # Add to the screen
        if self.app and hasattr(self.app, 'mount'):
            self.app.mount(code_block_selector)
            code_block_selector.focus()
    
    def _detect_language(self, code: str) -> str:
        """Detect the programming language of a code block."""
        # Simple language detection based on common patterns
        lines = code.split('\n')
        first_line = lines[0].strip() if lines else ""
        
        if first_line.startswith('#!'):
            if 'python' in first_line:
                return 'python'
            elif 'bash' in first_line or 'sh' in first_line:
                return 'bash'
        
        # Check for common language patterns
        if any(keyword in code for keyword in ['terraform', 'provider', 'resource', 'data']):
            return 'hcl'
        elif any(keyword in code for keyword in ['package', 'import', 'class', 'def ']):
            return 'python'
        elif any(keyword in code for keyword in ['function', 'const ', 'let ', 'var ']):
            return 'javascript'
        elif any(keyword in code for keyword in ['<?php', 'echo ', '$']):
            return 'php'
        elif any(keyword in code for keyword in ['<html', '<div', '<span']):
            return 'html'
        
        return 'text'
    
    def update(self, markdown: Any) -> None:
        """Update the content of the document with the provided markdown text and synchronize the changes with the associated document object."""
        self.document = self._parse_markdown(markdown)
        self.refresh()
    
    def go(self, location: Any) -> None:
        """Without this, the Markdown viewer would try to open a file on a disk, while the Markdown itself will open a browser link (desired)"""
        # This method is intentionally left empty to prevent file system operations
        # and allow browser links to work normally in the markdown content
        pass