from jorm.market.service import (
    SimpleEconomyRequest,
    SimpleEconomyResult,
    SimpleEconomySaveObject,
)
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import EconomyRequest, EconomyResult, Niche, UserToEconomy
from jarvis_db.market.infrastructure.warehouse.warehouse_service import WarehouseService


class EconomyService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[
            UserToEconomy,
            SimpleEconomySaveObject,
        ],
        warehouse_service: WarehouseService,
    ):
        self.__session = session
        self.__table_mapper = table_mapper
        self.__warehouse_service = warehouse_service

    def save_request(
        self,
        save_object: SimpleEconomySaveObject,
        user_id: int,
    ) -> int:
        user_tuple = self.__create_economy_tuple(
            save_object.user_result[0],
            save_object.user_result[1],
        )
        recommended_tuple = self.__create_economy_tuple(
            save_object.recommended_result[0],
            save_object.recommended_result[1],
        )
        user_to_economy = UserToEconomy(
            user_id=user_id,
            name=save_object.info.name,
            date=save_object.info.date,
            economy_request=user_tuple[0],
            economy_result=user_tuple[1],
            recommended_economy_request=recommended_tuple[0],
            recommended_economy_result=recommended_tuple[1],
        )
        self.__session.add(user_to_economy)
        self.__session.flush()
        return user_to_economy.id

    def find_user_requests(self, user_id: int) -> list[SimpleEconomySaveObject]:
        economy_request_options = [
            joinedload(EconomyRequest.niche).joinedload(Niche.category)
        ]
        results = (
            self.__session.execute(
                select(UserToEconomy)
                .where(UserToEconomy.user_id == user_id)
                .options(
                    joinedload(UserToEconomy.economy_request).options(
                        *economy_request_options,
                    ),
                    joinedload(UserToEconomy.economy_result),
                    joinedload(UserToEconomy.recommended_economy_request).options(
                        *economy_request_options,
                    ),
                    joinedload(UserToEconomy.recommended_economy_result),
                )
            )
            .scalars()
            .unique()
            .all()
        )
        return [self.__table_mapper.map(result) for result in results]

    def delete(self, request_id: int) -> bool:
        economy_record = self.__session.execute(
            select(UserToEconomy).where(UserToEconomy.id == request_id)
        ).scalar_one_or_none()
        if economy_record is None:
            return False
        try:
            with self.__session.begin_nested():
                self.__session.delete(economy_record)
                self.__session.flush()
                self.__session.execute(
                    delete(EconomyRequest).where(
                        EconomyRequest.id.in_(
                            [
                                economy_record.economy_request_id,
                                economy_record.recommended_economy_request_id,
                            ]
                        )
                    )
                )
                self.__session.execute(
                    delete(EconomyResult).where(
                        EconomyResult.id.in_(
                            [
                                economy_record.economy_result_id,
                                economy_record.recommended_economy_result_id,
                            ]
                        )
                    )
                )
                self.__session.flush()
        except SQLAlchemyError:
            return False
        return True

    @staticmethod
    def __map_request_to_record(
        warehouse_id: int,
        request: SimpleEconomyRequest,
    ) -> EconomyRequest:
        return EconomyRequest(
            niche_id=request.niche_id,
            product_exit_cost=request.product_exist_cost,
            warehouse_id=warehouse_id,
            cost_price=request.cost_price,
            length=int(request.length * 100),
            width=int(request.width * 100),
            height=int(request.height * 100),
            mass=int(request.mass * 100),
        )

    @staticmethod
    def __map_result_to_record(result: SimpleEconomyResult) -> EconomyResult:
        return EconomyResult(
            result_cost=result.result_cost,
            logistic_price=result.logistic_price,
            purchase_cost=result.purchase_cost,
            marketplace_expanses=result.marketplace_expanses,
            absolute_margin=result.absolute_margin,
            relative_margin=int(result.relative_margin * 100),
            roi=int(result.roi * 100),
            storage_price=result.storage_price,
        )

    def __create_economy_tuple(
        self,
        request: SimpleEconomyRequest,
        result: SimpleEconomyResult,
    ) -> tuple[EconomyRequest, EconomyResult]:
        warehouse = self.__warehouse_service.find_by_id(request.target_warehouse_id)
        if warehouse is None:
            raise Exception(
                f"No warehouse with id '{request.target_warehouse_id}' was found"
            )
        request_record = EconomyService.__map_request_to_record(
            request.target_warehouse_id, request
        )
        result_record = EconomyService.__map_result_to_record(result)
        return request_record, result_record
