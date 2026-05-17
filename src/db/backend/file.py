import os
import csv

from copy import deepcopy

from .database import DataBase
from .table import Table
from .errors import (
    TableAlreadyExist,
    PathDoesntExist,
)

_TYPES_MAP = {'str': str, 'int': int}


class FileDataBase(DataBase):
    def __init__(self, data_dir: str | None = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data'
            )
        self.__data_dir = os.path.abspath(data_dir)
        self.__current_table: Table | None = None
        self.__tables: dict[str, Table] = {}

        os.makedirs(self.__data_dir, exist_ok=True)

    def __repr__(self):
        if not self.__tables:
            return "FileDatabase: пусто"
        tables = ", ".join(self.__tables.keys())
        return f"FileDatabase(tables=[{tables}])"

    def get_current_table(self) -> Table | None:
        return self.__current_table

    def get_tables(self) -> dict:
        return deepcopy(self.__tables)

    def _path(self, name: str) -> str:
        return os.path.join(self.__data_dir, f"{name}.csv")

    def create_table(self, name: str, fields: dict) -> None:
        if name in self.__tables or os.path.exists(self._path(name)):
            raise TableAlreadyExist("таблица уже существует")
        self.save_table(name, Table(name, fields))

    def load_table(self, name: str) -> None:
        path = self._path(name)

        if not os.path.exists(path):
            raise PathDoesntExist(f"таблица '{name}' не найдена")

        with open(path, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames or []

            fields: dict[str, type] = {}
            field_headers: dict[str, str] = {}

            for header in headers:
                if header == "id":
                    continue
                if ":" in header:
                    fname, ftype = header.split(":", 1)
                    if ftype not in _TYPES_MAP:
                        raise PathDoesntExist(
                            f"неизвестный тип поля '{ftype}' в '{name}.csv'"
                        )
                    fields[fname] = _TYPES_MAP[ftype]
                    field_headers[header] = fname
                else:
                    fields[header] = str
                    field_headers[header] = header

            table = Table(name, fields)

            for row in reader:
                record_data = {}
                for header, fname in field_headers.items():
                    raw = row[header]
                    if raw == '' or raw is None:
                        record_data[fname] = None
                    else:
                        record_data[fname] = fields[fname](raw)
                table.create_record(record_data)

        self.__tables[name] = table
        self.__current_table = table

    def save_table(self, name: str, table: Table) -> None:
        os.makedirs(self.__data_dir, exist_ok=True)

        fields = table.get_fields()
        headers = ["id"] + [f"{k}:{t.__name__}" for k, t in fields.items()]
        header_by_field = {k: f"{k}:{t.__name__}" for k, t in fields.items()}

        with open(self._path(name), "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            for record in table.get_records():
                row = {"id": record.get_id()}
                data = record.get_data()
                for field_name, header in header_by_field.items():
                    row[header] = data[field_name] if data[field_name] is not None else ''
                writer.writerow(row)

        self.__tables[name] = table
