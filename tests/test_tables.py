import unittest
from jarvis_db.tables import User

class TableTest(unittest.TestCase):

    def test_table_access(self):
        self.assertEqual(User.__name__, 'User')

if __name__ == '__main__':
    unittest.main()