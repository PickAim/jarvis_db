from jorm.market.service import (
    RequestInfo,
    SimpleEconomyRequest,
    SimpleEconomyResult,
    SimpleEconomySaveObject,
)

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import EconomyRequest, EconomyResult, UserToEconomy


class EconomyTableToJormMapper(Mapper[UserToEconomy, SimpleEconomySaveObject]):
    def __init__(
        self,
        request_mapper: Mapper[EconomyRequest, SimpleEconomyRequest],
        result_mapper: Mapper[EconomyResult, SimpleEconomyResult],
    ):
        self.__request_mapper = request_mapper
        self.__result_mapper = result_mapper

    def map(self, value: UserToEconomy) -> SimpleEconomySaveObject:
        return SimpleEconomySaveObject(
            info=RequestInfo(value.id, value.date, value.name),
            user_result=(
                self.__request_mapper.map(value.economy_request),
                self.__result_mapper.map(value.economy_result),
            ),
            recommended_result=(
                self.__request_mapper.map(value.recommended_economy_request),
                self.__result_mapper.map(value.recommended_economy_result),
            ),
        )


class EconomyRequestTableMapper(Mapper[EconomyRequest, SimpleEconomyRequest]):
    def map(self, value: EconomyRequest) -> SimpleEconomyRequest:
        return SimpleEconomyRequest(
            niche_id=value.niche_id,
            category_id=value.niche.category_id,
            marketplace_id=value.niche.category.marketplace_id,
            product_exist_cost=value.product_exit_cost,
            cost_price=value.cost_price,
            length=value.lenght,
            width=value.width,
            height=value.height,
            mass=value.mass,
            target_warehouse_name=value.warehouse.name,
        )


class EcomomyResultTableMapper(Mapper[EconomyResult, SimpleEconomyResult]):
    def map(self, value: EconomyResult) -> SimpleEconomyResult:
        return SimpleEconomyResult(
            result_cost=value.result_cost,
            logistic_price=value.logistic_price,
            storage_price=value.storage_price,
            purchase_cost=value.purchase_cost,
            marketplace_expanses=value.marketplace_expanses,
            absolute_margin=value.absolute_margin,
            relative_margin=float(value.relative_margin / 100),
            roi=float(value.roi / 100),
        )
