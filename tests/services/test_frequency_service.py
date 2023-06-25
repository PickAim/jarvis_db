import unittest
from datetime import datetime

from jorm.market.service import FrequencyRequest, FrequencyResult, RequestInfo
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.repositores.mappers.market.service.frequency_request_mappers import (
    FrequencyRequestTableToJormMapper,
)
from jarvis_db.repositores.market.infrastructure.niche_repository import NicheRepository
from jarvis_db.repositores.market.service.frequency_request_repository import (
    FrequencyRequestRepository,
)
from jarvis_db.repositores.market.service.frequency_result_repository import (
    FrequencyResultRepository,
)
from jarvis_db.services.market.service.frequency_service import FrequencyService
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
            self.__niche_id = niche.id
            self.__marketplace_id = marketplace.id

    def test_save(self):
        request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
        request = FrequencyRequest(
            niche_name=self.__niche_name,
            category_name=self.__category_name,
            marketplace_id=self.__marketplace_id,
        )
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
                .join(tables.FrequencyRequest.niche)
                .join(tables.Niche.category)
                .distinct()
            ).scalar_one()
            self.assertEqual(request_info.name, db_request.name)
            self.assertEqual(request_info.date, db_request.date)
            self.assertEqual(request.niche_name, db_request.niche.name)
            self.assertEqual(request.category_name, db_request.niche.category.name)
            self.assertEqual(
                request.marketplace_id, db_request.niche.category.marketplace_id
            )
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
                niche_id=self.__niche_id,
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
        NicheRepository(session),
        FrequencyResultRepository(session),
        FrequencyRequestTableToJormMapper(),
    )
