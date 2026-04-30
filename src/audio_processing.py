from pathlib import Path
import os
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from src import config

def get_audio_metadata(file_path: str | Path) -> dict:
    file_path = Path(file_path)
    audio_format = File(file_path)

    if file_path.suffix not in ('.m4a', '.mp3', '.wav'):
        raise ValueError(f"Unacceptable file type.\nShould be: .m4a, .mp3, .wav\nWas {audio_format}")

    # Tag key mappings per format
    tag_map = {
        # M4A / MP4 tags
        "\xa9nam": "title",
        "\xa9ART": "artist",
        "\xa9alb": "album",
        "\xa9day": "year",
        "\xa9gen": "genre",
        "trkn":    "track_number",
        # MP3 / ID3 tags
        "TIT2": "title",
        "TPE1": "artist",
        "TALB": "album",
        "TDRC": "year",
        "TCON": "genre",
        "TRCK": "track_number",
    }

    metadata = {'file_name': file_path.name, 'format': type(audio_format).__name__}

    for meta_key, friendly_name in tag_map.items():
        if meta_key in audio_format:
            value = audio_format[meta_key]
            metadata[friendly_name] = str(value[0]) if isinstance(value, list) else str(value)

    return metadata

if __name__ == '__main__':
    file_path = config.UNPROCESSED_AUDIO_DIR / 'Shake It Off.mp3'
    metadata = get_audio_metadata(file_path)
    print(metadata)