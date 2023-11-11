from jorm.market.person import Account as AccountEntity
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.market.person.account.account_input_formatter import AccountInputFormatter
from jarvis_db.schemas import Account


class AccountService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[Account, AccountEntity],
        input_formatter: AccountInputFormatter,
    ):
        self.__session = session
        self.__table_mapper = table_mapper
        self.__input_formatter = input_formatter

    def create(self, account_entity: AccountEntity) -> int:
        account = Account(
            email=account_entity.email if account_entity.email else None,
            phone=self.__input_formatter.format_phone_number(
                account_entity.phone_number
            )
            if account_entity.phone_number
            else None,
            password=account_entity.hashed_password,
        )
        self.__session.add(account)
        self.__session.flush()
        return account.id

    def find_by_id(self, account_id: int) -> AccountEntity | None:
        account = self.__session.execute(
            select(Account).where(Account.id == account_id)
        ).scalar_one_or_none()
        return self.__table_mapper.map(account) if account is not None else None

    def find_by_email(self, email: str) -> tuple[AccountEntity, int] | None:
        account = self.__session.execute(
            select(Account).where(Account.email == email)
        ).scalar_one_or_none()
        return (
            (self.__table_mapper.map(account), account.id)
            if account is not None
            else None
        )

    def find_by_phone(self, phone: str) -> tuple[AccountEntity, int] | None:
        account = self.__session.execute(
            select(Account).where(Account.phone == phone)
        ).scalar_one_or_none()
        return (
            (self.__table_mapper.map(account), account.id)
            if account is not None
            else None
        )

    def find_by_email_or_phone(
        self, email: str = "", phone: str = ""
    ) -> tuple[AccountEntity, int] | None:
        account = self.__session.execute(
            select(Account).where(
                or_(
                    Account.email == email,
                    Account.phone == self.__input_formatter.format_phone_number(phone),
                )
            )
        ).scalar_one_or_none()
        return (
            (self.__table_mapper.map(account), account.id)
            if account is not None
            else None
        )

    def find_all(self) -> dict[int, AccountEntity]:
        accounts = self.__session.execute(select(Account)).scalars().all()
        return {account.id: self.__table_mapper.map(account) for account in accounts}
