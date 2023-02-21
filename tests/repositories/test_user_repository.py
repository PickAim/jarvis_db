import unittest

from jorm.market.person import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.person.user_mappers import UserJormToTableMapper, UserTableToJormMapper
from jarvis_db.repositores.market.person import UserRepository


class UserRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        email = 'user@mail.org'
        with session() as s, s.begin():
            s.add(tables.Account(phone='1231',
                  email='user@mail.org', password='safkm1'))
        with session() as s:
            db_account = s.execute(
                select(tables.Account)
                .where(tables.Account.email == email)
            ).scalar_one()
            self.__account_id = db_account.id
        self.__session = session

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
