from jarvis_db.core.mapper import Mapper
from jarvis_db.tables import TokenSet


class TokenTableMapper(Mapper[TokenSet, tuple[int, str, str, str]]):
    def map(self, value: TokenSet) -> tuple[int, str, str, str]:
        return (
            value.user_id,
            value.access_token,
            value.refresh_token,
            value.fingerprint_token,
        )
