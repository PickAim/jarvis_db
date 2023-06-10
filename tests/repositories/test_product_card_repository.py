import unittest

from jarvis_db import tables
from tests.db_context import DbContext


class ProductCardRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        niche_id = 1
        with self.__db_context.session() as s, s.begin():
            marketplace = tables.Marketplace(name="marketplace_1")
            category = tables.Category(name="category_1", marketplace=marketplace)
            niche = tables.Niche(
                id=niche_id,
                name="niche_1",
                marketplace_commission=10,
                partial_client_commission=20,
                client_commission=30,
                return_percent=15,
                category=category,
            )
            niche.products = [
                tables.ProductCard(
                    name=f"product#{i}",
                    article=i,
                    cost=i * 10,
                )
                for i in range(100, 111)
            ]
            category.marketplace = marketplace
            s.add(marketplace)
        self.__niche_id = niche_id


if __name__ == "__main__":
    unittest.main()
