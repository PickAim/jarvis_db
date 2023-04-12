from jorm.jarvis.db_access import JORMCollector
from jorm.market.infrastructure import Niche, Warehouse

from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import \
    WarehouseService


class JormCollectorImpl(JORMCollector):
    def __init__(self, niche_service: NicheService, warehouse_service: WarehouseService):
        self.__niche_service = niche_service
        self.__warehouse_service = warehouse_service

    def get_niche(self, niche_name: str) -> Niche:
        # TODO what to do with category id
        niche, _ = self.__niche_service.find_by_name(niche_name, 0)
        return niche

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        warehouse, _ = self.__warehouse_service.find_warehouse_by_name(
            warehouse_name)
        return warehouse

    def get_all_warehouses(self) -> list[Warehouse]:
        return list(self.__warehouse_service.find_all_warehouses().values())
