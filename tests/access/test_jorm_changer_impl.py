import unittest
from datetime import datetime
from unittest.mock import Mock

from jorm.market.infrastructure import (
    Address,
    Category,
    HandlerType,
    Niche,
    Product,
    Warehouse,
)
from jorm.market.service import (
    RequestInfo,
    SimpleEconomyRequest,
    SimpleEconomyResult,
    SimpleEconomySaveObject,
)

from jarvis_db.access.jorm_changer import JormChangerImpl


class JormChangerTest(unittest.TestCase):
    def setUp(self):
        self.__category_service_mock = Mock()
        self.__niche_service_mock = Mock()
        self.__product_card_service_mock = Mock()
        self.__product_history_service_mock = Mock()
        self.__economy_service_mock = Mock()
        self.__transit_service_mock = Mock()
        self.__user_items_service_mock = Mock()
        self.__data_provider_without_key_mock = Mock()
        self.__user_market_data_provider_mock = Mock()
        self.__standard_filler_mock = Mock()

    def create_changer(self) -> JormChangerImpl:
        return JormChangerImpl(
            self.__category_service_mock,
            self.__niche_service_mock,
            self.__product_card_service_mock,
            self.__product_history_service_mock,
            self.__economy_service_mock,
            self.__transit_service_mock,
            self.__user_items_service_mock,
            self.__data_provider_without_key_mock,
            self.__user_market_data_provider_mock,
            self.__standard_filler_mock,
        )

    def test_save_unit_economy_request(self):
        date_to_save = datetime(2020, 10, 23)
        request_name_to_save = "request name"
        request_info = RequestInfo(date=date_to_save, name=request_name_to_save)
        niche_id = 1
        category_id = 2
        marketplace_id = 3
        warehouse_name = "test_warehouse_name"
        user_request = SimpleEconomyRequest(
            niche_id,
            category_id,
            marketplace_id,
            100,
            110,
            10,
            11,
            12,
            13,
            warehouse_name,
        )
        recommended_request = SimpleEconomyRequest(
            niche_id,
            category_id,
            marketplace_id,
            101,
            111,
            20,
            21,
            32,
            43,
            warehouse_name,
        )
        user_result = SimpleEconomyResult(200, 25, 45, 35, 15, 150, 0.3, 0.2)
        recommended_result = SimpleEconomyResult(220, 35, 55, 75, 25, 170, 0.5, 0.15)
        save_object = SimpleEconomySaveObject(
            request_info,
            (user_request, user_result),
            (recommended_request, recommended_result),
        )
        user_id = 256
        save_request_mock = Mock()
        save_request_mock.return_value = 400
        self.__economy_service_mock.save_request = save_request_mock
        changer = self.create_changer()
        actual_saved_request_id = changer.save_simple_economy_request(
            save_object, user_id
        )
        self.assertEqual(save_request_mock.return_value, actual_saved_request_id)
        save_request_mock.assert_called_once_with(save_object, user_id)

    def test_update_niche(self):
        # region arrange
        niche_id = 2000
        category_id = 900
        marketplace_id = 3

        changer = self.create_changer()
        get_products_globals_ids_mock = Mock()
        get_products_globals_ids_mock.return_value = set()
        self.__data_provider_without_key_mock.get_products_globals_ids = (
            get_products_globals_ids_mock
        )
        get_products_mock = Mock()
        get_products_mock.return_value = []
        self.__data_provider_without_key_mock.get_products = get_products_mock
        niche_find_by_id_mock = Mock()
        niche = Niche(
            "test_niche_name",
            {
                HandlerType.CLIENT: 0.1,
                HandlerType.MARKETPLACE: 0.2,
                HandlerType.PARTIAL_CLIENT: 0.3,
            },
            0.4,
        )
        niche_find_by_id_mock.return_value = niche
        self.__niche_service_mock.find_by_id = niche_find_by_id_mock
        category_find_by_id_mock = Mock()
        category = Category("test_category_name", {niche.name: niche})
        category_find_by_id_mock.return_value = category
        self.__category_service_mock.find_by_id = category_find_by_id_mock
        niche_find_by_name_atomic_mock = Mock()
        niche_find_by_name_atomic_mock.return_value = (
            Niche(
                niche.name,
                niche.commissions,
                niche.returned_percent,
                [
                    Product(
                        f"test_product_name_{i}",
                        100 + 50 * i,
                        200 + i,
                        0.1 * i % 5,
                        f"test_brand_{i}",
                        f"test_seller_{i}",
                        niche.name,
                        category.name,
                    )
                    for i in range(10)
                ],
            ),
            niche_id,
        )
        self.__niche_service_mock.find_by_name_atomic = niche_find_by_name_atomic_mock
        # endregion
        # region act
        _ = changer.update_niche(niche_id, category_id, marketplace_id)
        # endregion
        # region assert
        niche_find_by_id_mock.assert_called_once_with(niche_id)
        category_find_by_id_mock.assert_called_once_with(category_id)
        niche_find_by_name_atomic_mock.assert_called_once_with(niche.name, category_id)
        # endregion

    def test_load_user_warehouse(self):
        changer = self.create_changer()
        fill_warehouses_mock = Mock()
        fill_warehouses_mock.return_value = [
            Warehouse(f"warehouse_name_{i}", i + 200, HandlerType.CLIENT, Address())
            for i in range(20)
        ]
        self.__standard_filler_mock.fill_warehouse = fill_warehouses_mock
        user_id = 100
        marketplace_id = 2
        result = changer.load_user_warehouse(user_id, marketplace_id)
        fill_warehouses_mock.assert_called_once_with(
            self.__user_market_data_provider_mock
        )
        self.assertListEqual(fill_warehouses_mock.return_value, result)
