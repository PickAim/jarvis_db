import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.market.items.product_history_repository import \
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

    def test_find_product_histories(self):
        with self.__session() as session, session.begin():
            histories_to_add = 10
            session.add_all([tables.ProductHistory(
                cost=10, product_id=self.__product_id) for _ in range(histories_to_add)])
        with self.__session() as session:
            repository = ProductHistoryRepository(session)
            histories = repository.find_product_histories(self.__product_id)
            self.assertEqual(histories_to_add, len(histories))
