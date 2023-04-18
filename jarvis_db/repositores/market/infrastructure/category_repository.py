from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Category, Marketplace


class CategoryRepository(AlchemyRepository[Category]):

    def find_by_name(self, name: str, marketplace_id: int) -> Category:
        return self._session.execute(
            select(Category)
            .join(Category.marketplace)
            .where(Marketplace.id == marketplace_id)
            .where(Category.name.ilike(name))
        ).scalar_one()

    def find_all_in_marketplace(self, marketplace_id: int) -> list[Category]:
        categories = self._session.execute(
            select(Category)
            .join(Category.marketplace)
            .where(Marketplace.id == marketplace_id)
        ).scalars().all()
        return list(categories)

    def exists_with_name(self, name: str, marketplace_id: int) -> bool:
        return self._session.execute(
            select(Category)
            .where(Category.marketplace_id == marketplace_id)
            .where(Category.name.ilike(name))
        ).scalar() is not None
