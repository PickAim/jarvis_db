import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jarvis_db.db_config import Base
from jarvis_db import tables
from jarvis_db.repositores.market.infrastructure import CategoryRepository
from jorm.market.infrastructure import Category
from jorm.market.infrastructure import Niche


class CategoryRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.__session = session

    def test_add(self):
        niches_count = 10
        name = 'cat1'
        niches = [Niche(f'n{i}', i, i + 1, i * 1.5, [])
                  for i in range(niches_count)]
        category = Category(name, {
            niche.name: niche for niche in niches
        })
        with self.__session() as session, session.begin():
            repository = CategoryRepository(session)
            repository.add(category)
        with self.__session() as session:
            db_category = session.query(tables.Category)\
                .join(tables.Category.niches)\
                .filter(tables.Category.name == name)\
                .one()
            self.assertTrue(db_category is not None)
            self.assertEqual(db_category.name, name)
            self.assertEqual(len(db_category.niches), niches_count)

    def test_fetch_all(self):
        categories_to_add = 10
        niches_per_category = [i + 1 for i in range(categories_to_add)]
        db_categories = [tables.Category(
            name=f'cat{i}',
            niches=[tables.Niche(
                name=f'niche_cat{i}_n_{j}',
                matketplace_commission=j * 10,
                return_percent=(j + 1) * 10
            )
                for j in range(item)]
        )
            for i, item in enumerate(niches_per_category)]
        with self.__session() as session, session.begin():
            session.add_all(db_categories)
        with self.__session() as session:
            repository = CategoryRepository(session)
            categories = repository.fetch_all()
        self.assertEqual(len(categories), categories_to_add)


if __name__ == '__main__':
    unittest.main()
