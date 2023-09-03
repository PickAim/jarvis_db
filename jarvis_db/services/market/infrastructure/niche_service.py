from typing import Iterable

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import Select, select, update
from sqlalchemy.orm import Session, noload

from jarvis_db.core.mapper import Mapper
from jarvis_db.queries.query_builder import QueryBuilder
from jarvis_db.schemas import Category, Niche


class NicheService:
    def __init__(
        self,
        session: Session,
        niche_query_builder: QueryBuilder[Niche],
        table_mapper: Mapper[Niche, NicheEntity],
    ):
        self.__session = session
        self.__niche_query_builder = niche_query_builder
        self.__table_mapper = table_mapper

    def create(self, niche_entity: NicheEntity, category_id: int):
        self.__session.add(
            NicheService.__create_niche_record(niche_entity, category_id)
        )
        self.__session.flush()

    def create_all(self, niche_entities: Iterable[NicheEntity], category_id: int):
        self.__session.add_all(
            (
                NicheService.__create_niche_record(niche, category_id)
                for niche in niche_entities
            )
        )
        self.__session.flush()

    def find_by_id(self, niche_id: int) -> NicheEntity | None:
        niche = self.__session.execute(
            select(Niche).where(Niche.id == niche_id).options(noload(Niche.products))
        ).scalar_one_or_none()
        return self.__table_mapper.map(niche) if niche is not None else None

    def fetch_by_id_atomic(self, niche_id: int) -> NicheEntity | None:
        niche = (
            self.__session.execute(
                self.__select_niche_atomic().where(Niche.id == niche_id)
            )
            .unique()
            .scalar_one_or_none()
        )
        return self.__table_mapper.map(niche) if niche is not None else None

    def find_by_name(
        self, name: str, category_id: int
    ) -> tuple[NicheEntity, int] | None:
        niche = self.__session.execute(
            select(Niche)
            .where(Niche.category_id == category_id)
            .where(Niche.name.ilike(name))
            .options(noload(Niche.products))
        ).scalar_one_or_none()
        return (self.__table_mapper.map(niche), niche.id) if niche is not None else None

    def find_by_name_atomic(
        self, name: str, category_id: int
    ) -> tuple[NicheEntity, int] | None:
        niche = (
            self.__session.execute(
                self.__select_niche_atomic()
                .where(Niche.category_id == category_id)
                .where(Niche.name.ilike(name))
            )
            .unique()
            .scalar_one_or_none()
        )
        return (self.__table_mapper.map(niche), niche.id) if niche is not None else None

    def find_all_in_category(self, category_id: int) -> dict[int, NicheEntity]:
        niches = (
            self.__session.execute(
                select(Niche)
                .where(Niche.category_id == category_id)
                .options(noload(Niche.products))
            )
            .scalars()
            .all()
        )
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def fetch_all_in_category_atomic(self, category_id: int) -> dict[int, NicheEntity]:
        niches = (
            self.__session.execute(
                self.__select_niche_atomic().where(Niche.category_id == category_id)
            )
            .unique()
            .scalars()
            .all()
        )
        return {niche.id: self.__table_mapper.map(niche) for niche in niches}

    def find_all_in_marketplace(self, marketplace_id: int) -> dict[int, NicheEntity]:
        niches = (
            self.__session.execute(
                select(Niche)
                .outerjoin(Niche.category)
                .where(Category.marketplace_id == marketplace_id)
                .distinct()
                .options(noload(Niche.products))
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

    def update(self, niche_id: int, niche: NicheEntity):
        self.__session.execute(
            update(Niche)
            .where(Niche.id == niche_id)
            .values(
                name=niche.name,
                marketplace_commission=int(
                    niche.commissions[HandlerType.MARKETPLACE] * 100
                ),
                partial_client_commission=int(
                    niche.commissions[HandlerType.PARTIAL_CLIENT] * 100
                ),
                client_commission=int(niche.commissions[HandlerType.CLIENT] * 100),
                return_percent=int(niche.returned_percent * 100),
            )
        )
        self.__session.flush()

    def __select_niche_atomic(self) -> Select[tuple[Niche]]:
        return (
            self.__niche_query_builder.join(select(Niche).join(Niche.category))
            .options(
                *self.__niche_query_builder.provide_load_options(),
            )
            .distinct()
        )

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
