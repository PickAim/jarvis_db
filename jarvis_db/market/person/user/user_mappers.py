from jorm.market.person import User

from jarvis_db import schemas
from jarvis_db.core.mapper import Mapper


class UserJormToTableMapper(Mapper[User, schemas.User]):
    def map(self, value: User) -> schemas.User:
        db_user = schemas.User(name=value.name, profit_tax=0, status=value.privilege)
        if value.user_id > 0:
            db_user.id = value.user_id
        return db_user


class UserTableToJormMapper(Mapper[schemas.User, User]):
    def map(self, value: schemas.User) -> User:
        return User(
            user_id=value.id,
            name=value.name,
            privilege=value.status,
            profit_tax=value.profit_tax,
            marketplace_keys={
                key_record.marketplace_id: key_record.api_key
                for key_record in value.marketplace_api_keys
            },
        )
