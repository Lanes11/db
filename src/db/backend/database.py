from abc import ABC, abstractmethod

from .table import Table

class DataBase(ABC):
    @abstractmethod
    def get_current_table(self) -> Table:
        pass

    @abstractmethod
    def get_tables(self) -> dict:
        pass

    @abstractmethod
    def create_table(self, name: str, fields: dict) -> None:
        pass

    @abstractmethod
    def load_table(self, table_name: str) -> None:
        pass

    @abstractmethod
    def save_table(self, table_name: str, table: Table) -> None:
        pass