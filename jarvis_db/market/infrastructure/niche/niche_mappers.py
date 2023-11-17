from jorm.market.infrastructure import HandlerType, Niche, Product

from jarvis_db import schemas
from jarvis_db.core import Mapper


class NicheJormToTableMapper(Mapper[Niche, schemas.Niche]):
    def map(self, value: Niche) -> schemas.Niche:
        return schemas.Niche(
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


class NicheTableToJormMapper(Mapper[schemas.Niche, Niche]):
    def __init__(
        self,
        product_mapper: Mapper[schemas.ProductCard, Product],
    ):
        self.__product_mapper = product_mapper

    def map(self, value: schemas.Niche) -> Niche:
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
            _products=[
                self.__product_mapper.map(product) for product in value.products
            ],
        )
