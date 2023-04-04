import unittest

from jorm.market.infrastructure import Address as AddressEntity
from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Warehouse as WarehouseEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.infrastructure.warehouse_mappers import \
    WarehouseTableToJormMapper
from jarvis_db.repositores.market.infrastructure.warehouse_repository import \
    WarehouseRepository
from jarvis_db.services.market.infrastructure.warehouse_service import \
    WarehouseService
from jarvis_db.tables import Address, Marketplace, Warehouse
from tests.db_context import DbContext


class WarehouseServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            marketplace = Marketplace(name='marketplace_1')
            session.add(marketplace)
            session.flush()
            self.__marketplace_id = marketplace.id

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            warehouse_name = 'warehose_1'
            warehouse_entity = WarehouseEntity(
                warehouse_name,
                200,
                HandlerType.CLIENT,
                AddressEntity(''),
            )
            service = create_service(session)
            service.create_warehouse(warehouse_entity, self.__marketplace_id)
        with self.__db_context.session() as session:
            warehouse = session.execute(
                select(Warehouse)
                .where(Warehouse.name == warehouse_name)
            ).scalar_one()
            mapper = WarehouseTableToJormMapper()
            actual = mapper.map(warehouse)
            self.assertEqual(warehouse_entity, actual)

    def test_find_by_name(self):
        warehouse_name = 'warehouse_1'
        with self.__db_context.session() as session, session.begin():
            session.add(Warehouse(
                owner_id=self.__marketplace_id,
                global_id=200,
                type=1,
                name=warehouse_name,
                address=Address(
                    country='AS',
                    region='QS',
                    street='DD',
                    number='HH',
                    corpus='YU'
                ),
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0
            ))
        with self.__db_context.session() as session:
            service = create_service(session)
            found = service.find_warehouse_by_name(warehouse_name)
            self.assertEqual(warehouse_name, found.name)

    def test_find_all(self):
        expected_count = 10
        with self.__db_context.session() as session, session.begin():
            db_warehouses = [Warehouse(
                owner_id=self.__marketplace_id,
                global_id=200 + 10 * i,
                type=i % 3,
                name=f'warehouse_{i}',
                address=Address(
                    country='AS',
                    region='QS',
                    street='DD',
                    number='HH',
                    corpus='YU'
                ),
                basic_logistic_to_customer_commission=i,
                additional_logistic_to_customer_commission=i * 2,
                logistic_from_customer_commission=i + 1,
                basic_storage_commission=i + 3,
                additional_storage_commission=i * 4,
                monopalette_storage_commission=i + 6
            ) for i in range(1, expected_count + 1)]
            mapper = WarehouseTableToJormMapper()
            session.add_all(db_warehouses)
            expected_warehouses = [mapper.map(
                warehouse) for warehouse in db_warehouses]
        with self.__db_context.session() as session:
            service = create_service(session)
            actual_warehouses = service.find_all_warehouses()
            for expected, actual in zip(expected_warehouses, actual_warehouses, strict=True):
                self.assertEqual(expected, actual)


def create_service(session: Session):
    return WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())
