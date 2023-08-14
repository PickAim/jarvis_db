import unittest
from typing import cast

from jorm.market.infrastructure import Category as CategoryEntity
from sqlalchemy import select

from jarvis_db.factories.mappers import create_category_table_mapper
from jarvis_db.factories.services import create_category_service
from jarvis_db.schemas import Category, Marketplace, Niche
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class CategoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
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
        with self.__db_context.session() as session:
            service = create_category_service(session)
            actual = service.find_by_id(category_id)
            self.assertEqual(expected, actual)

    def test_find_by_name(self):
        category_name = "qwerty"
        with self.__db_context.session() as session, session.begin():
            session.add(
                Category(name=category_name, marketplace_id=self.__marketplace_id)
            )
        with self.__db_context.session() as session:
            service = create_category_service(session)
            category, _ = cast(
                tuple[Category, int],
                service.find_by_name(category_name, self.__marketplace_id),
            )
            self.assertEqual(category_name, category.name)

    def test_find_all_in_marketplace(self):
        with self.__db_context.session() as session:
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(2)
            seeder.seed_categories(10)
            mapper = create_category_table_mapper()
            expected_categories = [
                mapper.map(category)
                for category in session.execute(select(Category)).scalars().all()
                if category.marketplace_id == self.__marketplace_id
            ]
            service = create_category_service(session)
            actual_categories = service.find_all_in_marketplace(
                self.__marketplace_id
            ).values()
            for expected, actual in zip(
                expected_categories, actual_categories, strict=True
            ):
                self.assertEqual(expected, actual)

    def test_fetch_all_in_marketplace_atomic(self):
        with self.__db_context.session() as session:
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(2)
            seeder.seed_categories(10)
            seeder.seed_niches(40)
            mapper = create_category_table_mapper()
            expected_categories = [
                mapper.map(category)
                for category in session.execute(
                    select(Category)
                    .outerjoin(Category.niches)
                    .outerjoin(Niche.products)
                    .distinct()
                )
                .scalars()
                .all()
                if category.marketplace_id == self.__marketplace_id
            ]
            service = create_category_service(session)
            actual_categories = list(
                service.fetch_all_in_marketplace_atomic(self.__marketplace_id).values()
            )
            for expected, actual in zip(
                expected_categories, actual_categories, strict=True
            ):
                self.assertEqual(expected, actual)

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
