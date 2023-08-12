from typing import Iterable

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.queries.query_builder import QueryBuilder
from jarvis_db.schemas import Niche, ProductCard


class NicheAtomicJoinQueryBuilder(QueryBuilder[Niche]):
    def __init__(self, product_query_builder: QueryBuilder[ProductCard]):
        self.__product_query_builder = product_query_builder

    def provide_load_options(self) -> Iterable[_AbstractLoad]:
        return [
            joinedload(Niche.category),
            joinedload(Niche.products).options(
                *self.__product_query_builder.provide_load_options()
            ),
        ]
