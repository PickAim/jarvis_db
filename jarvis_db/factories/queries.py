from jarvis_db.market.infrastructure.category.category_atomic_query_builder import (
    CategoryAtomicJoinQueryBuilder,
)
from jarvis_db.market.infrastructure.niche.niche_atomic_query_builder import (
    NicheAtomicJoinQueryBuilder,
)
from jarvis_db.market.items.product_card.product_atomic_query_builder import (
    ProductCardAtomicJoinQueryBuilder,
)
from jarvis_db.core.query_builder import QueryBuilder
from jarvis_db.schemas import Category, Niche, ProductCard


def create_category_query_builder(
    niche_query_builder: QueryBuilder[Niche] | None = None,
) -> QueryBuilder[Category]:
    return CategoryAtomicJoinQueryBuilder(
        niche_query_builder
        if niche_query_builder is not None
        else create_niche_query_builder()
    )


def create_niche_query_builder(
    product_card_query_builder: QueryBuilder[ProductCard] | None = None,
) -> QueryBuilder[Niche]:
    return NicheAtomicJoinQueryBuilder(
        product_card_query_builder
        if product_card_query_builder is not None
        else create_product_card_query_builder()
    )


def create_product_card_query_builder() -> QueryBuilder[ProductCard]:
    return ProductCardAtomicJoinQueryBuilder()
