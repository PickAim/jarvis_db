from typing import Iterable

from sqlalchemy import Select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.core.query_builder import _S, QueryBuilder
from jarvis_db.schemas import Leftover, ProductCard, ProductHistory


class ProductCardAtomicJoinQueryBuilder(QueryBuilder[ProductCard]):
    def join(self, query: Select[tuple[_S]]) -> Select[tuple[_S]]:
        return (
            query.outerjoin(ProductCard.histories)
            .outerjoin(ProductHistory.leftovers)
            .outerjoin(Leftover.warehouse)
        )

    def provide_load_options(self) -> Iterable[_AbstractLoad]:
        return [
            contains_eager(ProductCard.histories)
            .contains_eager(ProductHistory.leftovers)
            .contains_eager(Leftover.warehouse)
        ]
