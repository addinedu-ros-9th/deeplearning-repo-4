import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import cv2
import socket
import numpy as np
import struct

class CCTVWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("cctv.ui", self)
        self.setObjectName("cctvWidget") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.title.setText("GS25 금천점")
        self.comboBox.setStyleSheet("")

        # 네트워크 연결 설정
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.connect(('192.168.0.15', 7007))
        self.sock.connect(('192.168.0.21', 7007))
        self.sock.settimeout(0.1)
        # self.cap = cv2.VideoCapture(0) # 웹캠
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 860)  # 해상도 너비 설정
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 645)  # 해상도 높이 설정

        
        # 프레임 설정
        frame = 10

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / frame)) 


    def recv_full(self, size):
        data = b''
        while len(data) < size:
            packet = self.sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

    def update_frame(self):
        """네트워크로 받은 프레임을 cctv_box에 표시"""
        try:
            # 1. 4바이트 길이 먼저 받기
            length_bytes = self.recv_full(4)
            if not length_bytes:
                print("서버로부터 길이 수신 실패")
                return
            frame_len = struct.unpack('!I', length_bytes)[0]

            # 2. 프레임 데이터 받기
            frame_bytes = self.recv_full(frame_len)
            if not frame_bytes:
                print("서버로부터 프레임 데이터 수신 실패")
                return

            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.cctv_box.width(),
                    self.cctv_box.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
                self.cctv_box.setPixmap(scaled_pixmap)
            else:
                print("프레임 디코딩 실패")
        except socket.timeout:
            pass
        except Exception as e:
            print("프레임 수신 중 오류:", e)
        
        # """Update the webcam feed in the cctv_box."""
        # ret, frame = self.cap.read()
        # if ret:
        #     # RGB 형식으로 변환
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     # QImage로 변환
        #     h, w, ch = frame.shape
        #     bytes_per_line = ch * w
        #     qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        #     pixmap = QPixmap.fromImage(qt_image)

        #     # pixmap 크기 조정
        #     scaled_pixmap = pixmap.scaled(
        #         self.cctv_box.width(),
        #         self.cctv_box.height(),
        #         Qt.AspectRatioMode.KeepAspectRatio
        #     )

        #     # cctv_box에 pixmap 설정
        #     self.cctv_box.setPixmap(scaled_pixmap)
        # else:
        #     print("Failed to capture video frame.")


    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()