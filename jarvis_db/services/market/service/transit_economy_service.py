from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload
from jorm.market.service import (
    TransitEconomySaveObject,
    TransitEconomyRequest as TransitEconomyRequestEntity,
    TransitEconomyResult as TransitEconomyResultEntity,
)

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import (
    Niche,
    TransitEconomyRequest,
    TransitEconomyResult,
    UserToTransitEconomy,
)
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService


class TransitEconomyService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[UserToTransitEconomy, TransitEconomySaveObject],
        warehouse_service: WarehouseService,
    ):
        self.__session = session
        self.__table_mapper = table_mapper
        self.__warehouse_service = warehouse_service

    def create(self, save_object: TransitEconomySaveObject, user_id: int) -> int:
        user_tuple = self.__create_transit_tuple(
            save_object.user_result[0],
            save_object.user_result[1],
        )
        recommended_tuple = self.__create_transit_tuple(
            save_object.recommended_result[0],
            save_object.recommended_result[1],
        )
        user_to_transit = UserToTransitEconomy(
            user_id=user_id,
            name=save_object.info.name,
            date=save_object.info.date,
            transit_request=user_tuple[0],
            transit_result=user_tuple[1],
            recommended_transit_request=recommended_tuple[0],
            recommended_transit_result=recommended_tuple[1],
        )
        self.__session.add(user_to_transit)
        self.__session.flush()
        return user_to_transit.id

    def find_user_requests(self, user_id: int) -> list[TransitEconomySaveObject]:
        transit_request_options = [
            joinedload(TransitEconomyRequest.warehouse),
            joinedload(TransitEconomyRequest.niche).joinedload(Niche.category),
        ]
        results = (
            self.__session.execute(
                select(UserToTransitEconomy)
                .where(UserToTransitEconomy.user_id == user_id)
                .options(
                    joinedload(UserToTransitEconomy.transit_request).options(
                        *transit_request_options
                    ),
                    joinedload(UserToTransitEconomy.transit_result),
                    joinedload(
                        UserToTransitEconomy.recommended_transit_request
                    ).options(*transit_request_options),
                    joinedload(UserToTransitEconomy.recommended_transit_result),
                )
            )
            .unique()
            .scalars()
            .all()
        )
        return [self.__table_mapper.map(result) for result in results]

    def delete(self, request_id: int) -> bool:
        user_to_transit = self.__session.execute(
            select(UserToTransitEconomy).where(UserToTransitEconomy.id == request_id)
        ).scalar_one_or_none()
        if user_to_transit is None:
            return False
        self.__session.execute(
            delete(TransitEconomyResult).where(
                TransitEconomyResult.id.in_(
                    [
                        user_to_transit.transit_result_id,
                        user_to_transit.recommended_transit_result_id,
                    ]
                )
            )
        )
        self.__session.execute(
            delete(TransitEconomyRequest).where(
                TransitEconomyRequest.id.in_(
                    [
                        user_to_transit.transit_request_id,
                        user_to_transit.recommended_transit_request_id,
                    ]
                )
            )
        )
        self.__session.delete(user_to_transit)
        self.__session.flush()
        return True

    @staticmethod
    def __map_request_to_record(
        request: TransitEconomyRequestEntity, warehouse_id: int
    ) -> TransitEconomyRequest:
        return TransitEconomyRequest(
            niche_id=request.niche_id,
            product_exit_cost=request.product_exist_cost,
            warehouse_id=warehouse_id,
            cost_price=request.cost_price,
            lenght=request.length,
            width=request.width,
            height=request.height,
            mass=request.mass,
            transit_cost=request.transit_price,
            transit_count=request.transit_count,
        )

    @staticmethod
    def __map_result_to_record(result: TransitEconomyResultEntity):
        return TransitEconomyResult(
            result_cost=result.result_cost,
            logistic_price=result.logistic_price,
            purchase_cost=result.purchase_cost,
            marketplace_expanses=result.marketplace_expanses,
            absolute_margin=result.absolute_margin,
            relative_margin=int(result.relative_margin * 100),
            roi=int(result.roi * 100),
            storage_price=result.storage_price,
            purchase_investments=result.purchase_investments,
            commercial_expanses=result.commercial_expanses,
            tax_expanses=result.tax_expanses,
            absolute_transit_margin=result.absolute_transit_margin,
            relative_transit_margin=int(result.relative_transit_margin * 100),
            transit_roi=int(result.transit_roi * 100),
        )

    def __create_transit_tuple(
        self, request: TransitEconomyRequestEntity, result: TransitEconomyResultEntity
    ) -> tuple[TransitEconomyRequest, TransitEconomyResult]:
        warehouse_tuple = self.__warehouse_service.find_warehouse_by_name(
            request.target_warehouse_name, request.marketplace_id
        )
        if warehouse_tuple is None:
            raise Exception(
                f"No warehouse with name '{request.target_warehouse_name}'"
                f"was found in marketplace with id: {request.marketplace_id}"
            )
        _, warehouse_id = warehouse_tuple
        request_record = TransitEconomyService.__map_request_to_record(
            request, warehouse_id
        )
        result_record = TransitEconomyService.__map_result_to_record(result)
        return request_record, result_record
