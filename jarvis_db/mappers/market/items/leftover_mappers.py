from itertools import groupby
from typing import Iterable

from jorm.market.items import StorageDict
from jorm.support.types import SpecifiedLeftover
from operator import attrgetter

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import Leftover


class LeftoverTableToJormMapper(Mapper[Iterable[Leftover], StorageDict]):
    def __init__(self):
        self.__warehouse_global_id_getter: attrgetter[int] = attrgetter(
            "warehouse.global_id"
        )

    def map(self, value: Iterable[Leftover]) -> StorageDict:
        return StorageDict(
            {
                gid: [
                    SpecifiedLeftover(leftover.type, leftover.quantity)
                    for leftover in leftovers
                ]
                for gid, leftovers in groupby(
                    sorted(value, key=self.__warehouse_global_id_getter),
                    key=self.__warehouse_global_id_getter,
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
