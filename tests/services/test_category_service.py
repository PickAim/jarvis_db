import unittest

from jorm.market.infrastructure import Category as CategoryEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.infrastructure import (
    CategoryTableToJormMapper, NicheTableToJormMapper)
from jarvis_db.repositores.market.infrastructure.category_repository import \
    CategoryRepository
from jarvis_db.services.market.infrastructure.category_service import \
    CategoryService
from jarvis_db.tables import Category, Marketplace
from tests.db_context import DbContext


class CategoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='qwerty')
            session.add(marketplace)
            session.flush()
            self.__marketplace_id = marketplace.id

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            expected_category = CategoryEntity('qwerty')
            service.create(CategoryEntity('qwerty'), self.__marketplace_id)
        with self.__db_context.session() as session:
            actual_category = session.execute(
                select(Category)
                .where(Category.name == expected_category.name)
            ).scalar_one()
            self.assertEqual(expected_category.name, actual_category.name)

    def test_find_by_name(self):
        category_name = 'qwerty'
        with self.__db_context.session() as session, session.begin():
            session.add(Category(name=category_name,
                                 marketplace_id=self.__marketplace_id))
        with self.__db_context.session() as session:
            service = create_service(session)
            category, _ = service.find_by_name(
                category_name, self.__marketplace_id)
            self.assertEqual(category_name, category.name)

    def test_find_all_in_marketplace(self):
        with self.__db_context.session() as session:
            expected_categories = [Category(
                name=f'category_{i}', marketplace_id=self.__marketplace_id) for i in range(1, 11)]
            session.add_all(expected_categories)
            session.flush()
            service = create_service(session)
            actual_categories = service.find_all_in_marketplace(
                self.__marketplace_id).values()
            for expected, actual in zip(expected_categories, actual_categories, strict=True):
                self.assertEqual(expected.name, actual.name)


def create_service(session: Session) -> CategoryService:
    return CategoryService(CategoryRepository(session), CategoryTableToJormMapper(NicheTableToJormMapper()))
