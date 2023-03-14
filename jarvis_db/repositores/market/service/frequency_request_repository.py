from jorm.market.service import FrequencyRequest
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class FrequencyRequestRepository:
    def __init__(
            self, session: Session,
            to_jorm_mapper: Mapper[tables.FrequencyRequest, FrequencyRequest],
            to_table_mapper: Mapper[FrequencyRequest, tables.FrequencyRequest]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add_by_user(self, request: FrequencyRequest, user_id: int):
        db_requst = self.__to_table_mapper.map(request)
        db_requst.user_id = user_id
        self.__session.add(db_requst)

    def fetch_user_requests(self, user_id: int) -> dict[int, FrequencyRequest]:
        db_requests = self.__session.execute(
            select(tables.FrequencyRequest)
            .join(tables.FrequencyRequest.user)
            .where(tables.User.id == user_id)
        ).scalars().all()
        return {request.id: self.__to_jorm_mapper.map(request) for request in db_requests}
