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

from matplotlib.figure import Figure  # Figure 임포트
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 

from style import apply_style
from style import colors as c

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("dashboard.ui", self)
        self.text1.setProperty("class", "size18 weight700")
        self.text2.setProperty("class", "size18 weight700")
        self.year1.setProperty("class", "spinbox small")
        self.month1.setProperty("class", "spinbox small")
        self.date1.setProperty("class", "spinbox small")
        self.text_year.setProperty("class", "color-gray6 size12 weight300")
        self.text_month.setProperty("class", "color-gray6 size12 weight300")
        self.text_date.setProperty("class", "color-gray6 size12 weight300")
        self.end_date.setProperty("class", "textfield small readonly")
        self.divider1.setProperty("class", "bg grayc")
        self.graph_container.setProperty("class", "radius otlc")

        self.plot_widget = QVBoxLayout(self.graph_container)
        self.canvas = FigureCanvas(Figure(figsize=(4, 4)))
        self.plot_widget.addWidget(self.canvas)

        labels = ["파손", "유기", "절도", "전등 끔"]
        colors = [c["primary"], c["secondary"], c["therity"], c["fourth"]]

        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.pie(
            [45, 27, 18, 10],
            labels=None,
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.3)  # 가운데 구멍 크기 설정
        )
        self.ax.set_aspect('equal')

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS 파일 로드
    apply_style(app)

    dashboard = DashboardWidget()
    dashboard.show()
    sys.exit(app.exec())