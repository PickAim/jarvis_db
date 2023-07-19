from typing import Iterable

from jorm.market.infrastructure import Category as CategoryEntity
from sqlalchemy import select
from sqlalchemy.orm import Session

from jarvis_db.core.mapper import Mapper
from jarvis_db.tables import Category, Niche


class CategoryService:
    def __init__(
        self,
        session: Session,
        table_mapper: Mapper[Category, CategoryEntity],
    ):
        self.__session = session
        self.__table_mapper = table_mapper

    def create(self, category_entity: CategoryEntity, marketplace_id: int):
        self.__session.add(
            CategoryService.__create_category_record(category_entity, marketplace_id)
        )

    def create_all(
        self, category_entities: Iterable[CategoryEntity], marketplace_id: int
    ):
        self.__session.add_all(
            (
                CategoryService.__create_category_record(category, marketplace_id)
                for category in category_entities
            )
        )

    def find_by_name(
        self, name: str, marketplace_id: int
    ) -> tuple[CategoryEntity, int] | None:
        category = self.__session.execute(
            select(Category)
            .where(Category.marketplace_id == marketplace_id)
            .where(Category.name.ilike(name))
        ).scalar_one_or_none()
        return (
            (self.__table_mapper.map(category), category.id)
            if category is not None
            else None
        )

    def find_all_in_marketplace(self, marketplace_id: int) -> dict[int, CategoryEntity]:
        categories = (
            self.__session.execute(
                select(Category).where(Category.marketplace_id == marketplace_id)
            )
            .scalars()
            .all()
        )
        return {
            category.id: self.__table_mapper.map(category) for category in categories
        }

    def fetch_all_in_marketplace_atomic(
        self, marketplace_id
    ) -> dict[int, CategoryEntity]:
        categories = (
            self.__session.execute(
                select(Category)
                .join(Category.niches)
                .join(Niche.products)
                .where(Category.marketplace_id == marketplace_id)
            )
            .scalars()
            .all()
        )
        return {
            category.id: self.__table_mapper.map(category) for category in categories
        }

    def exists_with_name(self, name: str, marketplace_id: int) -> bool:
        category_id = self.__session.execute(
            select(Category.id)
            .where(Category.marketplace_id == marketplace_id)
            .where(Category.name.ilike(name))
        ).scalar_one_or_none()
        return category_id is not None

    def filter_existing_names(self, names: Iterable[str], marketplace_id) -> list[str]:
        names = list(names)
        existing_names = (
            self.__session.execute(
                select(Category.name)
                .where(Category.marketplace_id == marketplace_id)
                .where(Category.name.in_(names))
            )
            .scalars()
            .all()
        )
        return list(set(names) - set(existing_names))

    @staticmethod
    def __create_category_record(
        category: CategoryEntity, marketplace_id: int
    ) -> Category:
        return Category(name=category.name, marketplace_id=marketplace_id)
