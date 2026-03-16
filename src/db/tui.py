from .backend import memory


def _print_menu() -> None:
    print(f"\n=== База машин ({memory.current_table}) ===")
    print("1. Создать базу данных")
    print("2. Сменить базу данных")
    print("3. Показать все базы данных")
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


def _add_student() -> None:
    print("\nДобавление записи")

    brand = input("brand: ").strip()
    color = input("color: ").strip()
    horsepower = _read_int("horsepower: ")
    tank_capacity = _read_int("tank_capacity: ")

    try:
        record = memory.create_record(
            brand,
            color,
            horsepower,
            tank_capacity,
        )

        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _print_records(records: dict) -> None:
    if not records:
        print("Записи не найдены.")
        return

    for id, record in records.items():
        print(f"id={id}: {record}")


def _show_all_students() -> None:
    print("\nСписок записей")
    _print_records(memory.select_record())


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _find_students_by_filter() -> None:
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    car_id = _read_optional_int("id: ")

    brand = input("brand: ").strip() or None
    color = input("color: ").strip() or None

    horsepower = _read_optional_int("horsepower: ") or None
    tank_capacity = _read_optional_int("tank_capacity: ") or None

    records = memory.select_record(
        id=car_id,
        brand=brand,
        color=color,
        horsepower=horsepower,
        tank_capacity=tank_capacity,
    )

    _print_records(records)


def _update_student() -> None:
    print("\nОбновление записи (Enter = пропустить поле)")

    id = _read_int("id: ")
    brand = input("brand: ").strip() or None
    color = input("color: ").strip() or None
    horsepower = _read_int("horsepower: ") or None
    tank_capacity = _read_int("tank_capacity: ") or None

    try:
        record = memory.update_record(
            id,
            brand,
            color,
            horsepower,
            tank_capacity,
        )

        print(f"Запись обновлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _delete_student() -> None:
    print("\nУдаление записей по фильтру (Enter = пропустить поле)")

    car_id = _read_optional_int("id: ")

    brand = input("brand: ").strip() or None
    color = input("color: ").strip() or None

    horsepower = _read_optional_int("horsepower: ") or None
    tank_capacity = _read_optional_int("tank_capacity: ") or None

    records = memory.select_record(
        id=car_id,
        brand=brand,
        color=color,
        horsepower=horsepower,
        tank_capacity=tank_capacity,
    )

    memory.delete_record(records)


def _list_databases() -> None:
    print(memory.db)


def _create_database() -> None:
    print("\nДобавление базы данных")

    name = input("name: ").strip()

    try:
        memory.create_database(name)
        print("База данных создана")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _switch_database() -> None:
    print("\nСмена базы данных")

    name = input("name: ").strip()

    try:
        memory.switch_database(name)
        print("База данных заменена")

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
                _switch_database()

            case "3":
                _list_databases()

            case "4":
                _add_student()

            case "5":
                _show_all_students()

            case "6":
                _find_students_by_filter()

            case "7":
                _update_student()

            case "8":
                _delete_student()

            case "0":
                print("Выход из программы.")
                break

            case _:
                print("Неизвестная команда. Повторите ввод.")