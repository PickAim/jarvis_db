from typing import Iterable

from jorm.market.infrastructure import Marketplace
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core import Mapper


class MarketplaceRepository:
    def __init__(
            self, session: Session,
            to_jorm_mapper: Mapper[tables.Marketplace, Marketplace],
            to_table_mapper: Mapper[Marketplace, tables.Marketplace]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, marketplace: Marketplace):
        self.__session.add(self.__to_table_mapper.map(marketplace))

    def add_all(self, marketplaces: Iterable[Marketplace]):
        self.__session.add_all((self.__to_table_mapper.map(
            marketplace) for marketplace in marketplaces))

    def fetch_all(self) -> dict[int, Marketplace]:
        db_marketplaces = self.__session.execute(
            select(tables.Marketplace)
        ).scalars().all()
        return {marketplace.id: self.__to_jorm_mapper.map(marketplace) for marketplace in db_marketplaces}
