from abc import ABC, abstractmethod

from jorm.market.infrastructure import Niche, Warehouse
from jorm.server.providers.providers import (
    DataProviderWithoutKey,
    UserMarketDataProvider,
)

from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.items.product_card_service import ProductCardService


class StandardDbFiller(ABC):
    @abstractmethod
    def fill_categories(
        self,
        category_service: CategoryService,
        data_provider_without_key: DataProviderWithoutKey,
        category_num: int = -1,
    ) -> None:
        pass

    @abstractmethod
    def fill_niche_by_name(
        self,
        category_service: CategoryService,
        niche_service: NicheService,
        product_card_service: ProductCardService,
        data_provider_without_key: DataProviderWithoutKey,
        niche_name: str,
        product_num: int = -1,
    ) -> Niche | None:
        pass

    @abstractmethod
    def fill_niches(
        self,
        category_service: CategoryService,
        niche_service: NicheService,
        data_provider_without_key: DataProviderWithoutKey,
        niche_num: int = -1,
    ) -> None:
        pass

    @abstractmethod
    def fill_warehouse(
        self, provider_with_key: UserMarketDataProvider
    ) -> list[Warehouse]:
        pass
