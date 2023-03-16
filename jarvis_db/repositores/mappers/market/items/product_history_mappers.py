from jorm.market.items import ProductHistoryUnit
from jorm.support.types import StorageDict

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class ProductHistoryJormToTableMapper(Mapper[ProductHistoryUnit, tables.ProductHistory]):
    def map(self, value: ProductHistoryUnit) -> tables.ProductHistory:
        return tables.ProductHistory(
            cost=value.cost,
            date=value.unit_date,
            leftover=value.leftover.get_all_leftovers()
        )


class ProductHistoryTableToJormMapper(Mapper[tables.ProductHistory, ProductHistoryUnit]):
    def map(self, value: tables.ProductHistory) -> ProductHistoryUnit:
        return ProductHistoryUnit(
            cost=value.cost,
            leftover=StorageDict(),
            unit_date=value.date
        )
