from typing import Iterable

from sqlalchemy import Select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.core.query_builder import _S, QueryBuilder
from jarvis_db.schemas import Niche, ProductCard


class NicheAtomicJoinQueryBuilder(QueryBuilder[Niche]):
    def __init__(self, product_query_builder: QueryBuilder[ProductCard]):
        self.__product_query_builder = product_query_builder

    def join(self, query: Select[tuple[_S]]) -> Select[tuple[_S]]:
        return self.__product_query_builder.join(query.outerjoin(Niche.products))

    def provide_load_options(self) -> Iterable[_AbstractLoad]:
        return [
            contains_eager(Niche.category),
            contains_eager(Niche.products).options(
                *self.__product_query_builder.provide_load_options()
            ),
        ]
