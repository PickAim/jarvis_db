from jorm.market.infrastructure import Category, Niche

from jarvis_db import tables
from jarvis_db.core import Mapper


class CategoryJormToTableMapper(Mapper[Category, tables.Category]):
    def __init__(self, niche_jorm_mapper: Mapper[Niche, tables.Niche]):
        self.__niche_jorm_mapper = niche_jorm_mapper

    def map(self, value: Category) -> tables.Category:
        db_niches = [
            self.__niche_jorm_mapper.map(niche) for niche in value.niches.values()
        ]
        return tables.Category(name=value.name, niches=db_niches)


class CategoryTableToJormMapper(Mapper[tables.Category, Category]):
    def __init__(self, niche_table_mapper: Mapper[tables.Niche, Niche]):
        self.__niche_table_mapper = niche_table_mapper

    def map(self, value: tables.Category) -> Category:
        niches = [self.__niche_table_mapper.map(niche) for niche in value.niches]
        return Category(name=value.name, niches={niche.name: niche for niche in niches})
