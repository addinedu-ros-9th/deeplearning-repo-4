import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import cv2

class CCTVWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("cctv.ui", self)
        self.setObjectName("cctvWidget") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.title.setText("GS25 금천점")
        self.comboBox.setStyleSheet("")
        
        # 프레임 설정
        frame = 10

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / frame)) 

        self.cap = cv2.VideoCapture(0) # 웹캠
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 860)  # 해상도 너비 설정
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 645)  # 해상도 높이 설정

    def update_frame(self):
        """Update the webcam feed in the cctv_box."""
        ret, frame = self.cap.read()
        if ret:
            # RGB 형식으로 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # QImage로 변환
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # pixmap 크기 조정
            scaled_pixmap = pixmap.scaled(
                self.cctv_box.width(),
                self.cctv_box.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )

            # cctv_box에 pixmap 설정
            self.cctv_box.setPixmap(scaled_pixmap)
        else:
            print("Failed to capture video frame.")


    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()