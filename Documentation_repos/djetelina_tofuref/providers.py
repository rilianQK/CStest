from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from pathlib import Path
import json
from .helpers import get_registry_api, header_markdown_split
from .resources import Resource, ResourceType

@dataclass
class Provider:
    """The Provider class represents a provider in a registry system, managing metadata, versions, resources, and interactions with the registry API for a specific provider."""
    
    organization: str
    name: str
    description: str
    fork_of: Optional[str] = None
    popularity: int = 0
    log_widget: Optional[Any] = None
    raw_json: Optional[Dict] = None
    
    _active_version: Optional[str] = None
    _overview: Optional[str] = None
    
    versions: List[Dict[str, str]] = field(default_factory=list)
    resources: List[Resource] = field(default_factory=list)
    datasources: List[Resource] = field(default_factory.list)
    functions: List[Resource] = field(default_factory.list)
    guides: List[Resource] = field(default_factory.list)
    
    @property
    def display_name(self) -> str:
        """Return a formatted string combining the organization and name attributes in the format \"organization/name\"."""
        return f"{self.organization}/{self.name}"
    
    @property
    def _endpoint(self) -> str:
        """Construct and return a formatted endpoint string using the organization name, repository name, and active version."""
        return f"{self.organization}/{self.name}/{self.active_version}"
    
    @property
    def active_version(self) -> str:
        """Retrieve the currently active version ID, initializing it to the first version's ID if not already set."""
        if self._active_version is None and self.versions:
            self._active_version = self.versions[0].get('version', '')
        return self._active_version or ''
    
    @active_version.setter
    def active_version(self, value: str) -> None:
        """Set the active version."""
        self._active_version = value
    
    @property
    def overview(self) -> str:
        """Get the provider overview documentation."""
        if self._overview is None:
            try:
                endpoint = f"{self.organization}/{self.name}/{self.active_version}/docs"
                content = get_registry_api(endpoint, json=False, log_widget=self.log_widget)
                _, markdown_content = header_markdown_split(content)
                self._overview = markdown_content
            except Exception as e:
                if self.log_widget:
                    self.log_widget.write(f"Failed to fetch overview for {self.display_name}: {e}")
                self._overview = f"# {self.display_name}\n\n{self.description}\n\n*Failed to load detailed documentation*"
        return self._overview
    
    @property
    def use_configuration(self) -> str:
        """Get the provider configuration snippet."""
        return f"""terraform {{
  required_providers {{
    {self.name} = {{
      source  = "{self.organization}/{self.name}"
      version = "~> {self.active_version}"
    }}
  }}
}}

provider "{self.name}" {{
  # Configuration options
}}
"""
    
    def __rich__(self) -> str:
        """Convert the object's attributes (excluding \"raw_json\" and \"versions\") into a JSON-formatted string wrapped in a `RICH_JSON` type for rich display purposes."""
        from rich.json import JSON
        data = {
            'organization': self.organization,
            'name': self.name,
            'description': self.description,
            'fork_of': self.fork_of,
            'popularity': self.popularity,
            'active_version': self.active_version,
            'display_name': self.display_name
        }
        return JSON(json.dumps(data))
    
    def load_resources(self) -> None:
        """Load all resources for the provider."""
        try:
            endpoint = f"{self.organization}/{self.name}/{self.active_version}/docs"
            content = get_registry_api(endpoint, json=False, log_widget=self.log_widget)
            _, markdown_content = header_markdown_split(content)
            
            # Parse resources from markdown content
            # This is a simplified implementation - actual parsing would be more complex
            lines = markdown_content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('## '):
                    current_section = line[3:].lower()
                elif line.startswith('### ') and current_section:
                    resource_name = line[4:].strip()
                    resource_type = self._get_resource_type(current_section, resource_name)
                    
                    if resource_type:
                        resource = Resource(
                            name=resource_name,
                            type=resource_type,
                            provider=self,
                            content=line + "\n\n" + self._get_resource_content(resource_name)
                        )
                        
                        if resource_type == ResourceType.RESOURCE:
                            self.resources.append(resource)
                        elif resource_type == ResourceType.DATASOURCE:
                            self.datasources.append(resource)
                        elif resource_type == ResourceType.FUNCTION:
                            self.functions.append(resource)
                        elif resource_type == ResourceType.GUIDE:
                            self.guides.append(resource)
            
        except Exception as e:
            if self.log_widget:
                self.log_widget.write(f"Failed to load resources for {self.display_name}: {e}")
    
    def _get_resource_type(self, section: str, resource_name: str) -> Optional[ResourceType]:
        """Determine the resource type based on section and name."""
        section_lower = section.lower()
        if 'resource' in section_lower:
            return ResourceType.RESOURCE
        elif 'data' in section_lower or 'datasource' in section_lower:
            return ResourceType.DATASOURCE
        elif 'function' in section_lower:
            return ResourceType.FUNCTION
        elif 'guide' in section_lower or 'example' in section_lower:
            return ResourceType.GUIDE
        return None
    
    def _get_resource_content(self, resource_name: str) -> str:
        """Get content for a specific resource."""
        # This would typically make additional API calls
        return f"Documentation for {resource_name}\n\nAdditional details would be fetched from the API."
    
    @classmethod
    def from_json(cls, data: Dict) -> 'Provider':
        """Convert a JSON dictionary into a Provider object by extracting and mapping specific fields from the input data."""
        return cls(
            organization=data.get('namespace', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            fork_of=data.get('fork_of'),
            popularity=data.get('downloads', 0),
            raw_json=data,
            versions=data.get('versions', [])
        )