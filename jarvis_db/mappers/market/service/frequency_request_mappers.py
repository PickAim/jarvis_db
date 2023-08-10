from jorm.market.service import FrequencyRequest, FrequencyResult, RequestInfo

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper


class FrequencyRequestJormToTableMapper(
    Mapper[tuple[RequestInfo, FrequencyRequest], schemas.FrequencyRequest]
):
    def map(
        self, value: tuple[RequestInfo, FrequencyRequest]
    ) -> schemas.FrequencyRequest:
        info, request = value
        return schemas.FrequencyRequest(name=info.name, date=info.date)


class FrequencyRequestTableToJormMapper(
    Mapper[
        schemas.FrequencyRequest,
        tuple[FrequencyRequest, FrequencyResult, RequestInfo],
    ]
):
    def map(
        self, value: schemas.FrequencyRequest
    ) -> tuple[FrequencyRequest, FrequencyResult, RequestInfo]:
        info = RequestInfo(id=value.id, date=value.date, name=value.name)
        request = FrequencyRequest(
            category_id=value.niche.category.id,
            niche=value.niche.name,
            marketplace_id=value.niche.category.marketplace_id,
        )
        result = FrequencyResult(
            x=[result_unit.cost for result_unit in value.results],
            y=[result_unit.frequency for result_unit in value.results],
        )
        return request, result, info