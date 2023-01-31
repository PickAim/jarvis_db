from jorm.market.infrastructure import Niche
from sqlalchemy import func
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core import Mapper


class NicheRepository:
    def __init__(self, session: Session,
                 to_jorm_mapper: Mapper[tables.Niche, Niche],
                 to_table_mapper: Mapper[Niche, tables.Niche]):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add_by_category_name(self, niche: Niche, category_name: str):
        category = self.__session.query(tables.Category) \
            .outerjoin(tables.Category.niches) \
            .filter(func.lower(tables.Category.name) == func.lower(category_name)) \
            .one()
        category.niches.append(self.__to_table_mapper.map(niche))

    def add_all_by_category_name(self, niches: list[Niche], category_name: str):
        category = self.__session.query(tables.Category) \
            .outerjoin(tables.Category.niches) \
            .filter(func.lower(tables.Category.name) == func.lower(category_name)) \
            .one()
        category.niches.extend(
            [self.__to_table_mapper.map(niche) for niche in niches])

    def fetch_niches_by_category(self, category: str) -> list[Niche]:
        db_niches = self.__session.query(tables.Niche) \
            .join(tables.Niche.category) \
            .filter(func.lower(tables.Category.name) == func.lower(category)) \
            .all()
        return [self.__to_jorm_mapper.map(niche) for niche in db_niches]
