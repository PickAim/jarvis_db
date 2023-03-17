from jorm.market.service import FrequencyResult
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class FrequencyResultRepository:
    def __init__(
            self,
            session: Session,
            to_jorm_mapper: Mapper[tables.FrequencyResult, FrequencyResult],
            to_table_mapper: Mapper[FrequencyResult, tables.FrequencyResult]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, result: FrequencyResult):
        self.__session.add(self.__to_table_mapper.map(result))

    def fetch_all(self) -> dict[int, FrequencyResult]:
        db_results = self.__session.execute(
            select(tables.FrequencyResult)
        ).scalars().all()
        return {result.id: self.__to_jorm_mapper.map(result) for result in db_results}
