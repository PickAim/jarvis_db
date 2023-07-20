from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

_I = TypeVar("_I")
_O = TypeVar("_O")


class Mapper(ABC, Generic[_I, _O]):
    @abstractmethod
    def map(self, value: _I) -> _O:
        pass
