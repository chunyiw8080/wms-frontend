import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit
from PyQt6.QtGui import QPixmap, QPainter, QPalette, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from qfluentwidgets import (LineEdit, Theme, setTheme, PasswordLineEdit, InfoBar, InfoBarPosition, PrimaryPushButton)
import sys

from backendRequests.loginRequests import login_request
from windows.main_window import MainWindow


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('沈阳市二一三自动化装备有限公司库存管理系统')
        self.setFixedSize(512, 288)

        palette = self.palette()  # 获取当前调色板
        palette.setColor(QPalette.ColorRole.Window, QColor("lightgrey"))  # 将窗口背景色设置为白色
        self.setAutoFillBackground(True)  # 启用自动填充背景
        self.setPalette(palette)  # 应用调色板到窗口

        # 设置登录页背景图片
        # self.background = QPixmap("resources/images/background.jpg")
        # self.background = self.background.scaled(QSize(512, 288), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addStretch(1)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 155, 0)
        form_layout.addStretch(1)

        self.username_input = LineEdit(self)
        self.username_input.setPlaceholderText('用户名')
        self.username_input.setFixedWidth(200)
        self.username_input.setText('alice01')
        form_layout.addWidget(self.username_input)

        self.password_input = PasswordLineEdit(self)
        self.password_input.setPlaceholderText('密码')
        self.password_input.setFixedWidth(200)
        self.password_input.setText('pass123')
        form_layout.addWidget(self.password_input)

        login_btn = PrimaryPushButton('登录', self)
        login_btn.setFixedWidth(200)
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)

        form_layout.addStretch(1)

        main_layout.addLayout(form_layout)


    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        res = login_request(username, password, self.session)
        if res:
            print(self.session.cookies)
            self.accept_login()
        else:
            InfoBar.error(title='登陆失败', content='账号或密码错误', duration=3000, parent=self)

    def accept_login(self):
        self.main_window = MainWindow(self.session)
        self.main_window.show()
        # self.parent().session = self.session
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.LIGHT)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())