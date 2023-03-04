from sqlalchemy import select
from sqlalchemy.orm import Session
from jorm.market.service import EconomyResult
from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class EconomyResultRepository:
    def __init__(
            self,
            session: Session,
            to_jorm_mapper: Mapper[tables.EconomyResult, EconomyResult],
            to_table_mapper: Mapper[EconomyResult, tables.EconomyResult]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, result: EconomyResult):
        self.__session.add(self.__to_table_mapper.map(result))

    def fetch_add(self) -> list[EconomyResult]:
        db_results = self.__session.execute(
            select(tables.EconomyResult)
        ).scalars().all()
        return [self.__to_jorm_mapper.map(result) for result in db_results]
