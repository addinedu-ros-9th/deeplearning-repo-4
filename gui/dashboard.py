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

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("dashboard.ui", self)

    def show_at(self, pos):
        """특정 위치에 팝오버 표시"""
        self.move(pos)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = DashboardWidget()
    dashboard.show()
    sys.exit(app.exec())