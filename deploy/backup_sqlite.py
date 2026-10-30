"""Create an exclusive, consistent SQLite backup (also usable for offline restore)."""
import argparse
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from urllib.parse import quote


def backup(source, destination):
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if source == destination.resolve(strict=False):
        raise ValueError('Source and destination must differ.')
    # Never overwrite a backup; restrict sensitive database files to their owner.
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        uri = 'file:' + quote(str(source), safe='/') + '?mode=ro'
        with closing(sqlite3.connect(uri, uri=True)) as original, closing(sqlite3.connect(destination)) as copy:
            original.backup(copy)
            if copy.execute('PRAGMA quick_check').fetchone() != ('ok',):
                raise ValueError('SQLite integrity verification failed.')
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='Existing SQLite database')
    parser.add_argument('destination', help='New, private backup file; never overwritten')
    args = parser.parse_args()
    backup(args.source, args.destination)
    print('SQLite copy completed and integrity checked.')


if __name__ == '__main__':
    main()
