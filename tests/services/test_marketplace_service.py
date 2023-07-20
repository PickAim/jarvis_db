import unittest
from typing import cast

from jorm.market.infrastructure import Marketplace as MarketplaceEntity
from sqlalchemy import select

from jarvis_db.factories.services import create_marketplace_service
from jarvis_db.repositores.mappers.market.infrastructure.marketplace_mappers import (
    MarketplaceTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import (
    WarehouseTableToJormMapper,
)
from jarvis_db.tables import Marketplace, Warehouse
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class MarketplaceServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_create(self):
        marketplace_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            service = create_marketplace_service(session)
            service.create(MarketplaceEntity(marketplace_name))
        with self.__db_context.session() as session:
            marketplace = session.execute(
                select(Marketplace).where(Marketplace.name == marketplace_name)
            ).scalar_one()
            self.assertEqual(marketplace_name, marketplace.name)

    def test_find_by_name(self):
        marketplace_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(Marketplace(name=marketplace_name))
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            found, _ = cast(
                tuple[Marketplace, int], service.find_by_name(marketplace_name)
            )
            self.assertEqual(marketplace_name, found.name)

    def test_find_all(self):
        with self.__db_context.session() as sesion, sesion.begin():
            seeder = AlchemySeeder(sesion)
            seeder.seed_marketplaces(3)
            marketplaces = sesion.execute(select(Marketplace)).scalars().all()
            mapper = MarketplaceTableToJormMapper(WarehouseTableToJormMapper())
            expected_marketplaces = [
                mapper.map(marketplace) for marketplace in marketplaces
            ]
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            actual_marketplaces = service.find_all()
            for expected, actual in zip(
                expected_marketplaces, actual_marketplaces.values(), strict=True
            ):
                self.assertEqual(expected, actual)

    def test_fetch_all_atomic(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(3)
            seeder.seed_warehouses(6)
            marketplaces = (
                session.execute(
                    select(Marketplace).outerjoin(Marketplace.warehouses).distinct()
                )
                .scalars()
                .all()
            )
            mapper = MarketplaceTableToJormMapper(WarehouseTableToJormMapper())
            expected_marketplaces = [
                mapper.map(marketplace) for marketplace in marketplaces
            ]
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            actual_marketplaces = service.fetch_all_atomic().values()
            for expected, actual in zip(
                expected_marketplaces, actual_marketplaces, strict=True
            ):
                self.assertEqual(expected, actual)

    def test_exists_with_name_returns_true(self):
        marketplace_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(Marketplace(name=marketplace_name))
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            exists = service.exists_with_name(marketplace_name)
            self.assertTrue(exists)

    def test_exists_with_name_returns_false(self):
        marketplace_name = "qwerty"
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            exists = service.exists_with_name(marketplace_name)
            self.assertFalse(exists)
