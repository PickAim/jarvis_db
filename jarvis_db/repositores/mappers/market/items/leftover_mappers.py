from typing import Iterable

from jorm.market.items import StorageDict

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class LeftoverTableToJormMapper(Mapper[Iterable[tables.Leftover], StorageDict]):
    def map(self, value: Iterable[tables.Leftover]) -> StorageDict:
        result = {}
        for leftover in value:
            if leftover.warehouse.global_id not in result:
                result[leftover.warehouse.global_id] = {}
            result[leftover.warehouse.global_id][leftover.type] = leftover.quantity
        return StorageDict(result)


class LeftoverJormToTableMapper(Mapper[StorageDict, Iterable[tables.Leftover]]):
    def map(self, value: StorageDict) -> Iterable[tables.Leftover]:
        result = []
        for _, leftovers in value.items():
            for type, quantity in leftovers.items():
                result.append(tables.Leftover(type=type, quantity=quantity))
        return result
