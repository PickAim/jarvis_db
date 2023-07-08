from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import FrequencyRequest, User


class FrequencyRequestRepository(AlchemyRepository[FrequencyRequest]):
    def find_user_requests(self, user_id: int) -> list[FrequencyRequest]:
        db_requests = (
            self._session.execute(
                select(FrequencyRequest)
                .join(FrequencyRequest.user)
                .join(FrequencyRequest.results)
                .where(User.id == user_id)
            )
            .scalars()
            .all()
        )
        return list(db_requests)

    def find_by_id(self, request_id: int) -> FrequencyRequest | None:
        return self._session.execute(
            select(FrequencyRequest).where(FrequencyRequest.id == request_id)
        ).scalar_one_or_none()
