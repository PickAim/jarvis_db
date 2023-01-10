from jarvis_calc.database_interactors.db_access import DBAccessProvider
from jorm.market.person import Client


class ConcreteDBAccessProvider(DBAccessProvider):
    def get_client(self) -> Client:
        pass

    # TODO create me

