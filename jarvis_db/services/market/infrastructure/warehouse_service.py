from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Warehouse as WarehouseEntity

from jarvis_db.core import Mapper
from jarvis_db.repositores.market.infrastructure.warehouse_repository import \
    WarehouseRepository
from jarvis_db.tables import Address, Warehouse


class WarehouseService:
    def __init__(
            self,
            warehouse_repository: WarehouseRepository,
            table_mapper: Mapper[Warehouse, WarehouseEntity]
    ) -> None:
        self.__warehouse_repository = warehouse_repository
        self.__table_mapper = table_mapper

    def create_warehouse(self, warehouse_entity: WarehouseEntity, marketplace_id: int):
        handler_type = 0
        match warehouse_entity.handler_type:
            case HandlerType.PARTIAL_CLIENT:
                handler_type = 1
            case HandlerType.CLIENT:
                handler_type = 2
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
                type=handler_type,
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

    def find_warehouse_by_name(self, name: str) -> tuple[WarehouseEntity, int]:
        warehouse = self.__warehouse_repository.find_by_name(name)
        return self.__table_mapper.map(warehouse), warehouse.id

    def find_all_warehouses(self) -> dict[int, WarehouseEntity]:
        warehouses = self.__warehouse_repository.find_all()
        return {warehouse.id: self.__table_mapper.map(warehouse) for warehouse in warehouses}

    def exists_with_name(self, name: str) -> bool:
        return self.__warehouse_repository.exists_with_name(name)

    def filter_existing_names(self, names: Iterable[str]) -> list[str]:
        return self.__warehouse_repository.filter_existing_names(list(names))
