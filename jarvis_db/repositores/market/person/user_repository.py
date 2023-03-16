from typing import Iterable

from jorm.market.person import Account, User
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

    def add_to_account(self, user: User, account_id: int):
        db_user = self.__to_table_mapper.map(user)
        db_user.account_id = account_id
        self.__session.add(db_user)

    def find_by_account(self, account: Account) -> User:
        db_user = self.__session.execute(
            select(tables.User)
            .join(tables.User.account)
            .where(tables.Account.email == account.email, tables.Account.phone == account.phone_number)
        ).scalar_one()
        return self.__to_jorm_mapper.map(db_user)

    def fetch_all(self) -> list[User]:
        db_users = self.__session.execute(
            select(tables.User)
        ).scalars().all()
        return [self.__to_jorm_mapper.map(user) for user in db_users]
