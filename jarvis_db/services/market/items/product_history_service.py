from jorm.market.items import ProductHistory as ProductHistoryDomain, ProductHistoryUnit
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from jarvis_db.core import Mapper
from jarvis_db.schemas import (
    Category,
    Leftover,
    Marketplace,
    Niche,
    ProductCard,
    ProductHistory,
    Warehouse,
)


class ProductHistoryService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[ProductHistory, ProductHistoryUnit],
    ):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(self, product_history: ProductHistoryDomain, product_id: int):
        self.__session.add_all(
            (
                ProductHistory(
                    cost=history.cost,
                    date=history.unit_date,
                    product_id=product_id,
                    leftovers=[
                        Leftover(
                            type=leftover.specify,
                            quantity=leftover.leftover,
                            warehouse_id=(
                                select(Warehouse.id)
                                .join(Warehouse.marketplace)
                                .join(Marketplace.categories)
                                .join(Category.niches)
                                .join(Niche.products)
                                .where(ProductCard.id == product_id)
                                .where(Warehouse.global_id == gid)
                                .scalar_subquery()
                            ),
                        )
                        for gid, leftovers in history.leftover.items()
                        for leftover in leftovers
                    ],
                )
                for history in product_history.get_history()
            )
        )

    def find_product_history(self, product_id: int) -> ProductHistoryDomain:
        units = (
            self.__session.execute(
                select(ProductHistory)
                .options(
                    joinedload(ProductHistory.leftovers).joinedload(Leftover.warehouse)
                )
                .where(ProductHistory.product_id == product_id)
            )
            .scalars()
            .unique()
            .all()
        )
        return ProductHistoryDomain((self.__table_mapper.map(unit) for unit in units))
