import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jarvis_db.db_config import Base
from jarvis_db import tables
from jarvis_db.repositores.market.infrastructure import MarketplaceRepository
from jarvis_db.repositores.mappers.market.infrastructure import MarketplaceJormToTableMapper
from jarvis_db.repositores.mappers.market.infrastructure import MarketplaceTableToJormMapper
from jorm.market.infrastructure import Marketplace


class MarketplaceCategoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.__session = session

    def test_add(self):
        marketplace = Marketplace('marketplace1')
        with self.__session() as session, session.begin():
            repository = MarketplaceRepository(
                session, MarketplaceTableToJormMapper(), MarketplaceJormToTableMapper())
            repository.add(marketplace)
        with self.__session() as sesssion:
            db_marketplace: tables.Marketplace = session.query(
                tables.Marketplace).one()
            self.assertEqual(marketplace.name, db_marketplace.name)

    def test_add_all(self):
        marketplaces_to_add = 10
        marketplaces = [Marketplace(
            f'marketplace_{i}') for i in range(1, marketplaces_to_add + 1)]
        with self.__session() as session, session.begin():
            repository = MarketplaceRepository(
                session, MarketplaceTableToJormMapper(), MarketplaceJormToTableMapper())
            repository.add_all(marketplaces)
        with self.__session() as session:
            db_marketplaces: list[tables.Marketplace] = session.query(
                tables.Marketplace).all()
            for jorm_marketplace, db_marketplace in zip(marketplaces, db_marketplaces, strict=True):
                self.assertTrue(jorm_marketplace.name, db_marketplace.name)


if __name__ == '__main__':
    unittest.main()
