import os
import sys

from PyQt6.QtWidgets import QApplication

from login import LoginWindow
from management import MainWindow


class MainApp:
    def __init__(self):
        self.login_window = LoginWindow()
        self.main_window = None
        self.login_window.login_successful.connect(self.show_main_window)

    def show_main_window(self):
        self.login_window.hide()
        self.main_window = MainWindow()
        self.main_window.show()

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_window.show()
        self.login_window.username_input.clear()
        self.login_window.password_input.clear()

    # def resource_path(relative_path):
    #     """获取资源的绝对路径，兼容开发和打包环境"""
    #     if hasattr(sys, '_MEIPASS'):
    #         # PyInstaller 打包后的临时目录
    #         return os.path.join(sys._MEIPASS, relative_path)
    #     # 开发环境下的绝对路径
    #     return os.path.join(os.path.abspath("."), relative_path)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show_login()
    sys.exit(app.exec())
