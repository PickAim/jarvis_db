from typing import Iterable
from jorm.market.infrastructure import Warehouse as WarehouseEntity

from jarvis_db.core import Mapper
from jarvis_db.repositores.market.infrastructure.warehouse_repository import \
    WarehouseRepository
from jarvis_db.tables import Address, Warehouse
from jorm.market.infrastructure import HandlerType


class WarehouseService:
    def __init__(
            self,
            warehouse_repository: WarehouseRepository,
            entity_mapper: Mapper[Warehouse, WarehouseEntity]
    ) -> None:
        self.__warehouse_repository = warehouse_repository
        self.__entity_mapper = entity_mapper

    def create_warehouse(self, warehouse_entity: WarehouseEntity, marketplace_id: int):
        hanler_type = 0
        match warehouse_entity.handler_type:
            case HandlerType.PARTIAL_CLIENT:
                hanler_type = 1
            case HandlerType.CLIENT:
                hanler_type = 2
        self.__warehouse_repository.add(
            Warehouse(
                owner_id=marketplace_id,
                global_id=warehouse_entity.global_id,
                name=warehouse_entity.name,
                basic_logistic_to_customer_commission=warehouse_entity.basic_logistic_to_customer_commission,
                additional_logistic_to_customer_commission=warehouse_entity.additional_logistic_to_customer_commission,
                logistic_from_customer_commission=warehouse_entity.logistic_from_customer_commission,
                basic_storage_commission=warehouse_entity.basic_storage_commission,
                additional_storage_commission=int(
                    warehouse_entity.additional_storage_commission * 100),
                monopalette_storage_commission=warehouse_entity.mono_palette_storage_commission,
                type=hanler_type,
                address=Address(
                    country='',
                    region='',
                    street='',
                    number='',
                    corpus=''),
            ))

    def create_all(self, warehouse_entities: Iterable[WarehouseEntity], marketplace_id: int):
        for entity in warehouse_entities:
            self.create_warehouse(entity, marketplace_id)

    def find_warehouse_by_name(self, name: str) -> WarehouseEntity:
        return self.__entity_mapper.map(
            self.__warehouse_repository.find_by_name(name))

    def find_all_warehouses(self) -> list[WarehouseEntity]:
        return [self.__entity_mapper.map(
            warehouse) for warehouse in self.__warehouse_repository.find_all()]
