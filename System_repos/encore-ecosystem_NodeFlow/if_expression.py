from ...node.abstract import Function
from ...node.variable import Variable


def py_if(expression, true_case, false_case):
    """Return one of two provided values based on the evaluation of a given boolean expression."""
    return true_case if expression else false_case


class IF(Function):
    """A function node that implements conditional execution based on a boolean expression."""
    
    def compute(self, expression, true_case, false_case):
        """Execute conditional logic based on the provided expression, returning either the true_case or false_case value."""
        if isinstance(expression, Variable):
            expression = expression.value
        
        if expression:
            return true_case
        else:
            return false_case


IF = IF()

__all__ = ['IF']