from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import GreenTradeZoneCalculationResult
from jorm.support.calculation import GreenTradeZoneCalculateResult

from jarvis_db.cache.green_trade_zone.green_trade_zone_service import GreenZoneSegmentData


class GreenTradeZoneTableToJormMapper(
    Mapper[GreenTradeZoneCalculationResult, GreenTradeZoneCalculateResult]
):
    def map(
        self, value: GreenTradeZoneCalculationResult
    ) -> GreenTradeZoneCalculateResult:
        segment_data = GreenZoneSegmentData.model_validate(value.segment_data)
        return GreenTradeZoneCalculateResult(
            segments=segment_data.segments,
            segment_product_count=segment_data.segment_product_count,
            best_segment_idx=value.best_segment_index,
            segment_profits=segment_data.segment_profits,
            mean_segment_profit=segment_data.mean_segment_profit,
            mean_product_profit=segment_data.mean_product_profit,
            segment_product_with_trades_count=segment_data.segment_product_with_trades_count,
            best_mean_segment_profit_idx=value.best_mean_segment_profit_index,
            best_mean_product_profit_idx=value.best_mean_product_profit_index,
            best_segment_product_count_idx=value.best_segment_product_count_index,
            best_segment_product_with_trades_count_idx=value.best_segment_product_with_trades_count_index,
            best_segment_profit_idx=value.best_segment_profit_index,
        )
