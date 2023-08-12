from jorm.market.infrastructure import Product
from jorm.market.person import Warehouse as WarehouseDomain
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, contains_eager, load_only, joinedload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import (
    Category,
    Niche,
    ProductCard,
    User,
    UserToWarehouse,
    Warehouse,
    UserToProduct,
)


class UserItemsService:
    def __init__(
        self,
        session: Session,
        product_mapper: Mapper[ProductCard, Product],
        warehouse_mapper: Mapper[Warehouse, WarehouseDomain],
    ):
        self.__session = session
        self.__product_mapper = product_mapper
        self.__warehouse_mapper = warehouse_mapper

    def append_product(self, user_id: int, product_id: int):
        self.__session.add(UserToProduct(user_id=user_id, product_id=product_id))
        self.__session.flush()

    def remove_product(self, user_id: int, product_id: int):
        self.__session.execute(
            delete(UserToProduct)
            .where(UserToProduct.user_id == user_id)
            .where(UserToProduct.product_id == product_id)
        )
        self.__session.flush()

    def fetch_user_products(
        self, user_id: int, marketplace_id: int
    ) -> dict[int, Product]:
        products = (
            self.__session.execute(
                select(ProductCard)
                .join(UserToProduct, ProductCard.id == UserToProduct.product_id)
                .join(ProductCard.niche)
                .join(Niche.category)
                .where(Category.marketplace_id == marketplace_id)
                .where(UserToProduct.user_id == user_id)
                .distinct()
            )
            .scalars()
            .all()
        )
        return {product.id: self.__product_mapper.map(product) for product in products}

    def append_warehouse(self, user_id: int, warehouse_id: int):
        self.__session.add(UserToWarehouse(user_id=user_id, warehouse_id=warehouse_id))
        self.__session.flush()

    def remove_warehouse(self, user_id: int, warehouse_id: int):
        self.__session.execute(
            delete(UserToWarehouse)
            .where(UserToWarehouse.user_id == user_id)
            .where(UserToWarehouse.warehouse_id == warehouse_id)
        )
        self.__session.flush()

    def fetch_user_warehouses(
        self, user_id: int, marketplace_id: int
    ) -> dict[int, WarehouseDomain]:
        warehouses = (
            self.__session.execute(
                select(Warehouse)
                .join(UserToWarehouse, Warehouse.id == UserToWarehouse.warehouse_id)
                .where(UserToWarehouse.user_id == user_id)
                .where(Warehouse.marketplace_id == marketplace_id)
                .distinct()
            )
            .scalars()
            .all()
        )
        return {
            warehouse.id: self.__warehouse_mapper.map(warehouse)
            for warehouse in warehouses
        }
