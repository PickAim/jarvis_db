from sqlalchemy import delete, select, update
from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import TokenSet
from sqlalchemy.orm import Session


class TokenService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[TokenSet, tuple[int, str, str, str]],
    ):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(
        self, user_id: int, access_token: str, update_token: str, imprint_token: str
    ):
        self.__session.add(
            TokenSet(
                user_id=user_id,
                access_token=access_token,
                refresh_token=update_token,
                fingerprint_token=imprint_token,
            )
        )
        self.__session.flush()

    def find_by_imprint(self, user_id: int, imprint: str) -> tuple[str, str]:
        token = self.__session.execute(
            select(TokenSet)
            .where(TokenSet.user_id == user_id)
            .where(TokenSet.fingerprint_token == imprint)
        ).scalar_one()
        _, access, refresh, _ = self.__table_mapper.map(token)
        return access, refresh

    def update_by_imprint(
        self, user_id: int, access_token: str, update_token: str, imprint_token: str
    ):
        self.__session.execute(
            update(TokenSet)
            .where(TokenSet.user_id == user_id)
            .where(TokenSet.fingerprint_token == imprint_token)
            .values(access_token=access_token, refresh_token=update_token)
        )
        self.__session.flush()

    def update_by_access(
        self, user_id: int, old_update: str, access_token: str, update_token: str
    ):
        self.__session.execute(
            update(TokenSet)
            .where(TokenSet.user_id == user_id)
            .where(TokenSet.refresh_token == old_update)
            .values(access_token=access_token, refresh_token=update_token)
        )
        self.__session.flush()

    def delete_by_imprint(self, user_id: int, imprint: str):
        self.__session.execute(
            delete(TokenSet)
            .where(TokenSet.user_id == user_id)
            .where(TokenSet.fingerprint_token == imprint)
        )
        self.__session.flush()
