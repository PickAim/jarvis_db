from itertools import groupby
from typing import Iterable

from jorm.market.items import StorageDict
from jorm.support.types import SpecifiedLeftover

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import Leftover


class LeftoverTableToJormMapper(Mapper[Iterable[Leftover], StorageDict]):
    def map(self, value: Iterable[Leftover]) -> StorageDict:
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


class LeftoverJormToTableMapper(Mapper[StorageDict, Iterable[Leftover]]):
    def map(self, value: StorageDict) -> Iterable[Leftover]:
        return [
            Leftover(type=leftover.specify, quantity=leftover.leftover)
            for _, leftovers in value.items()
            for leftover in leftovers
        ]
