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
            self.assertEqual(expected, actual)

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
                self.assertEqual(expected, actual)

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
                self.assertEqual(expected, actual)


def create_service(session: Session) -> ProductCardService:
    return ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())