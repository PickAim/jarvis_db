import unittest

from jorm.market.person import Account as AccountEntity
from sqlalchemy import select

from jarvis_db.factories.services import create_account_service
from jarvis_db.mappers.market.person.account_mappers import AccountTableToJormMapper
from jarvis_db.schemas import Account
from tests.db_context import DbContext


class AccountServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            service = create_account_service(session)
            account_entity = AccountEntity("user@mail.org", "123", "+789456123")
            account_id = service.create(account_entity)
        with self.__db_context.session() as session:
            account = session.execute(
                select(Account).where(Account.id == account_id)
            ).scalar_one()
            self.assertEqual(account.email, account_entity.email)
            self.assertEqual(account.password, account_entity.hashed_password)
            self.assertEqual(account.phone, account_entity.phone_number)

    def test_find_by_id(self):
        mapper = AccountTableToJormMapper()
        account_id = 100
        with self.__db_context.session() as session, session.begin():
            account = Account(
                id=account_id, email="mail@org.com", phone="+723456789", password="123"
            )
            session.add(account)
            session.flush()
            expected = mapper.map(account)
        with self.__db_context.session() as session:
            service = create_account_service(session)
            actual = service.find_by_id(account_id)
            self.assertEqual(expected, actual)

    def test_find_by_email(self):
        email = "user@mail.org"
        with self.__db_context.session() as session, session.begin():
            session.add(Account(email=email, phone="+789456123", password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email(email)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(account.email, email)

    def test_find_by_phone(self):
        phone = "+73456789"
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
            session.add(Account(email=email, phone="+789456123", password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email_or_phone(email=email)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(account.email, email)

    def test_find_by_email_or_phone_should_return_account_by_phone(self):
        phone = "+7123456789"
        with self.__db_context.session() as session, session.begin():
            session.add(Account(email="user@mail.org", phone=phone, password="123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email_or_phone(phone=phone)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(phone, account.phone_number)

    def test_find_by_email_or_phone_should_work_correct_with_unfilled_phone(self):
        email = "user@mail.org"
        with self.__db_context.session() as session, session.begin():
            service = create_account_service(session)
            service.create(AccountEntity("anoter.user@mail.org", "456"))
            service.create(AccountEntity(email, "123"))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email_or_phone(email=email)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(email, account.email)
            self.assertEqual("", account.phone_number)

    def test_find_by_email_or_phone_should_work_correct_with_unfilled_email(self):
        phone = "+7987654321"
        with self.__db_context.session() as session, session.begin():
            service = create_account_service(session)
            service.create(AccountEntity("", "456", "123456789"))
            session.flush()
            service.create(AccountEntity("", "123", phone))
        with self.__db_context.session() as session:
            service = create_account_service(session)
            account_result = service.find_by_email_or_phone(phone=phone)
            assert account_result is not None
            account, _ = account_result
            self.assertEqual(phone, account.phone_number)
            self.assertEqual("", account.email)


if __name__ == "__main__":
    unittest.main()
