from jorm.market.person import User as UserEntity, Warehouse as WarehouseEntity
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, selectinload, joinedload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import Account, MarketplaceApiKey, User, UserToWarehouse
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
                .options(
                    joinedload(User.account), joinedload(User.marketplace_api_keys)
                )
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
                .options(
                    joinedload(User.account), joinedload(User.marketplace_api_keys)
                )
                .where(User.account_id == account_id)
            )
            .unique()
            .scalar_one_or_none()
        )
        return (self.__table_mapper.map(user), user.id) if user is not None else None

    def find_all(self) -> dict[int, UserEntity]:
        users = (
            self.__session.execute(
                select(User).options(
                    joinedload(User.account), selectinload(User.marketplace_api_keys)
                )
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

    # def append_product(self, user_id: int, product_id: int):
    #     self.__session.execute(
    #         insert(users_to_products).values(user_id=user_id, product_id=product_id)
    #     )
    #     self.__session.flush()

    # def remove_product(self, user_id: int, product_id: int):
    #     self.__session.execute(
    #         delete(users_to_products)
    #         .where(users_to_products.columns.user_id == user_id)
    #         .where(users_to_products.columns.product_id == product_id)
    #     )
    #     self.__session.flush()

    # def append_warehouse(self, user_id: int, warehouse_id: int):
    #     self.__session.add(UserToWarehouse(user_id=user_id, warehouse_id=warehouse_id))
    #     self.__session.flush()

    # def remove_warehouse(self, user_id: int, warehouse_id: int):
    #     self.__session.execute(
    #         delete(UserToWarehouse)
    #         .where(UserToWarehouse.user_id == user_id)
    #         .where(UserToWarehouse.warehouse_id == warehouse_id)
    #     )
    #     self.__session.flush()

    # def fetch_user_warehouses(self, user_id: int) -> dict[int, WarehouseEntity]:
    #     return {}

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
