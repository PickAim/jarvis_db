from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.schemas import Category, Marketplace, Niche


class NicheRepository(AlchemyRepository[Niche]):
    def fetch_full_by_id(self, niche_id: int) -> Niche:
        return self._session.execute(
            select(Niche)
            .join(Niche.category)
            .join(Niche.products)
            .where(Niche.id == niche_id)
        ).scalar_one()

    def find_by_name(self, niche_name: str, category_id: int) -> Niche | None:
        return self._session.execute(
            select(Niche)
            .join(Niche.category)
            .where(Category.id == category_id)
            .where(Niche.name.ilike(niche_name))
        ).scalar()

    def find_by_niche_name_and_category_name(
        self, niche_name: str, category_name: str, marketplace_id: int
    ) -> Niche | None:
        return self._session.execute(
            select(Niche)
            .join(Niche.category)
            .where(Category.marketplace_id == marketplace_id)
            .where(Category.name.ilike(category_name))
            .where(Niche.name.ilike(niche_name))
        ).scalar_one_or_none()

    def find_niches_by_category(self, category_id: int) -> list[Niche]:
        db_niches = (
            self._session.execute(
                select(Niche).join(Niche.category).where(Category.id == category_id)
            )
            .scalars()
            .all()
        )
        return list(db_niches)

    def find_by_marketplace(self, marketplace_id: int) -> list[Niche]:
        db_niches = (
            self._session.execute(
                select(Niche)
                .join(Niche.category)
                .join(Category.marketplace)
                .where(Marketplace.id == marketplace_id)
            )
            .scalars()
            .all()
        )
        return list(db_niches)

    def exists_with_name(self, name: str, category_id: int) -> bool:
        return (
            self._session.execute(
                select(Niche)
                .where(Niche.category_id == category_id)
                .where(Niche.name.ilike(name))
            ).scalar()
            is not None
        )

    def filter_existing_names(self, names: list[str], category_id: int) -> list[str]:
        existing_names = (
            self._session.execute(
                select(Niche.name)
                .where(Niche.category_id == category_id)
                .where(Niche.name.in_(names))
            )
            .scalars()
            .all()
        )
        return list(set(names) - set(existing_names))
