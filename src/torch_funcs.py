import torch
import torchaudio.transforms as T
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from src import config
from pathlib import Path


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
    SPEECH_WAVEFORM, SAMPLE_RATE = load_audio(path)

    # Mel spectrogram transform
    mel_spectrogram = T.MelSpectrogram(
        sample_rate=SAMPLE_RATE,
        n_fft=2048,        # FFT window size
        hop_length=512,    # step size between windows
        n_mels=128,        # number of mel filterbanks
    )
    to_db = T.AmplitudeToDB()  # convert power values to decibels for visualization

    mel_spec = mel_spectrogram(SPEECH_WAVEFORM)
    mel_spec_db = to_db(mel_spec)

    return mel_spec_db, SPEECH_WAVEFORM, SAMPLE_RATE

def plot_waveform_and_spectrogram(waveform: torch.Tensor, mel_spectrogram: torch.Tensor) -> None:
    # Plot
    fig, axs = plt.subplots(2, 1, figsize=(12, 7))

    axs[0].plot(waveform[0].numpy())
    axs[0].set_title("Original Waveform")
    axs[0].set_xlabel("Sample")
    axs[0].set_ylabel("Amplitude")

    img = axs[1].imshow(
        mel_spectrogram[0].numpy(),
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        cmap="magma"
    )
    axs[1].set_title("Mel Spectrogram (dB)")
    axs[1].set_xlabel("Frame")
    axs[1].set_ylabel("Mel Frequency Bin")
    plt.colorbar(img, ax=axs[1], label="dB")

    fig.tight_layout()
    plt.show()

if __name__ == '__main__':
    mel_spec, waveform, _ = generate_mel_spectrogram(Path(config.UNPROCESSED_AUDIO_DIR) / 'Paparazzi.m4a')
    plot_waveform_and_spectrogram(waveform, mel_spec)