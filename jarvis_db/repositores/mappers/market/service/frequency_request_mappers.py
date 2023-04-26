from jorm.market.service import FrequencyRequest, RequestInfo

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class FrequencyRequestJormToTableMapper(Mapper[tuple[RequestInfo, FrequencyRequest], tables.FrequencyRequest]):
    def map(self, value: tuple[RequestInfo, FrequencyRequest]) -> tables.FrequencyRequest:
        info, request = value
        return tables.FrequencyRequest(
            search_str=request.search_str,
            date=info.date
        )


class FrequencyRequestTableToJormMapper(Mapper[tables.FrequencyRequest, tuple[RequestInfo, FrequencyRequest]]):
    def map(self, value: tables.FrequencyRequest) -> tuple[RequestInfo, FrequencyRequest]:
        info = RequestInfo(
            id=value.id,
            date=value.date,
            name=value.user.account.email
        )
        request = FrequencyRequest(value.search_str)
        return info, request
