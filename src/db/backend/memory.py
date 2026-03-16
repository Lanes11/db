current_table = "default"

db = {
    "default": {
        "id": 0,
        "data": {},
    }
}


class Car:
    brand: str
    color: str
    horsepower: int
    tank_capacity: int

    def __init__(self, brand, color, horsepower, tank_capacity):
        self.brand = brand
        self.color = color
        self.horsepower = horsepower
        self.tank_capacity = tank_capacity

    def __repr__(self):
        return (
            f"Car(brand={self.brand}, "
            f"color={self.color}, "
            f"horsepower={self.horsepower}, "
            f"tank_capacity={self.tank_capacity})"
        )


def get_current_table():
    return db[current_table]


def create_record(
    brand: str,
    color: str,
    horsepower: int,
    tank_capacity: int,
) -> Car:

    if horsepower < 0:
        raise ValueError("Поле horsepower не может быть отрицательным.")

    if tank_capacity < 0:
        raise ValueError("Поле tank_capacity не может быть отрицательным.")

    table = get_current_table()

    new_record = Car(brand, color, horsepower, tank_capacity)

    table["data"][table["id"]] = new_record
    table["id"] += 1

    return new_record


def select_record(
    id: int | None = None,
    brand: str | None = None,
    color: str | None = None,
    horsepower: int | None = None,
    tank_capacity: int | None = None,
) -> dict:

    table = get_current_table()

    if (
        id is None
        and brand is None
        and color is None
        and horsepower is None
        and tank_capacity is None
    ):
        return table["data"].copy()

    result = {}

    for i, car in table["data"].items():

        if id is not None and i != id:
            continue

        if brand is not None and car.brand != brand:
            continue

        if color is not None and car.color != color:
            continue

        if horsepower is not None and car.horsepower != horsepower:
            continue

        if tank_capacity is not None and car.tank_capacity != tank_capacity:
            continue

        result[i] = car

    return result


def update_record(
    id: int,
    brand: str | None = None,
    color: str | None = None,
    horsepower: int | None = None,
    tank_capacity: int | None = None,
) -> Car:

    table = get_current_table()

    new_record = Car(brand, color, horsepower, tank_capacity)

    table["data"][id] = new_record

    return new_record


def delete_record(records: dict):

    table = get_current_table()

    for i in records.keys():
        table["data"].pop(i)

    print("Удаление прошло успешно")


def create_database(name: str):

    if name in db:
        raise ValueError("Такая база уже существует.")

    db[name] = {
        "id": 0,
        "data": {},
    }


def switch_database(name: str):
    global current_table

    if name not in db:
        raise ValueError("База не существует.")

    current_table = name