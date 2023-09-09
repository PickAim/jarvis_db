import unittest

from sqlalchemy import select

from jarvis_db.mappers.market.items.leftover_mappers import LeftoverTableToJormMapper
from jarvis_db.schemas import Leftover
from tests.db_context import DbContext
from tests.fixtures import AlchemySeeder


class LeftoverTableToJormMapperTest(unittest.TestCase):
    def setUp(self):
        self.__db_context = DbContext()
        with self.__db_context.session() as session, session.begin():
            seeder = AlchemySeeder(session)
            seeder.seed_products(1)
            seeder.seed_warehouses(2)
            seeder.seed_leftovers(100)

    def test_map(self):
        mapper = LeftoverTableToJormMapper()
        with self.__db_context.session() as session:
            leftovers = list(session.execute(select(Leftover)).scalars().all())
            storage_dict = mapper.map(leftovers)
        self.assertEqual(
            len(leftovers),
            sum(
                (
                    len(warehouse_leftovers)
                    for warehouse_leftovers in storage_dict.values()
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
