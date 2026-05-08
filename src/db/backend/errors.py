class TableError(Exception):
    pass


class TableAlreadyExist(TableError):
    pass


class TableDoesntExist(TableError):
    pass


class RecordFieldsIncorrect(TableError):
    pass


class FiltersFieldsIncorrect(TableError):
    pass


class IncorrectId(TableError):
    pass


class IncorrectField(TableError):
    pass


class DataBaseError(Exception):
    pass


class PathDoesntExist(DataBaseError):
    pass
