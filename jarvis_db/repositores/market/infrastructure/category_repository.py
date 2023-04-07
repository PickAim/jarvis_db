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

    def add(self, category: Category, marketplace_id: int):
        db_category = self.__to_table_mapper.map(category)
        db_category.marketplace_id = marketplace_id
        self.__session.add(db_category)

    def add_all(self, categories: list[Category], marketplace_id: int):
        db_marketplace = self.__session.execute(
            select(tables.Marketplace)
            .where(tables.Marketplace.id == marketplace_id)
        ).scalar_one()
        db_marketplace.categories.extend((self.__to_table_mapper.map(
            category) for category in categories))

    def find_by_name(self, name: str, marketplace_id: int) -> tuple[Category, int]:
        db_category = self.__session.execute(
            select(tables.Category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.id == marketplace_id)
            .where(tables.Category.name.ilike(name))
        ).scalar_one()
        return self.__to_jorm_mapper.map(db_category), db_category.id

    def find_all(self, marketplace_id: int) -> dict[int, Category]:
        db_categories = self.__session.execute(
            select(tables.Category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.id == marketplace_id)
        ).scalars().all()
        return {category.id: self.__to_jorm_mapper.map(category) for category in db_categories}
