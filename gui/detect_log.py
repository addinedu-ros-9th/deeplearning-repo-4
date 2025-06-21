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

from style import apply_style

class HorizontalLineDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # 기본 렌더링
        super().paint(painter, option, index)

        # 수평선만 그림
        painter.save()
        pen = QPen(QColor("#cccccc"))
        pen.setWidth(1)
        painter.setPen(pen)

        rect = option.rect

        # bottom만 그림
        painter.drawLine(rect.bottomLeft(), rect.bottomRight()) # 아래쪽 선

        painter.restore()


class DetectLogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("detect_log.ui", self)

        # 클래스 변경
        self.toggle_bg.setProperty("class", "radius bg graye")
        self.text1.setProperty("class", "color-black size14 weight700")
        self.text2.setProperty("class", "color-black size14 weight700")
        self.text3.setProperty("class", "color-black size14 weight700")
        self.toggle1.setProperty("class", "toggle") # 토글 버튼 오늘 
        self.toggle2.setProperty("class", "toggle active") # 토글 버튼 주간
        self.toggle3.setProperty("class", "toggle") # 토글 버튼 월간
        self.filter_bg.setProperty("class", "radius bg grayf5") # 토글 버튼 월간
        self.checkbox1.setProperty("class", "checkbox") # 파손 체크박스
        self.checkbox2.setProperty("class", "checkbox") # 유기 체크박스
        self.checkbox3.setProperty("class", "checkbox") # 절도 체크박스
        self.checkbox4.setProperty("class", "checkbox") # 전등 끔 체크박스
        self.checkbox1.setChecked(True)
        self.checkbox2.setChecked(True)
        self.checkbox3.setChecked(True)
        self.checkbox4.setChecked(True) 
        self.human_min.setProperty("class", "spinbox") # 사람 수 스핀박스
        self.human_max.setProperty("class", "spinbox")
        self.range1.setProperty("class", "align-center")
        self.range2.setProperty("class", "align-center")
        self.radio1.setProperty("class", "radiobox")
        self.radio2.setProperty("class", "radiobox")
        self.radio3.setProperty("class", "radiobox")
        self.radio1.setChecked(True) 
        self.detect_table.setProperty("class", "table") 

        # human_min 값 변경 시 이벤트 연결
        self.human_min.valueChanged.connect(self.on_human_min_changed)
        self.human_max.valueChanged.connect(self.on_human_max_changed)

        # 테이블 설정
        self.detect_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)# 테이블 수정 비활성화
        self.detect_table.setShowGrid(False) # 그리드 라인 제거
        # 수평선만 있는 델리게이트 적용
        delegate = HorizontalLineDelegate()
        self.detect_table.setItemDelegate(delegate)

        # 열 헤더 설정
        column = ["매장 명", "기록 시점", "불법행위 종류", "사람 수", "확인 여부", "녹화 클립", "삭제"]
        # 데이터 추가
        data = [
            ["GS25 금천점", "2023-06-21 14:30", "파손", "3", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 15:00", "유기", "2", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 15:30", "절도", "5", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
            ["GS25 금천점", "2023-06-21 16:00", "전등 끔", "1", "확인", "클립 보기", "삭제"],
        ]
        # 행 번호 숨기기
        self.detect_table.verticalHeader().setVisible(False)
        
        # 테이블 크기 조정
        self.detect_table.setRowCount(len(data))  # 데이터 행 개수만큼 설정
        self.detect_table.setColumnCount(len(column))  # 열 개수 설정
        self.detect_table.setHorizontalHeaderLabels(column)

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 텍스트 가운데 정렬
                self.detect_table.setItem(row, col, item)

        # 열 너비 설정
        column_widths = [194, 194, 194, 194, 200, 140, 100]
        for i, width in enumerate(column_widths):
            self.detect_table.setColumnWidth(i, width)
        
        # 특정 열을 화면 크기에 맞게 늘어나도록 설정
        self.detect_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 첫 번째 열
        self.detect_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 두 번째 열
        self.detect_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 세 번째 열
        self.detect_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 네 번째 열

    def on_human_min_changed(self, value):
        if value > self.human_max.value():
            self.human_max.setValue(value)

    def on_human_max_changed(self, value):
        if value < self.human_min.value():
            self.human_min.setValue(value)

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)
    
    widget = DetectLogWidget()
    widget.show_at(QPoint(100, 100))  # 예시 위치
    sys.exit(app.exec())