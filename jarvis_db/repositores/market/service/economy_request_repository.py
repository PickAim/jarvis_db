from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import EconomyRequest, User


class EconomyRequestRepository(AlchemyRepository[EconomyRequest]):
    # def add(self, request: EconomyRequest, user_id: int, marketplace_id: int):
    #     db_request = self.__to_table_mapper.map(request)
    #     niche_id = self._session.execute(
    #         select(tables.Niche.id)
    #         .join(tables.Niche.category)
    #         .join(tables.Category.marketplace)
    #         .where(tables.Marketplace.id == marketplace_id)
    #         .where(tables.Niche.name.ilike(request.niche_name))
    #     ).scalar_one()
    #     db_request.niche_id = niche_id
    #     db_request.user_id = user_id
    #     self.__session.add(db_request)

    def find_user_requests(self, user_id: int) -> list[EconomyRequest]:
        db_requests = self._session.execute(
            select(EconomyRequest)
            .join(EconomyRequest.user)
            .where(User.id == user_id)
        ).scalars().all()
        return list(db_requests)
