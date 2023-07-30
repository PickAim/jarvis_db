import unittest

from jorm.market.person import User as UserEntity
from sqlalchemy import select

from jarvis_db.factories.services import create_user_service
from jarvis_db.tables import Account, User
from tests.db_context import DbContext
from jorm.market.person import UserPrivilege


class UserServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            account = Account(email="user@mail.org", phone="789456123", password="123")
            session.add(account)
            session.flush()
            self.__account_id = account.id

    def test_create(self):
        user_entity = UserEntity(name="user1")
        with self.__db_context.session() as session, session.begin():
            service = create_user_service(session)
            service.create(user_entity, self.__account_id)
        with self.__db_context.session() as session:
            user = session.execute(
                select(User).where(User.name == user_entity.name)
            ).scalar_one_or_none()
            assert user is not None
            self.assertEqual(user_entity.name, user.name)
            self.assertEqual(user_entity.profit_tax, user.profit_tax)
            self.assertEqual(user_entity.privilege, user.status)
            self.assertEqual(self.__account_id, user.account_id)

    def test_find_by_account_id(self):
        user_id = 100
        user_name = "qwerty"
        profit_tax = 0.2
        privilege = UserPrivilege.ADVANCED
        with self.__db_context.session() as session, session.begin():
            session.add(
                User(
                    id=user_id,
                    name=user_name,
                    profit_tax=profit_tax,
                    account_id=self.__account_id,
                    status=privilege,
                )
            )
        with self.__db_context.session() as session:
            service = create_user_service(session)
            user_tuple = service.find_by_account_id(self.__account_id)
            assert user_tuple is not None
            user, _ = user_tuple
            self.assertEqual(user_id, user.user_id)
            self.assertEqual(user_name, user.name)
            self.assertEqual(profit_tax, user.profit_tax)
            self.assertEqual(privilege, user.privilege)


if __name__ == "__main__":
    unittest.main()
