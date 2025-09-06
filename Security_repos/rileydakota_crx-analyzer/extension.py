import os
import tempfile
import zipfile
import json
import hashlib
from enum import Enum
from typing import Optional, List, Dict, Any
from pathlib import Path

from .download import get_chrome_extension_url, get_edge_extension_url, download_extension
from .models import ChromeManifest


class Browser(Enum):
    CHROME = "chrome"
    EDGE = "edge"


class InvalidExtensionIDError(Exception):
    """Exception raised for invalid extension IDs."""
    pass


class Extension:
    def __init__(self, extension_id, browser, working_dir=None):
        self.extension_id = extension_id
        self.browser = browser
        self.working_dir = working_dir or tempfile.mkdtemp()
        
        # Initialize attributes
        self.extension_zip_path = None
        self.extension_dir_path = None
        self.manifest = None
        self.name = None
        self.version = None
        self.author = None
        self.homepage_url = None
        self.manifest_version = None
        self.sha256 = None
        self.permissions = []
        self.javascript_files = []
        self.urls = []
        
        # Set download URL based on browser
        if browser == Browser.CHROME:
            self.download_url = get_chrome_extension_url(extension_id)
        else:
            self.download_url = get_edge_extension_url(extension_id)

    def __enter__(self):
        """Context manager entry point."""
        self.__download_extension()
        self.__unzip_extension()
        self.__get_manifest()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit point - cleanup."""
        if self.extension_zip_path and os.path.exists(self.extension_zip_path):
            os.remove(self.extension_zip_path)
        if self.extension_dir_path and os.path.exists(self.extension_dir_path):
            import shutil
            shutil.rmtree(self.extension_dir_path)

    def __download_extension(self):
        """Download the extension to a temporary file."""
        self.extension_zip_path = os.path.join(self.working_dir, f"{self.extension_id}.crx")
        download_extension(self.download_url, self.extension_zip_path)
        
        # Calculate SHA256 hash
        with open(self.extension_zip_path, 'rb') as f:
            self.sha256 = hashlib.sha256(f.read()).hexdigest()

    def __unzip_extension(self):
        """Unzip the downloaded extension."""
        self.extension_dir_path = os.path.join(self.working_dir, self.extension_id)
        os.makedirs(self.extension_dir_path, exist_ok=True)
        
        with zipfile.ZipFile(self.extension_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extension_dir_path)

    def __get_manifest(self):
        """Read and parse the extension manifest."""
        manifest_path = os.path.join(self.extension_dir_path, 'manifest.json')
        
        if not os.path.exists(manifest_path):
            raise InvalidExtensionIDError(f"Manifest not found for extension ID: {self.extension_id}")
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        self.manifest = ChromeManifest(**manifest_data)
        
        # Extract metadata from manifest
        self.name = self.manifest.name
        self.version = self.manifest.version
        self.author = self.manifest.author
        self.homepage_url = self.manifest.homepage_url
        self.manifest_version = self.manifest.manifest_version
        
        # Extract permissions
        self.permissions = []
        if self.manifest.permissions:
            self.permissions.extend(self.manifest.permissions)
        if self.manifest.host_permissions:
            self.permissions.extend(self.manifest.host_permissions)
        if self.manifest.optional_permissions:
            self.permissions.extend(self.manifest.optional_permissions)
        if self.manifest.optional_host_permissions:
            self.permissions.extend(self.manifest.optional_host_permissions)
        
        # Find JavaScript files
        self.javascript_files = self._find_javascript_files()
        
        # Extract URLs from manifest and JavaScript files
        self.urls = self._extract_urls()

    def _find_javascript_files(self):
        """Find all JavaScript files in the extension."""
        js_files = []
        
        for root, dirs, files in os.walk(self.extension_dir_path):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.relpath(os.path.join(root, file), self.extension_dir_path))
        
        return js_files

    def _extract_urls(self):
        """Extract URLs from manifest and JavaScript files."""
        urls = set()
        
        # Extract URLs from manifest fields that might contain URLs
        manifest_fields = [
            self.manifest.homepage_url,
            self.manifest.update_url,
            self.manifest.options_page,
            self.manifest.devtools_page
        ]
        
        for field in manifest_fields:
            if field and isinstance(field, str) and field.startswith(('http://', 'https://')):
                urls.add(field)
        
        # Extract URLs from content_scripts
        if self.manifest.content_scripts:
            for script in self.manifest.content_scripts:
                if 'matches' in script:
                    urls.update(script['matches'])
        
        # Extract URLs from web_accessible_resources
        if self.manifest.web_accessible_resources:
            for resource in self.manifest.web_accessible_resources:
                if isinstance(resource, dict) and 'matches' in resource:
                    urls.update(resource['matches'])
                elif isinstance(resource, str) and resource.startswith(('http://', 'https://')):
                    urls.add(resource)
        
        # Extract URLs from JavaScript files (simple regex-based extraction)
        for js_file in self.javascript_files:
            js_path = os.path.join(self.extension_dir_path, js_file)
            try:
                with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Simple URL extraction pattern
                    import re
                    url_pattern = r'https?://[^\s"\'<>]+'
                    found_urls = re.findall(url_pattern, content)
                    urls.update(found_urls)
            except:
                continue
        
        return sorted(list(urls))

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def author(self):
        return self._author

    @property
    def homepage_url(self):
        return self._homepage_url

    @property
    def manifest_version(self):
        return self._manifest_version

    @property
    def permissions(self):
        return self._permissions

    @property
    def javascript_files(self):
        return self._javascript_files

    @property
    def urls(self):
        return self._urls

    # Setter methods for properties
    @name.setter
    def name(self, value):
        self._name = value

    @version.setter
    def version(self, value):
        self._version = value

    @author.setter
    def author(self, value):
        self._author = value

    @homepage_url.setter
    def homepage_url(self, value):
        self._homepage_url = value

    @manifest_version.setter
    def manifest_version(self, value):
        self._manifest_version = value

    @permissions.setter
    def permissions(self, value):
        self._permissions = value

    @javascript_files.setter
    def javascript_files(self, value):
        self._javascript_files = value

    @urls.setter
    def urls(self, value):
        self._urls = value