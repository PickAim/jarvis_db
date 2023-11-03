from jorm.market.person import User as UserEntity
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import Account, MarketplaceApiKey, User


class UserService:
    __user_select_options = [
        joinedload(User.account),
        joinedload(User.marketplace_api_keys),
    ]

    def __init__(self, session: Session, table_mapper: Mapper[User, UserEntity]):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(self, user_entity: UserEntity, account_id: int):
        user = User(
            name=user_entity.name,
            profit_tax=user_entity.profit_tax,
            account_id=account_id,
            status=user_entity.privilege,
            marketplace_api_keys=[
                MarketplaceApiKey(marketplace_id=marketplace_id, api_key=key)
                for marketplace_id, key in user_entity.marketplace_keys.items()
            ],
        )
        self.__session.add(user)
        self.__session.flush()

    def find_by_id(self, user_id: int) -> UserEntity | None:
        user = (
            self.__session.execute(
                select(User)
                .options(*UserService.__user_select_options)
                .where(User.id == user_id)
            )
            .unique()
            .scalar_one_or_none()
        )
        return self.__table_mapper.map(user) if user is not None else None

    def find_by_account_id(self, account_id: int) -> tuple[UserEntity, int] | None:
        user = (
            self.__session.execute(
                select(User)
                .options(*UserService.__user_select_options)
                .where(User.account_id == account_id)
                .distinct(User.id)
            )
            .unique()
            .scalar_one_or_none()
        )
        return (self.__table_mapper.map(user), user.id) if user is not None else None

    def find_all(self) -> dict[int, UserEntity]:
        users = (
            self.__session.execute(
                select(User)
                .options(*UserService.__user_select_options)
                .distinct(User.id)
            )
            .scalars()
            .unique()
            .all()
        )
        return {user.id: self.__table_mapper.map(user) for user in users}

    def append_api_key(self, user_id: int, api_key: str, marketplace_id: int):
        self.__session.add(
            MarketplaceApiKey(
                user_id=user_id, marketplace_id=marketplace_id, api_key=api_key
            )
        )
        self.__session.flush()

    def remove_api_key(self, user_id: int, marketplace_id: int):
        self.__session.execute(
            delete(MarketplaceApiKey)
            .where(MarketplaceApiKey.user_id == user_id)
            .where(MarketplaceApiKey.marketplace_id == marketplace_id)
        )
        self.__session.flush()

    def delete(self, user_id: int):
        self.__session.execute(
            delete(Account).where(
                Account.id
                == select(Account.id)
                .join(User.account)
                .where(User.id == user_id)
                .scalar_subquery()
            )
        )
        self.__session.flush()
