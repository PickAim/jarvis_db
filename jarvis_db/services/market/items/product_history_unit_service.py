from jorm.market.items import ProductHistoryUnit

from jarvis_db import tables
from jarvis_db.repositores.market.items.product_history_repository import \
    ProductHistoryRepository


class ProductHistoryUnitService:
    def __init__(
            self,
            product_history_repository: ProductHistoryRepository,
    ):
        self.__product_history_repository = product_history_repository

    def create(self, history_unit: ProductHistoryUnit, product_id: int) -> tables.ProductHistory:
        return self.__product_history_repository.save(tables.ProductHistory(
            cost=history_unit.cost,
            date=history_unit.unit_date,
            product_id=product_id)
        )

    def find_by_id(self, product_history_id: int) -> tables.ProductHistory:
        return self.__product_history_repository.find_by_id(product_history_id)
