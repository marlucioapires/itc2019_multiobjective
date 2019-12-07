# -*- coding: utf-8 -*-
import time


class OutputFile:
    def __init__(self, file_name: str, time_limit=0) -> None:
        self.file_name = file_name
        self.file = open(self.file_name, 'w')
        self.file.close()
        self.file = None
        self.start_time = time.time()
        self.buffer = ""
        self.time_limit = time_limit  # Tempo limite entre gravações de dados no arquivo.

    def write_forced(self, content):
        self.buffer = self.buffer + str(content) + "\n"
        self.__flush()

    def write(self, content):
        self.buffer = self.buffer + str(content) + "\n"
        if (time.time() - self.start_time) >= self.time_limit:
            self.start_time = time.time()
            self.__flush()

    def __open(self):
        if not self.file:
            self.file = open(self.file_name, 'a')

    def __flush(self):
        self.__open()
        self.file.write(self.buffer)
        self.buffer = ""
        self.__close()

    def __close(self):
        self.file.close()
        self.file = None
