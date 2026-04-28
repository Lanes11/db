from .errors import *
from copy import deepcopy


class Record:
    def __init__(self, id: int, data: dict):
        self.__id = id
        self.__data = deepcopy(data)

    def __repr__(self):
        return f"Record(id={self.__id}: {self.__data})"

    def update_field(self, key, value):
        self.__data[key] = value

    def get_data(self):
        return deepcopy(self.__data)

    def get_id(self):
        return self.__id


class Table:
    def __init__(self, name: str, fields: dict):
        self.__name = name
        self.__fields = deepcopy(fields)
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
        return deepcopy(self.__fields)

    def get_records(self):
        return list(self.__records.values())

    def create_record(self, data: dict) -> Record:
        if len(data) != len(self.__fields):
            raise RecordFieldsIncorrect("поля записи некорректны")

        for field, expected_type in self.__fields.items():
            if field not in data:
                raise RecordFieldsIncorrect(f"поле '{field}' отсутствует")
            if data[field] is not None and not isinstance(data[field], expected_type):
                raise RecordFieldsIncorrect(f"поле '{field}' должно иметь тип {expected_type.__name__}")

        new_record = Record(self.__id, data)
        self.__records[self.__id] = new_record
        self.__id += 1

        return new_record

    def select_records(self, filters: dict) -> list:
        records = []

        for field, value in filters.items():
            if field != "id" and field not in self.__fields:
                raise FiltersFieldsIncorrect(f"поле '{field}' отсутствует")

            if field != "id" and value is not None:
                expected_type = self.__fields[field]
                if not isinstance(value, expected_type):
                    raise FiltersFieldsIncorrect(f"поле '{field}' должно иметь тип {expected_type.__name__}")

            if field == "id" and value is not None and not isinstance(value, int):
                raise FiltersFieldsIncorrect("поле 'id' должно иметь тип int")

        for record_id, record in self.__records.items():
            data = record.get_data()
            match = True

            for field, value in filters.items():
                if value is None:
                    continue

                if field == "id":
                    if record_id != value:
                        match = False
                        break
                else:
                    if data[field] != value:
                        match = False
                        break

            if match:
                records.append(record)

        return records

    def update_record(self, id: int, record: dict) -> Record:
        if id not in self.__records:
            raise IncorrectId("такого id не существует")

        if len(record) != len(self.__fields):
            raise RecordFieldsIncorrect("поля записи некорректны")

        for field, expected_type in self.__fields.items():
            if field not in record:
                raise RecordFieldsIncorrect(f"поле '{field}' отсутствует")
            if record[field] is not None and not isinstance(record[field], expected_type):
                raise RecordFieldsIncorrect(f"поле '{field}' должно иметь тип {expected_type.__name__}")

        for field, value in record.items():
            if value is not None:
                self.__records[id].update_field(field, value)

        return self.__records[id]

    def delete_records(self, records: list):
        for record in set(records):
            if record.get_id() not in self.__records:
                raise IncorrectId(f"такой записи не существует: {record}")

            self.__records.pop(record.get_id())

    def sort_records(self, field: str, asc: bool):
        if field not in self.__fields:
            raise IncorrectField("такого поля не существует")

        def sort(item):
            value = item[1].get_data()[field]

            if value is None:
                return (0, None) if not asc else (1, None)
            return (1, value) if not asc else (0, value)

        self.__records = dict(sorted(self.__records.items(), key=sort, reverse=not asc))


class DataBase:
    def __init__(self):
        self.__current_table = Table("Car", {"Brand": str, "Horsepower": int})
        self.__tables = {self.__current_table.get_name(): self.__current_table}

    def __repr__(self):
        if not self.__tables:
            return "Database: пусто"

        __tables = ", ".join(self.__tables.keys())
        return f"Database(tables=[{__tables}])"

    def get_current_table(self) -> Table:
        return self.__current_table

    def get_tables(self):
        return deepcopy(self.__tables)

    def create_table(self, name: str, fields: dict):
        if name in self.__tables:
            raise TableAlreadyExist("таблица уже существует")

        self.__tables[name] = Table(name, fields)

    def switch_table(self, name: str):
        if name not in self.__tables:
            raise TableDoesntExist("такой таблицы не существует")
        self.__current_table = self.__tables[name]


db = DataBase()
