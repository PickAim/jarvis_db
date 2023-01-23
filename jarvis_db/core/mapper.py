from typing import TypeVar
from typing import Generic
from abc import ABC
from abc import abstractmethod

I = TypeVar('I')
O = TypeVar('O')


class Mapper(ABC, Generic[I, O]):
    @abstractmethod
    def map(self, value: I) -> O:
        pass
