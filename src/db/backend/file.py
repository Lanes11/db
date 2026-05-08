import os
import csv

from .database import DataBase
from .table import Table
from .errors import *
from copy import deepcopy


class FileDataBase(DataBase):
    def __init__(self):
        self.__data_dir = r'C:\Users\yan1k\PycharmProjects\db\src\data'
        self.__current_table = None
        self.__tables = {}

        os.makedirs(self.__data_dir, exist_ok=True)

    def __repr__(self):
        if not self.__tables:
            return "FileDatabase: пусто"

        tables = ", ".join(self.__tables.keys())
        return f"FileDatabase(__tables=[{tables}])"

    def get_current_table(self) -> Table:
        return self.__current_table

    def get_tables(self) -> dict:
        return deepcopy(self.__tables)

    def create_table(self, name: str, fields: dict) -> None:
        if name in self.__tables:
            raise TableAlreadyExist("Таблица уже существует")

        self.save_table(name, Table(name, fields))

    def load_table(self, name: str) -> None:
        path = os.path.join(self.__data_dir, f"{name}.csv")

        if not os.path.exists(path):
            raise PathDoesntExist(f"Таблица '{name}' не найдена")

        with open(path, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            fields = {field: str for field in reader.fieldnames if field != "id"}

            table = Table(name, fields)

            for row in reader:
                record_data = {}
                for key, value in row.items():
                    if key == "id":
                        continue
                    record_data[key] = value

                table.create_record(record_data)

        self.__tables[name] = table
        self.__current_table = table

    def save_table(self, name: str, table: Table) -> None:
        os.makedirs(self.__data_dir, exist_ok=True)

        path = os.path.join(self.__data_dir, f"{name}.csv")

        fields = table.get_fields()
        headers = ["id"] + list(fields.keys())

        with open(path, "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            for record in table.get_records():
                row = {"id": record.get_id()}
                row.update(record.get_data())
                writer.writerow(row)

        self.__tables[name] = table

db = FileDataBase()