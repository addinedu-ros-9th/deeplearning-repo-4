import sys, os
from PyQt6.uic import loadUi
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import numpy as np

from matplotlib.figure import Figure  # Figure 임포트
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
import koreanize_matplotlib

from style import apply_style
from style import colors as c

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("dashboard.ui", self)
        self.text1.setProperty("class", "size18 weight700")
        self.text1.setText(f"{self.year1.value()}년 {self.month1.value()}월 통계")
        self.text2.setText(f"전체 통계")
        self.year1.setProperty("class", "spinbox small")
        self.month1.setProperty("class", "spinbox small")
        self.text_year.setProperty("class", "color-gray6 size12 weight300")
        self.text_month.setProperty("class", "color-gray6 size12 weight300")
        self.divider1.setProperty("class", "bg grayc")
        self.graph1_container.setProperty("class", "radius otlc")
        self.graph2_container.setProperty("class", "radius otlc")
        self.graph3_container.setProperty("class", "radius otlc")
        self.graph1_text.setProperty("class", "size14 weight700")
        self.graph2_text.setProperty("class", "size14 weight700")
        self.text2.setProperty("class", "size14 weight700")
        self.search_btn.setProperty("class", "btn small outlined primary weight700")

        self.labels = ["파손", "유기", "절도", "전등 끔"]
        self.colors = [c["primary"], c["secondary"], c["therity"], c["fourth"]]
        self.data = np.array([
            [45, 40, 43, 47, 44, 46, 48, 32, 41, 56, 17, 65],  # 파손
            [38, 37, 39, 38, 37, 39, 40, 32, 15, 32, 61, 32],  # 유기
            [22, 25, 23, 24, 22, 23, 24, 12, 15, 21, 31, 21],  # 절도
            [18, 15, 14, 13, 16, 15, 14, 22, 15, 17, 12, 15],  # 전등 끔
        ])
        self.graph1_widget = QVBoxLayout(self.graph1)
        self.graph2_widget = QVBoxLayout(self.graph2)
        self.graph3_widget = QVBoxLayout(self.graph3)
        self.graph1_legend_layout = QHBoxLayout(self.graph1_legend)
        self.graph2_legend_layout = QHBoxLayout(self.graph2_legend)
        self.graph3_legend_layout = QHBoxLayout(self.graph3_legend)

        self.draw_graph1()
        self.draw_graph2()
        self.draw_graph3() 
        self.draw_legend()

        self.search_btn.clicked.connect(self.on_search_clicked)
    
    def clear_layout(self):
        while self.graph1_widget.count():
            item1 = self.graph1_widget.takeAt(0)
            item2 = self.graph2_widget.takeAt(0)
            item3 = self.graph3_widget.takeAt(0)
            widget1 = item1.widget()
            widget2 = item2.widget()
            widget3 = item3.widget()
            if widget1 is not None:
                widget1.setParent(None)
            if widget2 is not None:
                widget2.setParent(None)
            if widget3 is not None:
                widget3.setParent(None)
        while self.graph1_legend_layout.count():
            item1 = self.graph1_legend_layout.takeAt(0)
            item2 = self.graph2_legend_layout.takeAt(0)
            item3 = self.graph3_legend_layout.takeAt(0)
            widget1 = item1.widget()
            widget2 = item2.widget()
            widget3 = item3.widget()
            if widget1 is not None:
                widget1.setParent(None)
            if widget2 is not None:
                widget2.setParent(None)
            if widget3 is not None:
                widget3.setParent(None)

    def on_search_clicked(self):
        self.data = np.array([
            [38, 37, 39, 38, 37, 39, 40, 32, 15, 32, 61, 32],  # 유기
            [22, 25, 23, 24, 22, 23, 24, 12, 15, 21, 31, 21],  # 절도
            [45, 40, 43, 47, 44, 46, 48, 32, 41, 56, 17, 65],  # 파손
            [18, 15, 14, 13, 16, 15, 14, 22, 15, 17, 12, 15],  # 전등 끔
        ])
        self.text1.setText(f"{self.year1.value()}년 {self.month1.value()}월 통계")
        self.clear_layout()
        self.draw_graph1()
        self.draw_graph2()
        self.draw_graph3() 
        self.draw_legend()


    def draw_graph1(self):
        i = self.month1.value() - 1
        graph1_data = [self.data[0][i], self.data[1][i], self.data[2][i], self.data[3][i]]
        
        self.canvas = FigureCanvas(Figure(figsize=(3, 3)))
        self.graph1_widget.addWidget(self.canvas)
        
        self.ax1 = self.canvas.figure.add_subplot(111)
        self.ax1.set_position([0, 0, 1, 1])
        self.ax1.pie(
            graph1_data,
            labels=None,
            colors=self.colors,
            startangle=90,
            wedgeprops=dict(width=0.3)  # 가운데 구멍 크기 설정
        )
        self.ax1.set_aspect('equal')

    def draw_graph2(self):
        graph2_data = np.array([
            [12, 15, 14, 13, 16, 15, 22, 13, 12, 11, 10, 25],  # 파손
            [10, 12, 13, 11, 10, 12, 14, 11, 10, 9, 8, 13],    # 유기
            [8, 7, 9, 8, 7, 9, 10, 8, 7, 6, 5, 9],             # 절도
            [6, 5, 4, 5, 6, 5, 7, 5, 4, 3, 2, 6],              # 전등 끔
        ])
        months2 = [
            "~2시", "~4시", "~6시", "~8시", "~10시",
            "~12시", "~14시", "~16시", "~18시", "~20시",
            "~22시", "~24시"
        ]

        self.stacked_canvas = FigureCanvas(Figure(figsize=(10, 3)))
        self.graph2_widget.addWidget(self.stacked_canvas)

        ax2 = self.stacked_canvas.figure.add_subplot(111)

        x2 = np.arange(len(months2))
        bottom = np.zeros(len(months2))
        for i in range(len(self.labels)):
            ax2.bar(
                x2, graph2_data[i], width=0.5, bottom=bottom,
                color=self.colors[i], label=self.labels[i]
            )
            bottom += graph2_data[i]

        ax2.set_xticks(x2)
        ax2.set_xticklabels(months2, fontsize=9)
        max_val2 = np.max(np.sum(graph2_data, axis=0))
        min_val2 = np.min(np.sum(graph2_data, axis=0))
        mid_val2 = (min_val2 + max_val2) // 2
        ax2.set_yticks([min_val2, mid_val2, max_val2])
        ax2.set_yticklabels([f"{min_val2} 건", f"{mid_val2} 건", f"{max_val2} 건"], fontsize=9)
        ax2.set_ylim(0, max_val2 * 1.2)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#999')
        ax2.spines['bottom'].set_color('#999')
        ax2.tick_params(axis='x', length=0) #
        ax2.tick_params(axis='y', length=5, width=0.5)
        # ax3.set_xlim(-0.5, len(months3) - 0.5)
        ax2.margins(y=0.4)
        ax2.set_xlim(-0.8, len(months2))
        self.stacked_canvas.figure.tight_layout(rect=[0, 0, 1, 1])

    def draw_graph3(self):
        # 데이터 예시 (월별 4종류)
        months = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]

        # Figure/Canvas 생성
        self.bar_canvas = FigureCanvas(Figure(figsize=(8, 3)))
        self.graph3_widget.addWidget(self.bar_canvas)

        ax = self.bar_canvas.figure.add_subplot(111)

        # 막대 그래프 그리기
        x = np.arange(len(months))
        n = len(self.labels)
        width = 0.12

        for i in range(n):
            offset = (i - (n - 1) / 2) * width * 1.2
            ax.bar(x + offset, self.data[i], width, label=self.labels[i], color=self.colors[i])
            
        ax.set_xticks(x)
        ax.set_xticklabels(months, fontsize=9)
        # y축에 최소, 중간, 최대 값 표시
        min_val = np.min(self.data)
        max_val = np.max(self.data)
        mid_val = (min_val + max_val) // 2
        ax.set_yticks([min_val, mid_val, max_val])
        ax.set_yticklabels([str(min_val)+" 건", str(mid_val)+" 건", str(max_val)+" 건"], fontsize=9)
        ax.set_ylim(0, np.max(self.data) * 1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#999')
        ax.spines['bottom'].set_color('#999')
        ax.tick_params(axis='x', length=0)
        ax.tick_params(axis='y', length=5, width=0.5)
        x = np.arange(len(months))
        ax.set_xlim(-0.5, len(months) - 0.5)
        ax.margins(y=0.2)

        self.bar_canvas.figure.tight_layout(rect=[0, 0, 1, 1])

    def draw_legend(self):
        # 레전드 
        self.legend_label1 = QLabel("")
        self.legend_label2 = QLabel("")
        self.legend_label3 = QLabel("")
        self.legend_label4 = QLabel("")
        self.legend_title1 = QLabel(f"파손({np.sum(self.data[0])})")
        self.legend_title2 = QLabel(f"유기({np.sum(self.data[1])})")
        self.legend_title3 = QLabel(f"절도({np.sum(self.data[2])})")
        self.legend_title4 = QLabel(f"전등 끔({np.sum(self.data[3])})")
        self.legend_label1.setProperty("class", "label primary")
        self.legend_label2.setProperty("class", "label secondary")
        self.legend_label3.setProperty("class", "label therity")
        self.legend_label4.setProperty("class", "label fourth")
        self.legend_title1.setProperty("class", "size12 weight600")
        self.legend_title2.setProperty("class", "size12 weight600")
        self.legend_title3.setProperty("class", "size12 weight600")
        self.legend_title4.setProperty("class", "size12 weight600")
        self.graph1_legend_layout.addWidget(self.legend_label1)
        self.graph1_legend_layout.addWidget(self.legend_title1)
        self.graph1_legend_layout.addWidget(self.legend_label2)
        self.graph1_legend_layout.addWidget(self.legend_title2)
        self.graph1_legend_layout.addWidget(self.legend_label3)
        self.graph1_legend_layout.addWidget(self.legend_title3)
        self.graph1_legend_layout.addWidget(self.legend_label4)
        self.graph1_legend_layout.addWidget(self.legend_title4)

        self.legend2_label1 = QLabel("")
        self.legend2_label2 = QLabel("")
        self.legend2_label3 = QLabel("")
        self.legend2_label4 = QLabel("")
        self.legend2_onlyTitle1 = QLabel("파손")
        self.legend2_onlyTitle2 = QLabel("유기")
        self.legend2_onlyTitle3 = QLabel("절도")
        self.legend2_onlyTitle4 = QLabel("전등 끔")
        self.legend2_label1.setProperty("class", "label primary")
        self.legend2_label2.setProperty("class", "label secondary")
        self.legend2_label3.setProperty("class", "label therity")
        self.legend2_label4.setProperty("class", "label fourth")
        self.legend2_onlyTitle1.setProperty("class", "size12 weight600")
        self.legend2_onlyTitle2.setProperty("class", "size12 weight600")
        self.legend2_onlyTitle3.setProperty("class", "size12 weight600")
        self.legend2_onlyTitle4.setProperty("class", "size12 weight600")
        self.graph2_legend_layout.addWidget(self.legend2_label1)
        self.graph2_legend_layout.addWidget(self.legend2_onlyTitle1)
        self.graph2_legend_layout.addWidget(self.legend2_label2)
        self.graph2_legend_layout.addWidget(self.legend2_onlyTitle2)
        self.graph2_legend_layout.addWidget(self.legend2_label3)
        self.graph2_legend_layout.addWidget(self.legend2_onlyTitle3)
        self.graph2_legend_layout.addWidget(self.legend2_label4)
        self.graph2_legend_layout.addWidget(self.legend2_onlyTitle4)

        self.legend3_label1 = QLabel("")
        self.legend3_label2 = QLabel("")
        self.legend3_label3 = QLabel("")
        self.legend3_label4 = QLabel("")
        self.legend3_onlyTitle1 = QLabel("파손")
        self.legend3_onlyTitle2 = QLabel("유기")
        self.legend3_onlyTitle3 = QLabel("절도")
        self.legend3_onlyTitle4 = QLabel("전등 끔")
        self.legend3_label1.setProperty("class", "label primary")
        self.legend3_label2.setProperty("class", "label secondary")
        self.legend3_label3.setProperty("class", "label therity")
        self.legend3_label4.setProperty("class", "label fourth")
        self.legend3_onlyTitle1.setProperty("class", "size12 weight600")
        self.legend3_onlyTitle2.setProperty("class", "size12 weight600")
        self.legend3_onlyTitle3.setProperty("class", "size12 weight600")
        self.legend3_onlyTitle4.setProperty("class", "size12 weight600")
        self.graph3_legend_layout.addWidget(self.legend3_label1)
        self.graph3_legend_layout.addWidget(self.legend3_onlyTitle1)
        self.graph3_legend_layout.addWidget(self.legend3_label2)
        self.graph3_legend_layout.addWidget(self.legend3_onlyTitle2)
        self.graph3_legend_layout.addWidget(self.legend3_label3)
        self.graph3_legend_layout.addWidget(self.legend3_onlyTitle3)
        self.graph3_legend_layout.addWidget(self.legend3_label4)
        self.graph3_legend_layout.addWidget(self.legend3_onlyTitle4)

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