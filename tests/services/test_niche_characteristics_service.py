import unittest

from sqlalchemy import select
from jarvis_db.factories.services import create_niche_characteristics_service
from jarvis_db.cache.niche_characteristics.niche_characteristics_mappers import (
    NicheCharacteristicsTableToJormMapper,
)

from jarvis_db.schemas import Niche, NicheCharacteristicsCalculationResult
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder
from jorm.support.calculation import NicheCharacteristicsCalculateResult


class NicheCharacteristicsServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            seeder.seed_categories(1)
            seeder.seed_niches(1)
            self.__niche_id = session.execute(select(Niche.id)).scalar_one()

    def test_upsert_creates_if_no_exists(self):
        expected = NicheCharacteristicsCalculateResult(
            card_count=10,
            niche_profit=20,
            card_trade_count=30,
            mean_card_rating=4.5,
            card_with_trades_count=50,
            daily_mean_niche_profit=60,
            daily_mean_trade_count=70,
            mean_traded_card_cost=80,
            month_mean_niche_profit_per_card=90,
            monopoly_percent=10.5,
            maximum_profit_idx=110,
        )
        with self.__db_context.session() as session, session.begin():
            service = create_niche_characteristics_service(session)
            service.upsert(self.__niche_id, expected)
        with self.__db_context.session() as session:
            stats = session.execute(
                select(NicheCharacteristicsCalculationResult).where(
                    NicheCharacteristicsCalculationResult.niche_id == self.__niche_id
                )
            ).scalar_one()
            mapper = NicheCharacteristicsTableToJormMapper()
            actual = mapper.map(stats)
            self.assertEqual(expected, actual)

    def test_upsert_updates_if_exists(self):
        with self.__db_context.session() as session, session.begin():
            session.add(
                NicheCharacteristicsCalculationResult(
                    niche_id=self.__niche_id,
                    card_count=10,
                    niche_profit=20,
                    card_trade_count=30,
                    mean_card_rating=45,
                    card_with_trades_count=50,
                    daily_mean_niche_profit=60,
                    daily_mean_trade_count=70,
                    mean_traded_card_cost=80,
                    month_mean_niche_profit_per_card=90,
                    monopoly_percent=105,
                    maximum_profit_idx=110,
                )
            )
        expected = NicheCharacteristicsCalculateResult(
            card_count=110,
            niche_profit=120,
            card_trade_count=130,
            mean_card_rating=14.5,
            card_with_trades_count=150,
            daily_mean_niche_profit=160,
            daily_mean_trade_count=170,
            mean_traded_card_cost=180,
            month_mean_niche_profit_per_card=190,
            monopoly_percent=110.5,
            maximum_profit_idx=1110,
        )
        with self.__db_context.session() as session, session.begin():
            service = create_niche_characteristics_service(session)
            service.upsert(self.__niche_id, expected)
        with self.__db_context.session() as session:
            stats = session.execute(
                select(NicheCharacteristicsCalculationResult).where(
                    NicheCharacteristicsCalculationResult.niche_id == self.__niche_id
                )
            ).scalar_one()
            mapper = NicheCharacteristicsTableToJormMapper()
            actual = mapper.map(stats)
            self.assertEqual(expected, actual)

    def test_find_by_niche_id(self):
        mapper = NicheCharacteristicsTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            stats = NicheCharacteristicsCalculationResult(
                niche_id=self.__niche_id,
                card_count=10,
                niche_profit=20,
                card_trade_count=30,
                mean_card_rating=45,
                card_with_trades_count=50,
                daily_mean_niche_profit=60,
                daily_mean_trade_count=70,
                mean_traded_card_cost=80,
                month_mean_niche_profit_per_card=90,
                monopoly_percent=105,
                maximum_profit_idx=110,
            )
            session.add(stats)
            session.flush()
            expected = mapper.map(stats)
        with self.__db_context.session() as session:
            service = create_niche_characteristics_service(session)
            actual = service.find_by_niche_id(self.__niche_id)
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
