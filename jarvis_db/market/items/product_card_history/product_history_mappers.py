from typing import Iterable

from jorm.market.items import ProductHistoryUnit
from jorm.support.types import StorageDict

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper


class ProductHistoryJormToTableMapper(
    Mapper[ProductHistoryUnit, schemas.ProductHistory]
):
    def __init__(
        self, leftover_mapper: Mapper[StorageDict, Iterable[schemas.Leftover]]
    ):
        self.__leftover_mapper = leftover_mapper

    def map(self, value: ProductHistoryUnit) -> schemas.ProductHistory:
        return schemas.ProductHistory(
            cost=value.cost,
            date=value.unit_date,
            leftovers=self.__leftover_mapper.map(value.leftover),
        )


class ProductHistoryUnitTableToJormMapper(
    Mapper[schemas.ProductHistory, ProductHistoryUnit]
):
    def __init__(
        self, leftover_mapper: Mapper[Iterable[schemas.Leftover], StorageDict]
    ):
        self.__leftover_mapper = leftover_mapper

    def map(self, value: schemas.ProductHistory) -> ProductHistoryUnit:
        return ProductHistoryUnit(
            cost=value.cost,
            leftover=self.__leftover_mapper.map(value.leftovers),
            unit_date=value.date,
        )
