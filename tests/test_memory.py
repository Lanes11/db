import unittest
from src.db.backend.memory import *
from src.db.backend.errors import *


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.db = DataBase()
        self.table = self.db.get_current_table()

    def test_create_table_positive(self):
        self.db.create_table("Craft", {"Weight": int, "Length": int})

        self.assertEqual(len(self.db.get_tables()), 2)
        self.assertIn("Craft", self.db.get_tables())

    def test_create_table_negative(self):
        self.db.create_table("Craft", {"Weight": int, "Length": int})

        with self.assertRaises(TableAlreadyExist):
            self.db.create_table("Craft", {"Weight": int, "Length": int})

    def test_switch_table_positive(self):
        self.db.create_table("Craft", {"Weight": int, "Length": int})
        self.db.switch_table("Craft")

        self.assertEqual("Craft", self.db.get_current_table().get_name())

    def test_switch_table_negative(self):
        with self.assertRaises(TableDoesntExist):
            self.db.switch_table("Craft")

    def test_create_record_positive(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.assertEqual(len(self.table.get_records()), 1)

        self.table.create_record({"Brand": "Lada", "Horsepower": 50})
        self.assertEqual(len(self.table.get_records()), 2)

    def test_create_record_extra_field(self):
        with self.assertRaises(RecordFieldsIncorrect):
            self.table.create_record(
                {"Brand": "BMW", "Horsepower": 100, "UnnecessaryField": None}
            )

    def test_create_record_missing_field(self):
        with self.assertRaises(RecordFieldsIncorrect):
            self.table.create_record({"Horsepower": 100})

    def test_create_record_wrong_type(self):
        with self.assertRaises(RecordFieldsIncorrect):
            self.table.create_record({"Brand": "BMW", "Horsepower": "100"})

    def test_select_records_by_string_field(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 100})

        records = self.table.select_records(
            {"id": None, "Brand": "BMW", "Horsepower": None}
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()["Brand"], "BMW")

    def test_select_records_by_int_field(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 100})

        records = self.table.select_records(
            {"id": None, "Brand": None, "Horsepower": 100}
        )
        self.assertEqual(len(records), 2)

    def test_select_records_by_id(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 200})

        records = self.table.select_records(
            {"id": 1, "Brand": None, "Horsepower": None}
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()["Brand"], "Lada")

    def test_select_records_no_match(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        records = self.table.select_records(
            {"id": None, "Brand": "Tesla", "Horsepower": None}
        )
        self.assertEqual(records, [])

    def test_select_records_all(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "Lada", "Horsepower": 200})

        records = self.table.select_records(
            {"id": None, "Brand": None, "Horsepower": None}
        )
        self.assertEqual(len(records), 2)

    def test_select_records_unknown_field(self):
        with self.assertRaises(FiltersFieldsIncorrect):
            self.table.select_records(
                {"id": None, "Brand": "BMW", "UnnecessaryField": None}
            )

    def test_select_records_wrong_type(self):
        with self.assertRaises(FiltersFieldsIncorrect):
            self.table.select_records({"id": None, "Brand": "BMW", "Horsepower": "100"})

    def test_update_record_positive(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        self.table.update_record(0, {"Brand": None, "Horsepower": 50})

        records = self.table.select_records({"id": 0, "Brand": None, "Horsepower": 50})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()["Horsepower"], 50)

    def test_update_record_wrong_id(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        with self.assertRaises(IncorrectId):
            self.table.update_record(99, {"Brand": None, "Horsepower": 50})

    def test_update_record_extra_field(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        with self.assertRaises(RecordFieldsIncorrect):
            self.table.update_record(
                0, {"Brand": None, "Horsepower": 50, "UnnecessaryField": None}
            )

    def test_update_record_wrong_type(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        with self.assertRaises(RecordFieldsIncorrect):
            self.table.update_record(0, {"Brand": None, "Horsepower": "50"})

    def test_delete_records_positive(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})

        record = self.table.get_records()[0]
        self.table.delete_records([record])

        self.assertEqual(len(self.table.get_records()), 0)

    def test_delete_records_by_filter(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 100})
        self.table.create_record({"Brand": "BMW", "Horsepower": 200})
        self.table.create_record({"Brand": "Lada", "Horsepower": 50})

        to_delete = self.table.select_records(
            {"id": None, "Brand": "BMW", "Horsepower": None}
        )
        self.table.delete_records(to_delete)

        remaining = self.table.get_records()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].get_data()["Brand"], "Lada")

    def test_delete_records_wrong_record(self):
        with self.assertRaises(IncorrectId):
            self.table.delete_records([Record(99, {"Brand": "BMW", "Horsepower": 200})])

    def test_sort_records_asc(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 45})
        self.table.create_record({"Brand": "Lada", "Horsepower": 86})
        self.table.create_record({"Brand": "Tesla", "Horsepower": 5})

        self.table.sort_records("Horsepower", asc=True)
        records = self.table.get_records()

        self.assertEqual(records[0].get_id(), 2)
        self.assertEqual(records[1].get_id(), 0)
        self.assertEqual(records[2].get_id(), 1)

    def test_sort_records_desc(self):
        self.table.create_record({"Brand": "BMW", "Horsepower": 45})
        self.table.create_record({"Brand": "Lada", "Horsepower": 86})
        self.table.create_record({"Brand": "Tesla", "Horsepower": 5})

        self.table.sort_records("Horsepower", asc=False)
        records = self.table.get_records()

        self.assertEqual(records[0].get_id(), 1)
        self.assertEqual(records[1].get_id(), 0)
        self.assertEqual(records[2].get_id(), 2)

    def test_sort_records_wrong_field(self):
        with self.assertRaises(IncorrectField):
            self.table.sort_records("NonExistentField", asc=True)
