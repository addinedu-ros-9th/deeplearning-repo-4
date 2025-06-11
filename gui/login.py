import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from style import apply_style

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gigachad | Login")
        # .ui 파일 로드
        loadUi("login.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    main = Main()
    main.show()
    sys.exit(app.exec())