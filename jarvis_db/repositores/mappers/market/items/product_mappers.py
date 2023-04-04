from jarvis_db.core import Mapper
from jorm.market.items import Product, ProductHistory
from jarvis_db import tables


class ProductJormToTableMapper(Mapper[Product, tables.ProductCard]):
    def map(self, value: Product) -> tables.ProductCard:
        return tables.ProductCard(
            name=value.name,
            global_id=value.global_id,
            cost=value.cost,
            rating=int(value.rating * 100)
        )


class ProductTableToJormMapper(Mapper[tables.ProductCard, Product]):
    def map(self, value: tables.ProductCard) -> Product:
        return Product(
            name=value.name,
            global_id=value.global_id,
            cost=value.cost,
            history=ProductHistory(),
            rating=float(value.rating) / 100
        )
