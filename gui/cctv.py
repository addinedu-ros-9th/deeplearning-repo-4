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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.config import CENTRAL_IP, CENTRAL_PORT

from style import apply_style

class CCTVWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("cctv.ui", self)
        self.setObjectName("cctvWidget") 
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.title.setText("GS25 금천점")
        self.comboBox.setStyleSheet("")
        
        self.detect_table.setProperty("class", "table small")
        
        # 네트워크 연결 설정
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((CENTRAL_IP, 7007))
        # self.sock.connect(('192.168.0.21', 7007))
        self.sock.settimeout(0.1)
        # self.cap = cv2.VideoCapture(0) # 웹캠
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 860)  # 해상도 너비 설정
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 645)  # 해상도 높이 설정

        
        # 프레임 설정
        frame = 10

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        # self.timer.start(int(1000 / frame)) 

        # detect table 설정
        # 열 헤더 설정
        column = ["기록 시점", "불법행위 종류", "녹화 클립"]
        original_data = [
            ["2023-06-21 14:30", "파손", "./video01.mp4"],
            ["2023-06-21 14:30", "유기", "./video01.mp4"],
            ["2023-06-21 14:30", "파손", "./video01.mp4"],
            ["2023-06-21 14:30", "전등 끔", "./video01.mp4"],
            ["2023-06-21 14:30", "절도", "./video01.mp4"],
            ["2023-06-21 14:30", "파손", "./video01.mp4"],
            ["2023-06-21 14:30", "유기", "./video01.mp4"],
            ["2023-06-21 14:30", "파손", "./video01.mp4"],
            ["2023-06-21 14:30", "전등 끔", "./video01.mp4"],
            ["2023-06-21 14:30", "절도", "./video01.mp4"],
            ["2023-06-21 14:30", "파손", "./video01.mp4"],
            ["2023-06-21 14:30", "유기", "./video01.mp4"],
            ["2023-06-21 14:30", "파손", "./video01.mp4"],
            ["2023-06-21 14:30", "전등 끔", "./video01.mp4"],
            ["2023-06-21 14:30", "절도", "./video01.mp4"],
        ]
        self.data = original_data.copy()

        def dataChange():
            if self.comboBox.currentText() == "전체":
                self.data = original_data.copy()
            elif self.comboBox.currentText() == "파손":
                self.data = [row for row in original_data if row[1] == "파손"]
            elif self.comboBox.currentText() == "유기":
                self.data = [row for row in original_data if row[1] == "유기"]
            elif self.comboBox.currentText() == "절도":
                self.data = [row for row in original_data if row[1] == "절도"]
            elif self.comboBox.currentText() == "전등 끔":
                self.data = [row for row in original_data if row[1] == "전등 끔"]

            self.detect_table.setRowCount(len(self.data))  # 필터링된 데이터 행 개수만큼 설정
            
            for row, row_data in enumerate(self.data):
                for col, value in enumerate(row_data):
                    if col == 1:  # 불법행위 comboBox 종류 열
                        behavior_label = QLabel(value)
                        if value == "파손":
                            behavior_label.setProperty("class", "label behavior broken")
                        elif value == "유기":
                            behavior_label.setProperty("class", "label behavior abandon")
                        elif value == "절도":
                            behavior_label.setProperty("class", "label behavior theft")
                        elif value == "전등 끔":
                            behavior_label.setProperty("class", "label behavior light_off")

                        behavior_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬

                        layout = QHBoxLayout()
                        layout.addWidget(behavior_label)
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거

                        # 셀에 레이아웃 설정
                        cell_widget = QWidget()
                        cell_widget.setLayout(layout)
                        self.detect_table.setCellWidget(row, col, cell_widget)
                    elif col == 2:  # 녹화 클립 열
                        delete_button = QPushButton("")
                        delete_button.setProperty("class", "btn clip small")
                        # 삭제 버튼을 가운데 정렬하기 위한 레이아웃 설정
                        layout = QHBoxLayout()
                        layout.addWidget(delete_button)
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거

                        # 셀에 레이아웃 설정
                        cell_widget = QWidget()
                        cell_widget.setLayout(layout)
                        self.detect_table.setCellWidget(row, col, cell_widget)
                    else:  # 기록 시점 열
                        item = QTableWidgetItem(value)
                        self.detect_table.setItem(row, col, item)

        self.comboBox.currentIndexChanged.connect(dataChange)

        # 테이블 크기 조정
        self.detect_table.setRowCount(len(self.data))  # 데이터 행 개수만큼 설정
        self.detect_table.setColumnCount(len(column))  # 열 개수 설정
        self.detect_table.setHorizontalHeaderLabels(column)

        for row, row_data in enumerate(self.data):
            for col, value in enumerate(row_data):
                if col == 1: # 불법행위 comboBox 종류 열
                    behavior_label = QLabel(value)
                    if value == "파손" : 
                        behavior_label.setProperty("class", "label behavior broken")
                    elif value == "유기" :
                        behavior_label.setProperty("class", "label behavior abandon")
                    elif value == "절도" :
                        behavior_label.setProperty("class", "label behavior theft")
                    elif value == "전등 끔" :
                        behavior_label.setProperty("class", "label behavior light_off")
                        
                    behavior_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬

                    layout = QHBoxLayout()
                    layout.addWidget(behavior_label)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                    layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
                    
                    # 셀에 레이아웃 설정
                    cell_widget = QWidget()
                    cell_widget.setLayout(layout)
                    self.detect_table.setCellWidget(row, col, cell_widget)
                elif col == 2:  # 녹화 클립 열
                    delete_button = QPushButton("")
                    delete_button.setProperty("class", "btn clip small")
                     # 삭제 버튼을 가운데 정렬하기 위한 레이아웃 설정
                    layout = QHBoxLayout()
                    layout.addWidget(delete_button)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                    layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
                    
                    # 셀에 레이아웃 설정
                    cell_widget = QWidget()
                    cell_widget.setLayout(layout)
                    self.detect_table.setCellWidget(row, col, cell_widget)

                else:  # 기록 시점 열
                    item = QTableWidgetItem(value)
                    # label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.detect_table.setItem(row, col, item)

        column_widths = [100, 80, 24]
        for i, width in enumerate(column_widths):
            self.detect_table.setColumnWidth(i, width)
        
        # 특정 열을 화면 크기에 맞게 늘어나도록 설정
        self.detect_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 첫 번째 열

        # 헤더 숨기기
        self.detect_table.horizontalHeader().setVisible(False)  # 열 헤더 숨기기
        # 행 번호 숨기기
        self.detect_table.verticalHeader().setVisible(False)
        # 그리드 라인 제거
        self.detect_table.setShowGrid(False) 

    def showEvent(self, event):
        # 화면에 보일 때만 타이머 시작
        self.timer.start(int(1000 / 10))  # 프레임 수에 맞게 조정
        super().showEvent(event)

    def hideEvent(self, event):
        # 화면에서 사라질 때 타이머 정지
        self.timer.stop()
        super().hideEvent(event)

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
            print("데이터 수신 대기 시간 초과... 서버로부터 데이터가 오고 있는지 확인하세요.")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    cctv_widget = CCTVWidget()
    cctv_widget.show()
    sys.exit(app.exec())