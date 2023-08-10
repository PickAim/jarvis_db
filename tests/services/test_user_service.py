import unittest

from jorm.market.person import User as UserEntity
from jorm.market.person import UserPrivilege
from sqlalchemy import select

from jarvis_db.factories.services import create_user_service
from jarvis_db.mappers.market.person.user_mappers import (
    UserTableToJormMapper,
)
from jarvis_db.schemas import Account, Marketplace, MarketplaceApiKey, ProductCard, User
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class UserServiceTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext(echo=True)
        with self.__db_context.session() as session, session.begin():
            account = Account(email="user@mail.org", phone="789456123", password="123")
            session.add(account)
            session.flush()
            self.__account_id = account.id

    def test_create(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
        expected = UserEntity(
            name="user1", marketplace_keys={marketplace_id: "api_key"}
        )
        with self.__db_context.session() as session, session.begin():
            service = create_user_service(session)
            service.create(expected, self.__account_id)
        with self.__db_context.session() as session:
            user = session.execute(
                select(User).where(User.name == expected.name)
            ).scalar_one_or_none()
            assert user is not None
            mapper = UserTableToJormMapper()
            actual = mapper.map(user)
            expected.user_id = actual.user_id
            self.assertEqual(expected, actual)

    def test_find_by_id_without_api_keys(self):
        user_id = 100
        with self.__db_context.session() as session, session.begin():
            db_user = User(
                id=user_id,
                name="user_name",
                profit_tax=0.2,
                account_id=self.__account_id,
                status=UserPrivilege.ADVANCED,
            )
            session.add(db_user)
            mapper = UserTableToJormMapper()
            expected = mapper.map(db_user)
        with self.__db_context.session() as session:
            service = create_user_service(session)
            actual = service.find_by_id(user_id)
            self.assertEqual(expected, actual)

    def test_find_by_id_with_api_keys(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
        user_id = 100
        with self.__db_context.session() as session, session.begin():
            db_user = User(
                id=user_id,
                name="user_name",
                profit_tax=0.2,
                account_id=self.__account_id,
                status=UserPrivilege.ADVANCED,
                marketplace_api_keys=[
                    MarketplaceApiKey(marketplace_id=marketplace_id, api_key="api_key")
                ],
            )
            session.add(db_user)
            mapper = UserTableToJormMapper()
            expected = mapper.map(db_user)
        with self.__db_context.session() as session:
            service = create_user_service(session)
            actual = service.find_by_id(user_id)
            self.assertEqual(expected, actual)

    def test_find_by_account_id_without_api_keys(self):
        user_id = 100
        with self.__db_context.session() as session, session.begin():
            db_user = User(
                id=user_id,
                name="user_name",
                profit_tax=0.2,
                account_id=self.__account_id,
                status=UserPrivilege.ADVANCED,
            )
            session.add(db_user)
            mapper = UserTableToJormMapper()
            expected = mapper.map(db_user)
        with self.__db_context.session() as session:
            service = create_user_service(session)
            actual = service.find_by_id(user_id)
            self.assertEqual(expected, actual)

    def test_find_by_account_id_with_api_keys(self):
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
        with self.__db_context.session() as session, session.begin():
            db_user = User(
                id=100,
                name="user_name",
                profit_tax=0.2,
                account_id=self.__account_id,
                status=UserPrivilege.ADVANCED,
                marketplace_api_keys=[
                    MarketplaceApiKey(marketplace_id=marketplace_id, api_key="api_key")
                ],
            )
            session.add(db_user)
            mapper = UserTableToJormMapper()
            expected = mapper.map(db_user)
        with self.__db_context.session() as session:
            service = create_user_service(session)
            user_tuple = service.find_by_account_id(self.__account_id)
            assert user_tuple is not None
            actual, _ = user_tuple
            self.assertEqual(expected, actual)

    def test_find_all(self):
        mapper = UserTableToJormMapper()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_users(20)
            expected = {
                user.id: mapper.map(user)
                for user in session.execute(
                    select(User).join(User.account).outerjoin(User.marketplace_api_keys)
                )
                .scalars()
                .unique()
                .all()
            }
        with self.__db_context.session() as session:
            service = create_user_service(session)
            actual = service.find_all()
            self.assertDictEqual(expected, actual)

    def test_append_api_key(self):
        user_id = 100
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
            session.add(
                User(
                    id=user_id,
                    name="user_name",
                    profit_tax=0.2,
                    account_id=self.__account_id,
                    status=UserPrivilege.ADVANCED,
                )
            )
        api_key = "api_key"
        with self.__db_context.session() as session, session.begin():
            service = create_user_service(session)
            service.append_api_key(user_id, api_key, marketplace_id)
        with self.__db_context.session() as session:
            user = session.execute(select(User).where(User.id == user_id)).scalar_one()
            self.assertEqual(1, len(user.marketplace_api_keys))
            api_key_record = user.marketplace_api_keys[0]
            self.assertEqual(user_id, api_key_record.user_id)
            self.assertEqual(marketplace_id, api_key_record.marketplace_id)
            self.assertEqual(api_key, api_key_record.api_key)

    def test_remove_api_key(self):
        user_id = 100
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_marketplaces(1)
            marketplace_id = session.execute(select(Marketplace.id)).scalar_one()
            session.add(
                User(
                    id=user_id,
                    name="user_name",
                    profit_tax=0.2,
                    account_id=self.__account_id,
                    status=UserPrivilege.ADVANCED,
                    marketplace_api_keys=[
                        MarketplaceApiKey(
                            marketplace_id=marketplace_id, api_key="api_key"
                        )
                    ],
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_user_service(session)
            service.remove_api_key(user_id, marketplace_id)
        with self.__db_context.session() as session:
            user = session.execute(select(User).where(User.id == user_id)).scalar_one()
            self.assertEqual(0, len(user.marketplace_api_keys))

    def test_delete(self):
        user_id = 100
        with self.__db_context.session() as session, session.begin():
            session.add(
                User(
                    id=user_id,
                    name="user_name",
                    profit_tax=0.1,
                    account_id=self.__account_id,
                    status=UserPrivilege.BASIC,
                )
            )
        with self.__db_context.session() as session, session.begin():
            service = create_user_service(session)
            service.delete(user_id)
        with self.__db_context.session() as session:
            user = session.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            account = session.execute(
                select(Account).where(Account.id == self.__account_id)
            ).scalar_one_or_none()
            self.assertIsNone(user)
            self.assertIsNone(account)


if __name__ == "__main__":
    unittest.main()
