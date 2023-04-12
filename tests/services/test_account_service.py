import unittest

from jorm.market.person import Account as AccountEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.repositores.mappers.market.person.account_mappers import \
    AccountTableToJormMapper
from jarvis_db.repositores.market.person.account_repository import \
    AccountRepository
from jarvis_db.services.market.person.account_service import AccountService
from jarvis_db.tables import Account
from tests.db_context import DbContext


class AccountServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            service = create_service(session)
            account_entity = AccountEntity('user@mail.org', '123', '789456123')
            service.create(account_entity)
        with self.__db_context.session() as session:
            account = session.execute(
                select(Account)
                .where(Account.email == account_entity.email)
            ).scalar_one()
            self.assertEqual(account.email, account_entity.email)
            self.assertEqual(account.password, account_entity.hashed_password)
            self.assertEqual(account.phone, account_entity.phone_number)

    def test_find_by_email(self):
        email = 'user@mail.org'
        with self.__db_context.session() as session, session.begin():
            session.add(
                Account(email=email, phone='789456123', password='123'))
        with self.__db_context.session() as session:
            service = create_service(session)
            account, _ = service.find_by_email(email)
            self.assertEqual(account.email, email)


def create_service(session: Session) -> AccountService:
    return AccountService(AccountRepository(session), AccountTableToJormMapper())
