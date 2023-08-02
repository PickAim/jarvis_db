from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.schemas import Account, User


class UserRepository(AlchemyRepository[User]):
    def find_by_id(self, user_id: int) -> User:
        return self._session.execute(
            select(User).join(User.account).where(User.id == user_id)
        ).scalar_one()

    def find_by_account_id(self, account_id: int) -> User:
        return self._session.execute(
            select(User).join(User.account).where(Account.id == account_id)
        ).scalar_one()

    def find_all(self) -> list[User]:
        db_users = self._session.execute(select(User).join(Account)).scalars().all()
        return list(db_users)
