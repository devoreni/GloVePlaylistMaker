import shutil
import sqlite3
import os
from mutagen import File
import torch
import torchaudio.transforms as T
import matplotlib
matplotlib.use('QtAgg')
import numpy as np
from pydub import AudioSegment
from src import config
from pathlib import Path
from sklearn.mixture import BayesianGaussianMixture
import pickle
from pprint import pprint

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

def load_audio(path: str | Path) -> tuple[torch.Tensor, int]:
    """Load any audio format via pydub (uses ffmpeg under the hood)."""
    audio = AudioSegment.from_file(str(path))
    sr = audio.frame_rate
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    samples /= float(2 ** (audio.sample_width * 8 - 1))  # normalize to [-1.0, 1.0]

    if audio.channels > 1:
        samples = samples.reshape(-1, audio.channels).T  # [channels, samples]
    else:
        samples = samples[np.newaxis, :]                 # [1, samples]

    return torch.from_numpy(samples), sr

def generate_mel_spectrogram(path: str | Path) -> tuple[torch.Tensor, torch.Tensor, int]:
    # Load audio
    target_sr = 16000
    waveform, sr = load_audio(path)

    if sr != target_sr:
        resampler = T.Resample(orig_freq=sr, new_freq=target_sr)
        waveform = resampler(waveform)

    mel_spectrogram = T.MelSpectrogram(
        sample_rate=target_sr,
        n_fft=2048,
        hop_length=512,
        n_mels=128,
    )
    to_db = T.AmplitudeToDB()  # convert power values to decibels for visualization

    mel_spec = mel_spectrogram(waveform)
    mel_spec_db = to_db(mel_spec)

    return mel_spec_db, waveform, sr

def process_audio(path: str | Path, conn: sqlite3.Connection) -> tuple[bool, str]:
    cur = conn.cursor()
    audio_info = get_audio_metadata(path)
    mel_spec, _, _ = generate_mel_spectrogram(path)
    matrix = np.transpose(mel_spec.numpy()[0])

    gm = BayesianGaussianMixture(
        n_components=16,      # upper bound, not a target
        covariance_type='diag',
        random_state=0,
        n_init=3,
        reg_covar=1e-3,
        max_iter=200,
        weight_concentration_prior=1/16,  # key: encourages sparsity
        verbose=True
    ).fit(matrix)

    serialized_gm = pickle.dumps(gm)

    track = cur.execute(f"""Select * from tracks where gmm = ?""", (serialized_gm,)).fetchone()
    if track:
        os.remove(path)
        return False, f"Track already Exists as {track[5]} [{track[2]}, {track[3]}, {track[4]}"

    new_path = Path(config.PROCESSED_AUDIO_DIR) / os.path.basename(path)
    if os.path.exists(new_path):
        for i in range(1, 30):
            if os.path.exists(Path(config.PROCESSED_AUDIO_DIR) / f"{os.path.basename(path)} ({i})"):
                continue
            else:
                new_path = Path(config.PROCESSED_AUDIO_DIR) / f"{os.path.basename(path)} ({i})"
                break
        else:
            return False, f"Cannot find namespace for {os.path.basename(path)}"

    try:
        cur.execute(f"""
            insert into tracks (title, artist, album, gmm, path)
            values (?, ?, ?, ?, ?)
        """, (audio_info.get('title', None), audio_info.get('artist', None), audio_info.get('album', None), serialized_gm, str(os.path.basename(new_path))))
        shutil.move(path, new_path)
        conn.commit()

    except SyntaxError:
        conn.rollback()
        return False, f"Something went wrong. Insert error, check metadata for audio {os.path.basename(path)}."
    except sqlite3.OperationalError:
        conn.rollback()
        return False, f"A database operational error occurred. Try again later for {os.path.basename(path)}"
    except FileNotFoundError:
        conn.rollback()
        return False, f"The file {os.path.basename(path)} no longer exists."
    except PermissionError:
        conn.rollback()
        return False, f"Permission error for file {os.path.basename(path)}"
    except shutil.Error:
        conn.rollback()
        return False, f"Generic move error for file {os.path.basename(path)}. Try again later"
    except Exception as e:
        conn.rollback()
        print(e)
        return False, f"Something went wrong, rolling back changes for {os.path.basename(path)}"

    return True, f"Successfully processed {os.path.basename(path)}"

if __name__ == '__main__':
    file_path = config.UNPROCESSED_AUDIO_DIR / 'Shake It Off.mp3'

    pprint(get_audio_metadata(file_path))