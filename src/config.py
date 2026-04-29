import os.path
from pathlib import Path

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

MIGRATIONS_DIR = Path(project_root) / 'migrations'
