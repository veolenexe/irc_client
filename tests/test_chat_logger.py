import unittest
from chat_logger import ChatLogger


class TestChatLogger(unittest.TestCase):
    def setUp(self):
        self.chl = ChatLogger()

    def tearDown(self):
        self.chl.close()

    def test_close_not_openned_log(self):
        result = self.chl.close()
        assert not result

    def test_write_to_close_log(self):
        result = self.chl.write('test')
        assert not result

    def test_write_empy_string(self):
        self.chl.open()
        result = self.chl.write('')
        assert result

    def test_open_twice(self):
        first_open_result = self.chl.open()
        second_open_result = self.chl.open()
        assert first_open_result != second_open_result
