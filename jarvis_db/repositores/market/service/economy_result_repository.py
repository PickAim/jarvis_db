from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import UnitEconomyResult


class EconomyResultRepository(AlchemyRepository[UnitEconomyResult]):

    def find_add(self) -> list[UnitEconomyResult]:
        db_results = self._session.execute(
            select(UnitEconomyResult)
            .join(UnitEconomyResult.request)
        ).scalars().all()
        return list(db_results)
