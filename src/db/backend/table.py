from .record import *
from .errors import *

class Table:
    def __init__(self, name: str, fields: dict):
        for field, ftype in fields.items():
            if not isinstance(ftype, type):
                raise IncorrectField(
                    f"поле '{field}' должно быть типом (str, int) \n"
                    f"получено: {ftype!r}"
                )

        self.__name: str = name
        self.__fields: dict[str, type] = deepcopy(fields)
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

    def create_record(self, data: dict, record_id: int | None = None) -> Record:
        if len(data) != len(self.__fields):
            raise RecordFieldsIncorrect("поля записи некорректны")

        for field, expected_type in self.__fields.items():
            if field not in data:
                raise RecordFieldsIncorrect(f"поле '{field}' отсутствует")
            if data[field] is not None and not isinstance(data[field], expected_type):
                raise RecordFieldsIncorrect(
                    f"поле '{field}' должно иметь тип {expected_type.__name__}"
                )

        if record_id is None:
            record_id = self.__id
        elif not isinstance(record_id, int) or isinstance(record_id, bool) or record_id < 0:
            raise IncorrectId("id записи должен быть целым неотрицательным числом")
        elif record_id in self.__records:
            raise IncorrectId(f"запись с id={record_id} уже существует")

        new_record = Record(record_id, data)
        self.__records[record_id] = new_record
        self.__id = max(self.__id, record_id + 1)

        return new_record

    def select_records(self, filters: dict) -> list:
        records = []

        for field, value in filters.items():
            if field != "id" and field not in self.__fields:
                raise FiltersFieldsIncorrect(f"поле '{field}' отсутствует")

            if field != "id" and value is not None:
                expected_type = self.__fields[field]
                if not isinstance(value, expected_type):
                    raise FiltersFieldsIncorrect(
                        f"поле '{field}' должно иметь тип {expected_type.__name__}"
                    )

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
            if record[field] is not None and not isinstance(
                record[field], expected_type
            ):
                raise RecordFieldsIncorrect(
                    f"поле '{field}' должно иметь тип {expected_type.__name__}"
                )

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
