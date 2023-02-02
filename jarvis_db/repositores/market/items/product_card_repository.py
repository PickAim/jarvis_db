from sqlalchemy.orm import Session
from jorm.market.infrastructure import Niche
from jorm.market.items import Product


class ProductCardRepository:
    def __init__(self, session: Session):
        self.__session = session

    def add_product_to_niche(self, product: Product, niche: Niche):
        pass
