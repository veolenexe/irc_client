import unittest
from symbols_replacer import SymbolsReplacer


class TestSymbolsReplacer(unittest.TestCase):
    def setUp(self):
        self.sr = SymbolsReplacer()

    def test_right_symbol(self):
        a = ':-)'
        result = self.sr.find_smile(a)
        assert result == '☺'

    def test_wrong_symbol(self):
        a = 'asdasg141'
        result = self.sr.find_smile(a)
        assert result == 'asdasg141'

    def test_empty_string(self):
        result = self.sr.find_smile('')
        assert result == ''

    def test_lots_right_symbols(self):
        a = ':-)(y):-)(y):-)(y):-)(y):-)(y):-)(y):-)(y):-)(y):-)(y):-)'
        result = self.sr.find_smile(a)
        assert result == '☺✌☺✌☺✌☺✌☺✌☺✌☺✌☺✌☺✌☺'

    def test_lots_different_symbols(self):
        a = ':-)y):-)y):-)y):-)(y):-)(y):-)(y):-)(y):-)(y):)(y):-)'
        result = self.sr.find_smile(a)
        assert result == '☺y)☺y)☺y)☺✌☺✌☺✌☺✌☺✌:)✌☺'
