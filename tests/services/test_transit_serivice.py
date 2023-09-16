import unittest
from datetime import datetime

from jorm.market.service import (
    RequestInfo,
    TransitEconomyRequest,
    TransitEconomyResult,
    TransitEconomySaveObject,
)
from sqlalchemy import select

from jarvis_db import schemas
from jarvis_db.factories.mappers import create_transit_economy_table_mapper
from jarvis_db.factories.services import create_transit_economy_service
from jarvis_db.schemas import (
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
            warehouse_id = session.execute(select(Warehouse.id)).scalar_one()
            warehouse_name = session.execute(select(Warehouse.name)).scalar_one()
            category_id = session.execute(select(Category.id)).scalar_one()
            niche_id = session.execute(select(Niche.id)).scalar_one()
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
            self.__user_id = user_id
            self.__warehouse_id = warehouse_id
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

    def test_delete(self):
        with self.__db_context.session() as session, session.begin():
            user_request = schemas.TransitEconomyRequest(
                niche_id=self.__niche_id,
                product_exit_cost=100,
                warehouse_id=self.__warehouse_id,
                cost_price=200,
                lenght=10,
                width=20,
                height=20,
                mass=50,
                transit_cost=1000,
                transit_count=34,
            )
            recommended_request = user_request = schemas.TransitEconomyRequest(
                niche_id=self.__niche_id,
                product_exit_cost=110,
                warehouse_id=self.__warehouse_id,
                cost_price=210,
                lenght=15,
                width=20,
                height=20,
                mass=50,
                transit_cost=2000,
                transit_count=74,
            )
            user_result = schemas.TransitEconomyResult(
                result_cost=300,
                logistic_price=160,
                purchase_cost=230,
                marketplace_expanses=45,
                absolute_margin=25,
                relative_margin=90,
                roi=65,
                storage_price=85,
                purchase_investments=250,
                commercial_expanses=125,
                tax_expanses=86,
                absolute_transit_margin=890,
                relative_transit_margin=0.67,
                transit_roi=0.85,
            )
            recommended_result = schemas.TransitEconomyResult(
                result_cost=350,
                logistic_price=260,
                purchase_cost=260,
                marketplace_expanses=25,
                absolute_margin=35,
                relative_margin=70,
                roi=45,
                storage_price=55,
                purchase_investments=350,
                commercial_expanses=225,
                tax_expanses=46,
                absolute_transit_margin=990,
                relative_transit_margin=0.87,
                transit_roi=0.65,
            )
            user_to_transit = schemas.UserToTransitEconomy(
                name="test_name",
                date=datetime(2020, 5, 11),
                user_id=self.__user_id,
                transit_request=user_request,
                transit_result=user_result,
                recommended_transit_request=recommended_request,
                recommended_transit_result=recommended_result,
            )
            session.add(user_to_transit)
            session.flush()
            user_request_id = user_request.id
            user_result_id = user_result.id
            recommended_request_id = recommended_request.id
            recommended_result_id = recommended_result.id
            request_id = user_to_transit.id
        with self.__db_context.session() as session, session.begin():
            service = create_transit_economy_service(session)
            service.delete(request_id)
        with self.__db_context.session() as session:
            user_request = session.execute(
                select(schemas.TransitEconomyRequest).where(
                    schemas.TransitEconomyRequest.id == user_request_id
                )
            ).scalar_one_or_none()
            recommended_request = session.execute(
                select(schemas.TransitEconomyRequest).where(
                    schemas.TransitEconomyRequest.id == recommended_request_id
                )
            ).scalar_one_or_none()
            user_result = session.execute(
                select(schemas.TransitEconomyResult).where(
                    schemas.TransitEconomyResult.id == user_result_id
                )
            ).scalar_one_or_none()
            recommended_result = session.execute(
                select(schemas.TransitEconomyResult).where(
                    schemas.TransitEconomyResult.id == recommended_result_id
                )
            ).scalar_one_or_none()
            user_to_transit = session.execute(
                select(schemas.UserToTransitEconomy).where(
                    schemas.UserToTransitEconomy.id == request_id
                )
            ).scalar_one_or_none()
            self.assertIsNone(user_request)
            self.assertIsNone(user_result)
            self.assertIsNone(recommended_request)
            self.assertIsNone(recommended_result)
            self.assertIsNone(user_to_transit)
