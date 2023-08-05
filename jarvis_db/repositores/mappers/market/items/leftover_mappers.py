from itertools import groupby
from typing import Iterable

from jorm.market.items import StorageDict
from jorm.support.types import SpecifiedLeftover

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper


class LeftoverTableToJormMapper(Mapper[Iterable[schemas.Leftover], StorageDict]):
    def map(self, value: Iterable[schemas.Leftover]) -> StorageDict:
        return StorageDict(
            {
                gid: [
                    SpecifiedLeftover(leftover.type, leftover.quantity)
                    for leftover in leftovers
                ]
                for gid, leftovers in groupby(
                    value, key=lambda leftover: leftover.warehouse.global_id
                )
            }
        )


class LeftoverJormToTableMapper(Mapper[StorageDict, Iterable[schemas.Leftover]]):
    def map(self, value: StorageDict) -> Iterable[schemas.Leftover]:
        result = []
        for _, leftovers in value.items():
            for leftover in leftovers:
                result.append(
                    schemas.Leftover(type=leftover.specify, quantity=leftover.leftover)
                )
        return result
