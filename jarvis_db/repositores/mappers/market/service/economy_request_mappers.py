from jorm.market.service import EconomyRequest

from jarvis_db import tables
from jarvis_db.core.mapper import Mapper


class EconomyRequestJormToTableMapper(Mapper[EconomyRequest, tables.EconomyRequest]):
    def map(self, value: EconomyRequest) -> tables.EconomyRequest:
        return tables.EconomyRequest(
            date=value.date,
            prime_cost=value.prime_cost,
            transit_cost=value.transit_cost,
            transit_count=value.transit_count,
        )


class EconomyRequestTableToJormMapper(Mapper[tables.EconomyRequest, EconomyRequest]):
    def map(self, value: tables.EconomyRequest) -> EconomyRequest:
        return EconomyRequest(
            date=value.date,
            niche_name=value.niche.name,
            transit_cost=value.transit_cost,
            transit_count=value.transit_count,
            pack_cost=0,
            prime_cost=value.prime_cost
        )
