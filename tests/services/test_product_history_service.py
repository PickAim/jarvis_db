import unittest
from datetime import datetime

from jorm.market.items import ProductHistory, ProductHistoryUnit, StorageDict
from jorm.support.types import SpecifiedLeftover
from sqlalchemy import select

from jarvis_db import schemas
from jarvis_db.factories.mappers import create_product_history_mapper
from jarvis_db.factories.services import create_product_history_service
from jarvis_db.schemas import (
    Address,
    Category,
    Leftover,
    Marketplace,
    Niche,
    ProductCard,
    Warehouse,
)
from tests.db_context import DbContext


class ProductHistoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name="marketplace#1")
            category = Category(name="category#1", marketplace=marketplace)
            niche = Niche(
                name="niche#1",
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category,
            )
            product = ProductCard(
                name="product#1",
                global_id=12,
                rating=12,
                cost=230,
                niche=niche,
                brand="brand",
                seller="seller",
            )
            session.add(product)
            session.flush()
            self.__product_id = product.id
            address = Address(
                country="AS", region="QS", street="DD", number="HH", corpus="YU"
            )
            warehouse = Warehouse(
                marketplace=marketplace,
                global_id=200,
                type=0,
                name="qwerty",
                address=address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0,
            )
            session.add(warehouse)
            session.flush()
            self.__warehouse_id = warehouse.id
            self.__warehouse_gid = warehouse.global_id

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            service = create_product_history_service(session)
            units_to_add = 10
            leftovers_per_unit = 5
            expected = ProductHistory(
                [
                    ProductHistoryUnit(
                        cost=10,
                        unit_date=datetime(2020, 2, 12),
                        leftover=StorageDict(
                            {
                                self.__warehouse_gid: [
                                    SpecifiedLeftover("xl", 5)
                                    for _ in range(leftovers_per_unit)
                                ]
                            }
                        ),
                    )
                    for _ in range(units_to_add)
                ]
            )
            service.create(expected, self.__product_id)
        with self.__db_context.session() as session:
            mapper = create_product_history_mapper()
            histories = (
                session.execute(
                    select(schemas.ProductHistory)
                    .outerjoin(schemas.ProductHistory.leftovers)
                    .where(schemas.ProductHistory.product_id == self.__product_id)
                    .distinct()
                )
                .scalars()
                .all()
            )
            actual = ProductHistory((mapper.map(unit) for unit in histories))
            self.assertEqual(expected, actual)

    def test_find_history(self):
        mapper = create_product_history_mapper()
        with self.__db_context.session() as session, session.begin():
            units_to_add = 10
            leftovers_per_unit = 5
            history_units = [
                schemas.ProductHistory(
                    cost=200,
                    date=datetime(2022, 2, 1),
                    product_id=self.__product_id,
                    leftovers=[
                        Leftover(
                            type="xl", quantity=10, warehouse_id=self.__warehouse_id
                        )
                        for _ in range(leftovers_per_unit)
                    ],
                )
                for _ in range(units_to_add)
            ]
            session.add_all(history_units)
            session.flush()
            expected = ProductHistory((mapper.map(unit) for unit in history_units))
        with self.__db_context.session() as session:
            service = create_product_history_service(session)
            actual = service.find_product_history(self.__product_id)
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
