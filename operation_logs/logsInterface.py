import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication
from qfluentwidgets import CardWidget, PlainTextEdit, ComboBox, StrongBodyLabel, PushButton, InfoBar, SmoothMode
from utils.worker import Worker
from backendRequests.jsonRequests import APIClient
from config import URL


class LogsInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('LogsInterface')
        self.setWindowTitle('操作日志')

        self.setup_ui()
        # self.load_log_files()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 顶部按钮组
        card_widget = CardWidget(self)
        buttons_layout = QHBoxLayout(card_widget)

        self.files_label = StrongBodyLabel('读取日志: ', self)
        self.files_combo = ComboBox(self)
        self.files_combo.addItems(self.load_log_files())
        self.files_combo.setFixedWidth(300)
        self.search_btn = PushButton('读取', self)
        self.search_btn.clicked.connect(self.load_log_content)

        buttons_layout.addWidget(self.files_label)
        buttons_layout.addWidget(self.files_combo)
        buttons_layout.addWidget(self.search_btn)
        buttons_layout.addStretch(1)
        layout.addWidget(card_widget)

        self.plainText = PlainTextEdit(self)
        self.plainText.setReadOnly(True)
        self.plainText.scrollDelegate.verticalSmoothScroll.setSmoothMode(smoothMode=SmoothMode.NO_SMOOTH)
        self.plainText.scrollDelegate.horizonSmoothScroll.setSmoothMode(smoothMode=SmoothMode.NO_SMOOTH)
        font = QFont()
        font.setPointSize(12)
        self.plainText.setFont(font)
        layout.addWidget(self.plainText)

        self.setStyleSheet("LogsInterface {background-color:white;}")
        self.resize(1280, 760)

    def load_log_files(self):
        url = URL + '/logs/getfiles'
        response = Worker.unpack_thread_queue(APIClient.get_request, url)
        files = response.get('data')
        return files

    def load_log_content(self):
        filename = self.files_combo.currentText()
        url = URL + f'/logs/content/{filename}'
        try:
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            if response.get('success'):
                self.plainText.setPlainText('')
                content = response.get('data')
                for line in content:
                    self.plainText.appendPlainText(line)
            else:
                InfoBar.error(title='加载失败', content='日志内容加载失败', parent=self, duration=5000)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogsInterface()
    window.show()
    sys.exit(app.exec())
