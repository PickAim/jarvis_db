from sqlalchemy.orm import Session
from jorm.market.infrastructure import Category
from jorm.market.infrastructure import Niche
from jarvis_db import tables

class NicheRepository:
    def addNiche(niche: Niche):
        pass

class CategoryRepository:
    def __init__(self, session: Session):
        self.__session = session
    
    def add(self, category: Category):
        db_niches = [
            tables.Niche(
                name=niche.name.lower(),
                commission=int(niche.commission * 100),
                return_percent=int(niche.returned_percent * 100)
            ) for niche in category.niches.values()
        ]
        db_category = tables.Category(
            name=category.name,
            niches=db_niches
        )
        self.__session.add(db_category)

class AddressRepository:
    pass

class WarehouseRepository:
    pass

class MarketPlaceRepository:
    pass

