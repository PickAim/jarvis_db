from jorm.market.infrastructure import Category
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core import Mapper


class CategoryRepository:
    def __init__(self, session: Session,
                 to_jorm_mapper: Mapper[tables.Category, Category],
                 to_table_mapper: Mapper[Category, tables.Category]):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, category: Category):
        self.__session.add(self.__to_table_mapper.map(category))

    def add_all(self, categories: list[Category]):
        self.__session.add_all(
            (self.__to_table_mapper.map(category) for category in categories))

    def fetch_all(self) -> list[Category]:
        db_categories: list[tables.Category] = self.__session.query(tables.Category). \
            join(tables.Category.niches).all()
        return [self.__to_jorm_mapper.map(category) for category in db_categories]
