from typing import Type, Optional
from collections import deque
import heapq

from ..adapter.abstract import Adapter
from ..node.variable import Variable


class Pipeline:
    """The Pipeline class manages a sequence of Adapter instances to process Variable objects sequentially, ensuring type compatibility between adapters and tracking information loss across the pipeline."""

    def __init__(self):
        """Initialize the object with default values for loose_information as False and an empty list for pipeline to store Adapter objects."""
        self._pipeline = []
        self._loose_information = False

    def add_adapter(self, adapter):
        """Add an adapter to the pipeline, ensuring compatibility between consecutive adapters and tracking information loss."""
        if not isinstance(adapter, Adapter):
            raise TypeError("Adapter must be an instance of Adapter")
        
        if self._pipeline:
            last_adapter = self._pipeline[-1]
            last_target = last_adapter.get_type_of_target_variable()
            current_source = adapter.get_type_of_source_variable()
            
            if last_target != current_source:
                raise ValueError(f"Adapter type mismatch: {last_target} -> {current_source}")
        
        self._pipeline.append(adapter)
        if adapter.is_loses_information():
            self._loose_information = True

    def compute(self, variable):
        """Process a given variable through a series of adapters in a pipeline and return the transformed variable."""
        if not self._pipeline:
            return variable
        
        current_variable = variable
        for adapter in self._pipeline:
            current_variable = adapter.compute(current_variable)
        
        return current_variable

    def get_type_of_source_variable(self):
        """Retrieve the type of the source variable from the first element in the pipeline."""
        if not self._pipeline:
            return None
        return self._pipeline[0].get_type_of_source_variable()

    def get_type_of_target_variable(self):
        """Retrieve the type of the target variable from the last component in the pipeline."""
        if not self._pipeline:
            return None
        return self._pipeline[-1].get_type_of_target_variable()

    def is_loses_information(self):
        """Determine whether the operation or transformation associated with the instance results in a loss of information by checking the value of the internal flag `_loose_information`."""
        return self._loose_information


__all__ = ['Pipeline']