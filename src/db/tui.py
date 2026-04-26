from .backend import memory
from .backend.errors import *
from colorama import Fore, Style, init


class TUI:
    def __init__(self):
        self.db = memory.db
        init()

    def run(self) -> None:
        while True:
            self._print_menu()

            action = input("Выберите действие: ").strip()

            match action:
                case "1":
                    self._create_table()
                case "2":
                    self._switch_table()
                case "3":
                    self._print_tables()
                case "4":
                    self._add_record()
                case "5":
                    self._print_records()
                case "6":
                    self._print_find_records_by_filter()
                case "7":
                    self._update_record()
                case "8":
                    self._delete_record()
                case "0":
                    print("Выход из программы.")
                    break
                case _:
                    print("Неизвестная команда. Повторите ввод.")

    def _print_error(self, string: str) -> None:
        print(Fore.RED + string + Style.RESET_ALL)

    def _print_menu(self) -> None:
        print(f"""
        === Таблица ({self.db.get_current_table().get_name()}) ===
        1. Создать таблицу
        2. Сменить таблицу
        3. Показать все таблицы
        4. Добавить запись
        5. Показать все записи
        6. Найти записи по фильтру
        7. Обновить запись
        8. Удалить записи по фильтру
        0. Выход
        """)

    def _read_value(self, field: str, field_type):
        if field_type == str:
            value = input(f"{field} ({field_type.__name__}): ").strip()
            return value or None
        return self._read_optional_int(f"{field} ({field_type.__name__}): ")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                self._print_error("Ошибка: введите целое число")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()

            if raw == "":
                return None

            try:
                return int(raw)
            except ValueError:
                self._print_error("Ошибка: введите целое число или оставьте поле пустым")

    def _create_table(self) -> None:
        print("\nСоздание таблицы")

        fields = {}
        types_map = {"str": str, "int": int}

        while True:
            name = input("Имя: ").strip()
            if name: break
            self._print_error("Ошибка: имя не может быть пустым")

        while True:
            countField = self._read_int("Введите количество полей таблицы: ")
            if countField > 0: break
            self._print_error("Ошибка: количество полей таблицы не может быть меньше 1")

        n = 1

        print("\nНапишите название поля и его тип (str или int) через пробел: ")
        while n <= countField:
            fieldAndType = input(f"{n} поле: ").split()

            if len(fieldAndType) != 2 or fieldAndType[1] not in ["str", "int"]:
                self._print_error("\nОшибка: значение типа неверно (напишите str или int)")
                continue
            elif fieldAndType[0] in fields:
                self._print_error("\nОшибка: такое поле уже сущесвует")
                continue

            fields[fieldAndType[0]] = types_map[fieldAndType[1]]
            n += 1

        try:
            self.db.create_table(name, fields)
            print("Таблица создана")

        except TableError as exc:
            self._print_error(f"Ошибка: {exc}")

    def _switch_table(self) -> None:
        print("\nСмена таблицы")

        name = input("name: ").strip()

        try:
            self.db.switch_table(name)
            print("Таблица заменена")

        except TableError as exc:
            self._print_error(f"Ошибка: {exc}")

    def _print_tables(self) -> None:
        print(self.db)

    def _print_records(self) -> None:
        print(self.db.get_current_table())

    def _add_record(self) -> None:
        print("\nДобавление записи (Enter = пропустить поле)")

        table = self.db.get_current_table()
        fields = table.get_fields()
        data = {}

        for field, field_type in fields.items():
            data[field] = self._read_value(field, field_type)

        try:
            record = table.create_record(data)
            print(f"Запись добавлена: {record}")

        except TableError as exc:
            self._print_error(f"Ошибка: {exc}")

    def _find_records_by_filter(self) -> list:
        fields = self.db.get_current_table().get_fields()
        filters = {}

        filters["id"] = self._read_optional_int("id: ")

        for field, field_type in fields.items():
            filters[field] = self._read_value(field, field_type)

        try:
            return self.db.get_current_table().select_records(filters)

        except TableError as exc:
            self._print_error(f"Ошибка: {exc}")
            return []

    def _print_find_records_by_filter(self) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")

        records = self._find_records_by_filter()

        if not records:
            print("Записи не найдены")
        else:
            print(f"Записи найдены: {records}")

    def _update_record(self) -> None:
        print("\nОбновление записи (Enter = пропустить поле, кроме id)")

        fields = self.db.get_current_table().get_fields()
        id = self._read_int("id: ")

        data = {}

        for field, field_type in fields.items():
            data[field] = self._read_value(field, field_type)

        try:
            record = self.db.get_current_table().update_record(id, data)
            print(f"Запись обновлена: {record}")

        except TableError as exc:
            self._print_error(f"Ошибка: {exc}")

    def _delete_record(self) -> None:
        print("\nУдаление записей по фильтру (Enter = пропустить поле)")

        records = self._find_records_by_filter()

        if len(records)==len(self.db.get_current_table().get_records()):
            while True:
                answer = input("Вы удалите всю таблицу! Вы уверены, что хотите этого?(y/n): ")
                if answer not in ["y", "n"]:
                    self._print_error("Ошибка: введите y или n")
                    continue
                if answer == "n":
                    return
                break

        try:
            self.db.get_current_table().delete_records(records)
            print("Записи успешно удалены")
        except TableError as exc:
            self._print_error(f"Ошибка: {exc}")
