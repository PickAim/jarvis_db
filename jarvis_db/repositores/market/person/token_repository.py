from jarvis_db.tables import TokenSet

from sqlalchemy import select
from jarvis_db.repositores.alchemy_repository import AlchemyRepository


class TokenRepository(AlchemyRepository[TokenSet]):
    def find_by_fingerprint(self, user_id: int, fingerprint: str) -> TokenSet:
        return self._session.execute(
            select(TokenSet)
            .where(TokenSet.user_id == user_id)
            .where(TokenSet.fingerprint_token == fingerprint)
        ).scalar_one()

    def find_by_refresh(self, user_id: int, refresh_token: str) -> TokenSet:
        return self._session.execute(
            select(TokenSet)
            .where(TokenSet.user_id == user_id)
            .where(TokenSet.refresh_token == refresh_token)
        ).scalar_one()
