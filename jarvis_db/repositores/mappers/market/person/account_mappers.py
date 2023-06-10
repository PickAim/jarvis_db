from jorm.market.person import Account

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class AccountJormToTableMapper(Mapper[Account, tables.Account]):
    def map(self, value: Account) -> tables.Account:
        return tables.Account(
            phone=value.phone_number, email=value.email, password=value.hashed_password
        )


class AccountTableToJormMapper(Mapper[tables.Account, Account]):
    def map(self, value: tables.Account) -> Account:
        return Account(
            phone_number=value.phone, email=value.email, hashed_password=value.password
        )
