import unittest

from jorm.market.items import Product
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.items.product_mappers import \
    ProductTableToJormMapper
from jarvis_db.repositores.market.items.product_card_repository import \
    ProductCardRepository
from jarvis_db.services.market.items.product_card_service import \
    ProductCardService
from jarvis_db.tables import Category, Marketplace, Niche, ProductCard
from tests.db_context import DbContext


class ProductCardServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='qwerty')
            category = Category(name='qwerty', marketplace=marketplace)
            niche = Niche(
                name='niche#1',
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category)
            session.add(niche)
            session.flush()
            self.__niche_id = niche.id

    def test_create(self):
        expected = Product('qwerty', 100, 200, 5.0)
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
            self.assertEqual(expected.name, actual.name)
            self.assertEqual(expected.cost, actual.cost)
            self.assertEqual(expected.global_id, actual.global_id)
            self.assertEqual(expected.rating, actual.rating)

    def test_create_many(self):
        expected_products = [
            Product(f'product_{i}', 100 + 10 * i, 200 + 20 * i, 5.0 + i) for i in range(10)]
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            service.create_products(expected_products, self.__niche_id)
        with self.__db_context.session() as session:
            found = session.execute(
                select(ProductCard)
                .where(ProductCard.niche_id == self.__niche_id)
            ).scalars().all()
            mapper = ProductTableToJormMapper()
            actual_products = [mapper.map(product) for product in found]
            for expected, actual in zip(expected_products, actual_products, strict=True):
                self.assertEqual(expected.name, actual.name)
                self.assertEqual(expected.cost, actual.cost)
                self.assertEqual(expected.global_id, actual.global_id)
                self.assertEqual(expected.rating, actual.rating)

    def test_find_all_in_niche(self):
        mapper = ProductTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            products = [ProductCard(
                name=f'product_{i}',
                global_id=200 + i,
                cost=100 * i,
                rating=5.0 + i,
                niche_id=self.__niche_id
            ) for i in range(1, 11)]
            session.add_all(products)
            session.flush()
            expected_products = [mapper.map(product) for product in products]
        with self.__db_context.session() as session:
            service = create_service(session)
            actual_products = service.find_all_in_niche(
                self.__niche_id).values()
            for expected, actual in zip(expected_products, actual_products, strict=True):
                self.assertEqual(expected.name, actual.name)
                self.assertEqual(expected.cost, actual.cost)
                self.assertEqual(expected.global_id, actual.global_id)
                self.assertEqual(expected.rating, actual.rating)

    def test_filter_existing_ids(self):
        existing_ids = [i for i in range(100, 111)]
        with self.__db_context.session() as session, session.begin():
            products = (ProductCard(
                id=index,
                name=f'product_{global_id}',
                global_id=global_id,
                cost=100 * global_id,
                rating=5.0 + global_id,
                niche_id=self.__niche_id
            ) for index, global_id in enumerate(existing_ids, start=1))
            session.add_all(products)
        new_ids = [i for i in range(200, 211)]
        with self.__db_context.session() as session:
            service = create_service(session)
            filtered_ids = service.filter_existing_global_ids(
                [*existing_ids, *new_ids], self.__niche_id)
            self.assertEqual(sorted(new_ids), sorted(filtered_ids))

    def test_update(self):
        product_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(ProductCard(
                id=product_id,
                name='product_100',
                global_id=20,
                cost=10,
                rating=5.0,
                niche_id=self.__niche_id
            ))
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            expected = Product(
                'product_1',
                100,
                25,
                8.0
            )
            service.update(product_id, expected)
            product = session.execute(
                select(ProductCard)
                .where(ProductCard.id == product_id)
            ).scalar_one()
            mapper = ProductTableToJormMapper()
            actual = mapper.map(product)
            self.assertEqual(expected.name, actual.name)
            self.assertEqual(expected.cost, actual.cost)
            self.assertEqual(expected.global_id, actual.global_id)
            self.assertEqual(expected.rating, actual.rating)


def create_service(session: Session) -> ProductCardService:
    return ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
