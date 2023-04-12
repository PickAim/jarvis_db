from jorm.market.person import Account as AccountEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.person.account_repository import \
    AccountRepository
from jarvis_db.tables import Account


class AccountService:
    def __init__(
            self,
            account_repository: AccountRepository,
            table_mapper: Mapper[Account, AccountEntity]
    ):
        self.__account_repository = account_repository
        self.__table_mapper = table_mapper

    def create(self, account_entity: AccountEntity):
        self.__account_repository.add(Account(
            email=account_entity.email,
            phone=account_entity.phone_number,
            password=account_entity.hashed_password
        ))

    def find_by_email(self, email: str) -> tuple[AccountEntity, int]:
        account = self.__account_repository.find_by_email(email)
        return self.__table_mapper.map(account), account.id

    def find_all(self) -> dict[int, AccountEntity]:
        accounts = self.__account_repository.find_all()
        return {account.id: self.__table_mapper.map(account) for account in accounts}
