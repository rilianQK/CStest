# src/fh_utils/cli.py

import logging
import uvicorn
from .server import serve_dev, serve_prod

logger = logging.getLogger(__name__)

def _parse_uvicorn_argument(args):
    # Implementation here
    pass

def callback(version):
    # Implementation here
    pass

def dev(path, app, host, port, reload, live, ctx):
    serve_dev(path, app, host, port, live, reload, **ctx)

def run(path, app, host, port, ctx):
    serve_prod(path, app, host, port, **ctx)

def version_callback(value):
    # Implementation here
    pass