from pathlib import Path
import json as jsonlib
import logging
import re
from datetime import datetime, timedelta
from typing import Any

LOGGER = logging.getLogger(__name__)
CODEBLOCK_REGEX = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)

def cached_file_path(endpoint: Any) -> Path:
    """Generate a file path in the cache directory for a given endpoint, replacing slashes with underscores to ensure filesystem compatibility."""
    cache_dir = Path.home() / ".cache" / "tofuref"
    cache_dir.mkdir(parents=True, exist_ok=True)
    filename = endpoint.replace("/", "_") + ".json"
    return cache_dir / filename

def get_from_cache(endpoint: Any) -> str | None:
    """Retrieve cached content from a specified endpoint if it exists and is not expired, otherwise return None."""
    cache_file = cached_file_path(endpoint)
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cached_data = jsonlib.load(f)
        
        if 'expires' in cached_data and datetime.fromisoformat(cached_data['expires']) < datetime.now():
            return None
        
        return cached_data['content']
    except (jsonlib.JSONDecodeError, KeyError, ValueError):
        return None

def save_to_cache(endpoint: Any, contents: Any) -> None:
    """Save the given contents to a cache file associated with the specified endpoint, creating directories if necessary."""
    cache_file = cached_file_path(endpoint)
    cache_data = {
        'content': contents,
        'expires': (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    try:
        with open(cache_file, 'w') as f:
            jsonlib.dump(cache_data, f)
    except IOError as e:
        LOGGER.error(f"Failed to save cache for {endpoint}: {e}")

def get_registry_api(endpoint: Any, json: Any = True, log_widget: Any = None, timeout: Any = 10) -> dict[str, dict] | str:
    """Sends GET request to opentofu providers registry to a given endpoint and returns the response either as a JSON or as a string. It also \"logs\" the request. Local cache is used to save/retrieve API responses."""
    import requests
    
    base_url = "https://registry.opentofu.org/v1/providers/"
    full_url = base_url + endpoint
    
    if log_widget:
        log_widget.write(f"Requesting: {full_url}")
    
    cached_content = get_from_cache(endpoint)
    if cached_content:
        if log_widget:
            log_widget.write(f"Using cached response for: {endpoint}")
        return jsonlib.loads(cached_content) if json else cached_content
    
    try:
        response = requests.get(full_url, timeout=timeout)
        response.raise_for_status()
        
        content = response.json() if json else response.text
        
        save_to_cache(endpoint, jsonlib.dumps(content) if json else content)
        
        if log_widget:
            log_widget.write(f"Successfully fetched: {endpoint}")
        
        return content
    except requests.RequestException as e:
        if log_widget:
            log_widget.write(f"Failed to fetch {endpoint}: {e}")
        raise

def header_markdown_split(contents: Any) -> tuple[dict, str]:
    """Most of the documentation files from the registry have a YAML \"header\" that we mostly (at the moment) don't care about. Either way we check for the header, and if it's there, we split it."""
    if contents.startswith('---'):
        parts = contents.split('---', 2)
        if len(parts) >= 3:
            try:
                header = jsonlib.loads(parts[1])
                return header, parts[2].strip()
            except jsonlib.JSONDecodeError:
                pass
    
    return {}, contents

def is_provider_index_expired(file: Any, timeout: Any = 31) -> bool:
    """Provider index is mutable, we consider it expired after 31 days (unconfigurable for now). One request per month is not too bad (we could have static fallback for the cases where this is hit when offline). New providers that people actually want probably won't be showing too often, so a month should be okay."""
    if not file.exists():
        return True
    
    try:
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        return (datetime.now() - mod_time).days > timeout
    except OSError:
        return True