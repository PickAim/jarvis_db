from datetime import datetime
import unittest

from sqlalchemy import select
from jarvis_db.repositores.mappers.market.service.frequency_request_mappers import (
    FrequencyRequestTableToJormMapper,
)
from jarvis_db.repositores.market.service.frequency_request_repository import (
    FrequencyRequestRepository,
)
from jarvis_db.repositores.market.service.frequency_result_repository import (
    FrequencyResultRepository,
)
from jarvis_db.services.market.service.frequency_service import FrequencyService
from sqlalchemy.orm import Session
from jarvis_db.tables import Account, User

from tests.db_context import DbContext
from jorm.market.service import FrequencyRequest, FrequencyResult, RequestInfo
from jarvis_db import tables


class FrequencyServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            account = Account(phone="", email="", password="")
            user = User(name="", profit_tax=1, account=account)
            session.add(user)
            session.flush()
            self.__user_id = user.id

    def test_save(self):
        request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
        request = FrequencyRequest("search")
        result = FrequencyResult({i: i + 1 for i in range(10)})
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
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
                .distinct()
            ).scalar_one()
            self.assertEqual(request_info.name, db_request.name)
            self.assertEqual(request_info.date, db_request.date)
            self.assertEqual(request.search_str, db_request.search_str)
            for result_pair, result_unit in zip(
                result.frequencies.items(), db_request.results, strict=True
            ):
                cost, frequency = result_pair
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
                search_str="search",
            )
            results = [
                tables.FrequencyResult(cost=i * 10, frequency=i * 20, request=request)
                for i in range(10)
            ]
            session.add_all(results)
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
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


def create_service(session: Session) -> FrequencyService:
    return FrequencyService(
        FrequencyRequestRepository(session),
        FrequencyResultRepository(session),
        FrequencyRequestTableToJormMapper(),
    )
