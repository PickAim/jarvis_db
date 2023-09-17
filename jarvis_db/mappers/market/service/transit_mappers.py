from jorm.market.service import (
    RequestInfo,
    TransitEconomySaveObject,
)
from jorm.market.service import (
    TransitEconomyRequest as TransitEconomyRequestEntity,
)
from jorm.market.service import (
    TransitEconomyResult as TransitEconomyResultEntity,
)

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import (
    TransitEconomyRequest,
    TransitEconomyResult,
    UserToTransitEconomy,
)


class TransitTableToJormMapper(Mapper[UserToTransitEconomy, TransitEconomySaveObject]):
    def __init__(
        self,
        requset_mapper: Mapper[TransitEconomyRequest, TransitEconomyRequestEntity],
        result_mapper: Mapper[TransitEconomyResult, TransitEconomyResultEntity],
    ):
        self.__requset_mapper = requset_mapper
        self.__result_mapper = result_mapper

    def map(self, value: UserToTransitEconomy) -> TransitEconomySaveObject:
        return TransitEconomySaveObject(
            info=RequestInfo(value.id, value.date, value.name),
            user_result=(
                self.__requset_mapper.map(value.transit_request),
                self.__result_mapper.map(value.transit_result),
            ),
            recommended_result=(
                self.__requset_mapper.map(value.recommended_transit_request),
                self.__result_mapper.map(value.recommended_transit_result),
            ),
        )


class TransitRequestMapper(Mapper[TransitEconomyRequest, TransitEconomyRequestEntity]):
    def map(self, value: TransitEconomyRequest) -> TransitEconomyRequestEntity:
        return TransitEconomyRequestEntity(
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
            transit_price=value.transit_cost,
            transit_count=value.transit_count,
        )


class TransitResultMapper(Mapper[TransitEconomyResult, TransitEconomyResultEntity]):
    def map(self, value: TransitEconomyResult) -> TransitEconomyResultEntity:
        return TransitEconomyResultEntity(
            result_cost=value.result_cost,
            logistic_price=value.logistic_price,
            storage_price=value.storage_price,
            purchase_cost=value.purchase_cost,
            marketplace_expanses=value.marketplace_expanses,
            absolute_margin=value.absolute_margin,
            relative_margin=float(value.relative_margin / 100),
            roi=float(value.roi / 100),
            purchase_investments=value.purchase_investments,
            commercial_expanses=value.commercial_expanses,
            tax_expanses=value.tax_expanses,
            absolute_transit_margin=value.absolute_transit_margin,
            relative_transit_margin=float(value.relative_transit_margin / 100),
            transit_roi=float(value.transit_roi / 100),
        )
