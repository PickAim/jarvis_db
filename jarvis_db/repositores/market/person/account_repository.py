from typing import Iterable

from jorm.market.person import Account
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class AccountRepository:
    def __init__(
        self,
        session: Session,
        to_jorm_mapper: Mapper[tables.Account, Account],
        to_table_mapper: Mapper[Account, tables.Account]
    ):
        self.__session = session
        self.__to_jorm_mapper = to_jorm_mapper
        self.__to_table_mapper = to_table_mapper

    def add(self, account: Account):
        self.__session.add(self.__to_table_mapper.map(account))

    def add_all(self, accounts: Iterable[Account]):
        self.__session.add_all(
            (self.__to_table_mapper.map(account) for account in accounts))

    def find_by_email(self, email: str) -> Account:
        db_user = self.__session.execute(
            select(tables.Account)
            .where(tables.Account.email == email)
        ).scalar_one()
        return self.__to_jorm_mapper.map(db_user)

    def fetch_all(self) -> list[Account]:
        db_accounts = self.__session.execute(
            select(tables.Account)
        ).scalars().all()
        return [self.__to_jorm_mapper.map(account) for account in db_accounts]
