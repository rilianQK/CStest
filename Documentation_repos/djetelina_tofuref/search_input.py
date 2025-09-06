from textual.widgets import Input
from textual.binding import Binding
from textual import events
from typing import Optional

class SearchInput(Input):
    """A specialized input widget for search functionality with escape key binding to close the panel and emit change/submitted events."""
    
    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
    ]
    
    def __init__(self, **kwargs):
        """Initialize a search input field with a placeholder, ID, CSS classes, and a border title, allowing for additional customization through keyword arguments."""
        super().__init__(placeholder="Search...", id="search-input", **kwargs)
        self.border_title = "Search"
        self.add_class("search-input")
    
    def action_close(self) -> None:
        """Close the current action by posting Changed and Submitted messages with empty strings and None as values."""
        self.post_message(events.Changed(self, ""))
        self.post_message(events.Submitted(self, None))
        self.value = ""
        if self.parent:
            self.parent.remove_widget(self)