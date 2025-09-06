from abc import ABC, abstractmethod
from typing import OrderedDict
import inspect
from collections import OrderedDict as odict
from .variable import Variable

class Function(ABC):
    """Provide an abstract base class for defining custom functions with parameter and return type introspection capabilities."""
    
    @abstractmethod
    def compute(self, *args, **kwargs):
        """This method is intended to be overridden by subclasses to perform specific computations and return a Variable object, but it is not implemented in the current class."""
        pass
    
    def get_parameters(self):
        """Retrieve the parameter names and their corresponding type annotations from the `compute` method's signature, returning them as an ordered dictionary."""
        sig = inspect.signature(self.compute)
        parameters = odict()
        for name, param in sig.parameters.items():
            if name != 'self' and param.annotation != inspect.Parameter.empty:
                parameters[name] = param.annotation
        return parameters
    
    def get_return_type(self):
        """Retrieve the return type annotation of the `compute` method from the class instance, returning it as a `Type[Variable]`."""
        sig = inspect.signature(self.compute)
        return sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None

__all__ = ['Function']