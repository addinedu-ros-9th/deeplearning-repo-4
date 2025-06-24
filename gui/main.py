import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import *
from login import LoginWindow
from layout import LayoutWindow, UserPopover
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from style import apply_style

from modules.user_info import *

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gigachad")
        self.setGeometry(0, 0, 1440, 900)
    
        # QStackedWidget 생성
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # LoginWindow와 LayoutWindow 추가
        self.login_window = LoginWindow()
        self.layout_window = LayoutWindow()

        self.central_widget.addWidget(self.login_window)
        self.central_widget.addWidget(self.layout_window)

        # 로그인 성공 시 LayoutWindow로 전환
        self.login_window.login_successful.connect(self.show_layout_window)
        self.layout_window.logout_successful.connect(self.show_login_window)

        # 초기 화면 설정
        self.central_widget.setCurrentWidget(self.login_window)

    def show_layout_window(self):
        # LayoutWindow로 화면 전환
        self.central_widget.setCurrentWidget(self.layout_window)
        self.layout_window.refresh()
        
    def show_login_window(self):
        # LoginWindow로 화면 전환
        self.central_widget.setCurrentWidget(self.login_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    main_app = MainApp()
    main_app.show()

    sys.exit(app.exec())