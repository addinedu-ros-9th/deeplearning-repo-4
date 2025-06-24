import sys, os
import time
import PyQt6
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.config import CENTRAL_IP, CENTRAL_PORT
from modules.user_info import *

class LoginWindow(QMainWindow):
    # 로그인 성공 시그널 정의
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gigachad | Login")
        # .ui 파일 로드
        loadUi("login.ui", self)

        # 클래스 변경
        self.login_btn.setProperty("class", "btn contained primary large")
        self.login_checkbox.setProperty("class", "checkbox gray9")
        self.login_div.setProperty("class", "divider ver dotted")
        self.login_div2.setProperty("class", "divider ver dotted")
        self.login_textfield1.setProperty("class", "textfield large")
        self.login_textfield2.setProperty("class", "textfield large")
        self.login_greeting.setProperty("class", "size24 weight700")
        self.login_desc1.setProperty("class", "size16 weight300 color-gray9")
        self.login_desc2.setProperty("class", "size16 weight300 color-gray9")
        self.login_id.setProperty("class", "size14 color-gray3")
        self.login_password.setProperty("class", "size14 color-gray3")

        # pw영역 * 표시
        self.login_textfield2.setEchoMode(QLineEdit.EchoMode.Password)

        # 로그인 버튼 클릭시 이벤트 연결
        self.login_btn.clicked.connect(self.check_login)

        # 텍스트 필드 변경 이벤트 연결
        self.login_textfield1.textChanged.connect(self.textfield1_changed)
        self.login_textfield2.textChanged.connect(self.textfield2_changed)

        # Enter 키 입력 이벤트 연결
        self.login_textfield1.returnPressed.connect(self.check_login)
        self.login_textfield2.returnPressed.connect(self.check_login)

    def textfield1_changed(self):
        self.login_textfield1.setProperty("class", "textfield large")
        self.login_textfield1.style().unpolish(self.login_textfield1)   
        self.login_textfield1.style().polish(self.login_textfield1)
    
    def textfield2_changed(self):
        self.login_textfield2.setProperty("class", "textfield large")
        self.login_textfield2.style().unpolish(self.login_textfield2)   
        self.login_textfield2.style().polish(self.login_textfield2)

    def check_login(self):
        # login_textfield1에 입력된 값 확인
        # id_input = self.login_textfield1.text()
        # pw_input = self.login_textfield2.text()

        # user_exists = check_user_id(id_input)
        # check_pw = check_user_pw(id_input, pw_input)

        # print(f"User input: {id_input}")
        # if user_exists:
        #     if check_pw:
        #         if not self.login_checkbox.isChecked():
        #             self.login_textfield1.clear() # 수정해야됨
        #             self.login_textfield2.clear()
        #         # 로그인 성공 처리
        #         print("Login successful!")
        #         self.login_successful.emit()
        #         set_user(id_input)  # 사용자 정보 가져오기
        #     else : 
        #         print("Invalid password.")
        #         self.login_textfield2.setProperty("class", "textfield large error")
        #         self.login_textfield2.style().unpolish(self.login_textfield2)
        #         self.login_textfield2.style().polish(self.login_textfield2)
        #         self.login_textfield2.update() 
        # else:
        #     print("Invalid username.")
        #     self.login_textfield1.setProperty("class", "textfield large error")
        #     self.login_textfield1.style().unpolish(self.login_textfield1)
        #     self.login_textfield1.style().polish(self.login_textfield1)
        #     self.login_textfield1.update() 
        
        # # 텍스트 필드 포커스 제거
        # self.login_textfield1.clearFocus()
        # self.login_textfield2.clearFocus()

        user_id = self.login_textfield1.text()
        user_pw = self.login_textfield2.text()

        # 서버 요청
        url = f"http://{CENTRAL_IP}:{CENTRAL_PORT}/auth/login"
        data = {
            "user_id": user_id,
            "passwd": user_pw
        }

        print("[로그인 요청 URL]:", url)
        print("[전송 데이터]:", data)

        try:
            response = requests.post(url, json=data)
            print("[응답 코드]:", response.status_code)

            if response.status_code == 200:
                result = response.json()
                print("[응답 내용]:", result)

                # user_info = result.get("user")
                # if not user_info or "user_id" not in user_info:
                #     QMessageBox.warning(self, "오류", "로그인 응답에 사용자 정보가 없습니다.")
                #     return

                # logged_in_user_id = user_info["user_id"]

                # self.label_error.setText("")
                QMessageBox.information(self, "로그인 성공", f"{user_id}님 환영합니다!")
                self.login_successful.emit()
                # self.main_window = MainMonitorWindow(user_id=logged_in_user_id)
                # self.main_window.show()
                # self.close()
            elif response.status_code == 401:
                # 텍스트 필드 포커스 제거
                self.login_textfield1.clearFocus()
                self.login_textfield2.clearFocus()

                error_msg = response.json().get("message", "로그인 실패")
                print(f'ID 오류 : {error_msg}')

                # 실패 메세지 표시
                self.login_textfield1.setProperty("class", "textfield large error")
                self.login_textfield1.style().unpolish(self.login_textfield1)
                self.login_textfield1.style().polish(self.login_textfield1)
                self.login_textfield1.update() 
            elif response.status_code == 402:
                # 텍스트 필드 포커스 제거
                self.login_textfield1.clearFocus()
                self.login_textfield2.clearFocus()

                error_msg = response.json().get("message", "로그인 실패")
                print(f'PW 오류 : {error_msg}')

                # 실패 메세지 표시
                self.login_textfield2.setProperty("class", "textfield large error")
                self.login_textfield2.style().unpolish(self.login_textfield2)
                self.login_textfield2.style().polish(self.login_textfield2)
                self.login_textfield2.update()

        except Exception as e:
            print("[네트워크 예제]:", str(e))
            QMessageBox.critical(self, "네트워크 오류", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LoginWindow()
    main.show()
    sys.exit(app.exec())