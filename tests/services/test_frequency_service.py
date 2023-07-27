import unittest
from datetime import datetime

from jorm.market.service import FrequencyRequest, FrequencyResult, RequestInfo
from sqlalchemy import select

from jarvis_db import tables
from jarvis_db.factories.services import create_frequency_service
from jarvis_db.repositores.mappers.market.service.frequency_request_mappers import (
    FrequencyRequestTableToJormMapper,
)
from jarvis_db.tables import Account, Category, Marketplace, Niche, User
from tests.db_context import DbContext


class FrequencyServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            account = Account(phone="", email="", password="")
            user = User(name="", profit_tax=1, account=account)
            self.__category_name = "category#1"
            self.__niche_name = "niche#1"
            self.__marketplace_name = "marketplace_1"
            marketplace = Marketplace(name=self.__marketplace_name)
            category = Category(name=self.__category_name, marketplace=marketplace)
            niche = Niche(
                name=self.__niche_name,
                marketplace_commission=1,
                partial_client_commission=1,
                client_commission=1,
                return_percent=1,
                category=category,
            )
            session.add(user)
            session.add(niche)
            session.flush()
            self.__user_id = user.id
            self.__category_id = category.id
            self.__niche_id = niche.id
            self.__marketplace_id = marketplace.id

    def test_save(self):
        request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
        request = FrequencyRequest(
            niche=self.__niche_name,
            category_id=self.__category_id,
            marketplace_id=self.__marketplace_id,
        )
        result = FrequencyResult(x=[i for i in range(10)], y=[i * 2 for i in range(10)])
        with self.__db_context.session() as session, session.begin():
            service = create_frequency_service(session)
            request_id = service.save(
                request_info,
                request,
                result,
                self.__user_id,
            )
        with self.__db_context.session() as session:
            db_request = session.execute(
                select(tables.FrequencyRequest)
                .where(tables.FrequencyRequest.id == request_id)
                .join(tables.FrequencyRequest.results)
                .join(tables.FrequencyRequest.niche)
                .join(tables.Niche.category)
                .distinct()
            ).scalar_one()
            self.assertEqual(request_info.name, db_request.name)
            self.assertEqual(request_info.date, db_request.date)
            self.assertEqual(request.niche, db_request.niche.name)
            self.assertEqual(request.category_id, db_request.niche.category.id)
            self.assertEqual(
                request.marketplace_id, db_request.niche.category.marketplace_id
            )
            for cost, frequency, result_unit in zip(
                result.x, result.y, db_request.results, strict=True
            ):
                self.assertEqual(cost, result_unit.cost)
                self.assertEqual(frequency, result_unit.frequency)

    def test_remove(self):
        with self.__db_context.session() as session, session.begin():
            request_id = 100
            request = tables.FrequencyRequest(
                id=request_id,
                name="name",
                user_id=self.__user_id,
                date=datetime(2020, 2, 2),
                niche_id=self.__niche_id,
            )
            results = [
                tables.FrequencyResult(cost=i * 10, frequency=i * 20, request=request)
                for i in range(10)
            ]
            session.add_all(results)
        with self.__db_context.session() as session, session.begin():
            service = create_frequency_service(session)
            is_removed = service.remove(request_id)
            self.assertTrue(is_removed)
        with self.__db_context.session() as session:
            db_request = session.execute(
                select(tables.FrequencyRequest).where(
                    tables.FrequencyRequest.id == request_id
                )
            ).scalar_one_or_none()
            self.assertIsNone(db_request)
            db_results = (
                (
                    session.execute(
                        select(tables.FrequencyResult).where(
                            tables.FrequencyResult.request_id == request_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            self.assertEqual(0, len(db_results))

    def test_find_user_requests(self):
        mapper = FrequencyRequestTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            db_requests = [
                tables.FrequencyRequest(
                    name=f"request_name_{i}",
                    user_id=self.__user_id,
                    niche_id=self.__niche_id,
                    results=[
                        tables.FrequencyResult(cost=10 * j, frequency=20 * j)
                        for j in range(1, i + 1)
                    ],
                )
                for i in range(1, 11)
            ]
            session.add_all(db_requests)
            session.flush()
            requests = [mapper.map(request) for request in db_requests]
        with self.__db_context.session() as session:
            service = create_frequency_service(session)
            actual_user_requests = service.find_user_requests(self.__user_id)
            for expected_request_tuple, (request_id, response_tuple) in zip(
                requests, actual_user_requests.items(), strict=True
            ):
                (
                    expected_request,
                    expected_result,
                    expected_info,
                ) = expected_request_tuple
                actual_request, actual_result, actual_info = response_tuple
                self.assertEqual(expected_info.id, request_id)
                self.assertEqual(expected_request, actual_request)
                self.assertEqual(expected_result, actual_result)
                self.assertEqual(expected_info, actual_info)
