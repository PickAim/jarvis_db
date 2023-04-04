from typing import Iterable
from jorm.market.items import ProductHistoryUnit
from jorm.support.types import StorageDict

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class ProductHistoryJormToTableMapper(Mapper[ProductHistoryUnit, tables.ProductHistory]):
    def __init__(self, leftover_mapper: Mapper[StorageDict, Iterable[tables.Leftover]]):
        self.__leftover_mapper = leftover_mapper

    def map(self, value: ProductHistoryUnit) -> tables.ProductHistory:
        return tables.ProductHistory(
            cost=value.cost,
            date=value.unit_date,
            leftovers=self.__leftover_mapper.map(value.leftover)
        )


class ProductHistoryTableToJormMapper(Mapper[tables.ProductHistory, ProductHistoryUnit]):
    def __init__(self, leftover_mapper: Mapper[Iterable[tables.Leftover], StorageDict]):
        self.__leftover_mapper = leftover_mapper

    def map(self, value: tables.ProductHistory) -> ProductHistoryUnit:
        return ProductHistoryUnit(
            cost=value.cost,
            leftover=self.__leftover_mapper.map(value.leftovers),
            unit_date=value.date
        )
