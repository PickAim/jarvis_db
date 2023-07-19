from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.tables import Category, Niche


class NicheService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[Niche, NicheEntity],
    ):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(self, niche_entity: NicheEntity, category_id: int):
        self.__session.add(
            NicheService.__create_niche_record(niche_entity, category_id)
        )

    def create_all(self, niche_entities: Iterable[NicheEntity], category_id: int):
        self.__session.add_all(
            (
                NicheService.__create_niche_record(niche, category_id)
                for niche in niche_entities
            )
        )

    def fetch_by_id_with_products(self, niche_id: int) -> NicheEntity:
        niche = self.__session.execute(
            select(Niche).join(Niche.products).where(Niche.id == niche_id)
        ).scalar_one()
        return self.__table_mapper.map(niche)

    def find_by_name(
        self, name: str, category_id: int
    ) -> tuple[NicheEntity, int] | None:
        niche = self.__session.execute(
            select(Niche)
            .where(Niche.category_id == category_id)
            .where(Niche.name.ilike(name))
        ).scalar_one_or_none()
        return (self.__table_mapper.map(niche), niche.id) if niche is not None else None

    def find_all_in_category(self, category_id: int) -> dict[int, NicheEntity]:
        niches = (
            self.__session.execute(
                select(Niche).where(Niche.category_id == category_id)
            )
            .scalars()
            .all()
        )
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def fetch_all_in_category_atomic(self, category_id: int) -> dict[int, NicheEntity]:
        niches = (
            self.__session.execute(
                select(Niche)
                .join(Niche.products)
                .where(Niche.category_id == category_id)
            )
            .scalars()
            .all()
        )
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def find_all_in_marketplace(self, marketplace_id: int) -> dict[int, NicheEntity]:
        niches = (
            self.__session.execute(
                select(Niche)
                .join(Niche.category)
                .where(Category.marketplace_id == marketplace_id)
            )
            .scalars()
            .all()
        )
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def exists_with_name(self, name: str, category_id: int) -> bool:
        niche_id = self.__session.execute(
            select(Niche.id)
            .where(Niche.category_id == category_id)
            .where(Niche.name.ilike(name))
        ).scalar_one_or_none()
        return niche_id is not None

    def filter_existing_names(
        self, names: Iterable[str], category_id: int
    ) -> list[str]:
        names = list(names)
        existing_names = (
            self.__session.execute(
                select(Niche.name)
                .where(Niche.category_id == category_id)
                .where(Niche.name.in_(names))
            )
            .scalars()
            .all()
        )
        return list(set(names) - set(existing_names))

    @staticmethod
    def __create_niche_record(niche: NicheEntity, category_id: int) -> Niche:
        return Niche(
            name=niche.name,
            marketplace_commission=int(
                niche.commissions[HandlerType.MARKETPLACE] * 100
            ),
            partial_client_commission=int(
                niche.commissions[HandlerType.PARTIAL_CLIENT] * 100
            ),
            client_commission=int(niche.commissions[HandlerType.CLIENT] * 100),
            return_percent=int(niche.returned_percent * 100),
            category_id=category_id,
        )
