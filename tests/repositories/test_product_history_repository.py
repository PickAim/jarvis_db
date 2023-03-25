import unittest
from datetime import datetime

from jorm.market.items import ProductHistoryUnit
from jorm.support.types import StorageDict
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.items.leftover_mappers import (
    LeftoverJormToTableMapper, LeftoverTableToJormMapper)
from jarvis_db.repositores.mappers.market.items.product_history_mappers import (
    ProductHistoryJormToTableMapper, ProductHistoryTableToJormMapper)
from jarvis_db.repositores.market.items.product_hisory_repository import \
    ProductHistoryRepository


class ProductHistoryRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        product_id = 1
        warehouse_id = 1
        warehouse_global_id = 20
        with session() as s, s.begin():
            marketplace_id = 1
            db_marketplace = tables.Marketplace(
                id=marketplace_id, name='marketplace_1')
            db_category = tables.Category(
                name='category_id', marketplace=db_marketplace)
            db_niche = tables.Niche(
                name='niche_1',
                marketplace_commission=0,
                partial_client_commission=0,
                client_commission=0,
                return_percent=0,
                category=db_category
            )
            db_niche.category = db_category
            db_product = tables.ProductCard(
                id=product_id,
                name='product_1',
                article=1,
                cost=1,
                niche=db_niche
            )
            db_address = tables.Address(
                country='AS',
                region='QS',
                street='DD',
                number='HH',
                corpus='YU'
            )
            db_warehouse = tables.Warehouse(
                id=warehouse_id,
                owner_id=marketplace_id,
                global_id=warehouse_global_id,
                type=0,
                name='qwerty',
                address=db_address,
                basic_logistic_to_customer_commission=0,
                additional_logistic_to_customer_commission=0,
                logistic_from_customer_commission=0,
                basic_storage_commission=0,
                additional_storage_commission=0,
                monopalette_storage_commission=0
            )
            s.add(db_product)
            s.add(db_warehouse)
        self.__warehouse_id = warehouse_id
        self.__product_id = product_id
        self.__warehouse_global_id = warehouse_global_id
        self.__session = session

    def test_add(self):
        unit = ProductHistoryUnit(10, datetime.utcnow(), StorageDict())
        with self.__session() as session, session.begin():
            repository = ProductHistoryRepository(
                session, ProductHistoryTableToJormMapper(LeftoverTableToJormMapper()), ProductHistoryJormToTableMapper(LeftoverJormToTableMapper()))
            repository.add_product_history(unit, self.__product_id)
        with self.__session() as session:
            db_units = session.execute(
                select(tables.ProductHistory)
                .join(tables.ProductCard)
                .where(tables.ProductCard.id == self.__product_id)
            ).scalars().all()
            self.assertEqual(len(db_units), 1)
            db_unit = db_units[0]
            self.assertEqual(unit.cost, db_unit.cost)
            self.assertEqual(unit.unit_date, db_unit.date)
            # TODO self.assertEqual(unit.leftover, db_unit.leftover)

    def test_add_all(self):
        units = [ProductHistoryUnit(
            i * 10, datetime.utcnow(), StorageDict()) for i in range(1, 11)]
        with self.__session() as session, session.begin():
            repository = ProductHistoryRepository(
                session, ProductHistoryTableToJormMapper(LeftoverTableToJormMapper()), ProductHistoryJormToTableMapper(LeftoverJormToTableMapper()))
            repository.add_all_product_histories(units, self.__product_id)
        with self.__session() as session:
            db_units = session.execute(
                select(tables.ProductHistory)
                .join(tables.ProductCard)
                .where(tables.ProductCard.id == self.__product_id)
            ).scalars().all()
            for unit, db_unit in zip(units, db_units, strict=True):
                self.assertEqual(unit.cost, db_unit.cost)
                self.assertEqual(unit.unit_date, db_unit.date)
                # TODO self.assertEqual(unit.leftover, db_unit.leftover)

    def test_fetct_histories(self):
        expected_units = [ProductHistoryUnit(
            i * 10, datetime.utcnow(), StorageDict({self.__warehouse_global_id: {'abc': 1, 'def': 2}})) for i in range(1, 11)]
        to_table_mapper = ProductHistoryJormToTableMapper(
            LeftoverJormToTableMapper())
        with self.__session() as session, session.begin():
            db_units = [to_table_mapper.map(unit) for unit in expected_units]
            for db_unit in db_units:
                db_unit.product_id = self.__product_id
                for leftover in db_unit.leftovers:
                    leftover.warehouse_id = self.__warehouse_id
            session.add_all(db_units)
        with self.__session() as session:
            repository = ProductHistoryRepository(
                session, ProductHistoryTableToJormMapper(LeftoverTableToJormMapper()), ProductHistoryJormToTableMapper(LeftoverJormToTableMapper()))
            actual_units = repository.get_product_history(
                self.__product_id).history
            for actual_unit, expected_unit in zip(actual_units, expected_units, strict=True):
                self.assertEqual(expected_unit.cost, actual_unit.cost)
                self.assertEqual(expected_unit.leftover, actual_unit.leftover)
                self.assertEqual(expected_unit.unit_date,
                                 actual_unit.unit_date)
