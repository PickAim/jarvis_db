from typing import cast
import unittest

from jorm.market.infrastructure import Marketplace as MarketplaceEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.infrastructure.marketplace_mappers import \
    MarketplaceTableToJormMapper
from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import \
    WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure.marketplace_repository import \
    MarketplaceRepository
from jarvis_db.services.market.infrastructure.marketplace_service import \
    MarketplaceService
from jarvis_db.tables import Marketplace
from tests.db_context import DbContext


class MarketplaceServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_create(self):
        marketplace_name = 'qwerty'
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            service.create(MarketplaceEntity(marketplace_name))
        with self.__db_context.session() as session:
            marketplace = session.execute(
                select(Marketplace)
                .where(Marketplace.name == marketplace_name)
            ).scalar_one()
            self.assertEqual(marketplace_name, marketplace.name)

    def test_find_by_name(self):
        marketplace_name = 'qwerty'
        with self.__db_context.session() as session, session.begin():
            session.add(Marketplace(name=marketplace_name))
        with self.__db_context.session() as session:
            service = create_service(session)
            found, _ = cast(tuple[Marketplace, int],
                            service.find_by_name(marketplace_name))
            self.assertEqual(marketplace_name, found.name)

    def test_exists_with_name_returns_true(self):
        marketplace_name = 'qwerty'
        with self.__db_context.session() as session, session.begin():
            session.add(Marketplace(name=marketplace_name))
        with self.__db_context.session() as session:
            service = create_service(session)
            exists = service.exists_with_name(marketplace_name)
            self.assertTrue(exists)

    def test_exists_with_name_returns_false(self):
        marketplace_name = 'qwerty'
        with self.__db_context.session() as session:
            service = create_service(session)
            exists = service.exists_with_name(marketplace_name)
            self.assertFalse(exists)


def create_service(session: Session) -> MarketplaceService:
    return MarketplaceService(
        MarketplaceRepository(session),
        MarketplaceTableToJormMapper(WarehouseTableToJormMapper())
    )
