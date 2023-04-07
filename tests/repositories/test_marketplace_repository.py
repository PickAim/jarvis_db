import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.market.infrastructure import MarketplaceRepository


class MarketplaceRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.__session = session

    def test_fetch_all(self):
        marketplaces_to_add = 10
        with self.__session() as session, session.begin():
            db_marketplaces = [tables.Marketplace(
                name=f'markeplace_{i}') for i in range(1, marketplaces_to_add + 1)]
            session.add_all(db_marketplaces)
        with self.__session() as session:
            repository = MarketplaceRepository(session)
            marketplaces = repository.find_all()
            self.assertEqual(marketplaces_to_add, len(marketplaces))


if __name__ == '__main__':
    unittest.main()
