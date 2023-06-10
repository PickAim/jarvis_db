from jorm.market.infrastructure import Marketplace, Warehouse

from jarvis_db import tables
from jarvis_db.core import Mapper


class MarketplaceJormToTableMapper(Mapper[Marketplace, tables.Marketplace]):
    def __init__(self, warehouse_mapper: Mapper[Warehouse, tables.Warehouse]):
        self.__warehouse_mapper = warehouse_mapper

    def map(self, value: Marketplace) -> tables.Marketplace:
        return tables.Marketplace(
            name=value.name,
            warehouses=[
                self.__warehouse_mapper.map(warehouse) for warehouse in value.warehouses
            ],
        )


class MarketplaceTableToJormMapper(Mapper[tables.Marketplace, Marketplace]):
    def __init__(self, warehouse_mapper: Mapper[tables.Warehouse, Warehouse]):
        self.__warehouse_mapper = warehouse_mapper

    def map(self, value: tables.Marketplace) -> Marketplace:
        return Marketplace(
            value.name,
            [self.__warehouse_mapper.map(warehouse) for warehouse in value.warehouses],
        )
