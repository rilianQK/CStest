# src/fh_utils/ipython_ext.py

from IPython.core.magic import register_line_magic
import uvicorn
import socket
from .server import Server

PORT_RANGE = (8000, 9000)

class JupyterReloader:
    def __init__(self):
        self.server = None

    def load(self, app, page, width, height, port, host):
        if self.server:
            self.server.close()
        self.server = Server(uvicorn.Config(app, host=host, port=port))
        self.server.run_in_thread()
        return f"http://{host}:{port}/{page}"

class Server:
    def __init__(self, config):
        self.run = uvicorn.Server(config)
        self.running_app = None
        self.should_exit = False
        self.thread = None

    def close(self):
        self.should_exit = True
        if self.thread:
            self.thread.join()

    def install_signal_handlers(self):
        self.run.install_signal_handlers()

    def run_in_thread(self):
        import threading
        self.thread = threading.Thread(target=self.run.run)
        self.thread.daemon = True
        self.thread.start()
        import time
        timeout = 5
        while timeout > 0 and not self.run.started:
            time.sleep(0.1)
            timeout -= 0.1
        if not self.run.started:
            raise RuntimeError("Server didn't start within timeout")

class TupleNoPrint(tuple):
    def __repr__(self):
        return ""

    def __str__(self):
        return ""

@register_line_magic
def load_ipython_extension(ipython):
    ipython.register_magic_function(load_ipython_extension, 'line')

def find_available_port(host):
    for port in range(PORT_RANGE[0], PORT_RANGE[1]):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError("No available port found")