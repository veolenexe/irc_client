import socket
import re
import logging

PORT = 6667
SUCCESSFUL_CONNECT_MESSAGE = ('вы успешно подключились к серверу', 'message')
WRONG_NAME_MESSAGE = ('имя уже исполььзуется или имеет не верный формат',
                      'message')

RE_USER_MSG = re.compile(
    r':(?P<from>.*?)!\S+\sPRIVMSG\s(?P<to>.*?)\s+:(?!VERSION)(?P<msg>.*)$')
RE_NAMES = re.compile(r'353.*?[#&][^\x07\x2C\s]{,200} :(.*?)\r\n')
RE_CHANNEL_LIST = re.compile(r'.*?322.*?(\S*?)(?= \d*? :) (\d*?) :.*?')
RE_WRONG_NAME_INFO = re.compile(r':.*?43[123].*? :.*?')
RE_CONNECT_SUCCESSFUL = re.compile(r':.*?001.*? :.*?')
RE_DICT = {'user message': RE_USER_MSG,
           'channel list': RE_CHANNEL_LIST,
           'name list': RE_NAMES,
           'wrong name message': RE_WRONG_NAME_INFO,
           'successful connect': RE_CONNECT_SUCCESSFUL
           }

logging.basicConfig(handlers=[logging.FileHandler('chat.log', 'a', 'utf-8')],
                    level=logging.INFO,
                    format=u'%(message)s')


class IrcClientSocket:
    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.channel = ''
        self.server_connect = False
        self.channel_connect = False

    def connect_to_server(self, server, user):
        try:
            self.irc.close()
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc.connect((server, PORT))
            user_info = f'USER {user} {user} {user} {user}\n'
            self.irc.send(bytes(user_info, 'UTF-8', errors='replace'))
            self.irc.send(
                bytes(f'NICK {user}\n', 'UTF-8', errors='replace'))
            self.server_connect = True
        except (socket.gaierror, TimeoutError, OSError):
            self.__close_server()

    def connect_to_channel(self, channel):
        self.channel = channel
        self.irc.send(bytes(f'JOIN {self.channel}\n', 'UTF-8'))
        self.channel_connect = True

    def send_message(self, message):
        self.irc.send(bytes(f'PRIVMSG {self.channel} : {message}\n',
                            'UTF-8', 'replace'))
        logging.info(message)

    def show_channel_list(self):
        self.irc.send(bytes('LIST\n', 'UTF-8', errors='replace'))

    def show_name_list(self):
        if self.channel_connect:
            self.irc.send(
                bytes(f'NAMES {self.channel}\n', 'UTF-8', errors='replace'))

    @staticmethod
    def __find_regex(message):
        for regex_name, pattern in RE_DICT.items():
            result = re.findall(pattern, message)
            if 'JOIN' in message or 'QUIT' in message:
                return message, 'refresh names'
            if result:
                return result, regex_name
        return '', ''

    def __close_server(self):
        self.server_connect = False
        self.irc.close()

    def get_message(self):
        """
        необходимо запускать в цикле, отдельном потоке.
        :return: generator: tuple(message, message_type)
        """
        try:
            while self.server_connect:
                message = ''
                while not message.endswith('\r\n'):
                    message += self.irc.recv(2048).decode("UTF-8", 'replace')
                message = message.strip('nr')
                re_message, re_info = self.__find_regex(message)

                if re_info == '':
                    continue
                if re_info == 'user message':
                    user_message = re_message[0]
                    message = f'[{user_message[0]}]: {user_message[2][:-2]}'
                    logging.info(message)
                    yield (message, 'message')
                elif re_info == 'name list':
                    message = re.sub(r' ', '\n', re_message[0])
                    yield (message, 'names')
                elif re_info == 'channel list':
                    message = ''
                    for group in re_message:
                        message = f'{message}{group[0]} - {group[1]}\n'
                    yield (message, 'channels')
                elif re_info == 'refresh names':
                    self.show_name_list()
                elif re_info == 'wrong name message':
                    self.__close_server()
                    yield WRONG_NAME_MESSAGE
                elif re_info == 'successful connect':
                    yield SUCCESSFUL_CONNECT_MESSAGE
        except WindowsError:
            self.channel_connect = False


def main():
    ir = IrcClientSocket()
    ir.connect_to_server('chat.freenode.net', 'default_name')
    ir.connect_to_channel('#default_channel')
    while ir.server_connect:
        print(next(ir.get_message()))


if __name__ == '__main__':
    main()
