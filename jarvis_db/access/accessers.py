from jarvis_calc.database_interactors.db_access import DBAccessProvider

from jorm.market.infrastructure import Warehouse, Niche
from jorm.market.person import User, Account
from jorm.server.token.types import TokenType


class ConcreteDBAccessProvider(DBAccessProvider):
    def get_token_rnd_part(self, user_id: int, imprint: str, token_type: TokenType) -> str:
        pass

    def get_user_by_account(self, account: Account) -> User:
        pass

    def get_user_by_id(self, user_id: int) -> User:
        pass

    def get_account(self, login: str) -> Account:
        pass

    def get_niche(self, niche_name: str) -> Niche:
        pass

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        pass

    def get_all_warehouses(self) -> list[Warehouse]:
        pass

    # TODO create me
