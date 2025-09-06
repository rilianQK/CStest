# src/fh_utils/tailwind.py

import subprocess
import requests
from pathlib import Path
from .constants import CACHE_DIR

TAILWIND_CONFIG = "tailwind.config.js"
TAILWIND_DAISYCSS_CONFIG = "daisyui.config.js"
TAILWIND_SOURCE_CSS = "src/tailwind.css"
TAILWIND_URI = "/static/tailwind.css"

def add_daisy_and_tailwind(app, cfg=TAILWIND_DAISYCSS_CONFIG, css=TAILWIND_SOURCE_CSS, uri=TAILWIND_URI):
    _add(app, cfg, css, uri)

def add_tailwind(app, cfg=TAILWIND_CONFIG, css=TAILWIND_SOURCE_CSS, uri=TAILWIND_URI):
    _add(app, cfg, css, uri)

def tailwind_compile(outpath, cfg=TAILWIND_CONFIG, css=TAILWIND_SOURCE_CSS):
    cli_path = _cached_download_tailwind_cli("latest")
    subprocess.run([cli_path, "-c", cfg, "-i", css, "-o", outpath], check=True)

def _add(app, cfg, css, uri):
    @app.on_event("startup")
    async def startup_event():
        outpath = Path(CACHE_DIR) / "tailwind.css"
        tailwind_compile(outpath, cfg, css)
        app.mount(uri, StaticFiles(directory=outpath.parent), name="static")

def _cached_download_tailwind_cli(version):
    cli_path = CACHE_DIR / f"tailwindcss-{version}"
    if not cli_path.exists():
        url = _get_download_url(version)
        response = requests.get(url)
        cli_path.write_bytes(response.content)
        cli_path.chmod(0o755)
    return cli_path

def _get_download_url(version):
    os_name = "linux" if os.name == "posix" else "windows"
    arch = "x64" if os.architecture()[0] == "64bit" else "x86"
    return f"https://github.com/tailwindlabs/tailwindcss/releases/download/v{version}/tailwindcss-{os_name}-{arch}"