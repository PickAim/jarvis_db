from jorm.market.items import ProductHistoryUnit as ProductHistoryUnitEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.schemas import (
    Category,
    Leftover,
    Niche,
    ProductCard,
    ProductHistory,
)


class ProductHistoryUnitService:
    def __init__(self, session: Session):
        self.__session = session

    def create(
        self, history_unit: ProductHistoryUnitEntity, product_id: int
    ) -> ProductHistory:
        history = ProductHistory(
            cost=history_unit.cost,
            date=history_unit.unit_date,
            product_id=product_id,
        )
        self.__session.add(history)
        self.__session.flush()
        return history

    def find_by_id(self, product_history_id: int) -> ProductHistory:
        return (
            self.__session.execute(
                select(ProductHistory)
                .join(ProductHistory.product)
                .join(ProductCard.niche)
                .join(Niche.category)
                .join(Category.marketplace)
                .outerjoin(ProductHistory.leftovers)
                .outerjoin(Leftover.warehouse)
                .where(ProductHistory.id == product_history_id)
            )
            .unique()
            .scalar_one()
        )
