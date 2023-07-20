from jorm.jarvis.db_access import UserInfoCollector
from jorm.market.person import Account, User
from jorm.server.token.types import TokenType

from jarvis_db.services.market.person.account_service import AccountService
from jarvis_db.services.market.person.token_service import TokenService
from jarvis_db.services.market.person.user_service import UserService


class UserInfoCollectorImpl(UserInfoCollector):
    def __init__(
        self,
        account_service: AccountService,
        user_service: UserService,
        token_service: TokenService,
    ):
        self.__account_service = account_service
        self.__user_service = user_service
        self.__token_service = token_service

    def get_user_by_account(self, account: Account) -> User:
        user_result = self.__account_service.find_by_email_or_phone(
            account.email, account.phone_number
        )
        if user_result is None:
            raise Exception(
                f"No account with {account.email} or "
                f"phone {account.phone_number} is found"
            )
        _, account_id = user_result
        user, _ = self.__user_service.find_by_account_id(account_id)
        return user

    def get_account_and_id(self, email: str, phone: str) -> tuple[Account, int] | None:
        return self.__account_service.find_by_email_or_phone(email, phone)

    def get_user_by_id(self, user_id: int) -> User:
        return self.__user_service.find_by_id(user_id)

    def get_token_rnd_part(
        self, user_id: int, imprint: str, token_type: TokenType
    ) -> str:
        access, refresh = self.__token_service.find_by_imprint(user_id, imprint)
        return access if token_type == TokenType.ACCESS else refresh
