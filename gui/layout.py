import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from cctv import CCTVWidget
from dashboard import DashboardWidget
from detect_log import DetectLogWidget

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

        self.user_info = None 

        self.logoutBtn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.logoutBtn.clicked.connect(self.close)
        self.userId.setProperty("class", "weight700 size14 color-gray6")
        self.userEmail.setProperty("class", "weight300 size12 color-gray6")

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

    def set_user_info(self, user_info):
        self.user_info = user_info
        self.userId.setText(user_info['name'])
        self.userEmail.setText(user_info['email'])

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
        # self.userBtn.setText(super().user_id)

        # 클래스 지정      
        self.menuBtn1.setProperty("class", "menuBtn1 active")
        self.menuBtn2.setProperty("class", "menuBtn2")
        self.menuBtn3.setProperty("class", "menuBtn3")
        self.menuBtn1.clicked.connect(self.clickMenu1)
        self.menuBtn2.clicked.connect(self.clickMenu2)
        self.menuBtn3.clicked.connect(self.clickMenu3)
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

        self.cctv_widget = CCTVWidget(self)
        self.dashboard_widget = DashboardWidget(self)
        self.detect_log_widget = DetectLogWidget(self)
        self.cctv_widget.show_at(QPoint(190, 50))  # 초기 위치 설정
        self.dashboard_widget.show_at(QPoint(190, 50))
        self.detect_log_widget.show_at(QPoint(190, 50))
        self.dashboard_widget.hide()
        self.detect_log_widget.hide()

    def clickMenu1(self):
        self.menuBtn1.setProperty("class", "menuBtn1 active")
        self.menuBtn2.setProperty("class", "menuBtn2")
        self.menuBtn3.setProperty("class", "menuBtn3")
        self.menuBtn1.style().unpolish(self.menuBtn1)   
        self.menuBtn1.style().polish(self.menuBtn1)
        self.menuBtn2.style().unpolish(self.menuBtn2)   
        self.menuBtn2.style().polish(self.menuBtn2)
        self.menuBtn3.style().unpolish(self.menuBtn3)   
        self.menuBtn3.style().polish(self.menuBtn3)
        self.cctv_widget.show()
        self.dashboard_widget.hide()
        self.detect_log_widget.hide()
    
    def clickMenu2(self):
        self.menuBtn1.setProperty("class", "menuBtn1")
        self.menuBtn2.setProperty("class", "menuBtn2 active")
        self.menuBtn3.setProperty("class", "menuBtn3")
        self.menuBtn1.style().unpolish(self.menuBtn1)   
        self.menuBtn1.style().polish(self.menuBtn1)
        self.menuBtn2.style().unpolish(self.menuBtn2)   
        self.menuBtn2.style().polish(self.menuBtn2)
        self.menuBtn3.style().unpolish(self.menuBtn3)   
        self.menuBtn3.style().polish(self.menuBtn3)
        self.cctv_widget.hide()
        self.dashboard_widget.show()
        self.detect_log_widget.hide()
    
    def clickMenu3(self):
        self.menuBtn1.setProperty("class", "menuBtn1")
        self.menuBtn2.setProperty("class", "menuBtn2")
        self.menuBtn3.setProperty("class", "menuBtn3 active")
        self.menuBtn1.style().unpolish(self.menuBtn1)   
        self.menuBtn1.style().polish(self.menuBtn1)
        self.menuBtn2.style().unpolish(self.menuBtn2)   
        self.menuBtn2.style().polish(self.menuBtn2)
        self.menuBtn3.style().unpolish(self.menuBtn3)   
        self.menuBtn3.style().polish(self.menuBtn3)
        self.cctv_widget.hide()
        self.dashboard_widget.hide()
        self.detect_log_widget.show()

    def set_user_info(self, user_info):
        self.user_info = user_info
        self.userBtn.setText(user_info['user_id'])
        self.user_popover.set_user_info(user_info)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    layout_window = LayoutWindow()
    layout_window.show()

    sys.exit(app.exec())