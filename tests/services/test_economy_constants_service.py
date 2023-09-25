import unittest

from sqlalchemy import select
from jarvis_db.factories.services import create_economy_constants_service
from jarvis_db.mappers.market.service.economy_constants_mappers import (
    EconomyConstantsTableToJormMapper,
)
from jarvis_db.schemas import EconomyConstants, Marketplace

from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder
from sqlalchemy.exc import IntegrityError
from jorm.support.types import EconomyConstants as EconomyConstantsEntity


class EconomyConstantsServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            self.__marketplace_id = session.execute(select(Marketplace.id)).scalar_one()

    def test_one_to_one(self):
        with self.assertRaises(IntegrityError):
            with self.__db_context.session() as session, session.begin():
                session.add(
                    EconomyConstants(
                        marketplace_id=self.__marketplace_id,
                        max_mass=1,
                        max_side_sum=2,
                        max_side_length=3,
                        max_standard_volume_in_liters=4,
                        return_price=5,
                        oversize_logistic_price=6,
                        oversize_storage_price=7,
                        standard_warehouse_logistic_price=8,
                        standard_warehouse_storage_price=9,
                        nds_tax=10,
                        commercial_tax=11,
                        self_employed_tax=12,
                    )
                )
                session.add(
                    EconomyConstants(
                        marketplace_id=self.__marketplace_id,
                        max_mass=11,
                        max_side_sum=12,
                        max_side_length=13,
                        max_standard_volume_in_liters=14,
                        return_price=15,
                        oversize_logistic_price=16,
                        oversize_storage_price=17,
                        standard_warehouse_logistic_price=18,
                        standard_warehouse_storage_price=19,
                        nds_tax=20,
                        commercial_tax=21,
                        self_employed_tax=22,
                    )
                )

    def test_upsert_creates_constants(self):
        with self.__db_context.session() as session, session.begin():
            service = create_economy_constants_service(session)
            expected = EconomyConstantsEntity(
                max_mass=1.1,
                max_side_sum=2.2,
                max_side_length=3.3,
                max_standard_volume_in_liters=4.4,
                return_price=10,
                oversize_logistic_price=20,
                oversize_storage_price=30,
                standard_warehouse_logistic_price=50,
                standard_warehouse_storage_price=60,
                nds_tax=5.5,
                commercial_tax=6.6,
                self_employed_tax=7.7,
            )
            service.upsert_constants(self.__marketplace_id, expected)
        with self.__db_context.session() as session:
            mapper = EconomyConstantsTableToJormMapper()
            db_const = session.execute(
                select(EconomyConstants).where(
                    EconomyConstants.marketplace_id == self.__marketplace_id
                )
            ).scalar_one()
            actual = mapper.map(db_const)
            self.assertEqual(expected, actual)

    def test_upsert_updates_existing(self):
        with self.__db_context.session() as session, session.begin():
            session.add(
                EconomyConstants(
                    marketplace_id=self.__marketplace_id,
                    max_mass=100,
                    max_side_sum=200,
                    max_side_length=300,
                    max_standard_volume_in_liters=400,
                    return_price=500,
                    oversize_logistic_price=600,
                    oversize_storage_price=700,
                    standard_warehouse_logistic_price=800,
                    standard_warehouse_storage_price=900,
                    nds_tax=1000,
                    commercial_tax=1100,
                    self_employed_tax=1200,
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_economy_constants_service(session)
            expected = EconomyConstantsEntity(
                max_mass=21.0,
                max_side_sum=22.2,
                max_side_length=23.3,
                max_standard_volume_in_liters=24.4,
                return_price=210,
                oversize_logistic_price=220,
                oversize_storage_price=230,
                standard_warehouse_logistic_price=250,
                standard_warehouse_storage_price=260,
                nds_tax=25.5,
                commercial_tax=26.6,
                self_employed_tax=27.7,
            )
            service.upsert_constants(self.__marketplace_id, expected)
        with self.__db_context.session() as session, session:
            mapper = EconomyConstantsTableToJormMapper()
            actual = mapper.map(
                session.execute(
                    select(EconomyConstants).where(
                        EconomyConstants.marketplace_id == self.__marketplace_id
                    )
                ).scalar_one()
            )
            self.assertEqual(expected, actual)

    def test_find_by_marketplace_id(self):
        with self.__db_context.session() as session, session.begin():
            constants = EconomyConstants(
                marketplace_id=self.__marketplace_id,
                max_mass=100,
                max_side_sum=200,
                max_side_length=300,
                max_standard_volume_in_liters=400,
                return_price=500,
                oversize_logistic_price=600,
                oversize_storage_price=700,
                standard_warehouse_logistic_price=800,
                standard_warehouse_storage_price=900,
                nds_tax=1000,
                commercial_tax=1100,
                self_employed_tax=1200,
            )
            session.add(constants)
            session.flush()
            mapper = EconomyConstantsTableToJormMapper()
            expected = mapper.map(constants)
        with self.__db_context.session() as session:
            service = create_economy_constants_service(session)
            actual = service.find_by_marketplace_id(self.__marketplace_id)
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
