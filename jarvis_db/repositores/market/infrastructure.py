from sqlalchemy.orm import Session
from jorm.market.infrastructure import Category
from jorm.market.infrastructure import Niche
from jarvis_db import tables


class NicheRepository:
    def add(niche: Niche):
        pass


class CategoryRepository:
    def __init__(self, session: Session):
        self.__session = session

    def add(self, category: Category):
        db_niches = [
            tables.Niche(
                name=niche.name,
                commission=int(niche.commission * 100),
                return_percent=int(niche.returned_percent * 100)
            ) for niche in category.niches.values()
        ]
        db_category = tables.Category(
            name=category.name,
            niches=db_niches
        )
        self.__session.add(db_category)

    def fetch_all(self) -> list[Category]:
        db_categories = self.__session.query(tables.Category).\
            join(tables.Category.niches).all()
        categories = [Category(
            category.name,
            {niche.name: Niche(
                name=niche.name,
                commission=float(niche.commission / 100),
                returned_percent=float(niche.return_percent / 100),
                logistic_price=0,
                products=[]
            ) for niche in category.niches}
        ) for category in db_categories]
        return categories


class AddressRepository:
    pass


class WarehouseRepository:
    pass


class MarketPlaceRepository:
    pass
