from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Marketplace, Warehouse


class WarehouseRepository(AlchemyRepository[Warehouse]):
    def find_by_name(self, name: str) -> Warehouse | None:
        warehouse = self._session.execute(
            select(Warehouse).where(Warehouse.name.ilike(name))
        ).scalar()
        return warehouse

    def find_by_global_id(self, global_id: int, marketplace_id: int) -> Warehouse:
        warehouse = self._session.execute(
            select(Warehouse)
            .join(Warehouse.owner)
            .where(Marketplace.id == marketplace_id)
            .where(Warehouse.global_id == global_id)
        ).scalar_one()
        return warehouse

    def find_all(self) -> list[Warehouse]:
        warehouses = self._session.execute(select(Warehouse)).scalars().all()
        return list(warehouses)

    def find_all_by_marketplace(self, marketplace_id: int) -> list[Warehouse]:
        warehouses = (
            self._session.execute(
                select(Warehouse)
                .join(Warehouse.owner)
                .where(Marketplace.id == marketplace_id)
            )
            .scalars()
            .all()
        )
        return list(warehouses)

    def exists_with_name(self, name: str) -> bool:
        return (
            self._session.execute(
                select(Warehouse).where(Warehouse.name.ilike(name))
            ).scalar()
            is not None
        )

    def filter_existing_names(self, names: list[str]) -> list[str]:
        existing_names = (
            self._session.execute(
                select(Warehouse.name).where(Warehouse.name.in_(names))
            )
            .scalars()
            .all()
        )
        return list(set(names) - set(existing_names))
