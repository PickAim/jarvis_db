from datetime import datetime
import unittest

from jorm.market.service import (
    TransitEconomyRequest,
    TransitEconomyResult,
    TransitEconomySaveObject,
    RequestInfo,
)
from sqlalchemy import select
from jarvis_db.factories.mappers import create_transit_economy_table_mapper
from jarvis_db.factories.services import create_transit_economy_service

from jarvis_db.schemas import (
    Account,
    Address,
    Category,
    Marketplace,
    Niche,
    User,
    UserToTransitEconomy,
    Warehouse,
)
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class TransitSerivceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            seeder.seed_users(1)
            seeder.seed_warehouses(1)
            seeder.seed_categories(1)
            seeder.seed_niches(1)
            user_id = session.execute(select(User.id)).scalar_one()
            warehouse_name = session.execute(select(Warehouse.name)).scalar_one()
            category_id = session.execute(select(Category.id)).scalar_one()
            niche_id = session.execute(select(Niche.id)).scalar_one()
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
            self.__user_id = user_id
            self.__warehouse_name = warehouse_name
            self.__category_id = category_id
            self.__niche_id = niche_id
            self.__marketplace_id = marketplace_id

    def test_create(self):
        self.maxDiff = None
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        user_request = TransitEconomyRequest(
            self.__niche_id,
            self.__category_id,
            self.__marketplace_id,
            100,
            150,
            10,
            12,
            15,
            20,
            self.__warehouse_name,
            432,
            11,
        )
        recommended_request = TransitEconomyRequest(
            self.__niche_id,
            self.__category_id,
            self.__marketplace_id,
            101,
            151,
            11,
            13,
            27,
            30,
            self.__warehouse_name,
            532,
            51,
        )
        user_result = TransitEconomyResult(
            111, 222, 333, 400, 50, 90, 0.2, 0.3, 235, 125, 56, 88, 0.45, 0.66
        )
        recommended_result = TransitEconomyResult(
            211, 322, 433, 500, 56, 96, 0.25, 0.35, 335, 225, 76, 98, 0.75, 0.76
        )
        save_object = TransitEconomySaveObject(
            request_info,
            (user_request, user_result),
            (recommended_request, recommended_result),
        )
        with self.__db_context.session() as session, session.begin():
            service = create_transit_economy_service(session)
            transit_id = service.create(save_object, self.__user_id)
            save_object.info.id = transit_id
        with self.__db_context.session() as session:
            actual_transit = session.execute(
                select(UserToTransitEconomy).where(
                    UserToTransitEconomy.id == transit_id
                )
            ).scalar_one()
            mapper = create_transit_economy_table_mapper()
            actual_save_object = mapper.map(actual_transit)
            self.assertEqual(save_object.info, actual_save_object.info)
            self.assertTupleEqual(
                save_object.user_result, actual_save_object.user_result
            )
            self.assertTupleEqual(
                save_object.recommended_result, actual_save_object.recommended_result
            )
            self.assertEqual(save_object, actual_save_object)
