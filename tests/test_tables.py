import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jarvis_db.tables import Category
from jarvis_db.db_config import Base


class TableTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://')
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.__session = Session

    def test_table_access(self):
        items_to_add = 10
        categories = [Category(name=f'{i}') for i in range(items_to_add)]
        with self.__session() as session, session.begin():
            session.add_all(categories)
        with self.__session() as session:
            result = session.query(Category).all()
        self.assertEqual(len(result), items_to_add)


if __name__ == '__main__':
    unittest.main()
