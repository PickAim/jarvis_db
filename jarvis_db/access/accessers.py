from jarvis_calc.database_interactors.db_access import DBAccessProvider

from jorm.market.infrastructure import Warehouse, Niche
from jorm.market.person import Client, User


class ConcreteDBAccessProvider(DBAccessProvider):
    def get_current_user(self) -> User:
        pass

    def get_current_client(self) -> Client:
        pass

    def get_niche(self, niche_name: str) -> Niche:
        pass

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        pass

    def get_all_warehouses(self) -> list[Warehouse]:
        pass

    # TODO create me
