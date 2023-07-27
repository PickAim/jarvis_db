from jorm.market.items import Product, ProductHistory, ProductHistoryUnit

from jarvis_db import tables
from jarvis_db.core import Mapper


class ProductJormToTableMapper(Mapper[Product, tables.ProductCard]):
    def map(self, value: Product) -> tables.ProductCard:
        return tables.ProductCard(
            name=value.name,
            global_id=value.global_id,
            cost=value.cost,
            rating=int(value.rating * 100),
        )


class ProductTableToJormMapper(Mapper[tables.ProductCard, Product]):
    def __init__(
        self, history_mapper: Mapper[tables.ProductHistory, ProductHistoryUnit]
    ):
        self.__history_mapper = history_mapper

    def map(self, value: tables.ProductCard) -> Product:
        return Product(
            name=value.name,
            global_id=value.global_id,
            cost=value.cost,
            history=ProductHistory(
                (
                    self.__history_mapper.map(history_unit)
                    for history_unit in value.histories
                )
            ),
            rating=float(value.rating) / 100,
            brand=value.brand,
            seller=value.seller,
            niche_name=value.niche.name,
            category_name=value.niche.category.name,
        )
