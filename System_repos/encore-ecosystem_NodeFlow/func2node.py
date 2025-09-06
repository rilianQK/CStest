from ..node.abstract import Function
from ..node.variable import Variable

class ConvertedFunction(Function):
    """Define a base class for functions that convert input arguments into a Node object, requiring subclasses to implement the compute method."""
    
    def __init__(self, func):
        """Initialize the ConvertedFunction instance with a given Python callable function."""
        self.func = func
    
    def compute(self, *args, **kwargs):
        """Execute the stored function with the provided arguments and return the result wrapped in a Variable object."""
        result = self.func(*args, **kwargs)
        return Variable(result)

def func2node(func):
    """Convert a given Python callable function into a Function object that can be processed or executed within a specific framework or system."""
    return ConvertedFunction(func)

__all__ = ['func2node']