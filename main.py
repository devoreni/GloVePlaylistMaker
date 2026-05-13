import os
import sqlite3
from src import validate_db, audio_processing, config
from pathlib import Path

def main() -> None:
    conn = validate_db.get_connection(Path(__file__).parent / 'sen.db')
    for audio_file in config.UNPROCESSED_AUDIO_DIR.iterdir():
        if audio_file.is_file() and audio_file.suffix in ('.m4a', '.mp3', '.wav'):
            print(f'Processing {os.path.basename(audio_file)}')
            result = audio_processing.process_audio(audio_file, conn)
            print(result[1])
    return None


if __name__ == "__main__":
    main()
