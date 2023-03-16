import unittest

from jorm.market.person import Account
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.person.account_mappers import (
    AccountJormToTableMapper, AccountTableToJormMapper)
from jarvis_db.repositores.market.person import AccountRepository


class AccountRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        self.__session = session

    def test_add(self):
        account = Account('user#1', "12312", "user@mail.com")
        with self.__session() as session, session.begin():
            repository = AccountRepository(
                session, AccountTableToJormMapper(), AccountJormToTableMapper())
            repository.add(account)
        with self.__session() as session:
            db_account = session.execute(
                select(tables.Account)
            ).scalar_one()
            self.assertEqual(account.phone_number, db_account.phone)
            self.assertEqual(account.email, db_account.email)
            self.assertEqual(account.hashed_password, db_account.password)

    def test_add_all(self):
        account_to_add = 10
        accounts = [Account(f'user#{i}', f'{i}{i + 1}{i + 3}{i + 4}', f'user{i}@mail.org')
                    for i in range(1, account_to_add + 1)]
        with self.__session() as session, session.begin():
            repository = AccountRepository(
                session, AccountTableToJormMapper(), AccountJormToTableMapper())
            repository.add_all(accounts)
        with self.__session() as session:
            db_accounts = session.execute(
                select(tables.Account)
            ).scalars().all()
            for account, db_account in zip(accounts, db_accounts, strict=True):
                self.assertEqual(account.phone_number, db_account.phone)
                self.assertEqual(account.email, db_account.email)
                self.assertEqual(account.hashed_password, db_account.password)
