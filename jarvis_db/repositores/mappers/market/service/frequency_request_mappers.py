from jorm.market.service import FrequencyRequest

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class FrequencyRequestJormToTableMapper(Mapper[FrequencyRequest, tables.FrequencyRequest]):
    def map(self, value: FrequencyRequest) -> tables.FrequencyRequest:
        return tables.FrequencyRequest(
            search_str=value.search_str,
            date=value.date
        )


class FrequencyRequestTableToJormMapper(Mapper[tables.FrequencyRequest, FrequencyRequest]):
    def map(self, value: tables.FrequencyRequest) -> FrequencyRequest:
        return FrequencyRequest(
            date=value.date,
            search_str=value.search_str
        )
