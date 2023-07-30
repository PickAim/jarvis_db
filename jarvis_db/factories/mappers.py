from jorm.market.infrastructure import Marketplace, Niche, Product, Warehouse, Category

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.mappers.market.infrastructure.category_mappers import (
    CategoryTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.infrastructure.marketplace_mappers import (
    MarketplaceTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.infrastructure.niche_mappers import (
    NicheTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import (
    WarehouseTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.items.leftover_mappers import (
    LeftoverTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.items.product_history_mappers import (
    ProductHistoryTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.items.product_mappers import (
    ProductTableToJormMapper,
)


def create_marketplace_table_mapper(
    warehouse_mapper: Mapper[tables.Warehouse, Warehouse] | None = None
) -> Mapper[tables.Marketplace, Marketplace]:
    warehouse_mapper = (
        WarehouseTableToJormMapper() if warehouse_mapper is None else warehouse_mapper
    )
    return MarketplaceTableToJormMapper(warehouse_mapper)


def create_category_table_mapper(
    niche_mapper: Mapper[tables.Niche, Niche] | None = None
) -> Mapper[tables.Category, Category]:
    niche_mapper = create_niche_table_mapper() if niche_mapper is None else niche_mapper
    return CategoryTableToJormMapper(niche_mapper)


def create_niche_table_mapper(
    product_mapper: Mapper[tables.ProductCard, Product] | None = None,
) -> Mapper[tables.Niche, Niche]:
    product_mapper = (
        create_product_table_mapper() if product_mapper is None else product_mapper
    )
    return NicheTableToJormMapper(product_mapper)


def create_product_table_mapper() -> Mapper[tables.ProductCard, Product]:
    return ProductTableToJormMapper(
        ProductHistoryTableToJormMapper(LeftoverTableToJormMapper())
    )
