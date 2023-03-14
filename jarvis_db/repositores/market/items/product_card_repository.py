from typing import Iterable

from jorm.market.items import Product
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core import Mapper


class ProductCardRepository:
    def __init__(
            self, session: Session,
            to_jorm_mapper: Mapper[tables.ProductCard, Product],
            to_table_mapper: Mapper[Product, tables.ProductCard]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add_product_to_niche(self, product: Product, niche_id: int):
        db_product = self.__to_table_mapper.map(product)
        db_product.niche_id = niche_id
        self.__session.add(db_product)

    def add_products_to_niche(self, products: Iterable[Product], niche_id: int):
        niche = self.__session.execute(
            select(tables.Niche)
            .where(tables.Niche.id == niche_id)
        ).scalar_one()
        niche.products.extend((self.__to_table_mapper.map(product)
                              for product in products))

    def fetch_all_in_niche(self, niche_id: int) -> dict[int, Product]:
        products = self.__session.execute(
            select(tables.ProductCard)
            .where(tables.ProductCard.niche_id == niche_id)
        ).scalars().all()
        return {product.id: self.__to_jorm_mapper.map(product) for product in products}
