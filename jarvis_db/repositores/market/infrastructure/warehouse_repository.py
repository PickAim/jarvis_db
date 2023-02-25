from typing import Iterable

from jorm.market.infrastructure import Warehouse
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class WarehouseRepository:
    def __init__(
            self, session: Session,
            to_jorm_mapper: Mapper[tables.Warehouse, Warehouse],
            to_table_mapper: Mapper[Warehouse, tables.Warehouse]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add_by_marketplace_name(self, warehouse: Warehouse, marketplace_name: str):
        db_marketplace = self.__session.execute(
            select(tables.Marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
        ).scalar_one()
        db_marketplace.warehouses.append(self.__to_table_mapper.map(warehouse))

    def add_all_by_marketplace_name(self, warehouses: Iterable[Warehouse], marketplace_name: str):
        db_marketplace = self.__session.execute(
            select(tables.Marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
        ).scalar_one()
        db_marketplace.warehouses.extend(
            (self.__to_table_mapper.map(warehouse) for warehouse in warehouses))

    def fetch_all_by_marketplace_name(self, marketplace_name: str) -> list[Warehouse]:
        db_warehouses = self.__session.execute(
            select(tables.Warehouse)
            .join(tables.Warehouse.owner)
            .where(tables.Marketplace.name.ilike(marketplace_name))
        ).scalars().all()
        return [self.__to_jorm_mapper.map(warehouse) for warehouse in db_warehouses]
