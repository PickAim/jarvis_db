from jarvis_db.queries.implementations.niche_join_builder import NicheJoinBuilderImpl
from jarvis_db.queries.implementations.product_join_builder import (
    ProductCardJoinBuilderImpl,
)
from jarvis_db.queries.niche_query_builder import NicheJoinBuilder
from jarvis_db.queries.product_query_builer import ProductCardJoinBuilder


def create_niche_join_builder(
    product_join_builder: ProductCardJoinBuilder | None = None,
) -> NicheJoinBuilder:
    return NicheJoinBuilderImpl(
        create_product_card_join_builder()
        if product_join_builder is None
        else product_join_builder
    )


def create_product_card_join_builder() -> ProductCardJoinBuilder:
    return ProductCardJoinBuilderImpl()
