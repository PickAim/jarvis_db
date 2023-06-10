from jorm.jarvis.db_access import JORMCollector
from jorm.market.infrastructure import Niche, Product, Warehouse
from jorm.market.person import User
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)

from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService


class JormCollectorImpl(JORMCollector):
    def __init__(
        self,
        niche_service: NicheService,
        warehouse_service: WarehouseService,
        unit_economy_service: EconomyService,
        frequency_service: FrequencyService,
    ):
        self.__niche_service = niche_service
        self.__warehouse_service = warehouse_service
        self.__unit_economy_service = unit_economy_service
        self.__frequency_service = frequency_service

    def get_niche(self, niche_name: str, marketplace_id: int) -> Niche | None:
        niche_result = self.__niche_service.find_by_name(niche_name, marketplace_id)
        if niche_result is None:
            return None
        niche, _ = niche_result
        return niche

    def get_warehouse(self, warehouse_name: str) -> Warehouse | None:
        warehouse_result = self.__warehouse_service.find_warehouse_by_name(
            warehouse_name
        )
        if warehouse_result is None:
            return None
        warehouse, _ = warehouse_result
        return warehouse

    def get_all_warehouses(self) -> list[Warehouse] | None:
        return list(self.__warehouse_service.find_all_warehouses().values())

    def get_products_by_user(self, user: User) -> list[Product]:
        ...

    def get_all_unit_economy_results(
        self, user: User
    ) -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
        return list(
            self.__unit_economy_service.find_user_requests(user.user_id).values()
        )

    def get_all_frequency_results(
        self, user: User
    ) -> list[tuple[FrequencyRequest, FrequencyResult, RequestInfo]]:
        return list(self.__frequency_service.find_user_requests(user.user_id).values())
