from jorm.market.infrastructure import Category
from sqlalchemy import select
from sqlalchemy.orm import Session

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

    def add_category_to_marketplace(self, category: Category, marketplace_id: int):
        db_category = self.__to_table_mapper.map(category)
        db_category.marketplace_id = marketplace_id
        self.__session.add(db_category)

    def add_all_categories_to_marketplace(self, categories: list[Category], marketplace_id: int):
        db_marketplace = self.__session.execute(
            select(tables.Marketplace)
            .where(tables.Marketplace.id == marketplace_id)
        ).scalar_one()
        db_marketplace.categories.extend((self.__to_table_mapper.map(
            category) for category in categories))

    def fetch_marketplace_categories(self, marketplace_id: int) -> list[Category]:
        db_categories = self.__session.execute(
            select(tables.Category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.id == marketplace_id)
        ).scalars().all()
        return [self.__to_jorm_mapper.map(category) for category in db_categories]
