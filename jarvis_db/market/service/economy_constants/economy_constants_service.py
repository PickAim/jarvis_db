from typing import TypedDict
from jorm.support.types import EconomyConstants as EconomyConstantsEntity
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from jarvis_db.core.mapper import Mapper

from jarvis_db.schemas import EconomyConstants


class _EconomyConstantsTypedDict(TypedDict):
    max_mass: int
    max_side_sum: int
    max_side_length: int
    max_standard_volume_in_liters: int
    return_price: int
    oversize_logistic_price: int
    oversize_storage_price: int
    standard_warehouse_logistic_price: int
    standard_warehouse_storage_price: int
    nds_tax: int
    commercial_tax: int
    self_employed_tax: int


class EconomyConstantsService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[EconomyConstants, EconomyConstantsEntity],
    ) -> None:
        self.__session = session
        self.__table_mapper = table_mapper

    def upsert_constants(
        self, marketplace_id: int, constants: EconomyConstantsEntity
    ) -> None:
        existing_constants = self.__session.execute(
            select(EconomyConstants).where(
                EconomyConstants.marketplace_id == marketplace_id
            )
        ).scalar_one_or_none()
        if existing_constants is None:
            self.__session.add(
                EconomyConstants(
                    marketplace_id=marketplace_id,
                    **EconomyConstantsService.__map_constants_entity_to_typed_dict(
                        constants
                    )
                )
            )
        else:
            self.__session.execute(
                update(EconomyConstants)
                .where(EconomyConstants.marketplace_id == marketplace_id)
                .values(
                    **EconomyConstantsService.__map_constants_entity_to_typed_dict(
                        constants
                    )
                )
            )
        self.__session.flush()

    def find_by_marketplace_id(
        self, marketplace_id: int
    ) -> EconomyConstantsEntity | None:
        constants = self.__session.execute(
            select(EconomyConstants).where(
                EconomyConstants.marketplace_id == marketplace_id
            )
        ).scalar_one_or_none()
        return self.__table_mapper.map(constants) if constants is not None else None

    @staticmethod
    def __map_constants_entity_to_typed_dict(
        constants: EconomyConstantsEntity,
    ) -> _EconomyConstantsTypedDict:
        return _EconomyConstantsTypedDict(
            max_mass=int(constants.max_mass * 100),
            max_side_sum=int(constants.max_side_sum * 100),
            max_side_length=int(constants.max_side_length * 100),
            max_standard_volume_in_liters=int(
                constants.max_standard_volume_in_liters * 100
            ),
            return_price=constants.return_price,
            oversize_logistic_price=constants.oversize_logistic_price,
            oversize_storage_price=constants.oversize_storage_price,
            standard_warehouse_logistic_price=constants.standard_warehouse_logistic_price,
            standard_warehouse_storage_price=constants.standard_warehouse_storage_price,
            nds_tax=int(constants.nds_tax * 100),
            commercial_tax=int(constants.commercial_tax * 100),
            self_employed_tax=int(constants.self_employed_tax * 100),
        )
