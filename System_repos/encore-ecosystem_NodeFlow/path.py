from pathlib import Path
from ...node.abstract import Variable


class PathVariable(Variable):
    """A class to handle and manipulate file system paths, ensuring they are resolved and providing path concatenation functionality."""
    
    def __init__(self, value):
        """Initialize an instance with a resolved pathlib.Path object, ensuring the input is of type pathlib.Path and converting it to its absolute path form."""
        if not isinstance(value, Path):
            value = Path(value)
        super().__init__(value.resolve())
    
    def __truediv__(self, other):
        """Implement division operation for a custom class to return a new path by joining the current path with another path component."""
        if isinstance(other, PathVariable):
            return PathVariable(self.value / other.value)
        return PathVariable(self.value / other)


__all__ = ['PathVariable']