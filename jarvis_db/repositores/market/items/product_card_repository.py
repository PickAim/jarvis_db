from sqlalchemy import select
from sqlalchemy.orm import Session
from jorm.market.items import Product
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

    def add_product_to_niche(
        self,
        product: Product,
        niche_name: str,
        category_name: str,
        marketplace_name: str
    ):
        niche = self.__session.execute(
            select(tables.Niche)
            .join(tables.Niche.category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
            .where(tables.Category.name.ilike(category_name))
            .where(tables.Niche.name.ilike(niche_name))
        ).scalar_one()
        niche.products.append(self.__to_table_mapper.map(product))

    def add_products_to_niche(
        self,
        products: list[Product],
        niche_name: str,
        category_name: str,
        marketplace_name: str
    ):
        niche = self.__session.execute(
            select(tables.Niche)
            .join(tables.Niche.category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
            .where(tables.Category.name.ilike(category_name))
            .where(tables.Niche.name.ilike(niche_name))
        ).scalar_one()
        niche.products.extend((self.__to_table_mapper.map(product)
                              for product in products))

    def fetch_all_in_niche(
        self,
        niche_name: str,
        category_name: str,
        marketplace_name: str
    ) -> list[Product]:
        products = self.__session.execute(
            select(tables.ProductCard)
            .join(tables.ProductCard.niche)
            .where(tables.Niche.name.ilike(niche_name))
            .join(tables.Niche.category)
            .where(tables.Category.name.ilike(category_name))
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
        ).scalars().all()
        return [self.__to_jorm_mapper.map(product) for product in products]
