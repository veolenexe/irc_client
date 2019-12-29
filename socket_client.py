import socket
import re
from chat_logger import ChatLogger


class IrcClientSocket:
    PORT = 6667
    SUCCESSFUL_CONNECT_MESSAGE = (
        'вы успешно подключились к серверу', 'message')
    WRONG_NAME_MESSAGE = ('имя уже исполььзуется или имеет не верный формат',
                          'message')

    RE_USER_MSG = re.compile(
        r':(?P<from>.*?)!\S+\sPRIVMSG\s(?P<to>.*?)\s+:(?!VERSION)(?P<msg>.*)$')
    RE_NAMES = re.compile(r'353.*?[#&][^\x07\x2C\s]{,200} :(.*?)\r\n')
    RE_CHANNEL_LIST = re.compile(r'.*?322.*?(\S*?)(?= \d*? :) (\d*?) :.*?')
    RE_WRONG_NAME_INFO = re.compile(r':.*?43[123].*? :.*?')
    RE_CONNECT_SUCCESSFUL = re.compile(r':.*?001.*? :.*?')
    RE_PING = re.compile(r'^PING.*')
    RE_DICT = {'user message': RE_USER_MSG,
               'channel list': RE_CHANNEL_LIST,
               'name list': RE_NAMES,
               'wrong name message': RE_WRONG_NAME_INFO,
               'successful connect': RE_CONNECT_SUCCESSFUL,
               'ping': RE_PING
               }

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__channel = ''
        self.__server = ''
        self.__server_connect = False
        self.__channel_connect = False
        self.__chat_logger = ChatLogger()

    def connect_to_server(self, server, user):
        """
        подключается к сереру, окрывает лог.
        :param server: название сервера
        :param user: имя пользователся
        """
        try:
            self.irc.close()
            self.__server = server
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc.connect((server, IrcClientSocket.PORT))
            user_info = f'USER {user} {user} {user} {user}'
            self.__send_message(user_info)
            self.__send_message(f'NICK {user}')
            self.__server_connect = True
            self.__chat_logger.open()
        except (socket.gaierror, TimeoutError, OSError):
            self.close_server()

    def connect_to_channel(self, channel):
        """
        подключается к каналу, если канала нет, то создает его
        если название канала не соотв. формату - ничего не делает.
        :param channel: название канала
        """
        if self.__server_connect:
            self.__channel = channel
            self.__send_message(f'JOIN {self.__channel}')
            self.__channel_connect = True

    def send_private_message(self, message):
        self.__send_message(f'PRIVMSG {self.__channel} : {message}')
        self.__chat_logger.write(message)

    def is_server_connect(self):
        return self.__server_connect

    def get_channel_name(self):
        return self.__channel

    def is_channel_connect(self):
        return self.__channel_connect

    def show_channel_list(self):
        self.__send_message('LIST')

    def show_name_list(self):
        if self.__channel_connect:
            self.__send_message(f'NAMES {self.__channel}')

    def __send_message(self, message):
        """
        отправляет серверу сообщение
        :param message: сообщение
        """
        self.irc.send(bytes(f'{message}\n', 'UTF-8', errors='replace'))

    def __receive_message(self):
        message = ''
        while not message.endswith('\r\n'):
            message += self.irc.recv(2048).decode("UTF-8", 'replace')
        return message.strip('nr')

    @staticmethod
    def __find_regex(message):
        """
        :param message: сообщения, полученое от сервера
        :return: tuple(сообщение, тип сообщения)
        если не совпадает ни с одним типом - возвращает '', ''
        """
        for regex_name, pattern in IrcClientSocket.RE_DICT.items():
            result = re.findall(pattern, message)
            if result:
                return result, regex_name
            if 'JOIN' in message or 'QUIT' in message:
                return message, 'refresh names'
        return '', ''

    def close_server(self):
        self.__server_connect = False
        self.__channel_connect = False
        self.irc.close()
        self.__chat_logger.close()

    def get_message(self):
        """
        необходимо запускать в цикле, отдельном потоке.
        :return: generator: tuple(message, message_type)
        """
        try:
            while self.__server_connect:
                message = self.__receive_message()
                re_message, re_info = self.__find_regex(message)
                if re_info == '':
                    continue
                if re_info == 'user message':
                    user_message = re_message[0]
                    message = f'[{user_message[0]}]: {user_message[2][:-1]}'
                    self.__chat_logger.write(message)
                    yield (message, 'message')
                elif re_info == 'name list':
                    message = re_message[0]
                    yield (message, 'names')
                elif re_info == 'channel list':
                    message = ''
                    for group in re_message:
                        message = f'{message}{group[0]} - {group[1]}\n'
                    yield (message, 'channels')
                elif re_info == 'refresh names' and self.__channel_connect:
                    self.show_name_list()
                elif re_info == 'wrong name message':
                    self.close_server()
                    yield IrcClientSocket.WRONG_NAME_MESSAGE
                elif re_info == 'successful connect':
                    yield IrcClientSocket.SUCCESSFUL_CONNECT_MESSAGE
                elif re_info == 'ping':
                    self.__send_message(f'PONG {self.__server}')
        except WindowsError:
            self.close_server()
