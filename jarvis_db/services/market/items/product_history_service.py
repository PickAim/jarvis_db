from jorm.market.items import ProductHistory as ProductHistoryDomain, ProductHistoryUnit
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.core import Mapper
from jarvis_db.schemas import Leftover, ProductHistory
from jarvis_db.services.market.items.leftover_service import LeftoverService
from jarvis_db.services.market.items.product_history_unit_service import (
    ProductHistoryUnitService,
)


class ProductHistoryService:
    def __init__(
        self,
        session: Session,
        unit_service: ProductHistoryUnitService,
        leftover_service: LeftoverService,
        table_mapper: Mapper[ProductHistory, ProductHistoryUnit],
    ):
        self.__session = session
        self.__table_mapper = table_mapper
        self.__unit_servie = unit_service
        self.__leftover_service = leftover_service

    def create(self, product_history: ProductHistoryDomain, product_id: int):
        units = (
            (self.__unit_servie.create(unit, product_id), unit.leftover)
            for unit in product_history.get_history()
        )
        for unit, leftover in units:
            self.__leftover_service.create_leftovers(leftover, unit.id)

    def find_product_history(self, product_id: int) -> ProductHistoryDomain:
        units = (
            self.__session.execute(
                select(ProductHistory, ProductHistory.leftovers)
                .outerjoin(ProductHistory.leftovers)
                .join(Leftover.warehouse)
                .where(ProductHistory.product_id == product_id)
                .distinct()
            )
            .scalars()
            .all()
        )
        return ProductHistoryDomain((self.__table_mapper.map(unit) for unit in units))
