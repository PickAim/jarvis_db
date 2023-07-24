from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Warehouse as WarehouseEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.core import Mapper
from jarvis_db.tables import Address, Warehouse


class WarehouseService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[Warehouse, WarehouseEntity],
    ):
        self.__session = session
        self.__table_mapper = table_mapper

    def create_warehouse(self, warehouse_entity: WarehouseEntity, marketplace_id: int):
        self.__session.add(
            WarehouseService.__create_warehouse_entity(warehouse_entity, marketplace_id)
        )
        self.__session.flush()

    def create_all(
        self, warehouse_entities: Iterable[WarehouseEntity], marketplace_id: int
    ):
        self.__session.add_all(
            (
                WarehouseService.__create_warehouse_entity(warehouse, marketplace_id)
                for warehouse in warehouse_entities
            )
        )
        self.__session.flush()

    def find_warehouse_by_name(self, name: str) -> tuple[WarehouseEntity, int] | None:
        warehouse = self.__session.execute(
            select(Warehouse).join(Warehouse.address).where(Warehouse.name.ilike(name))
        ).scalar_one_or_none()
        return (
            (self.__table_mapper.map(warehouse), warehouse.id)
            if warehouse is not None
            else None
        )

    def find_by_global_id(
        self, marketplace_id: int, global_id: int
    ) -> tuple[int, WarehouseEntity] | None:
        warehouse = self.__session.execute(
            select(Warehouse)
            .where(Warehouse.owner_id == marketplace_id)
            .where(Warehouse.global_id == global_id)
        ).scalar_one_or_none()
        return (
            (warehouse.id, self.__table_mapper.map(warehouse))
            if warehouse is not None
            else None
        )

    def find_all_warehouses(self, marketplace_id: int) -> dict[int, WarehouseEntity]:
        warehouses = (
            self.__session.execute(
                select(Warehouse)
                .join(Warehouse.address)
                .where(Warehouse.owner_id == marketplace_id)
            )
            .scalars()
            .all()
        )
        return {
            warehouse.id: self.__table_mapper.map(warehouse) for warehouse in warehouses
        }

    def exists_with_name(self, name: str) -> bool:
        return (
            self.__session.execute(
                select(Warehouse).where(Warehouse.name.ilike(name))
            ).scalar_one_or_none()
            is not None
        )

    def filter_existing_names(self, names: Iterable[str]) -> list[str]:
        names = list(names)
        existing_names = (
            self.__session.execute(
                select(Warehouse.name).where(Warehouse.name.in_(names))
            )
            .scalars()
            .all()
        )
        return list(set(names) - set(existing_names))

    def fileter_existing_global_ids(self, ids: Iterable[int]) -> list[int]:
        ids = list(ids)
        existing_ids = (
            self.__session.execute(
                select(Warehouse.global_id).where(Warehouse.global_id.in_(ids))
            )
            .scalars()
            .all()
        )
        return list(set(ids) - set(existing_ids))

    @staticmethod
    def __create_warehouse_entity(
        warehouse: WarehouseEntity, marketplace_id: int
    ) -> Warehouse:
        handler_type_to_int = {
            HandlerType.MARKETPLACE: 0,
            HandlerType.PARTIAL_CLIENT: 1,
            HandlerType.CLIENT: 2,
        }
        handler_type_code = handler_type_to_int[warehouse.handler_type]
        return Warehouse(
            owner_id=marketplace_id,
            global_id=warehouse.global_id,
            name=warehouse.name,
            basic_logistic_to_customer_commission=warehouse.basic_logistic_to_customer_commission,
            additional_logistic_to_customer_commission=warehouse.additional_logistic_to_customer_commission,
            logistic_from_customer_commission=warehouse.logistic_from_customer_commission,
            basic_storage_commission=warehouse.basic_storage_commission,
            additional_storage_commission=int(
                warehouse.additional_storage_commission * 100
            ),
            monopalette_storage_commission=warehouse.mono_palette_storage_commission,
            type=handler_type_code,
            address=Address(country="", region="", street="", number="", corpus=""),
        )
