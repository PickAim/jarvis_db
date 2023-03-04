import unittest

from jorm.market.items import Product, ProductHistory
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.items import (
    ProductJormToTableMapper, ProductTableToJormMapper)
from jarvis_db.repositores.market.items import ProductCardRepository


class ProductCardRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        niche_id = 1
        with session() as s, s.begin():
            marketplace = tables.Marketplace(name='marketplace_1')
            category = tables.Category(
                name='category_1', marketplace=marketplace)
            niche = tables.Niche(
                id=niche_id,
                name='niche_1',
                marketplace_commission=10,
                partial_client_commission=20,
                client_commission=30,
                return_percent=15,
                category=category
            )
            niche.products = [tables.ProductCard(
                name=f'product#{i}', article=i, cost=i * 10,) for i in range(100, 111)]
            category.marketplace = marketplace
            s.add(marketplace)
        self.__session = session
        self.__niche_id = niche_id

    def test_add_product(self):
        product = Product('jorm product', 12500, 100, ProductHistory())
        with self.__session() as session, session.begin():
            repository = ProductCardRepository(
                session, ProductTableToJormMapper(), ProductJormToTableMapper())
            repository.add_product_to_niche(
                product, self.__niche_id)
        with self.__session() as session:
            db_product = session.execute(
                select(tables.ProductCard)
                .where(tables.ProductCard.name == product.name)
            ).scalar_one()
            self.assertEqual(db_product.name, product.name)
            self.assertEqual(db_product.cost, product.cost)
            self.assertEqual(db_product.article, product.article)

    def test_add_products(self):
        products_to_add = 5
        products = [Product(f'jorm product #{i}', i * 100, i * 10, ProductHistory())
                    for i in range(1, products_to_add + 1)]
        with self.__session() as session, session.begin():
            repository = ProductCardRepository(
                session, ProductTableToJormMapper(), ProductJormToTableMapper())
            repository.add_products_to_niche(
                products, self.__niche_id)
        with self.__session() as session:
            product_names = (product.name for product in products)
            db_products = session.execute(
                select(tables.ProductCard)
                .where(tables.ProductCard.name.in_(product_names))
            ).scalars().all()
            for product, db_product in zip(products, db_products, strict=True):
                self.assertEqual(db_product.name, product.name)
                self.assertEqual(db_product.cost, product.cost)
                self.assertEqual(db_product.article, product.article)


if __name__ == '__main__':
    unittest.main()
