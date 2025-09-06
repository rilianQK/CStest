from typing import Type, Optional
from collections import deque
import heapq

from ..node.abstract import Adapter, Variable
from ..adapter.pipeline import Pipeline


class Converter:
    """The Converter class is designed to manage and execute type conversions between different variable types using a graph of adapters and sub-converters, supporting both direct and multi-step conversions while tracking information loss during the process."""
    
    ROOT_CONVERTER = None
    
    def __init__(self, adapters=None, sub_converters=None):
        """Initialize the object with optional adapters and sub-converters, setting up an empty graph and registering any provided adapters or sub-converters."""
        self.graph = {}
        self.sub_converters = set()
        if adapters:
            self.register_adapters(adapters)
        if sub_converters:
            self.register_converters(sub_converters)

    def __enter__(self):
        """Set the current instance as the root converter in the Converter class upon entering a context managed by a `with` statement."""
        Converter.ROOT_CONVERTER = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the root converter to None when exiting the context manager to ensure proper cleanup and avoid potential memory leaks or state conflicts."""
        Converter.ROOT_CONVERTER = None

    def convert(self, variable, to_type):
        """Convert a given variable from its current type to a specified target type using a predefined conversion pipeline, returning the converted variable if successful or None if the conversion fails."""
        pipeline, preserves_info = self.get_converting_pipeline(type(variable), to_type)
        if pipeline:
            return pipeline.compute(variable)
        return None

    def get_converting_pipeline(self, source, target):
        """Find the shortest conversion pipeline between two types, prioritizing pipelines that do not lose information, and return the pipeline along with a boolean indicating whether information is preserved."""
        if source == target:
            return None, True
        
        queue = deque([(source, Pipeline(), True)])
        visited = set()
        
        while queue:
            current_type, current_pipeline, preserves_info = queue.popleft()
            if current_type in visited:
                continue
            visited.add(current_type
            
            if current_type == target:
                return current_pipeline, preserves_info
            
            for adapter in self.graph.get(current_type, []):
                new_pipeline = Pipeline()
                new_pipeline._pipeline = current_pipeline._pipeline + [adapter]
                new_preserves_info = preserves_info and not adapter.is_loses_information()
                queue.append((adapter.get_type_of_target_variable(), new_pipeline, new_preserves_info))
        
        return None, False

    def is_support_variable(self, variable_type):
        """Check if a given variable type is supported by the graph."""
        return variable_type in self.graph

    def register_adapter(self, adapter):
        """Register an adapter in a graph structure to map conversions between source and target variable types."""
        source_type = adapter.get_type_of_source_variable()
        target_type = adapter.get_type_of_target_variable()
        if source_type not in self.graph:
            self.graph[source_type] = []
        self.graph[source_type].append(adapter)

    def register_adapters(self, adapters):
        """Register multiple adapters by iterating through the provided iterable of adapters and registering each one individually."""
        for adapter in adapters:
            self.register_adapter(adapter)

    def register_converter(self, converter):
        """Register a converter object to the set of sub-converters managed by the current instance."""
        self.sub_converters.add(converter)

    def register_converters(self, converters):
        """Register multiple converters by iterating through an iterable of Converter objects and registering each one individually."""
        for converter in converters:
            self.register_converter(converter)


__all__ = ['Converter']