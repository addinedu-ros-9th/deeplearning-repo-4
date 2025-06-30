import sys, os
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

import sys
import os

from sympy import sec
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.user_info import *

from server.config import CENTRAL_IP, CENTRAL_GUI_PORT

from style import apply_style

class VideoPopupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("video_popup.ui", self)
        self.setObjectName("videoPopup") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.bg.setProperty("class", "video_bg")
        self.video_wrap.setProperty("class", "video_wrap")
        self.duration_bar.setProperty("class", "duration_bar")
        self.current_bar.setProperty("class", "current_bar")
        self.playBtn.setProperty("class", "playBtn pause")
        self.backwardBtn.setProperty("class", "backwardBtn")
        self.forwardBtn.setProperty("class", "forwardBtn")

        
        self.video_widget = QVideoWidget(self)
        self.video_widget.setStyleSheet("background-color: black;")
        self.video_layout = QVBoxLayout(self.video_wrap)  # self.bg가 레이아웃 대상이라면
        self.video_layout.addWidget(self.video_widget)
        self.video = QMediaPlayer(self)
        self.video.setVideoOutput(self.video_widget)

        # 버튼 시그널 연결
        self.playBtn.clicked.connect(self.video.play)
        # self.pauseBtn.clicked.connect(self.video.pause)
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