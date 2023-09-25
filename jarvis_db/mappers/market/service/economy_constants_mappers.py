from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import EconomyConstants
from jorm.support.types import (
    EconomyConstants as EconomyConstantsEntity,
)


class EconomyConstantsTableToJormMapper(
    Mapper[EconomyConstants, EconomyConstantsEntity]
):
    def map(self, value: EconomyConstants) -> EconomyConstantsEntity:
        return EconomyConstantsEntity(
            max_mass=float(value.max_mass / 100),
            max_side_sum=float(value.max_side_sum / 100),
            max_side_length=float(value.max_side_length / 100),
            max_standard_volume_in_liters=float(
                value.max_standard_volume_in_liters / 100
            ),
            return_price=value.return_price,
            oversize_logistic_price=value.oversize_logistic_price,
            oversize_storage_price=value.oversize_storage_price,
            standard_warehouse_logistic_price=value.standard_warehouse_logistic_price,
            standard_warehouse_storage_price=value.standard_warehouse_storage_price,
            nds_tax=float(value.nds_tax / 100),
            commercial_tax=float(value.commercial_tax / 100),
            self_employed_tax=float(value.self_employed_tax / 100),
        )
