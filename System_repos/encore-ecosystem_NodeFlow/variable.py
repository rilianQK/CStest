from abc import ABC, abstractmethod

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

__all__ = ['Variable']