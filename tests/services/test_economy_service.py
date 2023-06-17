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
from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import (
    WarehouseTableToJormMapper,
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
from jarvis_db.repositores.market.infrastructure.warehouse_repository import (
    WarehouseRepository,
)
from jarvis_db.repositores.market.service.economy_request_repository import (
    EconomyRequestRepository,
)
from jarvis_db.repositores.market.service.economy_result_repository import (
    EconomyResultRepository,
)
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.tables import (
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
            address = Address(
                country="AS", region="QS", street="DD", number="HH", corpus="YU"
            )
            warehouse = Warehouse(
                owner=marketplace,
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
            self.__niche_id = niche.id
            self.__user_id = user.id
            self.__marketplace_id = marketplace.id
            self.__warehouse_id = warehouse.id
            self.__warehouse_name = warehouse.name

    def test_save(self):
        request_info = RequestInfo(date=datetime(2020, 10, 23), name="name")
        request_entity = UnitEconomyRequest(
            100,
            20,
            self.__niche_name,
            self.__category_name,
            11,
            121,
            33,
            warehouse_name="qwerty",
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
                .join(tables.UnitEconomyRequest.warehouse)
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
            self.assertEqual(self.__warehouse_id, request.warehouse_id)
            self.assertEqual(self.__warehouse_name, request.warehouse.name)

    def test_remove(self):
        request_id = 100
        result_id = 100
        with self.__db_context.session() as session, session.begin():
            request = tables.UnitEconomyRequest(
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
            result = tables.UnitEconomyResult(
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
            service = create_service(session)
            is_removed = service.remove(request_id)
            self.assertTrue(is_removed)
        with self.__db_context.session() as session:
            request = session.execute(
                select(tables.UnitEconomyRequest).where(
                    tables.UnitEconomyRequest.id == request_id
                )
            ).scalar_one_or_none()
            result = session.execute(
                select(tables.UnitEconomyResult).where(
                    tables.UnitEconomyResult.id == result_id
                )
            ).scalar_one_or_none()
            self.assertIsNone(request)
            self.assertIsNone(result)


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
        WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper()),
    )
