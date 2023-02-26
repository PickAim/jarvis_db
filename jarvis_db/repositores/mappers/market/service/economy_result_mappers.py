from datetime import datetime
from jarvis_db.core.mapper import Mapper
from jorm.market.service import EconomyResult, Request
from jarvis_db import tables


class EconomyResultJormToTableMapper(Mapper[EconomyResult, tables.EconomyResult]):
    def map(self, value: EconomyResult) -> tables.EconomyResult:
        return tables.EconomyResult(
            buy_cost=value.buy_cost,
            pack_cost=value.pack_cost,
            marketplace_commission=value.marketplace_commission,
            logistic_price=value.logistic_price,
            margin=value.margin,
            recommended_price=value.recommended_price,
            transit_profit=value.transit_profit,
            roi=value.roi,
            transit_margin_percent=value.transit_margin_percent
        )


class EconomyResultTableToJormMapper(Mapper[tables.EconomyResult, EconomyResult]):
    def map(self, value: tables.EconomyResult) -> EconomyResult:
        return EconomyResult(
            buy_cost=value.buy_cost,
            logistic_price=value.logistic_price,
            margin=value.margin,
            marketplace_commission=value.marketplace_commission,
            pack_cost=value.pack_cost,
            recommended_price=value.recommended_price,
            roi=value.roi,
            transit_margin_percent=value.transit_margin_percent,
            transit_profit=value.transit_profit,
            storage_price=value.storage_price,
            request=Request(datetime.utcnow())
        )
