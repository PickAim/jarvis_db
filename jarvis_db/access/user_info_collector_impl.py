from jorm.jarvis.db_access import UserInfoCollector
from jorm.market.person import Account, User
from jorm.server.token.types import TokenType

from jarvis_db.repositores.market.person import (AccountRepository,
                                                 UserRepository)


class UserInfoCollectorImpl(UserInfoCollector):
    def __init__(self, account_repository: AccountRepository, user_repository: UserRepository):
        self.__account_repository = account_repository
        self.__user_repository = user_repository

    def get_user_by_account(self, account: Account) -> User:
        user, _ = self.__user_repository.find_by_account(account)
        return user

    def get_user_by_id(self, user_id: int) -> User:
        user, _ = self.__user_repository.find_by_id(user_id)
        return user

    def get_account(self, login: str) -> Account:
        account, _ = self.__account_repository.find_by_email(login)
        return account

    def get_token_rnd_part(self, user_id: int, imprint: str, token_type: TokenType) -> str:
        # TODO
        return super().get_token_rnd_part(user_id, imprint, token_type)
