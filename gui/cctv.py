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
import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.user_info import *

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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind(('0.0.0.0', 5006))  # UDP 수신 포트
            self.sock.settimeout(0.1)
            print(f"[CCTV] UDP 수신 대기 중: 0.0.0.0:5006")
        except Exception as e:
            print(f"[CCTV] UDP 소켓 설정 실패: {e}")
            self.sock = None
            
        # 프레임 재조립을 위한 버퍼
        self.frame_buffers = {}  # {frame_id: {packet_idx: data, ...}}
        
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
        self.original_data = [
            {
                "event_type": "broken",
                "time": "2025-06-23 16:00:00",
                "video_url": "video_201.mp4"
            },
            {
                "event_type": "theft",
                "time": "2025-06-23 18:30:00",
                "video_url": "video_202.mp4"
            },
            {
                "event_type": "abandon",
                "time": "2025-06-23 22:45:00",
                "video_url": "video_203.mp4"
            },
            {
                "event_type": "light_off",
                "time": "2025-06-24 03:15:00",
                "video_url": "video_204.mp4"
            }
        ]
        self.data = self.original_data.copy()

        self.comboBox.currentIndexChanged.connect(self.dataChange)

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

    def refresh(self):
        print("cctv refesh")
        self.title.setText(get_user_info()['store_name'])
        self.original_data = self.get_notification_data()
        self.dataChange()

    def dataChange(self):
        if self.comboBox.currentText() == "전체":
            self.data = self.original_data.copy()
        elif self.comboBox.currentText() == "파손":
            self.data = [row for row in self.original_data if row[1] == "파손"]
        elif self.comboBox.currentText() == "유기":
            self.data = [row for row in self.original_data if row[1] == "유기"]
        elif self.comboBox.currentText() == "절도":
            self.data = [row for row in self.original_data if row[1] == "절도"]
        elif self.comboBox.currentText() == "전등 끔":
            self.data = [row for row in self.original_data if row[1] == "전등 끔"]

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

    def get_notification_data(self):
        url = f"http://{CENTRAL_IP}:{CENTRAL_PORT}/load/notification"
        req_data = {
            "user_id": get_user_id(),
        }
        print("req_data:", req_data)
        try:
            response = requests.post(url, json=req_data)
            print("response.text:", response.text)  # 응답 원문 출력
            if response.status_code == 200:
                result = response.json()
                print("[cctv 알림 - 응답 내용]:", result)
                self.original_data = result.get('data', [])
                # return result.get('data', {})
            else:
                print(f"요청 실패: {response.status_code}")
                return {}
        except requests.RequestException as e:
            print(f"요청 중 오류 발생: {e}")
            return {}


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
        """UDP로 받은 프레임을 cctv_box에 표시 (패킷 재조립 방식)"""
        # 소켓이 연결되지 않은 경우 처리
        if self.sock is None:
            print("[CCTV] 소켓이 연결되지 않음 - 프레임 업데이트 건너뜀")
            return
            
        try:
            # UDP로 패킷 수신
            packet_info = self.receive_frame_udp_packetized()
            if packet_info is None:
                return
            
            frame_id = packet_info['frame_id']
            packet_idx = packet_info['packet_idx']
            num_packets = packet_info['num_packets']
            packet_data = packet_info['packet_data']
            timestamp = packet_info['timestamp']
            
            # 프레임 버퍼에 패킷 추가
            if frame_id not in self.frame_buffers:
                self.frame_buffers[frame_id] = {'num_packets': num_packets, 'packets': {}, 'timestamp': timestamp}
            
            self.frame_buffers[frame_id]['packets'][packet_idx] = packet_data
            
            # 모든 패킷이 수신되었는지 확인
            if len(self.frame_buffers[frame_id]['packets']) == num_packets:
                # 프레임 재조립
                frame_data = self.reassemble_frame(frame_id, self.frame_buffers[frame_id])
                if frame_data is not None:
                    # 딜레이 계산
                    current_time = time.time()
                    delay = current_time - timestamp
                    delay_text = f"Delay: {delay*1000:.2f} ms"
                    
                    print(f"[CCTV] 프레임 재조립 완료: 프레임 {frame_id}, 크기: {len(frame_data)} bytes, {delay_text}")
                    
                    # 프레임 디코딩 및 표시
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        # 딜레이 정보를 프레임 우하단에 표시
                        h, w = frame.shape[:2]
                        cv2.putText(frame, delay_text, (w - 200, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        
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
                
                # 완성된 프레임 버퍼 삭제
                del self.frame_buffers[frame_id]
            
            # 오래된 프레임 버퍼 정리
            current_frame_id = max(self.frame_buffers.keys()) if self.frame_buffers else 0
            old_frames = [fid for fid in self.frame_buffers.keys() if fid < current_frame_id - 10]
            for old_frame in old_frames:
                del self.frame_buffers[old_frame]
                
        except socket.timeout:
            # UDP 타임아웃은 정상적인 상황이므로 출력하지 않음
            pass
        except Exception as e:
            print("프레임 수신 중 오류:", e)

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

    def reassemble_frame(self, frame_id, packets_info):
        """패킷들을 재조립하여 완전한 프레임 생성"""
        num_packets = packets_info['num_packets']
        packets = packets_info['packets']
        
        # 모든 패킷이 수신되었는지 확인
        if len(packets) != num_packets:
            return None
        
        # 패킷들을 순서대로 결합
        frame_data = b''
        for i in range(num_packets):
            if i in packets:
                frame_data += packets[i]
            else:
                print(f"프레임 {frame_id}의 패킷 {i}번 누락됨.")
                return None  # 패킷 누락
        
        return frame_data

    def receive_frame_udp_packetized(self):
        """패킷 분할 방식으로 UDP 프레임 수신"""
        try:
            data, addr = self.sock.recvfrom(65536)
            
            if len(data) < 24:  # 헤더 크기: 8(double) + 4*4 = 24
                return None
            
            # 패킷 헤더 파싱: [timestamp(8bytes), frame_id(4bytes), packet_idx(4bytes), num_packets(4bytes), data_size(4bytes)]
            header = data[:24]
            timestamp, frame_id, packet_idx, num_packets, data_size = struct.unpack('!dIIII', header)
            packet_data = data[24:24+data_size]
            
            return {
                'timestamp': timestamp,
                'frame_id': frame_id,
                'packet_idx': packet_idx,
                'num_packets': num_packets,
                'packet_data': packet_data,
                'addr': addr
            }
        except socket.timeout:
            return None
        except Exception as e:
            print(f"UDP 수신 오류: {e}")
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    cctv_widget = CCTVWidget()
    cctv_widget.show()
    sys.exit(app.exec())