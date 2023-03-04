import unittest

from jorm.market.person import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.person.user_mappers import UserJormToTableMapper, UserTableToJormMapper
from jarvis_db.repositores.market.person import UserRepository
from jorm.market.person import Account


class UserRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        account = Account('1231', 'user@mail.org', 'qwerty')
        with session() as s, s.begin():
            s.add(tables.Account(phone=account.phone,
                  email=account.email, password=account.hashed_password))
        with session() as s:
            db_account = s.execute(
                select(tables.Account)
                .where(tables.Account.email == account.email)
            ).scalar_one()
            self.__account_id = db_account.id
        self.__session = session
        self.__account = account

    def test_add(self):
        user = User(name='User#1')
        with self.__session() as session, session.begin():
            repository = UserRepository(
                session, UserTableToJormMapper(), UserJormToTableMapper())
            repository.add_to_account(user, self.__account_id)
        with self.__session() as session:
            db_user = session.execute(
                select(tables.User)
                .join(tables.Account)
                .where(tables.User.name == user.name, tables.Account.id == self.__account_id)
            ).scalar_one()
            self.assertEqual(user.name, db_user.name)

    def test_find_by_account(self):
        user_name = 'User#1'
        with self.__session() as session, session.begin():
            db_account = session.execute(
                select(tables.Account)
                .where(tables.Account.email == self.__account.email)
            ).scalar_one()
            session.add(tables.User(name=user_name,
                        account=db_account, profit_tax=0))
        with self.__session() as session:
            repository = UserRepository(
                session, UserTableToJormMapper(), UserJormToTableMapper())
            user = repository.find_by_account(self.__account)
            self.assertEqual(user_name, user.name)
