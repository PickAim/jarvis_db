from sqlalchemy import or_, select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Account


class AccountRepository(AlchemyRepository[Account]):
    def find_by_email(self, email: str) -> Account | None:
        return self._session.execute(
            select(Account).where(Account.email == email).where(Account.email != "")
        ).scalar_one_or_none()

    def find_by_phone(self, phone: str) -> Account | None:
        return self._session.execute(
            select(Account).where(Account.phone == phone).where(Account.phone != "")
        ).scalar_one_or_none()

    def find_by_email_or_phone(self, email: str, phone: str) -> Account | None:
        return self._session.execute(
            select(Account).where(or_(Account.email == email, Account.phone == phone))
        ).scalar_one_or_none()

    def find_all(self) -> list[Account]:
        db_accounts = self._session.execute(select(Account)).scalars().all()
        return list(db_accounts)
