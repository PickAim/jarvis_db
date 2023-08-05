from jorm.market.infrastructure import Address, HandlerType, Warehouse

from jarvis_db import schemas
from jarvis_db.core import Mapper


class WarehouseJormToTableMapper(Mapper[Warehouse, schemas.Warehouse]):
    def map(self, value: Warehouse) -> schemas.Warehouse:
        return schemas.Warehouse(
            global_id=value.global_id,
            name=value.name,
            basic_logistic_to_customer_commission=value.basic_logistic_to_customer_commission,
            additional_logistic_to_customer_commission=value.additional_logistic_to_customer_commission,
            logistic_from_customer_commission=value.logistic_from_customer_commission,
            basic_storage_commission=value.basic_storage_commission,
            additional_storage_commission=int(
                value.additional_storage_commission * 100
            ),
            monopalette_storage_commission=value.mono_palette_storage_commission,
            type=value.handler_type.value,
            address=schemas.Address(
                country="", region="", street="", number="", corpus=""
            ),
        )


class WarehouseTableToJormMapper(Mapper[schemas.Warehouse, Warehouse]):
    def map(self, value: schemas.Warehouse) -> Warehouse:
        handler_type = HandlerType.CLIENT
        match value.type:
            case 0:
                handler_type = HandlerType.MARKETPLACE
            case 1:
                handler_type = HandlerType.PARTIAL_CLIENT
        return Warehouse(
            name=value.name,
            global_id=value.global_id,
            handler_type=handler_type,
            address=Address(),
            basic_logistic_to_customer_commission=value.basic_logistic_to_customer_commission,
            additional_logistic_to_customer_commission=value.additional_logistic_to_customer_commission,
            logistic_from_customer_commission=value.logistic_from_customer_commission,
            basic_storage_commission=value.basic_storage_commission,
            additional_storage_commission=value.additional_storage_commission,
            mono_palette_storage_commission=value.monopalette_storage_commission,
        )
