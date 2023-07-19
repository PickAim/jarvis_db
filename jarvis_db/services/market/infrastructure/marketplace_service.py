from typing import Iterable

from jorm.market.infrastructure import Marketplace as MarketplaceEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.tables import Marketplace


class MarketplaceService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[Marketplace, MarketplaceEntity],
    ):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(self, marketplace_entity: MarketplaceEntity):
        self.__session.add(
            MarketplaceService.__create_marketplace_record(marketplace_entity)
        )

    def create_all(self, marketplace_entities: Iterable[MarketplaceEntity]):
        self.__session.add_all(
            (
                MarketplaceService.__create_marketplace_record(marketplace)
                for marketplace in marketplace_entities
            )
        )

    def find_all(self) -> dict[int, MarketplaceEntity]:
        marketplaces = self.__session.execute(select(Marketplace)).scalars().all()
        return {
            marketplace.id: self.__table_mapper.map(marketplace)
            for marketplace in marketplaces
        }

    def fetch_all_atomic(self) -> dict[int, MarketplaceEntity]:
        marketplaces = (
            self.__session.execute(select(Marketplace).join(Marketplace.warehouses))
            .scalars()
            .all()
        )
        return {
            marketplace.id: self.__table_mapper.map(marketplace)
            for marketplace in marketplaces
        }

    def find_by_name(self, name: str) -> tuple[MarketplaceEntity, int] | None:
        marketplace = self.__session.execute(
            select(Marketplace).where(Marketplace.name.ilike(name))
        ).scalar_one_or_none()
        return (
            (self.__table_mapper.map(marketplace), marketplace.id)
            if marketplace is not None
            else None
        )

    def exists_with_name(self, name: str) -> bool:
        marketplace_id = self.__session.execute(
            select(Marketplace.id).where(Marketplace.name.ilike(name))
        ).scalar_one_or_none()
        return marketplace_id is not None

    @staticmethod
    def __create_marketplace_record(marketplace: MarketplaceEntity) -> Marketplace:
        return Marketplace(name=marketplace.name.lower())
