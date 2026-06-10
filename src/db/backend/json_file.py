import os
import json
from copy import deepcopy

from .database import DataBase
from .errors import TableAlreadyExist, PathDoesntExist, CorruptedTableFile, TableError
from .table import Table

_TYPES_MAP = {'str': str, 'int': int}
_TYPE_TO_STR = {str: 'str', int: 'int'}


class JsonDataBase(DataBase):
    def __init__(self, data_dir: str | None = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data_json')

        self.__data_dir = os.path.abspath(data_dir)
        self.__tables: dict[str, Table] = {}
        self.__current_table: Table | None = None

        os.makedirs(self.__data_dir, exist_ok=True)

    def __repr__(self):
        if not self.__tables:
            return "JsonDatabase: пусто"
        return f"JsonDatabase(tables={list(self.__tables.keys())})"

    def get_current_table(self) -> Table | None:
        return self.__current_table

    def get_tables(self) -> dict:
        return deepcopy(self.__tables)

    def _path(self, name: str) -> str:
        return os.path.join(self.__data_dir, f"{name}.json")

    def create_table(self, name: str, fields: dict) -> None:
        if name in self.__tables or os.path.exists(self._path(name)):
            raise TableAlreadyExist("таблица уже существует")

        table = Table(name, fields)
        self.save_table(name, table)

    def load_table(self, name: str) -> None:
        path = self._path(name)

        if not os.path.exists(path):
            raise PathDoesntExist(f"таблица '{name}' не найдена")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            fields_raw = data["fields"]
            records = data["records"]

            if not isinstance(fields_raw, dict) or not isinstance(records, list):
                raise ValueError("fields должен быть объектом, records - списком")

            fields = {}
            for field_name, field_type in fields_raw.items():
                if field_type not in _TYPES_MAP:
                    raise CorruptedTableFile(
                        f"Некорректный тип поля '{field_type}' "
                        f"в файле '{name}.json'"
                    )
                fields[field_name] = _TYPES_MAP[field_type]

            table = Table(name, fields)

            for rec in records:
                if isinstance(rec, dict) and set(rec) == {"id", "data"}:
                    table.create_record(rec["data"], record_id=rec["id"])
                else:
                    table.create_record(rec)

        except CorruptedTableFile:
            raise
        except (KeyError, TypeError, json.JSONDecodeError, ValueError, TableError) as exc:
            raise CorruptedTableFile(f"Ошибка чтения JSON таблицы '{name}': {exc}")

        self.__tables[name] = table
        self.__current_table = table

    def save_table(self, name: str, table: Table) -> None:
        fields = table.get_fields()

        data = {
            "fields": {
                k: _TYPE_TO_STR[v]
                for k, v in fields.items()
            },
            "records": [
                {
                    "id": record.get_id(),
                    "data": record.get_data(),
                }
                for record in table.get_records()
            ]
        }

        with open(self._path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.__tables[name] = table
