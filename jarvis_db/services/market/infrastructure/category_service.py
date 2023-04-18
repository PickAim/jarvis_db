from typing import Iterable

from jorm.market.infrastructure import Category as CategoryEntity

from jarvis_db.core.mapper import Mapper
from jarvis_db.repositores.market.infrastructure.category_repository import \
    CategoryRepository
from jarvis_db.tables import Category


class CategoryService:
    def __init__(
            self,
            category_repository: CategoryRepository,
            table_mapper: Mapper[Category, CategoryEntity]
    ):
        self.__category_repository = category_repository
        self.__table_mapper = table_mapper

    def create(self, category_entity: CategoryEntity, marketplace_id: int):
        category = Category(name=category_entity.name,
                            marketplace_id=marketplace_id)
        self.__category_repository.add(category)

    def create_all(self, category_entities: Iterable[CategoryEntity], marketplace_id: int):
        for category in category_entities:
            self.create(category, marketplace_id)

    def find_by_name(self, name: str, marketplace_id: int) -> tuple[CategoryEntity, int]:
        category = self.__category_repository.find_by_name(
            name, marketplace_id)
        return self.__table_mapper.map(category), category.id

    def find_all_in_marketplace(self, marketplace_id: int) -> dict[int, CategoryEntity]:
        categories = self.__category_repository.find_all_in_marketplace(
            marketplace_id)
        return {category.id: self.__table_mapper.map(category) for category in categories}
    
    def exists_with_name(self, name: str, marketplace_id: int) -> bool:
        return self.__category_repository.exists_with_name(name, marketplace_id)
