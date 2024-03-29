from jorm.jarvis.db_update import JORMChanger
from jorm.market.infrastructure import Category, Niche, Warehouse, HandlerType
from jorm.market.items import Product, ProductHistory
from jorm.market.service import SimpleEconomySaveObject, TransitEconomySaveObject
from jorm.server.providers.providers import (
    DataProviderWithoutKey,
    UserMarketDataProvider,
)
from jorm.support.calculation import (
    GreenTradeZoneCalculateResult,
    NicheCharacteristicsCalculateResult,
)
from jorm.support.types import EconomyConstants

from jarvis_db.access.fill.fillers import StandardDbFiller
from jarvis_db.cache.green_trade_zone.green_trade_zone_service import (
    GreenTradeZoneService,
)
from jarvis_db.cache.niche_characteristics.niche_characteristics_service import (
    NicheCharacteristicsService,
)
from jarvis_db.market.infrastructure.category.category_service import CategoryService
from jarvis_db.market.infrastructure.niche.niche_service import NicheService
from jarvis_db.market.items.product_card.product_card_service import ProductCardService
from jarvis_db.market.items.product_card_history.product_history_service import (
    ProductHistoryService,
)
from jarvis_db.market.person.user.user_items_service import UserItemsService
from jarvis_db.market.service.economy.economy_service import EconomyService
from jarvis_db.market.service.economy_constants.economy_constants_service import (
    EconomyConstantsService,
)
from jarvis_db.market.service.transit.transit_economy_service import (
    TransitEconomyService,
)


