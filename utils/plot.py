import numpy as np
from matplotlib.figure import Figure


def create_matplotlib_plot(title, ecg_signal: np.ndarray, fs: int, seconds: int = 10, fmt: str = 'r') -> Figure:
    fig = Figure(figsize=(9.4, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(np.arange(len(ecg_signal[:seconds*fs])
                      ) / fs, ecg_signal[:seconds*fs], fmt)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'{title} (for {seconds} s)')
    return fig
