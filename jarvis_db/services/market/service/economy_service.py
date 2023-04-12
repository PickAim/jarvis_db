from jorm.market.service import EconomyRequest as EconomyRequestEntity
from jorm.market.service import EconomyResult as EconomyResultEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.service.economy_request_repository import \
    EconomyRequestRepository
from jarvis_db.repositores.market.service.economy_result_repository import \
    EconomyResultRepository
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.tables import EconomyRequest, EconomyResult


class EconomyService:
    def __init__(
            self,
            request_repository: EconomyRequestRepository,
            request_table_mapper: Mapper[EconomyRequest, EconomyRequestEntity],
            result_repository: EconomyResultRepository,
            result_table_mapper: Mapper[EconomyResult, EconomyResultEntity],
            niche_service: NicheService
    ):
        self.__request_repository = request_repository
        self.__request_table_mapper = request_table_mapper
        self.__result_repository = result_repository
        self.__result_table_mapper = result_table_mapper
        self.__niche_service = niche_service

    def save_request(
            self,
            request_entity: EconomyRequestEntity,
            result_entity: EconomyResultEntity,
            user_id: int,
            category_id: int
    ):
        _, niche_id = self.__niche_service.find_by_name(
            request_entity.niche_name, category_id)
        request = self.__request_repository.save(EconomyRequest(
            user_id=user_id,
            niche_id=niche_id,
            date=request_entity.date,
            prime_cost=request_entity.prime_cost,
            transit_cost=request_entity.transit_cost,
            pack_cost=request_entity.pack_cost,
            transit_count=request_entity.transit_count
        ))
        result = EconomyResult(
            request_id=request.id,
            buy_cost=result_entity.buy_cost,
            pack_cost=result_entity.pack_cost,
            marketplace_commission=result_entity.marketplace_commission,
            logistic_price=result_entity.logistic_price,
            margin=result_entity.margin,
            recommended_price=result_entity.recommended_price,
            transit_profit=result_entity.transit_profit,
            roi=result_entity.roi,
            transit_margin_percent=result_entity.transit_margin_percent
        )
        self.__result_repository.add(result)

    def find_user_requests(self, user_id: int) -> dict[int, EconomyRequestEntity]:
        requests = self.__request_repository.find_user_requests(user_id)
        return {request.id: self.__request_table_mapper.map(request) for request in requests}
