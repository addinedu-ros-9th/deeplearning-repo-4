import sys, os
import time
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

import cv2
import socket
import numpy as np
import struct
import requests
from functools import partial
import sys
import os
import subprocess
import json

from sympy import sec
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.user_info import *

from server.config import CENTRAL_IP, CENTRAL_GUI_PORT

from style import apply_style

class ClipPopupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("video_popup.ui", self)
        self.setObjectName("clipPopup") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.bg.setProperty("class", "video_bg")
        self.video_wrap.setProperty("class", "video_wrap")
        self.duration_bar.setProperty("class", "duration_bar")
        self.current_bar.setProperty("class", "current_bar")
        
        self.video_widget = QVideoWidget(self)
        self.video_widget.setStyleSheet("background-color: black;")
        self.video_layout = QVBoxLayout(self.video_wrap)  # self.bg가 레이아웃 대상이라면
        self.video_layout.addWidget(self.video_widget)
        self.video = QMediaPlayer(self)
        self.video.setVideoOutput(self.video_widget)

        # 버튼 시그널 연결
        self.playBtn.clicked.connect(self.video.play)
        self.pauseBtn.clicked.connect(self.video.pause)
        self.backwardBtn.clicked.connect(self.seek_backward)
        self.forwardBtn.clicked.connect(self.seek_forward)

        # 비디오 길이(밀리초) 변경 시 호출
        self.video.durationChanged.connect(self.on_duration_changed)
        # 현재 재생 위치(밀리초) 변경 시 호출
        self.video.positionChanged.connect(self.on_position_changed)
        self.duration = 0  # 비디오 길이 초기화


    def on_duration_changed(self, duration):
        # duration은 밀리초 단위
        seconds = duration // 1000
        self.end_time.setText(f"{seconds // 60:02}:{seconds % 60:02}")  # MM:SS 형식으로 표시
        self.duration = duration

    def on_position_changed(self, position):
        # position은 밀리초 단위
        seconds = position // 1000
        self.current_time.setText(f"{seconds // 60:02}:{seconds % 60:02}")  # MM:SS 형식으로 표시
        if position == self.duration - 400:
            self.video.setPosition(0)  # 비디오가 끝나면 처음으로 돌아감
            self.video.pause()
            self.current_bar.setStyleSheet(f"width: 0px; min-width: 0px; max-width: 0px;")

        position_ratio = position / self.duration if self.duration > 0 else 0
        # current_bar의 style을 동적으로 변경 (예: 재생 위치에 따라 색상 변경)
        # 예시: position_ratio에 따라 색상 또는 길이 조정
        # self.current_bar.setStyleSheet(f"background-color: rgb({int(255 * position_ratio)}, 100, 100);")
        # 또는 width 조정
        bar_width = int(1300 * position_ratio)
        self.current_bar.setStyleSheet(f"width: {bar_width}px; min-width: {bar_width}px; max-width: {bar_width}px;")
        self.current_bar.style().unpolish(self.current_bar)   
        self.current_bar.style().polish(self.current_bar)

        print(f'{bar_width} : bar_width')

    def seek_backward(self):
        # 5초 뒤로
        pos = max(0, self.video.position() - 5000)
        self.video.setPosition(pos)

    def seek_forward(self):
        # 5초 앞으로
        pos = min(self.video.duration(), self.video.position() + 5000)
        self.video.setPosition(pos)

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()        

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

        self.clip_popup_widget = ClipPopupWidget(self)
        
        # 네트워크 연결 설정
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind(('0.0.0.0', 6007))  # UDP 수신 포트
            self.sock.settimeout(0.1)
            print(f"[CCTV] UDP 수신 대기 중: 0.0.0.0:6007")
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

        # 알림 데이터 새로고침 타이머 (10초마다)
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.get_notification_data)
        self.notification_timer.start(10000)  # 10초마다 실행

        # detect table 설정
        # 열 헤더 설정
        column = ["기록 시점", "불법행위 종류", "녹화 클립"]
        self.original_data = [
            {
                "time": "",
                "event_type": "",
                "video_url": ""
            },
        ]
        self.data = self.original_data.copy()

        self.comboBox.currentIndexChanged.connect(self.dataChange)

        # 테이블 크기 조정
        self.detect_table.setRowCount(len(self.data))  # 데이터 행 개수만큼 설정
        self.detect_table.setColumnCount(len(column))  # 열 개수 설정
        self.detect_table.setHorizontalHeaderLabels(column)

        for row, row_data in enumerate(self.data):
            for col, value in enumerate(row_data.values()):
                if col == 1: # 불법행위 comboBox 종류 열
                    behavior_label = QLabel(value)
                    if value == "broken" : 
                        behavior_label.setProperty("class", "label behavior broken")
                    elif value == "abandon" :
                        behavior_label.setProperty("class", "label behavior abandon")
                    elif value == "theft" :
                        behavior_label.setProperty("class", "label behavior theft")
                    elif value == "light_off" :
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
        self.get_notification_data()
        self.dataChange()     

    def get_notification_data(self):
        url = f"http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/load/notification"
        req_data = {
            "user_id": get_user_id(),
        }
        print("req_data:", req_data)
        try:
            response = requests.post(url, json=req_data)
            if response.status_code == 200:
                result = response.json()
                print("[cctv 알림 - 응답 내용]:", result)
                
                self.original_data = result
                self.data = self.original_data.copy()  # 초기 데이터 복사
                # return result
            else:
                print(f"요청 실패: {response.status_code}")
                return {}
        except requests.RequestException as e:
            print(f"요청 중 오류 발생: {e}")
            return {}

    def dataChange(self):
        if self.comboBox.currentText() == "전체":
            self.data = self.original_data
        elif self.comboBox.currentText() == "파손":
            self.data = [row for row in self.original_data if row.get("event_type") == "broken"]
        elif self.comboBox.currentText() == "유기":
            self.data = [row for row in self.original_data if row.get("event_type") == "abandon"]
        elif self.comboBox.currentText() == "절도":
            self.data = [row for row in self.original_data if row.get("event_type") == "theft"]
        elif self.comboBox.currentText() == "전등 끔":
            self.data = [row for row in self.original_data if row.get("event_type") == "light_off"]

        self.detect_table.setRowCount(len(self.data))  # 필터링된 데이터 행 개수만큼 설정
        print('self.data: ', self.data)
        for row, row_data in enumerate(self.data):
            for col, value in enumerate(row_data.values()):
                if col == 1:  # 불법행위 comboBox 종류 열
                    behavior_label = QLabel(value)
                    if value == "broken":
                        behavior_label.setProperty("class", "label behavior broken")
                        behavior_label.setText("파손")
                    elif value == "abandon":
                        behavior_label.setProperty("class", "label behavior abandon")
                        behavior_label.setText("유기")
                    elif value == "theft":
                        behavior_label.setProperty("class", "label behavior theft")
                        behavior_label.setText("절도")
                    elif value == "light_off":
                        behavior_label.setProperty("class", "label behavior light_off")
                        behavior_label.setText("전등 끔")

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
                    def clip_clicked(tmp_row_data):
                        url = f"http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/load/video"

                        req_data = {
                            "user_id": get_user_id(),
                            "video_url": tmp_row_data['video_url'],  
                        }

                        print("클립 req_data:", req_data)
                        try:
                            response = requests.get(url, params=req_data)
                            if response.status_code == 200:
                                print('비디오 응답 성공')
                                # 응답 파일 타입 확인
                                content_type = response.headers.get('Content-Type', '')
                                print("응답 Content-Type:", content_type)
                                if 'video' not in content_type:
                                    print(f"응답이 비디오가 아닙니다: {content_type}")
                                    return
                                # 화면 중앙에 팝업 표시
                                parent_rect = self.rect()
                                popup_rect = self.clip_popup_widget.rect()
                                center_pos = self.mapToGlobal(parent_rect.center() - popup_rect.center())
                                center_pos.setX(center_pos.x() - 95)
                                center_pos.setY(center_pos.y() - 25)
                                self.clip_popup_widget.show_at(center_pos)

                                # 비디오 수신
                                video_url = f'http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/load/video?video_url={tmp_row_data['video_url']}'
                                print("비디오 URL:", video_url)
                                self.clip_popup_widget.video.setSource(QUrl(video_url))
                                self.clip_popup_widget.video.play()


                                print("[비디오 - 응답 내용]:", response)
                                # self.refresh()  # 테이블 다시 그리기
                                # return result
                            else:
                                print(f"요청 실패: {response.status_code}")
                                return 
                        except requests.RequestException as e:
                            print(f"요청 중 오류 발생: {e}")
                            return 

                    clip_button = QPushButton("")
                    clip_button.setProperty("class", "btn clip small")
                    clip_button.clicked.connect(
                        partial(clip_clicked, row_data)
                    )
                    # 삭제 버튼을 가운데 정렬하기 위한 레이아웃 설정
                    layout = QHBoxLayout()
                    layout.addWidget(clip_button)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                    layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거

                    # 셀에 레이아웃 설정
                    cell_widget = QWidget()
                    cell_widget.setLayout(layout)
                    self.detect_table.setCellWidget(row, col, cell_widget)
                else:  # 기록 시점 열
                    item = QTableWidgetItem(value)
                    self.detect_table.setItem(row, col, item)   

    def showEvent(self, event):
        # 화면에 보일 때만 타이머 시작
        self.timer.start(int(1000 / 10))  # 프레임 수에 맞게 조정
        self.notification_timer.start(10000)  # 알림 타이머 시작
        super().showEvent(event)

    def hideEvent(self, event):
        # 화면에서 사라질 때 타이머 정지
        self.timer.stop()
        self.notification_timer.stop()  # 알림 타이머 정지
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
            
            # 알림 패킷인지 확인 (frame_id가 0인 경우)
            if frame_id == 0:
                try:
                    # JSON 데이터 디코딩
                    notification_json = packet_data.decode('utf-8')
                    notification_data = json.loads(notification_json)
                    
                    # 알림 타입인지 확인
                    if notification_data.get('type') == 'notification':
                        self.process_ai_notification(notification_data)
                        return
                except Exception as e:
                    print(f"[CCTV] 알림 패킷 처리 오류: {e}")
                    return
            
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

    def process_ai_notification(self, notification_data):
        """
        AI 서버로부터 받은 알림 처리
        
        Args:
            notification_data (dict): 알림 데이터
        """
        try:
            event_type = notification_data.get('event_type', 'unknown')
            person_count = notification_data.get('person_count', 0)
            confidence = notification_data.get('confidence', '0.00')
            timestamp = notification_data.get('timestamp', time.time())
            
            # 알림 메시지 생성
            if event_type == "Light_OFF":
                title = "🔦 Light OFF 감지"
                message = f"전등이 꺼진 상태가 감지되었습니다.\n사람 수: {person_count}명\n신뢰도: {confidence}"
            elif event_type == "Theft":
                title = "🚨 절도 행위 감지"
                message = f"절도 행위가 감지되었습니다.\n사람 수: {person_count}명\n신뢰도: {confidence}"
            elif event_type == "Broken":
                title = "🔨 파손 행위 감지"
                message = f"파손 행위가 감지되었습니다.\n사람 수: {person_count}명\n신뢰도: {confidence}"
            elif event_type == "Abandon":
                title = "📦 유기 행위 감지"
                message = f"유기 행위가 감지되었습니다.\n사람 수: {person_count}명\n신뢰도: {confidence}"
            else:
                title = "⚠️ 이상 행위 감지"
                message = f"이상 행위가 감지되었습니다.\n사람 수: {person_count}명\n신뢰도: {confidence}"
            
            print(f"[GUI] AI 서버 알림 수신: {title} - {message}")
            
            # 시스템 알림 전송
            try:
                subprocess.run([
                    'notify-send',
                    title,
                    message,
                    '--urgency=critical',
                    '--icon=dialog-warning'
                ], check=True)
                print(f"[GUI] 시스템 알림 전송: {title} - {message}")
            except subprocess.CalledProcessError as e:
                print(f"[GUI] 알림 전송 실패: {e}")
            except FileNotFoundError:
                print("[GUI] notify-send 명령어를 찾을 수 없습니다.")
            
        except Exception as e:
            print(f"[GUI] 알림 처리 오류: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    cctv_widget = CCTVWidget()
    cctv_widget.show()
    sys.exit(app.exec())