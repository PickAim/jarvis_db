from jorm.jarvis.db_access import UserInfoCollector
from jorm.market.person import Account, User
from jorm.server.token.types import TokenType

from jarvis_db.services.market.person.account_service import AccountService
from jarvis_db.services.market.person.user_service import UserService


class UserInfoCollectorImpl(UserInfoCollector):
    def __init__(self, account_service: AccountService, user_service: UserService):
        self.__account_service = account_service
        self.__user_service = user_service

    def get_user_by_account(self, account: Account) -> User:
        _, account_id = self.__account_service.find_by_email(account.email)
        user, _ = self.__user_service.find_by_account_id(account_id)
        return user

    def get_user_by_id(self, user_id: int) -> User:
        return self.__user_service.find_by_id(user_id)

    def get_account(self, login: str) -> Account:
        account, _ = self.__account_service.find_by_email(login)
        return account

    def get_token_rnd_part(self, user_id: int, imprint: str, token_type: TokenType) -> str:
        # TODO
        return super().get_token_rnd_part(user_id, imprint, token_type)
