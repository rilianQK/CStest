from textual.binding import Binding

# Vim-style navigation bindings for option lists
VIM_OPTION_LIST_NAVIGATE = [
    Binding("j", "cursor_down", "Down", show=False),
    Binding("k", "cursor_up", "Up", show=False),
    Binding("h", "cursor_left", "Left", show=False),
    Binding("l", "cursor_right", "Right", show=False),
    Binding("gg", "scroll_home", "Home", show=False),
    Binding("G", "scroll_end", "End", show=False),
    Binding("ctrl+d", "scroll_page_down", "Page Down", show=False),
    Binding("ctrl+u", "scroll_page_up", "Page Up", show=False),
]