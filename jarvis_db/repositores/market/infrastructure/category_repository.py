from sqlalchemy import select
from sqlalchemy.orm import Session
from jorm.market.infrastructure import Category
from jarvis_db import tables
from jarvis_db.core import Mapper


class CategoryRepository:
    def __init__(
        self, session: Session,
        to_jorm_mapper: Mapper[tables.Category, Category],
        to_table_mapper: Mapper[Category, tables.Category]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add_category_to_marketplace(self, category: Category, marketplace_name: str):
        marketplace = self.__session.execute(
            select(tables.Marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
        ).scalar_one()
        marketplace.categories.append(self.__to_table_mapper.map(category))

    def add_all_categories_to_marketplace(self, categories: list[Category], marketplace_name: str):
        marketplace = self.__session.query(tables.Marketplace).filter(
            tables.Marketplace.name.ilike(marketplace_name)).one()
        marketplace.categories.extend((self.__to_table_mapper.map(
            category) for category in categories))

    def fetch_marketplace_categories(self, marketplace_name: str) -> list[Category]:
        marketplace = self.__session.execute(
            select(tables.Marketplace)
            .join(tables.Marketplace.categories)
            .where(tables.Marketplace.name.ilike(marketplace_name))
        ).scalar_one()
        return [self.__to_jorm_mapper.map(category) for category in marketplace.categories]
