# proj_clean/pirel/__init__.py

from rich.console import Console
from functools import cached_property
from .releases import PythonReleases

__version__ = "0.1.0"

class PirelContext:
    def __init__(self):
        self.rich_console = Console(highlight=False)

    @cached_property
    def releases(self):
        return PythonReleases()

CONTEXT = PirelContext()