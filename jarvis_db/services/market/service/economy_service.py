from jorm.market.service import RequestInfo
from jorm.market.service import UnitEconomyRequest as UnitEconomyRequestEntity
from jorm.market.service import UnitEconomyResult as UnitEconomyResultEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.service.economy_request_repository import (
    EconomyRequestRepository,
)
from jarvis_db.repositores.market.service.economy_result_repository import (
    EconomyResultRepository,
)
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.tables import UnitEconomyRequest, UnitEconomyResult


class EconomyService:
    def __init__(
        self,
        request_repository: EconomyRequestRepository,
        result_repository: EconomyResultRepository,
        result_table_mapper: Mapper[
            UnitEconomyResult,
            tuple[UnitEconomyRequestEntity, UnitEconomyResultEntity, RequestInfo],
        ],
        category_service: CategoryService,
        niche_service: NicheService,
        warehouse_service: WarehouseService,
    ):
        self.__request_repository = request_repository
        self.__result_repository = result_repository
        self.__result_table_mapper = result_table_mapper
        self.__category_service = category_service
        self.__niche_service = niche_service
        self.__warehouse_service = warehouse_service

    def save_request(
        self,
        request_info: RequestInfo,
        request_entity: UnitEconomyRequestEntity,
        result_entity: UnitEconomyResultEntity,
        user_id: int,
    ) -> int:
        niche_result = self.__niche_service.find_by_name(
            request_entity.niche, request_entity.category_id
        )
        if niche_result is None:
            raise Exception(f'niche with name "{request_entity.niche}" is not found')
        warehouse_result = self.__warehouse_service.find_warehouse_by_name(
            request_entity.warehouse_name, request_entity.marketplace_id
        )
        if warehouse_result is None:
            raise Exception(
                f'warehouse with name "{request_entity.warehouse_name}" is not found'
            )
        _, niche_id = niche_result
        _, warehouse_id = warehouse_result
        request = self.__request_repository.save(
            UnitEconomyRequest(
                user_id=user_id,
                name=request_info.name,
                niche_id=niche_id,
                date=request_info.date,
                buy_cost=request_entity.buy,
                transit_cost=request_entity.transit_price,
                market_place_transit_price=request_entity.market_place_transit_price,
                pack_cost=request_entity.pack,
                transit_count=request_entity.transit_count,
                warehouse_id=warehouse_id,
            )
        )
        result = UnitEconomyResult(
            request_id=request.id,
            product_cost=result_entity.product_cost,
            pack_cost=result_entity.pack_cost,
            marketplace_commission=result_entity.marketplace_commission,
            logistic_price=result_entity.logistic_price,
            margin=result_entity.margin,
            recommended_price=result_entity.recommended_price,
            transit_profit=result_entity.transit_profit,
            roi=int(result_entity.roi * 100),
            transit_margin_percent=int(result_entity.transit_margin * 100),
            storage_price=result_entity.storage_price,
        )
        self.__result_repository.add(result)
        return request.id

    def find_user_requests(
        self, user_id: int
    ) -> dict[
        int, tuple[UnitEconomyRequestEntity, UnitEconomyResultEntity, RequestInfo]
    ]:
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
