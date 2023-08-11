from abc import ABC, abstractmethod
from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm.strategy_options import _AbstractLoad

_T = TypeVar("_T", bound=Any)


class ProductCardJoinBuilder(ABC):
    @abstractmethod
    def join_product_histories(self, query: Select[tuple[_T]]) -> Select[tuple[_T]]:
        pass


class ProductCardLoadBuilder(ABC):
    @abstractmethod
    def load_atomic(self, load: _AbstractLoad) -> _AbstractLoad:
        pass
