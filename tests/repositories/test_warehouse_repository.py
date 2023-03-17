import unittest

from jorm.market.infrastructure import Address, HandlerType, Warehouse
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import (
    WarehouseJormToTableMapper, WarehouseTableToJormMapper)
from jarvis_db.repositores.market.infrastructure import WarehouseRepository


class WarehouseRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        marketplace_id = 1
        with session() as s, s.begin():
            s.add(tables.Marketplace(id=marketplace_id, name='marketplace#1'))
        self.__marketplace_id = marketplace_id
        self.__session = session

    def test_add(self):
        warehouse = Warehouse('warehouse#1', 12, HandlerType.CLIENT, Address())
        with self.__session() as session, session.begin():
            repository = WarehouseRepository(
                session, WarehouseTableToJormMapper(), WarehouseJormToTableMapper())
            repository.add(
                warehouse, self.__marketplace_id)
        with self.__session() as session:
            db_warehouse = session.execute(
                select(tables.Warehouse)
                .join(tables.Warehouse.owner)
                .where(tables.Marketplace.id == self.__marketplace_id)
            ).scalar_one()
            self.assertEqual(warehouse.name, db_warehouse.name)

    def test_add_all(self):
        warehouses_to_add = 10
        warehouses = [
            Warehouse(f'warehouse#{i}', i, HandlerType.PARTIAL_CLIENT, Address()) for i in range(1, warehouses_to_add + 1)
        ]
        with self.__session() as session, session.begin():
            repository = WarehouseRepository(
                session, WarehouseTableToJormMapper(), WarehouseJormToTableMapper())
            repository.add_all(
                warehouses, self.__marketplace_id)
        with self.__session() as session:
            db_warehouses = session.execute(
                select(tables.Warehouse)
                .join(tables.Warehouse.owner)
                .where(tables.Marketplace.id == self.__marketplace_id)
            ).scalars().all()
            for warehouse, db_warehouse in zip(warehouses, db_warehouses, strict=True):
                self.assertEqual(warehouse.name, db_warehouse.name)
