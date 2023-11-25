from jorm.market.items import Product, ProductHistory, ProductHistoryUnit

from jarvis_db import schemas
from jarvis_db.core import Mapper


class ProductJormToTableMapper(Mapper[Product, schemas.ProductCard]):
    def map(self, value: Product) -> schemas.ProductCard:
        return schemas.ProductCard(
            name=value.name,
            global_id=value.global_id,
            cost=value.cost,
            rating=int(value.rating * 100),
        )


class ProductTableToJormMapper(Mapper[schemas.ProductCard, Product]):
    def __init__(
        self, history_mapper: Mapper[schemas.ProductHistory, ProductHistoryUnit]
    ):
        self.__history_mapper = history_mapper

    def map(self, value: schemas.ProductCard) -> Product:
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
            category_niche_list=[
                (niche.category.name, niche.name) for niche in value.niches
            ],
        )
