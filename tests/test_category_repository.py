import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jarvis_db.db_config import Base
from jarvis_db import tables
from jarvis_db.repositores.market.infrastructure import CategoryRepository
from jarvis_db.repositores.mappers.market.infrastructure import CategoryJormToTableMapper
from jarvis_db.repositores.mappers.market.infrastructure import CategoryTableToJormMapper
from jarvis_db.repositores.mappers.market.infrastructure import NicheJormToTableMapper
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper
from jorm.market.infrastructure import Category
from jorm.market.infrastructure import Niche
from jorm.market.infrastructure import HandlerType


class CategoryRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.__session = session

    def test_add(self):
        niches_count = 10
        name = 'cat1'
        niches = [Niche(f'n{i}',
                        {commission: 0.1 * index for index,
                            commission in enumerate(list(HandlerType))},
                        i * 0.2,
                        [])
                  for i in range(niches_count)]
        category = Category(name, {
            niche.name: niche for niche in niches
        })
        with self.__session() as session, session.begin():
            repository = CategoryRepository(session, CategoryTableToJormMapper(
                NicheTableToJormMapper()), CategoryJormToTableMapper(NicheJormToTableMapper()))
            repository.add(category)
        with self.__session() as session:
            db_category: tables.Category = session.query(tables.Category)\
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
                client_commission=j * 20,
                partial_client_commission=j * 30,
                return_percent=(j + 1) * 10
            )
                for j in range(item)]
        )
            for i, item in enumerate(niches_per_category)]
        with self.__session() as session, session.begin():
            session.add_all(db_categories)
        with self.__session() as session:
            repository = CategoryRepository(session, CategoryTableToJormMapper(
                NicheTableToJormMapper()), CategoryJormToTableMapper(NicheJormToTableMapper()))
            categories = repository.fetch_all()
        self.assertEqual(len(categories), categories_to_add)
        for category, expected_niches in zip(categories, niches_per_category, strict=True):
            self.assertEqual(len(category.niches), expected_niches)


if __name__ == '__main__':
    unittest.main()
