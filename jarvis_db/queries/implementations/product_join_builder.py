from sqlalchemy import Select

from jarvis_db.queries.product_query_builer import _T, ProductCardJoinBuilder
from jarvis_db.schemas import Leftover, ProductCard, ProductHistory


class ProductCardJoinBuilderImpl(ProductCardJoinBuilder):
    def join_product_histories(self, query: Select[tuple[_T]]) -> Select[tuple[_T]]:
        return (
            query.outerjoin(ProductCard.histories)
            .outerjoin(ProductHistory.leftovers)
            .outerjoin(Leftover.warehouse)
        )
