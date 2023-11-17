from jorm.market.infrastructure import Category, Marketplace, Niche, Product, Warehouse
from jorm.market.items import ProductHistoryUnit
from jorm.market.service import SimpleEconomySaveObject, TransitEconomySaveObject

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper
from jarvis_db.market.infrastructure.category.category_mappers import (
    CategoryTableToJormMapper,
)
from jarvis_db.market.infrastructure.marketplace.marketplace_mappers import (
    MarketplaceTableToJormMapper,
)
from jarvis_db.market.infrastructure.niche.niche_mappers import (
    NicheTableToJormMapper,
)
from jarvis_db.market.infrastructure.warehouse.warehouse_mappers import (
    WarehouseTableToJormMapper,
)
from jarvis_db.market.items.product_card.product_mappers import (
    ProductTableToJormMapper,
)
from jarvis_db.market.items.product_card_history.leftover_mappers import (
    LeftoverTableToJormMapper,
)
from jarvis_db.market.items.product_card_history.product_history_mappers import (
    ProductHistoryUnitTableToJormMapper,
)
from jarvis_db.market.service.economy.economy_mappers import (
    EconomyRequestTableMapper,
    EconomyResultTableMapper,
    EconomyTableToJormMapper,
)
from jarvis_db.market.service.transit.transit_mappers import (
    TransitRequestMapper,
    TransitResultMapper,
    TransitTableToJormMapper,
)


def create_marketplace_table_mapper(
    warehouse_mapper: Mapper[schemas.Warehouse, Warehouse] | None = None
) -> Mapper[schemas.Marketplace, Marketplace]:
    warehouse_mapper = (
        WarehouseTableToJormMapper() if warehouse_mapper is None else warehouse_mapper
    )
    return MarketplaceTableToJormMapper(warehouse_mapper)


def create_category_table_mapper(
    niche_mapper: Mapper[schemas.Niche, Niche] | None = None
) -> Mapper[schemas.Category, Category]:
    niche_mapper = create_niche_table_mapper() if niche_mapper is None else niche_mapper
    return CategoryTableToJormMapper(niche_mapper)


def create_niche_table_mapper(
    product_mapper: Mapper[schemas.ProductCard, Product] | None = None,
) -> Mapper[schemas.Niche, Niche]:
    product_mapper = (
        create_product_table_mapper() if product_mapper is None else product_mapper
    )
    return NicheTableToJormMapper(product_mapper)


def create_product_table_mapper(
    history_mapper: Mapper[schemas.ProductHistory, ProductHistoryUnit] | None = None
) -> Mapper[schemas.ProductCard, Product]:
    history_mapper = (
        create_product_history_mapper() if history_mapper is None else history_mapper
    )
    return ProductTableToJormMapper(history_mapper)


def create_product_history_mapper() -> (
    Mapper[schemas.ProductHistory, ProductHistoryUnit]
):
    return ProductHistoryUnitTableToJormMapper(LeftoverTableToJormMapper())


def create_economy_table_mapper() -> (
    Mapper[schemas.UserToEconomy, SimpleEconomySaveObject]
):
    return EconomyTableToJormMapper(
        EconomyRequestTableMapper(), EconomyResultTableMapper()
    )


def create_transit_economy_table_mapper() -> (
    Mapper[schemas.UserToTransitEconomy, TransitEconomySaveObject]
):
    return TransitTableToJormMapper(TransitRequestMapper(), TransitResultMapper())
