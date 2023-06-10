from jorm.market.items import ProductHistory
from jorm.market.items import ProductHistoryUnit

from jarvis_db import tables
from jarvis_db.core import Mapper
from jarvis_db.repositores.market.items import ProductHistoryRepository
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_history_unit_service import (
    ProductHistoryUnitService,
)


class ProductHistoryService:
    def __init__(
        self,
        unit_service: ProductHistoryUnitService,
        leftover_service: LeftoverService,
        product_history_repository: ProductHistoryRepository,
        table_mapper: Mapper[tables.ProductHistory, ProductHistoryUnit],
    ):
        self.__product_history_repository = product_history_repository
        self.__table_mapper = table_mapper
        self.__unit_servie = unit_service
        self.__leftover_service = leftover_service

    def create(self, product_history: ProductHistory, product_id: int):
        units = (
            (self.__unit_servie.create(unit, product_id), unit.leftover)
            for unit in product_history.get_history()
        )
        for unit, leftover in units:
            self.__leftover_service.create_leftovers(leftover, unit.id)

    def find_product_history(self, product_id: int) -> ProductHistory:
        units = self.__product_history_repository.find_product_histories(product_id)
        return ProductHistory([self.__table_mapper.map(unit) for unit in units])
