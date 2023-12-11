from models.signal import Signal


class State:
    threshold: int = 3
    model_index: int = 0
    file_name: str = ''
    secret_data: str = ''

    signal: Signal = None
