from abc import ABC, abstractmethod

from .table import Table


class DataBase(ABC):
    @abstractmethod
    def get_current_table(self) -> Table | None:
        raise NotImplementedError

    @abstractmethod
    def get_tables(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def create_table(self, name: str, fields: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_table(self, table_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_table(self, table_name: str, table: Table) -> None:
        raise NotImplementedError
