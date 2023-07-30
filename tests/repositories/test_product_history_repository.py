import unittest

from jarvis_db import tables
from jarvis_db.repositores.market.items.product_history_repository import (
    ProductHistoryRepository,
)
from tests.db_context import DbContext


class ProductHistoryRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        product_id = 1
        warehouse_id = 1
        warehouse_global_id = 20
        with self.__db_context.session() as s, s.begin():
            marketplace_id = 1
            db_marketplace = tables.Marketplace(id=marketplace_id, name="marketplace_1")
            db_category = tables.Category(
                name="category_id", marketplace=db_marketplace
            )
            db_niche = tables.Niche(
                name="niche_1",
                marketplace_commission=0,
                partial_client_commission=0,
                client_commission=0,
                return_percent=0,
                category=db_category,
            )
            db_niche.category = db_category
            db_product = tables.ProductCard(
                id=product_id,
                name="product_1",
                global_id=1,
                rating=10,
                cost=1,
                niche=db_niche,
                brand="brand",
                seller="seller",
            )
            db_address = tables.Address(
                country="AS", region="QS", street="DD", number="HH", corpus="YU"
            )
            db_warehouse = tables.Warehouse(
                id=warehouse_id,
                owner_id=marketplace_id,
                global_id=warehouse_global_id,
                type=0,
                name="qwerty",
                address=db_address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0,
            )
            s.add(db_product)
            s.add(db_warehouse)
        self.__product_id = product_id

    def test_find_product_histories(self):
        with self.__db_context.session() as session, session.begin():
            histories_to_add = 10
            histories = [
                tables.ProductHistory(cost=10, product_id=self.__product_id)
                for _ in range(histories_to_add)
            ]
            session.add_all(histories)
        with self.__db_context.session() as session:
            repository = ProductHistoryRepository(session)
            histories = repository.find_product_histories(self.__product_id)
            self.assertEqual(histories_to_add, len(histories))


if __name__ == "__main__":
    unittest.main()
