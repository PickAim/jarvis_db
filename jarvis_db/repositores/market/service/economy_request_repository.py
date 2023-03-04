from jorm.market.service import EconomyRequest
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class EconomyRequestRepository:
    def __init__(
            self,
            session: Session,
            to_jorm_mapper: Mapper[tables.EconomyRequest, EconomyRequest],
            to_table_mapper: Mapper[EconomyRequest, tables.EconomyRequest]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, request: EconomyRequest, user_id: int, marketplace_name: str):
        db_request = self.__to_table_mapper.map(request)
        niche_id = self.__session.execute(
            select(tables.Niche.id)
            .join(tables.Niche.category)
            .join(tables.Category.marketplace)
            .where(tables.Marketplace.name.ilike(marketplace_name))
            .where(tables.Niche.name.ilike(request.niche_name))
        ).scalar_one()
        db_request.niche_id = niche_id
        self.__session.add(db_request)

    def fetch_user_requests(self, user_id: int) -> list[EconomyRequest]:
        db_requests = self.__session.execute(
            select(tables.EconomyRequest)
            .join(tables.EconomyRequest.user)
            .where(tables.User.id == user_id)
        ).scalars().all()
        return [self.__to_jorm_mapper.map(request) for request in db_requests]
