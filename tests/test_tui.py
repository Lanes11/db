import unittest
from unittest.mock import patch, MagicMock
from src.db.tui import TUI
from src.db.backend.memory import DataBase
from colorama import Fore, Style


class TestTUI(unittest.TestCase):
    def setUp(self):
        self.tui = TUI()
        self.tui.db = DataBase()
        self.db = self.tui.db
        self.table = self.db.get_current_table()

    def error_msg(self, text: str) -> str:
        return Fore.RED + text + Style.RESET_ALL

    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_invalid_command(self, mock_print, mock_input):
        mock_input.side_effect = ["100", "0"]
        self.tui.run()

        mock_print.assert_any_call(self.error_msg("Ошибка: неизвестная команда"))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_exit(self, mock_print, mock_input):
        mock_input.side_effect = ["0"]
        self.tui.run()

        mock_print.assert_any_call("Выход из программы.")

    @patch("builtins.input")
    def test_run_dispatches_all_actions(self, mock_input):
        actions = {
            "1": "_create_table",
            "2": "_switch_table",
            "3": "_print_tables",
            "4": "_add_record",
            "5": "_print_records",
            "6": "_print_find_records_by_filter",
            "7": "_update_record",
            "8": "_delete_records",
            "9": "_sort_records",
        }

        for action, method_name in actions.items():
            with self.subTest(action=action):
                tui = TUI()
                tui.db = DataBase()

                for name in actions.values():
                    setattr(tui, name, MagicMock())

                mock_input.side_effect = [action, "0"]
                tui.run()

                getattr(tui, method_name).assert_called_once()

    @patch("builtins.input")
    def test_create_table_positive(self, mock_input):
        mock_input.side_effect = ["Craft", "2", "Weight int", "Length int"]
        self.tui._create_table()

        self.assertEqual(len(self.db.get_tables()), 2)
        self.assertIn("Craft", self.db.get_tables())

    @patch("builtins.input")
    @patch("builtins.print")
    def test_create_table_duplicate_prints_error(self, mock_print, mock_input):
        mock_input.side_effect = ["Car", "1", "Speed int"]
        self.tui._create_table()

        mock_print.assert_any_call(self.error_msg("Ошибка: таблица уже существует"))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_create_table_invalid_field_type_retries(self, mock_print, mock_input):
        mock_input.side_effect = ["Craft", "1", "Weight unknown", "Weight int"]
        self.tui._create_table()

        self.assertIn("Craft", self.db.get_tables())
        mock_print.assert_any_call(
            self.error_msg("Ошибка: значение типа неверно (напишите str или int)")
        )

    @patch("builtins.input")
    def test_switch_table_positive(self, mock_input):
        mock_input.side_effect = ["Craft", "1", "Weight int"]
        self.tui._create_table()

        mock_input.side_effect = ["Craft"]
        self.tui._switch_table()

        self.assertEqual("Craft", self.db.get_current_table().get_name())

    @patch("builtins.input")
    @patch("builtins.print")
    def test_switch_table_nonexistent_prints_error(self, mock_print, mock_input):
        mock_input.side_effect = ["NonExistent"]
        self.tui._switch_table()

        mock_print.assert_any_call(self.error_msg("Ошибка: такой таблицы не существует"))

    @patch("builtins.input")
    def test_add_record_positive(self, mock_input):

        mock_input.side_effect = ["BMW", "incorrect", "100"]
        self.tui._add_record()

        self.assertEqual(len(self.table.get_records()), 1)
        self.assertEqual(self.table.get_records()[0].get_data()["Horsepower"], 100)

    @patch("builtins.input")
    def test_find_records_by_brand(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 100})

        mock_input.side_effect = ["", "BMW", ""]
        records = self.tui._find_records_by_filter()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()["Brand"], "BMW")

    @patch("builtins.input")
    def test_find_records_by_horsepower(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 100})

        mock_input.side_effect = ["", "", "100"]
        records = self.tui._find_records_by_filter()

        self.assertEqual(len(records), 2)

    @patch("builtins.input")
    def test_find_records_all_none_returns_all(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 200})

        mock_input.side_effect = ["", "", ""]
        records = self.tui._find_records_by_filter()

        self.assertEqual(len(records), 2)

    @patch("builtins.input")
    def test_find_records_no_match(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        mock_input.side_effect = ["", "Tesla", ""]
        records = self.tui._find_records_by_filter()

        self.assertEqual(records, [])

    @patch("builtins.input")
    def test_update_record(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        mock_input.side_effect = ["0", "", "50"]
        self.tui._update_record()

        records = self.table.select_records({"id": 0, "Brand": None, "Horsepower": 50})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()["Horsepower"], 50)

    @patch("builtins.input")
    def test_delete_records_by_filter(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        mock_input.side_effect = ["0", "BMW", "100", "y"]
        self.tui._delete_records()

        self.assertEqual(len(self.table.get_records()), 0)

    @patch("builtins.input")
    def test_delete_all_records_asks_confirmation_no(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        mock_input.side_effect = ["", "", "", "n"]
        self.tui._delete_records()

        self.assertEqual(len(self.table.get_records()), 1)

    @patch("builtins.input")
    def test_sort_records_asc(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 5})
        self.table.create_record({"Brand": "Lada", "Horsepower": 86})
        self.table.create_record({"Brand": "Tesla", "Horsepower": 45})

        mock_input.side_effect = ["Horsepower", "t"]
        self.tui._sort_records()

        records = self.table.get_records()
        self.assertEqual(records[0].get_id(), 0)
        self.assertEqual(records[1].get_id(), 2)
        self.assertEqual(records[2].get_id(), 1)

    @patch("builtins.input")
    def test_sort_records_desc(self, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 5})
        self.table.create_record({"Brand": "Lada", "Horsepower": 86})
        self.table.create_record({"Brand": "Tesla", "Horsepower": 45})

        mock_input.side_effect = ["Horsepower", "f"]
        self.tui._sort_records()

        records = self.table.get_records()
        self.assertEqual(records[0].get_id(), 1)
        self.assertEqual(records[1].get_id(), 2)
        self.assertEqual(records[2].get_id(), 0)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_sort_records_invalid_field_retries(self, mock_print, mock_input):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        mock_input.side_effect = ["WrongField", "Horsepower", "t"]
        self.tui._sort_records()

        mock_print.assert_any_call(self.error_msg("Ошибка: некорректное поле записи"))
