from typing import Iterable

from jorm.market.items import StorageDict
from jorm.support.types import SpecifiedLeftover

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class LeftoverTableToJormMapper(Mapper[Iterable[tables.Leftover], StorageDict]):
    def map(self, value: Iterable[tables.Leftover]) -> StorageDict:
        result: dict[int, list[SpecifiedLeftover]] = {}
        for leftover in value:
            if leftover.warehouse.global_id not in result:
                result[leftover.warehouse.global_id] = []
            result[leftover.warehouse.global_id].append(
                SpecifiedLeftover(leftover.type, leftover.quantity))
        return StorageDict(result)


class LeftoverJormToTableMapper(Mapper[StorageDict, Iterable[tables.Leftover]]):
    def map(self, value: StorageDict) -> Iterable[tables.Leftover]:
        result = []
        for _, leftovers in value.items():
            for leftover in leftovers:
                result.append(tables.Leftover(
                    type=leftover.specify, quantity=leftover.leftover))
        return result
