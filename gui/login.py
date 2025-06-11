import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from colors import colors

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gigachad | Login")
        # .ui 파일 로드
        loadUi("login.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    with open("style/qss/layout.qss", "r") as f:
        style = f.read()
        for key, value in colors.items():
            style = style.replace("{{" + key + "}}", value)
        app.setStyleSheet(style)

    # 폰트 설정
    font_id = QFontDatabase.addApplicationFont("./style/fonts/Inter-VariableFont.ttf")
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    font = QFont(font_family)
    app.setFont(font)

    main = Main()
    main.show()
    sys.exit(app.exec())