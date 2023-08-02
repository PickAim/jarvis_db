from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.schemas import UnitEconomyRequest, UnitEconomyResult


class EconomyResultRepository(AlchemyRepository[UnitEconomyResult]):
    def find_all(self) -> list[UnitEconomyResult]:
        db_results = (
            self._session.execute(
                select(UnitEconomyResult).join(UnitEconomyResult.request)
            )
            .scalars()
            .all()
        )
        return list(db_results)

    def find_user_results(self, user_id: int) -> list[UnitEconomyResult]:
        results = (
            self._session.execute(
                select(UnitEconomyResult)
                .join(UnitEconomyResult.request)
                .where(UnitEconomyRequest.user_id == user_id)
            )
            .scalars()
            .all()
        )
        return list(results)
