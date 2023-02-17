from jorm.market.person import User

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class UserJormToTableMapper(Mapper[User, tables.User]):
    def map(self, value: User) -> tables.User:
        db_user = tables.User(
            name=value.name,
            profit_tax=0
        )
        if value.user_id > 0:
            db_user.id = value.user_id
        return db_user


class UserTableToJormMapper(Mapper[tables.User, User]):
    def map(self, value: tables.User) -> User:
        return User(
            user_id=value.id,
            name=value.name
        )
