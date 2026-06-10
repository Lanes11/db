import sys

from colorama import Fore, Style

from .backend.csv_file import CsvDataBase
from .backend.errors import TableAlreadyExist, TableError
from .backend.json_file import JsonDataBase
from .backend.memory import MemoryDataBase
from .backend.table import Table

NONE_TOKEN = 'None'

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


class TUI:
    def __init__(self):
        print('''
        Выберите тип базы данных:
        1. In-memory
        2. Csv file database
        3. Json file database
        '''
              )

        while True:
            choice = input('Введите номер: ').strip()
            if choice not in ('1', '2', '3'):
                self._print_error('Введите 1, 2 или 3')
                continue

            if choice == '1':
                self.db = MemoryDataBase()
            elif choice == '2':
                self.db = CsvDataBase()
            else:
                self.db = JsonDataBase()

            break

        try:
            self.db.create_table('Car', {'Brand': str, 'Horsepower': int})
        except TableAlreadyExist:
            pass

        try:
            self.db.load_table('Car')
        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')

    def run(self) -> None:
        while True:
            self._print_menu()

            action = input('Выберите действие: ').strip()

            match action:
                case '1':
                    self._create_table()
                case '2':
                    self._load_table()
                case '3':
                    self._print_tables()
                case '4':
                    self._add_record()
                case '5':
                    self._print_records()
                case '6':
                    self._print_find_records_by_filter()
                case '7':
                    self._update_record()
                case '8':
                    self._delete_records()
                case '9':
                    self._sort_records()
                case '0':
                    print('Выход из программы.')
                    break
                case _:
                    self._print_error('Ошибка: неизвестная команда')

    def _print_error(self, string: str) -> None:
        print(Fore.RED + string + Style.RESET_ALL)

    def _get_current_table(self) -> Table | None:
        table = self.db.get_current_table()
        if table is None:
            self._print_error('Ошибка: активная таблица не выбрана')
        return table

    def _print_menu(self) -> None:
        current_table = self.db.get_current_table()
        table_name = current_table.get_name() if current_table is not None else 'Нет активной таблицы'

        print(f'''
        === Таблица ({table_name}) ===
        1. Создать таблицу
        2. Сменить таблицу
        3. Показать все таблицы
        4. Добавить запись
        5. Показать все записи
        6. Найти записи по фильтру
        7. Обновить запись
        8. Удалить записи по фильтру
        9. Сортировка записей по параметру
        0. Выход
        ''')

    def _read_value(self, field: str, field_type):
        if field_type is str:
            value = input(f'{field} ({field_type.__name__}): ').strip()
            return value or None
        return self._read_optional_int(f'{field} ({field_type.__name__}): ')

    def _read_filter_value(self, field: str, field_type):
        while True:
            raw = input(
                f'{field} ({field_type.__name__}, Enter = не фильтровать, {NONE_TOKEN} = искать пустое): '
            ).strip()

            if raw == '':
                return False, None
            if raw == NONE_TOKEN:
                return True, None
            if field_type is str:
                return True, raw

            try:
                return True, int(raw)
            except ValueError:
                self._print_error(f'Ошибка: введите целое число, {NONE_TOKEN} или оставьте поле пустым')

    def _read_update_value(self, field: str, field_type):
        while True:
            raw = input(
                f'{field} ({field_type.__name__}, Enter = не менять, {NONE_TOKEN} = очистить): '
            ).strip()

            if raw == '':
                return False, None
            if raw == NONE_TOKEN:
                return True, None
            if field_type is str:
                return True, raw

            try:
                return True, int(raw)
            except ValueError:
                self._print_error(f'Ошибка: введите целое число, {NONE_TOKEN} или оставьте поле пустым')

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                self._print_error('Ошибка: введите целое число')

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()

            if raw == '':
                return None

            try:
                return int(raw)
            except ValueError:
                self._print_error(
                    'Ошибка: введите целое число или оставьте поле пустым'
                )

    def _create_table(self) -> None:
        print('\nСоздание таблицы')

        fields = {}
        types_map = {'str': str, 'int': int}

        while True:
            name = input('Имя: ').strip()
            if name:
                break
            self._print_error('Ошибка: имя не может быть пустым')

        while True:
            count_field = self._read_int('Введите количество полей таблицы: ')
            if count_field > 0:
                break
            self._print_error('Ошибка: количество полей таблицы не может быть меньше 1')

        n = 1

        print('\nНапишите название поля и его тип (str или int) через пробел: ')
        while n <= count_field:
            field_and_type = input(f'{n} поле: ').split()

            if len(field_and_type) != 2 or field_and_type[1] not in types_map:
                self._print_error(
                    'Ошибка: значение типа неверно (напишите str или int)'
                )
                continue
            elif field_and_type[0] in fields:
                self._print_error('Ошибка: такое поле уже существует')
                continue

            fields[field_and_type[0]] = types_map[field_and_type[1]]
            n += 1

        try:
            self.db.create_table(name, fields)
            print('Таблица создана')

        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')

    def _load_table(self) -> None:
        print('\nСмена таблицы')

        name = input('name: ').strip()

        try:
            self.db.load_table(name)
            print('Таблица заменена')

        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')

    def _print_tables(self) -> None:
        print(self.db)

    def _print_records(self) -> None:
        table = self._get_current_table()
        if table is not None:
            print(table)

    def _add_record(self) -> None:
        print('\nДобавление записи (Enter = пропустить поле)')

        table = self._get_current_table()
        if table is None:
            return

        fields = table.get_fields()
        data = {}

        for field, field_type in fields.items():
            data[field] = self._read_value(field, field_type)

        try:
            record = table.create_record(data)
            self.db.save_table(table.get_name(), table)
            print(f'Запись добавлена: {record}')

        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')

    def _find_records_by_filter(self, table: Table | None = None) -> list:
        if table is None:
            table = self._get_current_table()
        if table is None:
            return []

        fields = table.get_fields()
        filters = {}

        record_id = self._read_optional_int('id: ')
        if record_id is not None:
            filters['id'] = record_id

        for field, field_type in fields.items():
            should_filter, value = self._read_filter_value(field, field_type)
            if should_filter:
                filters[field] = value

        try:
            return table.select_records(filters)

        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')
            return []

    def _print_find_records_by_filter(self) -> None:
        print('\nПоиск по фильтру (Enter = пропустить поле)')

        records = self._find_records_by_filter()

        if not records:
            print('Записи не найдены')
        else:
            print(f'Записи найдены: {records}')

    def _update_record(self) -> None:
        print('\nОбновление записи (Enter = пропустить поле, кроме id)')

        table = self._get_current_table()
        if table is None:
            return

        fields = table.get_fields()
        record_id = self._read_int('id: ')
        changes = {}

        for field, field_type in fields.items():
            should_update, value = self._read_update_value(field, field_type)
            if should_update:
                changes[field] = value

        try:
            record = table.update_record(record_id, changes)
            self.db.save_table(table.get_name(), table)
            print(f'Запись обновлена: {record}')

        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')

    def _delete_records(self) -> None:
        print('\nУдаление записей по фильтру (Enter = пропустить поле)')

        table = self._get_current_table()
        if table is None:
            return

        records = self._find_records_by_filter()

        if len(records) == len(table.get_records()):
            while True:
                answer = input(
                    'Вы удалите всю таблицу! Вы уверены, что хотите этого?(y/n): '
                )
                if answer not in ['y', 'n']:
                    self._print_error('Ошибка: введите y или n')
                    continue
                if answer == 'n':
                    return
                break

        try:
            table.delete_records(records)
            self.db.save_table(table.get_name(), table)
            print('Записи успешно удалены')
        except TableError as exc:
            self._print_error(f'Ошибка: {exc}')

    def _sort_records(self) -> None:
        print('\nСортировка записей по параметру')
        table = self._get_current_table()
        if table is None:
            return

        fields = table.get_fields()
        while True:
            field = input(
                f'Введите любое поле записи {list(fields.keys())}: '
            ).strip()
            if field in fields:
                break
            self._print_error('Ошибка: некорректное поле записи')

        while True:
            asc = input('Возрастание/убывание (t/f)): ')
            if asc not in ['t', 'f']:
                self._print_error('Ошибка: введите t или f')
                continue
            if asc == 't':
                asc = True
            else:
                asc = False
            break

        table.sort_records(field, asc)
        self._print_records()
