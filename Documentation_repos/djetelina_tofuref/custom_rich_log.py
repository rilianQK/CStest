from textual.widgets import RichLog
from textual.containers import Container
from textual import events
from rich.text import Text
from rich.console import RenderableType
from typing import Optional

class CustomRichLog(RichLog):
    """A custom rich log display widget with bordered styling, markup support, and versioned subtitle for application logging."""
    
    def __init__(self, **kwargs):
        """Initialize a log widget with a bordered style, title, subtitle, and hidden display, inheriting from a parent class and allowing additional keyword arguments for customization."""
        super().__init__(**kwargs)
        self.border_title = "Log"
        self.border_subtitle = "v0.1.0"
        self.display = False
    
    def write(self, content: RenderableType) -> None:
        """Write content to the log with rich formatting support."""
        super().write(content)
    
    def clear(self) -> None:
        """Clear all content from the log."""
        super().clear()