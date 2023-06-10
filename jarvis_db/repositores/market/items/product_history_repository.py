from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import (
    Category,
    Leftover,
    Niche,
    ProductCard,
    ProductHistory,
    Warehouse,
)


class ProductHistoryRepository(AlchemyRepository[ProductHistory]):
    def find_by_id(self, product_history_id: int) -> ProductHistory:
        return self._session.execute(
            select(ProductHistory)
            .join(ProductHistory.product)
            .join(ProductCard.niche)
            .join(Niche.category)
            .join(Category.marketplace)
            .outerjoin(ProductHistory.leftovers)
            .outerjoin(Warehouse, Leftover.warehouse_id == Warehouse.id)
            .where(ProductHistory.id == product_history_id)
        ).scalar_one()

    def find_product_histories(self, product_id: int) -> list[ProductHistory]:
        db_history_units = (
            self._session.execute(
                select(ProductHistory)
                .join(ProductHistory.product)
                .join(ProductCard.niche)
                .join(Niche.category)
                .join(Category.marketplace)
                .outerjoin(ProductHistory.leftovers)
                .outerjoin(Warehouse, Leftover.warehouse_id == Warehouse.id)
                .where(ProductHistory.product_id == product_id)
                .distinct()
            )
            .scalars()
            .all()
        )
        return list(db_history_units)
