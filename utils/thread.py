from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np
from typing import Any
from steganography.MLPEE import MLPEEStego


class EmbedThread(QThread):
    original_signal: np.ndarray
    secret_data: str
    threshold: int
    model: Any

    result_ready = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stopped = False

    def set_value(self, model: Any, original_signal: np.ndarray, secret_data: str, threshold: int):
        self.model = model
        self.original_signal = original_signal
        self.secret_data = secret_data
        self.threshold = threshold

    def run(self):
        print("Running")
        result = self.perform_large_computation()
        if not self.stopped:
            self.result_ready.emit(result)

    def perform_large_computation(self):
        # Simulate a time-consuming computation
        stego = MLPEEStego(self.model)
        result = stego.embed(
            original_data=self.original_signal, secret_data=self.secret_data, threshold=self.threshold)

        return result


class ExtractThread(QThread):
    original_signal: np.ndarray
    threshold: int
    model: Any

    result_ready = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stopped = False

    def set_value(self, model: Any, original_signal: np.ndarray, threshold: int):
        self.model = model
        self.original_signal = original_signal
        self.threshold = threshold
        print(model, original_signal, threshold)

    def run(self):
        print("Running")
        result = self.perform_large_computation()
        if not self.stopped:
            self.result_ready.emit(result)

    def perform_large_computation(self):
        # Simulate a time-consuming computation
        stego = MLPEEStego(self.model)
        result = stego.extract(
            watermarked_data=self.original_signal, threshold=self.threshold)

        return result
