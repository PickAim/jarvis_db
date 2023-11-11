import unittest

from jorm.support.calculation import GreenTradeZoneCalculateResult
from sqlalchemy import select

from jarvis_db.factories.services import create_green_trade_zone_service
from jarvis_db.cache.green_trade_zone.green_trade_zone_mappers import (
    GreenTradeZoneTableToJormMapper,
)
from jarvis_db.schemas import GreenTradeZoneCalculationResult, Niche
from jarvis_db.cache.green_trade_zone.green_trade_zone_service import GreenZoneSegmentData
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class GreenTradeZoneServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_niches(1)
            self.__niche_id = session.execute(select(Niche.id)).scalar_one()

    def test_upsert_creates_if_do_not_exists(self):
        expected = GreenTradeZoneCalculateResult(
            segments=[(1, 2), (3, 4), (5, 6)],
            mean_segment_profit=[4, 5, 6],
            mean_product_profit=[1, 2, 3],
            segment_product_count=[7, 8, 9],
            segment_profits=[13, 14, 15],
            segment_product_with_trades_count=[10, 11, 12],
            best_mean_product_profit_idx=1,
            best_mean_segment_profit_idx=2,
            best_segment_idx=3,
            best_segment_product_count_idx=4,
            best_segment_product_with_trades_count_idx=5,
            best_segment_profit_idx=6,
        )
        with self.__db_context.session() as session, session.begin():
            service = create_green_trade_zone_service(session)
            service.upsert(self.__niche_id, expected)
        with self.__db_context.session() as session:
            db_result = session.execute(
                select(GreenTradeZoneCalculationResult).where(
                    Niche.id == self.__niche_id
                )
            ).scalar_one()
            mapper = GreenTradeZoneTableToJormMapper()
            actual = mapper.map(db_result)
            self.assertEqual(expected, actual)

    def test_upsert_updates_if_exists(self):
        mapper = GreenTradeZoneTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            db_result = GreenTradeZoneCalculationResult(
                niche_id=self.__niche_id,
                best_mean_product_profit_index=1,
                best_mean_segment_profit_index=2,
                best_segment_index=3,
                best_segment_product_count_index=4,
                best_segment_product_with_trades_count_index=5,
                best_segment_profit_index=6,
                segment_data=GreenZoneSegmentData(
                    segments=[(1, 2), (3, 4), (5, 6)],
                    mean_segment_profit=[4, 5, 6],
                    mean_product_profit=[1, 2, 3],
                    segment_product_count=[7, 8, 9],
                    segment_profits=[13, 14, 15],
                    segment_product_with_trades_count=[10, 11, 12],
                ).model_dump(),
            )
            session.flush()
        with self.__db_context.session() as session, session.begin():
            expected = GreenTradeZoneCalculateResult(
                segments=[(10, 20), (30, 40), (50, 60)],
                mean_segment_profit=[40, 50, 60],
                mean_product_profit=[10, 20, 30],
                segment_product_count=[70, 80, 90],
                segment_profits=[130, 140, 150],
                segment_product_with_trades_count=[100, 110, 120],
                best_mean_product_profit_idx=10,
                best_mean_segment_profit_idx=20,
                best_segment_idx=30,
                best_segment_product_count_idx=40,
                best_segment_product_with_trades_count_idx=50,
                best_segment_profit_idx=60,
            )
            service = create_green_trade_zone_service(session)
            service.upsert(self.__niche_id, expected)
        with self.__db_context.session() as session:
            db_result = session.execute(
                select(GreenTradeZoneCalculationResult).where(
                    GreenTradeZoneCalculationResult.niche_id == self.__niche_id
                )
            ).scalar_one()
            mapper = GreenTradeZoneTableToJormMapper()
            actual = mapper.map(db_result)
            self.assertEqual(expected, actual)

    def test_find_by_id(self):
        mapper = GreenTradeZoneTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            db_result = GreenTradeZoneCalculationResult(
                niche_id=self.__niche_id,
                best_mean_product_profit_index=1,
                best_mean_segment_profit_index=2,
                best_segment_index=3,
                best_segment_product_count_index=4,
                best_segment_product_with_trades_count_index=5,
                best_segment_profit_index=6,
                segment_data=GreenZoneSegmentData(
                    segments=[(1, 2), (3, 4), (5, 6)],
                    mean_segment_profit=[4, 5, 6],
                    mean_product_profit=[1, 2, 3],
                    segment_product_count=[7, 8, 9],
                    segment_profits=[13, 14, 15],
                    segment_product_with_trades_count=[10, 11, 12],
                ).model_dump(),
            )
            session.add(db_result)
            session.flush()
            expected = mapper.map(db_result)
        with self.__db_context.session() as session:
            service = create_green_trade_zone_service(session)
            actual = service.find_by_niche_id(self.__niche_id)
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
