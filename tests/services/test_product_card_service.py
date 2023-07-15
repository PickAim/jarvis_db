import unittest

from jorm.market.items import Product
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.items.product_mappers import (
    ProductTableToJormMapper,
)
from jarvis_db.repositores.market.items.product_card_repository import (
    ProductCardRepository,
)
from jarvis_db.services.market.items.product_card_service import ProductCardService
from tests.fixtures import AlchemySeeder
from tests.services.test_product_history_service import (
    create_service as create_history_service,
)
from jarvis_db.tables import Category, Marketplace, Niche, ProductCard
from tests.db_context import DbContext


class ProductCardServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_niches(1)
            niche = session.execute(select(Niche)).scalar_one()
            self.__niche_id = niche.id
            self.__niche_name = niche.name
            self.__category_name = niche.category.name

    def assert_product_equal(self, expected: Product, actual: Product):
        self.assertEqual(expected.name, actual.name)
        self.assertEqual(expected.cost, actual.cost)
        self.assertEqual(expected.global_id, actual.global_id)
        self.assertEqual(expected.rating, actual.rating)
        self.assertEqual(expected.brand, actual.brand)
        self.assertEqual(expected.seller, actual.seller)

    def test_create(self):
        expected = Product(
            "qwerty", 100, 200, 5.0, "brand", "seller", "niche_name", "category_name"
        )
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            service.create_product(expected, self.__niche_id)
        with self.__db_context.session() as session:
            found = session.execute(
                select(ProductCard)
                .where(ProductCard.niche_id == self.__niche_id)
                .where(ProductCard.name == expected.name)
            ).scalar_one()
            mapper = ProductTableToJormMapper()
            actual = mapper.map(found)
            self.assert_product_equal(expected, actual)
            self.assertEqual(self.__niche_name, actual.niche_name)
            self.assertEqual(self.__category_name, actual.category_name)

    def test_create_many(self):
        expected_products = [
            Product(
                f"product_{i}",
                100 + 10 * i,
                200 + 20 * i,
                5.0 + i,
                f"brand_{i}",
                f"seller_{i}",
                "niche_name",
                "category_name",
            )
            for i in range(10)
        ]
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            service.create_products(expected_products, self.__niche_id)
        with self.__db_context.session() as session:
            found = (
                session.execute(
                    select(ProductCard).where(ProductCard.niche_id == self.__niche_id)
                )
                .scalars()
                .all()
            )
            mapper = ProductTableToJormMapper()
            actual_products = [mapper.map(product) for product in found]
            for expected, actual in zip(
                expected_products, actual_products, strict=True
            ):
                self.assert_product_equal(expected, actual)
                self.assertEqual(self.__niche_name, actual.niche_name)
                self.assertEqual(self.__category_name, actual.category_name)

    def test_find_all_in_niche(self):
        mapper = ProductTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_niches(2)
            seeder.seed_products(100)
            products = session.execute(select(ProductCard)).scalars().all()
            expected_products = [mapper.map(product) for product in products if product.niche_id == self.__niche_id]
        with self.__db_context.session() as session:
            service = create_service(session)
            actual_products = list(service.find_all_in_niche(self.__niche_id).values())
            for expected, actual in zip(
                expected_products, actual_products, strict=True
            ):
                self.assert_product_equal(expected, actual)
                self.assertEqual(self.__niche_name, actual.niche_name)
                self.assertEqual(self.__category_name, actual.category_name)

    def test_filter_existing_ids(self):
        existing_ids = [i for i in range(100, 111)]
        with self.__db_context.session() as session, session.begin():
            products = (
                ProductCard(
                    id=index,
                    name=f"product_{global_id}",
                    global_id=global_id,
                    cost=100 * global_id,
                    rating=5.0 + global_id,
                    niche_id=self.__niche_id,
                    brand=f"brand_{index}",
                    seller=f"seller_{index}",
                )
                for index, global_id in enumerate(existing_ids, start=1)
            )
            session.add_all(products)
        new_ids = [i for i in range(200, 211)]
        with self.__db_context.session() as session:
            service = create_service(session)
            filtered_ids = service.filter_existing_global_ids(
                self.__niche_id, [*existing_ids, *new_ids]
            )
            self.assertEqual(sorted(new_ids), sorted(filtered_ids))

    def test_update(self):
        product_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(
                ProductCard(
                    id=product_id,
                    name="product_100",
                    global_id=20,
                    cost=10,
                    rating=5.0,
                    niche_id=self.__niche_id,
                    brand="brand",
                    seller="seller",
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            expected = Product(
                "product_1",
                100,
                25,
                8.0,
                "new_brand",
                "eew_seller",
                "niche_name",
                "category_name",
            )
            service.update(product_id, expected)
            product = session.execute(
                select(ProductCard).where(ProductCard.id == product_id)
            ).scalar_one()
            mapper = ProductTableToJormMapper()
            actual = mapper.map(product)
            self.assert_product_equal(expected, actual)
            self.assertEqual(self.__niche_name, actual.niche_name)
            self.assertEqual(self.__category_name, actual.category_name)


def create_service(session: Session) -> ProductCardService:
    history_service = create_history_service(session)
    return ProductCardService(
        ProductCardRepository(session), history_service, ProductTableToJormMapper()
    )
