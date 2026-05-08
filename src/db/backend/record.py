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