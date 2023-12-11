import wfdb
from typing import Any


class Signal:
    record: Any
    watermarked_record: Any = None
    information: dict
    fs: int

    def __init__(self, file_path: str, channel_names=['MLII']):
        self.record, self.information = wfdb.rdsamp(
            file_path, channel_names=channel_names)
        self.fs = self.information['fs']
