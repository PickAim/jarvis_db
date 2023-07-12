from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.infrastructure.niche_repository import NicheRepository
from jarvis_db.tables import Niche


class NicheService:
    def __init__(
        self,
        niche_repository: NicheRepository,
        table_mapper: Mapper[Niche, NicheEntity],
    ):
        self.__niche_repository = niche_repository
        self.__table_mapper = table_mapper

    def create(self, niche_entity: NicheEntity, category_id: int):
        niche = Niche(
            name=niche_entity.name,
            marketplace_commission=int(
                niche_entity.commissions[HandlerType.MARKETPLACE] * 100
            ),
            partial_client_commission=int(
                niche_entity.commissions[HandlerType.PARTIAL_CLIENT] * 100
            ),
            client_commission=int(niche_entity.commissions[HandlerType.CLIENT] * 100),
            return_percent=int(niche_entity.returned_percent * 100),
            category_id=category_id,
        )
        self.__niche_repository.add(niche)

    def create_all(self, niche_entities: Iterable[NicheEntity], category_id: int):
        for niche in niche_entities:
            self.create(niche, category_id)

    def fetch_by_id_with_products(self, niche_id: int) -> NicheEntity:
        return self.__table_mapper.map(
            self.__niche_repository.fetch_full_by_id(niche_id)
        )

    def find_by_name(
        self, name: str, category_id: int
    ) -> tuple[NicheEntity, int] | None:
        niche = self.__niche_repository.find_by_name(name, category_id)
        if niche is None:
            return None
        return self.__table_mapper.map(niche), niche.id

    def find_all_in_category(self, category_id: int) -> dict[int, NicheEntity]:
        niches = self.__niche_repository.find_niches_by_category(category_id)
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def find_all_in_marketplace(self, marketplace_id: int) -> dict[int, NicheEntity]:
        niches = self.__niche_repository.find_by_marketplace(marketplace_id)
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def exists_with_name(self, name: str, category_id: int) -> bool:
        return self.__niche_repository.exists_with_name(name, category_id)

    def filter_existing_names(
        self, names: Iterable[str], category_id: int
    ) -> list[str]:
        return self.__niche_repository.filter_existing_names(list(names), category_id)
