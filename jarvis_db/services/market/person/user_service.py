from jorm.market.person import User as UserEntity
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import Account, User
from jarvis_db.schemas import users_to_products


class UserService:
    def __init__(self, session: Session, table_mapper: Mapper[User, UserEntity]):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(self, user_entity: UserEntity, account_id: int):
        user = User(
            name=user_entity.name,
            profit_tax=user_entity.profit_tax,
            account_id=account_id,
            status=user_entity.privilege,
        )
        self.__session.add(user)
        self.__session.flush()

    def find_by_id(self, user_id: int) -> UserEntity | None:
        user = self.__session.execute(
            select(User).join(User.account).where(User.id == user_id)
        ).scalar_one_or_none()
        return self.__table_mapper.map(user) if user is not None else None

    def find_by_account_id(self, account_id: int) -> tuple[UserEntity, int] | None:
        user = self.__session.execute(
            select(User).join(User.account).where(User.account_id == account_id)
        ).scalar_one_or_none()
        return (self.__table_mapper.map(user), user.id) if user is not None else None

    def find_all(self) -> dict[int, UserEntity]:
        users = self.__session.execute(select(User).join(User.account)).scalars().all()
        return {user.id: self.__table_mapper.map(user) for user in users}

    def append_product(self, user_id: int, product_id: int):
        self.__session.execute(
            insert(users_to_products).values(user_id=user_id, product_id=product_id)
        )
        self.__session.flush()

    def remove_product(self, user_id: int, product_id: int):
        self.__session.execute(
            delete(users_to_products)
            .where(users_to_products.columns.user_id == user_id)
            .where(users_to_products.columns.product_id == product_id)
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
