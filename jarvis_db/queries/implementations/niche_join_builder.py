from sqlalchemy import Select

from jarvis_db.queries.niche_query_builder import _T, NicheJoinBuilder
from jarvis_db.queries.product_query_builer import ProductCardJoinBuilder
from jarvis_db.schemas import Niche


class NicheJoinBuilderImpl(NicheJoinBuilder):
    def __init__(self, product_join_builder: ProductCardJoinBuilder) -> None:
        self.__product_join_builder = product_join_builder

    def join_products(self, query: Select[tuple[_T]]) -> Select[tuple[_T]]:
        return self.__product_join_builder.join_product_histories(
            query.outerjoin(Niche.products)
        )
