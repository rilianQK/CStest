#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
import json

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, OptionList, MarkdownViewer, Input, RichLog, Static
)
from textual import events
from textual.screen import Screen
from rich.syntax import Syntax
from rich.text import Text
import pyperclip
import requests
from datetime import datetime, timedelta
import re

from .data.helpers import (
    cached_file_path, get_from_cache, save_to_cache, get_registry_api, header_markdown_split, is_provider_index_expired
)
from .data.providers import Provider
from .data.resources import Resource, ResourceType
from .widgets.code_block_select import CodeBlockSelect
from .widgets.content_window import ContentWindow
from .widgets.custom_rich_log import CustomRichLog
from .widgets.keybindings import VIM_OPTION_LIST_NAVIGATE
from .widgets.providers_option_list import ProvidersOptionList
from .widgets.resources_option_list import ResourcesOptionList
from .widgets.search_input import SearchInput

# Set up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class TofuRefApp(App):
    CSS_PATH = None
    TITLE = "TofuRef - OpenTofu Provider Reference"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f1", "providers", "Providers", show=True),
        Binding("f2", "resources", "Resources", show=True),
        Binding("f3", "content", "Content", show=True),
        Binding("f4", "log", "Log", show=True),
        Binding("f5", "fullscreen", "Fullscreen", show=True),
        Binding("f6", "search", "Search", show=True),
        Binding("f7", "version", "Version", show=True),
        Binding("f8", "use", "Use", show=True),
    ]
    ESCAPE_TO_MINIMIZE = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.providers = {}
        self.active_provider = None
        self.active_resource = None
        self.fullscreen_mode = False
        self.log_widget = None
        self.navigation_providers = None
        self.navigation_resources = None
        self.content_markdown = None
        self.search = None
        self.code_block_selector = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal():
            with Vertical(id="sidebar"):
                self.navigation_providers = ProvidersOptionList()
                yield self.navigation_providers
                self.navigation_resources = ResourcesOptionList()
                yield self.navigation_resources
            
            with Vertical(id="main-content"):
                self.content_markdown = ContentWindow()
                yield self.content_markdown
        
        self.log_widget = CustomRichLog()
        yield self.log_widget
        
        yield Footer()
    
    def on_mount(self) -> None:
        self._preload()
    
    def _preload(self) -> None:
        self.log_widget.write("Loading provider index...")
        self.providers = self.navigation_providers.load_index()
        self.navigation_providers.populate(list(self.providers.values()))
        self.log_widget.write(f"Loaded {len(self.providers)} providers")
    
    def action_providers(self) -> None:
        if self.navigation_providers:
            self.navigation_providers.focus()
    
    def action_resources(self) -> None:
        if self.navigation_resources:
            self.navigation_resources.focus()
    
    def action_content(self) -> None:
        if self.content_markdown:
            self.content_markdown.focus()
    
    def action_log(self) -> None:
        if self.log_widget:
            self.log_widget.display = not self.log_widget.display
            self.log_widget.refresh()
    
    def action_fullscreen(self) -> None:
        self.fullscreen_mode = not self.fullscreen_mode
        if self.fullscreen_mode:
            self.log_widget.write("Entering fullscreen mode")
        else:
            self.log_widget.write("Exiting fullscreen mode")
    
    def action_search(self) -> None:
        search_input = SearchInput()
        self.mount(search_input)
        search_input.focus()
    
    def action_version(self) -> None:
        if self.active_provider:
            self.log_widget.write(f"Version action for {self.active_provider.display_name}")
    
    def action_use(self) -> None:
        if self.active_provider:
            config = self.active_provider.use_configuration
            pyperclip.copy(config)
            self.notify("Configuration copied to clipboard!", title="Success")
    
    def on_option_list_option_selected(self, event: events.OptionSelected) -> None:
        if event.option_list == self.navigation_providers:
            provider_name = event.option_id
            if provider_name in self.providers:
                self.active_provider = self.providers[provider_name]
                self.log_widget.write(f"Selected provider: {provider_name}")
                self.navigation_resources.populate(self.active_provider)
                self.content_markdown.update(self.active_provider.overview)
        
        elif event.option_list == self.navigation_resources:
            if self.active_provider:
                resource_name = event.option_id
                self.log_widget.write(f"Selected resource: {resource_name}")
                
                all_resources = (
                    self.active_provider.resources +
                    self.active_provider.datasources +
                    self.active_provider.functions +
                    self.active_provider.guides
                )
                
                for resource in all_resources:
                    if resource.name == resource_name:
                        self.content_markdown.update(resource.content or f"# {resource_name}\n\nNo content available")
                        break
    
    def on_search_input_changed(self, event: events.Changed) -> None:
        query = event.value.lower()
        if not query:
            if self.navigation_providers.has_focus:
                self.navigation_providers.populate(list(self.providers.values()))
            return
        
        if self.navigation_providers.has_focus:
            filtered_providers = [
                p for p in self.providers.values()
                if query in p.display_name.lower() or query in p.description.lower()
            ]
            self.navigation_providers.populate(filtered_providers)
        
        elif self.navigation_resources.has_focus and self.active_provider:
            all_resources = (
                self.active_provider.resources +
                self.active_provider.datasources +
                self.active_provider.functions +
                self.active_provider.guides
            )
            filtered_resources = [
                r for r in all_resources
                if query in r.name.lower()
            ]
            self.navigation_resources.populate(self.active_provider, filtered_resources)
    
    def on_search_input_submitted(self, event: events.Submitted) -> None:
        if self.search and self.search.parent:
            self.search.parent.remove_widget(self.search)
        self.set_focus(None)

def main() -> None:
    app = TofuRefApp()
    app.run()

if __name__ == "__main__":
    main()