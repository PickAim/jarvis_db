from sqlalchemy.orm import Session
from sqlalchemy import func
from jarvis_db.core import Mapper
from jorm.market.infrastructure import Niche
from jarvis_db import tables


class NicheRepository:
    def __init__(self, session: Session, to_table_mapper: Mapper[Niche, tables.Niche]):
        self.__session = session
        self.__to_table_mapper = to_table_mapper

    def add_by_category_name(self, niche: Niche, category_name: str):
        category: tables.Category = self.__session.query(tables.Category)\
            .outerjoin(tables.Category.niches)\
            .filter(func.lower(tables.Category.name) == func.lower(category_name))\
            .one()
        category.niches.append(self.__to_table_mapper.map(niche))
