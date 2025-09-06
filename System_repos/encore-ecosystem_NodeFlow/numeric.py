from ...node.abstract import Adapter, Variable
from ...builtin.variables.numeric import Integer, Boolean, Float


class Boolean2Integer(Adapter):
    """Convert a Boolean value to an Integer value, where True becomes 1 and False becomes 0, without losing information."""
    
    def compute(self, variable):
        """Convert a Boolean value to an Integer where True becomes 1 and False becomes 0."""
        return Integer(1 if variable.value else 0)
    
    def is_loses_information(self):
        """Determine if the operation or transformation represented by the method results in any loss of information when applied to the data."""
        return False


class Float2Integer(Adapter):
    """Convert a floating-point number to an integer by truncating the decimal part, with the awareness that this operation may lose information."""
    
    def compute(self, variable):
        """Convert a floating-point number to an integer by truncating the decimal part."""
        return Integer(int(variable.value))
    
    def is_loses_information(self):
        """Determine if the operation or transformation represented by the method results in a loss of information, returning `True` if information is lost and `False` otherwise."""
        return True


class Integer2Boolean(Adapter):
    """Convert an Integer value to a Boolean value, where the Boolean is True if the Integer is non-zero and False otherwise, with the note that this conversion may lose information."""
    
    def compute(self, variable):
        """Convert an Integer object's value to a Boolean and return it as a Boolean object."""
        return Boolean(variable.value != 0)
    
    def is_loses_information(self):
        """Determine if the operation or transformation represented by the method results in a loss of information when applied to the data."""
        return True


class Integer2Float(Adapter):
    """Convert an Integer type to a Float type without losing information."""
    
    def compute(self, variable):
        """Convert an Integer object's value to a Float object's value."""
        return Float(float(variable.value))
    
    def is_loses_information(self):
        """Determine if the operation or transformation represented by the method results in any loss of information, returning a boolean indicating the result."""
        return False


class PyBool2Boolean(Adapter):
    """Adapt a Python boolean value to a custom Boolean type without information loss."""
    
    def compute(self, variable):
        """Convert a boolean input variable into a Boolean object and return it."""
        return Boolean(variable)
    
    def is_loses_information(self):
        """Determine if the operation or transformation represented by the object loses any information when applied."""
        return False


class PyFloat2Float(Adapter):
    """Adapt a Python float to a custom Float type without information loss."""
    
    def compute(self, variable):
        """Convert a given float variable into a Float object."""
        return Float(variable)
    
    def is_loses_information(self):
        """Determine whether the operation or transformation represented by the method results in a loss of information when applied to the data."""
        return False


class PyInt2Integer(Adapter):
    """Adapt a Python integer to an Integer object without information loss."""
    
    def compute(self, variable):
        """Convert an integer input into an Integer object."""
        return Integer(variable)
    
    def is_loses_information(self):
        """Determine if the operation or transformation represented by the method results in a loss of information when applied to the data."""
        return False


__all__ = ['Boolean2Integer', 'Float2Integer', 'Integer2Boolean', 'Integer2Float', 'PyBool2Boolean', 'PyFloat2Float', 'PyInt2Integer']