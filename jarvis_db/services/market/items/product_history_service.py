from jorm.market.items import ProductHistory
from sqlalchemy.orm import Session

from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_history_unit_service import \
    ProductHistoryUnitService


class ProductHistoryService:
    def __init__(
            self,
            unit_service: ProductHistoryUnitService,
            leftover_service: LeftoverService
    ):
        self.__unit_servie = unit_service
        self.__leftover_service = leftover_service

    def add_product_history(self, product_history: ProductHistory, product_id: int):
        units = ((self.__unit_servie.create(unit, product_id), unit.leftover)
                 for unit in product_history.history)
        for unit, leftover in units:
            self.__leftover_service.create_leftovers(leftover, unit.id)
