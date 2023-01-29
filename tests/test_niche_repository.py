import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jarvis_db.db_config import Base
from jarvis_db import tables as db
from jarvis_db.repositores.market.infrastructure import NicheRepository
from jarvis_db.repositores.mappers.market.infrastructure import NicheJormToTableMapper
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper
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
            repository = NicheRepository(
                session, NicheTableToJormMapper(), NicheJormToTableMapper())
            repository.add_by_category_name(niche, category_name)
        with self.__session() as session:
            db_category: db.Category = session.query(db.Category)\
                .join(db.Category.niches)\
                .filter(db.Category.name == category_name)\
                .one()
            self.assertEqual(len(db_category.niches), 1)
            db_niche = db_category.niches[0]
            self.assertEqual(db_niche.name, niche_name)

    def test_add_all_niches_by_category_name(self):
        category_name = 'cat1'
        db_category = db.Category(name=category_name)
        with self.__session() as session, session.begin():
            session.add(db_category)
        niches_to_add = 10
        niches: list[Niche] = [
            Niche(
                f'niche_{i}_cat1',
                {commission: i * 0.1 for i, commission in enumerate(
                    list(HandlerType), start=1)},
                0.1 * i) for i in range(1, niches_to_add + 1)]
        with self.__session() as session, session.begin():
            repository = NicheRepository(
                session, NicheTableToJormMapper(), NicheJormToTableMapper())
            repository.add_all_by_category_name(niches, category_name)
        with self.__session() as session:
            db_category: db.Category = session.query(db.Category)\
                .join(db.Category.niches)\
                .filter(db.Category.name == category_name)\
                .one()
            self.assertEqual(len(db_category.niches), niches_to_add)
            for niche, db_niche in zip(niches, db_category.niches, strict=True):
                self.assertEqual(niche.name, db_niche.name)
                self.assertEqual(int(niche.returned_percent * 100),
                                 db_niche.return_percent)
                self.assertEqual(
                    int(niche.commissions[HandlerType.CLIENT] * 100), db_niche.client_commission)
                self.assertEqual(
                    int(niche.commissions[HandlerType.PARTIAL_CLIENT] * 100), db_niche.partial_client_commission)
                self.assertEqual(
                    int(niche.commissions[HandlerType.MARKETPLACE] * 100), db_niche.marketplace_commission)

    def test_fetch_all_by_category(self):
        category_name = 'cat1'
        db_category = db.Category(name=category_name)
        niches_to_add = 10
        db_niches: list[db.Niche] = [db.Niche(name=f'niche_{i}_cat1',
                                              matketplace_commission=0.01 * i,
                                              partial_client_commission=0.02 * i,
                                              client_commission=0.03 * i,
                                              return_percent=0.04 * i)
                                     for i in range(1, niches_to_add + 1)]
        db_category.niches = db_niches
        to_jorm_mapper = NicheTableToJormMapper()
        expected_niches = [to_jorm_mapper.map(
            niche) for niche in db_niches]
        with self.__session() as session, session.begin():
            session.add(db_category)
        with self.__session() as session:
            repository = NicheRepository(
                session, to_jorm_mapper, NicheTableToJormMapper())
            niches = repository.fetch_niches_by_category(category_name)
            for expected, actual in zip(expected_niches, niches, strict=True):
                self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
