from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Marketplace


class MarketplaceRepository(AlchemyRepository[Marketplace]):
    def find_all(self) -> list[Marketplace]:
        db_marketplaces = (
            self._session.execute(
                select(Marketplace)
                .outerjoin(Marketplace.warehouses)
                .outerjoin(Marketplace.categories)
                .distinct()
            )
            .scalars()
            .all()
        )
        return list(db_marketplaces)

    def find_by_name(self, marketplace_name: str) -> Marketplace | None:
        return self._session.execute(
            select(Marketplace)
            .outerjoin(Marketplace.warehouses)
            .outerjoin(Marketplace.categories)
            .where(Marketplace.name == marketplace_name)
            .distinct()
        ).scalar()

    def exists_with_name(self, name: str) -> bool:
        return (
            self._session.execute(
                select(Marketplace).where(Marketplace.name.ilike(name))
            ).scalar()
            is not None
        )
