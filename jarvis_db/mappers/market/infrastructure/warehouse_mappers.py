from jorm.market.infrastructure import Address, HandlerType, Warehouse

from jarvis_db import schemas
from jarvis_db.core import Mapper


class WarehouseTableToJormMapper(Mapper[schemas.Warehouse, Warehouse]):
    __code_to_handler_type_dict = {
        0: HandlerType.MARKETPLACE,
        1: HandlerType.PARTIAL_CLIENT,
        2: HandlerType.CLIENT,
    }

    def map(self, value: schemas.Warehouse) -> Warehouse:
        return Warehouse(
            name=value.name,
            global_id=value.global_id,
            handler_type=WarehouseTableToJormMapper.__code_to_handler_type_dict.get(
                value.type, HandlerType.CLIENT
            ),
            address=Address(value.address.region, value.address.street),
            main_coefficient=float(value.main_coefficient / 100),
        )
