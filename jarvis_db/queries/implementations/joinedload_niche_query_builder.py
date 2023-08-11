from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from jarvis_db.queries.niche_query_builder import NicheLoadBuilder
from jarvis_db.queries.product_query_builer import ProductCardLoadBuilder
from jarvis_db.schemas import Niche


class JoinedLoadNicheLoadBuilder(NicheLoadBuilder):
    def __init__(self, product_loader: ProductCardLoadBuilder):
        self.__product_loader = product_loader

    def load_products(self) -> _AbstractLoad:
        return self.__product_loader.load_atomic(joinedload(Niche.products))
