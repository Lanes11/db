from .errors import *
from .database import DataBase
from .table import Table
from copy import deepcopy


class MemoryDataBase(DataBase):
    def __init__(self):
        self.__current_table = None
        self.__tables = {}

    def __repr__(self):
        if not self.__tables:
            return 'Database: пусто'

        __tables = ', '.join(self.__tables.keys())
        return f'Database(tables=[{__tables}])'

    def get_current_table(self) -> Table:
        return self.__current_table

    def get_tables(self):
        return deepcopy(self.__tables)

    def create_table(self, name: str, fields: dict):
        if name in self.__tables:
            raise TableAlreadyExist('таблица уже существует')

        self.save_table(name, Table(name, fields))

    def load_table(self, name: str):
        if name not in self.__tables:
            raise TableDoesntExist('такой таблицы не существует')
        self.__current_table = self.__tables[name]

    def save_table(self, name: str, table: Table):
        self.__tables[name] = table


db = MemoryDataBase()
