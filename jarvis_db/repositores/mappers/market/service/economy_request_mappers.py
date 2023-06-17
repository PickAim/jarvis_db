from jorm.market.service import RequestInfo, UnitEconomyRequest

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class EconomyRequestJormToTableMapper(
    Mapper[tuple[RequestInfo, UnitEconomyRequest], tables.UnitEconomyRequest]
):
    def map(
        self, value: tuple[RequestInfo, UnitEconomyRequest]
    ) -> tables.UnitEconomyRequest:
        info, request = value
        return tables.UnitEconomyRequest(
            date=info.date,
            buy_cost=request.buy,
            transit_cost=request.transit_price,
            transit_count=request.transit_count,
            pack_cost=request.pack,
        )


class EconomyRequestTableToJormMapper(
    Mapper[tables.UnitEconomyRequest, tuple[RequestInfo, UnitEconomyRequest]]
):
    def map(
        self, value: tables.UnitEconomyRequest
    ) -> tuple[RequestInfo, UnitEconomyRequest]:
        info = RequestInfo(value.id, value.date, value.name)
        request = UnitEconomyRequest(
            buy=value.buy_cost,
            pack=value.pack_cost,
            category=value.niche.category.name,
            niche=value.niche.name,
            transit_count=value.transit_count,
            transit_price=value.transit_cost,
            market_place_transit_price=value.market_place_transit_price,
            warehouse_name=value.warehouse.name,
        )
        return info, request
