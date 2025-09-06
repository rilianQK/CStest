from abc import ABC, abstractmethod
from typing import Type, Any, Optional, OrderedDict
from collections import OrderedDict as odict
import inspect


class Node(ABC):
    """To serve as an abstract base class for defining node structures in various data structures or algorithms."""
    pass


class Variable(Node):
    """Represents a variable node in a computational graph that can be processed by functions and supports equality checks."""
    
    def __init__(self, value):
        """Initialize an instance of the class with a given value and store it as an attribute."""
        self.value = value
    
    def __eq__(self, other):
        """Compare the value of the current instance with another object (either a Variable instance or a direct value) for equality."""
        if isinstance(other, Variable):
            return self.value == other.value
        return self.value == other
    
    def __rshift__(self, other):
        """Implement the right shift operation (>>) to enable function composition where the left operand is passed as input to the right operand's compute method."""
        if hasattr(other, 'compute'):
            return other.compute(self)
        return other(self)


class Function(Node):
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


class Adapter(ABC):
    """The Adapter class serves as an abstract base class for implementing adapters that transform one type of variable to another, with capabilities to check for information loss during the transformation and to inspect the input and output variable types."""
    
    @abstractmethod
    def compute(self, variable):
        """This method is intended to perform a computation or transformation on the given Variable object, but it is designed to be overridden by subclasses with specific implementations."""
        pass
    
    def get_type_of_source_variable(self):
        """Retrieve the type annotation of the 'variable' parameter from the signature of the 'compute' method."""
        sig = inspect.signature(self.compute)
        params = list(sig.parameters.values())
        if len(params) > 0 and params[0].annotation != inspect.Parameter.empty:
            return params[0].annotation
        return None
    
    def get_type_of_target_variable(self):
        """Determine the return type annotation of the `compute` method in the class instance."""
        sig = inspect.signature(self.compute)
        return sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None
    
    @abstractmethod
    def is_loses_information(self):
        """Determine whether the operation or transformation represented by the method results in a loss of information when applied to the data."""
        pass


__all__ = ['Node', 'Variable', 'Function', 'Adapter']