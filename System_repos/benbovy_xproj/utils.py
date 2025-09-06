from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Frozen(Generic[K, V]):
    """Wrapper around an object implementing the mapping interface to make it
    immutable. If you really want to modify the mapping, the mutable version is
    saved under the `mapping` attribute."""

    __slots__ = ("mapping",)

    def __init__(self, mapping):
        self.mapping = mapping

    def __contains__(self, key):
        return key in self.mapping

    def __getitem__(self, key):
        return self.mapping[key]

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.mapping!r})"


def FrozenDict(*args, **kwargs):
    """Create an immutable dictionary-like object from the provided arguments."""
    return Frozen(dict(*args, **kwargs))