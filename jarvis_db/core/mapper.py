from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

I = TypeVar('I')
O = TypeVar('O')


class Mapper(ABC, Generic[I, O]):
    @abstractmethod
    def map(self, value: I) -> O:
        pass
