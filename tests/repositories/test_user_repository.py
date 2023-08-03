import unittest

from jorm.market.person import Account
from sqlalchemy import select

from jarvis_db import schemas
from tests.db_context import DbContext


class UserRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        account = Account("1231", "user@mail.org", "qwerty")
        with self.__db_context.session() as s, s.begin():
            s.add(
                schemas.Account(
                    phone=account.phone_number,
                    email=account.email,
                    password=account.hashed_password,
                )
            )
        with self.__db_context.session() as s:
            db_account = s.execute(
                select(schemas.Account).where(schemas.Account.email == account.email)
            ).scalar_one()
            self.__account_id = db_account.id
        self.__account = account

    def test_add(self):
        ...

    def test_find_by_account(self):
        ...


if __name__ == "__main__":
    unittest.main()
