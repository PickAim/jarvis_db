from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.queries.product_query_builer import (
    ProductCardLoadBuilder,
)
from jarvis_db.schemas import Leftover, ProductCard, ProductHistory


class JoinedLoadProductCardLoadBuilder(ProductCardLoadBuilder):
    def load_atomic(self, load: _AbstractLoad) -> _AbstractLoad:
        return (
            load.joinedload(ProductCard.histories)
            .joinedload(ProductHistory.leftovers)
            .joinedload(Leftover.warehouse)
        )
