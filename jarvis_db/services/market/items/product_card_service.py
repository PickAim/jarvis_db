from typing import Iterable

from jorm.market.items import Product

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.items.product_card_repository import (
    ProductCardRepository,
)
from jarvis_db.tables import ProductCard


class ProductCardService:
    def __init__(
        self,
        product_card_repository: ProductCardRepository,
        table_mapper: Mapper[ProductCard, Product],
    ):
        self.__product_card_repository = product_card_repository
        self.__table_mapper = table_mapper

    def create_product(self, product: Product, niche_id: int):
        db_product = ProductCard(
            name=product.name,
            global_id=product.global_id,
            cost=product.cost,
            rating=int(product.rating * 100),
            niche_id=niche_id,
            brand=product.brand,
            seller=product.seller,
        )
        self.__product_card_repository.add(db_product)

    def create_products(self, products: Iterable[Product], niche_id: int):
        for product in products:
            self.create_product(product, niche_id)

    def find_all_in_niche(self, niche_id: int) -> dict[int, Product]:
        niche_products = self.__product_card_repository.find_all_in_niche(niche_id)
        return {
            product.id: self.__table_mapper.map(product) for product in niche_products
        }

    def update(self, product_id: int, product: Product):
        product_card = self.__product_card_repository.find_by_id(product_id)
        product_card.cost = product.cost
        product_card.global_id = product.global_id
        product_card.name = product.name
        product_card.rating = int(product.rating * 100)
        product_card.brand = product.brand
        product_card.seller = product.seller
        self.__product_card_repository.update(product_card)

    def filter_existing_global_ids(self, ids: Iterable[int]) -> list[int]:
        return self.__product_card_repository.filter_existing_global_ids(list(ids))
