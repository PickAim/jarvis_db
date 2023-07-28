import unittest

from tests.db_context import DbContext


class AccountRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__db_context = DbContext()

    def test_add(self):
        ...

    def test_add_all(self):
        ...


if __name__ == "__main__":
    unittest.main()
