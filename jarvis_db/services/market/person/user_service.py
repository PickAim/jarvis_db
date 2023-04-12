from jorm.market.person import User as UserEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.person import UserRepository
from jarvis_db.tables import User


class UserService:
    def __init__(
            self,
            user_repository: UserRepository,
            table_mapper: Mapper[User, UserEntity]
    ):
        self.__user_repository = user_repository
        self.__table_mapper = table_mapper

    def create(self, user_entity: UserEntity, account_id: int):
        user = User(
            name=user_entity.name,
            profit_tax=0,
            account_id=account_id
        )
        self.__user_repository.add(user)

    def find_by_id(self, user_id: int) -> UserEntity:
        user = self.__user_repository.find_by_id(user_id)
        return self.__table_mapper.map(user)

    def find_by_account_id(self, account_id: int) -> tuple[UserEntity, int]:
        user = self.__user_repository.find_by_account_id(account_id)
        return self.__table_mapper.map(user), user.id

    def find_all(self) -> dict[int, UserEntity]:
        users = self.__user_repository.find_all()
        return {user.id: self.__table_mapper.map(user) for user in users}
