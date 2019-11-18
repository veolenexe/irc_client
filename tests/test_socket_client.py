from unittest import TestCase
from socket_client import IrcClientSocket
from unittest.mock import patch


class TestSocketClient(TestCase):
    def setUp(self):
        self.irc = IrcClientSocket()

    def tearDown(self):
        self.irc.close_server()

    def test_mock_connect_to_channel(self):
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            self.irc.server_connect = True
            self.irc.connect_to_channel('channel')
        result = self.irc.channel_connect and self.irc.channel == 'channel'
        assert result

    def test_mock_priv_message_regex(self):
        priv_mgs = ':freenode-connect!frigg@' \
                   'freenode/utility-bot/frigg PRIVMSG safasf :TEST\r'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=priv_mgs):
                self.irc.server_connect = True
                message = next(self.irc.get_message())
            right_message = ('[freenode-connect]: TEST', 'message')
            assert message == right_message

    def test_mock_channels_regex(self):
        channel_msg = ':card.freenode.net 322 asdafs #theditch 8 :A/NZ' \
                      ' offensive, defensive and DFIR discussion.:card.' \
                      'freenode.net 322 asdafs #/r/seattle 9 :SEP 29,' \
                      ' Today is\r\n'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=channel_msg):
                self.irc.server_connect = True
                message = next(self.irc.get_message())
            right_message = ('#theditch - 8\n#/r/seattle - 9\n', 'channels')
            assert message == right_message

    def test_mock_wrong_name_regex(self):
        wrong_name_msg = ':your name is wrong. 431 is code of error : test\r\n'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=wrong_name_msg):
                self.irc.server_connect = True
                msg = next(self.irc.get_message())
            right_msg = (
                'имя уже исполььзуется или имеет не верный формат', 'message')
            result = msg == right_msg and not self.irc.server_connect
            assert result

    def test_mock_names_regex(self):
        names_msg = '353 som::e text #channelsometext :firstNick secondNick and_other\r\n'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=names_msg):
                self.irc.server_connect = True
                msg = next(self.irc.get_message())
            right_msg = ('firstNick\nsecondNick\nand_other', 'names')
            assert msg == right_msg
