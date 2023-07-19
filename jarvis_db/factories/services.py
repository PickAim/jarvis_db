from jorm.market.infrastructure import Niche, Marketplace
from sqlalchemy.orm import Session

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
from jarvis_db.repositores.mappers.market.items.product_mappers import (
    ProductTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.service.economy_request_mappers import (
    EconomyRequestTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.service.economy_result_mappers import (
    EconomyResultTableToJormMapper,
)
from jarvis_db.repositores.market.infrastructure.warehouse_repository import (
    WarehouseRepository,
)
from jarvis_db.repositores.market.service.economy_request_repository import (
    EconomyRequestRepository,
)
from jarvis_db.repositores.market.service.economy_result_repository import (
    EconomyResultRepository,
)
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import (
    MarketplaceService,
)
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.service.economy_service import EconomyService


def create_marketplace_service(
    session: Session,
    markeplace_mapper: Mapper[tables.Marketplace, Marketplace] | None = None,
) -> MarketplaceService:
    markeplace_mapper = (
        MarketplaceTableToJormMapper(WarehouseTableToJormMapper())
        if markeplace_mapper is None
        else markeplace_mapper
    )
    return MarketplaceService(session, markeplace_mapper)


def create_category_service(
    session: Session,
    niche_mapper: Mapper[tables.Niche, Niche] | None = None,
) -> CategoryService:
    if niche_mapper is None:
        niche_mapper = NicheTableToJormMapper(ProductTableToJormMapper())
    return CategoryService(
        session,
        CategoryTableToJormMapper(niche_mapper),
    )


def create_niche_service(
    session: Session, niche_mapper: Mapper[tables.Niche, Niche] | None = None
) -> NicheService:
    niche_mapper = (
        NicheTableToJormMapper(ProductTableToJormMapper())
        if niche_mapper is None
        else niche_mapper
    )
    return NicheService(session, NicheTableToJormMapper(ProductTableToJormMapper()))


def create_warehouse_service(session: Session) -> WarehouseService:
    return WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())


def create_economy_service(session: Session) -> EconomyService:
    niche_mapper = NicheTableToJormMapper(ProductTableToJormMapper())
    return EconomyService(
        EconomyRequestRepository(session),
        EconomyResultRepository(session),
        EconomyResultTableToJormMapper(EconomyRequestTableToJormMapper()),
        create_category_service(session, niche_mapper),
        create_niche_service(session, niche_mapper),
        WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper()),
    )
