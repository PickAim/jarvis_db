from typing import cast
import unittest

from jorm.market.infrastructure import Marketplace as MarketplaceEntity
from sqlalchemy import select
from jarvis_db.factories.services import create_marketplace_service

from jarvis_db.tables import Marketplace
from tests.db_context import DbContext


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
