import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from qfluentwidgets import (LineEdit, Theme, setTheme,
                            PasswordLineEdit, InfoBar, InfoBarPosition, PrimaryPushButton)
from backendRequests.jsonRequests import APIClient
from utils.token_utils import decode_token
from config import URL
from utils.worker import Worker


class LoginWindow(QWidget):
    login_successful = pyqtSignal()  # New signal for successful login

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('仓库管理系统 - 登录')
        self.setWindowIcon(QIcon('../resources/logo/logo.png'))
        self.setFixedSize(1024, 576)

        self.background = QPixmap("../resources/images/background.jpg")  # Replace with your image path
        self.background = self.background.scaled(QSize(1024, 576), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                 Qt.TransformationMode.SmoothTransformation)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Spacer to push form to the right
        main_layout.addStretch(1)

        # Right side - Login form
        form_layout = QVBoxLayout()

        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 220, 0)

        # Add top spacer
        form_layout.addStretch(1)

        # Logo
        logo_label = QLabel("仓库管理系统", self)
        logo_label.setStyleSheet("font-size: 28px; color: black; font-weight: bold ")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(logo_label)

        # Username input
        self.username_input = LineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setFixedWidth(200)
        form_layout.addWidget(self.username_input)

        # Password input
        self.password_input = PasswordLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setFixedWidth(200)
        form_layout.addWidget(self.password_input)

        # Login button
        login_button = PrimaryPushButton('登录', self)
        login_button.setFixedWidth(200)
        login_button.clicked.connect(self.login)
        form_layout.addWidget(login_button)

        # Add bottom spacer
        form_layout.addStretch(1)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def login(self):
        url = URL + '/users/login'
        if not self.username_input.text().strip() and not self.password_input.text().strip():
            InfoBar.error(title='登录失败', content="请输入用户名和密码", orient=Qt.Orientation.Vertical,
                          isClosable=True, position=InfoBarPosition.TOP_RIGHT, duration=4000, parent=self)
            return
        credentials = {
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip()
        }
        try:
            response = Worker.unpack_thread_queue(APIClient.post_request, url, credentials)
            print(f'login: {response}')
            result = response.get('success')
            token = response.get("token")
            print(f'token: {token}')
            payload = decode_token(str(token))
            print(f'token payload: {payload}')
            if result is True and token is not None:
                APIClient.set_jwt_token(response["token"])
                self.login_successful.emit()
            else:
                InfoBar.error(title='登录失败', content="用户名或密码不正确", orient=Qt.Orientation.Vertical,
                              isClosable=True, position=InfoBarPosition.TOP_RIGHT, duration=4000, parent=self)
        except Exception as e:
            InfoBar.error(title='登录失败', content=str(e), orient=Qt.Orientation.Vertical,
                          isClosable=True, position=InfoBarPosition.TOP_RIGHT, duration=4000, parent=self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.LIGHT)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
