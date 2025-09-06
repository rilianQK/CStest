import os
import requests
import tempfile
from typing import Optional

# Constants for browser versions and user agent
CHROME_VERSION = "120.0.0.0"
EDGE_VERSION = "120.0.0.0"
USER_AGENT = "Mozilla/5.0 (Macintosh; ARM Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def get_chrome_extension_url(extension_id, chrome_version=CHROME_VERSION) -> str:
    """
    Generate a URL to download a Chrome extension by its ID and Chrome version, formatted for a specific platform (Mac ARM64).

    Args:
        extension_id: ID of the Chrome extension
        chrome_version: Chrome version to use in the URL

    Returns:
        URL string for downloading the Chrome extension
    """
    return f"https://clients2.google.com/service/update2/crx?response=redirect&acceptformat=crx2,crx3&prodversion={chrome_version}&x=id%3D{extension_id}%26uc"


def get_edge_extension_url(extension_id, edge_version=EDGE_VERSION) -> str:
    """
    Generate a Microsoft Edge extension download URL based on the given extension ID and Edge version.

    Args:
        extension_id: ID of the Edge extension
        edge_version: Edge version to use in the URL

    Returns:
        URL string for downloading the Edge extension
    """
    return f"https://edge.microsoft.com/extensionwebstorebase/v1/crx?response=redirect&prodversion={edge_version}&x=id%3D{extension_id}%26uc"


def download_extension(url, output_path) -> None:
    """
    Downloads Chrome extension to specified path using extension ID.

    Args:
        url: URL to download the extension from
        output_path: Local file path where extension should be saved
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download extension: {e}")