from .backend.memory import create_record, select_record, update_record, delete_record

def _print_menu() -> None:
    print("\n=== База машин ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить запись")
    print("5. Удалить записи по фильтру")
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
        record = create_record(brand, color, horsepower, tank_capacity)

        print(f"Запись добавлена: {record}")
    except ValueError as exc:
        print(f"Ошибка: {exc}")

def _print_records(records: dict) -> None:
    if not records:
        print("Записи не найдены.")
        return

    for id, record in records.items():
        print(f"id={id}:", record)

def _show_all_students() -> None:
    print("\nСписок записей")
    _print_records(select_record())

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

    records = select_record(
        id = car_id,
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
        record = update_record(id, brand, color, horsepower, tank_capacity)

        print(f"Запись обновлена:", record)
    except ValueError as exc:
        print(f"Ошибка: {exc}")

def _delete_student() -> None:
    print("\nУдаление записей по фильтру (Enter = пропустить поле)")

    car_id = _read_optional_int("id: ")

    brand = input("brand: ").strip() or None
    color = input("color: ").strip() or None

    horsepower = _read_optional_int("horsepower: ") or None
    tank_capacity = _read_optional_int("tank_capacity: ") or None

    records = select_record(
        id = car_id,
        brand=brand,
        color=color,
        horsepower=horsepower,
        tank_capacity=tank_capacity,
    )

    delete_record(records)

def run() -> None:
    while True:
        _print_menu()

        action = input("Выберите действие: ").strip()

        match action:
            case "1":
                _add_student()
            case "2":
                _show_all_students()
            case "3":
                _find_students_by_filter()
            case "4":
                _update_student()
            case "5":
                _delete_student()
            case "0":
                print("Выход из программы.")
                break
            case _:
                print("Неизвестная команда. Повторите ввод.")