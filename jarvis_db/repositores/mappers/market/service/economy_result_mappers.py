from datetime import datetime

from jorm.market.service import UnitEconomyResult

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


class EconomyResultTableToJormMapper(Mapper[tables.UnitEconomyResult, UnitEconomyResult]):
    def map(self, value: tables.UnitEconomyResult) -> UnitEconomyResult:
        return UnitEconomyResult(
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
