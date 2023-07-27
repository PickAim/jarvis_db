import unittest

from jorm.market.person import Account as AccountEntity
from sqlalchemy import select

from jarvis_db.factories.services import create_account_service
from jarvis_db.tables import Account
from tests.db_context import DbContext


class AccountServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            service = create_account_service(session)
            account_entity = AccountEntity("user@mail.org", "123", "789456123")
            service.create(account_entity)
        with self.__db_context.session() as session:
            account = session.execute(
                select(Account).where(Account.email == account_entity.email)
            ).scalar_one()
            self.assertEqual(account.email, account_entity.email)
            self.assertEqual(account.password, account_entity.hashed_password)
            self.assertEqual(account.phone, account_entity.phone_number)

    def test_find_by_email(self):
        email = "user@mail.org"
        with self.__db_context.session() as session, session.begin():
            session.add(Account(email=email, phone="789456123", password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email(email)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(account.email, email)

    def test_find_by_phone(self):
        phone = "123456789"
        with self.__db_context.session() as session, session.begin():
            session.add(Account(email="user@mail.org", phone=phone, password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_phone(phone)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(phone, account.phone_number)

    def test_find_by_email_or_phone_should_return_account_by_email(self):
        email = "user@mail.org"
        with self.__db_context.session() as session, session.begin():
            session.add(Account(email=email, phone="789456123", password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email_or_phone(email, "")
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(account.email, email)

    def test_find_by_email_or_phone_should_return_account_by_phone(self):
        phone = "123456789"
        with self.__db_context.session() as session, session.begin():
            session.add(Account(email="user@mail.org", phone=phone, password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email_or_phone("", phone)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(phone, account.phone_number)
