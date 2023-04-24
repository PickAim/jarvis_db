import unittest
from jarvis_db.repositores.market.infrastructure.category_repository import CategoryRepository

from jarvis_db.tables import Category, Marketplace
from tests.db_context import DbContext


class CategoryRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        marketplace_id = 1
        with self.__db_context.session() as s, s.begin():
            s.add(Marketplace(id=marketplace_id, name='marketplace1'))
        self.__marketplace_id = marketplace_id

    def test_find_by_name(self):
        category_name = 'qwerty'
        with self.__db_context.session() as session, session.begin():
            session.add(
                Category(name=category_name, marketplace_id=self.__marketplace_id))
        with self.__db_context.session() as session:
            repository = CategoryRepository(session)
            found = repository.find_by_name(
                category_name, self.__marketplace_id)
            assert (found is not None)
            self.assertEqual(category_name, found.name)


if __name__ == '__main__':
    unittest.main()
