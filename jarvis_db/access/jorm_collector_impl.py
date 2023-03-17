from jorm.jarvis.db_access import JORMCollector
from jorm.market.infrastructure import Niche, Warehouse

from jarvis_db.repositores.market.infrastructure import (NicheRepository,
                                                         WarehouseRepository)


class JormCollectorImpl(JORMCollector):
    def __init__(self, niche_repository: NicheRepository, warehouse_repository: WarehouseRepository):
        self.__niche_repository = niche_repository
        self.__warehouse_repository = warehouse_repository

    def get_niche(self, niche_name: str) -> Niche:
        # TODO what to do with category id
        niche, _ = self.__niche_repository.find_by_name(niche_name, 0)
        return niche

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        warehouse, _ = self.__warehouse_repository.find_by_name(warehouse_name)
        return warehouse

    def get_all_warehouses(self) -> list[Warehouse]:
        return list(self.__warehouse_repository.find_all().values())
