from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Category, Niche, ProductCard, ProductHistory


class ProductHistoryRepository(AlchemyRepository[ProductHistory]):
    def find_by_id(self, id: int) -> ProductHistory:
        return self._session.execute(
            select(ProductHistory)
            .join(ProductHistory.product)
            .join(ProductCard.niche)
            .join(Niche.category)
            .join(Category.marketplace)
            .where(ProductHistory.id == id)
        ).scalar_one()

    def find_product_histories(self, product_id: int) -> list[ProductHistory]:
        db_history_units = self._session.execute(
            select(ProductHistory)
            .outerjoin(ProductHistory.leftovers)
            .where(ProductHistory.product_id == product_id)
            .distinct()
        ).scalars().all()
        return list(db_history_units)
