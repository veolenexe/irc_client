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
            with patch('socket.socket'):
                self.irc.connect_to_server('server', 'user')
                self.irc.connect_to_channel('channel')
        channel_name_is_correct = self.irc.get_channel_name() == 'channel'
        result = self.irc.is_channel_connect() and channel_name_is_correct
        assert result

    def test_mock_priv_message_regex(self):
        priv_mgs = ':freenode-connect!frigg@' \
                   'freenode/utility-bot/frigg PRIVMSG safasf :TEST\r'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=priv_mgs):
                with patch('socket.socket'):
                    self.irc.connect_to_server('server', 'user')
                    message = next(self.irc.get_message())
        correct_message = ('[freenode-connect]: TEST', 'message')
        assert message == correct_message

    def test_mock_channels_regex(self):
        channel_msg = ':card.freenode.net 322 asdafs #theditch 8 :A/NZ' \
                      ' offensive, defensive and DFIR discussion.:card.' \
                      'freenode.net 322 asdafs #/r/seattle 9 :SEP 29,' \
                      ' Today is\r\n'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=channel_msg):
                with patch('socket.socket'):
                    self.irc.connect_to_server('server', 'user')
                    message = next(self.irc.get_message())
        correct_message = ('#theditch - 8\n#/r/seattle - 9\n', 'channels')
        assert message == correct_message

    def test_mock_wrong_name_regex(self):
        wrong_name_msg = ':your name is wrong. 431 is code of error : test\r\n'
        correct_msg = ('имя уже исполььзуется или имеет не верный формат',
                       'message')
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=wrong_name_msg):
                with patch('socket.socket'):
                    self.irc.connect_to_server('server', 'user')
                    msg = next(self.irc.get_message())
        result = msg == correct_msg and not self.irc.is_server_connect()
        assert result

    def test_mock_names_regex(self):
        names_msg = '353 som::e text #channelsometext' \
                    ' :firstNick secondNick and_other\r\n'
        with patch.object(self.irc, '_IrcClientSocket__send_message'):
            with patch.object(self.irc, '_IrcClientSocket__receive_message',
                              return_value=names_msg):
                with patch('socket.socket'):
                    self.irc.connect_to_server('server', 'user')
                    # self.irc.server_connect = True
                    msg = next(self.irc.get_message())
        correct_msg = ('firstNick secondNick and_other', 'names')
        result = msg == correct_msg
        assert result
