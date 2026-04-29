import sqlite3
from pathlib import Path
from config import MIGRATIONS_DIR

def get_current_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute('select MAX(version) from schema_version').fetchone()
        return row[0] or 0
    except sqlite3.OperationalError as e:
        return 0

def get_migration_files() -> list[tuple[int, Path]]:
    migrations = []
    for file in MIGRATIONS_DIR.glob('*.sql'):
        try:
            version = int(file.stem.split('_')[0])
            migrations.append((version, file))
        except ValueError:
            continue
    return sorted(migrations)


def run_migrations(conn: sqlite3.Connection) -> None:
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
    conn = sqlite3.connect(db_path)
    run_migrations(conn)
    return conn