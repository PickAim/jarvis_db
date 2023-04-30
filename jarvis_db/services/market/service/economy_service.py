from jorm.market.service import RequestInfo
from jorm.market.service import UnitEconomyRequest as UnitEconomyRequestEntity
from jorm.market.service import UnitEconomyResult as UnitEconomyResultEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.service.economy_request_repository import \
    EconomyRequestRepository
from jarvis_db.repositores.market.service.economy_result_repository import \
    EconomyResultRepository
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.tables import UnitEconomyRequest, UnitEconomyResult


class EconomyService:
    def __init__(
            self,
            request_repository: EconomyRequestRepository,
            result_repository: EconomyResultRepository,
            result_table_mapper: Mapper[UnitEconomyResult, tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]],
            niche_service: NicheService
    ):
        self.__request_repository = request_repository
        self.__result_repository = result_repository
        self.__result_table_mapper = result_table_mapper
        self.__niche_service = niche_service

    def save_request(
            self,
            request_info: RequestInfo,
            request_entity: UnitEconomyRequestEntity,
            result_entity: UnitEconomyResultEntity,
            user_id: int,
            category_id: int
    ):
        niche_result = self.__niche_service.find_by_name(
            request_entity.niche, category_id)
        if niche_result is None:
            raise Exception(
                f'niche with name "{request_entity.niche}" not found')
        _, niche_id = niche_result
        request = self.__request_repository.save(UnitEconomyRequest(
            user_id=user_id,
            niche_id=niche_id,
            date=request_info.date,
            buy_cost=request_entity.buy,
            transit_cost=request_entity.transit_price,
            pack_cost=request_entity.pack,
            transit_count=request_entity.transit_count
        ))
        result = UnitEconomyResult(
            request_id=request.id,
            product_cost=result_entity.product_cost,
            pack_cost=result_entity.pack_cost,
            marketplace_commission=result_entity.marketplace_commission,
            logistic_price=result_entity.logistic_price,
            margin=result_entity.margin,
            recommended_price=result_entity.recommended_price,
            transit_profit=result_entity.transit_profit,
            roi=result_entity.roi,
            transit_margin_percent=result_entity.transit_margin
        )
        self.__result_repository.add(result)

    def find_user_requests(self, user_id: int) -> dict[int, tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
        results = self.__result_repository.find_user_results(user_id)
        return {request.id: self.__result_table_mapper.map(request) for request in results}
