from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

colors = {
    "primary" : "#03B4C8",
    "primary_dark" : "#0E9FAF",
    "secondary" : "#345984",
    "therity" : "#F98CAB",
    "fourth" : "#F2CD3B",
    "fourth_dark" : "#D7B017",
    "error" : "#F44336",
}

radius = "2px"

def apply_style(app):
    qss_path = "./style/qss/"
    qss_files = ["layout.qss", 
                 "login.qss",
                 "utils.qss",
                 "component/btn.qss",
                 "component/checkbox.qss",
                 "component/radiobox.qss",
                 "component/divider.qss",
                 "component/textfield.qss",
                 "component/select.qss",
                 "component/spinbox.qss",
                 "component/table.qss",
                 "component/scrollbar.qss",
                 "contents/cctv.qss",
                 "contents/dashboard.qss",
                 "contents/detect_log.qss"]
    style = ""
    for file in qss_files:
        with open(f'{qss_path}{file}', "r") as f:
            style += f.read() + "\n"
    for key, value in colors.items():
        style = style.replace("{{" + key + "}}", value)
    style = style.replace("{{radius}}", radius)
    app.setStyleSheet(style)

    # # 폰트 설정 # 폰트 없는게 더 나은 거 같기도 해서 일단 빼놓겠습니다.
    # font_id = QFontDatabase.addApplicationFont("./style/fonts/Inter-VariableFont.ttf")
    # font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    # font = QFont(font_family)
    # app.setFont(font)