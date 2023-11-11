from jorm.market.infrastructure import Marketplace, Warehouse

from jarvis_db import schemas
from jarvis_db.core import Mapper


class MarketplaceJormToTableMapper(Mapper[Marketplace, schemas.Marketplace]):
    def __init__(self, warehouse_mapper: Mapper[Warehouse, schemas.Warehouse]):
        self.__warehouse_mapper = warehouse_mapper

    def map(self, value: Marketplace) -> schemas.Marketplace:
        return schemas.Marketplace(
            name=value.name,
            warehouses=[
                self.__warehouse_mapper.map(warehouse) for warehouse in value.warehouses
            ],
        )


class MarketplaceTableToJormMapper(Mapper[schemas.Marketplace, Marketplace]):
    def __init__(self, warehouse_mapper: Mapper[schemas.Warehouse, Warehouse]):
        self.__warehouse_mapper = warehouse_mapper

    def map(self, value: schemas.Marketplace) -> Marketplace:
        return Marketplace(
            value.name,
            [self.__warehouse_mapper.map(warehouse) for warehouse in value.warehouses],
        )
