import sys, os
import time
import PyQt6
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class Main(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label_widget = QLabel("Hello, PyQt6!")
        button_widget = QPushButton("Click Me")
        combobox_widget = QComboBox()
        combobox_widget.addItems(["Option 1", "Option 2", "Option 3"])
        combobox_widget.setEditable(True)
        checkbox_widget = QCheckBox("Check me")
        checkbox_widget2 = QCheckBox("Check me2")
        radiobox_widget = QRadioButton("Radio me")
        radiobox_widget2 = QRadioButton("Radio me2")
        spinbox_widget = QSpinBox()
        date_widget = QDateEdit()
        time_widget = QTimeEdit()
        date_widget.setDate(QDate.currentDate())
        time_widget.setTime(QTime.currentTime())
        date_widget.setDisplayFormat("yyyy-MM-dd")
        time_widget.setDisplayFormat("HH:mm:ss")
        date_widget.setCalendarPopup(True)
        time_widget.setCalendarPopup(True)
        list_widget = QListWidget()
        list_widget.addItems(["Item 1", "Item 2", "Item 3"])
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        list_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        list_widget.setDragEnabled(True)
        list_widget.setAcceptDrops(True)
        list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        list_widget.setDropIndicatorShown(True)
        list_widget.setAlternatingRowColors(True)
    

        layout.addWidget(label_widget)
        layout.addWidget(button_widget)
        layout.addWidget(combobox_widget)
        layout.addWidget(checkbox_widget)
        layout.addWidget(checkbox_widget2)  
        layout.addWidget(radiobox_widget)
        layout.addWidget(radiobox_widget2)
        layout.addWidget(spinbox_widget)
        layout.addWidget(date_widget)
        layout.addWidget(time_widget)
        layout.addWidget(list_widget)

        self.setLayout(layout)

        self.resize(1920, 1080)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())