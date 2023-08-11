from jorm.jarvis.db_access import JORMCollector
from jorm.market.infrastructure import Category, Marketplace, Niche, Product, Warehouse
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)

from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import (
    MarketplaceService,
)
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService


class JormCollectorImpl(JORMCollector):
    def __init__(
        self,
        marketplace_service: MarketplaceService,
        niche_service: NicheService,
        category_service: CategoryService,
        warehouse_service: WarehouseService,
        unit_economy_service: EconomyService,
        frequency_service: FrequencyService,
    ):
        self.__marketplace_service = marketplace_service
        self.__niche_service = niche_service
        self.__category_service = category_service
        self.__warehouse_service = warehouse_service
        self.__unit_economy_service = unit_economy_service
        self.__frequency_service = frequency_service

    def get_all_marketplaces(self) -> dict[int, Marketplace]:
        return self.__marketplace_service.find_all()

    def get_all_marketplaces_atomic(self) -> dict[int, Marketplace]:
        return self.__marketplace_service.fetch_all_atomic()

    def get_all_categories(self, marketplace_id: int) -> dict[int, Category]:
        return self.__category_service.find_all_in_marketplace(marketplace_id)

    def get_all_categories_atomic(self, marketplace_id: int) -> dict[int, Category]:
        return self.__category_service.fetch_all_in_marketplace_atomic(marketplace_id)

    def get_all_niches(self, category_id: int) -> dict[int, Niche]:
        return self.__niche_service.find_all_in_category(category_id)

    def get_all_niches_atomic(self, category_id: int) -> dict[int, Niche]:
        return self.__niche_service.fetch_all_in_category_atomic(category_id)

    def get_niche(
        self, niche_name: str, category_id: int, marketplace_id: int
    ) -> Niche | None:
        niche_tuple = self.__niche_service.find_by_name_atomic(niche_name, category_id)
        if niche_tuple is None:
            return None
        niche, _ = niche_tuple
        return niche

    def get_warehouse(
        self, warehouse_name: str, marketplace_id: int
    ) -> Warehouse | None:
        warehouse_result = self.__warehouse_service.find_warehouse_by_name(
            warehouse_name, marketplace_id
        )
        if warehouse_result is None:
            return None
        warehouse, _ = warehouse_result
        return warehouse

    def get_all_warehouses(self, marketplace_id: int) -> dict[int, Warehouse]:
        return self.__warehouse_service.find_all_warehouses(marketplace_id)

    def get_all_warehouses_atomic(self, marketplace_id: int) -> dict[int, Warehouse]:
        return self.__warehouse_service.find_all_warehouses(marketplace_id)

    def get_products_by_user(
        self, user_id: int, marketplace_id: int
    ) -> dict[int, Product]:
        return {}

    def get_users_warehouses(
        self, user_id: int, marketplace_id: int
    ) -> dict[int, Warehouse]:
        return {}

    def get_all_unit_economy_results(
        self, user_id: int
    ) -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
        return list(self.__unit_economy_service.find_user_requests(user_id).values())

    def get_all_frequency_results(
        self, user_id: int
    ) -> list[tuple[FrequencyRequest, FrequencyResult, RequestInfo]]:
        return list(self.__frequency_service.find_user_requests(user_id).values())
