from typing import Iterable

from jorm.market.person import User
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class UserRepository:
    def __init__(
        self,
        session: Session,
        to_jorm_mapper: Mapper[tables.User, User],
        to_table_mapper: Mapper[User, tables.User]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, user: User):
        self.__session.add(self.__to_table_mapper.map(user))

    def add_all(self, users: Iterable[User]):
        self.__session.add_all(
            (self.__to_table_mapper.map(user) for user in users))

    def fetch_all(self) -> list[User]:
        db_users = self.__session.execute(
            select(tables.User)
        ).scalars().all()
        return [self.__to_jorm_mapper.map(user) for user in db_users]
