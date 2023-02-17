from jarvis_db import tables
from jarvis_db.core.mapper import Mapper
from jorm.market.person import Account


class AccountJormToTableMapper(Mapper[Account, tables.Account]):
    def map(self, value: Account) -> tables.Account:
        return tables.Account(
            login=value.login,
            password=value.hashed_password
        )


class AccountTableToJormMapper(Mapper[tables.Account, Account]):
    def map(self, value: tables.Account) -> Account:
        return Account(
            value.login,
            value.password
        )
