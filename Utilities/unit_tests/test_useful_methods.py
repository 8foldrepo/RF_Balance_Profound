import unittest
from Utilities.useful_methods import *


class TestUsefulMethods(unittest.TestCase):
    def test_cast_as_bool(self):
        self.assertFalse(cast_as_bool("false"))
        self.assertTrue(cast_as_bool("true"))
        self.assertTrue(cast_as_bool("True"))
        self.assertTrue(cast_as_bool("1"))
        self.assertFalse(cast_as_bool(0.0))


if __name__ == '__main__':
    unittest.main()
