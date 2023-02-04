from sqlalchemy import select
from sqlalchemy.orm import Session
from jorm.market.infrastructure import Niche
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

    def add_by_category_name(self, niche: Niche, category_name: str, marketplace_name: str):
        category = self.__session.execute(
            select(tables.Category)
            .join(tables.Category.marketplace)
            .outerjoin(tables.Category.niches)
            .where(tables.Marketplace.name.ilike(marketplace_name))
            .where(tables.Category.name.ilike(category_name))
        ).scalar_one()
        category.niches.append(self.__to_table_mapper.map(niche))

    def add_all_by_category_name(self, niches: list[Niche], category_name: str, marketplace_name: str):
        category = self.__session.execute(
            select(tables.Category)
            .join(tables.Category.marketplace)
            .outerjoin(tables.Category.niches)
            .where(tables.Marketplace.name.ilike(marketplace_name))
            .where(tables.Category.name.ilike(category_name))
        ).scalar_one()
        category.niches.extend(
            [self.__to_table_mapper.map(niche) for niche in niches])

    def fetch_niches_by_category(self, category_name: str, marketplace_name: str) -> list[Niche]:
        db_niches = self.__session.execute(
            select(tables.Niche)
            .join(tables.Niche.category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
            .where(tables.Category.name.ilike(category_name))
        ).scalars().all()
        return [self.__to_jorm_mapper.map(niche) for niche in db_niches]
