from jarvis_db.queries.implementations.niche_atomic_query_builder import (
    NicheAtomicJoinQueryBuilder,
)
from jarvis_db.queries.implementations.product_atomic_query_builder import (
    AtomicJoinProductCardQueryBuilder,
)
from jarvis_db.queries.query_builder import QueryBuilder
from jarvis_db.schemas import Niche, ProductCard


def create_niche_query_builder(
    product_card_query_builder: QueryBuilder[ProductCard] | None = None,
) -> QueryBuilder[Niche]:
    return NicheAtomicJoinQueryBuilder(
        product_card_query_builder
        if product_card_query_builder is not None
        else create_product_card_query_builder()
    )


def create_product_card_query_builder() -> QueryBuilder[ProductCard]:
    return AtomicJoinProductCardQueryBuilder()
