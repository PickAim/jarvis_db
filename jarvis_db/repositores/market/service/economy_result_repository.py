from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import EconomyResult


class EconomyResultRepository(AlchemyRepository[EconomyResult]):

    def find_add(self) -> list[EconomyResult]:
        db_results = self._session.execute(
            select(EconomyResult)
            .join(EconomyResult.request)
        ).scalars().all()
        return list(db_results)
