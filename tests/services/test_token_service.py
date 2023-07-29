import unittest

from jorm.market.person import UserPrivilege
from sqlalchemy import select

from jarvis_db.factories.services import create_token_service
from jarvis_db.tables import Account, TokenSet, User
from tests.db_context import DbContext


class TokenServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            account = Account(email="user@mail.org", phone="789456123", password="123")
            user = User(
                name="NoName", profit_tax=0, account=account, status=UserPrivilege.BASIC
            )
            session.add(account)
            session.add(user)
            session.flush()
            self.__user_id = user.id

    def test_create_should_work(self):
        access_token = "123"
        update_token = "456"
        imprint_token = "789"
        with self.__db_context.session() as session, session.begin():
            service = create_token_service(session)
            service.create(self.__user_id, access_token, update_token, imprint_token)
        with self.__db_context.session() as session:
            token = session.execute(
                select(TokenSet)
                .where(TokenSet.user_id == self.__user_id)
                .where(TokenSet.fingerprint_token == imprint_token)
            ).scalar_one()
            self.assertEqual(access_token, token.access_token)
            self.assertEqual(update_token, token.refresh_token)
            self.assertEqual(imprint_token, token.fingerprint_token)

    def test_find_by_imprint(self):
        access_token = "123"
        update_token = "456"
        imprint_token = "789"
        with self.__db_context.session() as session, session.begin():
            session.add(
                TokenSet(
                    user_id=self.__user_id,
                    access_token=access_token,
                    refresh_token=update_token,
                    fingerprint_token=imprint_token,
                )
            )
        with self.__db_context.session() as session:
            service = create_token_service(session)
            found_access, found_update = service.find_by_imprint(
                self.__user_id, imprint_token
            )
            self.assertEqual(access_token, found_access)
            self.assertEqual(update_token, found_update)

    def test_update_by_imprint(self):
        imprint_token = "789"
        with self.__db_context.session() as session, session.begin():
            session.add(
                TokenSet(
                    user_id=self.__user_id,
                    access_token="123",
                    refresh_token="456",
                    fingerprint_token=imprint_token,
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_token_service(session)
            new_access = "qwerty"
            new_update = "asdfg"
            service.update_by_imprint(
                self.__user_id, new_access, new_update, imprint_token
            )
        with self.__db_context.session() as session:
            token = session.execute(
                select(TokenSet)
                .where(TokenSet.user_id == self.__user_id)
                .where(TokenSet.fingerprint_token == imprint_token)
            ).scalar_one()
            self.assertEqual(new_access, token.access_token)
            self.assertEqual(new_update, token.refresh_token)

    def test_update_by_access(self):
        update_token = "123"
        with self.__db_context.session() as session, session.begin():
            session.add(
                TokenSet(
                    user_id=self.__user_id,
                    access_token="access_token",
                    refresh_token=update_token,
                    fingerprint_token="imprint_token",
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_token_service(session)
            new_access = "qwerty"
            new_update = "asdfg"
            service.update_by_access(
                self.__user_id, update_token, new_access, new_update
            )
        with self.__db_context.session() as session:
            token = session.execute(
                select(TokenSet)
                .where(TokenSet.user_id == self.__user_id)
                .where(TokenSet.refresh_token == new_update)
            ).scalar_one()
            self.assertEqual(new_access, token.access_token)
            self.assertEqual(new_update, token.refresh_token)

    def test_delete_by_imprint(self):
        imprint_token = "789"
        with self.__db_context.session() as session, session.begin():
            session.add(
                TokenSet(
                    user_id=self.__user_id,
                    access_token="123",
                    refresh_token="456",
                    fingerprint_token=imprint_token,
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_token_service(session)
            service.delete_by_imprint(self.__user_id, imprint_token)
        with self.__db_context.session() as session:
            token = session.execute(
                select(TokenSet)
                .where(TokenSet.user_id == self.__user_id)
                .where(TokenSet.fingerprint_token == imprint_token)
            ).scalar_one_or_none()
            self.assertIsNone(token)


if __name__ == "__main__":
    unittest.main()
