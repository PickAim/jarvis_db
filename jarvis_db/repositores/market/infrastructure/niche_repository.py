from jorm.market.infrastructure import Niche
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core import Mapper


class NicheRepository:
    def __init__(
        self, session: Session,
        to_jorm_mapper: Mapper[tables.Niche, Niche],
        to_table_mapper: Mapper[Niche, tables.Niche]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, niche: Niche, category_id: int):
        db_niche = self.__to_table_mapper.map(niche)
        db_niche.category_id = category_id
        self.__session.add(db_niche)

    def add_all(self, niches: list[Niche], category_id: int):
        db_category = self.__session.execute(
            select(tables.Category)
            .where(tables.Category.id == category_id)
        ).scalar_one()
        db_category.niches.extend(
            (self.__to_table_mapper.map(niche) for niche in niches))

    def find_by_name(self, niche_name: str, category_id: int) -> tuple[Niche, int]:
        db_niche = self.__session.execute(
            select(tables.Niche)
            .join(tables.Niche.category)
            .where(tables.Category.id == category_id)
            .where(tables.Niche.name.ilike(niche_name))
        ).scalar_one()
        return self.__to_jorm_mapper.map(db_niche), db_niche.id

    def fetch_niches_by_category(self, category_id: int) -> dict[int, Niche]:
        db_niches = self.__session.execute(
            select(tables.Niche)
            .join(tables.Niche.category)
            .where(tables.Category.id == category_id)
        ).scalars().all()
        return {niche.id: self.__to_jorm_mapper.map(niche) for niche in db_niches}
