from jorm.market.service import FrequencyRequest, FrequencyResult, RequestInfo

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class FrequencyRequestJormToTableMapper(
    Mapper[tuple[RequestInfo, FrequencyRequest], tables.FrequencyRequest]
):
    def map(
        self, value: tuple[RequestInfo, FrequencyRequest]
    ) -> tables.FrequencyRequest:
        info, request = value
        return tables.FrequencyRequest(name=info.name, date=info.date)


class FrequencyRequestTableToJormMapper(
    Mapper[
        tables.FrequencyRequest,
        tuple[FrequencyRequest, FrequencyResult, RequestInfo],
    ]
):
    def map(
        self, value: tables.FrequencyRequest
    ) -> tuple[FrequencyRequest, FrequencyResult, RequestInfo]:
        info = RequestInfo(id=value.id, date=value.date, name=value.name)
        request = FrequencyRequest(
            category_name=value.niche.category.name,
            niche_name=value.niche.name,
            marketplace_id=value.niche.category.marketplace_id,
        )
        result = FrequencyResult(
            {result_unit.cost: result_unit.frequency for result_unit in value.results}
        )
        return request, result, info
