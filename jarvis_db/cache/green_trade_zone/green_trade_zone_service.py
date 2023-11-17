from datetime import datetime
from typing import TypedDict

from jorm.support.calculation import GreenTradeZoneCalculateResult
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from jarvis_db.core.mapper import Mapper

from jarvis_db.schemas import GreenTradeZoneCalculationResult


class GreenZoneSegmentData(BaseModel):
    segments: list[tuple[int, int]]
    segment_profits: list[int]
    mean_segment_profit: list[int]
    mean_product_profit: list[int]
    segment_product_count: list[int]
    segment_product_with_trades_count: list[int]


class _GreenTradeZoneTypedDict(TypedDict):
    best_segment_index: int
    best_segment_profit_index: int
    best_mean_segment_profit_index: int
    best_mean_product_profit_index: int
    best_segment_product_count_index: int
    best_segment_product_with_trades_count_index: int


class GreenTradeZoneService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[
            GreenTradeZoneCalculationResult, GreenTradeZoneCalculateResult
        ],
    ) -> None:
        self.__session = session
        self.__table_mapper = table_mapper

    def upsert(
        self, niche_id: int, green_zone_trade_result: GreenTradeZoneCalculateResult
    ) -> None:
        existing_result = self.__session.execute(
            select(GreenTradeZoneCalculationResult).where(
                GreenTradeZoneCalculationResult.niche_id == niche_id
            )
        ).scalar_one_or_none()
        segment_data = GreenZoneSegmentData(
            segments=green_zone_trade_result.segments,
            segment_profits=green_zone_trade_result.segment_profits,
            mean_segment_profit=green_zone_trade_result.mean_segment_profit,
            mean_product_profit=green_zone_trade_result.mean_product_profit,
            segment_product_count=green_zone_trade_result.segment_product_count,
            segment_product_with_trades_count=green_zone_trade_result.segment_product_with_trades_count,
        )
        typed_dict = GreenTradeZoneService.__map_entity_to_typed_dict(
            green_zone_trade_result
        )
        if existing_result is None:
            self.__session.add(
                GreenTradeZoneCalculationResult(
                    niche_id=niche_id,
                    segment_data=segment_data.model_dump(),
                    **typed_dict
                )
            )
        else:
            self.__session.execute(
                update(GreenTradeZoneCalculationResult)
                .where(GreenTradeZoneCalculationResult.niche_id == niche_id)
                .values(
                    segment_data=segment_data.model_dump(),
                    date=datetime.utcnow(),
                    **typed_dict
                )
            )
        self.__session.flush()

    def find_by_niche_id(self, niche_id: int) -> GreenTradeZoneCalculateResult | None:
        db_result = self.__session.execute(
            select(GreenTradeZoneCalculationResult).where(
                GreenTradeZoneCalculationResult.niche_id == niche_id
            )
        ).scalar_one_or_none()
        return self.__table_mapper.map(db_result) if db_result is not None else None

    @staticmethod
    def __map_entity_to_typed_dict(
        green_zone_trade_result: GreenTradeZoneCalculateResult,
    ) -> _GreenTradeZoneTypedDict:
        return _GreenTradeZoneTypedDict(
            best_segment_index=green_zone_trade_result.best_segment_idx,
            best_segment_profit_index=green_zone_trade_result.best_segment_profit_idx,
            best_mean_segment_profit_index=green_zone_trade_result.best_mean_segment_profit_idx,
            best_mean_product_profit_index=green_zone_trade_result.best_mean_product_profit_idx,
            best_segment_product_count_index=green_zone_trade_result.best_segment_product_count_idx,
            best_segment_product_with_trades_count_index=green_zone_trade_result.best_segment_product_with_trades_count_idx,
        )
