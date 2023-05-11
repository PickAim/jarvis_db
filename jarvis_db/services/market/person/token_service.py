from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.person.token_repository import TokenRepository
from jarvis_db.tables import TokenSet


class TokenService:
    def __init__(
            self,
            token_repository: TokenRepository,
            table_mapper: Mapper[TokenSet, tuple[int, str, str, str]]
    ):
        self.__token_repository = token_repository
        self.__table_mapper = table_mapper

    def create(self, user_id: int, access_token: str, update_token: str, imprint_token: str):
        token_info = TokenSet(
            user_id=user_id,
            access_token=access_token,
            refresh_token=update_token,
            fingerprint_token=imprint_token
        )
        self.__token_repository.add(token_info)

    def find_by_imprint(self, user_id: int, imprint: str) -> tuple[str, str]:
        token = self.__token_repository.find_by_fingerprint(user_id, imprint)
        _, access, refresh, _ = self.__table_mapper.map(token)
        return access, refresh

    def update_by_imprint(self, user_id: int, access_token: str, update_token: str, imprint_token: str):
        token = self.__token_repository.find_by_fingerprint(
            user_id, imprint_token)
        token.access_token = access_token
        token.refresh_token = update_token
        self.__token_repository.update(token)

    def update_by_access(self, user_id: int, old_update: str, access_token: str, update_token: str):
        token = self.__token_repository.find_by_refresh(user_id, old_update)
        token.access_token = access_token
        token.refresh_token = update_token
        self.__token_repository.update(token)

    def delete_by_imprint(self, user_id: int, imprint: str):
        token = self.__token_repository.find_by_fingerprint(user_id, imprint)
        self.__token_repository.delete(token)
