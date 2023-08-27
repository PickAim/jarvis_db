import unittest
from typing import cast

from jorm.market.infrastructure import Marketplace as MarketplaceEntity
from sqlalchemy import select
from jarvis_db.factories.mappers import create_marketplace_table_mapper

from jarvis_db.factories.services import create_marketplace_service
from jarvis_db.mappers.market.infrastructure.marketplace_mappers import (
    MarketplaceTableToJormMapper,
)
from jarvis_db.mappers.market.infrastructure.warehouse_mappers import (
    WarehouseTableToJormMapper,
)
from jarvis_db.schemas import Marketplace
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class MarketplaceServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)

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
            seeder = AlchemySeeder(session)
            seeder.seed_warehouses(200)
            seeder.seed_products(200)
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            found, _ = cast(
                tuple[Marketplace, int], service.find_by_name(marketplace_name)
            )
            self.assertEqual(marketplace_name, found.name)
            self.assertEqual(0, len(found.warehouses))

    def test_find_by_id(self):
        mapper = create_marketplace_table_mapper()
        marketplace_id = 100
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(id=marketplace_id, name="qwerty")
            session.add(marketplace)
            session.flush()
            expected = mapper.map(marketplace)
            seeder = AlchemySeeder(session)
            seeder.seed_products(2000)
            seeder.seed_warehouses(200)
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            actual = service.find_by_id(marketplace_id)
            self.assertEqual(expected, actual)

    def test_find_all(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(3)
            marketplaces = session.execute(select(Marketplace)).scalars().all()
            mapper = MarketplaceTableToJormMapper(WarehouseTableToJormMapper())
            expected_marketplaces = {
                marketplace.id: mapper.map(marketplace) for marketplace in marketplaces
            }
            seeder.seed_warehouses(200)
            seeder.seed_products(200)
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            actual_marketplaces = service.find_all()
            self.assertDictEqual(expected_marketplaces, actual_marketplaces)

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
            expected_marketplaces = {
                marketplace.id: mapper.map(marketplace) for marketplace in marketplaces
            }
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            actual_marketplaces = service.fetch_all_atomic()
            self.assertDictEqual(expected_marketplaces, actual_marketplaces)

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

    def test_update(self):
        updated_name = "qwerty"
        marketplace_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(Marketplace(id=marketplace_id, name="old_name"))
        with self.__db_context.session() as session:
            service = create_marketplace_service(session)
            service.update(marketplace_id, MarketplaceEntity(updated_name))
            session.flush()
            actual = session.execute(
                select(Marketplace).where(Marketplace.id == marketplace_id)
            ).scalar_one()
            self.assertEqual(updated_name, actual.name)


if __name__ == "__main__":
    unittest.main()
