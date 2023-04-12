from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import FrequencyRequest, User


class FrequencyRequestRepository(AlchemyRepository[FrequencyRequest]):

    def fetch_user_requests(self, user_id: int) -> list[FrequencyRequest]:
        db_requests = self._session.execute(
            select(FrequencyRequest)
            .join(FrequencyRequest.user)
            .where(User.id == user_id)
        ).scalars().all()
        return list(db_requests)
