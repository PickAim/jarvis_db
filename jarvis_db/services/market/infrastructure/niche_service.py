from dataclasses import dataclass, field
from typing import Iterable, TypedDict

from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Niche as NicheEntity
from sqlalchemy import select, update
from sqlalchemy.orm import Session, noload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import Category, Niche
from sqlalchemy.sql.base import ExecutableOption


class _NicheTypedDict(TypedDict):
    name: str
    marketplace_commission: int
    partial_client_commission: int
    client_commission: int
    return_percent: int


@dataclass(frozen=True)
class NicheLoadOptions:
    atomic_options: list[ExecutableOption] = field(default_factory=list)
    no_history_options: list[ExecutableOption] = field(default_factory=list)


class NicheService:
    def __init__(
        self,
        session: Session,
        niche_load_options: NicheLoadOptions,
        table_mapper: Mapper[Niche, NicheEntity],
    ):
        self.__session = session
        self.__niche_load_options = niche_load_options
        self.__table_mapper = table_mapper

    def create(self, niche: NicheEntity, category_id: int):
        self.__session.add(
            Niche(
                category_id=category_id,
                **NicheService.__map_niche_entity_to_dict(niche),
            )
        )
        self.__session.flush()

    def create_all(self, niche_entities: Iterable[NicheEntity], category_id: int):
        self.__session.add_all(
            (
                Niche(
                    category_id=category_id,
                    **NicheService.__map_niche_entity_to_dict(niche),
                )
                for niche in niche_entities
            )
        )
        self.__session.flush()

    def find_by_id(self, niche_id: int) -> NicheEntity | None:
        niche = self.__session.execute(
            select(Niche).where(Niche.id == niche_id).options(noload(Niche.products))
        ).scalar_one_or_none()
        return self.__table_mapper.map(niche) if niche is not None else None

    def find_by_id_without_histories(self, niche_id: int) -> NicheEntity | None:
        niche = (
            self.__session.execute(
                select(Niche)
                .where(Niche.id == niche_id)
                .options(*self.__niche_load_options.no_history_options)
            )
            .unique()
            .scalar_one_or_none()
        )
        return self.__table_mapper.map(niche) if niche is not None else None

    def fetch_by_id_atomic(self, niche_id: int) -> NicheEntity | None:
        niche = (
            self.__session.execute(
                select(Niche)
                .where(Niche.id == niche_id)
                .options(*self.__niche_load_options.atomic_options)
                .distinct(Niche.id)
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
                select(Niche)
                .where(Niche.category_id == category_id)
                .where(Niche.name.ilike(name))
                .options(*self.__niche_load_options.atomic_options)
                .distinct(Niche.id)
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
                select(Niche)
                .where(Niche.category_id == category_id)
                .options(*self.__niche_load_options.atomic_options)
                .distinct(Niche.id)
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
            .values(**NicheService.__map_niche_entity_to_dict(niche))
        )
        self.__session.flush()

    @staticmethod
    def __map_niche_entity_to_dict(niche: NicheEntity) -> _NicheTypedDict:
        return _NicheTypedDict(
            name=niche.name,
            marketplace_commission=int(
                niche.commissions.get(HandlerType.MARKETPLACE, 0) * 100
            ),
            partial_client_commission=int(
                niche.commissions.get(HandlerType.PARTIAL_CLIENT, 0) * 100
            ),
            client_commission=int(niche.commissions.get(HandlerType.CLIENT, 0) * 100),
            return_percent=int(niche.returned_percent * 100),
        )
