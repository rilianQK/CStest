from textual.widgets import OptionList
from textual.binding import Binding
from textual import events
from rich.text import Text
from typing import Optional, List, TYPE_CHECKING

from .keybindings import VIM_OPTION_LIST_NAVIGATE

if TYPE_CHECKING:
    from ..data.providers import Provider
    from ..data.resources import Resource

class ResourcesOptionList(OptionList):
    """A class for managing and displaying a list of resources from a provider, with navigation and selection capabilities, and integration with a markdown content viewer."""
    
    BINDINGS = VIM_OPTION_LIST_NAVIGATE + [
        Binding("enter", "select_cursor", "Select", show=True),
        Binding("escape", "close", "Close", show=True),
    ]
    
    def __init__(self, **kwargs):
        """Initialize a navigation element with the name \"Resources\", ID \"nav-resources\", and CSS classes \"nav-selector bordered\", and set its border title to \"Resources\"."""
        super().__init__(**kwargs)
        self.border_title = "Resources"
        self.border_subtitle = "0 resources"
        self.name = "nav-resources"
        self.id = "nav-resources"
        self.add_class("nav-selector")
        self.add_class("bordered")
        self.highlighted = None
        self.loading = False
    
    def populate(self, provider: 'Provider', resources: Optional[List['Resource']] = None) -> None:
        """Populate the object with provider information and associated resources, setting the border subtitle and adding resource options either from the provider or a provided list."""
        self.clear_options()
        
        if resources is None:
            if not provider.resources and not provider.datasources and not provider.functions and not provider.guides:
                provider.load_resources()
            
            resources = []
            resources.extend(provider.resources)
            resources.extend(provider.datasources)
            resources.extend(provider.functions)
            resources.extend(provider.guides)
        
        # Sort resources by name
        resources.sort()
        
        for resource in resources:
            self.add_option(str(resource), id=resource.name)
        
        self.border_subtitle = f"{len(resources)} resources"
    
    def load_provider_resources(self, provider: 'Provider') -> None:
        """Load resources for a specific provider and populate the option list."""
        self.loading = True
        self.border_subtitle = "Loading..."
        
        try:
            provider.load_resources()
            self.populate(provider)
        except Exception as e:
            self.clear_options()
            self.add_option(f"Failed to load resources: {e}")
            self.border_subtitle = "Error"
        finally:
            self.loading = False
    
    def on_option_selected(self, event: events.OptionSelected) -> None:
        """Handle option selection by emitting a message with the selected resource."""
        if event.option_id:
            self.post_message(events.OptionSelected(self, event.option_id))