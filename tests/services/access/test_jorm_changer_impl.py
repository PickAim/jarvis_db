import unittest
from unittest.mock import Mock

from jorm.market.infrastructure import Address, HandlerType, Warehouse

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
