import torch
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import numpy as np
from src import config
from pathlib import Path
from pprint import pprint

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
    mel_spec, _, _ = generate_mel_spectrogram(Path(config.UNPROCESSED_AUDIO_DIR) / 'Blank Space.mp3')
    matrix = np.transpose(mel_spec.numpy()[0])
    bs_model = get_gaussian_mixture(matrix)
    bs_components = [(x, w) for x, w in enumerate(bs_model.weights_) if w > 0.01]
    for i, j in bs_components:
        print(bs_components)

    mel_spec, _, _ = generate_mel_spectrogram(Path(config.UNPROCESSED_AUDIO_DIR) / 'Shake It Off.mp3')
    matrix = np.transpose(mel_spec.numpy()[0])
    sio_model = get_gaussian_mixture(matrix)
    sio_components = [(x, w) for x, w in enumerate(sio_model.weights_) if w > 0.01]
    for i, j in sio_components:
        print(sio_components)

    mel_spec, _, _ = generate_mel_spectrogram(Path(config.UNPROCESSED_AUDIO_DIR) / 'Last Stand.m4a')
    matrix = np.transpose(mel_spec.numpy()[0])
    ls_model = get_gaussian_mixture(matrix)
    ls_components = [(x, w) for x, w in enumerate(ls_model.weights_) if w > 0.01]
    for i, j in ls_components:
        print(ls_components)

    bs_on_bs = bs_model.score_samples(bs_model.means_)
    pprint(bs_on_bs)
    print(sorted(bs_on_bs, reverse=True)[:3])
    print()

    bs_on_sio = bs_model.score_samples(sio_model.means_)
    pprint(bs_on_sio)
    print(sorted(bs_on_sio, reverse=True)[:3])
    print()

    sio_on_bs = sio_model.score_samples(bs_model.means_)
    pprint(sio_on_bs)
    print(sorted(sio_on_bs, reverse=True)[:3])
    print()

    bs_on_ls = bs_model.score_samples(ls_model.means_)
    pprint(bs_on_ls)
    print(sorted(bs_on_ls, reverse=True)[:3])




    # This will evaluate to True
    #my_model = get_gaussian_mixture(matrix)
    #my_model_dupe = get_gaussian_mixture(matrix)
    #x = pickle.dumps(my_model)
    #y = pickle.dumps(my_model2)
    #if x == y:
    #    print('objects are the same')



    #for i in range(250):
    #    print(my_model.predict_proba([matrix[i]]))




    # plot_waveform_and_spectrogram(waveform, mel_spec)