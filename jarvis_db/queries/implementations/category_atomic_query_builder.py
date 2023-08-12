from typing import Iterable

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.queries.query_builder import QueryBuilder
from jarvis_db.schemas import Category, Niche


class CategoryAtomicJoinQueryBuilder(QueryBuilder[Category]):
    def __init__(self, niche_query_builder: QueryBuilder[Niche]):
        self.__niche_query_builder = niche_query_builder

    def provide_load_options(self) -> Iterable[_AbstractLoad]:
        return [
            joinedload(Category.niches).options(
                *self.__niche_query_builder.provide_load_options()
            )
        ]
