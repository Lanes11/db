from .errors import *

class Record:
    def __init__(self, id: int, data: dict):
        self.__id = id
        self.__data = data

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __repr__(self):
        return f"Record(id={self.__id}: {self.__data})"

    def get_data(self):
        return self.__data

    def get_id(self):
        return self.__id


class Table:
    def __init__(self, name: str, fields: dict):
        self.__name = name
        self.__fields = fields
        self.__records: dict[int, Record] = {}
        self.__id = 0

    def __repr__(self):
        if not self.__records:
            return f"Table({self.__name}): пусто"

        records = "\n  ".join(repr(record) for record in self.__records.values())
        return f"Table({self.__name}):\n  {records}"

    def get_name(self):
        return self.__name

    def get_fields(self):
        return self.__fields

    def get_records(self):
        return self.__records

    def create_record(self, record: dict) -> Record:
        if len(record) != len(self.__fields):
            raise RecordFieldsIncorrect("Поля записи некорректны")

        for field, expected_type in self.__fields.items():
            if field not in record:
                raise RecordFieldsIncorrect(f"Поле '{field}' отсутствует")
            if type(record[field]).__name__ != expected_type:
                raise RecordFieldsIncorrect(f"Поле '{field}' должно иметь тип {expected_type}")

        new_record = Record(self.__id, record)
        self.__records[self.__id] = new_record
        self.__id+=1

        return new_record

    def select_record(self, filters: dict) -> list:
        if len(filters) - 1 != len(self.__fields) or "id" not in filters:
            raise FiltersFieldsIncorrect("Поля записи некорректны")

        for field, expected_type in self.__fields.items():
            if field not in filters:
                raise FiltersFieldsIncorrect(f"Поле '{field}' отсутствует")
            if filters[field] is not None and type(filters[field]).__name__ != expected_type:
                raise FiltersFieldsIncorrect(f"Поле '{field}' должно иметь тип {expected_type}")

        result = []

        for id, record in self.__records.items():
            if filters["id"] == id:
                result.append(record)
                continue

            for field, value in record.get_data().items():
                if filters[str(field)] == value:
                    result.append(record)

        return result

    def update_record(self, id: int, record: dict) -> Record:
        if id not in self.__records:
            raise IncorrectId("Такого id не существует")

        if len(record) != len(self.__fields):
            raise RecordFieldsIncorrect("Поля записи некорректны")

        for field, expected_type in self.__fields.items():
            if field not in record:
                raise RecordFieldsIncorrect(f"Поле '{field}' отсутствует")
            if record[field] is not None and type(record[field]).__name__ != expected_type:
                raise RecordFieldsIncorrect(f"Поле '{field}' должно иметь тип {expected_type}")

        for field, value in record.items():
            if value is not None:
                self.__records[id].get_data()[field] = value

        return self.__records[id]

    def delete_records(self, records: list):
        for record in records:
            if record.get_id() not in self.get_records():
                raise IncorrectId(f"Такой записи не существует: {record}")

            self.__records.pop(record.get_id())


class DataBase:
    def __init__(self):
        self.__current_table = Table("Car", {"Brand": "str", "Horsepower": "int"})
        self.__tables = {self.__current_table.get_name(): self.__current_table}

    def __repr__(self):
        if not self.__tables:
            return "Database: пусто"

        __tables = ", ".join(self.__tables.keys())
        return f"Database(__tables=[{__tables}])"

    def get_current_table(self) -> Table:
        return self.__current_table

    def get_tables(self):
        return self.__tables

    def create_table(self, name: str, fields: dict):
        if name in self.__tables:
            raise TableAlreadyExist("Таблица уже существует")

        self.__tables[name] = Table(name, fields)

    def switch_table(self, name: str):
        if name not in self.__tables:
            raise TableDoesntExist("Таблица не существует")

        self.__current_table = self.__tables[name]

db = DataBase()