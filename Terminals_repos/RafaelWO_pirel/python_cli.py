# proj_clean/pirel/python_cli.py

import re
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PYTHON_VERSION_RE = re.compile(r"Python (\d+\.\d+\.\d+)")

class ActivePythonInfo:
    def __init__(self, command, path, version):
        self.command = command
        self.path = path
        self.version = version

    def __repr__(self):
        return f"<ActivePythonInfo command={self.command} path={self.path} version={self.version}>"

class PythonVersion:
    def __init__(self, major, minor, micro):
        self.major = major
        self.minor = minor
        self.micro = micro

    def __repr__(self):
        return f"<PythonVersion {self.major}.{self.minor}.{self.micro}>"

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.micro}"

    @property
    def as_release(self):
        return f"{self.major}.{self.minor}"

    @property
    def version_tuple(self):
        return (self.major, self.minor, self.micro)

    @classmethod
    def from_cli(cls, version):
        match = PYTHON_VERSION_RE.match(version)
        if not match:
            raise ValueError(f"Invalid Python version string: {version}")
        major, minor, micro = map(int, match.group(1).split('.'))
        return cls(major, minor, micro)

    @classmethod
    def this(cls):
        return cls(*sys.version_info[:3])

def get_active_python_info():
    commands = ["python", "python3", "python2"]
    for command in commands:
        try:
            result = subprocess.run([command, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                path = Path(subprocess.run([command, "-c", "import sys; print(sys.executable)"], capture_output=True, text=True).stdout.strip())
                return ActivePythonInfo(command, path, PythonVersion.from_cli(version))
        except Exception as e:
            logger.error(f"Error retrieving Python info for {command}: {e}")
    return None