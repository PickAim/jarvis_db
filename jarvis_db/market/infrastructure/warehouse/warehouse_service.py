from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Warehouse as WarehouseEntity
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from jarvis_db.core import Mapper
from jarvis_db.schemas import Address, Warehouse


class WarehouseService:
    __handler_type_to_int = {
        HandlerType.MARKETPLACE: 0,
        HandlerType.PARTIAL_CLIENT: 1,
        HandlerType.CLIENT: 2,
    }

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

    def find_by_id(self, warehouse_id: int) -> WarehouseEntity | None:
        warehouse = self.__session.execute(
            select(Warehouse)
            .where(Warehouse.id == warehouse_id)
            .options(joinedload(Warehouse.address))
        ).scalar_one_or_none()
        return self.__table_mapper.map(warehouse) if warehouse is not None else None

    def find_warehouse_by_name(
        self, name: str, marketplace_id: int
    ) -> tuple[WarehouseEntity, int] | None:
        warehouse = self.__session.execute(
            select(Warehouse)
            .where(Warehouse.marketplace_id == marketplace_id)
            .where(Warehouse.name.ilike(name))
            .options(joinedload(Warehouse.address))
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
            .where(Warehouse.marketplace_id == marketplace_id)
            .where(Warehouse.global_id == global_id)
            .options(joinedload(Warehouse.address))
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
                .where(Warehouse.marketplace_id == marketplace_id)
                .options(joinedload(Warehouse.address))
            )
            .scalars()
            .all()
        )
        return {
            warehouse.id: self.__table_mapper.map(warehouse) for warehouse in warehouses
        }

    def exists_with_name(self, name: str, marketplace_id: int) -> bool:
        return (
            self.__session.execute(
                select(Warehouse)
                .where(Warehouse.marketplace_id == marketplace_id)
                .where(Warehouse.name.ilike(name))
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

    def filter_existing_global_ids(self, ids: Iterable[int]) -> list[int]:
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
        handler_type_code = WarehouseService.__handler_type_to_int.get(
            warehouse.handler_type, 0
        )
        return Warehouse(
            marketplace_id=marketplace_id,
            global_id=warehouse.global_id,
            name=warehouse.name,
            type=handler_type_code,
            main_coefficient=int(warehouse.main_coefficient * 100),
            address=Address(
                country="",
                region=warehouse.address.region,
                street=warehouse.address.street,
                number="",
                corpus="",
            ),
        )
