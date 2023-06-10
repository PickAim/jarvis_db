import unittest

from jarvis_db import tables
from jarvis_db.repositores.market.infrastructure.warehouse_repository import (
    WarehouseRepository,
)
from tests.db_context import DbContext


class WarehouseRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as s, s.begin():
            marketplace = tables.Marketplace(name="marketplace#1")
            s.add(marketplace)
            address = tables.Address(
                country="AS", region="QS", street="DD", number="HH", corpus="YU"
            )
            s.add(address)
            s.flush()
            self.__address_id = address.id
            self.__marketplace_id = marketplace.id

    def test_find_by_global_id(self):
        gid = 200
        with self.__db_context.session() as session, session.begin():
            warehouse = tables.Warehouse(
                owner_id=self.__marketplace_id,
                global_id=gid,
                type=0,
                name="qwerty",
                address_id=self.__address_id,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0,
            )
            session.add(warehouse)
        with self.__db_context.session() as session:
            repo = WarehouseRepository(session)
            found = repo.find_by_global_id(gid, self.__marketplace_id)
            self.assertEqual(gid, found.global_id)
