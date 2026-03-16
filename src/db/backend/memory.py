id = 0
table = {}

class Car():
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
        return f"Car(brand={self.brand}, color={self.color}, horsepower={self.horsepower}, tank_capacity={self.tank_capacity})"

def create_record(brand: str,
                  color: str,
                  horsepower: int,
                  tank_capacity: int,
                  ) -> Car:
    global id

    if horsepower<0:
        raise ValueError("Поле horsepower не может быть отрицательным.")

    if tank_capacity<0:
        raise ValueError("Поле tank_capacity не может быть отрицательным.")

    new_record = Car(brand, color, horsepower, tank_capacity)
    table[id] = new_record
    id+=1
    return new_record

def select_record(id: int | None = None,
                  brand: str | None = None,
                  color: str | None = None,
                  horsepower: int | None = None,
                  tank_capacity: int | None = None,
                  ) -> dict:
    if (
        id is None
        and brand is None
        and color is None
        and horsepower is None
        and tank_capacity is None
    ):
        return table.copy()

    result = {}

    for i, car in table.items():
        car = table[i]

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

def update_record(id: int | None = None,
                  brand: str | None = None,
                  color: str | None = None,
                  horsepower: int | None = None,
                  tank_capacity: int | None = None,
                  ) -> Car:

    new_record = Car(brand, color, horsepower, tank_capacity)
    table[id] = new_record
    return new_record

def delete_record(records: dict):
    for i in records.keys():
        table.pop(i)

    print("Удаление прошло успешно")