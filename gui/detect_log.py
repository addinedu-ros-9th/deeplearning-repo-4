import sys, os
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from functools import partial
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 사용자 모듈
from modules.user_info import *
from video_popup import VideoPopupWidget
from server.config import CENTRAL_IP, CENTRAL_GUI_PORT
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
        self.toggle1.setProperty("class", "toggle") # 토글 버튼 오늘 
        self.toggle2.setProperty("class", "toggle active") # 토글 버튼 주간
        self.toggle3.setProperty("class", "toggle") # 토글 버튼 월간
        self.text_year1.setProperty("class", "color-gray6 size12 weight300")
        self.text_year2.setProperty("class", "color-gray6 size12 weight300")
        self.text_month1.setProperty("class", "color-gray6 size12 weight300")
        self.text_month2.setProperty("class", "color-gray6 size12 weight300")
        self.text_date1.setProperty("class", "color-gray6 size12 weight300")
        self.text_date2.setProperty("class", "color-gray6 size12 weight300")
        self.year1.setProperty("class", "spinbox small") # 연도 스핀박스
        self.year2.setProperty("class", "spinbox small") # 연도 스핀박스
        self.month1.setProperty("class", "spinbox small") # 월 스핀박스
        self.month2.setProperty("class", "spinbox small") # 월 스핀박스
        self.date1.setProperty("class", "spinbox small") # 일 스핀박스
        self.date2.setProperty("class", "spinbox small") # 일 스핀박
        self.filter_bg.setProperty("class", "radius bg grayf5") # 토글 버튼 월간
        self.checkbox1.setProperty("class", "checkbox") # 파손 체크박스
        self.checkbox2.setProperty("class", "checkbox") # 유기 체크박스
        self.checkbox3.setProperty("class", "checkbox") # 절도 체크박스
        self.checkbox4.setProperty("class", "checkbox") # 전등 끔 체크박스
        self.checkbox1.setChecked(True)
        self.checkbox2.setChecked(True)
        self.checkbox3.setChecked(True)
        self.checkbox4.setChecked(True) 
        # self.human_min.setProperty("class", "spinbox") # 사람 수 스핀박스
        # self.human_max.setProperty("class", "spinbox")
        self.range1.setProperty("class", "align-center")
        # self.range2.setProperty("class", "align-center")
        self.radio1.setProperty("class", "radiobox") # 전체
        self.radio2.setProperty("class", "radiobox") # 확인 완료
        self.radio3.setProperty("class", "radiobox") # 미확인
        self.radio1.setChecked(True) 
        self.detect_table.setProperty("class", "table") 
        self.search_btn.setProperty("class", "btn outlined primary weight700") # 검색 버튼

        self.period =  "week"

        self.video_popup_widget = VideoPopupWidget(self)
        
        # human_min 값 변경 시 이벤트 연결
        # self.human_min.valueChanged.connect(self.on_human_min_changed)
        # self.human_max.valueChanged.connect(self.on_human_max_changed)

        # 테이블 설정
        self.detect_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)# 테이블 수정 비활성화
        self.detect_table.setShowGrid(False) # 그리드 라인 제거
        # 수평선만 있는 델리게이트 적용
        delegate = HorizontalLineDelegate()
        self.detect_table.setItemDelegate(delegate)

        # 열 헤더 설정
        column = ["매장 명", "기록 시점", "불법행위 종류", "사람 수", "확인 여부", "녹화 클립", "삭제"]
        # 데이터 추가
        self.data = [
            {
                "store_name": "GS 금천점",
                "time": "2025-01-01 12:00:00",
                "event_type": "broken",
                "person_count": str(2),
                "is_checked": 0,
                "video_url": "video_34.mp4"
            }
        ]
        # 행 번호 숨기기
        self.detect_table.verticalHeader().setVisible(False)
        
        # 테이블 크기 조정
        self.detect_table.setColumnCount(len(column))  # 열 개수 설정
        self.detect_table.setHorizontalHeaderLabels(column)

        # 열 너비 설정
        column_widths = [194, 194, 194, 194, 200, 140, 100]
        for i, width in enumerate(column_widths):
            self.detect_table.setColumnWidth(i, width)
        
        # 특정 열을 화면 크기에 맞게 늘어나도록 설정
        self.detect_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 첫 번째 열
        self.detect_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 두 번째 열
        self.detect_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 세 번째 열
        self.detect_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 네 번째 열

        # 오늘 / 주간 / 월간 토글 버튼 클릭 이벤트 연결
        self.toggle1.clicked.connect(self.click_toggle1)
        self.toggle2.clicked.connect(self.click_toggle2)
        self.toggle3.clicked.connect(self.click_toggle3)
        self.year1.valueChanged.connect(self.change_date)
        self.year2.valueChanged.connect(self.change_date)
        self.month1.valueChanged.connect(self.change_date)
        self.month2.valueChanged.connect(self.change_date)
        self.date1.valueChanged.connect(self.change_date)
        self.date2.valueChanged.connect(self.change_date)
        self.search_btn.clicked.connect(self.refresh)

        self.refresh()

    def refresh(self):
        print("detect_log refesh")
        # self.title.setText(get_user_info()['store_name'])
        self.get_table_data()
        self.drawTable()

    def get_table_data(self):
        url = f"http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/load/detect_log/filter"

        def get_date(year, month, date):
            if self.period is None:
                if month < 10:
                    month1 = f"0{month}"
                else:
                    month1 = month

                if date < 10:
                    date1 = f"0{date}"
                else:
                    date1 = date    
                return f"{year}-{month1}-{date1}"
            else:
                return None
        
        def get_is_checked():
            if self.radio1.isChecked():
                return [0, 1]  # 전체
            elif self.radio2.isChecked():
                return [1]  # 확인 완료
            elif self.radio3.isChecked():
                return [0]
            return None

        req_data = {
            "user_id": get_user_id(),
            "period": self.period,  
            "start_date": get_date(self.year1.value(), self.month1.value(), self.date1.value()),
            "end_date": get_date(self.year2.value(), self.month2.value(), self.date2.value()),
            "event_type": [
                "broken" if self.checkbox1.isChecked() else '',
                "abandon" if self.checkbox2.isChecked() else '',
                "theft" if self.checkbox3.isChecked() else '',
                "light_off" if self.checkbox4.isChecked() else ''
            ],
            "is_checked": get_is_checked()
        }
        # None 값 제거
        req_data["event_type"] = [e for e in req_data["event_type"] if e is not None]
        print("req_data:", req_data)
        try:
            response = requests.post(url, json=req_data)
            if response.status_code == 200:
                result = response.json()
                print("[cctv 알림 - 응답 내용]:", result)
                self.data = result
                # return result
            else:
                print(f"요청 실패: {response.status_code}")
                return 
        except requests.RequestException as e:
            print(f"요청 중 오류 발생: {e}")
            return 
        
    def drawTable(self):
        self.detect_table.setRowCount(len(self.data))  # 데이터 행 개수만큼 설정
        for row, row_data in enumerate(self.data):
            for col, value in enumerate(row_data.values()):
                if col == 2: # 불법행위 comboBox 종류 열
                    if row_data['is_checked'] == 1:
                        behavior_label = QLabel(value)
                        if value == "broken" : 
                            behavior_label.setProperty("class", "label behavior broken")
                            behavior_label.setText("파손")
                        elif value == "abandon" :
                            behavior_label.setProperty("class", "label behavior abandon")
                            behavior_label.setText("유기")
                        elif value == "theft" :
                            behavior_label.setProperty("class", "label behavior theft")
                            behavior_label.setText("절도")
                        elif value == "light_off" :
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

                    else:
                        combo_box = QComboBox()
                        combo_box.addItems(["파손", "유기", "절도", "전등 끔"])
                        combo_box.setProperty("class", "comboBox behavior")
                        if value == "broken" : 
                            combo_box.setCurrentText("파손")
                        elif value == "abandon" :
                            combo_box.setCurrentText("유기")
                        elif value == "theft" :
                            combo_box.setCurrentText("절도")
                        elif value == "light_off" :
                            combo_box.setCurrentText("전등 끔")

                        combo_confirm_button = QPushButton("변경")
                        combo_confirm_button.setProperty("class", "btn comfirm")
                        
                        def change_value(tmp_row_data, combo_box, combo_confirm_button):
                            if combo_box.currentText() == "파손":
                                tmp_behavior = "broken"
                            elif combo_box.currentText() == "유기":
                                tmp_behavior = "abandon"
                            elif combo_box.currentText() == "절도":
                                tmp_behavior = "theft"
                            elif combo_box.currentText() == "전등 끔":
                                tmp_behavior = "light_off"
                             
                            if tmp_behavior == tmp_row_data['event_type']:
                                combo_confirm_button.setProperty("class", "btn comfirm")
                                combo_confirm_button.style().unpolish(combo_confirm_button)   
                                combo_confirm_button.style().polish(combo_confirm_button)
                            else:
                                combo_confirm_button.setProperty("class", "btn comfirm changed")
                                combo_confirm_button.style().unpolish(combo_confirm_button)   
                                combo_confirm_button.style().polish(combo_confirm_button)

                        combo_box.currentIndexChanged.connect(
                            partial(change_value, row_data, combo_box, combo_confirm_button)
                        )

                        def confirm_clicked(tmp_row_data, combo_box):
                            if combo_box.currentText() == "파손":
                                changed_behavior = "broken"
                            elif combo_box.currentText() == "유기":
                                changed_behavior = "abandon"
                            elif combo_box.currentText() == "절도":
                                changed_behavior = "theft"
                            elif combo_box.currentText() == "전등 끔":
                                changed_behavior = "light_off"
                             
                            if changed_behavior != tmp_row_data['event_type']:
                                url = f"http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/change/event_type"

                                req_data = {
                                    "user_id": get_user_id(),
                                    "store_name": get_user_info()['store_name'],  
                                    "timestamp": tmp_row_data['time'],
                                    "event_type": changed_behavior,
                                }

                                print("변경 req_data:", req_data)
                                try:
                                    response = requests.post(url, json=req_data)
                                    if response.status_code == 200:
                                        result = response.json()
                                        print("[변경 - 응답 내용]:", result)
                                        self.refresh()  # 테이블 다시 그리기
                                        # return result
                                    else:
                                        print(f"요청 실패: {response.status_code}")
                                        return 
                                except requests.RequestException as e:
                                    print(f"요청 중 오류 발생: {e}")
                                    return 


                        
                        combo_confirm_button.clicked.connect(
                            partial(confirm_clicked, row_data, combo_box)
                        )

                        layout = QHBoxLayout()
                        layout.addWidget(combo_box)
                        layout.addWidget(combo_confirm_button)
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거

                        # 셀에 레이아웃 설정
                        cell_widget = QWidget()
                        cell_widget.setLayout(layout)
                        self.detect_table.setCellWidget(row, col, cell_widget)

                elif col == 4:  # 확인 여부 열
                    if value == 1 :
                        confirm_label = QLabel("확인 완료")
                        confirm_label.setProperty("class", "label confirm")
                        confirm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬

                        layout = QHBoxLayout()
                        layout.addWidget(confirm_label)
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
                        
                        # 셀에 레이아웃 설정
                        cell_widget = QWidget()
                        cell_widget.setLayout(layout)
                        self.detect_table.setCellWidget(row, col, cell_widget)
                    else:
                        confirm_label = QLabel("미확인")
                        confirm_label.setProperty("class", "label unconfirm")
                        confirm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬

                        confirm_button = QPushButton("불법 확정")
                        confirm_button.setProperty("class", "btn confirm")

                        def confirm_clicked(tmp_row_data):
                            url = f"http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/change/is_checked"

                            req_data = {
                                "user_id": get_user_id(),
                                "store_name": get_user_info()['store_name'],  
                                "timestamp": tmp_row_data['time'],
                            }

                            print("확인 req_data:", req_data)
                            try:
                                response = requests.post(url, json=req_data)
                                if response.status_code == 200:
                                    self.refresh()  # 테이블 다시 그리기
                                    # return result
                                else:
                                    print(f"요청 실패: {response.status_code}")
                                    return 
                            except requests.RequestException as e:
                                print(f"확인 요청 중 오류 발생: {e}")
                                return
                            
                        confirm_button.clicked.connect(
                            partial(confirm_clicked, row_data)
                        )
                        confirm_button.setFixedSize(100, 30)  # 버튼 크기 설정

                        layout = QHBoxLayout()
                        layout.addWidget(confirm_label)
                        layout.addWidget(confirm_button)
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거

                        # 셀에 레이아웃 설정
                        cell_widget = QWidget()
                        cell_widget.setLayout(layout)
                        self.detect_table.setCellWidget(row, col, cell_widget)

                elif col == 5: # 클립 보기 버튼 추가
                    clip_button = QPushButton("")
                    clip_button.setProperty("class", "btn clip")
                     # 삭제 버튼을 가운데 정렬하기 위한 레이아웃 설정
                    layout = QHBoxLayout()
                    layout.addWidget(clip_button)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                    layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
                    
                    # 셀에 레이아웃 설정
                    cell_widget = QWidget()
                    cell_widget.setLayout(layout)
                    self.detect_table.setCellWidget(row, col, cell_widget)
                    
                    def confirm_clicked(tmp_row_data):
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
                                popup_rect = self.video_popup_widget.rect()
                                center_pos = self.mapToGlobal(parent_rect.center() - popup_rect.center())
                                center_pos.setX(center_pos.x() - 95)
                                center_pos.setY(center_pos.y() - 25)
                                self.video_popup_widget.show_at(center_pos)
                                self.video_popup_widget.refresh()  # 비디오 팝업 위젯 새로고침

                                # 비디오 수신
                                video_url = f'http://{CENTRAL_IP}:{CENTRAL_GUI_PORT}/load/video?video_url={tmp_row_data['video_url']}'
                                print("비디오 URL:", video_url)
                                self.video_popup_widget.video.setSource(QUrl(video_url))
                                self.video_popup_widget.video.play()


                                print("[비디오 - 응답 내용]:", response)
                                # self.refresh()  # 테이블 다시 그리기
                                # return result
                            else:
                                print(f"요청 실패: {response.status_code}")
                                return 
                        except requests.RequestException as e:
                            print(f"요청 중 오류 발생: {e}")
                            return 
                        
                    clip_button.clicked.connect(
                        partial(confirm_clicked, row_data)
                    )
                
                    # 삭제 버튼 추가
                    delete_button = QPushButton("")
                    delete_button.setProperty("class", "btn delete")
                     # 삭제 버튼을 가운데 정렬하기 위한 레이아웃 설정
                    layout = QHBoxLayout()
                    layout.addWidget(delete_button)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 가운데 정렬
                    layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
                    
                    # 셀에 레이아웃 설정
                    cell_widget = QWidget()
                    cell_widget.setLayout(layout)
                    self.detect_table.setCellWidget(row, 6, cell_widget)
                else :
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 텍스트 가운데 정렬
                    self.detect_table.setItem(row, col, item)

    def click_toggle1(self): # 오늘 클릭
        self.toggle1.setProperty("class", "toggle active")
        self.toggle2.setProperty("class", "toggle")
        self.toggle3.setProperty("class", "toggle")
        self.toggle1.style().unpolish(self.toggle1)   
        self.toggle1.style().polish(self.toggle1)
        self.toggle2.style().unpolish(self.toggle2)   
        self.toggle2.style().polish(self.toggle2)
        self.toggle3.style().unpolish(self.toggle3)   
        self.toggle3.style().polish(self.toggle3)
        self.period = "today"

    def click_toggle2(self): # 주간 클릭
        self.toggle1.setProperty("class", "toggle")
        self.toggle2.setProperty("class", "toggle active")
        self.toggle3.setProperty("class", "toggle")
        self.toggle1.style().unpolish(self.toggle1)   
        self.toggle1.style().polish(self.toggle1)
        self.toggle2.style().unpolish(self.toggle2)   
        self.toggle2.style().polish(self.toggle2)
        self.toggle3.style().unpolish(self.toggle3)   
        self.toggle3.style().polish(self.toggle3)
        self.period = "week"

    def click_toggle3(self): # 월간 클릭
        self.toggle1.setProperty("class", "toggle")
        self.toggle2.setProperty("class", "toggle")
        self.toggle3.setProperty("class", "toggle active")
        self.toggle1.style().unpolish(self.toggle1)   
        self.toggle1.style().polish(self.toggle1)
        self.toggle2.style().unpolish(self.toggle2)   
        self.toggle2.style().polish(self.toggle2)
        self.toggle3.style().unpolish(self.toggle3)   
        self.toggle3.style().polish(self.toggle3)
        self.period = "month"

    def change_date(self):
        self.toggle1.setProperty("class", "toggle")
        self.toggle2.setProperty("class", "toggle")
        self.toggle3.setProperty("class", "toggle")
        self.toggle1.style().unpolish(self.toggle1)   
        self.toggle1.style().polish(self.toggle1)
        self.toggle2.style().unpolish(self.toggle2)   
        self.toggle2.style().polish(self.toggle2)
        self.toggle3.style().unpolish(self.toggle3)   
        self.toggle3.style().polish(self.toggle3)
        self.period = None

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