class JormChangerImpl(JORMChanger):
    def __init__(
        self,
        economy_constants_service: EconomyConstantsService,
        category_service: CategoryService,
        niche_service: NicheService,
        product_card_service: ProductCardService,
        product_history_service: ProductHistoryService,
        economy_service: EconomyService,
        transit_service: TransitEconomyService,
        user_items_service: UserItemsService,
        niche_characteristics_service: NicheCharacteristicsService,
        green_trade_zone_service: GreenTradeZoneService,
        data_provider_without_key: DataProviderWithoutKey,
        user_market_data_provider: UserMarketDataProvider,
        standard_filler: StandardDbFiller,
    ):
        self.__economy_constants_service = economy_constants_service
        self.__category_service = category_service
        self.__niche_service = niche_service
        self.__product_card_service = product_card_service
        self.__product_history_service = product_history_service
        self.__economy_service = economy_service
        self.__transit_service = transit_service
        self.__user_items_service = user_items_service
        self.__niche_characteristics_service = niche_characteristics_service
        self.__green_trade_zone_service = green_trade_zone_service
        self.__data_provider_without_key = data_provider_without_key
        self.__user_market_data_provider = user_market_data_provider
        self.__standard_filler = standard_filler

    def update_niche(
        self, niche_id: int, category_id: int, marketplace_id: int
    ) -> Niche | None:
        if self.__data_provider_without_key is None:
            return None
        niche = self.__niche_service.find_by_id(niche_id)
        if niche is None:
            return None
        category = self.__category_service.find_by_id(category_id)
        if category is None:
            return None
        niche_tuple = self.__niche_service.find_by_name_atomic(niche.name, category_id)
        if niche_tuple is None:
            return None
        niche, _ = niche_tuple
        return self.__update_niche(
            (niche, niche_id), category, self.__data_provider_without_key
        )

    def update_green_zone_cache(
        self, niche_id: int, green_trade_zone_calc_result: GreenTradeZoneCalculateResult
    ) -> None:
        self.__green_trade_zone_service.upsert(niche_id, green_trade_zone_calc_result)

    def update_niche_characteristics_cache(
        self,
        niche_id: int,
        niche_characteristics_calc_result: NicheCharacteristicsCalculateResult,
    ) -> None:
        self.__niche_characteristics_service.upsert(
            niche_id, niche_characteristics_calc_result
        )

    def update_economy_constants(
        self, marketplace_id: int, economy_constants: EconomyConstants
    ) -> None:
        self.__economy_constants_service.upsert_constants(
            marketplace_id, economy_constants
        )

    def save_simple_economy_request(
        self, save_object: SimpleEconomySaveObject, user_id: int
    ) -> int:
        return self.__economy_service.save_request(save_object, user_id)

    def save_transit_economy_request(
        self, save_object: TransitEconomySaveObject, user_id: int
    ) -> int:
        return self.__transit_service.save_request(save_object, user_id)

    def delete_simple_economy_request(self, request_id: int, user_id: int) -> None:
        self.__economy_service.delete(request_id)

    def delete_transit_economy_request(self, request_id: int, user_id: int) -> None:
        self.__transit_service.delete(request_id)

    # def update_all_niches(self, category_id: int, marketplace_id: int) -> None:
    #     # TODO it will be necessary to implement this method to update niche
    #     commissions as example
    #     https://github.com/PickAim/jdu/issues/55
    #     return

    def load_new_niche(self, niche_name: str, marketplace_id: int) -> Niche | None:
        if self.__data_provider_without_key is None or self.__standard_filler is None:
            return None
        return self.__standard_filler.fill_niche_by_name(
            self.__category_service,
            self.__niche_service,
            self.__product_card_service,
            self.__data_provider_without_key,
            niche_name,
        )

    def load_user_products(
        self, user_id: int, marketplace_id: int
    ) -> list[Product] | None:
        if (
            self.__user_market_data_provider is None
            or self.__data_provider_without_key is None
        ):
            return None
        user_products = self.__get_user_products(
            self.__user_market_data_provider, self.__data_provider_without_key
        )
        user_products_in_db = self.__user_items_service.fetch_user_products(
            user_id, marketplace_id
        )
        existing_products = [
            user_products_in_db[product_id] for product_id in user_products_in_db
        ]
        user_products = self.__create_and_update_user_products(
            user_id, existing_products, user_products, marketplace_id
        )
        return user_products

    def load_user_warehouses(
        self, user_id: int, marketplace_id: int
    ) -> list[Warehouse]:
        if self.__user_market_data_provider is None or self.__standard_filler is None:
            return []
        return self.__standard_filler.fill_user_warehouses(
            self.__user_market_data_provider
        )

    def load_all_warehouses(self, user_id: int, marketplace_id: int) -> list[Warehouse]:
        return self.__standard_filler.fill_all_warehouses(
            self.__data_provider_without_key
        )

    @staticmethod
    def __get_products_category_and_niche(
        products_ids: list[int], data_provider_without_key: DataProviderWithoutKey
    ) -> dict[int, tuple[str, str]]:
        result: dict[int, tuple[str, str]] = {}
        for product_id in products_ids:
            category_and_niche = data_provider_without_key.get_category_and_niche(
                product_id
            )
            if category_and_niche is None:
                continue
            result[product_id] = category_and_niche
        return result

    @staticmethod
    def __extract_only_new_histories(
        old_history: ProductHistory, new_history: ProductHistory
    ) -> ProductHistory:
        old_units = old_history.get_history()
        new_units = new_history.get_history()
        existing_dates = {unit.unit_date for unit in old_units}
        return ProductHistory(
            (unit for unit in new_units if unit.unit_date not in existing_dates)
        )

    def __update_niche(
        self,
        niche_info: tuple[Niche, int],
        category: Category,
        data_provider_without_key: DataProviderWithoutKey,
    ) -> Niche:
        niche, niche_id = niche_info
        all_products_ids: set[int] = data_provider_without_key.get_products_globals_ids(
            niche.name
        )
        all_products_ids.union({product.global_id for product in niche.products})
        new_products = data_provider_without_key.get_products(
            niche.name, category.name, all_products_ids
        )
        to_create, to_update = self.__split_products_to_create_and_update(
            niche.products, new_products
        )
        self.__standard_filler.check_warehouse_filled(to_create)
        self.__product_card_service.create_products(to_create, [niche_id])
        for product in to_update:
            product_id = self.__product_card_service.find_id_by_global_id(
                product.global_id, niche_id
            )
            if product_id is None:
                raise Exception(
                    "unexpected None result"
                    f"for product with global id {product.global_id}"
                )
            self.__product_card_service.update(product_id, product)
            self.__product_history_service.create(product.history, product_id)
        all_updated_products = [*to_update, *to_create]
        niche.products = all_updated_products
        return niche

    def __split_products_to_create_and_update(
        self, existing_products: list[Product], new_products: list[Product]
    ) -> tuple[list[Product], list[Product]]:
        global_id_to_existing_product = {
            product.global_id: product for product in existing_products
        }
        global_id_to_new_product = {
            product.global_id: product for product in new_products
        }
        to_create: list[Product] = []
        to_update: list[Product] = []
        for global_id in global_id_to_new_product:
            if global_id in global_id_to_existing_product:
                product_to_update = self.__merge_products(
                    global_id_to_existing_product[global_id],
                    global_id_to_new_product[global_id],
                )
                to_update.append(product_to_update)
            else:
                to_create.append(global_id_to_new_product[global_id])
        return to_create, to_update

    def __merge_products(self, into: Product, new_product: Product) -> Product:
        new_history = new_product.history.get_history()
        if new_history:
            into.history = self.__extract_only_new_histories(
                into.history, new_product.history
            )
        into.name = new_product.name
        into.width = new_product.width
        into.height = new_product.height
        into.depth = new_product.depth
        into.cost = new_product.cost
        into.brand = new_product.brand
        into.seller = new_product.seller
        into.rating = new_product.rating
        return into

    def __create_and_update_user_products(
        self,
        user_id: int,
        existing_products: list[Product],
        new_products: list[Product],
        marketplace_id: int,
    ) -> list[Product]:
        to_create, to_update = self.__split_products_to_create_and_update(
            existing_products, new_products
        )
        self.__standard_filler.check_warehouse_filled(to_create)
        for product in to_create:
            niche_id: int = self.__get_niche_id_for_product(product, marketplace_id)
            product_id = self.__product_card_service.create_product(product, [niche_id])
            self.__user_items_service.append_product(user_id, product_id)
        for product in to_update:
            category_name = product.category_niche_list[0][0]
            niche_name = product.category_niche_list[0][1]
            found_info: tuple[Category, int] = self.__category_service.find_by_name(
                category_name, marketplace_id
            )
            if found_info is None:
                continue
            category_id: int = found_info[1]
            found_info: tuple[Niche, int] = self.__niche_service.find_by_name(
                niche_name, category_id
            )
            if found_info is None:
                continue
            niche_id: int = found_info[1]
            product_id = self.__product_card_service.find_id_by_global_id(
                product.global_id, niche_id
            )
            if product_id is None:
                continue
            self.__product_card_service.update(product_id, product)
        return [*to_create, *to_update]

    def __get_niche_id_for_product(self, product: Product, marketplace_id: int) -> int:
        category_name = product.category_niche_list[0][0]
        niche_name = product.category_niche_list[0][1]
        found_info = self.__category_service.find_by_name(
            category_name, marketplace_id
        )
        if found_info is None:
            self.__category_service.create(Category(category_name), marketplace_id=marketplace_id)
            found_info: tuple[Category, int] = self.__category_service.find_by_name(
                category_name, marketplace_id
            )
        category_id: int = found_info[1]
        found_info: tuple[Niche, int] = self.__niche_service.find_by_name(
            niche_name, category_id
        )
        if found_info is None:
            self.__niche_service.create(Niche(niche_name, self.__create_empty_commissions(), 0),
                                        category_id=category_id)
            found_info: tuple[Niche, int] = self.__niche_service.find_by_name(
                niche_name, category_id
            )
        return found_info[1]

    @staticmethod
    def __create_empty_commissions() -> dict[HandlerType, float]:
        return {
            HandlerType.MARKETPLACE: 0,
            HandlerType.CLIENT: 0,
            HandlerType.PARTIAL_CLIENT: 0
        }

    def __get_user_products(
        self,
        user_market_data_provider: UserMarketDataProvider,
        data_provider_without_key: DataProviderWithoutKey,
    ) -> list[Product]:
        products_global_ids: list[int] = user_market_data_provider.get_user_products()
        base_products = data_provider_without_key.get_base_products(products_global_ids)
        products_id_to_cat_niche_name = self.__get_products_category_and_niche(
            [product.global_id for product in base_products], data_provider_without_key
        )
        for product in base_products:
            if product.global_id in products_id_to_cat_niche_name:
                category_and_niche = products_id_to_cat_niche_name[product.global_id]
                product.category_niche_list = [category_and_niche]
        return base_products
