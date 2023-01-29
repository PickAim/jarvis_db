from jorm.market.infrastructure import Marketplace

from jarvis_db import tables
from jarvis_db.core import Mapper


class MarketplaceJormToTableMapper(Mapper[Marketplace, tables.Marketplace]):
    def map(self, value: Marketplace) -> tables.Marketplace:
        return tables.Marketplace(name=value.name)


class MarketplaceTableToJormMapper(Mapper[tables.Marketplace, Marketplace]):
    def map(self, value: tables.Marketplace) -> Marketplace:
        return Marketplace(value.name, [])
