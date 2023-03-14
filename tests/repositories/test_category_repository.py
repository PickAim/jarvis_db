import unittest

from jorm.market.infrastructure import Category, HandlerType, Niche
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import (
    CategoryJormToTableMapper, CategoryTableToJormMapper,
    NicheJormToTableMapper, NicheTableToJormMapper)
from jarvis_db.repositores.market.infrastructure import CategoryRepository


class CategoryRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        marketplace_id = 1
        with session() as s, s.begin():
            s.add(tables.Marketplace(id=marketplace_id, name='marketplace1'))
        self.__session = session
        self.__marketplace_id = marketplace_id

    def test_add(self):
        niches_count = 10
        category_name = 'cat1'
        niches = [
            Niche(f'n{i}',
                  {commission: 0.1 * index for index,
                      commission in enumerate(list(HandlerType))},
                  i * 0.2)
            for i in range(niches_count)]
        category = Category(category_name, {
            niche.name: niche for niche in niches
        })
        with self.__session() as session, session.begin():
            repository = CategoryRepository(session, CategoryTableToJormMapper(
                NicheTableToJormMapper()), CategoryJormToTableMapper(NicheJormToTableMapper()))
            repository.add_category_to_marketplace(
                category, self.__marketplace_id)
        with self.__session() as session:
            db_category = session.execute(
                select(tables.Category)
                .join(tables.Category.niches)
                .filter(tables.Category.name == category_name)
                .distinct()
            ).scalar_one()
            self.assertEqual(db_category.name, category_name)
            for niche, db_niche in zip(niches, db_category.niches, strict=True):
                self.assertEqual(niche.name, db_niche.name)

    def test_add_all(self):
        categories_to_add = 10
        categories = [Category(f'category_{i}', {})
                      for i in range(1, categories_to_add + 1)]
        with self.__session() as session, session.begin():
            repository = CategoryRepository(
                session, CategoryTableToJormMapper(NicheTableToJormMapper()),
                CategoryJormToTableMapper(NicheJormToTableMapper()))
            repository.add_all_categories_to_marketplace(
                categories, self.__marketplace_id)
        with self.__session() as session:
            db_categories = session.execute(
                select(tables.Category)
            ).scalars().all()
            for jorm_category, db_category in zip(categories, db_categories, strict=True):
                self.assertEqual(jorm_category.name, db_category.name)

    def test_fetch_all(self):
        categories_to_add = 10
        niches_per_category = [i + 1 for i in range(categories_to_add)]
        db_categories = [tables.Category(
            name=f'cat{i}',
            niches=[tables.Niche(
                name=f'niche_cat{i}_n_{j}',
                marketplace_commission=j * 10,
                client_commission=j * 20,
                partial_client_commission=j * 30,
                return_percent=(j + 1) * 10,
            )
                for j in range(item)],
            marketplace_id=self.__marketplace_id
        )
            for i, item in enumerate(niches_per_category)]
        with self.__session() as session, session.begin():
            session.add_all(db_categories)
        with self.__session() as session:
            repository = CategoryRepository(session, CategoryTableToJormMapper(
                NicheTableToJormMapper()), CategoryJormToTableMapper(NicheJormToTableMapper()))
            categories = repository.fetch_marketplace_categories(
                self.__marketplace_id)
        self.assertEqual(len(categories), categories_to_add)
        for category, expected_niches in zip(categories.values(), niches_per_category, strict=True):
            self.assertEqual(len(category.niches), expected_niches)


if __name__ == '__main__':
    unittest.main()
