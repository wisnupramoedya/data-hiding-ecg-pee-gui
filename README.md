# GUI of Steganography PEE

## Penggunaan Dependencies

Proyek ini menggunakan beberapa pustaka Python yang diambil dari sumber-sumber yang ada. Berikut adalah daftar pustaka-pustaka yang diperlukan beserta tautan dan lisensi mereka:

- **PyQt6**

  - Tautan: [PyQt6](https://riverbankcomputing.com/software/pyqt/)
  - Lisensi: GPL

- **wfdb**

  - Tautan: [wfdb](https://github.com/MIT-LCP/wfdb-python)
  - Lisensi: MIT

- **numpy**

  - Tautan: [numpy](https://numpy.org/)
  - Lisensi: BSD-3-Clause

- **matplotlib**

  - Tautan: [matplotlib](https://matplotlib.org/)
  - Lisensi: Matplotlib License

- **scikit-learn**

  - Tautan: [scikit-learn](https://scikit-learn.org/stable/)
  - Lisensi: BSD-3-Clause

- **pyqt6-tools**
  - Tautan: [pyqt6-tools](https://pypi.org/project/pyqt6-tools/)
  - Lisensi: GPL

Pastikan untuk menginstal pustaka-pustaka di atas sebelum menggunakan proyek ini. Lisensi masing-masing pustaka harus dipatuhi.

## Installation

If you want to use this app, you might choose:

1. As a user

```
pip install -r requirements.txt
```

2. As a developer

```
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

## Run the Qt Designer

To edit `.ui` file, run this command.

```
pyqt6-tools designer
```

To save `.ui` to `.py`.

```
pyuic6 screens/app.ui -o screens/app.py
```

## Run the file

To run the program by Python

```
python main.py
```

## Build the file

To build the file, run this. Ensure that you have `pyinstaller`.

```
pyinstaller --onefile -n {app_name} main.py
```
