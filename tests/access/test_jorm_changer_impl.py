from datetime import datetime
import unittest
from unittest.mock import Mock

from jorm.market.infrastructure import Address, HandlerType, Warehouse
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
        self.__data_provider_without_key_factory_mock = Mock()
        self.__user_market_data_provider_factory_mock = Mock()
        self.__standard_filler_provider_mock = Mock()

    def create_changer(self) -> JormChangerImpl:
        return JormChangerImpl(
            self.__category_service_mock,
            self.__niche_service_mock,
            self.__product_card_service_mock,
            self.__product_history_service_mock,
            self.__economy_service_mock,
            self.__frequency_service_mock,
            self.__user_items_service_mock,
            self.__data_provider_without_key_factory_mock,
            self.__user_market_data_provider_factory_mock,
            self.__standard_filler_provider_mock,
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

    def test_load_user_warehouse(self):
        changer = self.create_changer()
        user_market_data_provider_mock = Mock()
        self.__user_market_data_provider_factory_mock.return_value = (
            user_market_data_provider_mock
        )
        db_filler_mock = Mock()
        fill_warehouses_mock = Mock()
        fill_warehouses_mock.return_value = [
            Warehouse(f"warehouse_name_{i}", i + 200, HandlerType.CLIENT, Address())
            for i in range(20)
        ]
        db_filler_mock.fill_warehouse = fill_warehouses_mock
        self.__standard_filler_provider_mock.return_value = db_filler_mock
        user_id = 100
        marketplace_id = 2
        result = changer.load_user_warehouse(user_id, marketplace_id)
        self.__user_market_data_provider_factory_mock.assert_called_once_with(
            user_id, marketplace_id
        )
        self.__standard_filler_provider_mock.assert_called_once_with(marketplace_id)
        fill_warehouses_mock.assert_called_once_with(user_market_data_provider_mock)
        self.assertListEqual(fill_warehouses_mock.return_value, result)
