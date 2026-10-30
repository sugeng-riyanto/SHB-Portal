import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from deploy.backup_sqlite import backup

class SQLiteBackupTests(unittest.TestCase):
    def test_backup_and_restore_are_consistent_and_private(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=root/'source.sqlite3'; copy=root/'copy.sqlite3'; restored=root/'restored.sqlite3'
            with sqlite3.connect(source) as db:
                db.execute('CREATE TABLE example (value TEXT)')
                db.execute('INSERT INTO example VALUES (?)',('dummy',))
            backup(source,copy)
            self.assertEqual(os.stat(copy).st_mode & 0o777,0o600)
            backup(copy,restored)
            with sqlite3.connect(restored) as db:
                self.assertEqual(db.execute('SELECT value FROM example').fetchone(),('dummy',))
            with self.assertRaises(FileExistsError): backup(source,copy)
            with sqlite3.connect(copy) as db:
                self.assertEqual(db.execute('SELECT value FROM example').fetchone(),('dummy',))
    def test_missing_source_does_not_create_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaises(FileNotFoundError): backup(root/'missing',root/'backup')
            self.assertFalse((root/'backup').exists())
