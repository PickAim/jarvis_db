from jorm.market.service import (RequestInfo, UnitEconomyRequest,
                                 UnitEconomyResult)

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class EconomyResultJormToTableMapper(Mapper[UnitEconomyResult, tables.UnitEconomyResult]):
    def map(self, value: UnitEconomyResult) -> tables.UnitEconomyResult:
        return tables.UnitEconomyResult(
            product_cost=value.product_cost,
            pack_cost=value.pack_cost,
            marketplace_commission=value.marketplace_commission,
            logistic_price=value.logistic_price,
            margin=value.margin,
            recommended_price=value.recommended_price,
            transit_profit=value.transit_profit,
            roi=value.roi,
            transit_margin_percent=int(value.transit_margin * 100)
        )


class EconomyResultTableToJormMapper(Mapper[tables.UnitEconomyResult, tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]):
    def __init__(self, request_mapper: Mapper[tables.UnitEconomyRequest, tuple[RequestInfo, UnitEconomyRequest]]):
        self.__request_mapper = request_mapper

    def map(self, value: tables.UnitEconomyResult) -> tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]:
        result = UnitEconomyResult(
            product_cost=value.product_cost,
            pack_cost=value.pack_cost,
            marketplace_commission=value.marketplace_commission,
            logistic_price=value.logistic_price,
            storage_price=value.storage_price,
            margin=value.margin,
            recommended_price=value.recommended_price,
            transit_profit=value.transit_profit,
            roi=float(value.roi / 100),
            transit_margin=float(value.transit_margin_percent / 100)
        )
        info, request = self.__request_mapper.map(value.request)
        return request, result, info
