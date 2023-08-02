from typing import Iterable

from jorm.market.items import StorageDict
from jorm.support.types import SpecifiedLeftover

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper


class LeftoverTableToJormMapper(Mapper[Iterable[schemas.Leftover], StorageDict]):
    def map(self, value: Iterable[schemas.Leftover]) -> StorageDict:
        result: dict[int, list[SpecifiedLeftover]] = {}
        for leftover in value:
            if leftover.warehouse.global_id not in result:
                result[leftover.warehouse.global_id] = []
            result[leftover.warehouse.global_id].append(
                SpecifiedLeftover(leftover.type, leftover.quantity)
            )
        return StorageDict(result)


class LeftoverJormToTableMapper(Mapper[StorageDict, Iterable[schemas.Leftover]]):
    def map(self, value: StorageDict) -> Iterable[schemas.Leftover]:
        result = []
        for _, leftovers in value.items():
            for leftover in leftovers:
                result.append(
                    schemas.Leftover(type=leftover.specify, quantity=leftover.leftover)
                )
        return result
