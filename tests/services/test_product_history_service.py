import unittest
from datetime import datetime

from jorm.market.items import ProductHistory, ProductHistoryUnit, StorageDict
from jorm.support.types import SpecifiedLeftover
from sqlalchemy import select

from jarvis_db import schemas
from jarvis_db.factories.mappers import create_product_history_mapper
from jarvis_db.factories.services import create_product_history_service
from jarvis_db.schemas import (
    Leftover,
    ProductCard,
    Warehouse,
)
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class ProductHistoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            seeder.seed_categories(1)
            seeder.seed_niches(1)
            seeder.seed_warehouses(1)
            seeder.seed_products(1)
            self.__product_id = session.execute(select(ProductCard.id)).scalar_one()
            self.__warehouse_id = session.execute(select(Warehouse.id)).scalar_one()
            self.__warehouse_gid = session.execute(
                select(Warehouse.global_id)
            ).scalar_one()

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
