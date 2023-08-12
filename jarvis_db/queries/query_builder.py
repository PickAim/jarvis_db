from abc import ABC
from typing import Any, Generic, Iterable, TypeVar

from sqlalchemy import Select
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.db_config import Base

_T = TypeVar("_T", bound=Base)
_S = TypeVar("_S", bound=Any)


class QueryBuilder(ABC, Generic[_T]):
    def join(self, query: Select[tuple[_S]]) -> Select[tuple[_S]]:
        return query

    def provide_load_options(self) -> Iterable[_AbstractLoad]:
        return []
