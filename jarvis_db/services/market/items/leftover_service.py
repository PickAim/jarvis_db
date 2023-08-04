from jorm.market.items import StorageDict

from jarvis_db.repositores.market.infrastructure.warehouse_repository import (
    WarehouseRepository,
)
from jarvis_db.repositores.market.items.leftover_repository import LeftoverRepository
from jarvis_db.schemas import Leftover
from jarvis_db.services.market.items.product_history_unit_service import (
    ProductHistoryUnitService,
)


class LeftoverService:
    def __init__(
        self,
        leftover_repository: LeftoverRepository,
        warehouse_repository: WarehouseRepository,
        product_history_service: ProductHistoryUnitService,
    ):
        self.__leftover_repository = leftover_repository
        self.__warehouse_repository = warehouse_repository
        self.__product_history_service = product_history_service

    def create_leftovers(self, leftover_create_request: StorageDict, history_id: int):
        marketplace_id = self.__product_history_service.find_by_id(
            history_id
        ).product.niche.category.marketplace_id
        warehouse_gid_map = {
            gid: warehouse.id
            for gid, warehouse in (
                (
                    gid,
                    self.__warehouse_repository.find_by_global_id(gid, marketplace_id),
                )
                for gid in leftover_create_request.keys()
            )
            if warehouse is not None
        }
        leftovers = []
        for gid, warehouse_leftovers in leftover_create_request.items():
            leftovers.extend(
                (
                    Leftover(
                        type=leftover.specify,
                        quantity=leftover.leftover,
                        product_history_id=history_id,
                        warehouse_id=warehouse_gid_map[gid],
                    )
                    for leftover in warehouse_leftovers
                )
            )
        self.__leftover_repository.add_all(leftovers)
