class Record:
    def __init__(self, id: int, data: dict):
        self.id = id
        self.data = data

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return f"Record(id={self.id}: {self.data})"


class Table:
    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields
        self.records: dict[int, Record] = {}
        self.id = 0

    def __repr__(self):
        if not self.records:
            return f"Table({self.name}): пусто"

        records = "\n  ".join(repr(record) for record in self.records.values())
        return f"Table({self.name}):\n  {records}"

    def create_record(self, record: dict) -> Record:
        new_record = Record(self.id, record)
        self.records[self.id] = new_record
        self.id+=1

        return new_record

    def select_record(self, filters: dict) -> list:
        if len(self.fields) != len(filters) - 1:
            raise ValueError("В фильтре присутсвуют лишние поля")

        for field in self.fields:
            if field not in filters:
                raise ValueError("Фильтр настроен некорректно")

        result = []

        for id, record in self.records.items():
            if filters["id"] == id:
                result.append(record)
                continue

            for field, value in record.data.items():
                if filters[str(field)] == value:
                    result.append(record)

        return result

    def update_record(self, id: int, record: dict) -> Record:
        for field, value in record.items():
            if value is not None:
                self.records[id].data[field] = value

        return self.records[id]

    def delete_records(self, records: list):
        for record in records:
            self.records.pop(record.id)


class DataBase:
    def __init__(self):
        self.current_table = Table("Car", {"Brand": "str", "Horsepower": "int"})
        self.tables = {self.current_table.name: self.current_table}

    def __repr__(self):
        if not self.tables:
            return "Database: пусто"

        tables = ", ".join(self.tables.keys())
        return f"Database(tables=[{tables}])"

    def create_table(self, name: str, fields: dict):
        if name in self.tables:
            raise ValueError("Таблица уже существует")

        self.tables[name] = Table(name, fields)

    def switch_table(self, name: str):
        if name not in self.tables:
            raise ValueError("Таблица не существует")

        self.current_table = self.tables[name]

    def get_current_table(self) -> Table:
        if self.current_table is None:
            raise ValueError("Таблица не выбрана")

        return self.current_table

db = DataBase()