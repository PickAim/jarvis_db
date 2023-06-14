import unittest
from datetime import datetime

from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.repositores.mappers.market.infrastructure.category_mappers import (
    CategoryTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.infrastructure.niche_mappers import (
    NicheTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.service.economy_request_mappers import (
    EconomyRequestTableToJormMapper,
)
from jarvis_db.repositores.mappers.market.service.economy_result_mappers import (
    EconomyResultTableToJormMapper,
)
from jarvis_db.repositores.market.infrastructure.category_repository import (
    CategoryRepository,
)
from jarvis_db.repositores.market.infrastructure.niche_repository import NicheRepository
from jarvis_db.repositores.market.service.economy_request_repository import (
    EconomyRequestRepository,
)
from jarvis_db.repositores.market.service.economy_result_repository import (
    EconomyResultRepository,
)
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.tables import Account, Category, Marketplace, Niche, User
from tests.db_context import DbContext


class EconomyServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
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
            user = User(name="", profit_tax=1, account=account)
            session.add(user)
            session.add(niche)
            session.flush()
            self.__user_id = user.id
            self.__marketplace_id = marketplace.id

    def test_save(self):
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        request_entity = UnitEconomyRequest(
            100, 20, self.__niche_name, self.__category_name, 11, 121, 33
        )
        result = UnitEconomyResult(200, 300, 12, 25, 151, 134, 12355, 2, 1.2, 2.0)
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            request_id = service.save_request(
                request_info,
                request_entity,
                result,
                self.__user_id,
                self.__marketplace_id,
            )
        with self.__db_context.session() as session:
            db_result = session.execute(
                select(tables.UnitEconomyResult)
                .where(tables.UnitEconomyResult.request_id == request_id)
                .join(tables.UnitEconomyResult.request)
            ).scalar_one()
            request = db_result.request
            self.assertEqual(request_info.date, request.date)
            self.assertEqual(result.product_cost, db_result.product_cost)
            self.assertEqual(result.pack_cost, db_result.pack_cost)
            self.assertEqual(
                result.marketplace_commission, db_result.marketplace_commission
            )
            self.assertEqual(result.logistic_price, db_result.logistic_price)
            self.assertEqual(result.margin, db_result.margin)
            self.assertEqual(result.recommended_price, db_result.recommended_price)
            self.assertEqual(result.transit_profit, db_result.transit_profit)
            self.assertEqual(result.roi, db_result.roi)
            self.assertEqual(result.transit_margin, db_result.transit_margin_percent)
            self.assertEqual(result.storage_price, db_result.storage_price)


def create_service(session: Session) -> EconomyService:
    niche_mapper = NicheTableToJormMapper()
    return EconomyService(
        EconomyRequestRepository(session),
        EconomyResultRepository(session),
        EconomyResultTableToJormMapper(EconomyRequestTableToJormMapper()),
        CategoryService(
            CategoryRepository(session),
            CategoryTableToJormMapper(niche_mapper),
        ),
        NicheService(NicheRepository(session), niche_mapper),
    )
