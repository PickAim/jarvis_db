import unittest
from datetime import datetime

from jorm.market.items import ProductHistory, ProductHistoryUnit, StorageDict
from jorm.support.types import SpecifiedLeftover
from sqlalchemy import select
from jarvis_db import tables

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
from jarvis_db.tables import (Address, Category, Marketplace, Niche,
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
                name='product#1', article=12, cost=230, niche=niche)
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
            self.__warehouse_gid = warehouse.global_id

    def test_add(self):
        with self.__db_context.session() as session, session.begin():
            unit_service = ProductHistoryUnitService(
                ProductHistoryRepository(session))
            service = ProductHistoryService(unit_service, LeftoverService(
                LeftoverRepository(session), WarehouseRepository(session), unit_service))
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
