import unittest
from unittest.mock import Mock

from jarvis_db.access.jorm_collector_impl import JormCollectorImpl


class JormCollectorImplTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__marketplace_service_mock = Mock()
        self.__economy_service_mock = Mock()
        self.__niche_service_mock = Mock()
        self.__category_service_mock = Mock()
        self.__warehouse_service_mock = Mock()
        self.__economy_service_mock = Mock()
        self.__transit_service_mock = Mock()
        self.__user_items_service_mock = Mock()
        self.__niche_characteristics_service_mock = Mock()
        self.__green_zone_trade_service_mock = Mock()
        self.__collector = JormCollectorImpl(
            marketplace_service=self.__marketplace_service_mock,
            economy_constants_service=self.__economy_service_mock,
            niche_service=self.__niche_service_mock,
            category_service=self.__category_service_mock,
            warehouse_service=self.__warehouse_service_mock,
            economy_service=self.__economy_service_mock,
            transit_service=self.__transit_service_mock,
            user_items_service=self.__user_items_service_mock,
            green_zone_trade_service=self.__green_zone_trade_service_mock,
            niche_characteristics_service=self.__niche_characteristics_service_mock,
        )

    def test_create(self):
        pass


if __name__ == "__main__":
    unittest.main()
