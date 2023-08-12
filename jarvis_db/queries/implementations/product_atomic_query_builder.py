from typing import Iterable

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.queries.query_builder import QueryBuilder
from jarvis_db.schemas import Leftover, ProductCard, ProductHistory


class ProductCardAtomicJoinQueryBuilder(QueryBuilder[ProductCard]):
    def provide_load_options(self) -> Iterable[_AbstractLoad]:
        return [
            joinedload(ProductCard.histories)
            .joinedload(ProductHistory.leftovers)
            .joinedload(Leftover.warehouse)
        ]
