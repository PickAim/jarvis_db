from jorm.jarvis.db_update import JORMChanger
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.service import RequestInfo, UnitEconomyRequest, UnitEconomyResult

from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.person.user_items_service import UserItemsService
from jarvis_db.services.market.service.economy_service import EconomyService
from jarvis_db.services.market.service.frequency_service import FrequencyService


class JormChangerImpl(JORMChanger):
    def __init__(
        self,
        niche_service: NicheService,
        economy_service: EconomyService,
        frequency_service: FrequencyService,
        user_items_service: UserItemsService,
    ):
        self.__niche_service = niche_service
        self.__economy_service = economy_service
        self.__frequency_service = frequency_service
        self.__user_items_service = user_items_service

    def update_niche(
        self, niche_id: int, category_id: int, marketplace_id: int
    ) -> Niche:
        # TODO How?
        ...

    def save_unit_economy_request(
        self,
        request: UnitEconomyRequest,
        result: UnitEconomyResult,
        request_info: RequestInfo,
        user_id: int,
    ) -> int:
        return self.__economy_service.save_request(
            request_info, request, result, user_id
        )

    def delete_unit_economy_request(self, request_id: int, user_id: int):
        self.__economy_service.delete(request_id)

    def delete_frequency_request(self, request_id: int, user_id: int):
        self.__frequency_service.delete(request_id)

    def load_new_niche(self, niche_name: str, marketplace_id: int) -> Niche | None:
        # TODO How?
        ...

    def load_user_products(self, user_id: int, marketplace_id: int) -> list[Product]:
        return list(
            self.__user_items_service.fetch_user_products_atomic(
                user_id, marketplace_id
            ).values()
        )

    def load_user_warehouse(self, user_id: int, marketplace_id: int) -> list[Warehouse]:
        return list(
            self.__user_items_service.fetch_user_warehouses(
                user_id, marketplace_id
            ).values()
        )
