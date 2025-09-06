from textual.widgets import OptionList
from textual.binding import Binding
from textual import events
from rich.text import Text
from typing import Dict, Optional, List
import logging
import json

from ..data.providers import Provider
from .keybindings import VIM_OPTION_LIST_NAVIGATE

LOGGER = logging.getLogger(__name__)

class ProvidersOptionList(OptionList):
    """A class that manages and displays a list of providers, allowing selection and loading of provider-specific resources, with fallback support when the primary data source is unavailable."""
    
    BINDINGS = VIM_OPTION_LIST_NAVIGATE + [
        Binding("enter", "select_cursor", "Select", show=True),
        Binding("escape", "close", "Close", show=True),
    ]
    
    def __init__(self, **kwargs):
        """Initialize a navigation provider component with specific attributes including name, ID, CSS classes, and a border title."""
        super().__init__(**kwargs)
        self.border_title = "Providers"
        self.border_subtitle = "0 providers"
        self.name = "nav-providers"
        self.id = "nav-providers"
        self.add_class("nav-selector")
        self.add_class("bordered")
    
    def load_index(self) -> Dict[str, Provider]:
        """Load the provider index from the registry API or fallback data."""
        try:
            from ..data.helpers import get_registry_api
            data = get_registry_api("", json=True, log_widget=None)
            
            providers = {}
            for item in data.get('providers', []):
                provider = Provider.from_json(item)
                providers[provider.display_name] = provider
            
            return providers
        except Exception as e:
            LOGGER.error(f"Failed to load provider index: {e}")
            
            # Fallback to static data if available
            try:
                from ..fallback import providers as fallback_providers
                providers = {}
                for item in fallback_providers.PROVIDERS_DATA:
                    provider = Provider.from_json(item)
                    providers[provider.display_name] = provider
                return providers
            except ImportError:
                LOGGER.error("No fallback providers available")
                return {}
    
    def populate(self, providers: Optional[List[Provider]] = None) -> None:
        """Populate the instance with options from specified providers or all available providers if none are specified, update the border subtitle with the count of selected providers, and clear existing options before adding new ones."""
        self.clear_options()
        
        if providers is None:
            providers_dict = self.load_index()
            providers = list(providers_dict.values())
        
        # Sort providers by popularity (descending)
        providers.sort(key=lambda p: p.popularity, reverse=True)
        
        for provider in providers:
            display_text = Text.assemble(
                (f"{provider.display_name}", "bold"),
                f" ({provider.popularity:,} downloads)"
            )
            self.add_option(display_text, id=provider.display_name)
        
        self.border_subtitle = f"{len(providers)} providers"
    
    def on_option_selected(self, event: events.OptionSelected) -> None:
        """Handle option selection by emitting a message with the selected provider."""
        if event.option_id:
            self.post_message(events.OptionSelected(self, event.option_id))