from jorm.market.service import FrequencyRequest as FrequencyRequestEntity
from jorm.market.service import FrequencyResult as FrequencyResultEntity
from jorm.market.service import RequestInfo

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.service.frequency_request_repository import (
    FrequencyRequestRepository,
)
from jarvis_db.repositores.market.service.frequency_result_repository import (
    FrequencyResultRepository,
)
from jarvis_db.tables import FrequencyRequest, FrequencyResult


class FrequencyService:
    def __init__(
        self,
        request_repository: FrequencyRequestRepository,
        result_repository: FrequencyResultRepository,
        result_table_mapper: Mapper[
            FrequencyResult,
            tuple[FrequencyRequestEntity, FrequencyResultEntity, RequestInfo],
        ],
    ):
        self.__request_repository = request_repository
        self.__result_repository = result_repository
        self.__result_table_mapper = result_table_mapper

    def save(
        self,
        request_info: RequestInfo,
        request_entity: FrequencyRequestEntity,
        result_entity: FrequencyResultEntity,
        user_id: int,
    ) -> int:
        request = self.__request_repository.save(
            FrequencyRequest(
                name=request_info.name,
                user_id=user_id,
                search_str=request_entity.search_str,
                date=request_info.date,
            )
        )
        results = (
            FrequencyResult(request_id=request.id, cost=cost, frequency=frequency)
            for cost, frequency in result_entity.frequencies.items()
        )
        self.__result_repository.add_all(results)
        return request.id

    def find_user_requests(
        self, user_id: int
    ) -> dict[int, tuple[FrequencyRequestEntity, FrequencyResultEntity, RequestInfo]]:
        results = self.__result_repository.find_user_results(user_id)
        return {
            request.id: self.__result_table_mapper.map(request) for request in results
        }

    def remove(self, request_id: int) -> bool:
        request = self.__request_repository.find_by_id(request_id)
        if request is not None:
            self.__request_repository.delete(request)
            return True
        else:
            return False
