from sqlalchemy.orm import Session
from sqlalchemy import func
from jorm.market.infrastructure import Category
from jorm.market.infrastructure import Niche
from jorm.market.infrastructure import HandlerType
from jarvis_db import tables


class NicheRepository:
    def __init__(self, session: Session):
        self.__session = session

    def add_by_category_name(self, niche: Niche, category_name: str):
        category: tables.Category = self.__session.query(tables.Category)\
            .outerjoin(tables.Category.niches)\
            .filter(tables.Category.name == category_name)\
            .one()
        category.niches.append(tables.Niche(
            name=niche.name,
            matketplace_commission=int(
                niche.commissions[HandlerType.MARKETPLACE] * 100),
            client_commission=int(
                niche.commissions[HandlerType.CLIENT] * 100),
            partial_client_commission=int(
                niche.commissions[HandlerType.PARTIAL_CLIENT] * 100),
            return_percent=int(niche.returned_percent * 100)
        ))


class CategoryRepository:
    def __init__(self, session: Session):
        self.__session = session

    def add(self, category: Category):
        db_niches = [
            tables.Niche(
                name=niche.name,
                matketplace_commission=int(
                    niche.commissions[HandlerType.MARKETPLACE] * 100),
                client_commission=int(
                    niche.commissions[HandlerType.CLIENT] * 100),
                partial_client_commission=int(
                    niche.commissions[HandlerType.PARTIAL_CLIENT] * 100),
                return_percent=int(niche.returned_percent * 100)
            ) for niche in category.niches.values()
        ]
        db_category = tables.Category(
            name=category.name,
            niches=db_niches
        )
        self.__session.add(db_category)

    def fetch_all(self) -> list[Category]:
        db_categories: list[tables.Category] = self.__session.query(tables.Category).\
            join(tables.Category.niches).all()
        categories = [Category(
            category.name,
            {niche.name: Niche(
                name=niche.name,
                commissions={
                    HandlerType.MARKETPLACE: float(
                        niche.matketplace_commission / 100),
                    HandlerType.CLIENT: float(
                        niche.client_commission / 100),
                    HandlerType.PARTIAL_CLIENT: float(
                        niche.partial_client_commission / 100)
                },
                returned_percent=float(niche.return_percent / 100),
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
