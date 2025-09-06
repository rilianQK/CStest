# proj_clean/pirel/_utils.py

from abc import ABC, abstractmethod

class VersionLike(ABC):
    @property
    @abstractmethod
    def version_tuple(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple == other.version_tuple

    def __ge__(self, other):
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple >= other.version_tuple

    def __gt__(self, other):
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple > other.version_tuple

    def __le__(self, other):
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple <= other.version_tuple

    def __lt__(self, other):
        if not isinstance(other, VersionLike):
            return NotImplemented
        return self.version_tuple < other.version_tuple