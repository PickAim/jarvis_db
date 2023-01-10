from abc import ABC
from jarvis_calc.database_interactors.db_access import DBUpdateProvider
from jorm.market.service import Request


class DataBaseUpdater(ABC):
    pass


class CalcUpdater(DBUpdateProvider):
    def save_request(self, request: Request) -> None:
        pass

    # TODO create me
