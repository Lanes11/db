import os
import tempfile
import unittest

from src.db.backend.file import FileDataBase
from src.db.backend.record import Record
from src.db.backend.errors import (
    TableAlreadyExist,
    PathDoesntExist,
    RecordFieldsIncorrect,
    IncorrectId,
)


class TestFileDataBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = FileDataBase(data_dir=self.tmp)
        self.db.create_table('Car', {'Brand': str, 'Horsepower': int})
        self.db.load_table('Car')
        self.table = self.db.get_current_table()

    def test_create_table_creates_file(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmp, 'Car.csv')))

    def test_create_table_duplicate_in_memory(self):
        with self.assertRaises(TableAlreadyExist):
            self.db.create_table('Car', {'Brand': str, 'Horsepower': int})

    def test_create_table_duplicate_on_disk(self):
        db2 = FileDataBase(data_dir=self.tmp)
        with self.assertRaises(TableAlreadyExist):
            db2.create_table('Car', {'Brand': str, 'Horsepower': int})

    def test_create_multiple_tables(self):
        self.db.create_table('Plane', {'Model': str, 'Speed': int})
        tables = self.db.get_tables()
        self.assertIn('Car', tables)
        self.assertIn('Plane', tables)
        self.assertEqual(len(tables), 2)

    def test_load_nonexistent_table(self):
        with self.assertRaises(PathDoesntExist):
            self.db.load_table('NonExistent')

    def test_load_table_sets_current(self):
        self.db.create_table('Plane', {'Model': str})
        self.db.load_table('Plane')
        self.assertEqual(self.db.get_current_table().get_name(), 'Plane')

    def test_load_preserves_field_types(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.db.save_table('Car', self.table)

        db2 = FileDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        fields = db2.get_current_table().get_fields()
        self.assertIs(fields['Brand'], str)
        self.assertIs(fields['Horsepower'], int)

    def test_load_preserves_records(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.table.create_record({'Brand': 'Lada', 'Horsepower': 50})
        self.db.save_table('Car', self.table)

        db2 = FileDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        records = db2.get_current_table().get_records()
        self.assertEqual(len(records), 2)
        data = [r.get_data() for r in records]
        self.assertIn({'Brand': 'BMW', 'Horsepower': 100}, data)
        self.assertIn({'Brand': 'Lada', 'Horsepower': 50}, data)

    def test_load_handles_none_values(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': None})
        self.db.save_table('Car', self.table)

        db2 = FileDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        records = db2.get_current_table().get_records()
        self.assertEqual(records[0].get_data()['Horsepower'], None)

    def test_save_overwrites_file(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.db.save_table('Car', self.table)

        self.table.delete_records([self.table.get_records()[0]])
        self.table.create_record({'Brand': 'Tesla', 'Horsepower': 500})
        self.db.save_table('Car', self.table)

        db2 = FileDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        records = db2.get_current_table().get_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()['Brand'], 'Tesla')

    def test_create_record_wrong_type(self):
        with self.assertRaises(RecordFieldsIncorrect):
            self.table.create_record({'Brand': 'BMW', 'Horsepower': 'fast'})

    def test_delete_records(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        record = self.table.get_records()[0]
        self.table.delete_records([record])
        self.assertEqual(len(self.table.get_records()), 0)

    def test_delete_unknown_record(self):
        with self.assertRaises(IncorrectId):
            self.table.delete_records([Record(99, {'Brand': 'X', 'Horsepower': 1})])
