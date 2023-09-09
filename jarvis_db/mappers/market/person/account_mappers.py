from jorm.market.person import Account

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper


class AccountJormToTableMapper(Mapper[Account, schemas.Account]):
    def map(self, value: Account) -> schemas.Account:
        return schemas.Account(
            phone=value.phone_number, email=value.email, password=value.hashed_password
        )


class AccountTableToJormMapper(Mapper[schemas.Account, Account]):
    def map(self, value: schemas.Account) -> Account:
        return Account(
            phone_number=value.phone if value.phone else "",
            email=value.email if value.email else "",
            hashed_password=value.password,
        )
