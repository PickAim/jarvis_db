from typing import Iterable, TypedDict

from jorm.market.items import Product
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, joinedload, noload

from jarvis_db.core.mapper import Mapper
from jarvis_db.schemas import (
    Category,
    Leftover,
    Niche,
    ProductCard,
    ProductHistory,
    ProductToNiche,
)
from jarvis_db.market.items.product_card_history.product_history_service import (
    ProductHistoryService,
)


class _ProductTypedDict(TypedDict):
    name: str
    global_id: int
    cost: int
    rating: int
    brand: str
    seller: str


class ProductCardService:
    __load_options = [
        noload(ProductCard.histories),
        joinedload(ProductCard.niches)
        .joinedload(Niche.category)
        .load_only(Category.name),
    ]

    def __init__(
        self,
        session: Session,
        history_service: ProductHistoryService,
        table_mapper: Mapper[ProductCard, Product],
    ):
        self.__session = session
        self.__table_mapper = table_mapper
        self.__history_service = history_service

    def create_product(self, product: Product, niche_ids: Iterable[int]) -> int:
        db_product = ProductCard(
            **ProductCardService.__map_entity_to_typed_dict(product)
        )
        with self.__session.begin_nested():
            self.__session.add(db_product)
            if niche_ids:
                self.__session.flush()
                self.__session.add_all(
                    (
                        ProductToNiche(product_id=db_product.id, niche_id=niche_id)
                        for niche_id in niche_ids
                    )
                )
            self.__history_service.create(product.history, db_product.id)
            self.__session.flush()
            return db_product.id

    def create_products(self, products: Iterable[Product], niche_ids: Iterable[int]):
        db_products = [
            ProductCard(**ProductCardService.__map_entity_to_typed_dict(product))
            for product in products
        ]
        with self.__session.begin_nested():
            self.__session.add_all(db_products)
            if niche_ids:
                self.__session.flush()
                self.__session.add_all(
                    (
                        ProductToNiche(product_id=product.id, niche_id=niche_id)
                        for product in db_products
                        for niche_id in niche_ids
                    )
                )
            self.__session.flush()
            for db_product, product in zip(db_products, products, strict=True):
                self.__history_service.create(product.history, db_product.id)
            self.__session.flush()

    def upsert_product(self, product: Product, niche_ids: Iterable[int]):
        found_product = self.__session.execute(
            select(ProductCard).where(ProductCard.global_id == product.global_id)
        ).scalar_one_or_none()
        if found_product is None:
            self.create_product(product, niche_ids)
        else:
            self.__session.add_all(
                (
                    ProductToNiche(product_id=found_product.id, niche_id=niche_id)
                    for niche_id in niche_ids
                )
            )
            self.__session.flush()

    def find_by_id(self, product_id: int) -> Product | None:
        product = (
            self.__session.execute(
                select(ProductCard)
                .where(ProductCard.id == product_id)
                .options(*ProductCardService.__load_options)
            )
            .unique()
            .scalar_one_or_none()
        )
        return self.__table_mapper.map(product) if product is not None else None

    def find_by_id_atomic(self, product_id: int) -> Product | None:
        product = (
            self.__session.execute(
                select(ProductCard)
                .where(ProductCard.id == product_id)
                .distinct(ProductCard.id)
                .options(
                    joinedload(ProductCard.niches).joinedload(
                        Niche.category, innerjoin=True
                    ),
                    joinedload(ProductCard.histories)
                    .joinedload(ProductHistory.leftovers)
                    .joinedload(Leftover.warehouse, innerjoin=True),
                )
            )
            .unique()
            .scalar_one_or_none()
        )
        return self.__table_mapper.map(product) if product is not None else None

    def find_by_global_id(
        self, global_id: int, niche_id: int
    ) -> tuple[Product, int] | None:
        product = (
            self.__session.execute(
                select(ProductCard)
                .join(ProductCard.niches)
                .where(ProductCard.global_id == global_id)
                .where(Niche.id == niche_id)
                .options(*ProductCardService.__load_options)
            )
            .unique()
            .scalar_one_or_none()
        )
        return (
            (self.__table_mapper.map(product), product.id)
            if product is not None
            else None
        )

    def find_id_by_global_id(self, global_id: int, niche_id: int) -> int | None:
        return (
            self.__session.execute(
                select(ProductCard.id)
                .join(ProductCard.niches)
                .where(ProductCard.global_id == global_id)
                .where(Niche.id == niche_id)
            )
            .unique()
            .scalar_one_or_none()
        )

    def find_all_in_niche(self, niche_id: int) -> dict[int, Product]:
        niche_products = (
            self.__session.execute(
                select(ProductCard)
                .join(ProductToNiche, ProductCard.id == ProductToNiche.product_id)
                .where(ProductToNiche.niche_id == niche_id)
                .options(*ProductCardService.__load_options)
            )
            .unique()
            .scalars()
            .all()
        )
        return {
            product.id: self.__table_mapper.map(product) for product in niche_products
        }

    def update(self, product_id: int, product: Product):
        self.__session.execute(
            update(ProductCard)
            .where(ProductCard.id == product_id)
            .values(**ProductCardService.__map_entity_to_typed_dict(product))
        )
        self.__session.flush()

    def add_niche_to_product(self, product_id: int, niche_id: int) -> None:
        self.__session.add(ProductToNiche(product_id=product_id, niche_id=niche_id))
        self.__session.flush()

    def remove_niche_from_product(self, product_id: int, niche_id: int) -> None:
        self.__session.execute(
            delete(ProductToNiche).where(
                ProductToNiche.product_id == product_id,
                ProductToNiche.niche_id == niche_id,
            )
        )
        self.__session.flush()

    def filter_existing_global_ids(
        self, niche_id: int, ids: Iterable[int]
    ) -> list[int]:
        ids = list(ids)
        existing_ids = (
            self.__session.execute(
                select(ProductCard.global_id)
                .join(ProductCard.niches)
                .where(Niche.id == niche_id)
                .where(ProductCard.global_id.in_(ids))
            )
            .scalars()
            .all()
        )
        return list(set(ids) - set(existing_ids))

    @staticmethod
    def __map_entity_to_typed_dict(product: Product) -> _ProductTypedDict:
        return _ProductTypedDict(
            name=product.name,
            global_id=product.global_id,
            cost=product.cost,
            rating=int(product.rating * 100),
            brand=product.brand,
            seller=product.seller,
        )
