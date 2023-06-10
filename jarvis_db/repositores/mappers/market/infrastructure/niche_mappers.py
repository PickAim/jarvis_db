from jorm.market.infrastructure import HandlerType, Niche

from jarvis_db import tables
from jarvis_db.core import Mapper


class NicheJormToTableMapper(Mapper[Niche, tables.Niche]):
    def map(self, value: Niche) -> tables.Niche:
        return tables.Niche(
            name=value.name,
            marketplace_commission=int(
                value.commissions[HandlerType.MARKETPLACE] * 100
            ),
            partial_client_commission=int(
                value.commissions[HandlerType.PARTIAL_CLIENT] * 100
            ),
            client_commission=int(value.commissions[HandlerType.CLIENT] * 100),
            return_percent=int(value.returned_percent * 100),
        )


class NicheTableToJormMapper(Mapper[tables.Niche, Niche]):
    def map(self, value: tables.Niche) -> Niche:
        return Niche(
            name=value.name,
            commissions={
                HandlerType.MARKETPLACE: float(value.marketplace_commission / 100),
                HandlerType.PARTIAL_CLIENT: float(
                    value.partial_client_commission / 100
                ),
                HandlerType.CLIENT: float(value.client_commission / 100),
            },
            returned_percent=float(value.return_percent / 100),
        )
