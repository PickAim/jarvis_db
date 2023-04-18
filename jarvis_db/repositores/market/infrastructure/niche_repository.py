from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Category, Marketplace, Niche


class NicheRepository(AlchemyRepository[Niche]):

    def find_by_name(self, niche_name: str, category_id: int) -> Niche:
        return self._session.execute(
            select(Niche)
            .join(Niche.category)
            .where(Category.id == category_id)
            .where(Niche.name.ilike(niche_name))
        ).scalar_one()

    def find_niches_by_category(self, category_id: int) -> list[Niche]:
        db_niches = self._session.execute(
            select(Niche)
            .join(Niche.category)
            .where(Category.id == category_id)
        ).scalars().all()
        return list(db_niches)

    def find_by_marketplace(self, marketplace_id: int) -> list[Niche]:
        db_niches = self._session.execute(
            select(Niche)
            .join(Niche.category)
            .join(Category.marketplace)
            .where(Marketplace.id == marketplace_id)
        ).scalars().all()
        return list(db_niches)

    def exists_with_name(self, name: str, category_id: int) -> bool:
        return self._session.execute(
            select(Niche)
            .where(Niche.category_id == category_id)
            .where(Niche.name.ilike(name))
        ).scalar() is not None
