from typing import Iterable

from jorm.market.items import ProductHistory, ProductHistoryUnit
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class ProductHistoryRepository:
    def __init__(
            self,
            session: Session,
            to_jorm_mapper: Mapper[tables.ProductHistory,
                                   ProductHistoryUnit],
            to_table_mapper: Mapper[ProductHistoryUnit,
                                    tables.ProductHistory]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add_product_history(self, history_unit: ProductHistoryUnit, product_id: int):
        db_history_unit = self.__to_table_mapper.map(history_unit)
        db_history_unit.product_id = product_id
        self.__session.add(db_history_unit)

    def add_all_product_histories(self, history_units: Iterable[ProductHistoryUnit], product_id: int):
        db_history_units = [self.__to_table_mapper.map(history_unit)
                            for history_unit in history_units]
        for db_history_unit in db_history_units:
            db_history_unit.product_id = product_id
        self.__session.add_all(db_history_units)

    def get_product_history(self, product_id: int) -> ProductHistory:
        db_history_units = self.__session.execute(
            select(tables.ProductHistory)
            .join(tables.ProductCard)
            .where(tables.ProductHistory.product_id == product_id)
        ).scalars().all()
        history_units = [self.__to_jorm_mapper.map(
            history_unit) for history_unit in db_history_units]
        return ProductHistory(history_units)
