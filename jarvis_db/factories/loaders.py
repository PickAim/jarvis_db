from jarvis_db.queries.implementations.joinedload_niche_query_builder import (
    JoinedLoadNicheLoadBuilder,
)
from jarvis_db.queries.implementations.joinload_product_query_builder import (
    JoinedLoadProductCardLoadBuilder,
)
from jarvis_db.queries.niche_query_builder import NicheLoadBuilder
from jarvis_db.queries.product_query_builer import ProductCardLoadBuilder


def create_niche_loader(
    product_loader: ProductCardLoadBuilder | None = None,
) -> NicheLoadBuilder:
    return JoinedLoadNicheLoadBuilder(
        create_product_loader() if product_loader is None else product_loader
    )


def create_product_loader() -> ProductCardLoadBuilder:
    return JoinedLoadProductCardLoadBuilder()
