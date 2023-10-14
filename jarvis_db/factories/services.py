from jorm.market.infrastructure import Marketplace, Niche, Product, Warehouse
from sqlalchemy.orm import Load, Session

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper
from jarvis_db.factories.mappers import (
    create_category_table_mapper,
    create_economy_table_mapper,
    create_marketplace_table_mapper,
    create_niche_table_mapper,
    create_product_table_mapper,
    create_transit_economy_table_mapper,
)
from jarvis_db.factories.queries import (
    create_category_query_builder,
)
from jarvis_db.mappers.cache.green_trade_zone_mappers import (
    GreenTradeZoneTableToJormMapper,
)
from jarvis_db.mappers.cache.niche_characteristics_mappers import (
    NicheCharacteristicsTableToJormMapper,
)
from jarvis_db.mappers.market.infrastructure.warehouse_mappers import (
    WarehouseTableToJormMapper,
)
from jarvis_db.mappers.market.items.leftover_mappers import (
    LeftoverTableToJormMapper,
)
from jarvis_db.mappers.market.items.product_history_mappers import (
    ProductHistoryUnitTableToJormMapper,
)
from jarvis_db.mappers.market.person import (
    AccountTableToJormMapper,
    UserTableToJormMapper,
)
from jarvis_db.mappers.market.person.token_mappers import TokenTableMapper
from jarvis_db.mappers.market.service.economy_constants_mappers import (
    EconomyConstantsTableToJormMapper,
)
from jarvis_db.services.cache.green_trade_zone_service import GreenTradeZoneService
from jarvis_db.services.cache.niche_characteristics_service import (
    NicheCharacteristicsService,
)
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import (
    MarketplaceService,
)
from jarvis_db.services.market.infrastructure.niche_service import (
    NicheLoadOptions,
    NicheService,
)
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_db.services.market.items.product_history_service import (
    ProductHistoryService,
)
from jarvis_db.services.market.person import AccountService, TokenService, UserService
from jarvis_db.services.market.person.user_items_service import UserItemsService
from jarvis_db.services.market.service.economy_constants_service import (
    EconomyConstantsService,
)
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.transit_economy_service import (
    TransitEconomyService,
)


def create_account_service(session: Session) -> AccountService:
    return AccountService(session, AccountTableToJormMapper())


def create_user_service(session: Session) -> UserService:
    return UserService(session, UserTableToJormMapper())


def create_user_items_service(
    session: Session,
    product_mapper: Mapper[schemas.ProductCard, Product] | None = None,
    warehouse_mapper: Mapper[schemas.Warehouse, Warehouse] | None = None,
) -> UserItemsService:
    return UserItemsService(
        session,
        create_product_table_mapper() if product_mapper is None else product_mapper,
        WarehouseTableToJormMapper() if warehouse_mapper is None else warehouse_mapper,
    )


def create_token_service(session: Session) -> TokenService:
    return TokenService(session, TokenTableMapper())


def create_marketplace_service(
    session: Session,
    marketplace_mapper: Mapper[schemas.Marketplace, Marketplace] | None = None,
) -> MarketplaceService:
    marketplace_mapper = (
        create_marketplace_table_mapper()
        if marketplace_mapper is None
        else marketplace_mapper
    )
    return MarketplaceService(session, marketplace_mapper)


def create_category_service(
    session: Session,
    niche_mapper: Mapper[schemas.Niche, Niche] | None = None,
) -> CategoryService:
    if niche_mapper is None:
        niche_mapper = create_niche_table_mapper()
    return CategoryService(
        session,
        create_category_query_builder(),
        create_category_table_mapper(niche_mapper),
    )


def create_niche_service(
    session: Session, niche_mapper: Mapper[schemas.Niche, Niche] | None = None
) -> NicheService:
    niche_mapper = create_niche_table_mapper() if niche_mapper is None else niche_mapper
    return NicheService(
        session,
        NicheLoadOptions(
            atomic_options=[
                Load(schemas.Niche).joinedload(schemas.Niche.category),
                Load(schemas.Niche)
                .joinedload(schemas.Niche.products)
                .joinedload(schemas.ProductCard.histories)
                .joinedload(schemas.ProductHistory.leftovers)
                .joinedload(schemas.Leftover.warehouse),
            ],
            no_history_options=[
                Load(schemas.Niche).joinedload(schemas.Niche.category),
                Load(schemas.Niche)
                .joinedload(schemas.Niche.products)
                .noload(schemas.ProductCard.histories),
            ],
        ),
        niche_mapper,
    )


def create_warehouse_service(
    session: Session,
    warehouse_mapper: Mapper[schemas.Warehouse, Warehouse] | None = None,
) -> WarehouseService:
    warehouse_mapper = (
        WarehouseTableToJormMapper() if warehouse_mapper is None else warehouse_mapper
    )
    return WarehouseService(session, warehouse_mapper)


def create_economy_service(session: Session) -> EconomyService:
    return EconomyService(
        session,
        create_economy_table_mapper(),
        create_warehouse_service(session),
    )


def create_transit_economy_service(
    session: Session, warehouse_service: WarehouseService | None = None
) -> TransitEconomyService:
    return TransitEconomyService(
        session,
        create_transit_economy_table_mapper(),
        warehouse_service
        if warehouse_service is not None
        else create_warehouse_service(session),
    )


def create_product_history_service(session: Session) -> ProductHistoryService:
    return ProductHistoryService(
        session,
        ProductHistoryUnitTableToJormMapper(LeftoverTableToJormMapper()),
    )


def create_product_card_service(
    session: Session, history_service: ProductHistoryService | None = None
) -> ProductCardService:
    history_service = (
        create_product_history_service(session)
        if history_service is None
        else history_service
    )
    return ProductCardService(
        session,
        history_service,
        create_product_table_mapper(),
    )


def create_economy_constants_service(session: Session) -> EconomyConstantsService:
    return EconomyConstantsService(session, EconomyConstantsTableToJormMapper())


def create_niche_characteristics_service(
    session: Session,
) -> NicheCharacteristicsService:
    return NicheCharacteristicsService(session, NicheCharacteristicsTableToJormMapper())


def create_green_trade_zone_service(session: Session) -> GreenTradeZoneService:
    return GreenTradeZoneService(session, GreenTradeZoneTableToJormMapper())
