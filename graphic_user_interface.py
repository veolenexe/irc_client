import sys
from PyQt5.QtWidgets import *
import winsound
from threading import Thread
from socket_client import IrcClientSocket
from symbols_replacer import SymbolsReplacer


class UserInterface(QWidget):  # pragma: no cover
    SOUNDS = {'click': lambda: winsound.PlaySound('sounds\\BigButtonClick.wav',
                                                  winsound.SND_ASYNC),
              'new message': lambda: winsound.PlaySound('sounds\\QuestNew.wav',
                                                        winsound.SND_ASYNC)}

    def __init__(self):
        app = QApplication(sys.argv)
        super().__init__()
        self.setMinimumSize(700, 500)
        self.irc_socket = IrcClientSocket()
        self.symbol_replacer = SymbolsReplacer()
        self.grid = QGridLayout()
        self.message_getter = Thread
        self.initUI()
        sys.exit(app.exec_())

    def initUI(self):
        server = QLabel('Server:')
        username = QLabel('Username:')
        send_button = QPushButton('send', self)
        show_channels_button = QPushButton('show channels', self)
        join_button = QPushButton('join', self)
        connect_button = QPushButton('connect', self)

        self.server_edit = QLineEdit()
        self.channel_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.channels_list = QTextBrowser()
        self.chat_window = QTextBrowser()
        self.users_list = QListWidget()
        self.send_message_field = QLineEdit()

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(server, 1, 0)
        self.grid.addWidget(self.server_edit, 1, 1)
        self.grid.addWidget(self.channel_edit, 5, 0, 1, 2)
        self.grid.addWidget(username, 2, 0)
        self.grid.addWidget(self.username_edit, 2, 1)
        self.grid.addWidget(self.channels_list, 6, 0, 5, 2)
        self.grid.addWidget(self.chat_window, 1, 3, 9, 2)
        self.grid.addWidget(self.users_list, 1, 5, 10, 4)
        self.grid.addWidget(self.send_message_field, 10, 3)

        self.grid.addWidget(join_button, 4, 1)
        self.grid.addWidget(show_channels_button, 4, 0)
        self.grid.addWidget(send_button, 10, 4)
        self.grid.addWidget(connect_button, 2, 0, 2, 2)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('VexChat')
        self.show()

        join_button.clicked.connect(self.join_to_channel)
        connect_button.clicked.connect(self.connect_to_server)
        send_button.clicked.connect(self.send_message)
        show_channels_button.clicked.connect(self.show_channels)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('VexChat')
        self.show()

    def closeEvent(self, event):
        if self.irc_socket.server_connect:
            self.irc_socket.close_server()
        event.accept()

    def connect_to_server(self):
        UserInterface.SOUNDS['click']()
        username = self.username_edit.text()
        server = self.server_edit.text()
        self.irc_socket.connect_to_server(server, username)
        if self.irc_socket.server_connect:
            self.message_getter = Thread(target=self.get_mesage, daemon=True)
            self.message_getter.start()
            self.__clear_all_window()
        else:
            self.chat_window.append('вы ввели неверное название сервера '
                                    'или недопустимое имя пользователя')

    def join_to_channel(self):
        UserInterface.SOUNDS['click']()
        if not self.irc_socket.server_connect:
            self.chat_window.append('вы не подключены к cерверу')
        else:
            self.irc_socket.connect_to_channel(self.channel_edit.text())

    def send_message(self):
        UserInterface.SOUNDS['click']()
        if not self.irc_socket.channel_connect:
            self.chat_window.append('вы не подключены к каналу')
        else:
            message = self.send_message_field.text()
            if message:
                self.irc_socket.send_private_message(message)
                self.chat_window.append(
                    self.symbol_replacer.find_smile(message))
        self.send_message_field.clear()

    def show_channels(self):
        UserInterface.SOUNDS['click']()
        self.channels_list.clear()
        if self.irc_socket.server_connect:
            self.irc_socket.show_channel_list()

    def __clear_all_window(self):
        self.channels_list.clear()
        self.chat_window.clear()
        self.users_list.clear()

    def get_mesage(self):
        try:
            while True:
                info = next(self.irc_socket.get_message())
                if info:
                    target = info[1]
                    message = info[0]
                    if target == 'message':
                        UserInterface.SOUNDS['new message']()
                        self.chat_window.append(
                            self.symbol_replacer.find_smile(message))
                    elif target == 'channels':
                        self.channels_list.append(message)
                    elif target == 'names':
                        self.refresh_name_list(message)
        except StopIteration:
            self.irc_socket.channel_connect = False
            self.chat_window.append('вы были отлючены от сервера')

    def refresh_name_list(self, message):
        self.users_list.clear()
        self.users_list.addItem(QListWidgetItem(message))
    #    self.users_list.setText(self.users)
