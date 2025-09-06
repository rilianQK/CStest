# src/fh_utils/server.py

import logging
import uvicorn
from pathlib import Path
from functools import lru_cache

FAST = "fast"
FULL = "full"
logger = logging.getLogger(__name__)
server = None
watcher = None

class CliException(Exception):
    pass

class Watcher:
    def __init__(self, **kwargs):
        self.should_exit = False
        self.watch_filter = None
        self.watcher = None

    def loop(self):
        # Implementation here
        pass

    def shutdown(self):
        # Implementation here
        pass

class _ModuleData:
    pass

def no_reload(func):
    # Implementation here
    pass

def no_reload_cache(user_function):
    # Implementation here
    pass

def serve(appname, app, host, port, reload, reload_includes, reload_excludes, **kwargs):
    # Implementation here
    pass

def _add_live_reload(app, **kwargs):
    # Implementation here
    pass

def _display_path(path):
    # Implementation here
    pass

def _get_import_string(path, app_name):
    # Implementation here
    pass

def _get_module_data_from_path(path):
    # Implementation here
    pass

def _patch_autoreload():
    # Implementation here
    pass

def _run_with_fast_reload(module_import_str, app_str, port, host, live, **kwargs):
    # Implementation here
    pass

def _terminate(port):
    # Implementation here
    pass

def serve_dev(path, app, host, port, live, reload, **kwargs):
    # Implementation here
    pass

def serve_prod(path, app, host, port, **kwargs):
    # Implementation here
    pass