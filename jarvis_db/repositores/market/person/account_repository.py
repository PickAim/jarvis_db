from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Account


class AccountRepository(AlchemyRepository[Account]):

    def find_by_email(self, email: str) -> Account:
        return self._session.execute(
            select(Account)
            .where(Account.email == email)
        ).scalar_one()

    def find_by_phone(self, phone: str) -> Account:
        return self._session.execute(
            select(Account)
            .where(Account.phone == phone)
        ).scalar_one()

    def find_all(self) -> list[Account]:
        db_accounts = self._session.execute(
            select(Account)
        ).scalars().all()
        return list(db_accounts)
