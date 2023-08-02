import unittest

from jarvis_db import schemas
from tests.db_context import DbContext


class NicheRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        marketplace_id = 1
        category_id = 1
        db_marketplace = schemas.Marketplace(id=marketplace_id, name="marketplace_1")
        db_category = schemas.Category(
            id=category_id, name="category_1", marketplace=db_marketplace
        )
        with self.__db_context.session() as s, s.begin():
            s.add(db_category)
        self.__marketplace_id = marketplace_id
        self.__category_id = category_id

    def test_add_niche_by_category_name(self):
        ...

    def test_add_all_niches_by_category_name(self):
        ...

    def test_fetch_all_by_category(self):
        ...

    def test_find_by_marketplace(self):
        ...


if __name__ == "__main__":
    unittest.main()
