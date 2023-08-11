import unittest

from sqlalchemy import select
from jarvis_db.factories.mappers import create_product_table_mapper
from jarvis_db.factories.services import create_user_items_service
from jarvis_db.mappers.market.infrastructure.warehouse_mappers import (
    WarehouseTableToJormMapper,
)
from jarvis_db.schemas import ProductCard, User, Warehouse

from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class UserItemServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_users(1)
            self.__user_id = session.execute(select(User.id)).scalar_one()

    def test_appends_product(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_products(1)
            product_id = session.execute(select(ProductCard.id)).scalar_one()
        with self.__db_context.session() as session, session.begin():
            service = create_user_items_service(session)
            service.append_product(self.__user_id, product_id)
        with self.__db_context.session() as session:
            user = session.execute(
                select(User).outerjoin(User.products).where(User.id == self.__user_id)
            ).scalar_one()
            self.assertEqual(1, len(user.products))
            product = user.products[0]
            self.assertEqual(product_id, product.id)

    def test_remove_product(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_products(1)
            product = session.execute(select(ProductCard)).scalar_one()
            user = session.execute(select(User).outerjoin(User.products)).scalar_one()
            user.products.append(product)
            product_id = product.id
        with self.__db_context.session() as session, session.begin():
            service = create_user_items_service(session)
            service.remove_product(self.__user_id, product_id)
            user = session.execute(
                select(User).outerjoin(User.products).where(User.id == self.__user_id)
            ).scalar_one()
            self.assertEqual(0, len(user.products))

    def test_append_wareouse(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_warehouses(1)
            warehouse_id = session.execute(select(Warehouse.id)).scalar_one()
        with self.__db_context.session() as session, session.begin():
            service = create_user_items_service(session)
            service.append_warehouse(self.__user_id, warehouse_id)
            user = session.execute(select(User).outerjoin(User.warehouses)).scalar_one()
            self.assertEqual(1, len(user.warehouses))
            warehouse = user.warehouses[0]
            self.assertEqual(warehouse_id, warehouse.id)

    def test_remove_warehouse(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_warehouses(1)
            warehouse = session.execute(select(Warehouse)).scalar_one()
            warehouse_id = warehouse.id
            user = session.execute(
                select(User).where(User.id == self.__user_id)
            ).scalar_one()
            user.warehouses.append(warehouse)
        with self.__db_context.session() as session, session.begin():
            service = create_user_items_service(session)
            service.remove_warehouse(self.__user_id, warehouse_id)
            user = session.execute(
                select(User).outerjoin(User.warehouses).where(User.id == self.__user_id)
            ).scalar_one()
            self.assertEqual(0, len(user.warehouses))

    def test_fetch_user_products(self):
        mapper = create_product_table_mapper()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_products(10)
            products = session.execute(select(ProductCard)).scalars().all()
            user = session.execute(
                select(User).where(User.id == self.__user_id)
            ).scalar_one()
            user.products.extend(products)
            session.flush()
            expected = {product.id: mapper.map(product) for product in products}
        with self.__db_context.session() as session:
            service = create_user_items_service(session)
            actual = service.fetch_user_products(self.__user_id)
            self.assertDictEqual(expected, actual)

    def test_fetch_user_warehouses(self):
        mapper = WarehouseTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_warehouses(10)
            warehouses = session.execute(select(Warehouse)).scalars().all()
            user = session.execute(
                select(User).where(User.id == self.__user_id)
            ).scalar_one()
            user.warehouses.extend(warehouses)
            session.flush()
            expected = {warehouse.id: mapper.map(warehouse) for warehouse in warehouses}
        with self.__db_context.session() as session:
            service = create_user_items_service(session)
            actual = service.fetch_user_warehouses(self.__user_id)
            self.assertDictEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
