from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import UnitEconomyRequest, User


class EconomyRequestRepository(AlchemyRepository[UnitEconomyRequest]):

    def find_user_requests(self, user_id: int) -> list[UnitEconomyRequest]:
        db_requests = self._session.execute(
            select(UnitEconomyRequest)
            .join(UnitEconomyRequest.user)
            .where(User.id == user_id)
        ).scalars().all()
        return list(db_requests)
