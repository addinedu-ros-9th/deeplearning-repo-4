import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic

from_class = uic.loadUiType("Test2.ui")[0]

class windowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Test2")

        self.count = 0
        self.pushButton.clicked.connect(self.button_Clicked)
        self.pushButton_2.clicked.connect(self.reset)
        self.pushButton_3.clicked.connect(self.write)
        
        self.label.setText(str(self.count))        

        self.in_lineEdit.textChanged.connect(self.changed)

    def button_Clicked(self):
        self.count += 1
        self.label.setText(str(self.count))

    def reset(self):
        self.count = 0
        self.label.setText(str(self.count))

    def write(self):
        self.label.setText(self.lineEdit.text())

    def changed(self):
        self.out_lineEdit.setText(self.in_lineEdit.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = windowClass()
    myWindow.show()
    
    sys.exit(app.exec())