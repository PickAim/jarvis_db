from jorm.market.service import FrequencyRequest as FrequencyRequestEntity
from jorm.market.service import FrequencyResult as FrequencyResultEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.service.frequency_request_repository import \
    FrequencyRequestRepository
from jarvis_db.repositores.market.service.frequency_result_repository import \
    FrequencyResultRepository
from jarvis_db.tables import FrequencyRequest, FrequencyResult


class FrequencyService:
    def __init__(
            self,
            request_repository: FrequencyRequestRepository,
            request_table_mapper: Mapper[FrequencyRequest, FrequencyRequestEntity],
            result_repository: FrequencyResultRepository,
            result_table_mapper: Mapper[FrequencyResult, FrequencyResultEntity]
    ):
        self.__request_repository = request_repository
        self.__request_table_mapper = request_table_mapper
        self.__result_repository = result_repository
        self.__result_table_mapper = result_table_mapper

    def save(self, request_entity: FrequencyRequestEntity, result_entity: FrequencyResultEntity, user_id):
        request = self.__request_repository.save(FrequencyRequest(
            user_id=user_id,
            search_str=request_entity.search_str,
            date=request_entity.date
        ))
        result = FrequencyResult(
            request_id=request.id,
            cost=0,
            frequency=0
        )
        self.__result_repository.add(result)

    def find_user_requests(self, user_id: int) -> dict[int, FrequencyRequestEntity]:
        requests = self.__request_repository.fetch_user_requests(user_id)
        return {request.id: self.__request_table_mapper.map(request) for request in requests}
