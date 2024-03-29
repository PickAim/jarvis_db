import unittest

from jorm.market.infrastructure import Category as CategoryEntity
from sqlalchemy import select
from sqlalchemy.orm import noload

from jarvis_db.factories.mappers import create_category_table_mapper
from jarvis_db.factories.services import create_category_service
from jarvis_db.schemas import Category, Marketplace, Niche
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class CategoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name="qwerty")
            session.add(marketplace)
            session.flush()
            self.__marketplace_id = marketplace.id

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            service = create_category_service(session)
            expected_category = CategoryEntity("qwerty")
            service.create(CategoryEntity("qwerty"), self.__marketplace_id)
        with self.__db_context.session() as session:
            actual_category = session.execute(
                select(Category).where(Category.name == expected_category.name)
            ).scalar_one()
            self.assertEqual(expected_category.name, actual_category.name)

    def test_find_by_id(self):
        category_id = 100
        mapper = create_category_table_mapper()
        with self.__db_context.session() as session, session.begin():
            category = Category(
                id=category_id,
                name="category_name",
                marketplace_id=self.__marketplace_id,
            )
            session.add(category)
            session.flush()
            expected = mapper.map(category)
            self.assertEqual(0, len(expected.niches))
            seeder = AlchemySeeder(session)
            seeder.seed_products(500)
        with self.__db_context.session() as session:
            service = create_category_service(session)
            actual = service.find_by_id(category_id)
            self.assertEqual(expected, actual)

    def test_find_by_name(self):
        category_id = 100
        category_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(
                Category(
                    id=category_id,
                    name=category_name,
                    marketplace_id=self.__marketplace_id,
                )
            )
            session.flush()
            seeder = AlchemySeeder(session)
            seeder.seed_products(2000)
        with self.__db_context.session() as session:
            service = create_category_service(session)
            category_tuple = service.find_by_name(category_name, self.__marketplace_id)
            assert category_tuple is not None
            category, actual_category_id = category_tuple
            self.assertEqual(category_id, actual_category_id)
            self.assertEqual(category_name, category.name)
            self.assertEqual(0, len(category.niches))

    def test_find_all_in_marketplace(self):
        mapper = create_category_table_mapper()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(2)
            seeder.seed_categories(10)
            seeder.seed_products(2000)
            expected_categories = {
                category.id: mapper.map(category)
                for category in session.execute(
                    select(Category).options(noload(Category.niches))
                )
                .scalars()
                .all()
                if category.marketplace_id == self.__marketplace_id
            }
        with self.__db_context.session() as session:
            service = create_category_service(session)
            actual_categories = service.find_all_in_marketplace(self.__marketplace_id)
            self.assertDictEqual(expected_categories, actual_categories)
            for category in actual_categories.values():
                self.assertEqual(0, len(category.niches))

    def test_fetch_all_in_marketplace_atomic(self):
        with self.__db_context.session() as session:
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(2)
            seeder.seed_categories(10)
            seeder.seed_niches(40)
            mapper = create_category_table_mapper()
            expected_categories = {
                category.id: mapper.map(category)
                for category in session.execute(
                    select(Category)
                    .outerjoin(Category.niches)
                    .outerjoin(Niche.products)
                    .distinct()
                )
                .scalars()
                .all()
                if category.marketplace_id == self.__marketplace_id
            }
            service = create_category_service(session)
            actual_categories = service.fetch_all_in_marketplace_atomic(
                self.__marketplace_id
            )
            self.assertDictEqual(expected_categories, actual_categories)

    def test_exists_with_name_returns_true(self):
        category_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(
                Category(name=category_name, marketplace_id=self.__marketplace_id)
            )
        with self.__db_context.session() as session:
            service = create_category_service(session)
            exists = service.exists_with_name(category_name, self.__marketplace_id)
            self.assertTrue(exists)

    def test_exists_with_name_returns_false(self):
        category_name = "qwerty"
        with self.__db_context.session() as session:
            service = create_category_service(session)
            exists = service.exists_with_name(category_name, self.__marketplace_id)
            self.assertFalse(exists)

    def test_filter_existing_names(self):
        existing_names = [f"category_{i}" for i in range(1, 11)]
        with self.__db_context.session() as session, session.begin():
            session.add_all(
                (
                    Category(name=category_name, marketplace_id=self.__marketplace_id)
                    for category_name in existing_names
                )
            )
        new_names = [f"new_category_{i}" for i in range(1, 11)]
        names_to_filter = [*existing_names, *new_names]
        with self.__db_context.session() as session:
            service = create_category_service(session)
            filtered_names = service.filter_existing_names(
                names_to_filter, self.__marketplace_id
            )
            self.assertEqual(sorted(new_names), sorted(filtered_names))

    def test_update(self):
        category_id = 100
        updated_name = "new_name"
        with self.__db_context.session() as session, session.begin():
            session.add(
                Category(
                    id=category_id,
                    marketplace_id=self.__marketplace_id,
                    name="old_name",
                )
            )
        with self.__db_context.session() as session:
            service = create_category_service(session)
            service.update(category_id, CategoryEntity(updated_name))
            session.flush()
            actual = session.execute(
                select(Category).where(Category.id == category_id)
            ).scalar_one()
            self.assertEqual(updated_name, actual.name)


if __name__ == "__main__":
    unittest.main()
