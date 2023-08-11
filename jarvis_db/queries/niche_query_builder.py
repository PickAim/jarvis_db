from abc import ABC, abstractmethod
from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm.strategy_options import _AbstractLoad

_T = TypeVar("_T", bound=Any)


class NicheJoinBuilder(ABC):
    @abstractmethod
    def join_products(self, query: Select[tuple[_T]]) -> Select[tuple[_T]]:
        pass


class NicheLoadBuilder(ABC):
    @abstractmethod
    def load_products(self) -> _AbstractLoad:
        pass
