from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import EconomyRequest, User


class EconomyRequestRepository(AlchemyRepository[EconomyRequest]):

    def find_user_requests(self, user_id: int) -> list[EconomyRequest]:
        db_requests = self._session.execute(
            select(EconomyRequest)
            .join(EconomyRequest.user)
            .where(User.id == user_id)
        ).scalars().all()
        return list(db_requests)
