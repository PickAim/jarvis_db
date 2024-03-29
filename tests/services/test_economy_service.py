import unittest
from datetime import datetime

from jorm.market.service import (
    RequestInfo,
    SimpleEconomyRequest,
    SimpleEconomyResult,
    SimpleEconomySaveObject,
)
from sqlalchemy import select

from jarvis_db import schemas
from jarvis_db.factories.mappers import create_economy_table_mapper
from jarvis_db.factories.services import create_economy_service
from jarvis_db.schemas import (
    Marketplace,
    Niche,
    User,
    UserToEconomy,
    Warehouse,
)
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class EconomyServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            seeder.seed_categories(1)
            seeder.seed_niches(1)
            seeder.seed_warehouses(1)
            seeder.seed_users(1)
            self.__niche_id = session.execute(select(Niche.id)).scalar_one()
            self.__user_id = session.execute(select(User.id)).scalar_one()
            self.__marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
            self.__warehouse_id = session.execute(select(Warehouse.id)).scalar_one()

    def test_save(self):
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        user_request = SimpleEconomyRequest(
            self.__niche_id,
            self.__marketplace_id,
            100,
            150,
            1.0,
            1.2,
            1.5,
            2.0,
            self.__warehouse_id,
        )
        recommended_request = SimpleEconomyRequest(
            self.__niche_id,
            self.__marketplace_id,
            70,
            90,
            1.1,
            2.2,
            2.5,
            3.0,
            self.__warehouse_id,
        )
        user_result = SimpleEconomyResult(111, 112, 114, 117, 23, 432, 0.3, 0.25)
        recommended_result = SimpleEconomyResult(211, 212, 214, 217, 33, 532, 0.4, 0.35)
        save_object = SimpleEconomySaveObject(
            request_info,
            (user_request, user_result),
            (recommended_request, recommended_result),
        )
        with self.__db_context.session() as session, session.begin():
            service = create_economy_service(session)
            request_id = service.save_request(save_object, self.__user_id)
        with self.__db_context.session() as session:
            db_result = session.execute(
                select(schemas.UserToEconomy).where(
                    schemas.UserToEconomy.id == request_id
                )
            ).scalar_one()
            mapper = create_economy_table_mapper()
            actual = mapper.map(db_result)
            save_object.info.id = request_id
            self.assertEqual(save_object, actual)

    def test_remove(self):
        with self.__db_context.session() as session, session.begin():
            user_request = schemas.EconomyRequest(
                niche_id=self.__niche_id,
                product_exit_cost=100,
                warehouse_id=self.__warehouse_id,
                cost_price=200,
                length=10,
                width=20,
                height=20,
                mass=50,
            )
            recommended_request = user_request = schemas.EconomyRequest(
                niche_id=self.__niche_id,
                product_exit_cost=110,
                warehouse_id=self.__warehouse_id,
                cost_price=210,
                length=15,
                width=20,
                height=20,
                mass=50,
            )
            user_result = schemas.EconomyResult(
                result_cost=300,
                logistic_price=160,
                purchase_cost=230,
                marketplace_expanses=45,
                absolute_margin=25,
                relative_margin=90,
                roi=65,
                storage_price=85,
            )
            recommended_result = schemas.EconomyResult(
                result_cost=350,
                logistic_price=260,
                purchase_cost=260,
                marketplace_expanses=25,
                absolute_margin=35,
                relative_margin=70,
                roi=45,
                storage_price=55,
            )
            user_to_economy = schemas.UserToEconomy(
                name="test_name",
                date=datetime(2020, 5, 11),
                user_id=self.__user_id,
                economy_request=user_request,
                economy_result=user_result,
                recommended_economy_request=recommended_request,
                recommended_economy_result=recommended_result,
            )
            session.add(user_to_economy)
            session.flush()
            user_request_id = user_request.id
            user_result_id = user_result.id
            recommended_request_id = recommended_request.id
            recommended_result_id = recommended_result.id
            request_id = user_to_economy.id
        with self.__db_context.session() as session, session.begin():
            service = create_economy_service(session)
            service.delete(request_id)
        with self.__db_context.session() as session:
            user_request = session.execute(
                select(schemas.EconomyRequest).where(
                    schemas.EconomyRequest.id == user_request_id
                )
            ).scalar_one_or_none()
            recommended_request = session.execute(
                select(schemas.EconomyRequest).where(
                    schemas.EconomyRequest.id == recommended_request_id
                )
            ).scalar_one_or_none()
            user_result = session.execute(
                select(schemas.EconomyResult).where(
                    schemas.EconomyResult.id == user_result_id
                )
            ).scalar_one_or_none()
            recommended_result = session.execute(
                select(schemas.EconomyResult).where(
                    schemas.EconomyResult.id == recommended_result_id
                )
            ).scalar_one_or_none()
            user_to_economy = session.execute(
                select(schemas.UserToEconomy).where(UserToEconomy.id == request_id)
            ).scalar_one_or_none()
            self.assertIsNone(user_request)
            self.assertIsNone(user_result)
            self.assertIsNone(recommended_request)
            self.assertIsNone(recommended_result)
            self.assertIsNone(user_to_economy)

    def test_find_user_results(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
