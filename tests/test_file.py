import os
import tempfile
import unittest
import json

from src.db.backend.csv_file import CsvDataBase
from src.db.backend.json_file import JsonDataBase
from src.db.backend.record import Record
from src.db.backend.errors import (
    TableAlreadyExist,
    PathDoesntExist,
    RecordFieldsIncorrect,
    IncorrectId,
    CorruptedTableFile,
    TableError,
)


class TestCsvDataBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = CsvDataBase(data_dir=self.tmp)
        self.db.create_table('Car', {'Brand': str, 'Horsepower': int})
        self.db.load_table('Car')
        self.table = self.db.get_current_table()

    def test_create_table_creates_file(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmp, 'Car.csv')))

    def test_create_table_duplicate_in_memory(self):
        with self.assertRaises(TableAlreadyExist):
            self.db.create_table('Car', {'Brand': str, 'Horsepower': int})

    def test_create_table_duplicate_on_disk(self):
        db2 = CsvDataBase(data_dir=self.tmp)
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

        db2 = CsvDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        fields = db2.get_current_table().get_fields()
        self.assertIs(fields['Brand'], str)
        self.assertIs(fields['Horsepower'], int)

    def test_load_preserves_records(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.table.create_record({'Brand': 'Lada', 'Horsepower': 50})
        self.db.save_table('Car', self.table)

        db2 = CsvDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        records = db2.get_current_table().get_records()
        self.assertEqual(len(records), 2)
        data = [r.get_data() for r in records]
        self.assertIn({'Brand': 'BMW', 'Horsepower': 100}, data)
        self.assertIn({'Brand': 'Lada', 'Horsepower': 50}, data)

    def test_load_handles_none_values(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': None})
        self.db.save_table('Car', self.table)

        db2 = CsvDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        records = db2.get_current_table().get_records()
        self.assertEqual(records[0].get_data()['Horsepower'], None)

    def test_save_overwrites_file(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.db.save_table('Car', self.table)

        self.table.delete_records([self.table.get_records()[0]])
        self.table.create_record({'Brand': 'Tesla', 'Horsepower': 500})
        self.db.save_table('Car', self.table)

        db2 = CsvDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        records = db2.get_current_table().get_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()['Brand'], 'Tesla')

    def test_save_writes_id_column(self):
        self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.db.save_table('Car', self.table)

        with open(os.path.join(self.tmp, 'Car.csv'), encoding='utf-8') as file:
            header = file.readline().strip().split(',')

        self.assertEqual(header[0], 'id')

    def test_load_preserves_record_ids_and_next_id(self):
        first = self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        second = self.table.create_record({'Brand': 'Lada', 'Horsepower': 50})
        self.table.delete_records([first])
        self.db.save_table('Car', self.table)

        db2 = CsvDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        table = db2.get_current_table()

        records = table.select_records({'id': second.get_id(), 'Brand': None, 'Horsepower': None})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()['Brand'], 'Lada')

        new_record = table.create_record({'Brand': 'Tesla', 'Horsepower': 500})
        self.assertEqual(new_record.get_id(), 2)

    def test_load_csv_invalid_int_raises_database_error(self):
        with open(os.path.join(self.tmp, 'Car.csv'), 'w', encoding='utf-8', newline='') as file:
            file.write('id,Brand:str,Horsepower:int\n0,BMW,fast\n')

        db2 = CsvDataBase(data_dir=self.tmp)

        with self.assertRaises(CorruptedTableFile) as context:
            db2.load_table('Car')

        self.assertIsInstance(context.exception, TableError)

    def test_load_csv_invalid_id_raises_database_error(self):
        with open(os.path.join(self.tmp, 'Car.csv'), 'w', encoding='utf-8', newline='') as file:
            file.write('id,Brand:str,Horsepower:int\nwrong,BMW,100\n')

        db2 = CsvDataBase(data_dir=self.tmp)

        with self.assertRaises(CorruptedTableFile):
            db2.load_table('Car')

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


class TestJsonDataBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = JsonDataBase(data_dir=self.tmp)
        self.db.create_table('Car', {'Brand': str, 'Horsepower': int})
        self.db.load_table('Car')
        self.table = self.db.get_current_table()

    def test_save_writes_record_ids(self):
        record = self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        self.db.save_table('Car', self.table)

        with open(os.path.join(self.tmp, 'Car.json'), encoding='utf-8') as file:
            data = json.load(file)

        self.assertEqual(data['records'][0]['id'], record.get_id())
        self.assertEqual(data['records'][0]['data'], {'Brand': 'BMW', 'Horsepower': 100})

    def test_load_preserves_record_ids_and_next_id(self):
        first = self.table.create_record({'Brand': 'BMW', 'Horsepower': 100})
        second = self.table.create_record({'Brand': 'Lada', 'Horsepower': 50})
        self.table.delete_records([first])
        self.db.save_table('Car', self.table)

        db2 = JsonDataBase(data_dir=self.tmp)
        db2.load_table('Car')
        table = db2.get_current_table()

        records = table.select_records({'id': second.get_id(), 'Brand': None, 'Horsepower': None})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get_data()['Brand'], 'Lada')

        new_record = table.create_record({'Brand': 'Tesla', 'Horsepower': 500})
        self.assertEqual(new_record.get_id(), 2)

    def test_load_old_json_format_without_ids(self):
        old_format = {
            'fields': {'Brand': 'str', 'Horsepower': 'int'},
            'records': [{'Brand': 'BMW', 'Horsepower': 100}],
        }
        with open(os.path.join(self.tmp, 'Car.json'), 'w', encoding='utf-8') as file:
            json.dump(old_format, file)

        db2 = JsonDataBase(data_dir=self.tmp)
        db2.load_table('Car')

        records = db2.get_current_table().get_records()
        self.assertEqual(records[0].get_id(), 0)
        self.assertEqual(records[0].get_data()['Brand'], 'BMW')

    def test_load_json_invalid_type_raises_database_error(self):
        data = {
            'fields': {'Brand': 'str', 'Horsepower': 'int'},
            'records': [{'id': 0, 'data': {'Brand': 'BMW', 'Horsepower': 'fast'}}],
        }
        with open(os.path.join(self.tmp, 'Car.json'), 'w', encoding='utf-8') as file:
            json.dump(data, file)

        db2 = JsonDataBase(data_dir=self.tmp)

        with self.assertRaises(CorruptedTableFile) as context:
            db2.load_table('Car')

        self.assertIsInstance(context.exception, TableError)

    def test_load_broken_json_raises_database_error(self):
        with open(os.path.join(self.tmp, 'Car.json'), 'w', encoding='utf-8') as file:
            file.write('{broken')

        db2 = JsonDataBase(data_dir=self.tmp)

        with self.assertRaises(CorruptedTableFile):
            db2.load_table('Car')
