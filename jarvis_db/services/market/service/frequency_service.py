from jorm.market.service import FrequencyRequest as FrequencyRequestEntity
from jorm.market.service import FrequencyResult as FrequencyResultEntity
from jorm.market.service import RequestInfo

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.infrastructure.niche_repository import NicheRepository
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
        niche_repository: NicheRepository,
        result_repository: FrequencyResultRepository,
        result_table_mapper: Mapper[
            FrequencyRequest,
            tuple[FrequencyRequestEntity, FrequencyResultEntity, RequestInfo],
        ],
    ):
        self.__request_repository = request_repository
        self.__niche_repository = niche_repository
        self.__result_repository = result_repository
        self.__result_table_mapper = result_table_mapper

    def save(
        self,
        request_info: RequestInfo,
        request_entity: FrequencyRequestEntity,
        result_entity: FrequencyResultEntity,
        user_id: int,
    ) -> int:
        db_niche = self.__niche_repository.find_by_niche_name_and_category_name(
            request_entity.niche,
            request_entity.category,
            request_entity.marketplace_id,
        )
        if db_niche is None:
            raise Exception(f"No niche matching request {request_entity}")
        request = FrequencyRequest(
            name=request_info.name,
            user_id=user_id,
            date=request_info.date,
            niche_id=db_niche.id,
        )
        results = (
            FrequencyResult(request=request, cost=cost, frequency=frequency)
            for cost, frequency in zip(result_entity.x, result_entity.y, strict=True)
        )
        self.__result_repository.add_all(results)
        return request.id

    def find_user_requests(
        self, user_id: int
    ) -> dict[int, tuple[FrequencyRequestEntity, FrequencyResultEntity, RequestInfo]]:
        results = self.__request_repository.find_user_requests(user_id)
        return {
            result_unit.id: self.__result_table_mapper.map(result_unit)
            for result_unit in results
        }

    def remove(self, request_id: int) -> bool:
        request = self.__request_repository.find_by_id(request_id)
        if request is not None:
            self.__request_repository.delete(request)
            return True
        else:
            return False
