from unicodedata import category
import unittest

from jorm.market.infrastructure import HandlerType, Niche
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from jarvis_db import tables
from jarvis_db.db_config import Base
from jarvis_db.repositores.mappers.market.infrastructure import (
    NicheJormToTableMapper, NicheTableToJormMapper)
from jarvis_db.repositores.market.infrastructure import NicheRepository


class NicheRepositoryTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        category_id = 1
        db_marketplace = tables.Marketplace(name='marketplace_1')
        db_category = tables.Category(
            id=category_id, name='category_1', marketplace=db_marketplace)
        with session() as s, s.begin():
            s.add(db_category)
        self.__category_id = category_id
        self.__session = session

    def test_add_niche_by_category_name(self):
        niche_name = 'niche_1_cat_1'
        niche = Niche(niche_name, {
            HandlerType.CLIENT: 0.1,
            HandlerType.MARKETPLACE: 0.2,
            HandlerType.PARTIAL_CLIENT: 0.3
        }, 0.2, [])
        with self.__session() as session, session.begin():
            repository = NicheRepository(
                session, NicheTableToJormMapper(), NicheJormToTableMapper())
            repository.add(
                niche, self.__category_id)
        with self.__session() as session:
            db_category: tables.Category = session.execute(
                select(tables.Category)
                .join(tables.Category.niches)
                .where(tables.Category.id == self.__category_id)
            ).scalar_one()
            self.assertEqual(len(db_category.niches), 1)
            db_niche = db_category.niches[0]
            self.assertEqual(db_niche.name, niche_name)

    def test_add_all_niches_by_category_name(self):
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
            repository.add_all(
                niches, self.__category_id)
        with self.__session() as session:
            db_niches = session.execute(
                select(tables.Niche)
                .join(tables.Niche.category)
                .where(tables.Category.id == self.__category_id)
            ).scalars().all()
            self.assertEqual(len(db_niches), niches_to_add)
            for niche, db_niche in zip(niches, db_niches, strict=True):
                self.assertEqual(niche.name, db_niche.name)
                self.assertEqual(int(niche.returned_percent * 100),
                                 db_niche.return_percent)
                self.assertEqual(
                    int(niche.commissions[HandlerType.CLIENT] * 100), db_niche.client_commission)
                self.assertEqual(
                    int(niche.commissions[HandlerType.PARTIAL_CLIENT] * 100), db_niche.partial_client_commission)
                self.assertEqual(
                    int(niche.commissions[HandlerType.MARKETPLACE] * 100), db_niche.marketplace_commission)

    def test_find_by_name(self):
        niche_name = 'niche_1_cat1'
        with self.__session() as session, session.begin():
            session.add(tables.Niche(name=niche_name,
                                     marketplace_commission=0.01,
                                     partial_client_commission=0.02,
                                     client_commission=0.03,
                                     return_percent=0.04,
                                     category_id=self.__category_id))
        with self.__session() as session:
            repository = NicheRepository(
                session, NicheTableToJormMapper(), NicheJormToTableMapper())
            niche = repository.find_by_name(
                niche_name, self.__category_id)
            self.assertEqual(niche_name, niche.name)

    def test_fetch_all_by_category(self):
        niches_to_add = 10
        db_niches: list[tables.Niche] = [tables.Niche(name=f'niche_{i}_cat1',
                                                      marketplace_commission=0.01 * i,
                                                      partial_client_commission=0.02 * i,
                                                      client_commission=0.03 * i,
                                                      return_percent=0.04 * i)
                                         for i in range(1, niches_to_add + 1)]
        with self.__session() as session, session.begin():
            db_category = session.execute(
                select(tables.Category)
                .where(tables.Category.id == self.__category_id)
            ).scalar_one()
            db_category.niches = db_niches
            to_jorm_mapper = NicheTableToJormMapper()
            expected_niches = [to_jorm_mapper.map(
                niche) for niche in db_niches]
        with self.__session() as session:
            repository = NicheRepository(
                session, to_jorm_mapper, NicheJormToTableMapper())
            niches = repository.fetch_niches_by_category(
                self.__category_id)
            for expected, actual in zip(expected_niches, niches, strict=True):
                self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
