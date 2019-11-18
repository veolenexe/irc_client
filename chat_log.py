class ChatLog:
    def __init__(self):
        self.__is_open = False
        self.__log = None

    def open(self):
        if not self.__is_open:
            self.__log = open('ChatLog.log', 'a', encoding='utf-8')
            self.__is_open = True

    def write(self, message):
        if self.__is_open:
            self.__log.write(f'{message}\n')

    def close(self):
        if self.__is_open:
            self.__log.close()
            self.__is_open = False
