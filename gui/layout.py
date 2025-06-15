import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class NotiPopover(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("userPopover.ui", self)
        self.setObjectName("userPopover") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.logoutBtn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.logoutBtn.clicked.connect(self.close)

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

class UserPopover(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("userPopover.ui", self)
        self.setObjectName("userPopover") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.logoutBtn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.logoutBtn.clicked.connect(self.close)
        self.userId.setProperty("class", "weight700 size14 color-gray6")
        self.userEmail.setProperty("class", "weight300 size12 color-gray6")

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

class LayoutWindow(QMainWindow):
    logout_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gigachad | CCTV")
        # .ui 파일 로드
        loadUi("layout.ui", self)
        # 네임 설정
        self.locTitle.setText("CCTV")
        self.locDepth1.setText("전체 매장")
        self.userBtn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # 클래스 지정      
        self.menuBtn1.setProperty("class", "menuBtn1 active")
        self.menuBtn2.setProperty("class", "menuBtn2")
        self.menuBtn3.setProperty("class", "menuBtn3")
        self.verLine.setProperty("class", "bg grayc")
        self.horLine.setProperty("class", "bg grayc")
        self.locTitle.setProperty("class", "weight700 size16 color-gray9")
        self.locDepth1.setProperty("class", "weight700 size16 color-gray9 active")
        self.locDepth2.setProperty("class", "weight700 size16 color-gray9 hidden")
        self.locDivider.setProperty("class", "weight700 size16 color-gray9")
        self.locArrow.setProperty("class", "weight700 size16 color-gray9 hidden")
        
        self.notiBtn.clicked.connect(self.show_noti_popover)
        self.userBtn.clicked.connect(self.show_user_popover)

        # UserPopover 생성 및 시그널 연결
        self.user_popover = UserPopover(self)
        self.user_popover.logoutBtn.clicked.connect(self.handle_logout2)

    def handle_logout2(self):
        """로그아웃 처리"""
        self.logout_successful.emit()

    def show_noti_popover(self):
        # 버튼 위치를 기준으로 팝오버 표시
        button_pos = self.notiBtn.mapToGlobal(self.notiBtn.rect().bottomRight())  # 버튼의 우측 하단 좌표
        popover_x = button_pos.x() - self.user_popover.width()  # 팝오버의 우측 끝이 버튼의 우측 끝과 정렬되도록 조정
        popover_y = button_pos.y() # 버튼의 아래쪽에 팝오버 표시
        self.user_popover.show_at(QPoint(popover_x, popover_y))

    def show_user_popover(self):
        # 버튼 위치를 기준으로 팝오버 표시
        button_pos = self.userBtn.mapToGlobal(self.userBtn.rect().bottomRight())  # 버튼의 우측 하단 좌표
        popover_x = button_pos.x() - self.user_popover.width()  # 팝오버의 우측 끝이 버튼의 우측 끝과 정렬되도록 조정
        popover_y = button_pos.y() # 버튼의 아래쪽에 팝오버 표시
        self.user_popover.show_at(QPoint(popover_x, popover_y))

    # def handle_logout(self):
    #     """로그아웃 처리"""
    #     self.parent().show_login_window()  # MainApp의 화면 전환 메서드 호출

# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     main = Layout()
#     main.show()
#     sys.exit(app.exec())