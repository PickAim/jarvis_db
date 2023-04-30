from jorm.jarvis.db_access import JORMCollector
from jorm.market.infrastructure import Niche, Product, Warehouse
from jorm.market.person import User
from jorm.market.service import (FrequencyRequest, FrequencyResult,
                                 RequestInfo, UnitEconomyRequest,
                                 UnitEconomyResult)

from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import \
    WarehouseService


class JormCollectorImpl(JORMCollector):
    def __init__(self, niche_service: NicheService, warehouse_service: WarehouseService):
        self.__niche_service = niche_service
        self.__warehouse_service = warehouse_service

    def get_niche(self, niche_name: str, marketplace_id: int) -> Niche | None:
        # TODO what to do with category id
        niche_result = self.__niche_service.find_by_name(
            niche_name, marketplace_id)
        if niche_result is None:
            return None
        niche, _ = niche_result
        return niche

    def get_warehouse(self, warehouse_name: str) -> Warehouse | None:
        warehouse_result = self.__warehouse_service.find_warehouse_by_name(
            warehouse_name)
        if warehouse_result is None:
            return None
        warehouse, _ = warehouse_result
        return warehouse

    def get_all_warehouses(self) -> list[Warehouse] | None:
        return list(self.__warehouse_service.find_all_warehouses().values())

    def get_products_by_user(self, user: User) -> list[Product]:
        ...

    def get_all_unit_economy_results(self, user: User) \
            -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
        ...

    def get_all_frequency_results(self, user: User) \
            -> list[tuple[FrequencyRequest, FrequencyResult, RequestInfo]]:
        ...
