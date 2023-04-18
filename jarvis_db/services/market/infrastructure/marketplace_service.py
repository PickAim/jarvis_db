from typing import Iterable

from jorm.market.infrastructure import Marketplace as MarketplaceEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.infrastructure.marketplace_repository import \
    MarketplaceRepository
from jarvis_db.tables import Marketplace


class MarketplaceService:
    def __init__(
            self,
            marketplace_repository: MarketplaceRepository,
            table_mapper: Mapper[Marketplace, MarketplaceEntity]
    ):
        self.__marketplace_repository = marketplace_repository
        self.__table_mapper = table_mapper

    def create(self, entity: MarketplaceEntity):
        marketplace = Marketplace(name=entity.name)
        self.__marketplace_repository.add(marketplace)

    def create_all(self, entities: Iterable[MarketplaceEntity]):
        marketplaces = (Marketplace(name=entity.name) for entity in entities)
        self.__marketplace_repository.add_all(marketplaces)

    def find_all(self) -> dict[int, MarketplaceEntity]:
        marketplaces = self.__marketplace_repository.find_all()
        return {marketplace.id: self.__table_mapper.map(
            marketplace) for marketplace in marketplaces}

    def find_by_name(self, name: str) -> tuple[MarketplaceEntity, int]:
        marketplace = self.__marketplace_repository.find_by_name(name)
        return self.__table_mapper.map(marketplace), marketplace.id

    def exists_with_name(self, name: str) -> bool:
        return self.__marketplace_repository.exists_with_name(name)
