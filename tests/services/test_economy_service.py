import unittest
from datetime import datetime

from jorm.market.person import UserPrivilege
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
    Account,
    Address,
    Category,
    Marketplace,
    Niche,
    User,
    Warehouse,
)
from tests.db_context import DbContext


class EconomyServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name="qwerty")
            self.__category_name = "qwerty"
            category = Category(name=self.__category_name, marketplace=marketplace)
            self.__niche_name = "niche#1"
            niche = Niche(
                name=self.__niche_name,
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category,
            )
            account = Account(phone="", email="", password="")
            user = User(
                name="", profit_tax=1, account=account, status=UserPrivilege.BASIC
            )
            address = Address(
                country="AS", region="QS", street="DD", number="HH", corpus="YU"
            )
            warehouse = Warehouse(
                marketplace=marketplace,
                global_id=200,
                type=0,
                name="qwerty",
                address=address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0,
            )
            session.add(user)
            session.add(niche)
            session.add(warehouse)
            session.flush()
            self.__category_id = category.id
            self.__niche_id = niche.id
            self.__user_id = user.id
            self.__marketplace_id = marketplace.id
            self.__warehouse_id = warehouse.id
            self.__warehouse_name = warehouse.name

    def test_save(self):
        self.maxDiff = None
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        user_request = SimpleEconomyRequest(
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
        )
        recommended_request = SimpleEconomyRequest(
            self.__niche_id,
            self.__category_id,
            self.__marketplace_id,
            70,
            90,
            11,
            22,
            25,
            30,
            self.__warehouse_name,
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
        # TODO
        pass

    def test_find_user_results(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
