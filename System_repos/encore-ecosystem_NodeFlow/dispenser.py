from ..node.variable import Variable
from ..converter.converter import Converter

class Dispenser:
    """The Dispenser class is designed to manage and validate the input parameters for a given function or callable, ensuring type compatibility and safe conversion before execution."""

    def __init__(self, **kwargs):
        """Initialize an instance of the class with a variables_table attribute populated by the provided keyword arguments."""
        self.variables_table = kwargs

    def __rshift__(self, other):
        """Implement the right shift operator (`>>`) to pass variables from the current object to a callable or function node, ensuring parameter names and types match, and perform type conversion if necessary before computation."""
        if not callable(other):
            raise TypeError("The right-hand side of the >> operator must be callable")

        parameters = other.get_parameters()
        converted_args = {}

        for name, param_type in parameters.items():
            if name not in self.variables_table:
                raise ValueError(f"Missing required parameter: {name}")

            variable = self.variables_table[name]
            if not isinstance(variable, Variable):
                raise TypeError(f"Parameter {name} must be an instance of Variable")

            if not isinstance(variable, param_type):
                converter = Converter.ROOT_CONVERTER
                if converter is None:
                    raise TypeError(f"No converter available to convert {type(variable)} to {param_type}")

                converted_variable = converter.convert(variable, param_type)
                if converted_variable is None:
                    raise TypeError(f"Cannot convert {type(variable)} to {param_type}")
                converted_args[name] = converted_variable
            else:
                converted_args[name] = variable

        return other.compute(**converted_args)


__all__ = ['Dispenser']