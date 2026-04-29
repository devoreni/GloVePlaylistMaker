import os
import sqlite3
from src import validate_db

def main() -> None:
    conn = validate_db.get_connection(Path(__file__).parent / 'sen.db')
    return None


if __name__ == "__main__":
    main()
