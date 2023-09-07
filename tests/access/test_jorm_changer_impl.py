import unittest
from datetime import datetime
from unittest.mock import Mock

from jorm.market.infrastructure import (
    Address,
    Category,
    HandlerType,
    Niche,
    Warehouse,
    Product,
)
from jorm.market.service import (
    FrequencyRequest,
    FrequencyResult,
    RequestInfo,
    UnitEconomyRequest,
    UnitEconomyResult,
)

from jarvis_db.access.jorm_changer import JormChangerImpl


class JormChangerTest(unittest.TestCase):
    def setUp(self):
        self.__category_service_mock = Mock()
        self.__niche_service_mock = Mock()
        self.__product_card_service_mock = Mock()
        self.__product_history_service_mock = Mock()
        self.__economy_service_mock = Mock()
        self.__frequency_service_mock = Mock()
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
            self.__frequency_service_mock,
            self.__user_items_service_mock,
            self.__data_provider_without_key_mock,
            self.__user_market_data_provider_mock,
            self.__standard_filler_mock,
        )

    def test_save_unit_economy_request(self):
        date_to_save = datetime(2020, 10, 23)
        request_name_to_save = "request name"
        request_info = RequestInfo(date=date_to_save, name=request_name_to_save)
        request_entity = UnitEconomyRequest(
            "test_niche_name",
            123,
            4,
            buy=100,
            pack=50,
            transit_count=11,
            transit_price=121,
            market_place_transit_price=33,
            warehouse_name="test_warehouse_name",
        )
        result_entity = UnitEconomyResult(
            product_cost=200,
            pack_cost=300,
            marketplace_commission=12,
            logistic_price=25,
            storage_price=151,
            margin=134,
            recommended_price=12355,
            transit_profit=2,
            roi=1.2,
            transit_margin=2.0,
        )
        user_id = 256
        save_request_mock = Mock()
        save_request_mock.return_value = 400
        self.__economy_service_mock.save_request = save_request_mock
        changer = self.create_changer()
        saved_request_id = changer.save_unit_economy_request(
            request_entity, result_entity, request_info, user_id
        )
        self.assertEqual(save_request_mock.return_value, saved_request_id)
        save_request_mock.assert_called_once_with(
            request_info, request_entity, result_entity, user_id
        )

    def test_save_frequency_request(self):
        request_info = RequestInfo(date=datetime(2020, 2, 2), name="name")
        request_entity = FrequencyRequest("test_niche_name", 25, 2)
        result_entity = FrequencyResult(
            x=[i for i in range(10)], y=[i for i in range(10)]
        )
        save_request_mock = Mock()
        save_request_mock.return_value = 56
        self.__frequency_service_mock.save = save_request_mock
        changer = self.create_changer()
        saved_request_id = changer.save_frequency_request(
            request_entity, result_entity, request_info, save_request_mock.return_value
        )
        self.assertEqual(save_request_mock.return_value, saved_request_id)
        save_request_mock.assert_called_once_with(
            request_info, request_entity, result_entity, save_request_mock.return_value
        )

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
