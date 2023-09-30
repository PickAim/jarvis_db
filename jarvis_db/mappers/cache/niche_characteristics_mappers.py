from jarvis_db.core.mapper import Mapper
from jorm.support.calculation import NicheCharacteristicsCalculateResult

from jarvis_db.schemas import NicheCharacteristicsCalculationResult


class NicheCharacteristicsTableToJormMapper(
    Mapper[NicheCharacteristicsCalculationResult, NicheCharacteristicsCalculateResult]
):
    def map(
        self, value: NicheCharacteristicsCalculationResult
    ) -> NicheCharacteristicsCalculateResult:
        return NicheCharacteristicsCalculateResult(
            card_count=value.card_count,
            niche_profit=value.niche_profit,
            card_trade_count=value.card_trade_count,
            mean_card_rating=float(value.mean_card_rating / 100),
            card_with_trades_count=value.card_with_trades_count,
            daily_mean_niche_profit=value.daily_mean_niche_profit,
            daily_mean_trade_count=value.daily_mean_trade_count,
            mean_traded_card_cost=value.mean_traded_card_cost,
            month_mean_niche_profit_per_card=value.month_mean_niche_profit_per_card,
            monopoly_percent=float(value.monopoly_percent / 100),
            maximum_profit_idx=value.maximum_profit_idx,
        )
