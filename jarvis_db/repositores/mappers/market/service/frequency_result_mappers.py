from datetime import datetime

from jorm.market.service import FrequencyResult, Request

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class FrequencyResultJormToTableMapper(Mapper[FrequencyResult, tables.FrequencyResult]):
    def map(self, value: FrequencyResult) -> tables.FrequencyResult:
        return tables.FrequencyResult(
            cost=0,
            frequency=0
        )


class FrequencyResultTableToJormMapper(Mapper[tables.FrequencyResult, FrequencyResult]):
    def map(self, value: tables.FrequencyResult) -> FrequencyResult:
        return FrequencyResult(
            request=Request(datetime.utcnow()),
            frequencies={}
        )
