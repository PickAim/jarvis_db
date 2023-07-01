from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import FrequencyResult


class FrequencyResultRepository(AlchemyRepository[FrequencyResult]):
    def fetch_all(self) -> list[FrequencyResult]:
        db_results = (
            self._session.execute(select(FrequencyResult).join(FrequencyResult.request))
            .scalars()
            .all()
        )
        return list(db_results)
