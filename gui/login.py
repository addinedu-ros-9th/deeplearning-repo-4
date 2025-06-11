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
        self.login_btn.setProperty("class", "btn contained primary large")
        self.login_checkbox.setProperty("class", "checkbox gray9")
        self.login_div.setProperty("class", "divider ver dotted")
        self.login_div2.setProperty("class", "divider ver dotted")
        self.login_textfield1.setProperty("class", "textfield large")
        self.login_textfield2.setProperty("class", "textfield large")
        self.login_greeting.setProperty("class", "size24 weight700")
        self.login_desc1.setProperty("class", "size16 weight300 color-gray9")
        self.login_desc2.setProperty("class", "size16 weight300 color-gray9")
        self.login_id.setProperty("class", "size14 color-gray3")
        self.login_password.setProperty("class", "size14 color-gray3")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    main = Main()
    main.show()
    sys.exit(app.exec())