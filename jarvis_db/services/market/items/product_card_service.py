from typing import Iterable

from jorm.market.items import Product
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.services.market.items.product_history_service import (
    ProductHistoryService,
)
from jarvis_db.schemas import ProductCard


class ProductCardService:
    def __init__(
        self,
        session: Session,
        history_service: ProductHistoryService,
        table_mapper: Mapper[ProductCard, Product],
    ):
        self.__session = session
        self.__table_mapper = table_mapper
        self.__history_service = history_service

    def create_product(self, product: Product, niche_id: int):
        db_product = ProductCardService.__create_product_record(product, niche_id)
        self.__session.add(db_product)
        self.__session.flush()
        self.__history_service.create(product.history, db_product.id)
        self.__session.flush()

    def create_products(self, products: Iterable[Product], niche_id: int):
        self.__session.add_all(
            (
                ProductCardService.__create_product_record(product, niche_id)
                for product in products
            )
        )
        self.__session.flush()

    def find_all_in_niche(self, niche_id: int) -> dict[int, Product]:
        niche_products = (
            self.__session.execute(
                select(ProductCard).where(ProductCard.niche_id == niche_id)
            )
            .scalars()
            .all()
        )
        return {
            product.id: self.__table_mapper.map(product) for product in niche_products
        }

    def filter_existing_global_ids(
        self, niche_id: int, ids: Iterable[int]
    ) -> list[int]:
        ids = list(ids)
        existing_ids = (
            self.__session.execute(
                select(ProductCard.global_id)
                .where(ProductCard.niche_id == niche_id)
                .where(ProductCard.global_id.in_(ids))
            )
            .scalars()
            .all()
        )
        return list(set(ids) - set(existing_ids))

    def update(self, product_id: int, product: Product):
        self.__session.execute(
            update(ProductCard)
            .where(ProductCard.id == product_id)
            .values(
                cost=product.cost,
                global_id=product.global_id,
                name=product.name,
                rating=int(product.rating * 100),
                brand=product.brand,
                seller=product.seller,
            )
        )
        self.__session.flush()

    @staticmethod
    def __create_product_record(product: Product, niche_id: int) -> ProductCard:
        return ProductCard(
            name=product.name,
            global_id=product.global_id,
            cost=product.cost,
            rating=int(product.rating * 100),
            niche_id=niche_id,
            brand=product.brand,
            seller=product.seller,
        )
