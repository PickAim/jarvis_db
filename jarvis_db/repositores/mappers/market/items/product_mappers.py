from jarvis_db.core import Mapper
from jorm.market.items import Product
from jarvis_db import tables


class ProductJormToTableMapper(Mapper[Product, tables.ProductCard]):
    def map(self, value: Product) -> tables.ProductCard:
        return tables.ProductCard(
            name=value.name,
            article=value.article,
            cost=value.cost
        )


class ProductTableToJormMapper(Mapper[tables.ProductCard, Product]):
    def map(self, value: tables.ProductCard) -> Product:
        return Product(
            name=value.name,
            article=value.article,
            cost=value.cost
        )
