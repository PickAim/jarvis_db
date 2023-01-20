import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jarvis_db.db_config import Base
from jarvis_db import tables as db
from jarvis_db.repositores.market.infrastructure import NicheRepository
from jorm.market.infrastructure import Niche
from jorm.market.infrastructure import HandlerType


class NicheRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.__session = session

    def test_add_niche_by_category_name(self):
        category_name = 'cat1'
        db_category = db.Category(name=category_name)
        with self.__session() as session, session.begin():
            session.add(db_category)
        niche_name = 'niche_1_cat_1'
        niche = Niche(niche_name, {
            HandlerType.CLIENT: 0.1,
            HandlerType.MARKETPLACE: 0.2,
            HandlerType.PARTIAL_CLIENT: 0.3
        }, 0.2, [])
        with self.__session() as session, session.begin():
            repository = NicheRepository(session)
            repository.add_by_category_name(niche, category_name)
        with self.__session() as session:
            db_category = session.query(db.Category)\
                .join(db.Category.niches)\
                .filter(db.Category.name == category_name)\
                .one()
            self.assertEqual(len(db_category.niches), 1)
            db_niche = db_category.niches[0]
            self.assertEqual(db_niche.name, niche_name)


if __name__ == '__main__':
    unittest.main()
