import sqlite3
from pathlib import Path
from src.config import MIGRATIONS_DIR

def get_current_version(conn: sqlite3.Connection) -> int:
    """
    gets the latest version from the schema_version table

    :param conn: sqlite connection
    :return: int, version number
    """
    try:
        row = conn.execute('select MAX(version) from schema_version').fetchone()
        return row[0] or 0
    except sqlite3.OperationalError as e:
        return 0

def get_migration_files() -> list[tuple[int, Path]]:
    """
    gets all migration .sql files from the migrations folder, parses them to get the order in which they should be applied,
    then stores them in tuples with a version number and the path. Sorts them before returning them

    :return: list of tuples containing a version no. and a path to the migration file.
    """
    migrations = []
    for file in MIGRATIONS_DIR.glob('*.sql'):
        try:
            version = int(file.stem.split('_')[0])
            migrations.append((version, file))
        except ValueError:
            continue
    return sorted(migrations)


def run_migrations(conn: sqlite3.Connection) -> None:
    """
    Gets the current version of the database from the schema_version table.
    If there are more migration files in the migrations folder, the schema is out of date and the pending migrations
    will be run.

    :param conn: sqlite connection
    :return: None
    """
    current = get_current_version(conn)
    migrations = [
        (version, path) for version, path in get_migration_files() if version > current
    ]
    if not migrations:
        print("Database schema up to date")
        return

    for version, path in migrations:
        print(f'Applying Migration {version}: {path.name}')
        sql = path.read_text()
        conn.executescript(sql)

def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """
    gets the connection as an argument, then runs the migrations in run_migrations

    :param db_path: path to the sqlite database
    :return: returns the connection
    """
    conn = sqlite3.connect(db_path)
    run_migrations(conn)
    return conn