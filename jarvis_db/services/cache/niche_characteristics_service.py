from typing import TypedDict

from jorm.support.calculation import NicheCharacteristicsCalculateResult
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import NicheCharacteristicsCalculationResult


class _NicheCharacteristicsTypedDict(TypedDict):
    card_count: int
    niche_profit: int
    card_trade_count: int
    mean_card_rating: int
    card_with_trades_count: int
    daily_mean_niche_profit: int
    daily_mean_trade_count: int
    mean_traded_card_cost: int
    month_mean_niche_profit_per_card: int
    monopoly_percent: int
    maximum_profit_idx: int


class NicheCharacteristicsService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[
            NicheCharacteristicsCalculationResult, NicheCharacteristicsCalculateResult
        ],
    ) -> None:
        self.__session = session
        self.__table_mapper = table_mapper

    def upsert(
        self, niche_id: int, niche_characteristics: NicheCharacteristicsCalculateResult
    ) -> None:
        existing_characteristics = self.__session.execute(
            select(NicheCharacteristicsCalculationResult).where(
                NicheCharacteristicsCalculationResult.niche_id == niche_id
            )
        ).scalar_one_or_none()
        if existing_characteristics is None:
            self.__session.add(
                NicheCharacteristicsCalculationResult(
                    niche_id=niche_id,
                    **NicheCharacteristicsService.__map_entity_to_record(
                        niche_characteristics
                    )
                )
            )
        else:
            self.__session.execute(
                update(NicheCharacteristicsCalculationResult)
                .where(NicheCharacteristicsCalculationResult.niche_id == niche_id)
                .values(
                    **NicheCharacteristicsService.__map_entity_to_record(
                        niche_characteristics
                    )
                )
            )
        self.__session.flush()

    def find_by_niche_id(
        self, niche_id: int
    ) -> NicheCharacteristicsCalculateResult | None:
        characteristics = self.__session.execute(
            select(NicheCharacteristicsCalculationResult).where(
                NicheCharacteristicsCalculationResult.niche_id == niche_id
            )
        ).scalar_one_or_none()
        return (
            self.__table_mapper.map(characteristics)
            if characteristics is not None
            else None
        )

    @staticmethod
    def __map_entity_to_record(
        characteristics: NicheCharacteristicsCalculateResult,
    ) -> _NicheCharacteristicsTypedDict:
        return _NicheCharacteristicsTypedDict(
            card_count=characteristics.card_count,
            niche_profit=characteristics.niche_profit,
            card_trade_count=characteristics.card_trade_count,
            mean_card_rating=int(characteristics.mean_card_rating * 100),
            card_with_trades_count=characteristics.card_with_trades_count,
            daily_mean_niche_profit=characteristics.daily_mean_niche_profit,
            daily_mean_trade_count=characteristics.daily_mean_trade_count,
            mean_traded_card_cost=characteristics.mean_traded_card_cost,
            month_mean_niche_profit_per_card=characteristics.month_mean_niche_profit_per_card,
            monopoly_percent=int(characteristics.monopoly_percent * 100),
            maximum_profit_idx=characteristics.maximum_profit_idx,
        )
