from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import FrequencyRequest, FrequencyResult


class FrequencyResultRepository(AlchemyRepository[FrequencyResult]):
    def fetch_all(self) -> list[FrequencyResult]:
        db_results = (
            self._session.execute(select(FrequencyResult).join(FrequencyResult.request))
            .scalars()
            .all()
        )
        return list(db_results)

    def find_user_results(self, user_id: int) -> list[FrequencyResult]:
        results = (
            self._session.execute(
                select(FrequencyResult)
                .join(FrequencyResult.request)
                .where(FrequencyRequest.user_id == user_id)
            )
            .scalars()
            .all()
        )
        return list(results)
