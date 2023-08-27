from jorm.market.service import FrequencyRequest as FrequencyRequestEntity
from jorm.market.service import FrequencyResult as FrequencyResultEntity
from jorm.market.service import RequestInfo
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import FrequencyRequest, FrequencyResult, User
from jarvis_db.services.market.infrastructure.niche_service import NicheService


class FrequencyService:
    def __init__(
        self,
        session: Session,
        niche_service: NicheService,
        result_table_mapper: Mapper[
            FrequencyRequest,
            tuple[FrequencyRequestEntity, FrequencyResultEntity, RequestInfo],
        ],
    ):
        self.__session = session
        self.__niche_service = niche_service
        self.__result_table_mapper = result_table_mapper

    def save(
        self,
        request_info: RequestInfo,
        request_entity: FrequencyRequestEntity,
        result_entity: FrequencyResultEntity,
        user_id: int,
    ) -> int:
        niche_tuple = self.__niche_service.find_by_name(
            request_entity.niche, request_entity.category_id
        )
        if niche_tuple is None:
            raise Exception(f"No niche matching request {request_entity}")
        _, niche_id = niche_tuple
        request = FrequencyRequest(
            name=request_info.name,
            user_id=user_id,
            date=request_info.date,
            niche_id=niche_id,
        )
        results = (
            FrequencyResult(request=request, cost=cost, frequency=frequency)
            for cost, frequency in zip(result_entity.x, result_entity.y, strict=True)
        )
        self.__session.add_all(results)
        self.__session.flush()
        return request.id

    def find_user_requests(
        self, user_id: int
    ) -> dict[int, tuple[FrequencyRequestEntity, FrequencyResultEntity, RequestInfo]]:
        results = (
            self.__session.execute(
                select(FrequencyRequest)
                .options(
                    selectinload(FrequencyRequest.results),
                )
                .join(FrequencyRequest.user)
                .where(User.id == user_id)
            )
            .scalars()
            .unique()
            .all()
        )
        return {
            result_unit.id: self.__result_table_mapper.map(result_unit)
            for result_unit in results
        }

    def delete(self, request_id: int) -> bool:
        request = self.__session.execute(
            select(FrequencyRequest).where(FrequencyRequest.id == request_id)
        ).scalar_one_or_none()
        if request is not None:
            self.__session.delete(request)
            self.__session.flush()
            return True
        else:
            return False
