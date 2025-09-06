from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TYPE_CHECKING
from rich.text import Text

if TYPE_CHECKING:
    from .providers import Provider

class ResourceType(Enum):
    """Define and enumerate different types of resources used in a system, such as general resources, datasources, guides, and functions."""
    RESOURCE = "resource"
    DATASOURCE = "datasource"
    GUIDE = "guide"
    FUNCTION = "function"

@dataclass
class Resource:
    """A resource represents a specific component within a provider, such as a resource, data source, function, or guide."""
    
    name: str
    type: ResourceType
    provider: 'Provider'
    content: Optional[str] = None
    
    def __str__(self) -> str:
        """Return a formatted string representation of the object, displaying its type and name with cyan-colored type abbreviation."""
        type_abbr = {
            ResourceType.RESOURCE: "R",
            ResourceType.DATASOURCE: "D",
            ResourceType.FUNCTION: "F",
            ResourceType.GUIDE: "G"
        }.get(self.type, "?")
        
        return f"[cyan]{type_abbr}[/cyan] {self.name}"
    
    def __rich__(self) -> Text:
        """Provide a string representation of the object for rich display in environments that support rich text rendering, such as Jupyter notebooks or rich terminal output."""
        return Text.from_markup(str(self))
    
    def __lt__(self, other: 'Resource') -> bool:
        """Compare two Resource objects based on their name attribute to determine if the current object's name is lexicographically less than the other object's name."""
        return self.name < other.name
    
    def __gt__(self, other: 'Resource') -> bool:
        """Compare two Resource objects based on their names to determine if the current object's name is lexicographically greater than the other object's name."""
        return self.name > other.name
    
    def __hash__(self) -> int:
        """Generate a unique hash value for an object based on its provider's name, type, and name attributes."""
        return hash((self.provider.name, self.type.value, self.name))