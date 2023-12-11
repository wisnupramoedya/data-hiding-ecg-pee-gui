from PyQt6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QMessageBox
from screens.app import Ui_MainWindow
from models.state import State
from models.constant import Constant
from utils.plot import create_matplotlib_plot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from models.signal import Signal
from utils.path import split_file_path_without_extension, split_path_for_saving
from utils.model import get_model
from utils.proccessor import preproccess_signal, string_to_bits, bits_to_string, postproccess_signal
from utils.thread import EmbedThread, ExtractThread
import wfdb


class MyWindow(QMainWindow, Ui_MainWindow):
    embedding_state: State
    extraction_state: State

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("StegaPEER")

        self.set_embed_widget()
        self.set_extract_widget()
        self.set_model_combo_box()

        self.embedding_state = State()
        self.extraction_state = State()

    def set_model_combo_box(self):
        options = Constant.models
        for option in options:
            self.modelComboBox.addItem(option)
            self.xModelComboBox.addItem(option)

        self.modelComboBox.currentIndexChanged.connect(
            self.on_model_combo_box_changed)
        self.xModelComboBox.currentIndexChanged.connect(
            self.x_on_model_combo_box_changed)

    def show_warning_box(self, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle('Warning')
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    """
    EMBEDDING
    """

    def set_embed_widget(self):
        self.getButton.clicked.connect(self.choose_file)
        self.secretTextEdit.textChanged.connect(
            self.on_secret_text_edit_changed)

        self.thresholdSlider.valueChanged.connect(
            self.on_threshold_slider_changed)

        self.embed_thread = EmbedThread()
        self.embed_thread.result_ready.connect(self.handle_embed_result)
        self.embedButton.clicked.connect(self.generate_embedding)
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.save_file)

    def choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Choose ECG File", "", "ECG Files (*.dat)")
        if file_name:
            self.embedding_state.file_name = split_file_path_without_extension(
                file_name)
            print("File is choosen:", self.embedding_state.file_name)

            self.embedding_state.signal = Signal(
                file_path=self.embedding_state.file_name)
            self.plot_ecg_signal_to_frame()
        else:
            self.embedding_state.file_name = ''
            print("File is not picked")

    def on_secret_text_edit_changed(self):
        self.embedding_state.secret_data = self.secretTextEdit.toPlainText()

    def on_model_combo_box_changed(self):
        selected_option_index = self.modelComboBox.currentIndex()
        self.embedding_state.model_index = selected_option_index

    def on_threshold_slider_changed(self, value):
        self.embedding_state.threshold = value

    def plot_ecg_signal_to_frame(self):
        signal = self.embedding_state.signal
        ecg_fig = create_matplotlib_plot(
            "ECG Signal", signal.record, signal.fs, fmt='b')
        self.canvas = FigureCanvas(ecg_fig)
        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.canvas)

    def plot_ecg_signal_to_frame_2(self):
        signal = self.embedding_state.signal
        ecg_fig = create_matplotlib_plot(
            "Embedded ECG Signal", signal.watermarked_record, signal.fs)
        self.canvas = FigureCanvas(ecg_fig)
        layout = QVBoxLayout(self.frame_2)
        layout.addWidget(self.canvas)

    def generate_embedding(self):
        model = get_model(self.embedding_state.model_index)
        threshold = self.embedding_state.threshold
        secret_data = self.embedding_state.secret_data
        signal = self.embedding_state.signal

        if (model is None or threshold is None or secret_data == ''):
            self.show_warning_box(
                f'Ensure that model, threshold, and secret data is not empty!')
            return

        if (signal is None):
            self.show_warning_box(
                f'Please pick the ECG signal first!')
            return

        original_signal = preproccess_signal(signal.record)
        secret_bits = string_to_bits(secret_data)
        self.embed_thread.set_value(
            model=model, original_signal=original_signal, secret_data=secret_bits, threshold=threshold)

        self.embedButton.setText('Loading...')
        self.embedButton.setDisabled(True)
        self.getButton.setDisabled(True)
        self.secretTextEdit.setDisabled(True)
        self.modelComboBox.setDisabled(True)
        self.thresholdSlider.setDisabled(True)
        self.saveButton.setDisabled(True)

        self.embed_thread.stopped = False
        self.embed_thread.start()

    def handle_embed_result(self, result):
        self.embed_thread.stopped = True
        watermarked_signal, loop = result
        if (loop == -1):
            self.show_warning_box(
                f'Threshold range is too low, pick other threshold!')
            return

        self.embedding_state.signal.watermarked_record = postproccess_signal(
            watermarked_signal)
        self.plot_ecg_signal_to_frame_2()

        self.embedButton.setText('Start Embedding')
        self.embedButton.setDisabled(False)
        self.getButton.setDisabled(False)
        self.secretTextEdit.setDisabled(False)
        self.modelComboBox.setDisabled(False)
        self.thresholdSlider.setDisabled(False)
        self.saveButton.setDisabled(False)

    def save_ecg(self, filename: str, directory: str = 'out'):
        signal = self.embedding_state.signal
        ecg_signal = signal.watermarked_record
        if (ecg_signal is None):
            self.show_warning_box(
                f'Embed the data first!')
            return

        record_name = filename
        signals_names = signal.information['sig_name']
        units = signal.information['units']
        fs = signal.information['fs']
        comments = signal.information['comments']

        # Save the ECG signal data to the new WFDB signal file
        wfdb.wrsamp(record_name,
                    fs=fs,
                    p_signal=ecg_signal,
                    units=units,
                    sig_name=signals_names,
                    comments=comments,
                    write_dir=directory)

    def save_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter("All Files (*)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                directory, filename = split_path_for_saving(file_path)
                self.save_ecg(filename, directory)
                self.informationLabel.setText(f"File saved to: {file_path}")

    """
    EXTRACTION
    """

    def set_extract_widget(self):
        self.xGetButton.clicked.connect(self.x_choose_file)

        self.xThresholdSlider.valueChanged.connect(
            self.x_on_threshold_slider_changed)

        self.extract_thread = ExtractThread()
        self.extract_thread.result_ready.connect(self.handle_extract_result)

        self.extractButton.clicked.connect(self.generate_extraction)
        self.xSaveButton.setDisabled(True)
        self.xSaveButton.clicked.connect(self.x_save_file)

    def x_choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Choose ECG File", "", "ECG Files (*.dat)")
        if file_name:
            self.extraction_state.file_name = split_file_path_without_extension(
                file_name)
            print("File is choosen:", self.extraction_state.file_name)

            self.extraction_state.signal = Signal(
                file_path=self.extraction_state.file_name)
            self.x_plot_ecg_signal_to_frame()
        else:
            self.extraction_state.file_name = ''
            print("File is not picked")

    def x_on_model_combo_box_changed(self):
        selected_option_index = self.xModelComboBox.currentIndex()
        self.extraction_state.model_index = selected_option_index

    def x_on_threshold_slider_changed(self, value):
        self.extraction_state.threshold = value

    def x_plot_ecg_signal_to_frame(self):
        signal = self.extraction_state.signal
        ecg_fig = create_matplotlib_plot(
            "ECG Signal", signal.record, signal.fs, fmt='b')
        self.canvas = FigureCanvas(ecg_fig)
        layout = QVBoxLayout(self.xFrame)
        layout.addWidget(self.canvas)

    def x_plot_ecg_signal_to_frame_2(self):
        signal = self.extraction_state.signal
        ecg_fig = create_matplotlib_plot(
            "Extracted ECG Signal", signal.watermarked_record, signal.fs)
        self.canvas = FigureCanvas(ecg_fig)
        layout = QVBoxLayout(self.xFrame_2)
        layout.addWidget(self.canvas)

    def generate_extraction(self):
        model = get_model(self.extraction_state.model_index)
        threshold = self.extraction_state.threshold
        signal = self.extraction_state.signal

        if (model is None or threshold is None):
            self.show_warning_box(
                f'Ensure that model and threshold is not empty!')
            return

        if (signal is None):
            self.show_warning_box(
                f'Please pick the watermarked ECG signal first!')
            return

        original_signal = preproccess_signal(signal.record)
        self.extract_thread.set_value(
            model=model, original_signal=original_signal, threshold=threshold)

        self.extractButton.setText('Loading...')
        self.extractButton.setDisabled(True)
        self.xGetButton.setDisabled(True)
        self.xModelComboBox.setDisabled(True)
        self.xThresholdSlider.setDisabled(True)
        self.xSaveButton.setDisabled(True)

        self.extract_thread.stopped = False
        self.extract_thread.start()

    def handle_extract_result(self, result):
        self.extract_thread.stopped = True
        original_signal, secret_data = result

        self.extraction_state.signal.watermarked_record = postproccess_signal(
            original_signal)
        self.x_plot_ecg_signal_to_frame_2()

        self.xResultLabel.setText(f'Result:\n{bits_to_string(secret_data)}')

        self.extractButton.setText('Start Extraction')
        self.extractButton.setDisabled(False)
        self.xGetButton.setDisabled(False)
        self.xModelComboBox.setDisabled(False)
        self.xThresholdSlider.setDisabled(False)
        self.xSaveButton.setDisabled(False)

    def x_save_ecg(self, filename: str, directory: str = 'out'):
        signal = self.extraction_state.signal
        ecg_signal = signal.watermarked_record
        if (ecg_signal is None):
            self.show_warning_box(
                f'Extract the data first!')
            return

        record_name = filename
        signals_names = signal.information['sig_name']
        units = signal.information['units']
        fs = signal.information['fs']
        comments = signal.information['comments']

        # Save the ECG signal data to the new WFDB signal file
        wfdb.wrsamp(record_name,
                    fs=fs,
                    p_signal=ecg_signal,
                    units=units,
                    sig_name=signals_names,
                    comments=comments,
                    write_dir=directory)

    def x_save_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter("All Files (*)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                directory, filename = split_path_for_saving(file_path)
                self.x_save_ecg(filename, directory)
                self.xInformationLabel.setText(f"File saved to: {file_path}")
