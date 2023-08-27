import unittest
from datetime import datetime

from jorm.market.person import UserPrivilege
from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult
from sqlalchemy import select

from jarvis_db import schemas
from jarvis_db.factories.services import create_economy_service
from jarvis_db.mappers.market.service.economy_request_mappers import (
    EconomyRequestTableToJormMapper,
)
from jarvis_db.mappers.market.service.economy_result_mappers import (
    EconomyResultTableToJormMapper,
)
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
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        request_entity = UnitEconomyRequest(
            self.__niche_name,
            self.__category_id,
            self.__marketplace_id,
            100,
            20,
            121,
            33,
            warehouse_name="qwerty",
        )
        result = UnitEconomyResult(200, 300, 12, 25, 151, 134, 12355, 2, 1.2, 2.0)
        with self.__db_context.session() as session, session.begin():
            service = create_economy_service(session)
            request_id = service.save_request(
                request_info,
                request_entity,
                result,
                self.__user_id,
            )
        with self.__db_context.session() as session:
            db_result = session.execute(
                select(schemas.UnitEconomyResult)
                .where(schemas.UnitEconomyResult.request_id == request_id)
                .join(schemas.UnitEconomyResult.request)
                .join(schemas.UnitEconomyRequest.warehouse)
            ).scalar_one()
            request = db_result.request
            self.assertEqual(request_info.date, request.date)
            self.assertEqual(request_info.name, request.name)
            self.assertEqual(result.product_cost, db_result.product_cost)
            self.assertEqual(result.pack_cost, db_result.pack_cost)
            self.assertEqual(
                result.marketplace_commission, db_result.marketplace_commission
            )
            self.assertEqual(result.logistic_price, db_result.logistic_price)
            self.assertEqual(result.margin, db_result.margin)
            self.assertEqual(result.recommended_price, db_result.recommended_price)
            self.assertEqual(result.transit_profit, db_result.transit_profit)
            self.assertEqual(int(result.roi * 100), db_result.roi)
            self.assertEqual(
                int(result.transit_margin * 100), db_result.transit_margin_percent
            )
            self.assertEqual(result.storage_price, db_result.storage_price)
            self.assertEqual(self.__warehouse_id, request.warehouse_id)
            self.assertEqual(self.__warehouse_name, request.warehouse.name)

    def test_remove(self):
        request_id = 100
        result_id = 100
        with self.__db_context.session() as session, session.begin():
            request = schemas.UnitEconomyRequest(
                id=request_id,
                name="name",
                user_id=self.__user_id,
                niche_id=self.__niche_id,
                date=datetime(2020, 2, 2),
                buy_cost=10,
                transit_cost=120,
                market_place_transit_price=1230,
                pack_cost=12340,
                transit_count=123450,
                warehouse_id=self.__warehouse_id,
            )
            result = schemas.UnitEconomyResult(
                id=result_id,
                request=request,
                product_cost=10,
                pack_cost=120,
                marketplace_commission=1230,
                logistic_price=12340,
                margin=123450,
                recommended_price=1234560,
                transit_profit=12345670,
                roi=230,
                transit_margin_percent=2340,
                storage_price=23450,
            )
            session.add(result)
        with self.__db_context.session() as session, session.begin():
            service = create_economy_service(session)
            is_removed = service.delete(request_id)
            self.assertTrue(is_removed)
        with self.__db_context.session() as session:
            request = session.execute(
                select(schemas.UnitEconomyRequest).where(
                    schemas.UnitEconomyRequest.id == request_id
                )
            ).scalar_one_or_none()
            result = session.execute(
                select(schemas.UnitEconomyResult).where(
                    schemas.UnitEconomyResult.id == result_id
                )
            ).scalar_one_or_none()
            self.assertIsNone(request)
            self.assertIsNone(result)

    def test_find_user_results(self):
        mapper = EconomyResultTableToJormMapper(EconomyRequestTableToJormMapper())
        with self.__db_context.session() as session, session.begin():
            db_results = [
                schemas.UnitEconomyResult(
                    product_cost=10 * i,
                    pack_cost=120 + i * 20,
                    marketplace_commission=1230 + i * 30,
                    logistic_price=12340 + i * 40,
                    margin=123450 + i * 50,
                    recommended_price=1234560 + i * 100,
                    transit_profit=12345670 + i * 200,
                    roi=230 + i * 25,
                    transit_margin_percent=2340 + i * 300,
                    storage_price=23450 + i * 1000,
                    request=schemas.UnitEconomyRequest(
                        name=f"request_{i}",
                        user_id=self.__user_id,
                        niche_id=self.__niche_id,
                        date=datetime(2020, 2, 2),
                        buy_cost=10 * i,
                        transit_cost=120 * i,
                        market_place_transit_price=1230 + i * 10,
                        pack_cost=12340 + i * 20,
                        transit_count=123450 + 100 * i,
                        warehouse_id=self.__warehouse_id,
                    ),
                )
                for i in range(1, 11)
            ]
            session.add_all(db_results)
            session.flush()
            expected_requests = [mapper.map(request) for request in db_results]
        with self.__db_context.session() as session:
            service = create_economy_service(session)
            actual_response = service.find_user_requests(self.__user_id)
            for expected_tuple, (requests_id, actual_tuple) in zip(
                expected_requests, actual_response.items(), strict=True
            ):
                expected_request, expected_result, expected_info = expected_tuple
                actual_request, actual_result, actual_info = actual_tuple
                self.assertEqual(expected_info.id, requests_id)
                self.assertEqual(expected_request, actual_request)
                self.assertEqual(expected_result, actual_result)
                self.assertEqual(expected_info, actual_info)


if __name__ == "__main__":
    unittest.main()
