from jarvis_db.core import Mapper
from jorm.market.infrastructure import Warehouse
from jorm.market.infrastructure import HandlerType
from jorm.market.infrastructure import Address
from jarvis_db import tables


class WarehouseJormToTableMapper(Mapper[Warehouse, tables.Warehouse]):
    # TODO how to stote logistic_to_customer_commission
    def map(self, value: Warehouse) -> tables.Warehouse:
        return tables.Warehouse(
            global_id=value.global_id,
            name=value.name,
            logistic_to_customer_commission=value.basic_logistic_to_customer_commission,
            logistic_from_customer_commission=value.logistic_from_customer_commission,
            basic_storage_commission=value.basic_storage_commission,
            additional_storage_commission=int(
                value.additional_storage_commission * 100),
            monopalette_storage_commission=value.mono_palette_storage_commission,
            type=int(value.handler_type)
        )


class WarehouseTableToJormMapper(Mapper[tables.Warehouse, Warehouse]):
    def map(self, value: tables.Warehouse) -> Warehouse:
        return Warehouse(
            name=value.name,
            global_id=value.global_id,
            handler_type=HandlerType(value.type),
            address=Address(),
            basic_logistic_to_customer_commission=value.logistic_to_customer_commission,
            logistic_from_customer_commission=value.logistic_from_customer_commission,
            additional_storage_commission=value.additional_storage_commission,
            basic_storage_commission=value.basic_storage_commission,
            mono_palette_storage_commission=value.monopalette_storage_commission
        )
