from sqlalchemy import select

from jarvis_db.repositores.alchemy_repository import AlchemyRepository
from jarvis_db.tables import Category, Niche, ProductCard


class ProductCardRepository(AlchemyRepository[ProductCard]):

    def find_by_id(self, product_id: int) -> ProductCard:
        return self._session.execute(
            select(ProductCard)
            .join(ProductCard.niche)
            .join(Niche.category)
            .join(Category.marketplace)
            .where(ProductCard.id == product_id)
        ).scalar_one()

    def find_all_in_niche(self, niche_id: int) -> list[ProductCard]:
        products = self._session.execute(
            select(ProductCard)
            .where(ProductCard.niche_id == niche_id)
        ).scalars().all()
        return list(products)
