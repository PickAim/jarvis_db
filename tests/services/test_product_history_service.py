import unittest
from datetime import datetime

from jorm.market.items import ProductHistory, ProductHistoryUnit, StorageDict
from jorm.support.types import SpecifiedLeftover
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.repositores.mappers.market.items import \
    ProductHistoryTableToJormMapper
from jarvis_db.repositores.mappers.market.items.leftover_mappers import \
    LeftoverTableToJormMapper
from jarvis_db.repositores.market.infrastructure.warehouse_repository import \
    WarehouseRepository
from jarvis_db.repositores.market.items.leftover_repository import \
    LeftoverRepository
from jarvis_db.repositores.market.items.product_history_repository import \
    ProductHistoryRepository
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_history_service import \
    ProductHistoryService
from jarvis_db.services.market.items.product_history_unit_service import \
    ProductHistoryUnitService
from jarvis_db.tables import (Address, Category, Leftover, Marketplace, Niche,
                              ProductCard, Warehouse)
from tests.db_context import DbContext


class ProductHistoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='marketplace#1')
            category = Category(name='category#1', marketplace=marketplace)
            niche = Niche(
                name='niche#1',
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category)
            product = ProductCard(
                name='product#1', global_id=12, rating=12, cost=230, niche=niche)
            session.add(product)
            session.flush()
            self.__product_id = product.id
            address = Address(
                country='AS',
                region='QS',
                street='DD',
                number='HH',
                corpus='YU'
            )
            warehouse = Warehouse(
                owner=marketplace,
                global_id=200,
                type=0,
                name='qwerty',
                address=address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0
            )
            session.add(warehouse)
            session.flush()
            self.__warehouse_id = warehouse.id
            self.__warehouse_gid = warehouse.global_id

    def test_add(self):
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            units_to_add = 10
            leftovers_per_unit = 5
            product_history = ProductHistory(
                [ProductHistoryUnit(
                    cost=10,
                    unit_date=datetime(2020, 2, 12),
                    leftover=StorageDict(
                        {self.__warehouse_gid: [SpecifiedLeftover(
                            'xl', 5) for _ in range(leftovers_per_unit)]}
                    )
                ) for _ in range(units_to_add)])
            service.add_product_history(product_history, self.__product_id)
        with self.__db_context.session() as session:
            histories = session.execute(
                select(tables.ProductHistory)
                .outerjoin(tables.ProductHistory.leftovers)
                .where(tables.ProductHistory.product_id == self.__product_id)
                .distinct()
            ).scalars().all()
            self.assertEqual(units_to_add, len(histories))
            for history in histories:
                self.assertEqual(leftovers_per_unit, len(history.leftovers))

    def test_find_history(self):
        with self.__db_context.session() as session, session.begin():
            units_to_add = 10
            leftovers_per_unit = 5
            history_units = [tables.ProductHistory(
                cost=200,
                date=datetime(2022, 2, 1),
                product_id=self.__product_id,
                leftovers=[Leftover(type='xl', quantity=10, warehouse_id=self.__warehouse_id)
                           for _ in range(leftovers_per_unit)]) for _ in range(units_to_add)]
            session.add_all(history_units)
        with self.__db_context.session() as session:
            service = create_service(session)
            histories = service.find_product_history(self.__product_id).history
            self.assertEqual(units_to_add, len(histories))
            for unit in histories:
                self.assertEqual(leftovers_per_unit, sum(
                    (len(leftovers) for leftovers in unit.leftover.values())))


def create_service(session: Session) -> ProductHistoryService:
    unit_service = ProductHistoryUnitService(
        ProductHistoryRepository(session))
    return ProductHistoryService(unit_service, LeftoverService(
        LeftoverRepository(session), WarehouseRepository(session), unit_service),
                                 ProductHistoryRepository(session),
                                 ProductHistoryTableToJormMapper(LeftoverTableToJormMapper()))


if __name__ == '__main__':
    unittest.main()
