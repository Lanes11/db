from .backend import memory

def _print_menu() -> None:
    print(f"\n=== Таблица ({memory.db.get_current_table().name}) ===")
    print("1. Создать таблицу")
    print("2. Сменить таблицу")
    print("3. Показать все таблицы")
    print("4. Добавить запись")
    print("5. Показать все записи")
    print("6. Найти записи по фильтру")
    print("7. Обновить запись")
    print("8. Удалить записи по фильтру")
    print("0. Выход")


def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _create_database() -> None:
    print("\nСоздание таблицы")

    fields = {}

    name = input("Имя: ").strip()
    countField = _read_int("Введите количество полей таблицы: ")
    n = 1

    print("\nНапишите название поля и его тип (str или int) через пробел: ")
    while n<=countField:
        fieldAndType = input(f"{n} поле: ").split()

        if len(fieldAndType)!=2 or fieldAndType[1] not in ["str", "int"]:
            print("\nЗначение типа неверно. Напишите str или int.")
            continue

        fields[fieldAndType[0]] = fieldAndType[1]

        n += 1

    try:
        memory.db.create_table(name, fields)
        print("Таблица создана")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _switch_table() -> None:
    print("\nСмена таблицы")

    name = input("name: ").strip()

    try:
        memory.db.switch_table(name)
        print("Таблица заменена")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _print_tables() -> None:
    print(memory.db)


def _print_records() -> None:
    print(memory.db.current_table)


def _add_record() -> None:
    print("\nДобавление записи")

    table = memory.db.current_table
    fields = table.fields
    data = {}

    for field, type in fields.items():
        if type == "str":
            value = input(f"{field} ({type}): ").strip()
        else:
            value = _read_int(f"{field} ({type}): ")

        data[field] = value

    try:
        record = table.create_record(data)

        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _find_records_by_filter() -> list:
    fields = memory.db.get_current_table().fields
    filters = {}

    filters["id"] = _read_optional_int("id: ")

    for field, type in fields.items():
        if type == "str":
            value = input(f"{field} ({type}): ").strip()
        else:
            value = _read_optional_int(f"{field} ({type}): ")

        filters[field] = value

    try:
        records = memory.db.get_current_table().select_record(filters)
        return records

    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return[]

def _print_find_records_by_filter() -> None:
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    records = _find_records_by_filter()

    if len(records) == 0:
        print("Записи не найдены")

    print(f"Записи найдены: {records}")


def _update_record() -> None:
    print("\nОбновление записи (Enter = пропустить поле, кроме id)")

    fields = memory.db.get_current_table().fields
    id = _read_int("id: ")

    data = {}

    for field, type in fields.items():
        if type == "str":
            value = input(f"{field} ({type}): ").strip()
        else:
            value = _read_optional_int(f"{field} ({type}): ")

        data[field] = value

    try:
        record = memory.db.get_current_table().update_record(id, data)

        print(f"Запись обновлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _delete_record() -> None:
    print("\nУдаление записей по фильтру (Enter = пропустить поле)")

    records = _find_records_by_filter()

    try:
        memory.db.get_current_table().delete_records(records)

        print(f"Записи успешно удалены")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def run() -> None:
    while True:
        _print_menu()

        action = input("Выберите действие: ").strip()

        match action:
            case "1":
                _create_database()

            case "2":
                _switch_table()

            case "3":
                _print_tables()

            case "4":
                _add_record()

            case "5":
                _print_records()

            case "6":
                _print_find_records_by_filter()

            case "7":
                _update_record()

            case "8":
                _delete_record()

            case "0":
                print("Выход из программы.")
                break

            case _:
                print("Неизвестная команда. Повторите ввод.")